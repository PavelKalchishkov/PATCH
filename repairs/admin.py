from django.contrib import admin

from repairs.models import RepairTask, TaskHistory, TaskPhoto


class TaskHistoryInline(admin.TabularInline):
    model = TaskHistory
    extra = 0
    readonly_fields = ("changed_by", "old_status", "new_status", "change_reason", "created_at")


class TaskPhotoInline(admin.TabularInline):
    model = TaskPhoto
    extra = 0


@admin.register(RepairTask)
class RepairTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "assigned_to", "effective_priority", "created_at")
    filter_horizontal = ("damages",)
    inlines = [TaskHistoryInline, TaskPhotoInline]
