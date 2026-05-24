from django.db import models
from django.core.validators import RegexValidator
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


class ContatoWhatsapp(models.Model):
    """
    Destinatários do relatório operacional diário enviado via WhatsApp.
    Telefone é armazenado no formato E.164 sem o '+' (ex: 5511987654321).
    """
    telefone_validator = RegexValidator(
        regex=r'^\d{12,15}$',
        message="Telefone deve conter apenas dígitos, no formato E.164 sem '+' (ex: 5511987654321)."
    )

    nome = models.CharField(max_length=100, verbose_name="Nome")
    telefone = models.CharField(
        max_length=15,
        unique=True,
        validators=[telefone_validator],
        verbose_name="Telefone (E.164 sem +)",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Contato WhatsApp"
        verbose_name_plural = "Contatos WhatsApp"
        ordering = ['nome']

    def __str__(self):
        status = "ativo" if self.ativo else "inativo"
        return f"{self.nome} ({self.telefone}) [{status}]"
