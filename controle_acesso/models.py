from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# =========================================================
# 0. PERFIL DE USUÁRIO COM ROLES
# =========================================================
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('apac', 'APAC'),
        ('supervisor', 'Supervisor'),
        ('superintendente', 'Superintendente'),
        ('admin', 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='apac', verbose_name="Função")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria perfil automaticamente ao criar novo usuário"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva perfil ao salvar usuário"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

# =========================================================
# 1. CADASTRO DE EQUIPAMENTOS (AS 3 CATRACAS)
# =========================================================

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
    
    # Controle do protocolo PUSH (anti-spam de 5 segundos)
    last_command_time = models.DateTimeField(null=True, blank=True, verbose_name="Último Comando PUSH")
    
    # Anti-rebote: último evento de giro registrado (evita duplicatas)
    last_event_time = models.DateTimeField(null=True, blank=True, verbose_name="Último Evento de Giro")

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