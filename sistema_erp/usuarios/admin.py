from django.contrib import admin
from .models import Perfil
from transacciones.models import MovimientoInventario
from .forms import PerfilForm

class MovimientoUsuarioInline(admin.TabularInline):
    model = MovimientoInventario
    extra = 0
    fields = ('producto', 'tipo', 'cantidad', 'proveedor')
    show_change_link = True


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    form = PerfilForm  # <--- Usamos el form con validaciones
    list_display = ('usuario', 'rol', 'telefono', 'area')
    search_fields = ('usuario__username', 'rol', 'area')
    list_filter = ('rol',)
    list_per_page = 20
    ordering = ('usuario',)
    inlines = [MovimientoUsuarioInline]
