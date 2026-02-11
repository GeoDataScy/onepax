from django.contrib import admin
from .models import BriefingSession


@admin.register(BriefingSession)
class BriefingSessionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_sessao', 'criado_em')
    list_filter = ('data_sessao',)
    search_fields = ('titulo',)
