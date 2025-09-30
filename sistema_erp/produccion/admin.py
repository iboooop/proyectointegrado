from django.contrib import admin
from .models import OrdenProduccion, Consumo

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ('idOrdenProduccion', 'fechaInicio', 'fechaFinalizacion', 'estado')
    search_fields = ('estado',)
    list_filter = ('estado', 'fechaInicio', 'fechaFinalizacion')
    ordering = ('fechaInicio',)

@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = ('idConsumo', 'cantidad', 'merma', 'producto', 'ordenProduccion')
    search_fields = ('producto__nombre', 'ordenProduccion__idOrdenProduccion')
    list_filter = ('ordenProduccion__estado',)
    ordering = ('ordenProduccion__fechaInicio',)
    list_select_related = ('producto', 'ordenProduccion')