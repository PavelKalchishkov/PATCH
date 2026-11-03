from django.db import transaction

from damages.models import PRIORITY_FROM_SEVERITY
from repairs.models import RepairTask, TaskHistory, TaskStatus
from reports.models import ReportStatus, RoadReport
from reports.services import transition_report


def log_task(task: RepairTask, new_status: str, user=None, reason: str = "") -> RepairTask:
    old_status = task.status
    task.status = new_status
    task.save(update_fields=["status", "updated_at"])
    TaskHistory.objects.create(
        task=task,
        changed_by=user if getattr(user, "is_authenticated", False) else None,
        old_status=old_status,
        new_status=new_status,
        change_reason=reason,
    )
    return task


def sync_priority_from_damages(task: RepairTask) -> None:
    severities = list(task.damages.values_list("severity", flat=True))
    if not severities:
        return
    suggested = min(PRIORITY_FROM_SEVERITY.get(s, 3) for s in severities)
    task.suggested_priority = suggested
    task.save(update_fields=["suggested_priority"])


def mark_related_reports(task: RepairTask, status: str, user, reason: str) -> None:
    if task.report_id:
        transition_report(task.report, status, user=user, reason=reason)


def reservable_reports():
    """Verified reports that nobody is repairing yet; each is one job for one contractor."""
    return (
        RoadReport.objects.filter(status=ReportStatus.VERIFIED, is_spam=False, repair_task__isnull=True)
        .prefetch_related("detections__catalog")
    )


class AlreadyReserved(Exception):
    pass


def _task_title(report):
    names = ", ".join(dict.fromkeys(d.catalog.name_bg for d in report.detections.all()))
    place = report.street_name or report.district or "unnamed street"
    return (f"{names} · {place}" if names else place)[:200]


def _task_description(report):
    techniques = dict.fromkeys(
        d.catalog.default_repair_technique for d in report.detections.all() if d.catalog.default_repair_technique
    )
    return "; ".join(techniques)


@transaction.atomic
def create_task_for_report(report_id, *, created_by, assigned_to=None, team=None, title="", description="",
                           priority_override=None, status=TaskStatus.RESERVED, reason="") -> RepairTask:
    # Lock the report so it can't get two repair tasks at once.
    report = RoadReport.objects.select_for_update().get(pk=report_id)
    if not reservable_reports().filter(pk=report.pk).exists():
        raise AlreadyReserved
    task = RepairTask.objects.create(
        report=report,
        title=title or _task_title(report),
        description=description or _task_description(report),
        team=team,
        assigned_to=assigned_to,
        created_by=created_by,
        priority_override=priority_override,
    )
    task.damages.set(report.detections.all())
    sync_priority_from_damages(task)
    log_task(task, status, user=created_by, reason=reason)
    transition_report(report, ReportStatus.SCHEDULED_FOR_REPAIR, user=created_by, reason=reason)
    return task


def reserve_report(report_id, contractor) -> RepairTask:
    profile = getattr(contractor, "contractor_profile", None)
    team = profile.teams.filter(is_active=True).first() if profile else None
    return create_task_for_report(
        report_id, created_by=contractor, assigned_to=contractor, team=team,
        status=TaskStatus.RESERVED, reason="Reserved by contractor",
    )


@transaction.atomic
def release_task(task: RepairTask, contractor) -> None:
    report = task.report
    task.delete()
    if report and report.status == ReportStatus.SCHEDULED_FOR_REPAIR:
        transition_report(report, ReportStatus.VERIFIED, user=contractor, reason="Contractor released the reservation")
