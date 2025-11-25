from django.db import models
from django.utils import timezone
from productos.models import Producto
from proveedores.models import Proveedor
from django.contrib.auth.models import User
from usuarios.models import Perfil


class Bodega(models.Model):
    """Modelo para almacenar las bodegas del sistema."""
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True)
    capacidad_maxima = models.IntegerField(default=0, help_text="Capacidad máxima en unidades")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('INGRESO', 'Ingreso'),
        ('SALIDA', 'Salida'),
        ('VENTA', 'Venta'),
        ('DEVOLUCION', 'Devolución'),
        ('AJUSTE', 'Ajuste'),
        ('TRANSFERENCIA', 'Transferencia entre bodegas'),
    ]
    ESTADO_CHOICES = [
        ('POR_CONFIRMAR', 'Por confirmar'),
        ('EN_PROCESO', 'En proceso'),
        ('CANCELADO', 'Cancelado'),
        ('DESACTIVADO', 'Desactivado'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Bodegas
    bodega_origen = models.ForeignKey(
        Bodega, 
        on_delete=models.PROTECT, 
        related_name='movimientos_origen',
        help_text="Bodega de origen del movimiento (obligatorio)"
    )
    bodega_destino = models.ForeignKey(
        Bodega, 
        on_delete=models.PROTECT, 
        related_name='movimientos_destino',
        null=True, 
        blank=True,
        help_text="Bodega de destino (solo para transferencias)"
    )

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='POR_CONFIRMAR')
    fecha_activacion = models.DateTimeField(null=True, blank=True)
    fecha_desactivacion = models.DateTimeField(null=True, blank=True)
    # Control avanzado
    manejo_lotes = models.BooleanField(default=False)
    manejo_series = models.BooleanField(default=False)
    perecible = models.BooleanField(default=False)
    lote = models.CharField(max_length=50, blank=True)
    serie = models.CharField(max_length=100, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    # Referencias
    doc_referencia = models.CharField(max_length=120, blank=True)
    doc_referencia_file = models.FileField(upload_to='transacciones/docs/', blank=True, null=True)
    motivo = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"