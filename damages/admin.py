from django.contrib import admin

from damages.models import BOQItem, DamageCatalog, DamageDetection


@admin.register(DamageCatalog)
class DamageCatalogAdmin(admin.ModelAdmin):
    list_display = ("damage_code", "name_bg", "unit_of_measure", "base_price_per_unit")


class BOQInline(admin.TabularInline):
    model = BOQItem
    extra = 0
    readonly_fields = ("total_line_cost",)


@admin.register(DamageDetection)
class DamageDetectionAdmin(admin.ModelAdmin):
    list_display = ("id", "catalog", "report", "severity", "confidence", "estimated_repair_cost")
    inlines = [BOQInline]


@admin.register(BOQItem)
class BOQItemAdmin(admin.ModelAdmin):
    list_display = ("material_or_service", "quantity", "unit", "unit_rate", "total_line_cost")
    readonly_fields = ("total_line_cost",)
