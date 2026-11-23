from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication. LoginView is exempt from LoginRequiredMiddleware by
    # design; LogoutView only accepts POST (CSRF-protected).
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='employees/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', include('employees.urls')),
]
