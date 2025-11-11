from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['idCliente', 'rut', 'nombre', 'telefono', 'email', 'estadoCondicion']
    list_filter = ['estadoCondicion']
    search_fields = ['rut', 'nombre', 'email']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'rut')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Estado', {
            'fields': ('estadoCondicion',)
        }),
    )