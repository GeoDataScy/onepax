from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """View de login customizada que retorna role no token"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Retorna os dados do usuário autenticado atual (incluindo role)
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_role(request):
    """
    Retorna o role do usuário autenticado
    """
    try:
        role = request.user.profile.role
    except Exception:
        role = 'apac'

    return Response({
        'username': request.user.username,
        'role': role,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Endpoint de logout (apenas confirma, o token é removido no frontend)
    """
    return Response({
        'message': 'Logout realizado com sucesso',
        'status': 'success'
    }, status=status.HTTP_200_OK)
