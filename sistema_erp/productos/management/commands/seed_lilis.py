from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
import random

from proveedores.models import Proveedor
from productos.models import Producto
from usuarios.models import Perfil

CATEGORIES = ['ALFAJORES', 'CONFITERIA', 'CHOCOLATES', 'GALLETAS']

ROLES = ['ADMIN', 'BODEGA', 'VENTAS', 'COMPRAS', 'EDITOR', 'LECTOR']


class Command(BaseCommand):
    help = "Seed mínima para Lilis: usuarios, perfiles, productos y proveedores."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Ignora conteos existentes.')
        parser.add_argument('--usuarios', type=int, default=100)
        parser.add_argument('--proveedores', type=int, default=100)
        parser.add_argument('--productos', type=int, default=100)

    def handle(self, *args, **options):
        force = options["force"]
        qty_users = options["usuarios"]
        qty_prov = options["proveedores"]
        qty_prod = options["productos"]

        self.stdout.write(self.style.NOTICE("Iniciando seed mínima para Lilis..."))

        with transaction.atomic():
            self._seed_usuarios_especiales()
            self._seed_usuarios(qty_users, force)
            self._seed_proveedores(qty_prov, force)
            self._seed_productos(qty_prod, force)

        self.stdout.write(self.style.SUCCESS("Seed finalizada correctamente."))

    # ==============================
    # USUARIOS ESPECIALES
    # ==============================
    def _seed_usuarios_especiales(self):

        # ADMIN
        admin, created = User.objects.get_or_create(
            username="admin_lilis",
            defaults={"email": "admin@lilis.cl"}
        )
        if created:
            admin.set_password("admin123")
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            Perfil.objects.create(usuario=admin, rol="ADMIN", telefono="+56 9 11111111", estado="ACTIVO")
            self.stdout.write("✔ Usuario ADMIN creado (admin_lilis / admin123)")

        # LECTOR
        lector, created = User.objects.get_or_create(
            username="lector_lilis",
            defaults={"email": "lector@lilis.cl"}
        )
        if created:
            lector.set_password("lector123")
            lector.save()
            Perfil.objects.create(usuario=lector, rol="LECTOR", telefono="+56 9 22222222", estado="ACTIVO")
            self.stdout.write("✔ Usuario LECTOR creado (lector_lilis / lector123)")

        # EDITOR
        editor, created = User.objects.get_or_create(
            username="editor_lilis",
            defaults={"email": "editor@lilis.cl"}
        )
        if created:
            editor.set_password("editor123")
            editor.save()
            Perfil.objects.create(usuario=editor, rol="EDITOR", telefono="+56 9 33333333", estado="ACTIVO")
            self.stdout.write("✔ Usuario EDITOR creado (editor_lilis / editor123)")

    # ==============================
    # USUARIOS NORMALES
    # ==============================
    def _seed_usuarios(self, cantidad, force):
        existentes = User.objects.filter(username__startswith="lilis_user_").count()

        if existentes >= cantidad and not force:
            self.stdout.write(f"Usuarios existentes ({existentes}) >= {cantidad}. Omitiendo.")
            return

        # borrar usuarios previos si force=True
        if force:
            User.objects.filter(username__startswith="lilis_user_").delete()
            Perfil.objects.exclude(usuario__username__in=["admin_lilis","lector_lilis","editor_lilis"]).delete()

        users = []
        perfiles = []

        for i in range(1, cantidad + 1):
            username = f"lilis_user_{i:03d}"
            email = f"{username}@lilis.cl"

            u = User(username=username, email=email)
            u.set_password("lilis123")
            users.append(u)

        User.objects.bulk_create(users)
        users = list(User.objects.filter(username__startswith="lilis_user_"))

        for u in users:
            perfiles.append(
                Perfil(
                    usuario=u,
                    rol=random.choice(ROLES),
                    telefono=f"+56 9 {random.randint(20000000,99999999)}",
                    estado="ACTIVO"
                )
            )

        Perfil.objects.bulk_create(perfiles)

        self.stdout.write(f"✔ {len(users)} usuarios normales creados.")

    # ==============================
    # PROVEEDORES
    # ==============================
    def _seed_proveedores(self, cantidad, force):
        existentes = Proveedor.objects.count()

        if existentes >= cantidad and not force:
            self.stdout.write(f"Proveedores existentes ({existentes}) >= {cantidad}. Omitiendo.")
            return

        if force:
            Proveedor.objects.all().delete()

        lista = []
        for i in range(1, cantidad + 1):
            lista.append(
                Proveedor(
                    nombre=f"Lilis Proveedor {i:03d}",
                    rut=f"76.{i:03d}.{random.randint(100,999)}-{random.randint(0,9)}",
                    contacto=f"Contacto {i:03d}",
                    telefono=f"+56 9 {random.randint(20000000,99999999)}",
                    correo=f"proveedor{i:03d}@lilis.cl",
                    direccion=f"Calle Dulce {i:03d}, Santiago",
                    estado="ACTIVO",
                )
            )

        Proveedor.objects.bulk_create(lista)
        self.stdout.write(f"✔ {len(lista)} proveedores creados.")

    # ==============================
    # PRODUCTOS
    # ==============================
    def _seed_productos(self, cantidad, force):
        existentes = Producto.objects.count()

        if existentes >= cantidad and not force:
            self.stdout.write(f"Productos existentes ({existentes}) >= {cantidad}. Omitiendo.")
            return

        if force:
            Producto.objects.all().delete()

        productos = []

        for i in range(1, cantidad + 1):
            categoria = random.choice(CATEGORIES)
            nombre_base = {
                'ALFAJORES': 'Alfajor Artesanal',
                'CONFITERIA': 'Dulce Artesanal',
                'CHOCOLATES': 'Chocolate Fino',
                'GALLETAS': 'Galleta Tradicional'
            }[categoria]

            # Campos adaptados a modelos típicos; evitan valores vacíos y duplicados en SKU
            kwargs = {
                "nombre": f"{nombre_base} Lilis {i:03d}",
                "categoria": categoria,
                "descripcion": f"Producto {nombre_base.lower()} hecho a mano.",
                "precio_venta": round(random.uniform(500, 5000), 2),
                "stock_actual": random.randint(0, 300),
                "lote": f"L{i:04d}",
                "proveedor": random.choice(list(Proveedor.objects.all())) if Proveedor.objects.exists() else None,
                "stock": random.choice(['ALTO','BAJO']) if "stock" in [f.name for f in Producto._meta.get_fields()] else None,
                "sku": f"SKU{i:05d}",
                "ean_upc": str(random.randint(10**12, 10**13 - 1)),
            }

            # Limpiar None keys que no existan en el modelo
            model_fields = {f.name for f in Producto._meta.get_fields()}
            clean_kwargs = {k: v for k, v in kwargs.items() if k in model_fields and v is not None}

            productos.append(Producto(**clean_kwargs))

        Producto.objects.bulk_create(productos)
        self.stdout.write(f"✔ {len(productos)} productos creados.")
