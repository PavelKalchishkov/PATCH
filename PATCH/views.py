from django.shortcuts import render

from reports.models import ReportStatus, RoadReport


def home(request):
    stats = {
        "reports": RoadReport.objects.count(),
        "open": RoadReport.objects.exclude(status__in=[ReportStatus.REPAIRED, ReportStatus.REJECTED]).count(),
        "repaired": RoadReport.objects.filter(status=ReportStatus.REPAIRED).count(),
    }
    latest = RoadReport.objects.select_related("user")[:6]
    return render(request, "home.html", {"stats": stats, "latest": latest})
