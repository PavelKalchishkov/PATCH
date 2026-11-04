import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    CITIZEN = "citizen", _("Citizen")
    INSPECTOR = "inspector", _("Inspector")
    ADMIN = "admin", _("Administrator")
    CONTRACTOR = "contractor", _("Contractor")


SPAM_STRIKE_LIMIT = 3


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name="Administrator", password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CITIZEN)
    phone = models.CharField(max_length=30, blank=True)
    # A role the user asked for at sign-up that an admin still has to approve.
    requested_role = models.CharField(max_length=20, choices=UserRole.choices, blank=True)
    # Reports of this user that inspectors marked as spam; at SPAM_STRIKE_LIMIT they can't report any more.
    spam_strikes = models.PositiveSmallIntegerField(default=0)
    # Set when the user clicks the link we email them; cleared again if they change their email.
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def is_citizen(self):
        return self.role == UserRole.CITIZEN

    @property
    def is_inspector(self):
        return self.role == UserRole.INSPECTOR

    @property
    def is_admin_role(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_contractor(self):
        return self.role == UserRole.CONTRACTOR

    @property
    def reporting_banned(self):
        return self.spam_strikes >= SPAM_STRIKE_LIMIT

    @property
    def initials(self):
        return "".join(part[0] for part in self.full_name.split()[:2]).upper() or "?"

    @property
    def has_pending_role_request(self):
        return bool(self.requested_role) and self.requested_role != self.role

    @property
    def can_moderate(self):
        return self.role in {UserRole.INSPECTOR, UserRole.ADMIN} or self.is_superuser


class ContractorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="contractor_profile",
        limit_choices_to={"role": UserRole.CONTRACTOR},
    )
    company_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=80, blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contractor_profiles"

    def __str__(self):
        return self.company_name


class ContractorTeam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contractor = models.ForeignKey(
        ContractorProfile,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    name = models.CharField(max_length=150)
    members = models.ManyToManyField(User, related_name="repair_teams", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contractor_teams"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.contractor.company_name})"
