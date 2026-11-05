import logging

from django.db import transaction

from reports.models import ReportHistory, RoadReport

logger = logging.getLogger(__name__)


def transition_report(report: RoadReport, new_status: str, user=None, reason: str = "") -> RoadReport:
    old_status = report.status
    if old_status == new_status and not reason:
        return report
    report.status = new_status
    report.save(update_fields=["status", "updated_at"])
    ReportHistory.objects.create(
        report=report,
        changed_by=user if getattr(user, "is_authenticated", False) else None,
        old_status=old_status,
        new_status=new_status,
        change_reason=reason,
    )
    return report


def delete_report_completely(report: RoadReport) -> None:
    """Delete a report with everything hanging off it, including the photo files.

    The database removes damages, cost estimates, confirmations, votes and the repair task
    (with its history and photo records) through cascades; the files themselves are removed
    only once that has been committed, so a failed delete never loses photos.
    """
    from repairs.models import TaskPhoto

    files = [f for f in (report.original_image, report.annotated_image) if f]
    files += [c.photo for c in report.confirmations.all() if c.photo]
    files += [p.image for p in TaskPhoto.objects.filter(task__report=report) if p.image]
    names = [(f.storage, f.name) for f in files]

    def remove_files():
        for storage, name in names:
            try:
                storage.delete(name)
            except OSError:
                # e.g. already gone, or briefly locked on Windows; the report itself is deleted either way.
                logger.warning("Could not delete photo file %s", name)

    with transaction.atomic():
        report.delete()
        transaction.on_commit(remove_files)
