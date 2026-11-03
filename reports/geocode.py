"""Reverse geocoding: turn a map point into a street and district for the report form.

Uses OpenStreetMap's Nominatim service. Its usage policy asks for an identifying
User-Agent and at most one request per second, so lookups go through the server
(not the browser) and are cached; the form also waits until the user stops clicking.
"""
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.core.cache import cache

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "PATCH-road-inspector/1.0 (municipal road damage register)"
TIMEOUT_SECONDS = 6
CACHE_SECONDS = 60 * 60 * 24 * 7

STREET_KEYS = ("road", "pedestrian", "footway", "cycleway", "path", "residential", "square")
DISTRICT_KEYS = ("suburb", "city_district", "quarter", "neighbourhood", "borough")
SETTLEMENT_KEYS = ("city", "town", "village", "municipality")


class GeocodingError(Exception):
    pass


def _first(address, keys):
    return next((address[k] for k in keys if address.get(k)), "")


def reverse_geocode(lat, lng, language="bg"):
    # ~1 m precision is plenty for a street name and lets nearby clicks share the cache.
    lat, lng = round(float(lat), 5), round(float(lng), 5)
    key = f"geocode:{language}:{lat}:{lng}"
    cached = cache.get(key)
    if cached is not None:
        return cached

    query = urllib.parse.urlencode({
        "format": "jsonv2", "lat": lat, "lon": lng, "zoom": 18,
        "addressdetails": 1, "accept-language": language,
    })
    request = urllib.request.Request(f"{NOMINATIM_URL}?{query}", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.warning("Reverse geocoding %s,%s failed: %s", lat, lng, exc)
        raise GeocodingError from exc

    address = data.get("address") or {}
    street = _first(address, STREET_KEYS)
    if street and address.get("house_number"):
        street = f"{street} {address['house_number']}"
    result = {
        "street": street,
        "district": _first(address, DISTRICT_KEYS) or _first(address, SETTLEMENT_KEYS),
    }
    cache.set(key, result, CACHE_SECONDS)
    return result
