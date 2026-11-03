import time

from django import forms
from django.utils.translation import gettext_lazy as _

from reports.models import RoadReport
from reports.photo_quality import validate_photo


# A report must be sent soon after its photo is taken on the report page; the clock
# allowance covers phones whose time is slightly off.
MAX_PHOTO_AGE_SECONDS = 15 * 60
CLOCK_SKEW_SECONDS = 5 * 60


class CameraCaptureMixin:
    """Validation shared by everything sent from the camera page: a fresh photo with a location."""

    LOCATION_FIELDS = ("latitude", "longitude", "location_accuracy")

    def _setup_capture_messages(self, photo_field):
        self.fields[photo_field].required = True
        self.fields[photo_field].error_messages["required"] = _("Take a photo of the damage with the camera.")
        self.fields[photo_field].error_messages["invalid_image"] = _("The photo couldn't be read. Please take it again.")
        location_missing = _("Your location wasn't captured. Allow location access and take the photo again.")
        for name in self.LOCATION_FIELDS:
            self.fields[name].error_messages["required"] = location_missing
            self.fields[name].error_messages["invalid"] = location_missing
        photo_time = _("Take the photo with the camera on this page, then send the report.")
        self.fields["captured_at"].error_messages["required"] = photo_time
        self.fields["captured_at"].error_messages["invalid"] = photo_time

    def clean_captured_at(self):
        captured_ms = self.cleaned_data["captured_at"]
        age = time.time() - captured_ms / 1000
        if age > MAX_PHOTO_AGE_SECONDS or age < -CLOCK_SKEW_SECONDS:
            raise forms.ValidationError(
                _("The photo is too old. Take a new photo and send the report right away.")
            )
        return captured_ms


def _location_fields():
    return {
        "latitude": forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.HiddenInput(), localize=False),
        "longitude": forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.HiddenInput(), localize=False),
        # Filled in by the camera page at the moment the photo is taken.
        "location_accuracy": forms.FloatField(widget=forms.HiddenInput(), min_value=0, localize=False),
        "captured_at": forms.IntegerField(widget=forms.HiddenInput(), localize=False),
    }


class ReportSubmitForm(CameraCaptureMixin, forms.ModelForm):
    latitude = _location_fields()["latitude"]
    longitude = _location_fields()["longitude"]
    location_accuracy = _location_fields()["location_accuracy"]
    captured_at = _location_fields()["captured_at"]
    # Set when the citizen says a nearby existing report is a different problem.
    confirm_new = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = RoadReport
        fields = ("street_name", "district", "original_image", "latitude", "longitude")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs["class"] = "input"
        self._setup_capture_messages("original_image")
        self.fields["original_image"].validators.append(validate_photo)
        self.fields["street_name"].widget.attrs["placeholder"] = _("Street or boulevard")
        self.fields["district"].widget.attrs["placeholder"] = _("District / municipality")


class ConfirmationForm(CameraCaptureMixin, forms.Form):
    """A citizen's photo added to an existing report instead of a duplicate one."""

    photo = forms.ImageField()
    latitude = _location_fields()["latitude"]
    longitude = _location_fields()["longitude"]
    location_accuracy = _location_fields()["location_accuracy"]
    captured_at = _location_fields()["captured_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_capture_messages("photo")
        self.fields["photo"].validators.append(validate_photo)
