from django.urls import path

from vision import views

app_name = "vision"

urlpatterns = [
    path("jobs/", views.job_list, name="jobs"),
]
