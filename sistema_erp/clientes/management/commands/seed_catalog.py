from django.core.management.base import BaseCommand
from django.utils import timezone
from clientes.models import Cliente
from productos.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario
from pedidos.models import Pedido, DetallePedido
from compras.models import OrdenCompra, DetalleOrdenCompra

class Command(BaseCommand):
    help = "Carga datos iniciales para clientes, productos, proveedores, pedidos y órdenes de compra"

    def handle(self, *args, **kwargs):
        # Crear usuarios
        usuario1, _ = Usuario.objects.get_or_create(nombre="Usuario 1", email="usuario1@example.com", telefono="123456789", contrasena="password1")
        usuario2, _ = Usuario.objects.get_or_create(nombre="Usuario 2", email="usuario2@example.com", telefono="987654321", contrasena="password2")

        # Crear clientes
        cliente1, _ = Cliente.objects.get_or_create(nombre="Cliente 1", rut="12345678-9", direccion="Calle Falsa 123", telefono="123456789", email="cliente1@example.com")
        cliente2, _ = Cliente.objects.get_or_create(nombre="Cliente 2", rut="98765432-1", direccion="Avenida Siempre Viva 456", telefono="987654321", email="cliente2@example.com")

        # Crear productos
        producto1, _ = Producto.objects.get_or_create(nombre="Producto 1", categoria="Categoría A", precioBase=100.00)
        producto2, _ = Producto.objects.get_or_create(nombre="Producto 2", categoria="Categoría B", precioBase=200.00)

        # Crear proveedores
        proveedor1, _ = Proveedor.objects.get_or_create(nombre="Proveedor 1", rut="11111111-1", direccion="Calle Comercio 123", telefono="123456789", email="proveedor1@example.com")
        proveedor2, _ = Proveedor.objects.get_or_create(nombre="Proveedor 2", rut="22222222-2", direccion="Avenida Industria 456", telefono="987654321", email="proveedor2@example.com")

        # Crear pedidos relacionados con clientes y productos
        pedido1, _ = Pedido.objects.get_or_create(cliente=cliente1, usuario=usuario1, fecha=timezone.make_aware(timezone.datetime(2025, 9, 25)))
        DetallePedido.objects.get_or_create(pedido=pedido1, producto=producto1, cantidad=2, precioUnitario=100.00)

        pedido2, _ = Pedido.objects.get_or_create(cliente=cliente2, usuario=usuario2, fecha=timezone.make_aware(timezone.datetime(2025, 9, 26)))
        DetallePedido.objects.get_or_create(pedido=pedido2, producto=producto2, cantidad=1, precioUnitario=200.00)

        # Crear órdenes de compra relacionadas con proveedores y productos
        orden_compra1, _ = OrdenCompra.objects.get_or_create(proveedor=proveedor1, usuario=usuario1, fecha=timezone.make_aware(timezone.datetime(2025, 9, 25)), estado="pendiente")
        DetalleOrdenCompra.objects.get_or_create(ordenCompra=orden_compra1, producto=producto1, cantidad=5, precioUnitario=95.00)

        orden_compra2, _ = OrdenCompra.objects.get_or_create(proveedor=proveedor2, usuario=usuario2, fecha=timezone.make_aware(timezone.datetime(2025, 9, 26)), estado="aprobada")
        DetalleOrdenCompra.objects.get_or_create(ordenCompra=orden_compra2, producto=producto2, cantidad=3, precioUnitario=190.00)

        self.stdout.write(self.style.SUCCESS("Datos iniciales cargados correctamente con relaciones"))