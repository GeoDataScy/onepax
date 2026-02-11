from django.contrib import admin
from .models import BriefingSession


@admin.register(BriefingSession)
class BriefingSessionAdmin(admin.ModelAdmin):
    list_display = ('numero_voo', 'companhia_aerea', 'cliente_final', 'data', 'horario', 'unidade_maritima', 'servico', 'solicitante')
    list_filter = ('companhia_aerea', 'cliente_final', 'data')
    search_fields = ('companhia_aerea', 'cliente_final', 'solicitante', 'servico')
