from django.urls import path
from . import views

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='clientes_list'),
    path('create/', views.ClienteCreateView.as_view(), name='clientes_create'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='clientes_detail'),
    path('<int:pk>/edit/', views.ClienteUpdateView.as_view(), name='clientes_edit'),
    path('<int:pk>/delete/', views.ClienteDeleteView.as_view(), name='clientes_delete'),
]