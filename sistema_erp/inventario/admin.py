from django.contrib import admin
from .models import Bodega, Stock, Merma

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('idBodega', 'nombre', 'region', 'direccion', 'capacidad')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('idStock', 'cantidad', 'lote', 'bodega')

@admin.register(Merma)
class MermaAdmin(admin.ModelAdmin):
    list_display = ('idMerma', 'lote', 'cantidad', 'motivo')
