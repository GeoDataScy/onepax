from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging
from .models import Catraca, EventoCatraca

logger = logging.getLogger(__name__)

# =========================================================
# 1. VIEW DE EVENTO DE GIRO (/receive/catra_event)
# =========================================================

@csrf_exempt
def receber_evento_catraca(request):
    """
    Recebe o evento de giro da Control iD, onde device_id está DENTRO da chave 'event'.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # --- DEBUG NO TERMINAL ---
            print("\n--- EVENTO GIRO RECEBIDO ---")
            print(json.dumps(data, indent=4))
            print("----------------------------\n")

            event_data = data.get('event', {})

            # 1. Identificar a Catraca pelo device_id
            # O ID é numérico na Control iD, mas o nosso modelo usa string (Ex: 'catraca_emb_01').
            # Vamos usar o campo 'device_id' do JSON para procurar no campo 'identificador' do nosso banco.
            device_id_recebido = event_data.get('device_id') # Ex: 935107
            
            # Nota: Você deve ter cadastrado as catracas com o ID NUMÉRICO real da Control ID.
            # Se você as cadastrou com 'catraca_emb_01', teremos que mudar no banco.
            # Por agora, assumimos que o ID está cadastrado no campo `identificador` do modelo Catraca.
            
            # Vamos procurar pelo ID numérico ou string
            catraca = Catraca.objects.filter(identificador=str(device_id_recebido)).first()
            
            if not catraca:
                logger.warning(f"Catraca não cadastrada: {device_id_recebido}")
                # Retorna 200 OK para a catraca não re-enviar
                return JsonResponse({"status": "error", "message": "Dispositivo desconhecido"}, status=200)

            # 2. Ler o Tipo de Giro
            tipo_giro = event_data.get('name', 'UNKNOWN') # Ex: "TURN LEFT"
            
            # 3. Salvar no Banco (Log completo)
            EventoCatraca.objects.create(
                catraca=catraca,
                timestamp=timezone.now(),
                sentido=tipo_giro,
                raw_data=json.dumps(data)
            )
            
            logger.info(f"Giro '{tipo_giro}' registrado na {catraca.nome}. Contador atualizando...")
            
            return JsonResponse({"status": "success", "message": "Evento processado"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
        except Exception as e:
            logger.error(f"Erro interno no evento de giro: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)


# =========================================================
# 2. VIEW DE HEARTBEAT (/receive/api/notifications/device_is_alive)
# =========================================================

@csrf_exempt
def receber_heartbeat(request):
    """
    Recebe o sinal de vida da catraca e responde com 200 OK.
    """
    if request.method == 'POST':
        # O Django só precisa responder 200 OK para confirmar que recebeu.
        logger.info("Heartbeat recebido. Catraca está online.")
        return JsonResponse({"status": "success", "message": "OK"}, status=200)
    
    return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)