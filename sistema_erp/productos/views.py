from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .forms import ProductoForm
from transacciones.models import MovimientoInventario
from django.core.paginator import Paginator
from django.db.models import Q

def lista_productos(request):
    q = request.GET.get('q', '')
    paginate_by = request.GET.get('paginate_by')
    if not paginate_by:
        paginate_by = request.session.get('paginate_by', 15)
    else:
        request.session['paginate_by'] = paginate_by

    sort = request.GET.get('sort', 'nombre')
    dir = request.GET.get('dir', 'asc')
    order = sort if dir == 'asc' else f'-{sort}'

    productos = Producto.objects.all()

    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) |
            Q(stock_actual__icontains=q) |
            Q(precio__icontains=q) |
            Q(proveedor__nombre__icontains=q)
        )

    productos = productos.order_by(order)

    paginator = Paginator(productos, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'productos/product_list.html', {
        'productos': page_obj,
        'page_obj': page_obj,
    })


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

