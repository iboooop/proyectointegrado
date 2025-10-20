from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Perfil, RoleModulePermission, Module
from .forms import PerfilForm
from django.contrib import messages  
from functools import wraps


def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario'):  # Verificar si hay un usuario en la sesión
            return redirect('login')  # Redirigir al login si no hay sesión
        return view_func(request, *args, **kwargs)
    return wrapper


@custom_login_required
def dashboard_view(request):
    usuario = request.session.get('usuario')
    rol = request.session.get('rol')
    return render(request, 'usuarios/dashboard.html', {'usuario': usuario, 'rol': rol})

# Decorador para verificar el rol del usuario
def role_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            perfil = Perfil.objects.filter(usuario=request.user).first()
            if perfil and perfil.rol in roles:
                return view_func(request, *args, **kwargs)
            return JsonResponse({"error": "No tienes permiso para acceder a esta vista"}, status=403)
        return wrapper
    return decorator

# Vista para listar usuarios (solo accesible para ADMIN)
@custom_login_required
@role_required(['ADMIN'])
def usuarios_list_view(request):
    perfiles = Perfil.objects.all()  # Obtener todos los perfiles de usuarios
    return render(request, 'usuarios/list.html', {'perfiles': perfiles})

# Vista para crear un usuario (solo accesible para ADMIN)
@custom_login_required
@role_required(['ADMIN'])
def usuarios_create_view(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect('usuarios_list')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PerfilForm()
    return render(request, 'usuarios/create.html', {'form': form})

# Vista para editar un usuario (solo accesible para ADMIN)
@custom_login_required
@role_required(['ADMIN'])
def usuarios_edit_view(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect('usuarios_list')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'usuarios/edit.html', {'form': form, 'perfil': perfil})

# Vista para eliminar un usuario (solo accesible para ADMIN)
@custom_login_required
@role_required(['ADMIN'])
def usuarios_delete_view(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    perfil.delete()
    messages.success(request, "Usuario eliminado exitosamente.")
    return redirect('usuarios_list')

# Vista para listar módulos y permisos (solo accesible para ADMIN)
