from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string

from proveedores.models import Proveedor
from productos.models import Producto
from usuarios.models import Perfil
from transacciones.models import MovimientoInventario, Bodega

CATEGORIES = ['ALFAJORES', 'CONFITERIA', 'CHOCOLATES', 'GALLETAS']
ROLES = ['ADMIN', 'BODEGA', 'VENTAS', 'COMPRAS']
TIPOS_MOV = ['ENTRADA', 'SALIDA', 'AJUSTE']

class Command(BaseCommand):
    help = "Genera datos de ejemplo para la empresa de alimentos Lilis (100 de cada CRUD principal)."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Ignora conteos existentes y agrega igualmente.')
        parser.add_argument('--users', type=int, default=100, help='Cantidad de usuarios a generar.')
        parser.add_argument('--proveedores', type=int, default=100, help='Cantidad de proveedores a generar.')
        parser.add_argument('--productos', type=int, default=100, help='Cantidad de productos a generar.')
        parser.add_argument('--movimientos', type=int, default=100, help='Cantidad de movimientos a generar.')

    def handle(self, *args, **options):
        force = options['force']
        qty_users = options['users']
        qty_prov = options['proveedores']
        qty_prod = options['productos']
        qty_mov = options['movimientos']

        self.stdout.write(self.style.NOTICE('Iniciando seed para Lilis...'))
        with transaction.atomic():
            proveedores = self._seed_proveedores(qty_prov, force)
            usuarios, perfiles = self._seed_usuarios(qty_users, force)
            productos = self._seed_productos(qty_prod, proveedores, force)
            self._ensure_bodega_demo()
            self._seed_movimientos(qty_mov, productos, proveedores, usuarios, perfiles, force)
        self.stdout.write(self.style.SUCCESS('Seed completado.'))

    # ---------- Helpers ----------
    def _seed_proveedores(self, cantidad, force):
        existentes = Proveedor.objects.count()
        if existentes >= cantidad and not force:
            self.stdout.write(f'Proveedores existentes ({existentes}) >= {cantidad}, omitiendo creación.')
            return list(Proveedor.objects.all())
        lista = []
        for i in range(1, cantidad+1):
            rut = f"76.{i:03d}.{random.randint(100,999)}-{random.randint(0,9)}"
            p = Proveedor(
                nombre=f"Lilis Proveedor {i:03d}",
                rut=rut,
                contacto=f"Contacto {i:03d}",
                telefono=f"+56 9 {random.randint(10000000, 99999999)}",
                correo=f"proveedor{i:03d}@lilis.cl",
                direccion=f"Calle Dulce {i:03d}, Santiago",
                estado='ACTIVO'
            )
            lista.append(p)
        Proveedor.objects.bulk_create(lista)
        self.stdout.write(f"Creado {len(lista)} proveedores.")
        return list(Proveedor.objects.all())

    def _seed_usuarios(self, cantidad, force):
        existentes = User.objects.count()
        if existentes >= cantidad and not force:
            self.stdout.write(f'Usuarios existentes ({existentes}) >= {cantidad}, omitiendo creación.')
            users = list(User.objects.all())
            perfiles = list(Perfil.objects.select_related('usuario').all())
            return users, perfiles
        users = []
        perfiles = []
        for i in range(1, cantidad+1):
            username = f"lilis_user_{i:03d}"
            email = f"{username}@lilis.cl"
            u = User(username=username, email=email)
            u.set_password('lilis123')
            users.append(u)
        User.objects.bulk_create(users)
        # Recuperar usuarios con ids asignados
        users = list(User.objects.filter(username__startswith='lilis_user_'))
        for u in users:
            perfiles.append(Perfil(usuario=u, rol=random.choice(ROLES), telefono=f"+56 9 {random.randint(10000000, 99999999)}", estado='ACTIVO'))
        Perfil.objects.bulk_create(perfiles)
        self.stdout.write(f"Creado {len(users)} usuarios y {len(perfiles)} perfiles.")
        return users, perfiles

    def _seed_productos(self, cantidad, proveedores, force):
        existentes = Producto.objects.count()
        if existentes >= cantidad and not force:
            self.stdout.write(f'Productos existentes ({existentes}) >= {cantidad}, omitiendo creación.')
            return list(Producto.objects.all())
        productos = []
        for i in range(1, cantidad+1):
            categoria = random.choice(CATEGORIES)
            nombre_base = {
                'ALFAJORES': 'Alfajor Artesanal',
                'CONFITERIA': 'Dulce Artesanal',
                'CHOCOLATES': 'Chocolate Fino',
                'GALLETAS': 'Galleta Tradicional'
            }[categoria]
            proveedor = random.choice(proveedores)
            p = Producto(
                nombre=f"{nombre_base} Lilis {i:03d}",
                categoria=categoria,
                descripcion=f"Producto {nombre_base.lower()} hecho a mano con ingredientes chilenos. Lote {i:03d}.",
                precio=round(random.uniform(500, 5000), 2),
                stock_actual=random.randint(0, 500),
                lote=f"L{i:04d}",
                proveedor=proveedor,
                stock=random.choice(['ALTO','BAJO'])
            )
            productos.append(p)
        Producto.objects.bulk_create(productos)
        self.stdout.write(f"Creado {len(productos)} productos.")
        return list(Producto.objects.all())

    def _ensure_bodega_demo(self):
        if not Bodega.objects.exists():
            Bodega.objects.create(codigo='PRINCIPAL', nombre='Bodega Principal Lilis')
            self.stdout.write('Creada bodega principal.')

    def _seed_movimientos(self, cantidad, productos, proveedores, usuarios, perfiles, force):
        existentes = MovimientoInventario.objects.count()
        if existentes >= cantidad and not force:
            self.stdout.write(f'Movimientos existentes ({existentes}) >= {cantidad}, omitiendo creación.')
            return
        movimientos = []
        bodega = Bodega.objects.first()
        for i in range(1, cantidad+1):
            producto = random.choice(productos)
            tipo = random.choice(TIPOS_MOV)
            cantidad_mov = random.randint(1, 50)
            usuario = random.choice(usuarios)
            perfil = Perfil.objects.filter(usuario=usuario).first()
            proveedor = random.choice(proveedores) if random.random() < 0.7 else None
            mov = MovimientoInventario(
                producto=producto,
                proveedor=proveedor,
                usuario=usuario,
                perfil=perfil,
                bodega=bodega,
                tipo=tipo,
                cantidad=cantidad_mov,
                fecha=timezone.now(),
                manejo_lotes=False,
                manejo_series=False,
                perecible=False,
                lote=producto.lote,
                observaciones=f"Movimiento {tipo.lower()} generado por seed Lilis #{i}",
            )
            movimientos.append(mov)
        MovimientoInventario.objects.bulk_create(movimientos)
        self.stdout.write(f"Creado {len(movimientos)} movimientos de inventario.")
