
from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ACTIVO')

    # Relación con categorías de productos (referencia perezosa para evitar import circular)
    categorias = models.ManyToManyField(
        'productos.CategoriaProducto',
        blank=True,
        related_name="proveedores",
    )

    def __str__(self):
        return self.nombre
