from django.db import models
from django.utils import timezone
from productos.models import Producto
from proveedores.models import Proveedor
from django.contrib.auth.models import User
from usuarios.models import Perfil


class Bodega(models.Model):
    """Bodegas o ubicaciones de inventario.

    Mantenerlo en este módulo evita acoplar con otros apps hasta que se requiera
    un catálogo más complejo.
    """
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"

    def __str__(self) -> str:  # pragma: no cover - representación simple
        return f"{self.codigo} - {self.nombre}"

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
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)  # referencia al app clientes
    bodega_origen = models.ForeignKey('bodegas.Bodega', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_origen')  # referencia al app bodegas
    bodega_destino = models.ForeignKey('bodegas.Bodega', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_destino')  # referencia al app bodegas
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True)
    bodega = models.ForeignKey('Bodega', on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    # Control avanzado
    manejo_lotes = models.BooleanField(default=False)
    manejo_series = models.BooleanField(default=False)
    perecible = models.BooleanField(default=False)
    lote = models.CharField(max_length=50, blank=True)
    serie = models.CharField(max_length=100, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    # Referencias
    doc_referencia = models.CharField(max_length=120, blank=True)
    motivo = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"