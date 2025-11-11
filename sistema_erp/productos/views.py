from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Producto
from .forms import ProductoForm
from transacciones.models import MovimientoInventario

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    Workbook = None


# ---------------- LISTAR ----------------
def lista_productos(request):
    productos = Producto.objects.select_related('proveedor').all()
    return render(request, 'productos/product_list.html', {'productos': productos})


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
