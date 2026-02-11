from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from controle_acesso.permissions import IsSuperintendente


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperintendente])
def central_analise_status(request):
    """Status do módulo Central de Análise"""
    return Response({
        'status': 'ok',
        'module': 'central_analise',
        'message': 'Módulo Central de Análise ativo',
    })
