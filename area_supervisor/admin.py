from django.contrib import admin
from .models import SupervisorLog


@admin.register(SupervisorLog)
class SupervisorLogAdmin(admin.ModelAdmin):
    list_display = ('acao', 'data_registro', 'criado_em')
    list_filter = ('data_registro',)
    search_fields = ('acao', 'detalhes')
