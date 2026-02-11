from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.briefing_status, name='briefing_status'),
    path('', views.BriefingListCreateView.as_view(), name='briefing_list_create'),
    path('<int:pk>/', views.BriefingDetailView.as_view(), name='briefing_detail'),
]
