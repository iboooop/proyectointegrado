from django.urls import path
from .views import (
    dashboard_view, usuarios_list_view, usuarios_create_view,
    usuarios_detail_view, usuarios_edit_view, usuarios_delete_view, 
    export_usuarios_excel, usuarios_reset_password_view
)

urlpatterns = [
    path('', usuarios_list_view, name='usuarios_list'),  
    path('dashboard/', dashboard_view, name='dashboard'),
    path('list/', usuarios_list_view, name='usuarios_list'),
    path('create/', usuarios_create_view, name='usuarios_create'),
    path('<int:id>/', usuarios_detail_view, name='usuarios_detail'),
    path('edit/<int:id>/', usuarios_edit_view, name='usuarios_edit'),
    path('delete/<int:id>/', usuarios_delete_view, name='usuarios_delete'),
    path('reset-password/<int:id>/', usuarios_reset_password_view, name='usuarios_reset_password'),
    path('exportar/', export_usuarios_excel, name='usuarios_export'),
]