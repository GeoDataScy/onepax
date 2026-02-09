from django.db import models
from django.utils import timezone

# =========================================================
# 1. CADASTRO DE EQUIPAMENTOS (AS 3 CATRACAS)
# =========================================================
# controle_acesso/models.py
from django.db import models
from django.utils import timezone

class Catraca(models.Model):
    TIPO_CHOICES = [
        ('EMBARQUE', 'Embarque (Soma no Voo de Saída)'),
        ('DESEMBARQUE', 'Desembarque (Soma no Voo de Chegada)'),
    ]

    nome = models.CharField(max_length=50, help_text="Ex: Catraca 1 - Portão A")
    identificador = models.CharField(max_length=50, unique=True, verbose_name="ID do Dispositivo")
    ip = models.GenericIPAddressField(verbose_name="Endereço IP", blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Operação")
    push_ativo = models.BooleanField(default=False, verbose_name="PUSH Ativo?")
    
    # NOVO CAMPO: Marco zero individual da catraca
    inicio_contagem = models.DateTimeField(default=timezone.now, verbose_name="Início da Contagem Atual")

    def __str__(self):
        return f"{self.nome} ({self.tipo}) - {self.identificador}"

# ... (O resto do ficheiro EventoCatraca permanece igual)

# =========================================================
# 2. LOG DE GIROS (EVENTOS)
# =========================================================
class EventoCatraca(models.Model):
    # Relaciona o giro à catraca específica que gerou o evento
    catraca = models.ForeignKey(Catraca, on_delete=models.CASCADE, related_name="eventos")
    
    # Data e hora exata do giro
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Sentido do giro (Horário/Anti-horário) - Importante para saber se entrou ou saiu
    sentido = models.CharField(max_length=20, blank=True, null=True)
    
    # Payload completo (JSON bruto para auditoria)
    raw_data = models.TextField(blank=True, null=True, verbose_name="Dados Brutos")

    class Meta:
        verbose_name = "Evento de Giro"
        verbose_name_plural = "Eventos de Giro"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Giro em {self.catraca.nome} às {self.timestamp.strftime('%H:%M:%S')}"