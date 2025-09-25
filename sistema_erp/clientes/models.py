from django.db import models
from core.models import BaseModel  # Importar el BaseModel

# Create your models here.

class Cliente(BaseModel):  # Heredar de BaseModel
    idCliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, db_index=True)  # Índice para mejorar consultas
    rut = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=45)
    estadoCondicion = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
