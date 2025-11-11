"""
URL configuration for sistema_erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('autenticacion/', include('autenticacion.urls')),  # URLs de autenticación
    path('usuarios/', include('usuarios.urls')),  # URLs de usuarios
    path('', views.dashboard, name='dashboard'),
    path('forzar-404/', views.force_404, name='force_404'),
    path('ver-404/', views.preview_404, name='preview_404'),
    path('productos/', include('productos.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('transacciones/', include('transacciones.urls')),
    path('bodegas/', include('bodegas.urls')),         # <-- Agregado bodegas
    path('clientes/', include('clientes.urls')),
    # Catch-all: al final, cualquier otra URL muestra el 404 personalizado incluso en DEBUG
    re_path(r'^(?P<extra>.*)$', views.not_found_view, name='not_found'),
]

# Handler para errores HTTP personalizados
handler404 = 'sistema_erp.views.custom_404_view'
