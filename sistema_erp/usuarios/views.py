from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from .forms import UsuarioForm, PerfilForm
from .models import Perfil

# ---------------- DASHBOARD ----------------
@login_required
def dashboard_view(request):
    perfil = Perfil.objects.filter(usuario=request.user).first()
    if not perfil:
        return redirect('login')

    if perfil.rol == 'ADMIN':
        return render(request, 'dashboard.html', {
            'total_productos': 100,
            'total_proveedores': 50,
            'total_transacciones': 200,
            'total_usuarios': 10,
            'ultimos_productos': [],
            'ultimas_transacciones': []
        })
    else:
        return render(request, 'usuarios/acceso_restringido.html', {'rol': perfil.rol})


# ---------------- LISTADO ----------------
@login_required
def usuarios_list_view(request):
    perfil = Perfil.objects.filter(usuario=request.user).first()
    if not perfil or perfil.rol != 'ADMIN':
        return redirect('dashboard')

    perfiles = Perfil.objects.all()
    return render(request, 'usuarios/list.html', {'perfiles': perfiles})


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

                messages.success(request, "Usuario creado exitosamente.")
                return redirect('usuarios_list')
            except ValidationError as e:
                # Adjuntar el error no asociado a campo específico
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

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST, instance=usuario)
        perfil_form = PerfilForm(request.POST, instance=perfil)

        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, "Cambios guardados correctamente.")
            return redirect('usuarios_list')
        else:
            print("Errores UsuarioForm:", usuario_form.errors)
            print("Errores PerfilForm:", perfil_form.errors)
            messages.error(request, "No se pudieron guardar los cambios. Verifique los datos.")
    else:
        usuario_form = UsuarioForm(instance=usuario)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'usuarios/edit.html', {
        'usuario_form': usuario_form,
        'perfil_form': perfil_form
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