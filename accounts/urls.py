from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views
from .forms import ConsolePasswordResetForm

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('settings/', views.settings_view, name='settings'),
    path('password_reset/',
        PasswordResetView.as_view(
            form_class=ConsolePasswordResetForm,
            template_name='registration/password_reset_form.html',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset'),
    path('password_reset/done/',
        PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('reset/done/',
        PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
]
