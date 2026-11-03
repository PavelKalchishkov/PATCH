"""Reject photos that can't show road damage: black, white, blank, blurry or tiny.

The thresholds were set by measuring real report photos (brightness 110-140, contrast 38-53,
sharpness 32-44) against bad ones (black, covered lens, white, flat grey, heavily blurred).
templates/reports/submit.html runs the same checks in the browser right after the photo is
taken; keep the numbers there in step with these.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageFilter, ImageStat

MIN_SIDE_PX = 240
MIN_BRIGHTNESS = 30
MAX_BRIGHTNESS = 235
MIN_CONTRAST = 10
MIN_SHARPNESS = 6
ANALYSIS_SIZE = 256

MESSAGES = {
    "too_small": _("The photo is too small. Take it with the camera on this page."),
    "too_dark": _("The photo is too dark. Make sure nothing covers the camera and there is enough light, then take it again."),
    "too_bright": _("The photo is almost white. Don't point the camera at the sun or a bright light, then take it again."),
    "blank": _("The photo looks blank, with no detail. Point the camera at the road damage and take it again."),
    "blurry": _("The photo is too blurry. Hold the phone still for a moment and take it again."),
}


def measure(image: Image.Image) -> dict:
    gray = image.convert("L")
    gray.thumbnail((ANALYSIS_SIZE, ANALYSIS_SIZE))
    stat = ImageStat.Stat(gray)
    edges = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES))
    return {"brightness": stat.mean[0], "contrast": stat.stddev[0], "sharpness": edges.mean[0], "size": image.size}


def problem_with(image: Image.Image):
    """The first problem code for this photo, or None if it's usable."""
    m = measure(image)
    if min(m["size"]) < MIN_SIDE_PX:
        return "too_small"
    if m["brightness"] < MIN_BRIGHTNESS:
        return "too_dark"
    if m["brightness"] > MAX_BRIGHTNESS:
        return "too_bright"
    if m["contrast"] < MIN_CONTRAST:
        return "blank"
    if m["sharpness"] < MIN_SHARPNESS:
        return "blurry"
    return None


def validate_photo(uploaded_file):
    """Form-field validator: raises ValidationError with a friendly message for a bad photo."""
    if not uploaded_file:
        return uploaded_file
    position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else None
    try:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as image:
            image.load()
            problem = problem_with(image)
    except (OSError, ValueError):
        raise ValidationError(_("The photo couldn't be read. Please take it again."), code="invalid_image")
    finally:
        if position is not None:
            uploaded_file.seek(0)
    if problem:
        raise ValidationError(MESSAGES[problem], code=problem)
    return uploaded_file
