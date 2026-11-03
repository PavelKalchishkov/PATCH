from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from accounts.models import ContractorProfile, User, UserRole


class StyledMixin:
    def _style(self):
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = f"{css} input".strip()


class LoginForm(StyledMixin, AuthenticationForm):
    username = forms.EmailField(label=_("Email"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class RegisterForm(StyledMixin, UserCreationForm):
    email = forms.EmailField(label=_("Email"))
    full_name = forms.CharField(max_length=150, label=_("Full name"))
    phone = forms.CharField(max_length=30, required=False, label=_("Phone (optional)"))
    role = forms.ChoiceField(
        choices=[
            (UserRole.CITIZEN, _("Citizen")),
            (UserRole.CONTRACTOR, _("Contractor")),
            (UserRole.INSPECTOR, _("Inspector (needs admin approval)")),
        ],
        label=_("Role"),
        help_text=_("Inspector accounts start as citizen accounts until an administrator approves them."),
    )
    company_name = forms.CharField(max_length=200, required=False, label=_("Company name (contractors)"))
    license_number = forms.CharField(max_length=80, required=False, label=_("License number (contractors)"))
    address = forms.CharField(max_length=255, required=False, label=_("Address (contractors)"))

    class Meta:
        model = User
        fields = ("email", "full_name", "phone", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("role") == UserRole.CONTRACTOR and not cleaned.get("company_name"):
            self.add_error("company_name", _("Company name is required for contractor accounts."))
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.full_name = self.cleaned_data["full_name"]
        user.phone = self.cleaned_data.get("phone", "")
        user.role = self.cleaned_data["role"]
        if user.role == UserRole.INSPECTOR:
            # Inspectors can verify reports, so nobody gets the role without an admin's approval.
            user.role = UserRole.CITIZEN
            user.requested_role = UserRole.INSPECTOR
        if commit:
            user.save()
            if user.role == UserRole.CONTRACTOR:
                ContractorProfile.objects.create(
                    user=user,
                    company_name=self.cleaned_data["company_name"],
                    license_number=self.cleaned_data.get("license_number", ""),
                    address=self.cleaned_data.get("address", ""),
                )
        return user


class ContractorProfileForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ("company_name", "license_number", "address", "notes")
        labels = {
            "company_name": _("Company name"),
            "license_number": _("License number"),
            "address": _("Address"),
            "notes": _("Notes"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class AccountDetailsForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("full_name", "email", "phone")
        labels = {"full_name": _("Name"), "email": _("Email"), "phone": _("Phone (optional)")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Another account already uses this email address."))
        return email


class StyledPasswordChangeForm(StyledMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class RoleChangeForm(forms.Form):
    role = forms.ChoiceField(choices=UserRole.choices, label=_("Role"))
