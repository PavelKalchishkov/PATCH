"""Spam protection for citizen reports: a rate limit, duplicate detection and spam strikes."""
import math
from dataclasses import dataclass
from datetime import timedelta

from django.db.models import F
from django.utils import timezone

from accounts.models import User, UserRole
from reports.models import ReportStatus, RoadReport, SubmissionLog

HOURLY_LIMIT = 3
DAILY_LIMIT = 10
DUPLICATE_RADIUS_M = 25
# A confirmation must be close to the report it confirms; GPS drift gets a little slack.
CONFIRMATION_MAX_DISTANCE_M = 60
OPEN_STATUSES = (
    ReportStatus.SUBMITTED, ReportStatus.PROCESSING, ReportStatus.VERIFIED, ReportStatus.SCHEDULED_FOR_REPAIR,
)


# ---------- A. Rate limit ----------

@dataclass
class Quota:
    allowed: bool
    remaining_hour: int
    remaining_day: int
    next_allowed_at: object = None  # datetime when the next slot opens, if blocked


def is_exempt(user):
    return user.is_superuser or user.role in (UserRole.INSPECTOR, UserRole.ADMIN)


def quota_for(user) -> Quota:
    if is_exempt(user):
        return Quota(True, HOURLY_LIMIT, DAILY_LIMIT)
    now = timezone.now()
    hour_start, day_start = now - timedelta(hours=1), now - timedelta(days=1)
    recent = list(SubmissionLog.objects.filter(user=user, created_at__gte=day_start).values_list("created_at", flat=True))
    in_hour = sorted(t for t in recent if t >= hour_start)
    in_day = sorted(recent)
    remaining_hour = max(0, HOURLY_LIMIT - len(in_hour))
    remaining_day = max(0, DAILY_LIMIT - len(in_day))
    if remaining_hour and remaining_day:
        return Quota(True, remaining_hour, remaining_day)
    # The next slot opens when the oldest submission in the full window ages out.
    candidates = []
    if not remaining_hour:
        candidates.append(in_hour[-HOURLY_LIMIT] + timedelta(hours=1))
    if not remaining_day:
        candidates.append(in_day[-DAILY_LIMIT] + timedelta(days=1))
    return Quota(False, remaining_hour, remaining_day, max(candidates))


def log_submission(user):
    SubmissionLog.objects.create(user=user)


# ---------- B. Duplicates ----------

def distance_m(lat1, lng1, lat2, lng2):
    """Great-circle distance in metres."""
    lat1, lng1, lat2, lng2 = map(math.radians, map(float, (lat1, lng1, lat2, lng2)))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(a))


def nearby_open_reports(lat, lng, radius_m=DUPLICATE_RADIUS_M):
    """Open, non-spam reports within radius_m, nearest first, as (report, distance) pairs."""
    lat, lng = float(lat), float(lng)
    # Cheap bounding box first, exact distance after.
    dlat = radius_m / 111_320
    dlng = radius_m / (111_320 * max(math.cos(math.radians(lat)), 0.01))
    candidates = RoadReport.objects.filter(
        status__in=OPEN_STATUSES, is_spam=False,
        latitude__range=(lat - dlat, lat + dlat), longitude__range=(lng - dlng, lng + dlng),
    ).prefetch_related("detections__catalog")
    found = [(r, distance_m(lat, lng, r.latitude, r.longitude)) for r in candidates]
    return sorted([(r, d) for r, d in found if d <= radius_m], key=lambda pair: pair[1])


# ---------- C. Spam strikes ----------

def update_spam_strike(report, was_spam):
    """Give or take back a strike when an inspector marks or unmarks a report as spam."""
    if not report.user_id or was_spam == report.is_spam:
        return
    if report.is_spam:
        User.objects.filter(pk=report.user_id).update(spam_strikes=F("spam_strikes") + 1)
    else:
        User.objects.filter(pk=report.user_id, spam_strikes__gt=0).update(spam_strikes=F("spam_strikes") - 1)
