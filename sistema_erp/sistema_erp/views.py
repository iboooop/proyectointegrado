from django.shortcuts import render
from productos.models import Producto
from proveedores.models import Proveedor
from transacciones.models import MovimientoInventario
from usuarios.models import Perfil

def dashboard(request):
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_transacciones = MovimientoInventario.objects.count()
    total_usuarios = MovimientoInventario.objects.count()

    ultimos_productos = Producto.objects.all().order_by('-id')[:5]
    ultimas_transacciones = MovimientoInventario.objects.all().order_by('-fecha')[:5]

    context = {
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'total_transacciones': total_transacciones,
        'total_usuarios': total_usuarios,
        'ultimos_productos': ultimos_productos,
        'ultimas_transacciones': ultimas_transacciones,
    }

    return render(request, 'dashboard.html', context)
