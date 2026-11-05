from django.urls import path

from reports import views

app_name = "reports"

urlpatterns = [
    path("submit/", views.submit_report, name="submit"),
    path("mine/", views.my_reports, name="mine"),
    path("geocode/", views.geocode, name="geocode"),
    path("nearby/", views.nearby_reports, name="nearby"),
    path("<uuid:report_id>/confirm/", views.confirm_report, name="confirm"),
    path("<uuid:report_id>/vote/<str:kind>/", views.vote, name="vote"),
    path("moderation/", views.moderation_queue, name="moderation"),
    path("<uuid:report_id>/", views.report_detail, name="detail"),
    path("<uuid:report_id>/delete/", views.delete_report, name="delete"),
    path("<uuid:report_id>/admin-delete/", views.admin_delete_report, name="admin_delete"),
    path("<uuid:report_id>/moderate/", views.moderate_report, name="moderate"),
    path("<uuid:report_id>/before-after/", views.before_after, name="before_after"),
    path("<uuid:report_id>/reviewed/", views.moderation_result, name="moderation_result"),
]
