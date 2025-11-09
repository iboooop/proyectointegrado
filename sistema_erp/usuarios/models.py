from django.db import models
from django.contrib.auth.models import User, Group

# ------------------------------
# PERFIL DE USUARIO
# ------------------------------

class Perfil(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('BODEGA', 'Operador de Bodega'),
        ('VENTAS', 'Operador de Ventas'),
        ('COMPRAS', 'Operador de Compras'),
    ]

    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=15, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    mfa_habilitado = models.BooleanField(default=False)
    sesiones_activas = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario.username} ({self.rol})"


# ------------------------------
# MÓDULOS DEL SISTEMA
# ------------------------------
class Module(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


# ------------------------------
# ROLES Y PERMISOS
# ------------------------------
class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")

    def __str__(self):
        return self.group.name


class RoleModulePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="module_perms")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="role_perms")
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_change = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "module")

    def __str__(self):
        return f"{self.role} -> {self.module} (v:{self.can_view}/a:{self.can_add}/c:{self.can_change}/d:{self.can_delete})"
