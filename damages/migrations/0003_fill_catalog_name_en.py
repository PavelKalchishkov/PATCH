from django.db import migrations

ENGLISH_NAMES = {
    "CRACK_LONGITUDINAL": "Longitudinal crack",
    "CRACK_NETWORK": "Alligator cracking",
    "CURB_BROKEN": "Broken curb",
    "POTHOLE_DEEP": "Deep pothole",
    "POTHOLE_SHALLOW": "Shallow pothole",
    "RUTTING": "Rutting",
    "SURFACE_RAVELING": "Surface raveling",
}


def fill_english_names(apps, schema_editor):
    DamageCatalog = apps.get_model("damages", "DamageCatalog")
    for code, name in ENGLISH_NAMES.items():
        DamageCatalog.objects.filter(damage_code=code, name_en="").update(name_en=name)


class Migration(migrations.Migration):
    dependencies = [("damages", "0002_catalog_name_en")]
    operations = [migrations.RunPython(fill_english_names, migrations.RunPython.noop)]
