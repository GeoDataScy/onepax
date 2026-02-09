from django.contrib import admin
from .models import Catraca, EventoCatraca

@admin.register(Catraca)
class CatracaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ip', 'push_ativo')

@admin.register(EventoCatraca)
class EventoCatracaAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'catraca', 'sentido')
    list_filter = ('catraca', 'timestamp')
