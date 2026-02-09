from django.urls import path
from . import auth_views

urlpatterns = [
    path('me/', auth_views.current_user, name='current_user'),
    path('logout/', auth_views.logout_view, name='logout'),
]
