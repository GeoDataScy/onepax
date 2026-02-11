from django.db import models
from django.utils import timezone


class BriefingSession(models.Model):
    """
    Placeholder para sessões de briefing.
    Será expandido conforme requisitos futuros.
    """
    titulo = models.CharField(max_length=200, verbose_name="Título do Briefing")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_sessao = models.DateTimeField(default=timezone.now, verbose_name="Data da Sessão")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Sessão de Briefing"
        verbose_name_plural = "Sessões de Briefing"
        ordering = ['-data_sessao']

    def __str__(self):
        return f"Briefing: {self.titulo} — {self.data_sessao.strftime('%d/%m/%Y %H:%M')}"
