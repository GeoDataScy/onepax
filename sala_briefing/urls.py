from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.briefing_status, name='briefing_status'),
    path('', views.briefing_list_create, name='briefing_list_create'),
]
