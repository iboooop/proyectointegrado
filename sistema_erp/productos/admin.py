from django.contrib import admin
from .models import Producto, Lote, Costo

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precioBase')

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('idLote', 'fechaIngreso', 'fechaVencimiento', 'producto', 'ubicacion')

@admin.register(Costo)
class CostoAdmin(admin.ModelAdmin):
    list_display = ('idCosto', 'monto', 'lote', 'producto', 'fechaCosto')
