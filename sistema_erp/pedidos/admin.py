from django.contrib import admin
from .models import Pedido, DetallePedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('idPedido', 'fecha', 'cliente', 'usuario')

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('idDetallePedido', 'cantidad', 'precioUnitario', 'pedido', 'producto')
