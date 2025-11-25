from django.urls import path
from . import views
from .autocomplete import ProductoAutocomplete
from .views import get_producto_json

# app_name = 'productos' # <- ELIMINA O COMENTA ESTA LÍNEA

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('exportar/', views.exportar_productos_excel, name='productos_export'),
    path('producto-autocomplete/', ProductoAutocomplete.as_view(), name='producto-autocomplete'),
    path('<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('<int:id>/editar/', views.editar_producto, name='editar_producto'),
    path('<int:id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('agregar/', views.crear_producto, name='producto_agregar'),
    path('api/get-producto/<int:pk>/', get_producto_json, name='get_producto_json'),
]
