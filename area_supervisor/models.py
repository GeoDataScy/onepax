from django.db import models
from django.utils import timezone


class SupervisorLog(models.Model):
    """
    Placeholder para logs do supervisor.
    Será expandido conforme requisitos futuros.
    """
    acao = models.CharField(max_length=200, verbose_name="Ação")
    detalhes = models.TextField(blank=True, null=True, verbose_name="Detalhes")
    data_registro = models.DateTimeField(default=timezone.now, verbose_name="Data do Registro")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Log do Supervisor"
        verbose_name_plural = "Logs do Supervisor"
        ordering = ['-data_registro']

    def __str__(self):
        return f"Log: {self.acao} — {self.data_registro.strftime('%d/%m/%Y %H:%M')}"
