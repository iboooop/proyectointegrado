from django.urls import path
from .views import usuarios_list_view, usuarios_create_view, usuarios_edit_view, usuarios_delete_view, dashboard_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('list/', usuarios_list_view, name='usuarios_list'),
    path('create/', usuarios_create_view, name='usuarios_create'),
    path('edit/<int:id>/', usuarios_edit_view, name='usuarios_edit'),
    path('delete/<int:id>/', usuarios_delete_view, name='usuarios_delete'),
]