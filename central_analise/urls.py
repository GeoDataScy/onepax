from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.central_analise_status, name='central_analise_status'),
]
