from django.contrib import admin
from .models import Perfil, Module, Role, RoleModulePermission
from transacciones.models import MovimientoInventario
from .forms import PerfilForm


# ============================================================
# Inline: Movimientos asociados a un usuario
# ============================================================
class MovimientoUsuarioInline(admin.TabularInline):
    model = MovimientoInventario
    extra = 0
    fields = ('producto', 'tipo', 'cantidad', 'proveedor')
    show_change_link = True


# ============================================================
# Perfil del usuario
# ============================================================
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    form = PerfilForm
    list_display = ('usuario', 'rol', 'telefono', 'area')
    search_fields = ('usuario__username', 'rol', 'area')
    list_filter = ('rol',)
    list_per_page = 20
    ordering = ('usuario',)
    inlines = [MovimientoUsuarioInline]


# ============================================================
# Módulos del ERP
# ============================================================
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'icon')
    search_fields = ('code', 'name')


# ============================================================
# Roles
# ============================================================
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('group',)
    search_fields = ('group__name',)


# ============================================================
# Permisos por módulo
# ============================================================
@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module', 'can_view', 'can_add', 'can_change', 'can_delete')
    list_filter = ('role', 'module')
    search_fields = ('role__group__name', 'module__name')
    list_editable = ('can_view', 'can_add', 'can_change', 'can_delete')
