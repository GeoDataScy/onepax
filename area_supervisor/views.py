from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from controle_acesso.permissions import IsSupervisor


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisor])
def supervisor_status(request):
    """Status do módulo Área do Supervisor"""
    return Response({
        'status': 'ok',
        'module': 'area_supervisor',
        'message': 'Módulo Área do Supervisor ativo',
    })
