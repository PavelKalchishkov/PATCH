import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from reports.models import RoadReport


class VisionJobStatus(models.TextChoices):
    QUEUED = "queued", _("Queued")
    RUNNING = "running", _("Running")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")


class VisionJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(RoadReport, on_delete=models.CASCADE, related_name="vision_jobs")
    status = models.CharField(
        max_length=16,
        choices=VisionJobStatus.choices,
        default=VisionJobStatus.QUEUED,
    )
    model_name = models.CharField(max_length=80, default="patch-cv-v1")
    blur_faces = models.BooleanField(default=True)
    blur_plates = models.BooleanField(default=True)
    detections_written = models.PositiveIntegerField(default=0)
    log = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Vision {str(self.id)[:8]} ({self.status})"
