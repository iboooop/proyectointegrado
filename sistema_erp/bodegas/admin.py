from django.contrib import admin
from .models import Bodega

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'estado', 'responsable', 'capacidad_maxima']
    list_filter = ['estado', 'tipo']
    search_fields = ['codigo', 'nombre', 'responsable']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'tipo')
        }),
        ('Ubicación y Contacto', {
            'fields': ('direccion', 'telefono', 'responsable')
        }),
        ('Capacidad y Estado', {
            'fields': ('capacidad_maxima', 'estado')
        }),
    )