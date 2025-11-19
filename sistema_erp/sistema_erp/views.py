from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from productos.models import Producto
from proveedores.models import Proveedor
from transacciones.models import MovimientoInventario
from usuarios.models import Perfil
from django.http import Http404
from django.conf import settings

# Imports opcionales (la otra rama agregó estos modelos). Se manejan de forma segura si no existen.
try:
    from bodegas.models import Bodega  # type: ignore
except Exception:  # pragma: no cover
    Bodega = None  # fallback si app no está instalada

try:
    from clientes.models import Cliente  # type: ignore
except Exception:  # pragma: no cover
    Cliente = None  # fallback si app no está instalada

@login_required
def dashboard(request):
    """Dashboard principal combinando campos de ambas ramas (productos, proveedores, transacciones, usuarios,
    y opcionalmente bodegas/clientes si existen)."""
    # Sincroniza el rol en sesión (lógica de la rama HEAD)
    try:
        perfil = Perfil.objects.select_related('usuario').filter(usuario=request.user).first()
        if perfil:
            if request.session.get('rol') != perfil.rol:
                request.session['rol'] = perfil.rol
        else:
            request.session['rol'] = 'Sin rol'
    except Exception:
        request.session['rol'] = request.session.get('rol') or 'Sin rol'

    # Contadores base
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_transacciones = MovimientoInventario.objects.count()
    total_usuarios = User.objects.count()

    # Contadores extendidos opcionales (otra rama)
    if Bodega:

        try:
            total_bodegas = Bodega.objects.filter(estado='ACTIVO').count()
        except Exception:
            total_bodegas = Bodega.objects.count() if hasattr(Bodega, 'objects') else 0
    else:
        total_bodegas = 0

    if Cliente:

        try:
            total_clientes = Cliente.objects.filter(estadoCondicion='activo').count()
        except Exception:
            total_clientes = Cliente.objects.count() if hasattr(Cliente, 'objects') else 0

    else:
        total_clientes = 0

    # Últimos registros (mantener selects optimizados cuando es posible)
    # Usar 'pk' para compatibilidad con claves primarias personalizadas (idProducto)
    ultimos_productos = Producto.objects.order_by('-pk')[:5]
    ultimas_transacciones = MovimientoInventario.objects.select_related('producto').order_by('-fecha')[:5]
    ultimos_clientes = Cliente.objects.order_by('-idCliente')[:5] if Cliente and hasattr(Cliente, 'objects') else []
    bodegas = Bodega.objects.all()[:8] if Bodega and hasattr(Bodega, 'objects') else []

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


def custom_404_view(request, exception):
    """Vista personalizada para páginas no encontradas (404)."""
    return render(request, '404.html', status=404)


def force_404(request):
    """Ruta utilitaria para probar el handler 404 en desarrollo."""
    if getattr(settings, 'DEBUG', False):
        # En DEBUG, Django muestra el debug page para Http404; renderizamos para previsualizar
        return render(request, '404.html', status=404)
    raise Http404("Prueba de 404")


def preview_404(request):
    """Vista que renderiza directamente el template 404 (siempre), útil para QA."""
    return render(request, '404.html', status=404)


def not_found_view(request, extra=None):
    """Catch-all para rutas no definidas que muestra el template 404 incluso con DEBUG=True.

    Se coloca al final del urlpatterns para no interferir con rutas válidas.
    """
    return render(request, '404.html', status=404)
