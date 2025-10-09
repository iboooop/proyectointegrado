from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import Perfil
from proveedores.models import Proveedor
from productos.models import Producto
from transacciones.models import MovimientoInventario

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el sistema ERP'

    def handle(self, *args, **kwargs):
        # Usuarios y Perfiles
        usuarios = [
            {"username": "admin", "password": "admin123", "rol": "ADMIN"},
            {"username": "bodega", "password": "bodega123", "rol": "BODEGA"},
            {"username": "compras", "password": "compras123", "rol": "COMPRAS"},
        ]
        perfiles = []
        for u in usuarios:
            user, created = User.objects.get_or_create(username=u["username"])
            if created:
                user.set_password(u["password"])
                user.save()
            perfil, _ = Perfil.objects.get_or_create(usuario=user, rol=u["rol"])
            perfiles.append(perfil)

        # Proveedores
        proveedores_data = [
            {"nombre": "Ana Torres", "rut": "12345678-9", "contacto": "Ana Torres", "telefono": "987654321", "correo": "ana@proveedor.com", "direccion": "Calle 1", "estado": "ACTIVO"},
            {"nombre": "Carlos Ruiz", "rut": "98765432-1", "contacto": "Carlos Ruiz", "telefono": "912345678", "correo": "carlos@proveedor.com", "direccion": "Calle 2", "estado": "INACTIVO"},
        ]
        proveedores = []
        for p in proveedores_data:
            proveedor, _ = Proveedor.objects.get_or_create(**p)
            proveedores.append(proveedor)

        # Productos
        productos_data = [
            {"nombre": "Galleta Choco", "categoria": "GALLETAS", "descripcion": "Galleta con chocolate", "precio": 12.5, "stock_actual": 100, "fecha_vencimiento": None, "lote": "L001", "proveedor": proveedores[0]},
            {"nombre": "Alfajor Dulce", "categoria": "ALFAJORES", "descripcion": "Alfajor relleno", "precio": 15.0, "stock_actual": 50, "fecha_vencimiento": None, "lote": "L002", "proveedor": proveedores[1]},
        ]
        productos = []
        for prod in productos_data:
            producto, _ = Producto.objects.get_or_create(**prod)
            productos.append(producto)

        # Movimientos de Inventario
        movimientos_data = [
            {"producto": productos[0], "proveedor": proveedores[0], "usuario": User.objects.get(username="admin"), "perfil": perfiles[0], "tipo": "ENTRADA", "cantidad": 20, "observaciones": "Ingreso inicial"},
            {"producto": productos[1], "proveedor": proveedores[1], "usuario": User.objects.get(username="bodega"), "perfil": perfiles[1], "tipo": "SALIDA", "cantidad": 5, "observaciones": "Venta"},
        ]
        for mov in movimientos_data:
            MovimientoInventario.objects.get_or_create(**mov)

        self.stdout.write(self.style.SUCCESS('¡Datos de ejemplo cargados exitosamente!'))