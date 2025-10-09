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

@admin.action(description="Marcar productos seleccionados como INACTIVOS")
def marcar_bajo(modeladmin, request, queryset):
    queryset.update(stock='BAJO')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm  # <--- Usamos el form con validaciones
    list_display = ('nombre', 'categoria', 'precio', 'stock_actual', 'fecha_vencimiento', 'lote', 'stock')
    search_fields = ('nombre', 'categoria', 'lote')
    list_filter = ('categoria', 'stock')
    list_per_page = 20
    ordering = ('nombre',)
    inlines = [MovimientoInline]
    actions = [marcar_alto, marcar_bajo]