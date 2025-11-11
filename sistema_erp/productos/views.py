from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Producto
from .forms import ProductoForm
from transacciones.models import MovimientoInventario
from django.core.paginator import Paginator
from django.db.models import Q

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    Workbook = None


# ---------------- LISTAR ----------------
def lista_productos(request):
    qs = Producto.objects.select_related('proveedor').all()

    # --- Búsqueda ---
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q)
            | Q(categoria__icontains=q)
            | Q(precio__icontains=q)
            | Q(stock_actual__icontains=q)
            | Q(proveedor__nombre__icontains=q)
        )

    # --- Orden ---
    sort = (request.GET.get('sort') or 'nombre').strip()
    direction = (request.GET.get('dir') or 'asc').strip().lower()
    if direction == 'desc':
        sort = f'-{sort}'
    qs = qs.order_by(sort)

    # --- Paginación ---
    allowed_sizes = [5, 10, 20, 50]
    try:
        page_size = int(request.GET.get('page_size') or request.session.get('producto_page_size') or 10)
    except ValueError:
        page_size = 10
    if page_size not in allowed_sizes:
        page_size = 10
    request.session['producto_page_size'] = page_size

    paginator = Paginator(qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'productos': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'q': q,
        'sort': sort,
        'dir': direction,
        'page_size': page_size,
        'page_sizes': allowed_sizes,
    }

    # --- Render parcial (AJAX) ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('partial') == '1':
        return render(request, 'productos/partials/producto_table.html', context)

    # --- Render completo ---
    return render(request, 'productos/product_list.html', context)



# ---------------- CREAR ----------------
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/product_add.html', {'form': form})


# ---------------- DETALLE ----------------
def detalle_producto(request, id):
    # ✅ Corregido: buscar por idProducto, no por id
    producto = get_object_or_404(Producto.objects.select_related('proveedor'), idProducto=id)
    movimientos = MovimientoInventario.objects.filter(producto=producto).select_related('proveedor', 'usuario').order_by('-fecha')

    return render(request, 'productos/product_detail.html', {
        'producto': producto,
        'movimientos': movimientos,
    })


# ---------------- EDITAR ----------------
def editar_producto(request, id):
    # ✅ Corregido igual
    producto = get_object_or_404(Producto, idProducto=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('detalle_producto', id=producto.idProducto)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/product_edit.html', {'form': form, 'producto': producto})


# ---------------- ELIMINAR ----------------
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, idProducto=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return redirect('detalle_producto', id=id)


# ---------------- EXPORTAR EXCEL ----------------
def exportar_productos_excel(request):
    if Workbook is None:
        return HttpResponse("openpyxl no está instalado.", status=500)

    qs = Producto.objects.select_related('proveedor').all().order_by('idProducto')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Productos'

    headers = ['ID', 'Nombre', 'Categoría', 'Proveedor', 'Precio', 'Stock', 'Fecha Vencimiento', 'Lote', 'Bodega']
    header_fill = PatternFill(start_color='EAF2FF', end_color='EAF2FF', fill_type='solid')
    bold = Font(bold=True, color='1f2937')
    center = Alignment(horizontal='center', vertical='center')

    ws.append(headers)
    medium_side = Side(style='medium', color='64748B')
    header_border = Border(top=medium_side, left=medium_side, right=medium_side, bottom=medium_side)
    for c in ws[1]:
        c.font = bold
        c.fill = header_fill
        c.alignment = center
        c.border = header_border

    thin_side = Side(style='thin', color='CBD5E1')
    row_border = Border(top=thin_side, left=thin_side, right=thin_side, bottom=thin_side)

    for idx, p in enumerate(qs, start=2):
        row = [
            p.idProducto,
            p.nombre,
            p.categoria,
            getattr(p.proveedor, 'nombre', '') if p.proveedor else '',
            p.precio,
            p.stock_actual,
            p.fecha_vencimiento.strftime('%Y-%m-%d') if p.fecha_vencimiento else '',
            p.lote or '',
            getattr(p.bodega, 'nombre', '') if p.bodega else '',
        ]
        ws.append(row)

        # Filas alternadas
        if idx % 2 == 0:
            alt_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')
            for c in ws[idx]:
                c.fill = alt_fill

        for c in ws[idx]:
            c.border = row_border
            c.alignment = Alignment(vertical='center')

    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = 'A2'
    ws.row_dimensions[1].height = 24

    widths = [8, 24, 18, 24, 12, 10, 16, 14, 20]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    from datetime import datetime
    response['Content-Disposition'] = f'attachment; filename="productos_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx"'
    wb.save(response)
    return response
