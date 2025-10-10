from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Perfil, Module, Role, RoleModulePermission
from proveedores.models import Proveedor
from productos.models import Producto
from transacciones.models import MovimientoInventario

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el sistema ERP con roles, módulos y permisos de Django'

    def handle(self, *args, **kwargs):
        # ============================================================
        # 1️⃣ Crear roles (Grupos) y asociar al modelo Role
        # ============================================================
        roles = ['Administrador', 'Bodega', 'Compras']
        for r in roles:
            grupo, _ = Group.objects.get_or_create(name=r)
            Role.objects.get_or_create(group=grupo)

        admin_group = Group.objects.get(name='Administrador')
        bodega_group = Group.objects.get(name='Bodega')
        compras_group = Group.objects.get(name='Compras')

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
        # 3️⃣ Asignar permisos personalizados (RoleModulePermission)
        # ============================================================

        admin_role = Role.objects.get(group__name='Administrador')
        bodega_role = Role.objects.get(group__name='Bodega')
        compras_role = Role.objects.get(group__name='Compras')

        productos_module = Module.objects.get(code='productos')
        proveedores_module = Module.objects.get(code='proveedores')
        transacciones_module = Module.objects.get(code='transacciones')
        usuarios_module = Module.objects.get(code='usuarios')

        # ------------------------------------------------------------
        # ADMIN: todos los permisos (se fuerza en cada ejecución)
        # ------------------------------------------------------------
        for module in [productos_module, proveedores_module, transacciones_module, usuarios_module]:
            RoleModulePermission.objects.update_or_create(
                role=admin_role,
                module=module,
                defaults={'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': True}
            )

        # ------------------------------------------------------------
        # BODEGA: solo Transacciones (ver y agregar)
        # ------------------------------------------------------------
        RoleModulePermission.objects.update_or_create(
            role=bodega_role,
            module=transacciones_module,
            defaults={'can_view': True, 'can_add': True, 'can_change': False, 'can_delete': False}
        )

        # ------------------------------------------------------------
        # COMPRAS: Productos y Proveedores (ver, agregar y modificar)
        # ------------------------------------------------------------
        for module in [productos_module, proveedores_module]:
            RoleModulePermission.objects.update_or_create(
                role=compras_role,
                module=module,
                defaults={'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': False}
            )


        # Compras maneja proveedores y productos
        for module in [proveedores_module, productos_module]:
            RoleModulePermission.objects.get_or_create(
                role=compras_role,
                module=module,
                defaults={'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': False}
            )

        # ============================================================
        # 4️⃣ Asignar permisos REALES de Django a los grupos
        # ============================================================

        # Mapear module.code a la clase de modelo correspondiente
        def model_for_module(module):
            code = module.code
            if code == 'productos':
                return Producto
            if code == 'proveedores':
                return Proveedor
            if code == 'transacciones':
                return MovimientoInventario
            # por defecto, si hay un módulo de usuarios, asignamos User
            if code == 'usuarios':
                return User
            return None

        # Para cada role (grupo) recogemos sus RoleModulePermission y asignamos
        # únicamente los permisos (add/view/change/delete) que estén marcados.
        for role in [admin_role, bodega_role, compras_role]:
            grupo = role.group
            permisos_a_asignar = []
            rms = RoleModulePermission.objects.filter(role=role)
            for rm in rms:
                model_cls = model_for_module(rm.module)
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

            # Asignar permisos únicos al grupo
            grupo.permissions.set(permisos_a_asignar)

        # ============================================================
        # 5️⃣ Crear usuarios y perfiles
        # ============================================================
        usuarios = [
            {"username": "admin", "password": "admin123", "rol": "ADMIN", "grupo": admin_group},
            {"username": "bodega", "password": "bodega123", "rol": "BODEGA", "grupo": bodega_group},
            {"username": "compras", "password": "compras123", "rol": "COMPRAS", "grupo": compras_group},
        ]
        perfiles = []
        for u in usuarios:
            user, created = User.objects.get_or_create(username=u["username"])
            if created:
                user.set_password(u["password"])
            # Establecer is_staff para los usuarios que deben acceder al admin
            if u["username"] == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                # bodega y compras deben poder entrar al admin para revisar, pero no ser superusers
                user.is_staff = True
                user.is_superuser = False
            user.save()

            # Limpiar permisos directos y asignar el grupo deseado de forma determinista
            user.user_permissions.clear()
            user.groups.set([u["grupo"]])

            # Invalidar caché de permisos en memoria para forzar recálculo
            if hasattr(user, '_perm_cache'):
                del user._perm_cache
            # Asegurar que los cambios se persistan y loguear el resultado para depuración
            user.save()
            self.stdout.write(f"User '{user.username}': is_staff={user.is_staff}, is_superuser={user.is_superuser}, groups={[g.name for g in user.groups.all()]}")

            perfil, _ = Perfil.objects.get_or_create(usuario=user, rol=u["rol"])
            perfiles.append(perfil)

        # ============================================================
        # 6️⃣ Crear proveedores
        # ============================================================
        proveedores_data = [
            {"nombre": "Ana Torres", "rut": "12345678-9", "contacto": "Ana Torres", "telefono": "987654321", "correo": "ana@proveedor.com", "direccion": "Calle 1", "estado": "ACTIVO"},
            {"nombre": "Carlos Ruiz", "rut": "98765432-1", "contacto": "Carlos Ruiz", "telefono": "912345678", "correo": "carlos@proveedor.com", "direccion": "Calle 2", "estado": "INACTIVO"},
        ]
        proveedores = [Proveedor.objects.get_or_create(**p)[0] for p in proveedores_data]

        # ============================================================
        # 7️⃣ Crear productos
        # ============================================================
        productos_data = [
            {"nombre": "Galleta Choco", "categoria": "GALLETAS", "descripcion": "Galleta con chocolate", "precio": 12.5, "stock_actual": 100, "lote": "L001", "proveedor": proveedores[0]},
            {"nombre": "Alfajor Dulce", "categoria": "ALFAJORES", "descripcion": "Alfajor relleno", "precio": 15.0, "stock_actual": 50, "lote": "L002", "proveedor": proveedores[1]},
        ]
        productos = [Producto.objects.get_or_create(**prod)[0] for prod in productos_data]

        # ============================================================
        # 8️⃣ Crear movimientos de inventario
        # ============================================================
        movimientos_data = [
            {"producto": productos[0], "proveedor": proveedores[0], "usuario": User.objects.get(username="admin"), "perfil": perfiles[0], "tipo": "ENTRADA", "cantidad": 20, "observaciones": "Ingreso inicial"},
            {"producto": productos[1], "proveedor": proveedores[1], "usuario": User.objects.get(username="bodega"), "perfil": perfiles[1], "tipo": "SALIDA", "cantidad": 5, "observaciones": "Venta"},
        ]
        for mov in movimientos_data:
            MovimientoInventario.objects.get_or_create(**mov)

        # ============================================================
        # 9️⃣ Final
        # ============================================================
        self.stdout.write(self.style.SUCCESS('✅ ¡Datos de ejemplo, roles y permisos cargados exitosamente!'))
