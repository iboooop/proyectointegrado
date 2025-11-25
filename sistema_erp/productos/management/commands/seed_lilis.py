from django.core.management.base import BaseCommand
from django.db import transaction, models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from proveedores.models import Proveedor
from productos.models import Producto
from usuarios.models import Perfil
from transacciones.models import Bodega, MovimientoInventario

CATEGORIES = ['ALFAJORES', 'CONFITERIA', 'CHOCOLATES', 'GALLETAS', 'REGALOS CORPORATIVOS']
ROLES = ['ADMIN', 'BODEGA', 'VENTAS', 'COMPRAS', 'EDITOR', 'LECTOR']
CIUDADES = ['Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Antofagasta']
PLAZOS_PAGO = ['Contado', '30 días', '60 días', '90 días']


class Command(BaseCommand):
    help = "Seed de Lilis reducida: solo 5 de cada modelo."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Borra datos existentes antes de generar.')

    @transaction.atomic
    def handle(self, *args, **options):
        force = options["force"]
        self.stdout.write(self.style.NOTICE("Iniciando seed reducida (solo 5 registros)..."))

        # usuarios especiales
        self._seed_usuarios_especiales()

        # modelos con SOLO 5 registros
        self._seed_usuarios(5, force)
        self._seed_proveedores(5, force)
        self._seed_productos(5, force)
        self._seed_bodegas(5, force)
        self._seed_movimientos(5, force)

        # actualizar stock de productos
        self._update_product_stock()

        self.stdout.write(self.style.SUCCESS("✔ Seed reducida generada correctamente."))

    # ==============================
    # USUARIOS ESPECIALES
    # ==============================
    def _seed_usuarios_especiales(self):
        # Admin
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

        # Lector
        lector, created = User.objects.get_or_create(
            username="lector_lilis",
            defaults={"email": "lector@lilis.cl"}
        )
        if created:
            lector.set_password("lector123")
            lector.save()
            Perfil.objects.create(usuario=lector, rol="LECTOR", telefono="+56 9 22222222", estado="ACTIVO")
            self.stdout.write("✔ Usuario LECTOR creado")

        # Editor
        editor, created = User.objects.get_or_create(
            username="editor_lilis",
            defaults={"email": "editor@lilis.cl"}
        )
        if created:
            editor.set_password("editor123")
            editor.save()
            Perfil.objects.create(usuario=editor, rol="EDITOR", telefono="+56 9 33333333", estado="ACTIVO")
            self.stdout.write("✔ Usuario EDITOR creado")

    # ==============================
    # USUARIOS NORMALES (solo 5)
    # ==============================
    def _seed_usuarios(self, cantidad, force):
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
        users = list(User.objects.filter(username__startswith='lilis_user_'))

        for u in users:
            perfiles.append(Perfil(usuario=u, rol=random.choice(ROLES), telefono=f"+56 9 {random.randint(20000000,99999999)}", estado="ACTIVO"))

        Perfil.objects.bulk_create(perfiles)

        self.stdout.write(f"✔ {len(users)} usuarios creados.")

    # ==============================
    # PROVEEDORES (solo 5)
    # ==============================
    def _seed_proveedores(self, cantidad, force):
        if force:
            Proveedor.objects.all().delete()

        lista = []
        for i in range(1, cantidad + 1):
            ciudad = random.choice(CIUDADES)
            lista.append(
                Proveedor(
                    nombre=f"Proveedor {i}",
                    rut=f"76.{i:03d}.{random.randint(100,999)}-{random.randint(0,9)}",
                    contacto=f"Contacto {i}",
                    telefono=f"+56 9 {random.randint(20000000,99999999)}",
                    correo=f"proveedor{i}@lilis.cl",
                    direccion=f"Calle Dulce {i}, {ciudad}",
                    razon_social=f"Proveedor S.A. {i}",
                    nombre_fantasia=f"ProveMax {i}",
                    ciudad=ciudad,
                    pais='Chile',
                    plazo_pago=random.choice(PLAZOS_PAGO),
                    descuento=random.uniform(0, 20),
                    proveedor_preferente=random.choice([True, False]),
                    lead_time=random.randint(1, 30),
                    estado="ACTIVO",
                )
            )

        Proveedor.objects.bulk_create(lista)
        self.stdout.write("✔ 5 proveedores creados.")

    # ==============================
    # PRODUCTOS (solo 5)
    # ==============================
    def _seed_productos(self, cantidad, force):
        if force:
            Producto.objects.all().delete()

        proveedores = list(Proveedor.objects.all())

        productos = []

        for i in range(1, cantidad + 1):
            categoria = random.choice(CATEGORIES)
            productos.append(
                Producto(
                    sku=f"SKU{i:05d}",
                    ean_upc=str(random.randint(10**12, 10**13 - 1)),
                    nombre=f"Producto {i}",
                    descripcion="Descripción generada por seed.",
                    categoria=categoria,
                    marca="Lilis",
                    modelo="Standard",
                    uom_compra="UN",
                    uom_venta="UN",
                    factor_conversion=1.0,
                    costo_estandar=1000,
                    precio_venta=2000,
                    impuesto_iva=19.0,
                    stock_minimo=0,
                    stock_maximo=100,
                    punto_reorden=10,
                    perishable=False,
                    control_por_lote=True,
                    activo=True,
                    proveedor=random.choice(proveedores) if proveedores else None,
                )
            )

        Producto.objects.bulk_create(productos)
        self.stdout.write("✔ 5 productos creados.")

    # ==============================
    # BODEGAS (solo 5)
    # ==============================
    def _seed_bodegas(self, cantidad, force):
        if force:
            Bodega.objects.all().delete()

        lista = []
        for i in range(1, cantidad + 1):
            lista.append(
                Bodega(
                    codigo=f"BOD-{i:03d}",
                    nombre=f"Bodega {i}",
                    direccion=f"Dirección {i}",
                    capacidad_maxima=5000,
                    estado="ACTIVO"
                )
            )

        Bodega.objects.bulk_create(lista)
        self.stdout.write("✔ 5 bodegas creadas.")

    # ==============================
    # MOVIMIENTOS (solo 5)
    # ==============================
    def _seed_movimientos(self, cantidad, force):
        if force:
            MovimientoInventario.objects.all().delete()

        productos = list(Producto.objects.all())
        bodegas = list(Bodega.objects.all())
        usuarios = list(User.objects.all())

        tipos = [t[0] for t in MovimientoInventario.TIPO_MOVIMIENTO]

        movimientos = []

        for _ in range(cantidad):
            producto = random.choice(productos)
            tipo = random.choice(tipos)

            movimientos.append(
                MovimientoInventario(
                    producto=producto,
                    proveedor=producto.proveedor,
                    bodega_origen=random.choice(bodegas),
                    bodega_destino=random.choice(bodegas),
                    usuario=random.choice(usuarios),
                    tipo=tipo,
                    cantidad=random.randint(1, 10),
                    fecha=timezone.now(),
                    estado='POR_CONFIRMAR',
                    motivo="Seed reducida",
                    lote=f"L{random.randint(1000,9999)}",
                    serie=f"S{random.randint(100000,999999)}",
                )
            )

        MovimientoInventario.objects.bulk_create(movimientos)
        self.stdout.write("✔ 5 movimientos creados.")

    # ==============================
    # ACTUALIZAR STOCK
    # ==============================
    def _update_product_stock(self):
        productos = Producto.objects.all()
        for p in productos:
            entradas = MovimientoInventario.objects.filter(producto=p, tipo__in=['INGRESO','AJUSTE']).count()
            salidas = MovimientoInventario.objects.filter(producto=p, tipo__in=['SALIDA','VENTA']).count()
            p.stock_actual = entradas - salidas
            p.save()

        self.stdout.write("✔ Stock actualizado.")
