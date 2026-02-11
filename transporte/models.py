from django.db import models
from django.utils import timezone


class RegistroTransporte(models.Model):
    """
    Placeholder para registros de transporte.
    Será expandido conforme requisitos futuros.
    """
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    origem = models.CharField(max_length=100, verbose_name="Origem")
    destino = models.CharField(max_length=100, verbose_name="Destino")
    data_transporte = models.DateTimeField(default=timezone.now, verbose_name="Data do Transporte")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Registro de Transporte"
        verbose_name_plural = "Registros de Transporte"
        ordering = ['-data_transporte']

    def __str__(self):
        return f"Transporte: {self.origem} → {self.destino} — {self.data_transporte.strftime('%d/%m/%Y %H:%M')}"
