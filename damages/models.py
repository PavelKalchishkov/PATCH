import uuid
from decimal import Decimal

from django.db import models
from django.db.models import F
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from reports.models import RoadReport


class SeverityLevel(models.TextChoices):
    LOW = "low", _("Low")
    MEDIUM = "medium", _("Medium")
    HIGH = "high", _("High")
    CRITICAL = "critical", _("Critical")


PRIORITY_FROM_SEVERITY = {
    SeverityLevel.LOW: 4,
    SeverityLevel.MEDIUM: 3,
    SeverityLevel.HIGH: 2,
    SeverityLevel.CRITICAL: 1,
}


class DamageCatalog(models.Model):
    damage_code = models.CharField(max_length=50, unique=True)
    name_bg = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    unit_of_measure = models.CharField(max_length=20)
    base_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    default_repair_technique = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "damage_catalog"
        ordering = ["damage_code"]

    def __str__(self):
        return f"{self.damage_code} — {self.name_bg}"

    @property
    def name(self):
        """Name in the active UI language, falling back to Bulgarian."""
        if get_language() and get_language().startswith("en") and self.name_en:
            return self.name_en
        return self.name_bg


class DamageDetection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        RoadReport,
        on_delete=models.CASCADE,
        related_name="detections",
        db_column="report_id",
    )
    catalog = models.ForeignKey(
        DamageCatalog,
        on_delete=models.RESTRICT,
        related_name="detections",
        db_column="catalog_id",
    )
    confidence = models.DecimalField(max_digits=4, decimal_places=3)
    severity = models.CharField(
        max_length=16,
        choices=SeverityLevel.choices,
        default=SeverityLevel.MEDIUM,
    )
    raw_bbox = models.JSONField()
    estimated_area_sqm = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    estimated_depth_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estimated_repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_confirmed_by_human = models.BooleanField(default=False)
    suggested_priority = models.PositiveSmallIntegerField(default=3)
    priority_override = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "damage_detections"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.catalog.damage_code} on {self.report_id}"

    @property
    def effective_priority(self):
        return self.priority_override or self.suggested_priority

    def save(self, *args, **kwargs):
        self.suggested_priority = PRIORITY_FROM_SEVERITY.get(self.severity, 3)
        # Once a cost estimate (BOQ) exists, its total is the cost; before that, a rough area x unit price.
        boq_total = None
        if self.pk:
            lines = self.boq_items.values_list("quantity", "unit_rate")
            if lines:
                boq_total = sum((quantity * rate for quantity, rate in lines), Decimal("0"))
        if boq_total is not None:
            self.estimated_repair_cost = boq_total
        elif self.estimated_area_sqm is not None and self.catalog_id:
            self.estimated_repair_cost = self.estimated_area_sqm * self.catalog.base_price_per_unit
        super().save(*args, **kwargs)


class BOQItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    detection = models.ForeignKey(
        DamageDetection,
        on_delete=models.CASCADE,
        related_name="boq_items",
        db_column="detection_id",
    )
    material_or_service = models.CharField(max_length=150)
    quantity = models.DecimalField(max_digits=8, decimal_places=3)
    unit = models.CharField(max_length=20)
    unit_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_line_cost = models.GeneratedField(
        expression=F("quantity") * F("unit_rate"),
        output_field=models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "boq_items"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.material_or_service} × {self.quantity}"
