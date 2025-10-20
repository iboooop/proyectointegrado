from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Perfil, RoleModulePermission, Module
from .forms import PerfilForm

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
@login_required
@role_required(['ADMIN'])
def usuarios_list_view(request):
    perfiles = Perfil.objects.select_related('usuario').all()
    return render(request, 'usuarios/list.html', {'perfiles': perfiles})

# Vista para crear un usuario (solo accesible para ADMIN)
@login_required
@role_required(['ADMIN'])
@csrf_exempt
def usuarios_create_view(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Usuario creado exitosamente"})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = PerfilForm()
    return render(request, 'usuarios/create.html', {'form': form})

# Vista para editar un usuario (solo accesible para ADMIN)
@login_required
@role_required(['ADMIN'])
@csrf_exempt
def usuarios_edit_view(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Usuario actualizado exitosamente"})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'usuarios/edit.html', {'form': form, 'perfil': perfil})

# Vista para eliminar un usuario (solo accesible para ADMIN)
@login_required
@role_required(['ADMIN'])
@csrf_exempt
def usuarios_delete_view(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    perfil.delete()
    return JsonResponse({"message": "Usuario eliminado exitosamente"})

# Vista para listar módulos y permisos (solo accesible para ADMIN)
@login_required
@role_required(['ADMIN'])
def permisos_list_view(request):
    permisos = RoleModulePermission.objects.select_related('role', 'module').all()
    return render(request, 'usuarios/permisos_list.html', {'permisos': permisos})