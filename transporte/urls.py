from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.transporte_status, name='transporte_status'),
    path('', views.transporte_list_create, name='transporte_list_create'),
]
