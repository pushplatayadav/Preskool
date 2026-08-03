from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),
    path(
        "password-reset-done/",
        views.password_reset_done_view,
        name="password-reset-done",
    ),
    path(
        "reset-password/<str:uidb64>/<str:token>/",
        views.reset_password_view,
        name="reset-password",
    ),
    path("verify-otp/", views.verify_otp_view, name="verify-otp"),
    path("resend-otp/", views.resend_otp_view, name="resend-otp"),
    path("forgot-password/verify-otp/", views.forgot_password_verify_otp_view, name="forgot-password-verify-otp"),
    path("forgot-password/resend-otp/", views.forgot_password_resend_otp_view, name="forgot-password-resend-otp"),
    path("reset-password/", views.reset_password_view, name="reset-password-direct"),
]
