from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from controle_acesso.auth_views import CustomTokenObtainPairView
from controle_acesso.views import (
    push_handler, result_handler,
    desembarque_push_handler, desembarque_result_handler,
    receive_dao_handler, receber_evento_catraca,
)
from rest_framework_simplejwt.views import TokenRefreshView

# Health check para EasyPanel
def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # Health Check (EasyPanel verifica esta rota)
    path('', health_check, name='health_check'),
    
    path('admin/', admin.site.urls),
    
    # =====================================================
    # PROTOCOLO PUSH CONTROL iD - EMBARQUE
    # (mesmas rotas da AWS /push e /result)
    # =====================================================
    path('push/', push_handler, name='push_handler'),
    path('push', push_handler, name='push_handler_nb'),
    path('result/', result_handler, name='result_handler'),
    path('result', result_handler, name='result_handler_nb'),
    
    # =====================================================
    # PROTOCOLO PUSH CONTROL iD - DESEMBARQUE
    # (mesmas rotas da AWS /desembarque/push e /desembarque/result)
    # =====================================================
    path('desembarque/push/', desembarque_push_handler, name='desemb_push'),
    path('desembarque/push', desembarque_push_handler, name='desemb_push_nb'),
    path('desembarque/result/', desembarque_result_handler, name='desemb_result'),
    path('desembarque/result', desembarque_result_handler, name='desemb_result_nb'),
    
    # =====================================================
    # DAO (eventos genéricos da catraca)
    # =====================================================
    path('receive/dao/', receive_dao_handler, name='receive_dao'),
    path('receive/dao', receive_dao_handler, name='receive_dao_nb'),
    
    # DAO de desembarque (AWS tinha em /desembarque/dao/)
    path('desembarque/dao/', receive_dao_handler, name='desemb_dao'),
    path('desembarque/dao', receive_dao_handler, name='desemb_dao_nb'),
    
    # Evento de giro de desembarque (AWS tinha em /desembarque/catra_event/)
    path('desembarque/catra_event/', receber_evento_catraca, name='desemb_catra_event'),
    path('desembarque/catra_event', receber_evento_catraca, name='desemb_catra_event_nb'),
    
    # Rotas de Autenticação JWT (com role no token)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('controle_acesso.auth_urls')),
    
    # Rotas da API (operacao_voo)
    path('', include('operacao_voo.urls')),
    
    # Rotas da Catraca (evento de giro + heartbeat)
    path('receive/', include('controle_acesso.urls')),
    
    # Rotas dos novos módulos
    path('api/briefing/', include('sala_briefing.urls')),
    path('api/transporte/', include('transporte.urls')),
    path('api/supervisor/', include('area_supervisor.urls')),
    path('api/central-analise/', include('central_analise.urls')),
]