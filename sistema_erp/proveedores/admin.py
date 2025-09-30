from django.contrib import admin
from .models import Proveedor, ProductoProveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'direccion', 'telefono', 'email')
    search_fields = ('nombre', 'rut', 'email')
    list_filter = ('direccion',)
    ordering = ('nombre',)

@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    list_display = ('producto', 'proveedor', 'precio', 'fechaRegistro')
    search_fields = ('producto__nombre', 'proveedor__nombre')
    list_filter = ('fechaRegistro',)
    ordering = ('fechaRegistro',)
    list_select_related = ('producto', 'proveedor')