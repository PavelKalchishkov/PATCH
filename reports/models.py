import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _


class ReportStatus(models.TextChoices):
    SUBMITTED = "submitted", _("Submitted")
    PROCESSING = "processing", _("Processing")
    VERIFIED = "verified", _("Verified")
    SCHEDULED_FOR_REPAIR = "scheduled_for_repair", _("Scheduled for repair")
    REPAIRED = "repaired", _("Repaired")
    REJECTED = "rejected", _("Rejected")


class RoadReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="road_reports",
        db_column="user_id",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    geom = models.JSONField(help_text="GeoJSON Point in EPSG:4326")
    street_name = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=32,
        choices=ReportStatus.choices,
        default=ReportStatus.SUBMITTED,
    )
    original_image_url = models.TextField()
    annotated_image_url = models.TextField(blank=True)
    original_image = models.ImageField(upload_to="reports/original/", blank=True)
    annotated_image = models.ImageField(upload_to="reports/annotated/", blank=True)
    device_metadata = models.JSONField(null=True, blank=True)
    inspector_notes = models.TextField(blank=True)
    is_spam = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "road_reports"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        place = self.street_name or self.district or gettext("unlocated")
        return gettext("Report %(id)s · %(place)s") % {"id": str(self.id)[:8], "place": place}

    # One report is repaired as one job; these summarise all of its detected damages.
    @property
    def damage_names(self):
        names = dict.fromkeys(d.catalog.name for d in self.detections.all())
        return ", ".join(names)

    @property
    def top_severity(self):
        from damages.models import PRIORITY_FROM_SEVERITY

        detections = list(self.detections.all())
        if not detections:
            return None
        return min(detections, key=lambda d: PRIORITY_FROM_SEVERITY.get(d.severity, 3))

    @property
    def priority(self):
        detections = list(self.detections.all())
        return min((d.effective_priority for d in detections), default=None)

    @property
    def estimated_cost(self):
        costs = [d.estimated_repair_cost for d in self.detections.all() if d.estimated_repair_cost is not None]
        return sum(costs) if costs else None

    @property
    def accurate_votes(self):
        return self.votes.filter(kind="accurate").count()

    @property
    def spam_flags(self):
        return self.votes.filter(kind="spam").count()

    def can_vote(self, user):
        """Citizens can vote on other people's reports while they are still open."""
        return (
            user.is_authenticated
            and getattr(user, "role", None) == "citizen"
            and self.user_id != user.id
            and self.status not in (ReportStatus.REPAIRED, ReportStatus.REJECTED)
            and not self.is_spam
        )

    @property
    def can_owner_delete(self):
        # Once repair work is planned, deleting would pull damages out of repair tasks.
        return self.status not in (ReportStatus.SCHEDULED_FOR_REPAIR, ReportStatus.REPAIRED)

    def save(self, *args, **kwargs):
        self.geom = {
            "type": "Point",
            "coordinates": [float(self.longitude), float(self.latitude)],
        }
        super().save(*args, **kwargs)

    def as_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": self.geom,
            "properties": {
                "id": str(self.id),
                "status": self.status,
                "status_label": self.get_status_display(),
                "street_name": self.street_name,
                "district": self.district,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "image": self.annotated_image.url if self.annotated_image else "",
                "repaired": self.status == ReportStatus.REPAIRED,
                "accurate_votes": getattr(self, "accurate_count", 0),
                # Same rule as repairs.services.reservable_reports: verified and nobody repairing it yet.
                "reservable": (
                    self.status == ReportStatus.VERIFIED and not self.is_spam and not hasattr(self, "repair_task")
                ),
            },
        }

    def approved_repairs(self):
        from repairs.models import RepairTask, TaskStatus

        return (
            RepairTask.objects.filter(damages__report=self, status=TaskStatus.APPROVED)
            .distinct()
            .select_related("team", "assigned_to")
            .prefetch_related("photos")
        )


class ReportHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        RoadReport,
        on_delete=models.CASCADE,
        related_name="history",
        db_column="report_id",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_status_changes",
        db_column="changed_by_user_id",
    )
    old_status = models.CharField(max_length=32, choices=ReportStatus.choices, blank=True)
    new_status = models.CharField(max_length=32, choices=ReportStatus.choices)
    change_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report_id} {self.old_status} → {self.new_status}"


class SubmissionLog(models.Model):
    """One row per report or confirmation a user sends; the rate limit counts these.

    Kept separately from reports so that deleting a report doesn't free up a slot.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "report_submissions"
        ordering = ["-created_at"]


class ReportConfirmation(models.Model):
    """Another citizen's photo of a problem that was already reported nearby."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(RoadReport, on_delete=models.CASCADE, related_name="confirmations")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="report_confirmations"
    )
    photo = models.ImageField(upload_to="reports/confirmations/")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_accuracy_m = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_confirmations"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["report", "user"], name="one_confirmation_per_user")]


class VoteKind(models.TextChoices):
    ACCURATE = "accurate", _("Accurate")
    SPAM = "spam", _("Spam")


class ReportVote(models.Model):
    """A citizen saying a report is accurate, or flagging it as spam for inspectors."""

    report = models.ForeignKey(RoadReport, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_votes")
    kind = models.CharField(max_length=10, choices=VoteKind.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_votes"
        constraints = [models.UniqueConstraint(fields=["report", "user"], name="one_vote_per_user")]
