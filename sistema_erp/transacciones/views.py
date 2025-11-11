from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import MovimientoInventario, Bodega
from .forms import MovimientoInventarioForm


def lista_transacciones(request):
    qs = MovimientoInventario.objects.select_related('producto', 'proveedor', 'usuario', 'bodega')

    # Búsqueda
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(producto__nombre__icontains=q)
            | Q(proveedor__nombre__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(tipo__icontains=q)
            | Q(lote__icontains=q)
            | Q(serie__icontains=q)
            | Q(doc_referencia__icontains=q)
            | Q(motivo__icontains=q)
        )

    # Orden
    sort = (request.GET.get('sort') or 'fecha').strip()
    direction = (request.GET.get('dir') or 'desc').strip().lower()
    sort_map = {
        'fecha': 'fecha',
        'tipo': 'tipo',
        'producto__nombre': 'producto__nombre',
        'proveedor__nombre': 'proveedor__nombre',
        'cantidad': 'cantidad',
        'usuario__username': 'usuario__username',
        'lote': 'lote',
        'serie': 'serie',
        'fecha_vencimiento': 'fecha_vencimiento',
        'doc_referencia': 'doc_referencia',
    }
    order_field = sort_map.get(sort, 'fecha')
    if direction == 'desc':
        order_field = f'-{order_field}'
    qs = qs.order_by(order_field)

    # Tamaño de página persistente
    allowed_sizes = [5, 10, 20, 50]
    try:
        page_size = int(request.GET.get('page_size') or request.session.get('trans_page_size') or 10)
    except ValueError:
        page_size = 10
    if page_size not in allowed_sizes:
        page_size = 10
    request.session['trans_page_size'] = page_size

    paginator = Paginator(qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transacciones': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'q': q,
        'sort': sort,
        'dir': direction,
        'page_size': page_size,
        'page_sizes': allowed_sizes,
    }

    if request.GET.get('partial') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'transacciones/partials/transaccion_table.html', context)
    return render(request, 'transacciones/transaccion_list.html', context)

def crear_transaccion(request):
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            # El formulario ya incluye usuario y perfil; se guarda directo
            form.save()
            return redirect('/transacciones/?created=1')
    else:
        initial = {'fecha': timezone.now().strftime('%Y-%m-%dT%H:%M')}
        form = MovimientoInventarioForm(initial=initial)
    return render(request, 'transacciones/transaccion_add.html', {'form': form})

def detalle_transaccion(request, id):
    transaccion = get_object_or_404(MovimientoInventario.objects.select_related('producto', 'proveedor', 'usuario'), id=id)
    return render(request, 'transacciones/transaccion_detail.html', {'transaccion': transaccion})

def editar_transaccion(request, id):
    transaccion = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST, instance=transaccion)
        if form.is_valid():
            form.save()
            return redirect('/transacciones/?updated=1')
    else:
        initial = {'fecha': transaccion.fecha.strftime('%Y-%m-%dT%H:%M') if transaccion.fecha else timezone.now().strftime('%Y-%m-%dT%H:%M')}
        form = MovimientoInventarioForm(instance=transaccion, initial=initial)
    return render(request, 'transacciones/transaccion_edit.html', {'form': form, 'transaccion': transaccion})

def eliminar_transaccion(request, id):
    transaccion = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        transaccion.delete()
        return redirect('/transacciones/?deleted=1')
    return redirect('detalle_transaccion', id=id)
