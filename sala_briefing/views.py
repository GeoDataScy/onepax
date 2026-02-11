from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from controle_acesso.permissions import IsSupervisor
from .models import BriefingSession


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisor])
def briefing_status(request):
    """Status do módulo Sala de Briefing"""
    return Response({
        'status': 'ok',
        'module': 'sala_briefing',
        'message': 'Módulo Sala de Briefing ativo',
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsSupervisor])
def briefing_list_create(request):
    """
    GET  — Lista todos os briefings
    POST — Cria um novo briefing
    """
    if request.method == 'GET':
        briefings = BriefingSession.objects.all()
        data = [{
            'id': b.id,
            'companhia_aerea': b.companhia_aerea,
            'cliente_final': b.cliente_final,
            'data': b.data.strftime('%d/%m/%Y'),
            'numero_voo': b.numero_voo,
            'unidade_maritima': b.unidade_maritima,
            'horario': b.horario.strftime('%H:%M'),
            'servico': b.servico,
            'solicitante': b.solicitante,
            'criado_em': b.criado_em.isoformat(),
        } for b in briefings]
        return Response(data)

    elif request.method == 'POST':
        try:
            from datetime import datetime

            d = request.data
            briefing = BriefingSession.objects.create(
                companhia_aerea=d.get('companhia_aerea', ''),
                cliente_final=d.get('cliente_final', ''),
                data=datetime.strptime(d['data'], '%d/%m/%Y').date() if '/' in str(d.get('data', '')) else d['data'],
                numero_voo=int(d['numero_voo']),
                unidade_maritima=d.get('unidade_maritima', ''),
                horario=d['horario'],
                servico=d.get('servico', ''),
                solicitante=d.get('solicitante', ''),
            )
            return Response({
                'id': briefing.id,
                'message': 'Briefing criado com sucesso',
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Erro ao criar briefing',
            }, status=status.HTTP_400_BAD_REQUEST)
