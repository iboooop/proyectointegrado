from django.contrib import admin
from .models import Perfil, Module, Role, RoleModulePermission
from transacciones.models import MovimientoInventario
from .forms import PerfilForm
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from productos.models import Producto
from proveedores.models import Proveedor
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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
    # Mostrar los campos booleanos como iconos (marca/cruz) en lugar de
    # inputs editables en la lista. Para editar, entra a cada fila.
    list_display_links = ('role',)

    actions = ['sync_selected_role_permissions']

    # Helper para mapear módulo -> modelo (coincide con lo que usa el seed)
    def model_for_module(self, module):
        code = module.code
        if code == 'productos':
            return Producto
        if code == 'proveedores':
            return Proveedor
        if code == 'transacciones':
            return MovimientoInventario
        if code == 'usuarios':
            return User
        return None

    def sync_role_permissions(self, role):
        """Construye y aplica la lista de Permission para el group del role
        basada en los RoleModulePermission asociados.
        """
        grupo = role.group
        permisos_a_asignar = []
        rms = RoleModulePermission.objects.filter(role=role)
        for rm in rms:
            model_cls = self.model_for_module(rm.module)
            if not model_cls:
                continue
            ct = ContentType.objects.get_for_model(model_cls)
            codenames = []
            if rm.can_view:
                codenames.append(f'view_{model_cls._meta.model_name}')
            if rm.can_add:
                codenames.append(f'add_{model_cls._meta.model_name}')
            if rm.can_change:
                codenames.append(f'change_{model_cls._meta.model_name}')
            if rm.can_delete:
                codenames.append(f'delete_{model_cls._meta.model_name}')
            if codenames:
                perms = Permission.objects.filter(content_type=ct, codename__in=codenames)
                permisos_a_asignar.extend(list(perms))

        grupo.permissions.set(permisos_a_asignar)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Después de guardar la fila, sincronizamos los permisos del grupo
        try:
            self.sync_role_permissions(obj.role)
        except Exception:
            # No queremos que un error de sincronización rompa el admin; mostrar mensaje es mejor
            pass

    def delete_model(self, request, obj):
        role = obj.role
        super().delete_model(request, obj)
        # Re-sincronizar para actualizar el grupo después de borrar la fila
        try:
            self.sync_role_permissions(role)
        except Exception:
            pass

    def sync_selected_role_permissions(self, request, queryset):
        roles = {q.role for q in queryset}
        for role in roles:
            try:
                self.sync_role_permissions(role)
            except Exception:
                pass
        self.message_user(request, f"Sincronizados permisos para {len(roles)} role(s).")
    sync_selected_role_permissions.short_description = 'Sync selected RoleModulePermission -> Group permissions'


# ------------------------------------------------------------
# Personalizar lista de Users para mostrar is_staff y rol/grupo
# ------------------------------------------------------------
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'display_role', 'display_groups')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'perfil__rol')

    def display_role(self, obj):
        # Intentar obtener el perfil y mostrar rol legible
        try:
            perfil = obj.perfil
            return perfil.get_rol_display() if hasattr(perfil, 'get_rol_display') else perfil.rol
        except Exception:
            return '-'
    display_role.short_description = _('Rol')
    display_role.admin_order_field = 'perfil__rol'

    def display_groups(self, obj):
        groups = obj.groups.all()
        if not groups:
            return '-'
        # Mostrar como lista separada por comas con enlace al grupo en admin
        parts = []
        for g in groups:
            try:
                url = reverse('admin:auth_group_change', args=(g.pk,))
                parts.append(f"<a href='{url}'>{g.name}</a>")
            except Exception:
                parts.append(g.name)
        return format_html(', '.join(parts))
    display_groups.short_description = _('Groups')


# Re-registrar User admin: primero anular el registro anterior si existe
try:
    admin.site.unregister(User)
except Exception:
    pass
admin.site.register(User, UserAdmin)
