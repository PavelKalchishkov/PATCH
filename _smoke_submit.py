import io
from http.cookiejar import CookieJar
from urllib.request import HTTPCookieProcessor, Request, build_opener

from PIL import Image

opener = build_opener(HTTPCookieProcessor(CookieJar()))
BASE = "http://127.0.0.1:8000"


def get(path):
    resp = opener.open(BASE + path)
    return resp.status, resp.read().decode("utf-8", "ignore")


def csrf_from(html):
    key = 'name="csrfmiddlewaretoken" value="'
    i = html.index(key) + len(key)
    return html[i : html.index('"', i)]


def login(email, password):
    _, html = get("/accounts/login/")
    token = csrf_from(html)
    body = (
        f"csrfmiddlewaretoken={token}&username={email}&password={password}".encode()
    )
    req = Request(
        BASE + "/accounts/login/",
        data=body,
        headers={
            "Referer": BASE + "/accounts/login/",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    return opener.open(req).geturl()


print("login", login("citizen@patch.local", "citizen123"))
status, html = get("/reports/submit/")
print("submit form", status)
token = csrf_from(html)

img = Image.new("RGB", (640, 480), (40, 40, 40))
for x in range(200, 420):
    for y in range(160, 340):
        img.putpixel((x, y), (12, 12, 12))
buf = io.BytesIO()
img.save(buf, format="JPEG")
jpeg = buf.getvalue()

boundary = "----PatchBoundary"
parts = []


def add_field(name, value):
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
    )


add_field("csrfmiddlewaretoken", token)
add_field("street_name", "bul. Vitosha")
add_field("district", "Sofia")
add_field("latitude", "42.697700")
add_field("longitude", "23.321900")
add_field("device_make", "Pixel")
add_field("capture_angle", "30")
parts.append(
    (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"original_image\"; filename=\"hole.jpg\"\r\n"
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode()
    + jpeg
    + b"\r\n"
)
parts.append(f"--{boundary}--\r\n".encode())
data = b"".join(parts)
req = Request(
    BASE + "/reports/submit/",
    data=data,
    headers={
        "Referer": BASE + "/reports/submit/",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    },
)
resp = opener.open(req)
print("submitted", resp.status, resp.geturl())
html = resp.read().decode("utf-8", "ignore")
print("has detection", "POTHOLE" in html or "Дупка" in html or "detection" in html.lower())
print("has image", "annotated" in html or "/media/" in html)
