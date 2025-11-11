from django.shortcuts import render, get_object_or_404, redirect
from .models import Proveedor
from productos.models import Producto
from transacciones.models import MovimientoInventario
from .forms import ProveedorForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

def lista_proveedores(request):
    q = request.GET.get('q', '')
    paginate_by = request.GET.get('paginate_by')
    if not paginate_by:
        paginate_by = request.session.get('proveedores_paginate_by', 5)
    else:
        request.session['proveedores_paginate_by'] = paginate_by

    sort = request.GET.get('sort', 'nombre')
    dir = request.GET.get('dir', 'asc')
    order = sort if dir == 'asc' else f'-{sort}'

    proveedores = Proveedor.objects.all()

    if q:
        proveedores = proveedores.filter(
            Q(nombre__icontains=q) |
            Q(rut__icontains=q) |
            Q(contacto__icontains=q) |
            Q(telefono__icontains=q) |
            Q(correo__icontains=q)
        )

    proveedores = proveedores.order_by(order)

    paginator = Paginator(proveedores, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'proveedores/proveedor_list.html', {
        'proveedores': page_obj,
        'page_obj': page_obj,
    })


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
            messages.success(request, "Cambios guardados")
            return redirect('editar_proveedor', id=proveedor.id)
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proveedores/proveedor_edit.html', {'form': form, 'proveedor': proveedor})

def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        proveedor.delete()
        return redirect('lista_proveedores')
    return redirect('detalle_proveedor', id=id)
