from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
import random

from proveedores.models import Proveedor
from productos.models import Producto
from usuarios.models import Perfil

CATEGORIES = ['ALFAJORES', 'CONFITERIA', 'CHOCOLATES', 'GALLETAS', 'REGALOS CORPORATIVOS']
ROLES = ['ADMIN', 'BODEGA', 'VENTAS', 'COMPRAS', 'EDITOR', 'LECTOR']
CIUDADES = ['Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Antofagasta']
PLAZOS_PAGO = ['Contado', '30 días', '60 días', '90 días']

class Command(BaseCommand):
    help = "Seed mínima para Lilis: usuarios, perfiles, productos y proveedores."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Ignora conteos existentes.')
        parser.add_argument('--usuarios', type=int, default=100)
        parser.add_argument('--proveedores', type=int, default=7456)
        parser.add_argument('--productos', type=int, default=8645)

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
            razon_social = f"Proveedor S.A. {i:03d}"
            nombre_fantasia = f"ProveMax {i:03d}"
            ciudad = random.choice(CIUDADES)
            plazo_pago = random.choice(PLAZOS_PAGO)  # Selecciona aleatoriamente el plazo de pago
            descuento = round(random.uniform(0, 20), 2)  # Descuento entre 0% y 20%
            proveedor_preferente = random.choice([True, False])  # Algunos preferentes, otros no
            lead_time = random.randint(1, 30)  # Lead time entre 1 y 30 días

            lista.append(
                Proveedor(
                    nombre=f"Lilis Proveedor {i:03d}",
                    rut=f"76.{i:03d}.{random.randint(100,999)}-{random.randint(0,9)}",
                    contacto=f"Contacto {i:03d}",
                    telefono=f"+56 9 {random.randint(20000000,99999999)}",
                    correo=f"proveedor{i:03d}@lilis.cl",
                    direccion=f"Calle Dulce {i:03d}, {ciudad}",
                    razon_social=razon_social,
                    nombre_fantasia=nombre_fantasia,
                    ciudad=ciudad,
                    pais='Chile', # Añadido el campo país
                    plazo_pago=plazo_pago,
                    descuento=descuento,
                    proveedor_preferente=proveedor_preferente,
                    lead_time=lead_time,
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

        unidades = ['UN', 'CAJA', 'KG', 'GR', 'LT', 'PAQ']  # Opciones válidas según el modelo
        marcas = ['Lilis', 'DulceArte', 'ManosDulces', 'CasaChoco', 'MarcaEjemplo']
        modelos = ['Estándar', 'Premium', 'Eco', 'Clásico', 'Edición Limitada']

        proveedores_list = list(Proveedor.objects.all()) if Proveedor.objects.exists() else []

        for i in range(1, cantidad + 1):
            categoria = random.choice(['ALFAJORES', 'CONFITERIA', 'CHOCOLATES', 'GALLETAS', 'REGALOS CORPORATIVOS'])
            nombre_base = {
                'ALFAJORES': 'Alfajor Artesanal',
                'CONFITERIA': 'Dulce Artesanal',
                'CHOCOLATES': 'Chocolate Fino',
                'GALLETAS': 'Galleta Tradicional',
                'REGALOS CORPORATIVOS': 'Regalo Corporativo'
            }[categoria]

            precio_venta = round(random.uniform(500, 5000), 2)
            costo_estandar = round(precio_venta * random.uniform(0.35, 0.85), 2)

            unidad_compra = random.choice(unidades)
            unidad_venta = random.choice(unidades)

            perecible_default = categoria not in ['REGALOS CORPORATIVOS']
            estado = random.random() < 0.8  # 80% activos

            productos.append(
                Producto(
                    sku=f"SKU{i:05d}",
                    ean_upc=str(random.randint(10**12, 10**13 - 1)),
                    nombre=f"{nombre_base} Lilis {i:03d}",
                    descripcion=f"Producto {nombre_base.lower()} hecho a mano.",
                    categoria=categoria,
                    marca=random.choice(marcas),
                    modelo=random.choice(modelos),
                    uom_compra=unidad_compra,
                    uom_venta=unidad_venta,
                    factor_conversion=1.0,
                    costo_estandar=costo_estandar,
                    precio_venta=precio_venta,
                    impuesto_iva=19.0,
                    stock_minimo=0,
                    stock_maximo=random.randint(50, 300),
                    punto_reorden=random.randint(10, 50),
                    perishable=perecible_default,
                    control_por_lote=True,
                    activo=estado,
                    proveedor=random.choice(proveedores_list) if proveedores_list else None,
                )
            )

        Producto.objects.bulk_create(productos)
        self.stdout.write(f"✔ {len(productos)} productos creados.")