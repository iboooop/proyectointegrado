from django.db import models
from productos.models import Lote

# Create your models here.

class Bodega(models.Model):
    idBodega = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    capacidad = models.IntegerField()

    def __str__(self):
        return self.nombre

class Stock(models.Model):
    idStock = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)

    def __str__(self):
        return f"Stock {self.idStock} - Lote {self.lote.idLote}"

class Merma(models.Model):
    idMerma = models.AutoField(primary_key=True)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=200)

    def __str__(self):
        return f"Merma {self.idMerma} - Lote {self.lote.idLote}"
