from django.urls import path
from . import auth_views

urlpatterns = [
    path('me/', auth_views.current_user, name='current_user'),
    path('check-role/', auth_views.check_role, name='check_role'),
    path('logout/', auth_views.logout_view, name='logout'),
]
