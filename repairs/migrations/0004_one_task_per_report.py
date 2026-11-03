from django.db import migrations

# Most advanced first: when a report has several tasks, the one furthest along is kept.
STATUS_RANK = ["approved", "completed", "in_progress", "rejected", "accepted", "assigned", "reserved", "draft"]
PRIORITY_FROM_SEVERITY = {"low": 4, "medium": 3, "high": 2, "critical": 1}


def merge_tasks_per_report(apps, schema_editor):
    RoadReport = apps.get_model("reports", "RoadReport")
    RepairTask = apps.get_model("repairs", "RepairTask")
    TaskHistory = apps.get_model("repairs", "TaskHistory")
    TaskPhoto = apps.get_model("repairs", "TaskPhoto")

    for report in RoadReport.objects.all():
        tasks = list(RepairTask.objects.filter(damages__report=report).distinct().order_by("created_at"))
        if not tasks:
            continue
        rank = {status: i for i, status in enumerate(STATUS_RANK)}
        primary = min(tasks, key=lambda t: rank.get(t.status, len(STATUS_RANK)))
        for other in tasks:
            if other.pk == primary.pk:
                continue
            TaskHistory.objects.filter(task=other).update(task=primary)
            TaskPhoto.objects.filter(task=other).update(task=primary)
            other.delete()

        detections = list(report.detections.select_related("catalog"))
        names = ", ".join(dict.fromkeys(d.catalog.name_bg for d in detections))
        place = report.street_name or report.district or "unnamed street"
        primary.report = report
        primary.title = f"{names} · {place}"[:200] if names else primary.title
        if detections:
            primary.suggested_priority = min(PRIORITY_FROM_SEVERITY.get(d.severity, 3) for d in detections)
        primary.save(update_fields=["report", "title", "suggested_priority"])
        primary.damages.set(detections)


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0003_repair_task_report"),
        ("reports", "0001_initial"),
        ("damages", "0003_fill_catalog_name_en"),
    ]
    operations = [migrations.RunPython(merge_tasks_per_report, migrations.RunPython.noop)]
