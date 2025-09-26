from django.contrib import admin
from .models import OrdenProduccion, Consumo

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ('idOrdenProduccion', 'fechaInicio', 'fechaFinalizacion', 'estado')

@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = ('idConsumo', 'cantidad', 'merma', 'producto', 'ordenProduccion')
