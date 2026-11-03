from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from PATCH import errors, views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("reports/", include("reports.urls")),
    path("damages/", include("damages.urls")),
    path("repairs/", include("repairs.urls")),
    path("vision/", include("vision.urls")),
]

# Uploaded photos. Django serves them itself, also with DEBUG off: fine for a small test
# site; a busy one would move them to object storage (S3, R2) behind a CDN.
urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

if settings.DEBUG:
    urlpatterns += [path("errors/<int:code>/", errors.preview, name="error_preview")]

handler400 = "PATCH.errors.bad_request"
handler403 = "PATCH.errors.permission_denied"
handler404 = "PATCH.errors.page_not_found"
handler500 = "PATCH.errors.server_error"

admin.site.site_header = "PATCH administration"
admin.site.site_title = "PATCH"
admin.site.index_title = "Road Inspector & Registry"
