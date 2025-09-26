from django.contrib import admin
from .models import OrdenCompra, DetalleOrdenCompra

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('idOrdenCompra', 'fecha', 'estado', 'proveedor', 'usuario')

@admin.register(DetalleOrdenCompra)
class DetalleOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('idDetalleOrdenCompra', 'cantidad', 'precioUnitario', 'ordenCompra', 'producto')
