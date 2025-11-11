from django.urls import path
from . import views

app_name = 'bodegas'   # <-- añadir namespace

urlpatterns = [
    path('', views.BodegaListView.as_view(), name='bodegas_list'),
    path('create/', views.BodegaCreateView.as_view(), name='bodegas_create'),
    path('<int:pk>/', views.BodegaDetailView.as_view(), name='bodegas_detail'),
    path('<int:pk>/edit/', views.BodegaUpdateView.as_view(), name='bodegas_edit'),
    path('<int:pk>/delete/', views.BodegaDeleteView.as_view(), name='bodegas_delete'),
]