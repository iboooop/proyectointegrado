from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .forms import ProductoForm
from transacciones.models import MovimientoInventario

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

