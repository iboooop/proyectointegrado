from django.contrib import admin
from .models import MovimientoInventario

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'proveedor', 'tipo', 'cantidad', 'fecha', 'usuario')
    search_fields = ('producto__nombre', 'proveedor__nombre', 'usuario__username')
    list_filter = ('tipo', 'fecha')
    list_per_page = 20
    ordering = ('-fecha',)

