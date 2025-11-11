from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib import messages
from usuarios.models import Perfil
from .forms import LoginForm, RegistroForm

# ------------------------------
# Función para registrar un nuevo usuario
# ------------------------------
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            rol = form.cleaned_data['rol']
            telefono = form.cleaned_data.get('telefono')

            # Verificar duplicados en la base de datos
            if User.objects.filter(username=usuario).exists() or User.objects.filter(email=email).exists():
                messages.error(request, "El usuario o email ya existe.")
                return redirect('registro')

            # Crear el usuario y perfil
            user = User.objects.create_user(username=usuario, email=email, password=password)
            Perfil.objects.create(usuario=user, rol=rol, telefono=telefono)

            messages.success(request, "Usuario registrado exitosamente. Por favor, inicia sesión.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = RegistroForm()
    return render(request, 'autenticacion/registro.html', {'form': form})

# ------------------------------
# Función para iniciar sesión
# ------------------------------
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario_o_email = form.cleaned_data['usuario_o_email']
            password = form.cleaned_data['password']

            # Autenticar usuario por username o email (case-insensitive)
            user = User.objects.filter(username__iexact=usuario_o_email).first() or User.objects.filter(email__iexact=usuario_o_email).first()
            if user:
                auth_user = authenticate(request, username=user.username, password=password)
                if auth_user:
                    login(request, auth_user)  # Iniciar sesión
                    perfil = Perfil.objects.filter(usuario=user).first()
                    request.session['usuario'] = user.username
                    request.session['rol'] = perfil.rol if perfil else "Sin rol"
                    # Redirigir al dashboard
                    return render(request, 'dashboard.html', {
                        'total_productos': 100,  # Ejemplo de datos
                        'total_proveedores': 50,
                        'total_transacciones': 200,
                        'total_usuarios': 10,
                        'ultimos_productos': [],  # Lista vacía como ejemplo
                        'ultimas_transacciones': []  # Lista vacía como ejemplo
                    })
                else:
                    # Depuración servidor únicamente
                    print("[DEBUG login_view] Autenticación fallida para usuario:", user.username)
            else:
                print("[DEBUG login_view] Usuario no encontrado por username/email:", usuario_o_email)
            messages.error(request, "Credenciales inválidas. Por favor, inténtalo de nuevo.")
        else:
            messages.error(request, "Por favor, completa todos los campos correctamente.")
    else:
        form = LoginForm()
    return render(request, 'autenticacion/login.html', {'form': form})

# ------------------------------
# Función para recuperar contraseña (envía un enlace por correo)
# ------------------------------
def recuperar_password_view(request):
    # Funcionalidad de envío deshabilitada: si llega POST, mostramos info y permanecemos en la vista
    if request.method == 'POST':
        messages.info(request, "La recuperación por correo está deshabilitada en este entorno.")
    return render(request, 'autenticacion/recuperar_password.html')

# ------------------------------
# Función para restablecer contraseña usando un token
# ------------------------------
def restablecer_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "El enlace de recuperación no es válido.")
        return redirect('login')

    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password')
        confirmar_password = request.POST.get('confirmar_password')

        if nueva_password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect(request.path)

        if default_token_generator.check_token(user, token):
            user.set_password(nueva_password)
            user.save()
            messages.success(request, "Tu contraseña ha sido restablecida exitosamente.")
            return redirect('login')
        else:
            messages.error(request, "El enlace de recuperación ha expirado.")
            return redirect('login')

    return render(request, 'autenticacion/restablecer_password.html', {'uidb64': uidb64, 'token': token})

# ------------------------------
# Función para cambiar contraseña (usuario autenticado)
# ------------------------------
@login_required
def cambiar_password_view(request):
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        nueva_password = request.POST.get('nueva_password')
        confirmar_password = request.POST.get('confirmar_password')

        if not request.user.check_password(password_actual):
            messages.error(request, "La contraseña actual es incorrecta.")
            return redirect('cambiar_password')

        if nueva_password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('cambiar_password')

        request.user.set_password(nueva_password)
        request.user.save()
        messages.success(request, "Tu contraseña ha sido cambiada exitosamente.")
        return redirect('login')

    return render(request, 'autenticacion/cambiar_password.html')

# ------------------------------
# Cerrar sesión
# ------------------------------
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

