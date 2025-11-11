from django.db import models

class Bodega(models.Model):
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único de la bodega")
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15, blank=True)
    responsable = models.CharField(max_length=100, help_text="Nombre del encargado")
    capacidad_maxima = models.IntegerField(help_text="Capacidad en unidades", default=0)
    
    TIPO_CHOICES = [
        ('PRINCIPAL', 'Principal'),
        ('SECUNDARIA', 'Secundaria'),
        ('TRANSITO', 'Tránsito'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SECUNDARIA')
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"