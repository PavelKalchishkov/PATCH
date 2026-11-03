import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import ContractorTeam
from damages.models import DamageDetection
from reports.models import RoadReport


class TaskStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    RESERVED = "reserved", _("Reserved")
    ASSIGNED = "assigned", _("Assigned")
    ACCEPTED = "accepted", _("Accepted")
    IN_PROGRESS = "in_progress", _("In progress")
    COMPLETED = "completed", _("Completed")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


# How a contractor sees their work: every task status falls into one of three stages.
CONTRACTOR_STAGES = {
    "reserved": (TaskStatus.RESERVED, TaskStatus.ASSIGNED, TaskStatus.ACCEPTED),
    "in_progress": (TaskStatus.IN_PROGRESS, TaskStatus.REJECTED),
    "finished": (TaskStatus.COMPLETED, TaskStatus.APPROVED),
}


class RepairTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # A report is repaired as one job: one task per report, covering all of its damages.
    report = models.OneToOneField(
        RoadReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="repair_task",
    )
    damages = models.ManyToManyField(DamageDetection, related_name="repair_tasks")
    team = models.ForeignKey(
        ContractorTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_repair_tasks",
        limit_choices_to={"role": "contractor"},
    )
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.DRAFT)
    suggested_priority = models.PositiveSmallIntegerField(default=3)
    priority_override = models.PositiveSmallIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_repair_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repair_tasks"
        ordering = ["priority_override", "suggested_priority", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def effective_priority(self):
        return self.priority_override or self.suggested_priority

    @property
    def send_back_reason(self):
        """The inspector's note from the latest time this repair was sent back."""
        row = self.history.filter(new_status=TaskStatus.REJECTED).order_by("-created_at").first()
        return row.change_reason if row else ""

    def current_after_photo(self):
        """The newest "after" photo taken since work last (re)started, or None.

        A photo from before an inspector sent the repair back shows the rejected work, so it doesn't count.
        """
        restarted = (
            self.history.filter(new_status__in=(TaskStatus.IN_PROGRESS, TaskStatus.REJECTED))
            .order_by("-created_at")
            .values_list("created_at", flat=True)
            .first()
        )
        photos = self.photos.filter(kind=PhotoKind.AFTER).order_by("-created_at")
        if restarted:
            photos = photos.filter(created_at__gte=restarted)
        return photos.first()

    @property
    def contractor_stage(self):
        for stage, statuses in CONTRACTOR_STAGES.items():
            if self.status in statuses:
                return stage
        return None


class TaskHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(RepairTask, on_delete=models.CASCADE, related_name="history")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_status_changes",
    )
    old_status = models.CharField(max_length=20, choices=TaskStatus.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=TaskStatus.choices)
    change_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_history"
        ordering = ["-created_at"]


class PhotoKind(models.TextChoices):
    BEFORE = "before", _("Before")
    AFTER = "after", _("After")
    OTHER = "other", _("Other")


class TaskPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(RepairTask, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="repairs/photos/")
    image_url = models.TextField(blank=True)
    kind = models.CharField(max_length=16, choices=PhotoKind.choices, default=PhotoKind.OTHER)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_photos"
        ordering = ["-created_at"]
