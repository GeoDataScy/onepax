from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas de Autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('controle_acesso.auth_urls')),
    
    # Rotas do Frontend
    path('', include('operacao_voo.urls')),
    
    # Rotas da Catraca. Tudo que a catraca enviar para o PATH BASE /receive/
    path('receive/', include('controle_acesso.urls')),
]