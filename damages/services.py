from decimal import Decimal

from damages.models import BOQItem, DamageDetection


def generate_boq(detection: DamageDetection) -> list[BOQItem]:
    detection.boq_items.all().delete()
    area = detection.estimated_area_sqm or Decimal("1.000")
    catalog = detection.catalog
    items = [
        {
            "material_or_service": f"{catalog.name_bg} repair — {catalog.default_repair_technique or 'standard patch'}",
            "quantity": area,
            "unit": catalog.unit_of_measure,
            "unit_rate": catalog.base_price_per_unit,
        },
        {
            "material_or_service": "Traffic management and site preparation",
            "quantity": Decimal("1.000"),
            "unit": "ls",
            "unit_rate": Decimal("85.00"),
        },
    ]
    created = [BOQItem.objects.create(detection=detection, **row) for row in items]
    total = sum((item.quantity * item.unit_rate for item in created), Decimal("0"))
    detection.estimated_repair_cost = total
    detection.save(update_fields=["estimated_repair_cost"])
    return created
