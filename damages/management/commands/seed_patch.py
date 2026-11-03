from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import ContractorProfile, ContractorTeam, User, UserRole
from damages.models import DamageCatalog


CATALOG = [
    ("POTHOLE_DEEP", "Дълбока дупка", "кв.м", "42.50", "Cut-out and hot-mix asphalt patch"),
    ("POTHOLE_SHALLOW", "Плитка дупка", "кв.м", "28.00", "Cold mix or spray-injection patch"),
    ("CRACK_NETWORK", "Мрежовидни пукнатини", "кв.м", "19.40", "Surface dressing and crack sealing"),
    ("CRACK_LONGITUDINAL", "Надлъжна пукнатина", "л.м", "6.80", "Rout and seal"),
    ("CURB_BROKEN", "Счупен бордюр", "л.м", "54.00", "Kerbstone replacement"),
    ("RUTTING", "Колея", "кв.м", "36.20", "Milling and overlay"),
    ("SURFACE_RAVELING", "Изронена настилка", "кв.м", "22.10", "Slurry seal"),
]


ENGLISH_NAMES = {
    "POTHOLE_DEEP": "Deep pothole",
    "POTHOLE_SHALLOW": "Shallow pothole",
    "CRACK_NETWORK": "Alligator cracking",
    "CRACK_LONGITUDINAL": "Longitudinal crack",
    "CURB_BROKEN": "Broken curb",
    "RUTTING": "Rutting",
    "SURFACE_RAVELING": "Surface raveling",
}


class Command(BaseCommand):
    help = "Load damage catalog and demo accounts for PATCH."

    def add_arguments(self, parser):
        parser.add_argument(
            "--catalog-only",
            action="store_true",
            help="Only load the damage catalog. Use this on a public server: the demo accounts have known passwords.",
        )

    def handle(self, *args, **options):
        for code, name, unit, price, technique in CATALOG:
            DamageCatalog.objects.update_or_create(
                damage_code=code,
                defaults={
                    "name_bg": name,
                    "name_en": ENGLISH_NAMES.get(code, ""),
                    "unit_of_measure": unit,
                    "base_price_per_unit": Decimal(price),
                    "default_repair_technique": technique,
                    "description": name,
                },
            )
        if options["catalog_only"]:
            self.stdout.write(self.style.SUCCESS(f"Damage catalog loaded ({len(CATALOG)} types)."))
            return
        users = [
            ("admin@patch.local", "PATCH Admin", "admin12345", UserRole.ADMIN, True),
            ("inspector@patch.local", "Nina Inspector", "inspector123", UserRole.INSPECTOR, True),
            ("citizen@patch.local", "Ivan Citizen", "citizen123", UserRole.CITIZEN, False),
            ("contractor@patch.local", "Geo Asphalt", "contractor123", UserRole.CONTRACTOR, False),
        ]
        created_users = {}
        for email, name, password, role, staff in users:
            user, made = User.objects.get_or_create(
                email=email,
                defaults={"full_name": name, "role": role, "is_staff": staff, "is_superuser": role == UserRole.ADMIN},
            )
            if made:
                user.set_password(password)
                user.save()
            created_users[role] = user
        contractor = created_users[UserRole.CONTRACTOR]
        profile, _ = ContractorProfile.objects.get_or_create(
            user=contractor,
            defaults={"company_name": "Geo Asphalt Ltd", "license_number": "RD-441", "address": "Sofia"},
        )
        ContractorTeam.objects.get_or_create(contractor=profile, name="Night crew A")
        self.stdout.write(self.style.SUCCESS("Catalog and demo users are ready."))
        self.stdout.write("admin@patch.local / admin12345")
        self.stdout.write("inspector@patch.local / inspector123")
        self.stdout.write("citizen@patch.local / citizen123")
        self.stdout.write("contractor@patch.local / contractor123")
