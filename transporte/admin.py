from django.contrib import admin
from .models import RegistroTransporte


@admin.register(RegistroTransporte)
class RegistroTransporteAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'origem', 'destino', 'data_transporte', 'criado_em')
    list_filter = ('data_transporte',)
    search_fields = ('descricao', 'origem', 'destino')
