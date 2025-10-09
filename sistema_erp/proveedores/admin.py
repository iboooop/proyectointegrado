from django.contrib import admin
from .models import Proveedor
from .forms import ProveedorForm
from productos.models import Producto

class ProductoInline(admin.TabularInline):
    model = Producto
    extra = 0
    fields = ('nombre', 'categoria', 'precio', 'stock_actual', 'fecha_vencimiento')
    show_change_link = True

@admin.action(description="Marcar proveedores seleccionados como ACTIVOS")
def marcar_activo(modeladmin, request, queryset):
    queryset.update(estado='ACTIVO')

@admin.action(description="Marcar proveedores seleccionados como INACTIVOS")
def marcar_inactivo(modeladmin, request, queryset):
    queryset.update(estado='INACTIVO')

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    form = ProveedorForm  # <--- Usamos el form con validaciones
    list_display = ('nombre', 'rut', 'contacto', 'telefono', 'correo', 'estado')
    search_fields = ('nombre', 'rut', 'correo')
    list_filter = ('estado',)
    list_per_page = 20
    ordering = ('nombre',)
    inlines = [ProductoInline]
    actions = [marcar_activo, marcar_inactivo]