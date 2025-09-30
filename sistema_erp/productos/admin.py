from django.contrib import admin
from .models import Producto, Lote, Costo

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precioBase')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)
    ordering = ('nombre',)

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('idLote', 'fechaIngreso', 'fechaVencimiento', 'producto', 'ubicacion')
    search_fields = ('producto__nombre', 'ubicacion')
    list_filter = ('fechaIngreso', 'fechaVencimiento')
    ordering = ('fechaIngreso',)
    list_select_related = ('producto',)

@admin.register(Costo)
class CostoAdmin(admin.ModelAdmin):
    list_display = ('idCosto', 'monto', 'lote', 'producto', 'fechaCosto')
    search_fields = ('producto__nombre', 'lote__idLote')
    list_filter = ('fechaCosto',)
    ordering = ('fechaCosto',)
    list_select_related = ('lote', 'producto')