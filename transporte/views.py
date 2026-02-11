from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from controle_acesso.permissions import IsSupervisor
from .models import RegistroTransporte


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisor])
def transporte_status(request):
    """Status do módulo Transporte"""
    return Response({
        'status': 'ok',
        'module': 'transporte',
        'message': 'Módulo Transporte ativo',
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsSupervisor])
def transporte_list_create(request):
    """
    GET  — Lista todos os registros de transporte
    POST — Cria um novo registro de transporte
    """
    if request.method == 'GET':
        registros = RegistroTransporte.objects.all()
        data = [{
            'id': r.id,
            'empresa_solicitante': r.empresa_solicitante,
            'cliente_final': r.cliente_final,
            'data': r.data.strftime('%d/%m/%Y') if r.data else '',
            'numero_voo': r.numero_voo,
            'prefixo_aeronave': r.prefixo_aeronave,
            'prefixo_manual': r.prefixo_manual,
            'horario': r.horario.strftime('%H:%M') if r.horario else '',
            'servico': r.servico,
            'criado_em': r.criado_em.isoformat(),
        } for r in registros]
        return Response(data)

    elif request.method == 'POST':
        try:
            from datetime import datetime

            d = request.data
            registro = RegistroTransporte.objects.create(
                empresa_solicitante=d.get('empresa_solicitante', ''),
                cliente_final=d.get('cliente_final', ''),
                data=datetime.strptime(d['data'], '%d/%m/%Y').date() if '/' in str(d.get('data', '')) else d.get('data'),
                numero_voo=int(d.get('numero_voo', 0)),
                prefixo_aeronave=d.get('prefixo_aeronave', ''),
                prefixo_manual=d.get('prefixo_manual', ''),
                horario=d.get('horario'),
                servico=d.get('servico', ''),
            )
            return Response({
                'id': registro.id,
                'message': 'Registro de transporte criado com sucesso',
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Erro ao criar registro de transporte',
            }, status=status.HTTP_400_BAD_REQUEST)
