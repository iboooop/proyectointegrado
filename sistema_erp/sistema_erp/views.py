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
    total_usuarios = User.objects.count()  # ← CORREGIDO (antes estaba mal, contaba transacciones)
    total_bodegas = Bodega.objects.filter(estado='ACTIVO').count()  # ← NUEVO
    total_clientes = Cliente.objects.filter(estadoCondicion='activo').count()  # ← NUEVO

    # Últimos registros para las tarjetas inferiores
    ultimos_productos = Producto.objects.all().order_by('-id')[:5]
    ultimas_transacciones = MovimientoInventario.objects.all().order_by('-fecha')[:5]
    ultimos_clientes = Cliente.objects.all().order_by('-idCliente')[:5]  # ← NUEVO

    # Bodegas para el panel inferior
    bodegas = Bodega.objects.all()[:8]  # ← NUEVO (máximo 8 bodegas)

    context = {
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'total_transacciones': total_transacciones,
        'total_usuarios': total_usuarios,
        'total_bodegas': total_bodegas,  # ← NUEVO
        'total_clientes': total_clientes,  # ← NUEVO
        'ultimos_productos': ultimos_productos,
        'ultimas_transacciones': ultimas_transacciones,
        'ultimos_clientes': ultimos_clientes,  # ← NUEVO
        'bodegas': bodegas,  # ← NUEVO
    }

    return render(request, 'dashboard.html', context)