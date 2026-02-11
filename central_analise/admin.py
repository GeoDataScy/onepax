from django.contrib import admin
from .models import AnaliseRegistro


@admin.register(AnaliseRegistro)
class AnaliseRegistroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_analise', 'data_analise', 'criado_em')
    list_filter = ('tipo_analise', 'data_analise')
    search_fields = ('titulo', 'tipo_analise')
