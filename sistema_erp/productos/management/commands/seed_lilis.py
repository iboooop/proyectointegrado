from django.core.management.base import BaseCommand
from django.db import transaction, models # <- Añadido models
from django.contrib.auth.models import User
from django.utils import timezone # <- Añadido timezone
from datetime import timedelta # <- Añadido timedelta
import random

from proveedores.models import Proveedor
from productos.models import Producto
from usuarios.models import Perfil
from transacciones.models import Bodega, MovimientoInventario # <- Añadido Bodega y MovimientoInventario

CATEGORIES = ['ALFAJORES', 'CONFITERIA', 'CHOCOLATES', 'GALLETAS', 'REGALOS CORPORATIVOS']
ROLES = ['ADMIN', 'BODEGA', 'VENTAS', 'COMPRAS', 'EDITOR', 'LECTOR']
CIUDADES = ['Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Antofagasta']
PLAZOS_PAGO = ['Contado', '30 días', '60 días', '90 días']

class Command(BaseCommand):
    help = "Seed completa para Lilis: añade bodegas y movimientos al seed existente."

    def add_arguments(self, parser):
        # Argumentos existentes
        parser.add_argument('--force', action='store_true', help='Borra datos existentes antes de crear nuevos.')
        parser.add_argument('--usuarios', type=int, default=100)
        parser.add_argument('--proveedores', type=int, default=7014) # Ajustado para un seed más rápido
        parser.add_argument('--productos', type=int, default=10000) # Ajustado para un seed más rápido
        
        # Nuevos argumentos
        parser.add_argument('--bodegas', type=int, default=10)
        parser.add_argument('--movimientos', type=int, default=7000)

    @transaction.atomic
    def handle(self, *args, **options):
        force = options["force"]
        self.stdout.write(self.style.NOTICE("Iniciando seed para Lilis..."))

        # Funciones de seed existentes
        self._seed_usuarios_especiales()
        self._seed_usuarios(options["usuarios"], force)
        self._seed_proveedores(options["proveedores"], force)
        self._seed_productos(options["productos"], force)

        # ---- NUEVAS FUNCIONES AÑADIDAS ----
        self._seed_bodegas(options["bodegas"], force)
        self._seed_movimientos(options["movimientos"], force)
        self._update_product_stock()
        # ------------------------------------

        self.stdout.write(self.style.SUCCESS("Seed finalizada correctamente."))

    # ==============================
    # TUS FUNCIONES DE SEED EXISTENTES (SIN CAMBIOS)
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

    # ==============================
    # NUEVAS FUNCIONES AÑADIDAS
    # ==============================
    def _seed_bodegas(self, cantidad, force):
        if Bodega.objects.count() >= cantidad and not force:
            self.stdout.write(f"Bodegas existentes ({Bodega.objects.count()}) >= {cantidad}. Omitiendo.")
            return
        if force: Bodega.objects.all().delete()

        nombres_bodegas = [f"Bodega {n}" for n in ['Central', 'Despacho', 'Recepción', 'Producción', 'Insumos', 'Norte', 'Sur', 'Este', 'Oeste', 'Devoluciones']]
        lista = []
        for i in range(min(cantidad, len(nombres_bodegas))):
            lista.append(Bodega(
                codigo=f"BOD-{i+1:03d}",
                nombre=nombres_bodegas[i],
                direccion=f"Av. Siempre Viva {random.randint(100, 999)}, {random.choice(CIUDADES)}",
                capacidad_maxima=random.randint(1000, 10000),
                estado='ACTIVO'
            ))
        Bodega.objects.bulk_create(lista)
        self.stdout.write(f"✔ {len(lista)} bodegas creadas.")

    def _seed_movimientos(self, cantidad, force):
        if MovimientoInventario.objects.count() >= cantidad and not force:
            self.stdout.write(f"Movimientos existentes ({MovimientoInventario.objects.count()}) >= {cantidad}. Omitiendo.")
            return
        if force: MovimientoInventario.objects.all().delete()

        productos = list(Producto.objects.all())
        bodegas = list(Bodega.objects.all())
        usuarios = list(User.objects.all())

        if not productos or not bodegas:
            self.stdout.write(self.style.ERROR("Se necesitan productos y bodegas para crear movimientos."))
            return

        tipos_movimiento = [choice[0] for choice in MovimientoInventario.TIPO_MOVIMIENTO]
        movimientos = []
        for _ in range(cantidad):
            producto = random.choice(productos)
            tipo = random.choice(tipos_movimiento)
            
            bodega_origen = None
            bodega_destino = None

            if tipo == 'INGRESO':
                bodega_destino = random.choice(bodegas)
            elif tipo in ['SALIDA', 'VENTA', 'AJUSTE']:
                bodega_origen = random.choice(bodegas)
            elif tipo == 'TRANSFERENCIA':
                if len(bodegas) > 1:
                    bodega_origen, bodega_destino = random.sample(bodegas, 2)
                else:
                    continue
            elif tipo == 'DEVOLUCION':
                bodega_destino = random.choice(bodegas)

            # --- LÓGICA AÑADIDA ---
            fecha_movimiento = timezone.now() - timedelta(days=random.randint(0, 365))
            fecha_venc = None
            if producto.perishable:
                # Si es perecedero, calcula una fecha de vencimiento futura
                fecha_venc = fecha_movimiento.date() + timedelta(days=random.randint(30, 365))
            
            lote_gen = f"L{random.randint(1000, 9999)}"
            serie_gen = f"S{random.randint(100000, 999999)}"
            # --- FIN LÓGICA AÑADIDA ---

            movimientos.append(MovimientoInventario(
                producto=producto,
                proveedor=producto.proveedor,
                bodega_origen=bodega_origen,
                bodega_destino=bodega_destino,
                usuario=random.choice(usuarios) if usuarios else None,
                tipo=tipo,
                cantidad=random.randint(1, 50),
                fecha=fecha_movimiento,
                estado='POR_CONFIRMAR',
                perecible=producto.perishable,
                lote=lote_gen, # <- DATO AÑADIDO
                serie=serie_gen, # <- DATO AÑADIDO
                fecha_vencimiento=fecha_venc, # <- DATO AÑADIDO
                motivo=f"Movimiento automático de seed."
            ))
        MovimientoInventario.objects.bulk_create(movimientos)
        self.stdout.write(f"✔ {len(movimientos)} movimientos de inventario creados.")

    def _update_product_stock(self):
        self.stdout.write("Calculando y actualizando stock de productos...")
        productos_a_actualizar = []
        for producto in Producto.objects.all():
            # Suma todas las cantidades que entran al inventario
            entradas = MovimientoInventario.objects.filter(
                producto=producto, tipo__in=['INGRESO', 'DEVOLUCION']
            ).aggregate(total=models.Sum('cantidad'))['total'] or 0
            
            # Suma todas las cantidades que salen del inventario
            salidas = MovimientoInventario.objects.filter(
                producto=producto, tipo__in=['SALIDA', 'VENTA']
            ).aggregate(total=models.Sum('cantidad'))['total'] or 0
            
            # Las transferencias y ajustes pueden sumar o restar, pero para un cálculo simple de stock total, no se consideran
            # ya que el producto no sale del sistema, solo cambia de bodega.
            
            producto.stock = entradas - salidas
            productos_a_actualizar.append(producto)

        Producto.objects.bulk_update(productos_a_actualizar, ['stock'])
        self.stdout.write(f"✔ Stock actualizado para {len(productos_a_actualizar)} productos.")