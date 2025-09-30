from django.db import models

# Create your models here.

class Producto(models.Model):
    idProducto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    precioBase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Lote(models.Model):
    idLote = models.AutoField(primary_key=True)
    fechaIngreso = models.DateTimeField()
    fechaVencimiento = models.DateTimeField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=45)

    def __str__(self):
        return f"Lote {self.idLote} - {self.producto.nombre}"

class Costo(models.Model):
    idCosto = models.AutoField(primary_key=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fechaCosto = models.DateTimeField()

    def __str__(self):
        return f"Costo {self.idCosto} - {self.producto.nombre}"
