from django.contrib import admin
from .models import RegistroTransporte


@admin.register(RegistroTransporte)
class RegistroTransporteAdmin(admin.ModelAdmin):
    list_display = ('numero_voo', 'empresa_solicitante', 'cliente_final', 'data', 'horario', 'prefixo_aeronave', 'servico')
    list_filter = ('empresa_solicitante', 'cliente_final', 'data')
    search_fields = ('empresa_solicitante', 'cliente_final', 'servico')
