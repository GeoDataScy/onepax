from django.contrib import admin
from .models import AnaliseRegistro, ContatoWhatsapp, ConfiguracaoRelatorio


@admin.register(AnaliseRegistro)
class AnaliseRegistroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_analise', 'data_analise', 'criado_em')
    list_filter = ('tipo_analise', 'data_analise')
    search_fields = ('titulo', 'tipo_analise')


@admin.register(ContatoWhatsapp)
class ContatoWhatsappAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'telefone')
    list_editable = ('ativo',)


@admin.register(ConfiguracaoRelatorio)
class ConfiguracaoRelatorioAdmin(admin.ModelAdmin):
    list_display = ('horario_envio_diario', 'atualizado_em')

    def has_add_permission(self, request):
        return not ConfiguracaoRelatorio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
