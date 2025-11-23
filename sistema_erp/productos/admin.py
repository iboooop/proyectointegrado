from django.contrib import admin
from .models import Producto
from .forms import ProductoForm
from transacciones.models import MovimientoInventario



class MovimientoInline(admin.TabularInline):
    model = MovimientoInventario
    extra = 0
    fields = ('tipo', 'cantidad', 'usuario', 'proveedor')
    show_change_link = True

@admin.action(description="Marcar productos seleccionados como Stock ALTO")
def marcar_alto(modeladmin, request, queryset):
    queryset.update(stock='ALTO')

@admin.action(description="Marcar productos seleccionados como stock BAJO")
def marcar_bajo(modeladmin, request, queryset):
    queryset.update(stock='BAJO')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = (
        'sku', 'nombre', 'categoria', 'marca', 'modelo', 'proveedor',
        'uom_compra', 'uom_venta', 'factor_conversion',
        'costo_estandar', 'precio_venta', 'impuesto_iva',
        'stock_minimo', 'stock_maximo', 'punto_reorden',
        'perishable', 'control_por_lote', 'control_por_serie', 'bodega', 'stock_actual',
    )
    search_fields = ('sku', 'nombre', 'categoria', 'marca', 'modelo', 'proveedor__nombre')
    list_filter = ('categoria', 'marca', 'proveedor', 'bodega', 'perishable', 'control_por_lote', 'control_por_serie')
    list_per_page = 20
    ordering = ('nombre',)
    inlines = [MovimientoInline]
    actions = [marcar_alto, marcar_bajo]