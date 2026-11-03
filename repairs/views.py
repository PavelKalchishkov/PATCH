from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from accounts.mixins import role_required
from accounts.models import ContractorTeam, UserRole
from repairs.models import CONTRACTOR_STAGES, PhotoKind, RepairTask, TaskPhoto, TaskStatus
from repairs.services import (
    AlreadyReserved,
    log_task,
    mark_related_reports,
    release_task,
    create_task_for_report,
    reservable_reports,
    reserve_report,
)
from reports.models import ReportStatus, RoadReport
from reports.photo_quality import validate_photo


@role_required(UserRole.INSPECTOR, UserRole.ADMIN, UserRole.CONTRACTOR)
def task_list(request):
    tasks = RepairTask.objects.select_related("team", "assigned_to")
    if request.user.role != UserRole.CONTRACTOR:
        return render(request, "repairs/list.html", {"tasks": tasks})

    own = list(tasks.filter(assigned_to=request.user).prefetch_related("damages__report", "damages__catalog"))
    labels = {"reserved": _("Reserved"), "in_progress": _("In progress"), "finished": _("Finished")}
    stages = [
        {"key": key, "label": labels[key], "tasks": [t for t in own if t.status in statuses]}
        for key, statuses in CONTRACTOR_STAGES.items()
    ]
    active = request.GET.get("stage")
    if active not in labels:
        # Open the first stage that has work in it.
        active = next((s["key"] for s in stages if s["tasks"]), "reserved")
    return render(request, "repairs/board.html", {"stages": stages, "active": active})


@role_required(UserRole.CONTRACTOR)
def available_work(request):
    reports = sorted(reservable_reports().order_by("created_at"), key=lambda r: r.priority or 3)
    return render(request, "repairs/available.html", {"reports": reports})


@role_required(UserRole.CONTRACTOR)
def reserve(request, report_id):
    if request.method != "POST":
        return redirect("repairs:available")
    report = get_object_or_404(RoadReport, pk=report_id)
    try:
        task = reserve_report(report.pk, request.user)
    except AlreadyReserved:
        messages.error(request, _("Someone else has already reserved this repair."))
        return redirect("repairs:available")
    messages.success(request, _("Repair reserved. It is now in your repairs under Reserved."))
    return redirect("repairs:detail", task_id=task.id)


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def create_task(request):
    reports = reservable_reports().order_by("created_at")
    teams = ContractorTeam.objects.filter(is_active=True).select_related("contractor__user")
    errors = []
    if request.method == "POST":
        report_id = request.POST.get("report")
        team = teams.filter(pk=request.POST.get("team") or None).first()
        override = request.POST.get("priority_override")
        if not report_id:
            errors.append(_("Choose the report to repair."))
        if not team:
            errors.append(_("Choose the contractor team that will do the repair."))
        if not errors:
            try:
                task = create_task_for_report(
                    report_id,
                    created_by=request.user,
                    team=team,
                    assigned_to=team.contractor.user,
                    title=request.POST.get("title", "").strip(),
                    description=request.POST.get("description", "").strip(),
                    priority_override=int(override) if override else None,
                    status=TaskStatus.ASSIGNED,
                    reason="Assigned to contractor team",
                )
            except (AlreadyReserved, RoadReport.DoesNotExist):
                errors.append(_("That report is no longer available. It may have been reserved by a contractor."))
            else:
                messages.success(request, _("Repair task created."))
                return redirect("repairs:detail", task_id=task.id)
    return render(request, "repairs/create.html", {"reports": reports, "teams": teams, "errors": errors})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(
        RepairTask.objects.prefetch_related("damages__catalog", "history", "photos"),
        pk=task_id,
    )
    if request.user.role == UserRole.CONTRACTOR and task.assigned_to_id != request.user.id:
        messages.error(request, _("This task is not assigned to you."))
        return redirect("repairs:list")
    return render(request, "repairs/detail.html", {"task": task, "photo_kinds": PhotoKind.choices})


@role_required(UserRole.CONTRACTOR)
def transition_own_task(request, task_id, action):
    task = get_object_or_404(RepairTask, pk=task_id, assigned_to=request.user)
    if request.method != "POST":
        return redirect("repairs:detail", task_id=task.id)

    if action == "release":
        if task.status != TaskStatus.RESERVED:
            messages.error(request, _("Only reservations that have not started can be released."))
            return redirect("repairs:detail", task_id=task.id)
        release_task(task, request.user)
        messages.success(request, _("Reservation released. The damage is available to other contractors again."))
        return redirect("repairs:list")

    # action -> (allowed current statuses, new status, default reason, flash message)
    mapping = {
        "start": (CONTRACTOR_STAGES["reserved"], TaskStatus.IN_PROGRESS, "Work started", _("Work started.")),
        "finish": (CONTRACTOR_STAGES["in_progress"], TaskStatus.COMPLETED, "Contractor marked the work finished",
                   _("Marked as finished. An inspector will review it.")),
    }
    if action not in mapping:
        messages.error(request, _("Unknown action."))
        return redirect("repairs:detail", task_id=task.id)
    allowed, new_status, reason, message = mapping[action]
    if task.status not in allowed:
        messages.error(request, _("This task can't do that from its current status."))
        return redirect("repairs:detail", task_id=task.id)
    if action == "finish":
        # A finished repair must be shown: the photo is what inspectors approve and the public sees.
        upload = request.FILES.get("after_photo")
        if upload:
            problem = _photo_problem(upload)
            if problem:
                messages.error(request, problem)
                return redirect("repairs:detail", task_id=task.id)
            _save_photo(task, upload, PhotoKind.AFTER, request.user)
        elif not task.current_after_photo():
            messages.error(request, _("Add a photo of the finished repair before marking it finished."))
            return redirect("repairs:detail", task_id=task.id)
    log_task(task, new_status, user=request.user, reason=request.POST.get("reason") or reason)
    messages.success(request, message)
    return redirect("repairs:detail", task_id=task.id)


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def approve_task(request, task_id):
    task = get_object_or_404(RepairTask, pk=task_id)
    action = request.POST.get("action")
    if request.method != "POST" or action not in ("approve", "reject"):
        return redirect("repairs:detail", task_id=task.id)
    if task.status != TaskStatus.COMPLETED:
        messages.error(request, _("Only repairs the contractor has marked finished can be approved or sent back."))
        return redirect("repairs:detail", task_id=task.id)
    reason = request.POST.get("reason", "").strip()
    if action == "reject" and not reason:
        messages.error(request, _("Add a note telling the contractor what to fix before sending the repair back."))
        return redirect("repairs:detail", task_id=task.id)
    if action == "approve":
        log_task(task, TaskStatus.APPROVED, user=request.user, reason=reason or "Repair approved")
        mark_related_reports(task, ReportStatus.REPAIRED, request.user, "Repair approved")
    else:
        log_task(task, TaskStatus.REJECTED, user=request.user, reason=reason or "Repair sent back")
    return redirect("repairs:approval_result", task_id=task.id)


@role_required(UserRole.INSPECTOR, UserRole.ADMIN)
def approval_result(request, task_id):
    task = get_object_or_404(
        RepairTask.objects.select_related("assigned_to", "team").prefetch_related("damages__report", "damages__catalog"),
        pk=task_id,
    )
    if task.status not in (TaskStatus.APPROVED, TaskStatus.REJECTED):
        return redirect("repairs:detail", task_id=task.id)
    waiting = RepairTask.objects.filter(status=TaskStatus.COMPLETED).order_by("updated_at")
    return render(
        request,
        "repairs/approval_result.html",
        {
            "task": task,
            "approved": task.status == TaskStatus.APPROVED,
            "last_change": task.history.filter(new_status=task.status).select_related("changed_by").first(),
            "next_task": waiting.first(),
            "remaining": waiting.count(),
        },
    )


@role_required(UserRole.CONTRACTOR, UserRole.INSPECTOR, UserRole.ADMIN)
def upload_photo(request, task_id):
    task = get_object_or_404(RepairTask, pk=task_id)
    if request.user.role == UserRole.CONTRACTOR and task.assigned_to_id != request.user.id:
        messages.error(request, _("This task is not assigned to you."))
        return redirect("repairs:list")
    if request.method == "POST" and request.FILES.get("image"):
        problem = _photo_problem(request.FILES["image"])
        if problem:
            messages.error(request, problem)
            return redirect("repairs:detail", task_id=task.id)
        kind = request.POST.get("kind")
        _save_photo(task, request.FILES["image"], kind if kind in PhotoKind.values else PhotoKind.OTHER, request.user)
        messages.success(request, _("Photo attached."))
    return redirect("repairs:detail", task_id=task.id)


def _photo_problem(upload):
    """Why an uploaded repair photo can't be used (not an image, black, blurry...), or None."""
    try:
        forms.ImageField().clean(upload)
        validate_photo(upload)
    except forms.ValidationError as error:
        if error.code == "invalid_image" or not error.messages:
            return _("That file isn't a photo we can read. Take or choose the photo again.")
        return error.messages[0]
    return None


def _save_photo(task, upload, kind, user):
    photo = TaskPhoto.objects.create(task=task, image=upload, kind=kind, uploaded_by=user)
    photo.image_url = photo.image.url
    photo.save(update_fields=["image_url"])
    return photo
