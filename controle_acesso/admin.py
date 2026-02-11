from django.contrib import admin
from .models import Catraca, EventoCatraca, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('role',)


@admin.register(Catraca)
class CatracaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ip', 'push_ativo')


@admin.register(EventoCatraca)
class EventoCatracaAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'catraca', 'sentido')
    list_filter = ('catraca', 'timestamp')
