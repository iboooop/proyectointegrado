from django.shortcuts import render
from productos.models import Producto
from proveedores.models import Proveedor
from transacciones.models import MovimientoInventario
from usuarios.models import Perfil
from bodegas.models import Bodega  # ← NUEVO
from clientes.models import Cliente  # ← NUEVO
from django.contrib.auth.models import User  # ← AGREGADO para contar usuarios correctamente

def dashboard(request):
    # Contadores para las tarjetas superiores
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_transacciones = MovimientoInventario.objects.count()
    total_usuarios = User.objects.count()
    total_bodegas = Bodega.objects.filter(estado='ACTIVO').count()
    total_clientes = Cliente.objects.filter(estadoCondicion='activo').count()

    # Últimos registros para las tarjetas inferiores
    # Usar '-pk' para evitar errores cuando la PK no se llame 'id'
    ultimos_productos = Producto.objects.all().order_by('-pk')[:5]
    ultimas_transacciones = MovimientoInventario.objects.all().order_by('-fecha')[:5]
    ultimos_clientes = Cliente.objects.all().order_by('-pk')[:5]

    # Bodegas para el panel inferior (hasta 8)
    bodegas = Bodega.objects.all()[:8]

    context = {
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'total_transacciones': total_transacciones,
        'total_usuarios': total_usuarios,
        'total_bodegas': total_bodegas,
        'total_clientes': total_clientes,
        'ultimos_productos': ultimos_productos,
        'ultimas_transacciones': ultimas_transacciones,
        'ultimos_clientes': ultimos_clientes,
        'bodegas': bodegas,
    }

    return render(request, 'dashboard.html', context)