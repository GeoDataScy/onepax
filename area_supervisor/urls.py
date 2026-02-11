from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.supervisor_status, name='supervisor_status'),
]
