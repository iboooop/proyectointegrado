from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Perfil, Module, Role, RoleModulePermission
from proveedores.models import Proveedor
from productos.models import Producto
from transacciones.models import MovimientoInventario
from bodegas.models import Bodega
from clientes.models import Cliente
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el sistema ERP con roles, módulos y permisos de Django'

    def handle(self, *args, **kwargs):
        # ============================================================
        # 1️⃣ Crear roles (Grupos) y asociar al modelo Role
        # ============================================================
        roles = ['Administrador', 'Bodega', 'Compras', 'Ventas']  # ← Agregado Ventas
        for r in roles:
            grupo, _ = Group.objects.get_or_create(name=r)
            Role.objects.get_or_create(group=grupo)

        admin_group = Group.objects.get(name='Administrador')
        bodega_group = Group.objects.get(name='Bodega')
        compras_group = Group.objects.get(name='Compras')
        ventas_group = Group.objects.get(name='Ventas')  # ← NUEVO

        # ============================================================
        # 2️⃣ Crear módulos del ERP
        # ============================================================
        modulos = [
            ('productos', 'Productos'),
            ('proveedores', 'Proveedores'),
            ('transacciones', 'Transacciones'),
            ('usuarios', 'Usuarios'),
            ('bodegas', 'Bodegas'),
            ('clientes', 'Clientes'),
        ]
        for code, name in modulos:
            Module.objects.get_or_create(code=code, name=name)

        # ============================================================
        # 3️⃣ Asignar permisos personalizados (RoleModulePermission)
        # ============================================================

        admin_role = Role.objects.get(group__name='Administrador')
        bodega_role = Role.objects.get(group__name='Bodega')
        compras_role = Role.objects.get(group__name='Compras')
        ventas_role = Role.objects.get(group__name='Ventas')  # ← NUEVO

        productos_module = Module.objects.get(code='productos')
        proveedores_module = Module.objects.get(code='proveedores')
        transacciones_module = Module.objects.get(code='transacciones')
        usuarios_module = Module.objects.get(code='usuarios')
        bodegas_module = Module.objects.get(code='bodegas')  # ← NUEVO
        clientes_module = Module.objects.get(code='clientes')  # ← NUEVO

        # ------------------------------------------------------------
        # ADMIN: todos los permisos (se fuerza en cada ejecución)
        # ------------------------------------------------------------
        for module in [productos_module, proveedores_module, transacciones_module, 
                      usuarios_module, bodegas_module, clientes_module]:  # ← Agregados módulos nuevos
            RoleModulePermission.objects.update_or_create(
                role=admin_role,
                module=module,
                defaults={'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': True}
            )

        # ------------------------------------------------------------
        # BODEGA: Transacciones y Bodegas (ver, agregar y modificar)
        # ------------------------------------------------------------
        for module in [transacciones_module, bodegas_module]:
            RoleModulePermission.objects.update_or_create(
                role=bodega_role,
                module=module,
                defaults={'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': False}
            )

        # ------------------------------------------------------------
        # COMPRAS: Productos, Proveedores y Bodegas (ver, agregar y modificar)
        # ------------------------------------------------------------
        for module in [productos_module, proveedores_module, bodegas_module]:
            RoleModulePermission.objects.update_or_create(
                role=compras_role,
                module=module,
                defaults={'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': False}
            )

        # ------------------------------------------------------------
        # VENTAS: Clientes, Productos y Transacciones (ver, agregar y modificar)
        # ------------------------------------------------------------
        for module in [clientes_module, productos_module, transacciones_module]:
            RoleModulePermission.objects.update_or_create(
                role=ventas_role,
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
            if code == 'usuarios':
                return User
            if code == 'bodegas':
                return Bodega
            if code == 'clientes':
                return Cliente
            return None

        # Para cada role (grupo) recogemos sus RoleModulePermission y asignamos
        # únicamente los permisos (add/view/change/delete) que estén marcados.
        for role in [admin_role, bodega_role, compras_role, ventas_role]:
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
            {"username": "ventas", "password": "ventas123", "rol": "VENTAS", "grupo": ventas_group},  # ← NUEVO
        ]
        perfiles = []
        for u in usuarios:
            user, created = User.objects.get_or_create(username=u["username"])
            if created:
                user.set_password(u["password"])
            
            if u["username"] == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = True
                user.is_superuser = False
            user.save()

            user.user_permissions.clear()
            user.groups.set([u["grupo"]])

            if hasattr(user, '_perm_cache'):
                del user._perm_cache
            user.save()
            
            self.stdout.write(f"User '{user.username}': is_staff={user.is_staff}, is_superuser={user.is_superuser}, groups={[g.name for g in user.groups.all()]}")

            perfil, _ = Perfil.objects.get_or_create(usuario=user, rol=u["rol"])
            perfiles.append(perfil)

        # ============================================================
        # 6️⃣ Crear bodegas 🏭
        # ============================================================
        self.stdout.write(self.style.SUCCESS('📦 Creando bodegas...'))
        
        bodegas_data = [
            {
                "codigo": "BOD-001",
                "nombre": "Bodega Central Santiago",
                "direccion": "Av. Libertador Bernardo O'Higgins 1234, Santiago",
                "telefono": "+56 2 2345 6789",
                "responsable": "María González",
                "capacidad_maxima": 10000,
                "tipo": "PRINCIPAL",
                "estado": "ACTIVO"
            },
            {
                "codigo": "BOD-002",
                "nombre": "Bodega Maipú",
                "direccion": "Camino a Melipilla 5678, Maipú",
                "telefono": "+56 2 2987 6543",
                "responsable": "Pedro Sánchez",
                "capacidad_maxima": 5000,
                "tipo": "SECUNDARIA",
                "estado": "ACTIVO"
            },
            {
                "codigo": "BOD-003",
                "nombre": "Bodega Puente Alto",
                "direccion": "Av. Concha y Toro 9012, Puente Alto",
                "telefono": "+56 2 2456 7890",
                "responsable": "Carmen Silva",
                "capacidad_maxima": 3000,
                "tipo": "SECUNDARIA",
                "estado": "ACTIVO"
            },
            {
                "codigo": "BOD-004",
                "nombre": "Bodega Tránsito Aeropuerto",
                "direccion": "Av. Armando Cortínez 3000, Pudahuel",
                "telefono": "+56 2 2678 9012",
                "responsable": "Luis Martínez",
                "capacidad_maxima": 1500,
                "tipo": "TRANSITO",
                "estado": "ACTIVO"
            },
            {
                "codigo": "BOD-005",
                "nombre": "Bodega La Florida (Mantenimiento)",
                "direccion": "Av. Vicuña Mackenna 7890, La Florida",
                "telefono": "+56 2 2345 1234",
                "responsable": "Jorge Rojas",
                "capacidad_maxima": 2000,
                "tipo": "SECUNDARIA",
                "estado": "MANTENIMIENTO"
            },
        ]
        
        bodegas = []
        for bodega_data in bodegas_data:
            bodega, created = Bodega.objects.get_or_create(
                codigo=bodega_data["codigo"],
                defaults=bodega_data
            )
            bodegas.append(bodega)
            if created:
                self.stdout.write(f"  ✅ Bodega creada: {bodega.nombre}")
            else:
                self.stdout.write(f"  ⚠️  Bodega ya existe: {bodega.nombre}")

        # ============================================================
        # 7️⃣ Crear clientes 👥
        # ============================================================
        self.stdout.write(self.style.SUCCESS('👥 Creando clientes...'))

        clientes_data = [
            {
                "rut": "12345678-9",
                "nombre": "Juan Pérez López",
                "direccion": "Calle Los Aromos 123, Providencia",
                "telefono": "+56 9 8765 4321",
                "email": "juan.perez@email.com",
                "estadoCondicion": "activo",  # ← Cambiar a minúscula según tu modelo
            },
            {
                "rut": "98765432-1",
                "nombre": "SuperMercado MegaCompras S.A.",
                "direccion": "Av. Apoquindo 4500, Las Condes",
                "telefono": "+56 2 2234 5678",
                "email": "compras@megacompras.cl",
                "estadoCondicion": "activo",
            },
            {
                "rut": "11223344-5",
                "nombre": "María García Torres",
                "direccion": "Pasaje San José 456, Ñuñoa",
                "telefono": "+56 9 1234 5678",
                "email": "maria.garcia@email.com",
                "estadoCondicion": "activo",
            },
            {
                "rut": "55667788-9",
                "nombre": "Minimarket Don José Ltda.",
                "direccion": "Av. Grecia 2345, Peñalolén",
                "telefono": "+56 2 2345 6789",
                "email": "ventas@minimarketdonjose.cl",
                "estadoCondicion": "activo",
            },
            {
                "rut": "33445566-7",
                "nombre": "Roberto Muñoz Díaz",
                "direccion": "Calle Los Olivos 789, Maipú",
                "telefono": "+56 9 9876 5432",
                "email": "roberto.munoz@email.com",
                "estadoCondicion": "suspendido",  # ← Cambiar a minúscula
            },
            {
                "rut": "77889900-1",
                "nombre": "Distribuidora Nacional SpA",
                "direccion": "Camino a Lonquén 1500, San Bernardo",
                "telefono": "+56 2 2987 6543",
                "email": "contacto@distribuidoranacional.cl",
                "estadoCondicion": "activo",
            },
        ]

        clientes = []
        for cliente_data in clientes_data:
            cliente, created = Cliente.objects.get_or_create(
                rut=cliente_data["rut"],
                defaults=cliente_data
            )
            clientes.append(cliente)
            if created:
                self.stdout.write(f"  ✅ Cliente creado: {cliente.nombre}")
            else:
                self.stdout.write(f"  ⚠️  Cliente ya existe: {cliente.nombre}")

        # ============================================================
        # 8️⃣ Crear proveedores
        # ============================================================
        self.stdout.write(self.style.SUCCESS('🏭 Creando proveedores...'))
        
        proveedores_data = [
            {"nombre": "Ana Torres", "rut": "12345678-9", "contacto": "Ana Torres", "telefono": "987654321", "correo": "ana@proveedor.com", "direccion": "Calle 1", "estado": "ACTIVO"},
            {"nombre": "Carlos Ruiz", "rut": "98765432-1", "contacto": "Carlos Ruiz", "telefono": "912345678", "correo": "carlos@proveedor.com", "direccion": "Calle 2", "estado": "INACTIVO"},
        ]
        proveedores = [Proveedor.objects.get_or_create(**p)[0] for p in proveedores_data]

        # ============================================================
        # 9️⃣ Crear productos (ahora con bodega asignada)
        # ============================================================
        self.stdout.write(self.style.SUCCESS('📦 Creando productos...'))
        
        productos_data = [
            {
                "nombre": "Galleta Choco", 
                "categoria": "GALLETAS", 
                "descripcion": "Galleta con chocolate", 
                "precio": 1250, 
                "stock_actual": 500, 
                "lote": "L001", 
                "proveedor": proveedores[0],
                "bodega": bodegas[0]  # ← Bodega Central
            },
            {
                "nombre": "Alfajor Dulce", 
                "categoria": "ALFAJORES", 
                "descripcion": "Alfajor relleno", 
                "precio": 1500, 
                "stock_actual": 300, 
                "lote": "L002", 
                "proveedor": proveedores[1],
                "bodega": bodegas[1]  # ← Bodega Maipú
            },
            {
                "nombre": "Chocolate Amargo", 
                "categoria": "CHOCOLATES", 
                "descripcion": "Chocolate 70% cacao", 
                "precio": 2500, 
                "stock_actual": 150, 
                "lote": "L003", 
                "proveedor": proveedores[0],
                "bodega": bodegas[0]  # ← Bodega Central
            },
            {
                "nombre": "Caramelos Masticables", 
                "categoria": "CONFITERIA", 
                "descripcion": "Caramelos surtidos", 
                "precio": 800, 
                "stock_actual": 1000, 
                "lote": "L004", 
                "proveedor": proveedores[0],
                "bodega": bodegas[2]  # ← Bodega Puente Alto
            },
        ]
        productos = [Producto.objects.get_or_create(nombre=prod["nombre"], defaults=prod)[0] for prod in productos_data]

        # ============================================================
        # 🔟 Crear movimientos de inventario (con bodegas y clientes)
        # ============================================================
        self.stdout.write(self.style.SUCCESS('📊 Creando movimientos de inventario...'))
        
        movimientos_data = [
            {
                "producto": productos[0], 
                "proveedor": proveedores[0], 
                "bodega_destino": bodegas[0],
                "usuario": User.objects.get(username="admin"), 
                "perfil": perfiles[0], 
                "tipo": "ENTRADA", 
                "cantidad": 500, 
                "observaciones": "Ingreso inicial a Bodega Central"
            },
            {
                "producto": productos[1], 
                "cliente": clientes[0],
                "bodega_origen": bodegas[1],
                "usuario": User.objects.get(username="ventas"), 
                "perfil": perfiles[3], 
                "tipo": "VENTA", 
                "cantidad": 50, 
                "observaciones": f"Venta a {clientes[0].nombre}"
            },
            {
                "producto": productos[2], 
                "proveedor": proveedores[0], 
                "bodega_destino": bodegas[0],
                "usuario": User.objects.get(username="compras"), 
                "perfil": perfiles[2], 
                "tipo": "ENTRADA", 
                "cantidad": 150, 
                "observaciones": "Compra de chocolates"
            },
            {
                "producto": productos[0], 
                "bodega_origen": bodegas[0],
                "bodega_destino": bodegas[2],
                "usuario": User.objects.get(username="bodega"), 
                "perfil": perfiles[1], 
                "tipo": "TRANSFERENCIA", 
                "cantidad": 100, 
                "observaciones": "Transferencia de Bodega Central a Puente Alto"
            },
            {
                "producto": productos[3], 
                "cliente": clientes[1],
                "bodega_origen": bodegas[2],
                "usuario": User.objects.get(username="ventas"), 
                "perfil": perfiles[3], 
                "tipo": "VENTA", 
                "cantidad": 200, 
                "observaciones": f"Venta mayorista a {clientes[1].razon_social if hasattr(clientes[1], 'razon_social') else clientes[1].nombre}"
            },
        ]
        
        for mov in movimientos_data:
            MovimientoInventario.objects.get_or_create(
                producto=mov["producto"],
                tipo=mov["tipo"],
                cantidad=mov["cantidad"],
                defaults=mov
            )

        # ============================================================
        # 1️⃣1️⃣ Final
        # ============================================================
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ ¡Datos de ejemplo cargados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f"📊 Resumen:")
        self.stdout.write(f"   - Usuarios: {len(usuarios)}")
        self.stdout.write(f"   - Bodegas: {len(bodegas)}")
        self.stdout.write(f"   - Clientes: {len(clientes)}")
        self.stdout.write(f"   - Proveedores: {len(proveedores)}")
        self.stdout.write(f"   - Productos: {len(productos)}")
        self.stdout.write(f"   - Movimientos: {len(movimientos_data)}")
        self.stdout.write(self.style.SUCCESS('=' * 70))