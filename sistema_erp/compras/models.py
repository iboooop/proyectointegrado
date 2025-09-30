from django.db import models
from usuarios.models import Usuario
from proveedores.models import Proveedor
from productos.models import Producto

class OrdenCompra(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    idOrdenCompra = models.AutoField(primary_key=True)
    fecha = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='ordenes_compra')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ordenes_compra')

    def __str__(self):
        return f"OrdenCompra {self.idOrdenCompra}"

class DetalleOrdenCompra(models.Model):
    idDetalleOrdenCompra = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    ordenCompra = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_orden_compra')

    def __str__(self):
        return f"Detalle {self.idDetalleOrdenCompra} - Orden {self.ordenCompra.idOrdenCompra}"
