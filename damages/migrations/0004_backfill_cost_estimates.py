from decimal import Decimal

from django.db import migrations

# Same lines as damages.services.generate_boq at the time of writing.
SITE_PREPARATION = ("Traffic management and site preparation", Decimal("1.000"), "ls", Decimal("85.00"))


def backfill(apps, schema_editor):
    DamageDetection = apps.get_model("damages", "DamageDetection")
    BOQItem = apps.get_model("damages", "BOQItem")
    for detection in DamageDetection.objects.filter(boq_items__isnull=True).select_related("catalog"):
        catalog = detection.catalog
        rows = [
            (f"{catalog.name_bg} repair — {catalog.default_repair_technique or 'standard patch'}",
             detection.estimated_area_sqm or Decimal("1.000"), catalog.unit_of_measure, catalog.base_price_per_unit),
            SITE_PREPARATION,
        ]
        for name, quantity, unit, rate in rows:
            BOQItem.objects.create(detection=detection, material_or_service=name, quantity=quantity, unit=unit, unit_rate=rate)
        detection.estimated_repair_cost = sum((quantity * rate for _, quantity, _, rate in rows), Decimal("0"))
        detection.save(update_fields=["estimated_repair_cost"])


class Migration(migrations.Migration):
    dependencies = [("damages", "0003_fill_catalog_name_en")]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
