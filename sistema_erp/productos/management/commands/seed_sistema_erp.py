from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from usuarios.models import Perfil, Module, Role, RoleModulePermission
from proveedores.models import Proveedor
from productos.models import Producto
from transacciones.models import MovimientoInventario

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el sistema ERP con roles, módulos y permisos'

    def handle(self, *args, **kwargs):
        # ============================================================
        # 1️⃣ Crear roles (Grupos) y asociar al modelo Role
        # ============================================================
        roles = ['Administrador', 'Bodega', 'Compras']
        for r in roles:
            grupo, _ = Group.objects.get_or_create(name=r)
            Role.objects.get_or_create(group=grupo)

        # ============================================================
        # 2️⃣ Crear módulos del ERP
        # ============================================================
        modulos = [
            ('productos', 'Productos'),
            ('proveedores', 'Proveedores'),
            ('transacciones', 'Transacciones'),
            ('usuarios', 'Usuarios'),
        ]
        for code, name in modulos:
            Module.objects.get_or_create(code=code, name=name)

        # ============================================================
        # 3️⃣ Asignar permisos por rol y módulo
        # ============================================================
        admin_role = Role.objects.get(group__name='Administrador')
        bodega_role = Role.objects.get(group__name='Bodega')
        compras_role = Role.objects.get(group__name='Compras')

        productos_module = Module.objects.get(code='productos')
        proveedores_module = Module.objects.get(code='proveedores')
        transacciones_module = Module.objects.get(code='transacciones')
        usuarios_module = Module.objects.get(code='usuarios')

        # Admin puede todo
        for module in [productos_module, proveedores_module, transacciones_module, usuarios_module]:
            RoleModulePermission.objects.get_or_create(
                role=admin_role,
                module=module,
                defaults={
                    'can_view': True,
                    'can_add': True,
                    'can_change': True,
                    'can_delete': True,
                }
            )

        # Bodega solo maneja transacciones
        RoleModulePermission.objects.get_or_create(
            role=bodega_role,
            module=transacciones_module,
            defaults={
                'can_view': True,
                'can_add': True,
                'can_change': False,
                'can_delete': False,
            }
        )

        # Compras maneja proveedores y productos
        for module in [proveedores_module, productos_module]:
            RoleModulePermission.objects.get_or_create(
                role=compras_role,
                module=module,
                defaults={
                    'can_view': True,
                    'can_add': True,
                    'can_change': True,
                    'can_delete': False,
                }
            )

        # ============================================================
        # 4️⃣ Crear usuarios y perfiles
        # ============================================================
        usuarios = [
            {"username": "admin", "password": "admin123", "rol": "ADMIN", "grupo": "Administrador"},
            {"username": "bodega", "password": "bodega123", "rol": "BODEGA", "grupo": "Bodega"},
            {"username": "compras", "password": "compras123", "rol": "COMPRAS", "grupo": "Compras"},
        ]
        perfiles = []
        for u in usuarios:
            user, created = User.objects.get_or_create(username=u["username"])
            if created:
                user.set_password(u["password"])
                user.save()
            # Asignar grupo al usuario
            group = Group.objects.get(name=u["grupo"])
            user.groups.add(group)
            perfil, _ = Perfil.objects.get_or_create(usuario=user, rol=u["rol"])
            perfiles.append(perfil)

        # ============================================================
        # 5️⃣ Crear proveedores
        # ============================================================
        proveedores_data = [
            {"nombre": "Ana Torres", "rut": "12345678-9", "contacto": "Ana Torres", "telefono": "987654321", "correo": "ana@proveedor.com", "direccion": "Calle 1", "estado": "ACTIVO"},
            {"nombre": "Carlos Ruiz", "rut": "98765432-1", "contacto": "Carlos Ruiz", "telefono": "912345678", "correo": "carlos@proveedor.com", "direccion": "Calle 2", "estado": "INACTIVO"},
        ]
        proveedores = [Proveedor.objects.get_or_create(**p)[0] for p in proveedores_data]

        # ============================================================
        # 6️⃣ Crear productos
        # ============================================================
        productos_data = [
            {"nombre": "Galleta Choco", "categoria": "GALLETAS", "descripcion": "Galleta con chocolate", "precio": 12.5, "stock_actual": 100, "fecha_vencimiento": None, "lote": "L001", "proveedor": proveedores[0]},
            {"nombre": "Alfajor Dulce", "categoria": "ALFAJORES", "descripcion": "Alfajor relleno", "precio": 15.0, "stock_actual": 50, "fecha_vencimiento": None, "lote": "L002", "proveedor": proveedores[1]},
        ]
        productos = [Producto.objects.get_or_create(**prod)[0] for prod in productos_data]

        # ============================================================
        # 7️⃣ Crear movimientos de inventario
        # ============================================================
        movimientos_data = [
            {"producto": productos[0], "proveedor": proveedores[0], "usuario": User.objects.get(username="admin"), "perfil": perfiles[0], "tipo": "ENTRADA", "cantidad": 20, "observaciones": "Ingreso inicial"},
            {"producto": productos[1], "proveedor": proveedores[1], "usuario": User.objects.get(username="bodega"), "perfil": perfiles[1], "tipo": "SALIDA", "cantidad": 5, "observaciones": "Venta"},
        ]
        for mov in movimientos_data:
            MovimientoInventario.objects.get_or_create(**mov)

        # ============================================================
        # 8️⃣ Final
        # ============================================================
        self.stdout.write(self.style.SUCCESS('✅ ¡Datos de ejemplo y roles cargados exitosamente!'))
