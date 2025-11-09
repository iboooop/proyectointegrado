from django.db import models
from productos.models import Producto
from proveedores.models import Proveedor
from django.contrib.auth.models import User
from usuarios.models import Perfil
from bodegas.models import Bodega  # ← NUEVO IMPORT
from clientes.models import Cliente  # ← NUEVO IMPORT

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
        ('VENTA', 'Venta'),  # ← NUEVO TIPO
        ('TRANSFERENCIA', 'Transferencia entre bodegas'),  # ← NUEVO TIPO
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)  # ← NUEVO CAMPO
    bodega_origen = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_origen')  # ← NUEVO CAMPO
    bodega_destino = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_destino')  # ← NUEVO CAMPO
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"