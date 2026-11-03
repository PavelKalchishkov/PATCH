from reports.models import ReportHistory, RoadReport


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
