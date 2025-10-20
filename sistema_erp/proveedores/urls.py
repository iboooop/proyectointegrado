from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('<int:id>/', views.detalle_proveedor, name='detalle_proveedor'),
    path('<int:id>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('<int:id>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
]
