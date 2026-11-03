from accounts.mixins import role_required
from accounts.models import UserRole
from django.shortcuts import render

from vision.models import VisionJob


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def job_list(request):
    jobs = VisionJob.objects.select_related("report")[:100]
    return render(request, "vision/jobs.html", {"jobs": jobs})
