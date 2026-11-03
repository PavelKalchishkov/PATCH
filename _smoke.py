from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

opener = build_opener(HTTPCookieProcessor(CookieJar()))


def get(path):
    resp = opener.open("http://127.0.0.1:8000" + path)
    return resp.status, resp.read().decode("utf-8", "ignore")


def csrf_from(html):
    key = 'name="csrfmiddlewaretoken" value="'
    i = html.index(key) + len(key)
    return html[i : html.index('"', i)]


def login(email, password):
    status, html = get("/accounts/login/")
    token = csrf_from(html)
    data = urlencode(
        {"csrfmiddlewaretoken": token, "username": email, "password": password}
    ).encode()
    req = Request(
        "http://127.0.0.1:8000/accounts/login/",
        data=data,
        headers={"Referer": "http://127.0.0.1:8000/accounts/login/"},
    )
    resp = opener.open(req)
    return resp.geturl(), resp.status


print("login admin", login("admin@patch.local", "admin12345"))
for path in ["/accounts/users/", "/reports/moderation/", "/damages/catalog/", "/repairs/", "/repairs/new/", "/vision/jobs/", "/accounts/profile/"]:
    status, html = get(path)
    print(status, path, "error" if "Traceback" in html else "ok", len(html))
