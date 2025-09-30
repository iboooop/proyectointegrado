from django.contrib import admin
from .models import Bodega, Stock, Merma

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('idBodega', 'nombre', 'region', 'direccion', 'capacidad')
    search_fields = ('nombre', 'region', 'direccion')
    list_filter = ('region',)
    ordering = ('nombre',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('idStock', 'cantidad', 'lote', 'bodega')
    search_fields = ('lote__idLote', 'bodega__nombre')
    list_filter = ('bodega__region',)
    ordering = ('bodega__nombre',)
    list_select_related = ('lote', 'bodega')

@admin.register(Merma)
class MermaAdmin(admin.ModelAdmin):
    list_display = ('idMerma', 'lote', 'cantidad', 'motivo')
    search_fields = ('lote__idLote', 'motivo')
    list_filter = ('lote__producto__nombre',)
    ordering = ('lote__idLote',)
    list_select_related = ('lote',)