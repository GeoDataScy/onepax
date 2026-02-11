from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.briefing_status, name='briefing_status'),
]
