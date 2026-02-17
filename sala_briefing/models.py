from django.db import models
from django.utils import timezone


class BriefingSession(models.Model):
    """
    Registro de Sala de Briefing.
    Cada registro representa uma sessão de briefing com dados do voo/serviço.
    """
    companhia_aerea = models.CharField(max_length=100, verbose_name="Companhia Aérea", default='')
    cliente_final = models.CharField(max_length=100, verbose_name="Cliente Final", default='')
    data = models.DateField(verbose_name="Data", null=True)
    prefixo_aeronave = models.CharField(max_length=50, verbose_name="Prefixo da Aeronave", default='', blank=True)
    numero_voo = models.IntegerField(verbose_name="Número do Voo", default=0)
    unidade_maritima = models.CharField(max_length=100, verbose_name="Unidade Marítima", default='')
    horario = models.TimeField(verbose_name="Horário", null=True)
    servico = models.CharField(max_length=200, verbose_name="Serviço", default='')
    solicitante = models.CharField(max_length=100, verbose_name="Solicitante", default='')

    # Controle interno
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Sessão de Briefing"
        verbose_name_plural = "Sessões de Briefing"
        ordering = ['-data', '-horario']

    def __str__(self):
        data_str = self.data.strftime('%d/%m/%Y') if self.data else 'Sem data'
        return f"Briefing Voo {self.numero_voo} — {self.companhia_aerea} — {data_str}"
