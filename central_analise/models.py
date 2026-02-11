from django.db import models
from django.utils import timezone


class AnaliseRegistro(models.Model):
    """
    Placeholder para registros de análise.
    Será expandido conforme requisitos futuros.
    """
    titulo = models.CharField(max_length=200, verbose_name="Título")
    tipo_analise = models.CharField(max_length=100, verbose_name="Tipo de Análise")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_analise = models.DateTimeField(default=timezone.now, verbose_name="Data da Análise")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Registro de Análise"
        verbose_name_plural = "Registros de Análise"
        ordering = ['-data_analise']

    def __str__(self):
        return f"Análise: {self.titulo} — {self.data_analise.strftime('%d/%m/%Y %H:%M')}"
