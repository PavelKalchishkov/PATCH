from django.contrib import admin

from reports.models import ReportHistory, RoadReport


class ReportHistoryInline(admin.TabularInline):
    model = ReportHistory
    extra = 0
    readonly_fields = ("changed_by", "old_status", "new_status", "change_reason", "created_at")


@admin.register(RoadReport)
class RoadReportAdmin(admin.ModelAdmin):
    list_display = ("id", "street_name", "district", "status", "user", "created_at")
    list_filter = ("status", "is_spam", "is_duplicate")
    inlines = [ReportHistoryInline]


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ("report", "old_status", "new_status", "changed_by", "created_at")
