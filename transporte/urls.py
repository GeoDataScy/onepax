from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.transporte_status, name='transporte_status'),
    path('', views.TransporteListCreateView.as_view(), name='transporte_list_create'),
    path('<int:pk>/', views.TransporteDetailView.as_view(), name='transporte_detail'),
]
