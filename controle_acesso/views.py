from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from uuid import UUID, uuid4
import json
import logging
from .models import Catraca, EventoCatraca

logger = logging.getLogger(__name__)


# =========================================================
# 1. EVENTO DE GIRO (/receive/catra_event/)
#    A catraca envia quando alguém passa (TURN LEFT / TURN RIGHT)
# =========================================================

@csrf_exempt
def receber_evento_catraca(request):
    """
    Recebe o evento de giro da Control iD.
    Baseado no receive_event do Gerenciador (AWS).
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Evento recebido: {data}")

            # --- DEBUG NO TERMINAL ---
            print("\n--- EVENTO GIRO RECEBIDO ---")
            print(json.dumps(data, indent=4))
            print("----------------------------\n")

            # Filtrar: só TURN LEFT e TURN RIGHT
            event_data = data.get('event', {})
            event_name = event_data.get('name')
            if event_name not in ['TURN LEFT', 'TURN RIGHT']:
                return JsonResponse(
                    {"status": "ignored", "message": f"Evento {event_name} ignorado."},
                    status=200
                )

            # UUID do evento
            try:
                uuid = UUID(event_data.get('uuid', ''), version=4)
            except (ValueError, KeyError, TypeError):
                uuid = uuid4()

            # device_id está na RAIZ do JSON (não dentro de 'event')
            device_id_recebido = data.get('device_id')

            # Procurar a catraca pelo identificador
            catraca = Catraca.objects.filter(identificador=str(device_id_recebido)).first()

            if not catraca:
                logger.warning(f"Catraca não cadastrada: {device_id_recebido}")
                return JsonResponse({"status": "error", "message": "Dispositivo desconhecido"}, status=200)

            # =============================================
            # ANTI-REBOTE: Ignorar giros duplicados
            # (AWS: embarque=0s, desembarque=5s)
            # Usamos 5 segundos como padrão para evitar duplicatas no modo livre
            # =============================================
            event_time = timezone.now()
            DEBOUNCE_SECONDS = 5
            
            if catraca.last_event_time and (event_time - catraca.last_event_time) <= timedelta(seconds=DEBOUNCE_SECONDS):
                logger.info(f"[ANTI-REBOTE] Evento ignorado para {catraca.nome} (intervalo < {DEBOUNCE_SECONDS}s)")
                return JsonResponse(
                    {"status": "ignored", "message": "Evento ignorado devido ao intervalo de tempo."},
                    status=200
                )

            # Atualizar o timestamp do último evento
            catraca.last_event_time = event_time
            catraca.save()

            # Salvar o evento
            EventoCatraca.objects.create(
                catraca=catraca,
                timestamp=event_time,
                sentido=event_name,
                raw_data=json.dumps(data)
            )

            logger.info(f"Giro '{event_name}' registrado na {catraca.nome}")

            return JsonResponse(
                {"status": "success", "message": "Evento registrado com sucesso"},
                status=200
            )

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
        except Exception as e:
            logger.error(f"Erro ao processar o evento: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


# =========================================================
# 2. PUSH HANDLER - EMBARQUE
#    GET /push  →  Catraca faz polling para verificar se há comandos
#    Baseado no push_handler do Gerenciador (AWS)
# =========================================================

@csrf_exempt
def push_handler(request):
    """
    GET /push?deviceId=XXX
    Se a catraca tem push_ativo=True, retorna comando de liberação (anticlockwise).
    Se não, retorna no_action.
    Janela anti-spam de 5 segundos.
    """
    if request.method == "GET":
        device_id = request.GET.get('deviceId', None)
        
        if not device_id:
            return JsonResponse({"status": "no_action"}, status=200)

        # Procurar a catraca pelo identificador
        catraca = Catraca.objects.filter(identificador=str(device_id)).first()
        
        if not catraca or not catraca.push_ativo:
            logger.info(f"[EMBARQUE] Push desativado para device {device_id}")
            return JsonResponse({"status": "no_action"}, status=200)

        # Janela anti-spam: mínimo 5 segundos entre comandos
        if catraca.last_command_time and (now() - catraca.last_command_time) < timedelta(seconds=5):
            logger.info(f"[EMBARQUE] Comando recente para {device_id}. Ignorando.")
            return JsonResponse({"status": "no_action"}, status=200)

        # Comando de liberação: EMBARQUE = anticlockwise (igual à AWS)
        response_data = {
            "verb": "POST",
            "endpoint": "execute_actions",
            "body": {
                "actions": [
                    {"action": "catra", "parameters": "allow=anticlockwise"}
                ]
            },
            "contentType": "application/json",
        }

        # Atualizar timestamp do último comando
        catraca.last_command_time = now()
        catraca.save()

        logger.info(f"[EMBARQUE] Comando de liberação enviado para {device_id}")
        return JsonResponse(response_data, status=200)

    return JsonResponse({"error": "Método não permitido"}, status=405)


# =========================================================
# 3. RESULT HANDLER - EMBARQUE
#    POST /result  →  Catraca envia resultado do comando executado
#    Baseado no result_handler do Gerenciador (AWS)
# =========================================================

@csrf_exempt
def result_handler(request):
    """
    POST /result?deviceId=XXX
    Recebe o resultado/feedback do comando executado pela catraca.
    """
    if request.method == "POST":
        device_id = request.GET.get('deviceId', 'desconhecido')
        
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
            logger.info(f"[EMBARQUE] Resultado recebido do device {device_id}: {data}")

            # Atualizar last_command_time da catraca
            catraca = Catraca.objects.filter(identificador=str(device_id)).first()
            if catraca:
                catraca.last_command_time = now()
                catraca.save()
                logger.info(f"[EMBARQUE] Comando concluído para {catraca.nome}")

            return JsonResponse(
                {"status": "success", "message": "Resultado processado com sucesso."},
                status=200
            )

        except Exception as e:
            logger.error(f"[EMBARQUE] Erro ao processar resultado: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


# =========================================================
# 4. PUSH HANDLER - DESEMBARQUE
#    GET /desembarque/push  →  Polling da catraca de desembarque
#    Baseado no push_handler_desembarque do app desembarque (AWS)
# =========================================================

@csrf_exempt
def desembarque_push_handler(request):
    """
    GET /desembarque/push?deviceId=XXX
    Se a catraca tem push_ativo=True, retorna comando de liberação (clockwise).
    DESEMBARQUE usa clockwise (diferente do embarque que usa anticlockwise).
    """
    if request.method == "GET":
        device_id = request.GET.get('deviceId', None)
        
        if not device_id:
            return JsonResponse({"status": "no_action"}, status=200)

        catraca = Catraca.objects.filter(identificador=str(device_id)).first()
        
        if not catraca or not catraca.push_ativo:
            logger.info(f"[DESEMBARQUE] Push desativado para device {device_id}")
            return JsonResponse({"status": "no_action"}, status=200)

        # Janela anti-spam: mínimo 5 segundos entre comandos
        if catraca.last_command_time and (now() - catraca.last_command_time) < timedelta(seconds=5):
            logger.info(f"[DESEMBARQUE] Comando recente para {device_id}. Ignorando.")
            return JsonResponse({"status": "no_action"}, status=200)

        # Comando de liberação: DESEMBARQUE = clockwise (igual à AWS)
        response_data = {
            "verb": "POST",
            "endpoint": "execute_actions",
            "body": {
                "actions": [
                    {"action": "catra", "parameters": "allow=clockwise"}
                ]
            },
            "contentType": "application/json",
        }

        # Atualizar timestamp do último comando
        catraca.last_command_time = now()
        catraca.save()

        logger.info(f"[DESEMBARQUE] Comando de liberação enviado para {device_id}")
        return JsonResponse(response_data, status=200)

    return JsonResponse({"error": "Método não permitido"}, status=405)


# =========================================================
# 5. RESULT HANDLER - DESEMBARQUE
#    POST /desembarque/result  →  Resultado do comando de desembarque
#    Baseado no result_handler_desembarque do app desembarque (AWS)
# =========================================================

@csrf_exempt
def desembarque_result_handler(request):
    """
    POST /desembarque/result?deviceId=XXX
    Recebe o resultado/feedback do comando executado pela catraca de desembarque.
    """
    if request.method == "POST":
        device_id = request.GET.get('deviceId', 'desconhecido')
        
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
            endpoint = data.get('endpoint', 'execute_actions')
            logger.info(f"[DESEMBARQUE] Resultado recebido do device {device_id}: {data}")

            # Atualizar last_command_time da catraca
            catraca = Catraca.objects.filter(identificador=str(device_id)).first()
            if catraca:
                catraca.last_command_time = now()
                catraca.save()
                logger.info(f"[DESEMBARQUE] Comando concluído para {catraca.nome}")

            return JsonResponse(
                {"status": "success", "message": "Resultado processado com sucesso.", "endpoint": endpoint},
                status=200
            )

        except json.JSONDecodeError as e:
            logger.error(f"[DESEMBARQUE] JSON inválido: {e}")
            return JsonResponse({"status": "error", "message": "JSON inválido."}, status=400)
        except Exception as e:
            logger.error(f"[DESEMBARQUE] Erro ao processar resultado: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


# =========================================================
# 6. DAO HANDLER (recebe eventos genéricos)
# =========================================================

@csrf_exempt
def receive_dao_handler(request):
    """
    Endpoint para processar eventos gerais da catraca (DAO).
    """
    if request.method == "POST":
        try:
            if request.body:
                data = json.loads(request.body.decode('utf-8'))
                logger.info(f"Dados recebidos do DAO: {data}")
            else:
                logger.warning("Corpo vazio recebido do DAO.")
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            logger.error(f"Erro ao processar DAO: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"error": "Método não permitido."}, status=405)


# =========================================================
# 7. HEARTBEAT (/receive/api/notifications/device_is_alive)
# =========================================================

@csrf_exempt
def receber_heartbeat(request):
    """
    Recebe o sinal de vida da catraca e responde com 200 OK.
    """
    if request.method == 'POST':
        logger.info("Heartbeat recebido. Catraca está online.")
        return JsonResponse({"status": "success", "message": "OK"}, status=200)
    
    return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)