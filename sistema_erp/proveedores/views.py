from django.shortcuts import render, get_object_or_404, redirect
from .models import Proveedor
from productos.models import Producto
from transacciones.models import MovimientoInventario
from .forms import ProveedorForm

def lista_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'proveedores/proveedor_list.html', {'proveedores': proveedores})


def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'proveedores/proveedor_add.html', {'form': form})

def detalle_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    productos = Producto.objects.filter(proveedor=proveedor)
    movimientos = MovimientoInventario.objects.filter(proveedor=proveedor).select_related('producto').order_by('-fecha')

    context = {
        'proveedor': proveedor,
        'productos': productos,
        'movimientos': movimientos,
    }
    return render(request, 'proveedores/proveedor_detail.html', context)

def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('detalle_proveedor', id=proveedor.id)
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proveedores/proveedor_edit.html', {'form': form, 'proveedor': proveedor})

def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        proveedor.delete()
        return redirect('lista_proveedores')
    return redirect('detalle_proveedor', id=id)
