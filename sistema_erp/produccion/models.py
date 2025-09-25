from django.db import models
from productos.models import Producto

class OrdenProduccion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('finalizado', 'Finalizado'),
    ]

    idOrdenProduccion = models.AutoField(primary_key=True)
    fechaInicio = models.DateTimeField()
    fechaFinalizacion = models.DateTimeField()
    estado = models.CharField(max_length=50, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"OrdenProduccion {self.idOrdenProduccion}"

class Consumo(models.Model):
    idConsumo = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    merma = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='consumos')
    ordenProduccion = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE, related_name='consumos')

    def clean(self):
        if self.cantidad <=  0 or self.merma <= 0:
            raise ValueError("La cantidad y la merma no pueden ser negativas.")

    def __str__(self):
        return f"Consumo {self.idConsumo} - Orden {self.ordenProduccion.idOrdenProduccion}"
