from django.contrib import admin

from vision.models import VisionJob


@admin.register(VisionJob)
class VisionJobAdmin(admin.ModelAdmin):
    list_display = ("id", "report", "status", "detections_written", "created_at")
    readonly_fields = ("log", "started_at", "finished_at")
