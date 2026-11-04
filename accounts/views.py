from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import pgettext

from PATCH.errors import error_page
from accounts import verification
from accounts.forms import (
    AccountDetailsForm,
    ContractorProfileForm,
    LoginForm,
    RegisterForm,
    RoleChangeForm,
    StyledPasswordChangeForm,
)
from accounts.mixins import role_required
from accounts.models import SPAM_STRIKE_LIMIT, ContractorProfile, User, UserRole
from repairs.models import CONTRACTOR_STAGES
from reports.models import ReportStatus


class PatchLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class PatchLogoutView(LogoutView):
    next_page = "home"


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        _report_sending(request, verification.send_verification_email(request, user, force=True), user)
        if user.has_pending_role_request:
            messages.success(
                request,
                _(
                    "Welcome to PATCH. Your inspector request was sent to an administrator. "
                    "You can use PATCH as a citizen until it is approved."
                ),
            )
        else:
            messages.success(request, _("Welcome to PATCH."))
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    user = request.user
    # Several forms share this page; a hidden "form" field says which one was posted.
    posted = request.POST.get("form") if request.method == "POST" else None

    details_form = AccountDetailsForm(request.POST if posted == "details" else None, instance=user)
    password_form = StyledPasswordChangeForm(user, request.POST if posted == "password" else None)

    contractor_form = None
    profile_obj = getattr(user, "contractor_profile", None)
    if user.role == UserRole.CONTRACTOR:
        if profile_obj is None:
            profile_obj = ContractorProfile.objects.create(user=user, company_name=user.full_name)
        contractor_form = ContractorProfileForm(
            request.POST if posted == "contractor" else None, instance=profile_obj
        )

    if posted == "details" and details_form.is_valid():
        email_changed = "email" in details_form.changed_data
        details_form.save()
        messages.success(request, _("Account details updated."))
        if email_changed:
            verification.mark_unverified(user)
            messages.info(request, _("Your email changed, so it needs verifying again."))
            _report_sending(request, verification.send_verification_email(request, user, force=True), user)
        return redirect("accounts:profile")
    if posted == "password" and password_form.is_valid():
        password_form.save()
        update_session_auth_hash(request, password_form.user)
        messages.success(request, _("Password changed."))
        return redirect("accounts:profile")
    if posted == "contractor" and contractor_form and contractor_form.is_valid():
        contractor_form.save()
        messages.success(request, _("Contractor profile updated."))
        return redirect("accounts:profile")
    if posted == "details":
        # Keep the header showing saved values, not the rejected input.
        user.refresh_from_db()

    if user.role == UserRole.CONTRACTOR:
        repairs_url = reverse("repairs:list")
        tasks = user.assigned_repair_tasks.all()
        stats = [
            (tasks.filter(status__in=CONTRACTOR_STAGES[key]).count(), label, f"{repairs_url}?stage={key}")
            for key, label in (("reserved", _("Reserved")), ("in_progress", _("In progress")), ("finished", _("Finished")))
        ]
    else:
        reports_url = reverse("reports:mine")
        reports = user.road_reports.all()
        stats = [
            (reports.count(), _("Reports"), reports_url),
            (reports.exclude(status__in=[ReportStatus.REPAIRED, ReportStatus.REJECTED]).count(), _("Open"), reports_url),
            (reports.filter(status=ReportStatus.REPAIRED).count(), pgettext("count", "Repaired"), reports_url),
        ]
    initials = user.initials
    # With no mail server, the link can't reach anyone's inbox, so show it here (development only).
    local_verify_link = (
        verification.verification_link(request, user)
        if settings.DEBUG and not settings.EMAIL_SENDS_REAL_MAIL and not user.email_verified else ""
    )
    return render(
        request,
        "accounts/profile.html",
        {
            "details_form": details_form,
            "password_form": password_form,
            "contractor_form": contractor_form,
            "profile_obj": profile_obj,
            "stats": stats,
            "initials": initials,
            "local_verify_link": local_verify_link,
        },
    )


def verify_email(request, token):
    """The link from the email. Works without signing in, e.g. when opened on another device."""
    user = verification.user_for_token(token)
    if user is None:
        return error_page(
            request, 400, _("This verification link doesn't work"),
            _("It may have expired, been used for an old email address, or been copied incompletely. "
              "Sign in and send yourself a new link from your profile."),
            retry_url=reverse("accounts:profile"), retry_label=_("Go to my profile"),
        )
    already = user.email_verified
    verification.mark_verified(user)
    if already:
        messages.info(request, _("Your email address was already verified."))
    else:
        messages.success(request, _("Thank you. Your email address %(email)s is verified.") % {"email": user.email})
    return redirect("accounts:profile" if request.user.is_authenticated else "accounts:login")


@login_required
def resend_verification(request):
    if request.method == "POST" and not request.user.email_verified:
        _report_sending(request, verification.send_verification_email(request, request.user), request.user)
    return redirect("accounts:profile")


def _report_sending(request, outcome, user):
    """Tell the user exactly what happened to their verification email."""
    if outcome == verification.SENT:
        messages.success(request, _("We sent a link to %(email)s. Check your inbox and spam folder.") % {"email": user.email})
    elif outcome == verification.SAVED_LOCALLY:
        messages.warning(request, _("Email sending isn't set up on this server, so no email was sent. "
                                    "Use the verification link on your profile page."))
    elif outcome == verification.FAILED:
        messages.error(request, _("The verification email couldn't be sent right now. Try again from your profile in a few minutes."))
    else:
        messages.warning(request, _("A link was sent less than two minutes ago. Please check your inbox first."))


@role_required(UserRole.ADMIN)
def user_directory(request):
    users = User.objects.all()
    pending = [u for u in users if u.has_pending_role_request]
    return render(
        request,
        "accounts/users.html",
        {"users": users, "pending": pending, "roles": UserRole.choices, "strike_limit": SPAM_STRIKE_LIMIT},
    )


@role_required(UserRole.ADMIN)
def review_role_request(request, user_id, decision):
    target = get_object_or_404(User, pk=user_id)
    if request.method != "POST" or not target.has_pending_role_request:
        return redirect("accounts:users")
    requested = target.get_requested_role_display()
    if decision == "approve":
        target.role = target.requested_role
        messages.success(request, _("Approved: %(name)s is now %(role)s.") % {"name": target.full_name, "role": requested})
    else:
        messages.success(
            request, _("Declined %(name)s's request to become %(role)s.") % {"name": target.full_name, "role": requested}
        )
    target.requested_role = ""
    target.save(update_fields=["role", "requested_role", "updated_at"])
    return redirect("accounts:users")


@role_required(UserRole.ADMIN)
def change_role(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    form = RoleChangeForm(request.POST or None)
    if request.method != "POST" or not form.is_valid():
        return redirect("accounts:users")
    if target == request.user:
        messages.error(request, _("You cannot change your own role."))
        return redirect("accounts:users")
    target.role = form.cleaned_data["role"]
    # A direct change by an admin settles any open request.
    target.requested_role = ""
    target.save(update_fields=["role", "requested_role", "updated_at"])
    messages.success(
        request, _("%(name)s's role is now %(role)s.") % {"name": target.full_name, "role": target.get_role_display()}
    )
    return redirect("accounts:users")


@role_required(UserRole.ADMIN)
def reset_strikes(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        target.spam_strikes = 0
        target.save(update_fields=["spam_strikes", "updated_at"])
        messages.success(request, _("%(name)s's spam strikes were reset. They can report again.") % {"name": target.full_name})
    return redirect("accounts:users")


@role_required(UserRole.ADMIN)
def toggle_block(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, _("You cannot block your own account."))
        return redirect("accounts:users")
    target.is_active = not target.is_active
    target.save(update_fields=["is_active", "updated_at"])
    if target.is_active:
        messages.success(request, _("%(name)s was unblocked.") % {"name": target.full_name})
    else:
        messages.success(request, _("%(name)s was blocked.") % {"name": target.full_name})
    return redirect("accounts:users")
