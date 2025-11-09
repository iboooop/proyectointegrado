from django.db import models

class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    idCliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)  # ← CAMBIO CLAVE
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)  # ← CAMBIO CLAVE
    estadoCondicion = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO'  # ← CAMBIO para consistencia
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)  # ← NUEVO
    
    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']  # ← NUEVO
    
    def __str__(self):
        return f"{self.nombre} ({self.rut})"