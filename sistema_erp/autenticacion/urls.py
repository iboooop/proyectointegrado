from django.urls import path
from .views import login_view, registro_view, recuperar_password_view, dashboard_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('recuperar/', recuperar_password_view, name='recuperar_password'),
    path('dashboard/', dashboard_view, name='dashboard'),
]