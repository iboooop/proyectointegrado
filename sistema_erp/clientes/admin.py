from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'direccion', 'telefono', 'email', 'estadoCondicion')
    search_fields = ('nombre', 'rut', 'email')
    list_filter = ('estadoCondicion',)
    ordering = ('nombre',)