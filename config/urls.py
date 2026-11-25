from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import include, path
from django.utils.decorators import method_decorator

from employees import views as employee_views

# Exempt password reset views from LoginRequiredMiddleware
PasswordResetView = method_decorator(login_not_required, name="dispatch")(
    auth_views.PasswordResetView
)
PasswordResetDoneView = method_decorator(login_not_required, name="dispatch")(
    auth_views.PasswordResetDoneView
)
PasswordResetConfirmView = method_decorator(login_not_required, name="dispatch")(
    auth_views.PasswordResetConfirmView
)
PasswordResetCompleteView = method_decorator(login_not_required, name="dispatch")(
    auth_views.PasswordResetCompleteView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth Routes
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", employee_views.register, name="register"),
    # Password Reset Routes
    path(
        "password-reset/",
        PasswordResetView.as_view(template_name="password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # App Routes
    path("", include("employees.urls")),
]
