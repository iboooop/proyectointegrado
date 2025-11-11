from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes_list, name='clientes_list'),
    path('crear/', views.clientes_create, name='clientes_create'),
    path('<int:pk>/', views.clientes_detail, name='clientes_detail'),
    path('<int:pk>/editar/', views.clientes_edit, name='clientes_edit'),
    path('<int:pk>/eliminar/', views.clientes_delete, name='clientes_delete'),
    path('exportar/', views.exportar_clientes_excel, name='clientes_export'),
]
