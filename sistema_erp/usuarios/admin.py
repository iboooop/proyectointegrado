from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'estado')
    search_fields = ('nombre', 'email')
    list_filter = ('estado',)
    ordering = ('nombre',)