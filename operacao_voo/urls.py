from django.urls import path
from . import views

urlpatterns = [
    # Rotas de controle Global
    path('start-emb-flight/', views.api_iniciar_embarque, name='start_emb'),
    path('stop-emb-flight/', views.api_parar_embarque, name='stop_emb'),
    path('salvar-embarque/', views.api_salvar_embarque, name='salvar_emb'),
    
    # ROTA DE CONTROLE INDIVIDUAL (Habilitar/Encerrar por Catraca)
    path('api/catraca-push/<str:device_id>/<str:action>/', views.api_toggle_catraca_push, name='toggle_catraca_push'),
    
    # ROTA DE CONTAGEM FILTRADA POR ID (EMBARQUE)
    path('api/total-embarcados/<str:device_id>/', views.api_total_embarcados_por_catraca, name='total_emb_por_catraca'),
         
    # Rotas de Desembarque
    path('start-desemb-flight/', views.api_iniciar_desembarque, name='start_desemb'),
    path('stop-desemb-flight/', views.api_parar_desembarque, name='stop_desemb'),
    path('salvar-desembarque/', views.api_salvar_desembarque, name='salvar_desemb'),
    path('api/total-desembarcados/', views.api_total_desembarcados, name='total_desemb'),
    path('api/total-desembarcados/<str:device_id>/', views.api_total_desembarcados_por_catraca, name='total_desemb_por_catraca'),
]