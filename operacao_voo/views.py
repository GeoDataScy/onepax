from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Embarque, Desembarque
from controle_acesso.models import Catraca, EventoCatraca
import json
import logging

logger = logging.getLogger(__name__)

# ESTADOS GLOBAIS
VOO_EMBARQUE_ATIVO = {"ativo": False, "inicio": None, "id_voo": None}
VOO_DESEMBARQUE_ATIVO = {"ativo": False, "inicio": None, "id_voo": None}

def embarque_view(request):
    return render(request, 'operacao_voo/embarque.html')

# --- CONTROLE GLOBAL ---

@csrf_exempt
@require_POST
def api_iniciar_embarque(request):
    """ Inicia o cronômetro do voo globalmente """
    VOO_EMBARQUE_ATIVO["ativo"] = True
    if not VOO_EMBARQUE_ATIVO["inicio"]:
        VOO_EMBARQUE_ATIVO["inicio"] = timezone.now()
    
    logger.info("Estado de Voo de Embarque definido como ATIVO.")
    return JsonResponse({"status": "success", "message": "Voo de Embarque Ativado no Sistema."})

@csrf_exempt
@require_POST
def api_parar_embarque(request):
    """ Para o estado global do voo. Cada catraca é desativada individualmente pelo frontend. """
    VOO_EMBARQUE_ATIVO["ativo"] = False
    VOO_EMBARQUE_ATIVO["inicio"] = None

    logger.info("Estado global de embarque encerrado.")
    return JsonResponse({"status": "success", "message": "Embarque Encerrado globalmente."})

# --- CONTROLE INDIVIDUAL ---

@csrf_exempt
@require_POST
def api_toggle_catraca_push(request, device_id, action):
    """
    Controle individual de cada catraca.
    
    enable → Liga o push E reseta o contador (botão "Liberar Passageiro")
    reset  → SÓ reseta o contador, NÃO liga o push (botão "Habilitar Catraca")
    disable → Desliga o push (botão "Encerrar Voo")
    """
    catraca = get_object_or_404(Catraca, identificador=device_id)

    if action == "enable":
        # Liga o push E reseta last_command_time para forçar verde imediato
        catraca.inicio_contagem = timezone.now()
        catraca.push_ativo = True
        catraca.last_command_time = None  # força a catraca ficar verde no próximo poll
        catraca.save()

        # Garante que o estado global do embarque está ativo
        VOO_EMBARQUE_ATIVO["ativo"] = True
        if not VOO_EMBARQUE_ATIVO["inicio"]:
            VOO_EMBARQUE_ATIVO["inicio"] = timezone.now()

        msg = f"Catraca {device_id} liberada - ficará verde em até 5 segundos."

    elif action == "reset":
        # SÓ zera o contador — NÃO liga o push, catraca NÃO fica verde
        catraca.inicio_contagem = timezone.now()
        catraca.save()

        msg = f"Catraca {device_id} habilitada - contador zerado para novo voo."

    else:  # disable
        catraca.push_ativo = False
        catraca.save()

        msg = f"Catraca {device_id} desativada."

    logger.info(msg)
    return JsonResponse({"status": "success", "message": msg})

def api_total_embarcados_por_catraca(request, device_id):
    """
    CONTAGEM SEGREGADA:
    Só conta giros após o 'inicio_contagem' individual de cada catraca.
    """
    catraca = get_object_or_404(Catraca, identificador=device_id)

    total = EventoCatraca.objects.filter(
        catraca=catraca,
        timestamp__gte=catraca.inicio_contagem
    ).count()

    return JsonResponse({'total_embarcados': total})

@csrf_exempt
@require_POST
def api_salvar_embarque(request):
    try:
        data = json.loads(request.body)
        flight_number = data.get('numeroVoo') or data.get('flight_number')
        if not flight_number:
            return JsonResponse({"status": "error", "message": "Número do Voo obrigatório"}, status=400)

        departure_date = (data.get('dataEmbarque') or '')[:10]
        departure_time = data.get('horaEmbarque')
        catraca_id = data.get('catraca_id', '1001')
        passageiros = data.get('passengers_boarded', 0)

        voo_existente = Embarque.objects.filter(
            flight_number=flight_number,
            departure_date=departure_date
        ).first()

        if voo_existente:
            if catraca_id == '1001':
                voo_existente.passageiros_catraca1 = passageiros
                voo_existente.catraca1_salvo = True
            elif catraca_id == '1002':
                voo_existente.passageiros_catraca2 = passageiros
                voo_existente.catraca2_salvo = True

            voo_existente.passengers_boarded = voo_existente.passageiros_catraca1 + voo_existente.passageiros_catraca2

            if departure_time:
                voo_existente.departure_time = departure_time

            voo_existente.save()

            return JsonResponse({
                "status": "success",
                "total_passageiros": voo_existente.passengers_boarded,
                "consolidado": voo_existente.catraca1_salvo and voo_existente.catraca2_salvo
            })
        else:
            novo_voo = Embarque.objects.create(
                flight_number=flight_number,
                aeronave=data.get('aeronave'),
                operadora=data.get('operadorAereo'),
                departure_date=departure_date,
                departure_time=departure_time,
                platform=data.get('plataforma'),
                icao=data.get('icao'),
                cliente_final=data.get('clienteFinal'),
                passageiros_catraca1=passageiros if catraca_id == '1001' else 0,
                passageiros_catraca2=passageiros if catraca_id == '1002' else 0,
                passengers_boarded=passageiros,
                observacao=data.get('observacoes', ''),
                catraca1_salvo=(catraca_id == '1001'),
                catraca2_salvo=(catraca_id == '1002')
            )
            return JsonResponse({
                "status": "success",
                "total_passageiros": novo_voo.passengers_boarded,
                "consolidado": False
            })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# --- DESEMBARQUE ---

@csrf_exempt
@require_POST
def api_iniciar_desembarque(request):
    VOO_DESEMBARQUE_ATIVO["inicio"] = timezone.now()
    return JsonResponse({"status": "success", "message": "Desembarque Iniciado."})

@csrf_exempt
@require_POST
def api_parar_desembarque(request):
    VOO_DESEMBARQUE_ATIVO["ativo"] = False
    VOO_DESEMBARQUE_ATIVO.update({"inicio": None})
    return JsonResponse({"status": "success", "message": "Desembarque Encerrado."})

def api_total_desembarcados(request):
    """
    Total global de desembarque somando todas as catracas de desembarque
    a partir do inicio_contagem individual de cada uma (persistido em DB).
    """
    total = 0
    for catraca in Catraca.objects.filter(tipo='DESEMBARQUE'):
        total += EventoCatraca.objects.filter(
            catraca=catraca,
            timestamp__gte=catraca.inicio_contagem
        ).count()
    return JsonResponse({"total_desembarcados": total})

def api_total_desembarcados_por_catraca(request, device_id):
    """
    CONTAGEM SEGREGADA POR CATRACA DE DESEMBARQUE:
    Só conta giros após o 'inicio_contagem' individual de cada catraca.
    """
    catraca = get_object_or_404(Catraca, identificador=device_id)

    total = EventoCatraca.objects.filter(
        catraca=catraca,
        timestamp__gte=catraca.inicio_contagem
    ).count()

    return JsonResponse({'total_desembarcados': total})

@csrf_exempt
@require_POST
def api_salvar_desembarque(request):
    try:
        data = json.loads(request.body)
        flight_number = data.get('numeroVoo') or data.get('flight_number')
        if not flight_number:
            return JsonResponse({'status': 'error', 'message': 'Número do Voo obrigatório'}, status=400)

        novo_voo = Desembarque.objects.create(
            flight_number=flight_number,
            aeronave=data.get('aeronave'),
            operadora=data.get('operadorAereo') or data.get('operadora'),
            arrival_date=(data.get('dataEmbarque') or '')[:10],
            arrival_time=data.get('horaEmbarque'),
            origin=data.get('plataforma'),
            cliente_final=data.get('clienteFinal'),
            passengers_disembarked=data.get('passengers_boarded', 0),
            observacao=data.get('observacoes', '')
        )
        return JsonResponse({'status': 'success', 'message': f'Voo {flight_number} de desembarque salvo com sucesso!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =========================================================
# VIEWS GENÉRICAS PARA CRUD (Supervisor)
# =========================================================
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import EmbarqueSerializer, DesembarqueSerializer
from controle_acesso.permissions import IsSupervisor

class EmbarqueListCreateView(generics.ListCreateAPIView):
    queryset = Embarque.objects.all().order_by('-departure_date', '-departure_time')
    serializer_class = EmbarqueSerializer
    permission_classes = [IsAuthenticated]

class EmbarqueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Embarque.objects.all()
    serializer_class = EmbarqueSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

class DesembarqueListCreateView(generics.ListCreateAPIView):
    queryset = Desembarque.objects.all().order_by('-arrival_date', '-arrival_time')
    serializer_class = DesembarqueSerializer
    permission_classes = [IsAuthenticated]

class DesembarqueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Desembarque.objects.all()
    serializer_class = DesembarqueSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]
