from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from accounts.mixins import role_required
from accounts.models import UserRole
from damages.models import DamageCatalog, DamageDetection
from reports.models import ReportStatus, RoadReport


def public_map(request):
    return render(request, "damages/map.html")


def map_geojson(request):
    reports = (
        RoadReport.objects.exclude(status=ReportStatus.REJECTED).exclude(is_spam=True).select_related("repair_task")
        .annotate(accurate_count=Count("votes", filter=Q(votes__kind="accurate")))
    )
    features = [report.as_geojson_feature() for report in reports]
    return JsonResponse({"type": "FeatureCollection", "features": features})


def public_register(request):
    # One row per report: a report is repaired as a single job, whatever damages it shows.
    reports = (
        RoadReport.objects.exclude(status=ReportStatus.REJECTED)
        .exclude(is_spam=True)
        .filter(detections__isnull=False)
        .distinct()
        .prefetch_related("detections__catalog")
    )
    return render(request, "damages/register.html", {"reports": reports})


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def catalog_list(request):
    return render(request, "damages/catalog.html", {"items": DamageCatalog.objects.all()})


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def override_priority(request, detection_id):
    detection = get_object_or_404(DamageDetection, pk=detection_id)
    if request.method == "POST":
        value = request.POST.get("priority_override")
        detection.priority_override = int(value) if value else None
        detection.save(update_fields=["priority_override"])
        messages.success(request, _("Priority override saved."))
    return redirect("reports:detail", report_id=detection.report_id)
