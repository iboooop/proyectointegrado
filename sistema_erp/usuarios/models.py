# apps/usuarios/models.py
from django.contrib.auth.models import User
from django.db import models

class Perfil(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('BODEGA', 'Operador de Bodega'),
        ('COMPRAS', 'Operador de Compras'),
        ('VENTAS', 'Operador de Ventas'),
        ('PRODUCCION', 'Jefe de Producción'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=15, blank=True)
    area = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.rol})"
