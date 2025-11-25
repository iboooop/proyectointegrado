from django.db import models

PAISES_CHOICES = [
    ('Argentina', 'Argentina'),
    ('Bolivia', 'Bolivia'),
    ('Brasil', 'Brasil'),
    ('Chile', 'Chile'),
    ('China', 'China'),
    ('Colombia', 'Colombia'),
    ('Costa Rica', 'Costa Rica'),
    ('Cuba', 'Cuba'),
    ('Ecuador', 'Ecuador'),
    ('El Salvador', 'El Salvador'),
    ('España', 'España'),
    ('EEUU', 'Estados Unidos'),
    ('Guatemala', 'Guatemala'),
    ('Honduras', 'Honduras'),
    ('México', 'México'),
    ('Nicaragua', 'Nicaragua'),
    ('Panamá', 'Panamá'),
    ('Paraguay', 'Paraguay'),
    ('Perú', 'Perú'),
    ('República Dominicana', 'República Dominicana'),
    ('Uruguay', 'Uruguay'),
    ('Venezuela', 'Venezuela'),
]


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    razon_social = models.CharField(max_length=200)
    nombre_fantasia = models.CharField(max_length=200, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    correo = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    sitio_web = models.URLField(max_length=200, blank=True)  # Campo añadido
    direccion = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=50, choices=PAISES_CHOICES, default='Chile')
    
    MONEDA_CHOICES = [
        ('CLP', 'CLP (Peso chileno)'),
        ('USD', 'USD (Dólar)'),
        ('EUR', 'EUR (Euro)'),
    ]
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='CLP')

    plazo_pago = models.CharField(max_length=20, choices=[
        ('Contado', 'Contado'),
        ('30 días', '30 días'),
        ('60 días', '60 días'),
        ('90 días', '90 días'),
    ], default='Contado')
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    proveedor_preferente = models.BooleanField(default=False)
    lead_time = models.PositiveIntegerField(default=7)  # Tiempo de entrega en días
    observaciones = models.TextField(blank=True)

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
