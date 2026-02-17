from django.urls import path
from . import views

urlpatterns = [
    # Evento de Giro (URL final: /receive/catra_event/)
    path('catra_event/', views.receber_evento_catraca, name='catra_event'),
    path('catra_event', views.receber_evento_catraca, name='catra_event_nb'),
    
    # Heartbeat
    path('api/notifications/device_is_alive/', views.receber_heartbeat, name='device_is_alive'),
]