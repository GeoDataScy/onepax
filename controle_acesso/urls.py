from django.urls import path
from . import views

urlpatterns = [
    # Rota de Giro OBRIGATÓRIA (URL final: /receive/catra_event/)
    # MUDANÇA AQUI! Adicione a barra final:
    path('catra_event/', views.receber_evento_catraca, name='catra_event'),
    
    # Rota de Heartbeat (Também adicionando a barra por consistência)
    # MUDANÇA AQUI! Adicione a barra final:
    path('api/notifications/device_is_alive/', views.receber_heartbeat, name='device_is_alive'),
]