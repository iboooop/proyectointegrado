from django.urls import path
from . import views

urlpatterns = [
    # --- LISTAR ---
    path('', views.bodegas_list, name='bodegas_list'),

    # --- CRUD (todas funciones, como en clientes) ---
    path('crear/', views.bodegas_create, name='bodegas_create'),
    path('<int:pk>/', views.bodegas_detail, name='bodegas_detail'),
    path('<int:pk>/editar/', views.bodegas_edit, name='bodegas_edit'),
    path('<int:pk>/eliminar/', views.bodegas_delete, name='bodegas_delete'),

    # --- EXPORTAR ---
    path('exportar/', views.exportar_bodegas_excel, name='bodegas_export'),
]
