from django.urls import path
from .views import (
    login_view, registro_view, recuperar_password_view, restablecer_password_view,
    cambiar_password_view
)

urlpatterns = [
    path('login/', login_view, name='login'),  # URL para iniciar sesión
    path('registro/', registro_view, name='registro'),  # URL para registrar un nuevo usuario
    path('recuperar/', recuperar_password_view, name='recuperar_password'),  # URL para recuperar contraseña
    path('restablecer/<uidb64>/<token>/', restablecer_password_view, name='restablecer_password'),  # URL para restablecer contraseña con token
    path('cambiar/', cambiar_password_view, name='cambiar_password'),  # URL para cambiar contraseña

]