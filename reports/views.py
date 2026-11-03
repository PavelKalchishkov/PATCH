import logging

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import get_language
from django.views.decorators.http import require_GET
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from PATCH.errors import error_page
from accounts.mixins import role_required
from accounts.models import SPAM_STRIKE_LIMIT, UserRole
from reports import antispam
from reports.forms import ConfirmationForm, ReportSubmitForm
from reports.geocode import GeocodingError, reverse_geocode
from reports.models import ReportConfirmation, ReportStatus, ReportVote, RoadReport, VoteKind
from repairs.models import PhotoKind, RepairTask, TaskStatus
from repairs.services import reservable_reports
from reports.services import transition_report
from vision.pipeline import enqueue_vision_job

logger = logging.getLogger(__name__)

# Reports an inspector still has to verify or reject.
AWAITING_REVIEW = (ReportStatus.SUBMITTED, ReportStatus.PROCESSING)


def _reporting_block(user):
    """Why this user can't send a report right now ("banned", "limit" or None), plus their quota."""
    if user.reporting_banned:
        return "banned", None
    quota = antispam.quota_for(user)
    if not quota.allowed:
        return "limit", quota
    return None, quota


def _limit_message(quota):
    return _("You've reached the limit of %(hour)s reports an hour and %(day)s a day. "
             "You can send the next one at %(time)s.") % {
        "hour": antispam.HOURLY_LIMIT, "day": antispam.DAILY_LIMIT,
        "time": timezone.localtime(quota.next_allowed_at).strftime("%H:%M"),
    }


def _banned_message():
    return _("Your account can no longer send reports because %(limit)s of your reports were marked as spam. "
             "If you think this is a mistake, contact an administrator.") % {"limit": SPAM_STRIKE_LIMIT}


@login_required
def submit_report(request):
    if request.user.role == UserRole.CONTRACTOR:
        messages.info(request, _("Contractor accounts don't file damage reports. Pick up verified damage from Available work."))
        return redirect("repairs:available")
    block, quota = _reporting_block(request.user)
    form = ReportSubmitForm(request.POST or None, request.FILES or None)
    context = {
        "form": form,
        # Not "block": inside {% block %} tags Django already uses that name.
        "report_block": block,
        "quota": quota,
        "block_message": _banned_message() if block == "banned" else (_limit_message(quota) if block else ""),
        "limits": {"hour": antispam.HOURLY_LIMIT, "day": antispam.DAILY_LIMIT},
    }
    if request.method != "POST":
        return render(request, "reports/submit.html", context)
    if block:
        return render(request, "reports/submit.html", {**context, "problems": [context["block_message"]]},
                      status=429 if block == "limit" else 403)
    if not form.is_valid():
        # One line per problem; the location fields share a single message.
        problems = list(dict.fromkeys(str(e) for errors in form.errors.values() for e in errors))
        return render(request, "reports/submit.html", {**context, "problems": problems}, status=400)
    if not form.cleaned_data["confirm_new"]:
        if antispam.nearby_open_reports(form.cleaned_data["latitude"], form.cleaned_data["longitude"]):
            # The page asks before sending; this catches anything that skipped the question.
            problem = _("This problem may already be reported nearby. Take the photo again and choose "
                        "whether it's the same problem.")
            return render(request, "reports/submit.html", {**context, "problems": [problem]}, status=409)

    try:
        # One transaction, so a failure part-way never leaves half a report behind.
        with transaction.atomic():
            report = form.save(commit=False)
            report.user = request.user
            report.device_metadata = {
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "source": "camera",
                "captured_at_ms": form.cleaned_data["captured_at"],
                "location_accuracy_m": round(form.cleaned_data["location_accuracy"], 1),
            }
            report.save()
            if report.original_image:
                report.original_image_url = report.original_image.url
                report.save(update_fields=["original_image_url"])
            antispam.log_submission(request.user)
    except Exception:
        logger.exception("Saving a road report failed")
        return error_page(
            request, None, _("Your report wasn't submitted"),
            _("Something went wrong while saving it, so nothing was sent. Please take the photo again and resend it."),
            status=500,
            retry_url=reverse("reports:submit"),
        )

    try:
        enqueue_vision_job(report)
    except Exception:
        logger.exception("Starting the vision job for report %s failed", report.id)
        messages.warning(
            request,
            _("Your report was saved, but the automatic photo analysis couldn't start. "
              "An inspector will review it manually."),
        )
    else:
        messages.success(request, _("Report submitted. Computer vision analysis is running."))
    return redirect("reports:detail", report_id=report.id)


@login_required
@require_GET
def nearby_reports(request):
    """Open reports close to a photo's location, so the citizen can add to one instead of duplicating it."""
    try:
        lat, lng = float(request.GET["lat"]), float(request.GET["lng"])
    except (KeyError, ValueError):
        return JsonResponse({"error": "lat and lng are required"}, status=400)
    confirmed = set(ReportConfirmation.objects.filter(user=request.user).values_list("report_id", flat=True))
    results = [{
        "id": str(report.id),
        "title": report.street_name or report.district or _("Road report"),
        "damages": report.damage_names,
        "status": report.status,
        "status_label": report.get_status_display(),
        "distance_m": round(distance),
        "image": report.annotated_image.url if report.annotated_image else "",
        "mine": report.user_id == request.user.id,
        "already_confirmed": report.id in confirmed,
        "confirm_url": reverse("reports:confirm", args=[report.id]),
    } for report, distance in antispam.nearby_open_reports(lat, lng)[:3]]
    return JsonResponse({"reports": results})


@login_required
def confirm_report(request, report_id):
    """Add the citizen's photo to an existing report rather than filing a duplicate."""
    report = get_object_or_404(RoadReport, pk=report_id)
    if request.method != "POST":
        return redirect("reports:detail", report_id=report.id)
    block, quota = _reporting_block(request.user)
    form = ConfirmationForm(request.POST, request.FILES)
    problem = None
    if request.user.role == UserRole.CONTRACTOR:
        problem = _("Contractor accounts don't file damage reports. Pick up verified damage from Available work.")
    elif block == "banned":
        problem = _banned_message()
    elif block == "limit":
        problem = _limit_message(quota)
    elif report.user_id == request.user.id:
        problem = _("You already reported this problem.")
    elif report.status not in antispam.OPEN_STATUSES or report.is_spam:
        problem = _("This report is already closed, so it can't take more photos.")
    elif ReportConfirmation.objects.filter(report=report, user=request.user).exists():
        problem = _("You've already added a photo to this report.")
    elif not form.is_valid():
        problem = next(str(e) for errors in form.errors.values() for e in errors)
    elif antispam.distance_m(form.cleaned_data["latitude"], form.cleaned_data["longitude"],
                             report.latitude, report.longitude) > antispam.CONFIRMATION_MAX_DISTANCE_M:
        problem = _("Your photo was taken too far from this report to confirm it.")
    if problem:
        messages.error(request, problem)
        return redirect("reports:submit")

    with transaction.atomic():
        ReportConfirmation.objects.create(
            report=report,
            user=request.user,
            photo=form.cleaned_data["photo"],
            latitude=form.cleaned_data["latitude"],
            longitude=form.cleaned_data["longitude"],
            location_accuracy_m=round(form.cleaned_data["location_accuracy"], 1),
        )
        antispam.log_submission(request.user)
    messages.success(request, _("Thank you. Your photo was added to the existing report, "
                                "which helps inspectors prioritise it."))
    return redirect("reports:detail", report_id=report.id)


@login_required
def vote(request, report_id, kind):
    """Mark a report accurate or flag it as spam; the same click again takes the vote back."""
    report = get_object_or_404(RoadReport, pk=report_id)
    if request.method != "POST" or kind not in VoteKind.values:
        return redirect("reports:detail", report_id=report.id)
    if not report.can_vote(request.user):
        messages.error(request, _("You can't vote on this report."))
        return redirect("reports:detail", report_id=report.id)
    existing = ReportVote.objects.filter(report=report, user=request.user).first()
    if existing and existing.kind == kind:
        existing.delete()
        messages.info(request, _("Your vote was removed."))
    else:
        ReportVote.objects.update_or_create(report=report, user=request.user, defaults={"kind": kind})
        if kind == VoteKind.SPAM:
            messages.success(request, _("Thank you. Inspectors will see that you flagged this report as spam."))
        else:
            messages.success(request, _("Thank you for confirming this report is accurate."))
    return redirect(f"{reverse('reports:detail', args=[report.id])}#votes")


@login_required
@require_GET
def geocode(request):
    """Street and district for a map point, used to prefill the report form."""
    try:
        lat, lng = float(request.GET["lat"]), float(request.GET["lng"])
    except (KeyError, ValueError):
        return JsonResponse({"error": "lat and lng are required"}, status=400)
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return JsonResponse({"error": "coordinates out of range"}, status=400)
    language = "bg" if (get_language() or "bg").startswith("bg") else "en"
    try:
        return JsonResponse(reverse_geocode(lat, lng, language))
    except GeocodingError:
        return JsonResponse({"error": "lookup failed"}, status=502)


@login_required
def my_reports(request):
    qs = RoadReport.objects.filter(user=request.user)
    return render(request, "reports/list.html", {"reports": qs, "title": _("My reports")})


def report_detail(request, report_id):
    report = get_object_or_404(
        RoadReport.objects.prefetch_related("detections__catalog", "detections__boq_items", "history"),
        pk=report_id,
    )
    is_public = report.status != ReportStatus.REJECTED and not report.is_spam
    is_owner = request.user.is_authenticated and report.user_id == request.user.id
    can_moderate = request.user.is_authenticated and request.user.can_moderate
    if not (is_public or is_owner or can_moderate):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(request, _("You can only view your own reports."))
        return redirect("reports:mine")
    repair_task = RepairTask.objects.filter(report=report).select_related("assigned_to").first()
    can_reserve = (
        request.user.is_authenticated
        and request.user.role == UserRole.CONTRACTOR
        and reservable_reports().filter(pk=report.pk).exists()
    )
    awaiting_review = report.status in AWAITING_REVIEW
    vision_job = report.vision_jobs.order_by("-created_at").first()
    # The inspector's verify/reject decision, shown in place of the buttons once it has been made.
    decision = None
    if not awaiting_review:
        decision = (
            report.history.filter(new_status__in=(ReportStatus.VERIFIED, ReportStatus.REJECTED))
            .select_related("changed_by")
            .first()
        )
    return render(
        request,
        "reports/detail.html",
        {
            "report": report,
            "can_reserve": can_reserve,
            "repair_task": repair_task,
            "awaiting_review": awaiting_review,
            "decision": decision,
            "vision_job": vision_job,
            "can_vote": report.can_vote(request.user),
            "my_vote": (
                ReportVote.objects.filter(report=report, user=request.user).values_list("kind", flat=True).first()
                if request.user.is_authenticated else None
            ),
        },
    )


@login_required
def delete_report(request, report_id):
    report = get_object_or_404(RoadReport, pk=report_id, user=request.user)
    if request.method != "POST":
        return redirect("reports:detail", report_id=report.id)
    if not report.can_owner_delete:
        messages.error(request, _("This report is already in the repair workflow and can no longer be deleted."))
        return redirect("reports:detail", report_id=report.id)
    for field in (report.original_image, report.annotated_image):
        if field:
            field.delete(save=False)
    report.delete()
    messages.success(request, _("Report deleted."))
    return redirect("reports:mine")


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def moderation_queue(request):
    reports = RoadReport.objects.exclude(status=ReportStatus.REJECTED).select_related("user")
    repairs = (
        RepairTask.objects.filter(status=TaskStatus.COMPLETED)
        .select_related("assigned_to", "team")
        .prefetch_related("damages__report")
        .order_by("updated_at")
    )
    tab = request.GET.get("tab")
    if tab not in ("damages", "repairs"):
        tab = "damages"
    return render(
        request,
        "reports/moderate.html",
        {
            "tab": tab,
            "reports": reports,
            "repairs": repairs,
            "reports_waiting": reports.filter(status__in=AWAITING_REVIEW, is_spam=False).count(),
        },
    )


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def moderate_report(request, report_id):
    report = get_object_or_404(RoadReport, pk=report_id)
    if request.method != "POST":
        return redirect("reports:detail", report_id=report.id)

    action = request.POST.get("action")
    if action in ("verify", "reject") and report.status not in AWAITING_REVIEW:
        messages.error(request, _("This report has already been reviewed."))
        return redirect("reports:detail", report_id=report.id)
    reason = request.POST.get("reason", "")
    was_spam = report.is_spam
    report.inspector_notes = request.POST.get("inspector_notes", report.inspector_notes)
    report.is_spam = bool(request.POST.get("is_spam"))
    report.is_duplicate = bool(request.POST.get("is_duplicate"))
    duplicate_of = request.POST.get("duplicate_of")
    if duplicate_of:
        report.duplicate_of_id = duplicate_of
    report.save()
    antispam.update_spam_strike(report, was_spam)

    if action == "verify":
        for detection in report.detections.all():
            detection.is_confirmed_by_human = True
            detection.save(update_fields=["is_confirmed_by_human"])
        transition_report(report, ReportStatus.VERIFIED, user=request.user, reason=reason or "Inspector verified")
        return redirect("reports:moderation_result", report_id=report.id)
    elif action == "reject":
        transition_report(report, ReportStatus.REJECTED, user=request.user, reason=reason or "Rejected after review")
        return redirect("reports:moderation_result", report_id=report.id)
    else:
        messages.info(request, _("Moderation flags saved."))
    return redirect("reports:detail", report_id=report.id)


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def moderation_result(request, report_id):
    report = get_object_or_404(RoadReport.objects.prefetch_related("detections__catalog"), pk=report_id)
    if report.status not in (ReportStatus.VERIFIED, ReportStatus.REJECTED):
        return redirect("reports:detail", report_id=report.id)
    last_change = report.history.filter(new_status=report.status).select_related("changed_by").first()
    next_report = (
        RoadReport.objects.filter(status__in=AWAITING_REVIEW, is_spam=False)
        .exclude(pk=report.pk)
        .order_by("created_at")
        .first()
    )
    return render(
        request,
        "reports/moderation_result.html",
        {
            "report": report,
            "verified": report.status == ReportStatus.VERIFIED,
            "last_change": last_change,
            "next_report": next_report,
            "remaining": RoadReport.objects.filter(status__in=AWAITING_REVIEW, is_spam=False).count(),
        },
    )


def before_after(request, report_id):
    report = get_object_or_404(RoadReport.objects.prefetch_related("detections__catalog"), pk=report_id)
    if report.status != ReportStatus.REPAIRED:
        return redirect("reports:detail", report_id=report.id)
    repairs = list(report.approved_repairs())
    photos = [p for task in repairs for p in task.photos.all()]
    # Prefer photos the contractor tagged "after"; otherwise the newest site photo.
    after_photo = next((p for p in photos if p.kind == PhotoKind.AFTER), None) or (photos[0] if photos else None)
    repaired_on = report.history.filter(new_status=ReportStatus.REPAIRED).first()
    # The annotated image has faces and plates blurred, so it is the one safe to show publicly.
    before_image = report.annotated_image or report.original_image
    return render(
        request,
        "reports/before_after.html",
        {
            "report": report,
            "repairs": repairs,
            "before_image": before_image,
            "after_photo": after_photo,
            "repaired_on": repaired_on,
        },
    )
