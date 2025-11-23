from django.db import models
from bodegas.models import Bodega
from proveedores.models import Proveedor


class CategoriaProducto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    idProducto = models.AutoField(primary_key=True)

    # Identificación
    sku = models.CharField(max_length=16, unique=True, verbose_name="SKU")
    ean_upc = models.CharField(
        max_length=13, unique=True, blank=True, null=True, verbose_name="EAN/UPC"
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, blank=True)
    categoria = models.CharField(
        max_length=50,
        choices=[
            ("ALFAJORES", "Alfajores"),
            ("BARRAS", "Barras"),
            ("CUCHUFLIES", "Cuchuflies"),
            ("ESPECIALES", "Especiales"),
            ("GALLETAS", "Galletas"),
            ("GOLOSINAS", "Golosinas"),
            ("REGALOS", "Regalos corporativos"),
            ("RETAIL", "Venta retail"),
        ],
    )
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)

    # Unidades y precios
    UOM_CHOICES = [
        ("UN", "Unidad"),
        ("CAJA", "Caja"),
        ("KG", "Kilogramo"),
        ("GR", "Gramo"),
        ("LT", "Litro"),
        ("PAQ", "Paquete"),
    ]
    uom_compra = models.CharField(max_length=10, choices=UOM_CHOICES)
    uom_venta = models.CharField(max_length=10, choices=UOM_CHOICES)

    factor_conversion = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    costo_estandar = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    costo_promedio = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True, editable=False
    )
    precio_venta = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19)

    # Stock y control
    stock_minimo = models.IntegerField(default=0)
    stock_maximo = models.IntegerField(blank=True, null=True)
    punto_reorden = models.IntegerField(blank=True, null=True)
    perishable = models.BooleanField(default=False)
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)

    # Relaciones y soporte
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="productos",
    )
    bodega = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True)

    # Imagen subida + URLs opcionales
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    ficha_tecnica_url = models.URLField(blank=True, null=True)

    # Derivados / solo lectura
    stock_actual = models.IntegerField(default=0, editable=False)

    # Estado del producto
    activo = models.BooleanField(default=False)
    fecha_activacion = models.DateTimeField(blank=True, null=True)
    fecha_desactivacion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.sku} - {self.nombre} ({self.categoria})"

    @property
    def id(self):
        return self.idProducto

    @property
    def alerta_bajo_stock(self):
        if self.stock_actual <= (self.stock_minimo or 0):
            return True
        if self.punto_reorden is not None and self.stock_actual <= self.punto_reorden:
            return True
        return False

    @property
    def alerta_por_vencer(self):
        if self.perishable and hasattr(self, "fecha_vencimiento") and self.fecha_vencimiento:
            from datetime import date, timedelta

            dias_alerta = 30
            return self.fecha_vencimiento <= (date.today() + timedelta(days=dias_alerta))
        return False