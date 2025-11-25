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
from django.conf import settings  # <-- AÑADIR
from django.conf.urls.static import static  # <-- AÑADIR
from rest_framework import routers
from productos.api_views import ProductoViewSet

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)



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

    path("api/", include(router.urls)),
    # Catch-all: al final, cualquier otra URL muestra el 404 personalizado incluso en DEBUG
    re_path(r'^(?P<extra>.*)$', views.not_found_view, name='not_found'),
    
]

# Handler para errores HTTP personalizados
handler404 = 'sistema_erp.views.custom_404_view'

# CORRIGE EL BLOQUE ANTERIOR CON ESTE
if settings.DEBUG:
    # Añadimos las URLs para servir archivos estáticos y de medios en modo de desarrollo
    # Se añaden al principio para que no sean capturadas por el re_path catch-all
    urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + urlpatterns
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
