from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('<int:id>/editar/', views.editar_producto, name='editar_producto'),
    path('<int:id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
]
