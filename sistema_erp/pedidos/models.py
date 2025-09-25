from django.db import models
from usuarios.models import Usuario
from productos.models import Producto
from clientes.models import Cliente

class Pedido(models.Model):
    idPedido = models.AutoField(primary_key=True)
    fecha = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')

    def __str__(self):
        return f"Pedido {self.idPedido}"

class DetallePedido(models.Model):
    idDetallePedido = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_pedido')

    def __str__(self):
        return f"Detalle {self.idDetallePedido} - Pedido {self.pedido.idPedido}"
