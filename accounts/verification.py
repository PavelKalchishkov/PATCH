"""Email verification: a signed link that proves a user can read mail at their address."""
import logging
import smtplib

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from accounts.models import User

logger = logging.getLogger(__name__)

SALT = "patch.accounts.verify-email"

# What happened when we tried to send: these drive the message the user sees.
SENT, SAVED_LOCALLY, FAILED, TOO_SOON = "sent", "saved_locally", "failed", "too_soon"
LINK_VALID_SECONDS = 3 * 24 * 60 * 60
RESEND_COOLDOWN_SECONDS = 2 * 60


def make_token(user):
    # The address is part of the token, so a link stops working once the email changes.
    return signing.dumps({"user": str(user.pk), "email": user.email.lower()}, salt=SALT)


def user_for_token(token):
    """The user this link verifies, or None if it's invalid, expired or for an old address."""
    try:
        data = signing.loads(token, salt=SALT, max_age=LINK_VALID_SECONDS)
    except signing.BadSignature:  # also covers SignatureExpired
        return None
    user = User.objects.filter(pk=data.get("user")).first()
    if not user or user.email.lower() != data.get("email"):
        return None
    return user


def mark_verified(user):
    if not user.email_verified:
        user.email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=["email_verified", "email_verified_at", "updated_at"])


def mark_unverified(user):
    user.email_verified = False
    user.email_verified_at = None
    user.save(update_fields=["email_verified", "email_verified_at", "updated_at"])


def verification_link(request, user):
    return request.build_absolute_uri(reverse("accounts:verify_email", args=[make_token(user)]))


def send_verification_email(request, user, *, force=False):
    """Email the link and report what really happened: SENT, SAVED_LOCALLY, FAILED or TOO_SOON."""
    key = f"verify-email-sent:{user.pk}"
    if not force and cache.get(key):
        return TOO_SOON
    context = {"user": user, "link": verification_link(request, user), "days": LINK_VALID_SECONDS // 86400}
    try:
        send_mail(
            _("Confirm your email address for PATCH"),
            render_to_string("accounts/email/verify.txt", context, request=request),
            None,
            [user.email],
        )
    except (smtplib.SMTPException, OSError):
        logger.exception("Sending the verification email to user %s failed", user.pk)
        return FAILED
    cache.set(key, True, RESEND_COOLDOWN_SECONDS)
    return SENT if settings.EMAIL_SENDS_REAL_MAIL else SAVED_LOCALLY
