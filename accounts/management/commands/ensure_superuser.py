"""Create the first administrator from environment variables, if it doesn't exist yet.

Meant for hosts like Railway where you can set variables in the dashboard but may not have
a terminal. Set DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD and (optionally)
DJANGO_SUPERUSER_FULL_NAME, deploy once, then remove the password variable.
Runs on every deploy and does nothing when the variables are missing or the account exists,
so it never changes an existing password.
"""
import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Create the administrator named in DJANGO_SUPERUSER_* variables, if it doesn't exist."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        full_name = os.environ.get("DJANGO_SUPERUSER_FULL_NAME", "").strip() or "Administrator"
        if not email or not password:
            self.stdout.write("ensure_superuser: no DJANGO_SUPERUSER_EMAIL/PASSWORD set, nothing to do.")
            return
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(f"ensure_superuser: {email} already exists, left unchanged.")
            return
        try:
            validate_password(password)
        except ValidationError as error:
            # Don't stop the deploy over it; just say why no account was made.
            self.stderr.write(f"ensure_superuser: password not accepted ({' '.join(error.messages)}), no account created.")
            return
        user = User.objects.create_superuser(email=email, full_name=full_name, password=password)
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        self.stdout.write(self.style.SUCCESS(f"ensure_superuser: administrator {email} created."))
