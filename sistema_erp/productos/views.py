from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Producto
from .forms import ProductoForm
from transacciones.models import MovimientoInventario
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
except ImportError:
    Workbook = None

def lista_productos(request):
    productos = Producto.objects.select_related('proveedor').all()
    return render(request, 'productos/product_list.html', {'productos': productos})


def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # redirige al listado después de guardar
    else:
        form = ProductoForm()
    return render(request, 'productos/product_add.html', {'form': form})

def detalle_producto(request, id):
    producto = get_object_or_404(Producto.objects.select_related('proveedor'), id=id)
    movimientos = MovimientoInventario.objects.filter(producto=producto).select_related('proveedor', 'usuario').order_by('-fecha')
    
    return render(request, 'productos/product_detail.html', {
        'producto': producto,
        'movimientos': movimientos,
    })

def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('detalle_producto', id=producto.id)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/product_edit.html', {'form': form, 'producto': producto})

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return redirect('detalle_producto', id=id)


def exportar_productos_excel(request):
    if Workbook is None:
        return HttpResponse("openpyxl no está instalado.", status=500)

    qs = Producto.objects.select_related('proveedor').all().order_by('id')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Productos'

    headers = [
        'ID', 'SKU', 'Nombre', 'Proveedor', 'Stock', 'Precio', 'Estado'
    ]
    header_fill = PatternFill(start_color='EAF2FF', end_color='EAF2FF', fill_type='solid')
    bold = Font(bold=True, color='1f2937')
    center = Alignment(horizontal='center', vertical='center')
    ws.append(headers)
    medium_side = Side(style='medium', color='64748B')
    header_border = Border(top=medium_side, left=medium_side, right=medium_side, bottom=medium_side)
    for c in ws[1]:
        c.font = bold; c.fill = header_fill; c.alignment = center; c.border = header_border

    thin_side = Side(style='thin', color='CBD5E1')
    row_border = Border(top=thin_side, left=thin_side, right=thin_side, bottom=thin_side)
    for idx, p in enumerate(qs, start=2):
        row = [
            p.id,
            getattr(p, 'sku', ''),
            p.nombre,
            getattr(p.proveedor, 'nombre', '') if getattr(p, 'proveedor', None) else '',
            getattr(p, 'stock', ''),
            getattr(p, 'precio', ''),
            getattr(p, 'estado', ''),
        ]
        ws.append(row)
        if idx % 2 == 0:
            alt_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')
            for c in ws[idx]: c.fill = alt_fill
        for col_i, c in enumerate(ws[idx], start=1):
            c.border = row_border
            if col_i in (1,4,5,6):
                c.alignment = Alignment(horizontal='center', vertical='center')
            else:
                c.alignment = Alignment(vertical='center')

    # AutoFilter y freeze
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = 'A2'
    from openpyxl.utils import get_column_letter
    widths = [8, 16, 32, 24, 10, 12, 14]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 24
    for r in range(2, ws.max_row+1): ws.row_dimensions[r].height = 18

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    from datetime import datetime
    response['Content-Disposition'] = f'attachment; filename="productos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"'
    wb.save(response)
    return response

