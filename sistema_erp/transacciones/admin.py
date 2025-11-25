from django.contrib import admin
from .models import MovimientoInventario, Bodega
from .forms import MovimientoInventarioForm

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'direccion', 'capacidad_maxima', 'estado', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'direccion')
    list_filter = ('estado',)
    list_per_page = 20
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    form = MovimientoInventarioForm  # <--- Usamos el form con validaciones
    list_display = ('producto', 'proveedor', 'bodega_origen', 'bodega_destino', 'tipo', 'cantidad', 'fecha', 'usuario')
    search_fields = ('producto__nombre', 'proveedor__nombre', 'usuario__username', 'bodega_origen__nombre', 'bodega_destino__nombre')
    list_filter = ('tipo', 'fecha', 'bodega_origen', 'estado')
    list_per_page = 20
    ordering = ('-fecha',)

