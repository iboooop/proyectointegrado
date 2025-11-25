from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import login_view, registro_view, logout_view
from .forms import CustomSetPasswordForm

urlpatterns = [
    # LOGIN / LOGOUT / REGISTRO
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registro'),

    # 🔹 1) Usuario ingresa correo
    path('password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='autenticacion/password_reset.html',
            email_template_name='autenticacion/password_reset_email.txt',    # texto plano (fallback)
            html_email_template_name='autenticacion/password_reset_email.html', # HTML (la plantilla bonita)
            subject_template_name='autenticacion/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset'),

    # 🔹 2) Confirmación de que email fue enviado
    path('password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='autenticacion/password_reset_done.html'
        ),
        name='password_reset_done'),

    # 🔹 3) El usuario abre enlace recibido por correo
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='autenticacion/password_reset_confirm.html',
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm'),

    # 🔹 4) Contraseña cambiada con éxito
    path('password_reset_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='autenticacion/password_reset_complete.html'
        ),
        name='password_reset_complete'),
]
