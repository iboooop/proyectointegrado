from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse


# ✅ Corrección: importamos Bodega desde la app bodegas, no desde transacciones
from bodegas.models import Bodega
from .models import MovimientoInventario
from .forms import MovimientoInventarioForm



# ---------------- LISTA ----------------
def lista_transacciones(request):
    # Filtros de búsqueda
    q = (request.GET.get('q') or '').strip()

    # Ordenación segura por campos permitidos
    sort = (request.GET.get('sort') or 'fecha').strip()
    direction = (request.GET.get('dir') or 'desc').strip().lower()

    sort_map = {
        'fecha': 'fecha',
        'tipo': 'tipo',
        'producto': 'producto__nombre',
        'proveedor': 'proveedor__nombre',
        'cantidad': 'cantidad',
        'usuario': 'usuario',
        'lote': 'lote',
    }

    base_qs = MovimientoInventario.objects.select_related('producto', 'proveedor').all()
    if q:
        base_qs = base_qs.filter(
            Q(producto__nombre__icontains=q) |
            Q(proveedor__nombre__icontains=q) |
            Q(tipo__icontains=q) |
            Q(usuario__icontains=q) |
            Q(lote__icontains=q) |
            Q(observaciones__icontains=q)
        )

    order_field = sort_map.get(sort, 'fecha')
    if direction == 'desc':
        order_field = f'-{order_field}'
    base_qs = base_qs.order_by(order_field)

    # Paginación
    allowed_page_sizes = [5, 10, 20, 50, 100]
    try:
        page_size = int(request.GET.get('page_size') or request.session.get('transacciones_page_size') or 10)
    except ValueError:
        page_size = 10
    if page_size not in allowed_page_sizes:
        page_size = 10
    request.session['transacciones_page_size'] = page_size

    paginator = Paginator(base_qs, page_size)
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
        'page_sizes': allowed_page_sizes,
    }

    # Respuesta parcial para AJAX (solo tabla y paginación)
    if request.GET.get('partial') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'transacciones/partials/transaccion_table.html', context)

    return render(request, 'transacciones/transaccion_list.html', context)


# ---------------- CREAR ----------------
def crear_transaccion(request):
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/transacciones/?created=1')
    else:
        initial = {'fecha': timezone.now().strftime('%Y-%m-%dT%H:%M')}
        form = MovimientoInventarioForm(initial=initial)
    return render(request, 'transacciones/transaccion_add.html', {'form': form})


# ---------------- DETALLE ----------------
def detalle_transaccion(request, id):
    transaccion = get_object_or_404(
        MovimientoInventario.objects.select_related('producto', 'proveedor', 'usuario'), id=id
    )
    return render(request, 'transacciones/transaccion_detail.html', {'transaccion': transaccion})


# ---------------- EDITAR ----------------
def editar_transaccion(request, id):
    transaccion = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST, instance=transaccion)
        if form.is_valid():
            form.save()
            return redirect('/transacciones/?updated=1')
    else:
        initial = {
            'fecha': transaccion.fecha.strftime('%Y-%m-%dT%H:%M')
            if transaccion.fecha else timezone.now().strftime('%Y-%m-%dT%H:%M')
        }
        form = MovimientoInventarioForm(instance=transaccion, initial=initial)
    return render(request, 'transacciones/transaccion_edit.html', {'form': form, 'transaccion': transaccion})


# ---------------- ELIMINAR ----------------
def eliminar_transaccion(request, id):
    transaccion = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        transaccion.delete()
        return redirect('/transacciones/?deleted=1')
    return redirect('detalle_transaccion', id=id)


# ---------------- EXPORTAR EXCEL ----------------
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    Workbook = None


def exportar_transacciones_excel(request):
    """Exporta los movimientos filtrados/ordenados a un archivo XLSX con detalles."""
    if Workbook is None:
        return HttpResponse(
            "openpyxl no está instalado. Agrega 'openpyxl' a requirements.txt e instala las dependencias.",
            status=500
        )

    qs = MovimientoInventario.objects.select_related('producto', 'proveedor', 'usuario', 'bodega')

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

    wb = Workbook()
    ws = wb.active
    ws.title = 'Movimientos'

    headers = [
        'Fecha', 'Tipo', 'Producto', 'Proveedor', 'Usuario', 'Cantidad',
        'Bodega', 'Lote', 'Serie', 'Vence', 'Doc Ref', 'Motivo', 'Observaciones'
    ]
    header_fill = PatternFill(start_color='EAF2FF', end_color='EAF2FF', fill_type='solid')
    bold = Font(bold=True, color='1f2937')
    center = Alignment(horizontal='center', vertical='center')

    ws.append(headers)
    medium_side = Side(style='medium', color='64748B')
    header_border = Border(top=medium_side, left=medium_side, right=medium_side, bottom=medium_side)
    for cell in ws[1]:
        cell.font = bold
        cell.fill = header_fill
        cell.alignment = center
        cell.border = header_border

    thin_side = Side(style='thin', color='CBD5E1')
    row_border = Border(top=thin_side, left=thin_side, right=thin_side, bottom=thin_side)

    for idx, m in enumerate(qs, start=2):
        row = [
            m.fecha.strftime('%Y-%m-%d %H:%M') if m.fecha else '',
            dict(MovimientoInventario.TIPO_MOVIMIENTO).get(m.tipo, m.tipo),
            getattr(m.producto, 'nombre', ''),
            getattr(m.proveedor, 'nombre', '') if m.proveedor else '',
            getattr(m.usuario, 'username', '') if m.usuario else '',
            m.cantidad,
            getattr(m.bodega, 'codigo', '') if m.bodega else '',
            m.lote or '',
            m.serie or '',
            m.fecha_vencimiento.strftime('%Y-%m-%d') if m.fecha_vencimiento else '',
            m.doc_referencia or '',
            m.motivo or '',
            (m.observaciones or '')[:1000],
        ]
        ws.append(row)

        # Color alternado
        if idx % 2 == 0:
            alt_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')
            for c in ws[idx]:
                c.fill = alt_fill

        # Bordes y alineación
        for c in ws[idx]:
            c.border = row_border
            c.alignment = Alignment(vertical='center')

    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = 'A2'
    ws.row_dimensions[1].height = 24

    widths = [18, 12, 28, 22, 18, 10, 16, 14, 18, 14, 16, 24, 40]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    from datetime import datetime
    filename = f"movimientos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    wb.save(response)
    return response
