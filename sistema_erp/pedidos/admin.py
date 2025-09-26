from django.contrib import admin
from .models import Pedido, DetallePedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('idPedido', 'fecha', 'cliente', 'usuario')
    search_fields = ('cliente__nombre', 'usuario__nombre')
    list_filter = ('fecha',)
    ordering = ('fecha',)
    list_select_related = ('cliente', 'usuario')

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('idDetallePedido', 'cantidad', 'precioUnitario', 'pedido', 'producto')
    search_fields = ('pedido__idPedido', 'producto__nombre')
    list_filter = ('pedido__fecha',)
    ordering = ('pedido__fecha',)
    list_select_related = ('pedido', 'producto')