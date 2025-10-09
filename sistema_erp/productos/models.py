from django.db import models
from proveedores.models import Proveedor

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=[
        ('GALLETAS', 'Galletas'),
        ('CHOCOLATES', 'Chocolates'),
        ('ALFAJORES', 'Alfajores'),
        ('CONFITERIA', 'Confitería'),
    ])
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    lote = models.CharField(max_length=50, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    
    STOCK_CHOICES = [
        ('ALTO', 'Alto'),
        ('BAJO', 'Bajo'),
    ]
    stock = models.CharField(max_length=10, choices=STOCK_CHOICES, default='ALTO')

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"
