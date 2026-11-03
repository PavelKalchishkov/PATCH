from django.urls import path

from repairs import views

app_name = "repairs"

urlpatterns = [
    path("", views.task_list, name="list"),
    path("new/", views.create_task, name="create"),
    path("available/", views.available_work, name="available"),
    path("reserve/<uuid:report_id>/", views.reserve, name="reserve"),
    path("<uuid:task_id>/", views.task_detail, name="detail"),
    path("<uuid:task_id>/act/<str:action>/", views.transition_own_task, name="act"),
    path("<uuid:task_id>/approve/", views.approve_task, name="approve"),
    path("<uuid:task_id>/reviewed/", views.approval_result, name="approval_result"),
    path("<uuid:task_id>/photos/", views.upload_photo, name="upload_photo"),
]
