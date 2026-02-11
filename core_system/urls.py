from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from controle_acesso.auth_views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

# Health check para EasyPanel
def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # Health Check (EasyPanel verifica esta rota)
    path('', health_check, name='health_check'),
    
    path('admin/', admin.site.urls),
    
    # Rotas de Autenticação JWT (com role no token)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('controle_acesso.auth_urls')),
    
    # Rotas da API (operacao_voo)
    path('', include('operacao_voo.urls')),
    
    # Rotas da Catraca
    path('receive/', include('controle_acesso.urls')),
    
    # Rotas dos novos módulos
    path('api/briefing/', include('sala_briefing.urls')),
    path('api/transporte/', include('transporte.urls')),
    path('api/supervisor/', include('area_supervisor.urls')),
    path('api/central-analise/', include('central_analise.urls')),
]