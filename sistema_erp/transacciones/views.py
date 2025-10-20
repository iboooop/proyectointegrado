from django.shortcuts import render, get_object_or_404, redirect
from .models import MovimientoInventario
from .forms import MovimientoInventarioForm


def lista_transacciones(request):
    transacciones = MovimientoInventario.objects.select_related('producto', 'proveedor', 'usuario').order_by('-fecha')
    return render(request, 'transacciones/transaccion_list.html', {'transacciones': transacciones})

def crear_transaccion(request):
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_transacciones')
    else:
        form = MovimientoInventarioForm()
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
            return redirect('detalle_transaccion', id=transaccion.id)
    else:
        form = MovimientoInventarioForm(instance=transaccion)
    return render(request, 'transacciones/transaccion_edit.html', {'form': form, 'transaccion': transaccion})

def eliminar_transaccion(request, id):
    transaccion = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        transaccion.delete()
        return redirect('lista_transacciones')
    return redirect('detalle_transaccion', id=id)
