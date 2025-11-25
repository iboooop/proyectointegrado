from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from .models import MovimientoInventario

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_movimiento(sender, instance, created, **kwargs):
    """
    Actualiza el stock de un producto cuando se crea o modifica un MovimientoInventario.
    """
    producto = instance.producto
    cantidad = instance.cantidad
    tipo_movimiento = instance.tipo

    # Usamos F() para evitar condiciones de carrera
    from django.db.models import F

    if created:
        # Movimiento nuevo
        if tipo_movimiento in ['INGRESO', 'DEVOLUCION', 'AJUSTE']:
            producto.stock_actual = F('stock_actual') + cantidad
        elif tipo_movimiento in ['SALIDA', 'VENTA']:
            producto.stock_actual = F('stock_actual') - cantidad
        # Para 'TRANSFERENCIA', el stock total no cambia.
    else:
        # Para movimientos existentes, la forma más segura es recalcular.
        recalcular_stock_producto(producto)
        return 

    if created:
        producto.save(update_fields=['stock_actual'])
        producto.refresh_from_db()


@receiver(post_delete, sender=MovimientoInventario)
def anular_stock_movimiento(sender, instance, **kwargs):
    """
    Anula el efecto de un movimiento en el stock cuando este se elimina.
    """
    producto = instance.producto
    cantidad = instance.cantidad
    tipo_movimiento = instance.tipo

    from django.db.models import F

    if tipo_movimiento in ['INGRESO', 'DEVOLUCION', 'AJUSTE']:
        producto.stock_actual = F('stock_actual') - cantidad
    elif tipo_movimiento in ['SALIDA', 'VENTA']:
        producto.stock_actual = F('stock_actual') + cantidad

    producto.save(update_fields=['stock_actual'])
    producto.refresh_from_db()


def recalcular_stock_producto(producto):
    """
    Recalcula el stock total de un producto basándose en todos sus movimientos.
    Es más lento pero más seguro en caso de inconsistencias o ediciones.
    """
    ingresos = MovimientoInventario.objects.filter(
        producto=producto, tipo__in=['INGRESO', 'DEVOLUCION', 'AJUSTE']
    ).aggregate(total=models.Sum('cantidad'))['total'] or 0

    salidas = MovimientoInventario.objects.filter(
        producto=producto, tipo__in=['SALIDA', 'VENTA']
    ).aggregate(total=models.Sum('cantidad'))['total'] or 0

    producto.stock_actual = ingresos - salidas
    producto.save(update_fields=['stock_actual'])