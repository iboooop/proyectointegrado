from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from .forms import UsuarioForm, PerfilForm
from .models import Perfil
from productos.models import Producto
from proveedores.models import Proveedor
from transacciones.models import MovimientoInventario
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
except Exception:
    Workbook = None

# ---------------- DASHBOARD ----------------
@login_required
def dashboard_view(request):
    perfil = Perfil.objects.filter(usuario=request.user).first()
    if not perfil:
        return redirect('login')

    if perfil.rol == 'ADMIN':
        total_productos = Producto.objects.count()
        total_proveedores = Proveedor.objects.count()
        total_transacciones = MovimientoInventario.objects.count()
        total_usuarios = User.objects.count()

        # Compatibilidad con clave primaria custom (idProducto) usando 'pk'
        ultimos_productos = Producto.objects.order_by('-pk')[:5]
        ultimas_transacciones = MovimientoInventario.objects.select_related('producto').order_by('-fecha')[:5]

        return render(request, 'dashboard.html', {
            'total_productos': total_productos,
            'total_proveedores': total_proveedores,
            'total_transacciones': total_transacciones,
            'total_usuarios': total_usuarios,
            'ultimos_productos': ultimos_productos,
            'ultimas_transacciones': ultimas_transacciones
        })
    else:
        return render(request, 'usuarios/acceso_restringido.html', {'rol': perfil.rol})


# ---------------- LISTADO ----------------
@login_required
def usuarios_list_view(request):
    perfil = Perfil.objects.filter(usuario=request.user).first()
    if not perfil or perfil.rol != 'ADMIN':
        return redirect('dashboard')

    # Filtros de búsqueda
    q = (request.GET.get('q') or '').strip()

    # Ordenación segura por campos permitidos
    sort = (request.GET.get('sort') or 'usuario__username').strip()
    direction = (request.GET.get('dir') or 'asc').strip().lower()

    sort_map = {
        'usuario__username': 'usuario__username',
        'usuario__email': 'usuario__email',
        'usuario__first_name': 'usuario__first_name',
        'usuario__last_name': 'usuario__last_name',
        'telefono': 'telefono',
        'rol': 'rol',
        'estado': 'estado',
        'mfa_habilitado': 'mfa_habilitado',
        'usuario__last_login': 'usuario__last_login',
        'sesiones_activas': 'sesiones_activas',
    }

    base_qs = Perfil.objects.select_related('usuario').all()
    if q:
        base_qs = base_qs.filter(
            Q(usuario__first_name__icontains=q)
            | Q(usuario__last_name__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(usuario__email__icontains=q)
            | Q(telefono__icontains=q)
        )

    order_field = sort_map.get(sort, 'usuario__username')
    if direction == 'desc':
        order_field = f'-{order_field}'
    base_qs = base_qs.order_by(order_field)

    # Paginación
    # Tamaño de página configurable (persistente en sesión)
    allowed_page_sizes = [5, 10, 20, 50, 100]
    try:
        page_size = int(request.GET.get('page_size') or request.session.get('usuarios_page_size') or 10)
    except ValueError:
        page_size = 10
    if page_size not in allowed_page_sizes:
        page_size = 10
    request.session['usuarios_page_size'] = page_size

    paginator = Paginator(base_qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'perfiles': page_obj.object_list,
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
        return render(request, 'usuarios/partials/list_table.html', context)

    return render(request, 'usuarios/list.html', context)


# ---------------- CREAR ----------------
@login_required
def usuarios_create_view(request):
    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST)
        perfil_form = PerfilForm(request.POST)

        if usuario_form.is_valid() and perfil_form.is_valid():
            try:
                with transaction.atomic():
                    usuario = usuario_form.save()
                    perfil = perfil_form.save(commit=False)
                    perfil.usuario = usuario
                    perfil.save()

                # Redirigir al listado con bandera de creación para SweetAlert
                url = f"{reverse('usuarios_list')}?created=1"
                return redirect(url)
            except ValidationError as e:
                usuario_form.add_error(None, e.message if hasattr(e, 'message') else str(e))
                messages.error(request, "Hubo un error al crear el usuario. Verifique los datos ingresados.")
        else:
            print("Errores UsuarioForm:", usuario_form.errors)
            print("Errores PerfilForm:", perfil_form.errors)
            messages.error(request, "Hubo un error al crear el usuario. Verifique los datos ingresados.")
    else:
        usuario_form = UsuarioForm()
        perfil_form = PerfilForm()

    return render(request, 'usuarios/create.html', {
        'usuario_form': usuario_form,
        'perfil_form': perfil_form,
        'show_messages': request.method == 'POST'
    })


# ---------------- EDITAR ----------------
@login_required
def usuarios_edit_view(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    usuario = perfil.usuario
    updated = False  # 🔹 Bandera para saber si se guardó correctamente

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST, instance=usuario)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)

        if usuario_form.is_valid() and perfil_form.is_valid():
            # Detectar si realmente hubo cambios en alguno de los formularios
            user_changed = usuario_form.has_changed()
            perfil_changed = perfil_form.has_changed()
            password_changed = bool(usuario_form.cleaned_data.get('password'))

            if not (user_changed or perfil_changed or password_changed):
                messages.info(request, "No se detectaron cambios para guardar.")
                # Renderizar la misma vista sin redirigir ni marcar 'updated'
                return render(request, 'usuarios/edit.html', {
                    'usuario_form': usuario_form,
                    'perfil_form': perfil_form,
                    'updated': False,
                    'no_changes': True,
                })

            # Guardar solo si hubo cambios
            usuario_form.save()
            perfil_form.save()
            # Mensaje flash de éxito (consumido una sola vez)
            messages.success(request, "Los cambios se han guardado correctamente.")
            # Redirigir sin query params para evitar re-mostrar al refrescar
            return redirect(reverse('usuarios_edit', args=[perfil.id]))
        else:
            print("Errores UsuarioForm:", usuario_form.errors)
            print("Errores PerfilForm:", perfil_form.errors)
            messages.error(request, "No se pudieron guardar los cambios. Verifique los datos.")
    else:
        usuario_form = UsuarioForm(instance=usuario)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'usuarios/edit.html', {
        'usuario_form': usuario_form,
        'perfil_form': perfil_form,
        # Los SweetAlerts se disparan por mensajes (messages.success), no por query params
    })


# ---------------- ELIMINAR ----------------
@login_required
def usuarios_delete_view(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    usuario = perfil.usuario

    if request.method == 'POST':
        usuario.delete()
        perfil.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('usuarios_list')

    return render(request, 'usuarios/delete.html', {'perfil': perfil})


# ---------------- EXPORTAR EXCEL ----------------
@login_required
def export_usuarios_excel(request):
    """Exporta todos los usuarios (User + Perfil) a un archivo XLSX."""
    if Workbook is None:
        return HttpResponse("openpyxl no está instalado. Agrega 'openpyxl' a requirements.txt e instala las dependencias.", status=500)

    perfiles = Perfil.objects.select_related('usuario').order_by('usuario__username')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Usuarios'

    headers = [
        'Username', 'Email', 'Nombres', 'Apellidos', 'Teléfono',
        'Rol', 'Estado', 'MFA', 'Último acceso', 'Sesiones activas'
    ]
    header_fill = PatternFill(start_color='EAF2FF', end_color='EAF2FF', fill_type='solid')
    bold = Font(bold=True, color='1f2937')
    center = Alignment(horizontal='center', vertical='center')

    ws.append(headers)
    # Estilos de encabezado con bordes gruesos
    from openpyxl.styles import Border, Side
    medium_side = Side(style='medium', color='64748B')
    header_border = Border(top=medium_side, left=medium_side, right=medium_side, bottom=medium_side)
    for cell in ws[1]:
        cell.font = bold
        cell.fill = header_fill
        cell.alignment = center
        cell.border = header_border

    thin_side = Side(style='thin', color='CBD5E1')
    row_border = Border(top=thin_side, left=thin_side, right=thin_side, bottom=thin_side)
    for idx, p in enumerate(perfiles, start=2):
        u = p.usuario
        row = [
            u.username,
            u.email,
            u.first_name,
            u.last_name,
            p.telefono or '',
            p.get_rol_display() if hasattr(p, 'get_rol_display') else p.rol,
            p.estado,
            'Sí' if p.mfa_habilitado else 'No',
            u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else '',
            p.sesiones_activas,
        ]
        ws.append(row)
        # Alternancia de filas para mejor lectura
        # Alternancia filas pares
        if idx % 2 == 0:
            alt_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')
            for c in ws[idx]:
                c.fill = alt_fill
        # Bordes y alineaciones
        for col_i, c in enumerate(ws[idx], start=1):
            c.border = row_border
            if col_i in (1,2,3,4,6,7):  # texto clave
                c.alignment = Alignment(vertical='center')
            if col_i == 9:  # Último acceso
                c.alignment = Alignment(horizontal='center', vertical='center')
            if col_i == 10:  # Sesiones activas
                c.alignment = Alignment(horizontal='center', vertical='center')

    # Formatos y UX de hoja: auto-filter, freeze panes y anchos
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = 'A2'
    # Ajustar altura encabezado y datos
    ws.row_dimensions[1].height = 24
    for r in range(2, ws.max_row+1):
        ws.row_dimensions[r].height = 18
    from openpyxl.utils import get_column_letter
    widths = [18, 28, 20, 20, 16, 18, 14, 10, 20, 18]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"usuarios_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

@login_required
def user_list(request):
    # obtener rol de forma segura
    perfil = getattr(request.user, 'perfil', None)
    rol = getattr(perfil, 'rol', None)

    # permitir ADMIN, LECTOR y EDITOR
    if rol not in ('ADMIN', 'LECTOR', 'EDITOR'):
        return HttpResponseForbidden("No tiene permisos para ver usuarios.")

    # Filtros de búsqueda
    q = (request.GET.get('q') or '').strip()

    # Ordenación segura por campos permitidos
    sort = (request.GET.get('sort') or 'usuario__username').strip()
    direction = (request.GET.get('dir') or 'asc').strip().lower()

    sort_map = {
        'usuario__username': 'usuario__username',
        'usuario__email': 'usuario__email',
        'usuario__first_name': 'usuario__first_name',
        'usuario__last_name': 'usuario__last_name',
        'telefono': 'telefono',
        'rol': 'rol',
        'estado': 'estado',
        'mfa_habilitado': 'mfa_habilitado',
        'usuario__last_login': 'usuario__last_login',
        'sesiones_activas': 'sesiones_activas',
    }

    base_qs = Perfil.objects.select_related('usuario').all()
    if q:
        base_qs = base_qs.filter(
            Q(usuario__first_name__icontains=q)
            | Q(usuario__last_name__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(usuario__email__icontains=q)
            | Q(telefono__icontains=q)
        )

    order_field = sort_map.get(sort, 'usuario__username')
    if direction == 'desc':
        order_field = f'-{order_field}'
    base_qs = base_qs.order_by(order_field)

    # Paginación
    # Tamaño de página configurable (persistente en sesión)
    allowed_page_sizes = [5, 10, 20, 50, 100]
    try:
        page_size = int(request.GET.get('page_size') or request.session.get('usuarios_page_size') or 10)
    except ValueError:
        page_size = 10
    if page_size not in allowed_page_sizes:
        page_size = 10
    request.session['usuarios_page_size'] = page_size

    paginator = Paginator(base_qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'perfiles': page_obj.object_list,
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
        return render(request, 'usuarios/partials/list_table.html', context)

    return render(request, 'usuarios/list.html', context)
