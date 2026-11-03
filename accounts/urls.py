from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.PatchLoginView.as_view(), name="login"),
    path("logout/", views.PatchLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("verify/<str:token>/", views.verify_email, name="verify_email"),
    path("verify-resend/", views.resend_verification, name="resend_verification"),
    path("users/", views.user_directory, name="users"),
    path("users/<uuid:user_id>/role/", views.change_role, name="change_role"),
    path("users/<uuid:user_id>/request/<str:decision>/", views.review_role_request, name="review_request"),
    path("users/<uuid:user_id>/toggle-block/", views.toggle_block, name="toggle_block"),
    path("users/<uuid:user_id>/reset-strikes/", views.reset_strikes, name="reset_strikes"),
]
