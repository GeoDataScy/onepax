from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from controle_acesso.permissions import IsSupervisor


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisor])
def briefing_status(request):
    """Status do módulo Sala de Briefing"""
    return Response({
        'status': 'ok',
        'module': 'sala_briefing',
        'message': 'Módulo Sala de Briefing ativo',
    })
