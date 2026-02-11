from django.db import models


class RegistroTransporte(models.Model):
    """
    Registro de Transporte.
    Cada registro representa uma solicitação de transporte.
    """
    empresa_solicitante = models.CharField(max_length=100, verbose_name="Empresa que Solicita", default='')
    cliente_final = models.CharField(max_length=100, verbose_name="Cliente Final", default='')
    data = models.DateField(verbose_name="Data", null=True)
    numero_voo = models.IntegerField(verbose_name="Número do Voo", default=0)
    prefixo_aeronave = models.CharField(max_length=50, verbose_name="Prefixo da Aeronave", default='', blank=True)
    prefixo_manual = models.CharField(
        max_length=50,
        verbose_name="Prefixo Manual",
        default='',
        blank=True,
        help_text="Preencher somente se o campo Prefixo da Aeronave não for informado"
    )
    horario = models.TimeField(verbose_name="Horário", null=True)
    servico = models.CharField(max_length=200, verbose_name="Serviço", default='')

    # Controle interno
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Registro de Transporte"
        verbose_name_plural = "Registros de Transporte"
        ordering = ['-data', '-horario']

    def __str__(self):
        data_str = self.data.strftime('%d/%m/%Y') if self.data else 'Sem data'
        return f"Transporte Voo {self.numero_voo} — {self.empresa_solicitante} — {data_str}"
