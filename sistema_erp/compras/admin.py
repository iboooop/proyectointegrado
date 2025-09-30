from django.contrib import admin
from .models import OrdenCompra, DetalleOrdenCompra

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('idOrdenCompra', 'fecha', 'estado', 'proveedor', 'usuario')
    search_fields = ('proveedor__nombre', 'usuario__nombre')
    list_filter = ('estado', 'fecha')
    ordering = ('fecha',)
    list_select_related = ('proveedor', 'usuario')

@admin.register(DetalleOrdenCompra)
class DetalleOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('idDetalleOrdenCompra', 'cantidad', 'precioUnitario', 'ordenCompra', 'producto')
    search_fields = ('ordenCompra__idOrdenCompra', 'producto__nombre')
    list_filter = ('ordenCompra__fecha',)
    ordering = ('ordenCompra__fecha',)
    list_select_related = ('ordenCompra', 'producto')