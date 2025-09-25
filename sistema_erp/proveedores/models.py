from django.db import models
from productos.models import Producto

# Create your models here.

class Proveedor(models.Model):
    idProveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=150)

    def __str__(self):
        return self.nombre

class ProductoProveedor(models.Model):
    idProductoProveedor = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fechaRegistro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.proveedor.nombre}"
