from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Health check para EasyPanel
def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # Health Check (EasyPanel verifica esta rota)
    path('', health_check, name='health_check'),
    
    path('admin/', admin.site.urls),
    
    # Rotas de Autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('controle_acesso.auth_urls')),
    
    # Rotas da API (operacao_voo)
    path('', include('operacao_voo.urls')),
    
    # Rotas da Catraca. Tudo que a catraca enviar para o PATH BASE /receive/
    path('receive/', include('controle_acesso.urls')),
]