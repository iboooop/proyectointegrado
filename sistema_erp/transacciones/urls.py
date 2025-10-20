from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_transacciones, name='lista_transacciones'),
    path('<int:id>/', views.detalle_transaccion, name='detalle_transaccion'),
    path('<int:id>/editar/', views.editar_transaccion, name='editar_transaccion'),
    path('<int:id>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
]
