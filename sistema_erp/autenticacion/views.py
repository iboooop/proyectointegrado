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
import os
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
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
    """
    Login con límite de intentos por IP:
    - 3 intentos fallidos → bloqueo temporal de 3 minutos
    - Muestra remaining_seconds en la plantilla para el timer JS
    """
    MAX_ATTEMPTS = 3
    BLOCK_SECONDS = 3 * 60  # 3 minutos

    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key_attempts = f'login_attempts:ip:{ip}'
    key_block = f'login_block:ip:{ip}'

    # comprobar bloqueo por IP
    remaining_seconds = 0
    block_until = cache.get(key_block)
    now = timezone.now()
    if block_until and block_until > now:
        remaining_seconds = int((block_until - now).total_seconds())

    # inicializar form (mantener en contexto siempre)
    if request.method == 'POST':
        form = LoginForm(request.POST)
    else:
        form = LoginForm()

    if request.method == 'POST':
        # si está bloqueado, no procesar credenciales
        if remaining_seconds > 0:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            messages.error(request, f"Has superado los intentos. Intenta nuevamente en {minutes}m {seconds}s.")
            return render(request, 'autenticacion/login.html', {'form': form, 'remaining_seconds': remaining_seconds})

        if not form.is_valid():
            # mostrar errores de validación del form
            return render(request, 'autenticacion/login.html', {'form': form, 'remaining_seconds': remaining_seconds})

        usuario_or_email = form.cleaned_data.get('usuario_o_email', '').strip()
        password = form.cleaned_data.get('password', '')

        # Ajusta aquí si permites login por email -> ejemplo simple usa username
        user = authenticate(request, username=usuario_or_email, password=password)

        if user is None:
            # intento fallido: incrementar contador
            attempts = cache.get(key_attempts, 0) + 1
            cache.set(key_attempts, attempts, timeout=BLOCK_SECONDS)
            if attempts >= MAX_ATTEMPTS:
                block_until = now + timedelta(seconds=BLOCK_SECONDS)
                cache.set(key_block, block_until, timeout=BLOCK_SECONDS)
                cache.delete(key_attempts)
                remaining_seconds = BLOCK_SECONDS
                messages.error(request, f"Has superado {MAX_ATTEMPTS} intentos. Bloqueado por 3 minutos.")
            else:
                rest = MAX_ATTEMPTS - attempts
                # mensaje genérico para no revelar si usuario existe o no
                messages.error(request, f"Nombre de usuario o contraseña incorrectos. Te quedan {rest} intento(s).")
            return render(request, 'autenticacion/login.html', {'form': form, 'remaining_seconds': remaining_seconds})

        # user autenticado correctamente -> verificar perfil y estado
        perfil = Perfil.objects.filter(usuario=user).first()
        if perfil and perfil.estado in ['BLOQUEADO', 'INACTIVO']:
            if perfil.estado == 'BLOQUEADO':
                mensaje_error = 'Tu cuenta ha sido bloqueada. Por favor, comunícate con el administrador del sistema para resolver esta situación.'
            else:
                mensaje_error = 'Tu cuenta está inactiva. Por favor, comunícate con el administrador del sistema para activarla.'
            form.add_error(None, mensaje_error)
            return render(request, 'autenticacion/login.html', {'form': form})

        # limpiar contadores y loguear
        cache.delete(key_attempts)
        cache.delete(key_block)
        login(request, user)
        request.session['usuario'] = user.username
        request.session['rol'] = perfil.rol if perfil else "Sin rol"

        # si debe cambiar clave provisional -> redirigir (asegúrate que exista la ruta 'cambiar_password')
        if perfil and getattr(perfil, 'debe_cambiar_clave', False):
            messages.warning(request, 'Por seguridad, debes cambiar tu contraseña provisoria antes de continuar.')
            return redirect('cambiar_password')

        return redirect('dashboard')

    # GET
    return render(request, 'autenticacion/login.html', {'form': form, 'remaining_seconds': remaining_seconds})

# ------------------------------
# Función para recuperar contraseña (envía un enlace por correo)
# ------------------------------
def recuperar_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario con ese correo registrado.")
            return redirect('recuperar_password')

        # Generar token seguro
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construir enlace absoluto
        url_reset = request.build_absolute_uri(
            f"/autenticacion/reset/{uid}/{token}/"
        )

        # Enviar correo
        send_mail(
            subject="Recuperación de contraseña - Lilis ERP",
            message=f"Hola {user.username},\n\n"
                    f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n\n"
                    f"{url_reset}\n\n"
                    f"Si no solicitaste este cambio, puedes ignorar este mensaje.",
            from_email=os.getenv("EMAIL_HOST_USER"),
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Hemos enviado un correo con instrucciones para recuperar tu contraseña.")
        return redirect('login')

    return render(request, 'autenticacion/recuperar_password.html')

# ------------------------------
# Función para restablecer contraseña usando un token
# ------------------------------
def restablecer_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        messages.error(request, "El enlace de recuperación no es válido.")
        return redirect('login')

    # Validar token
    if not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace de recuperación ha expirado o no es válido.")
        return redirect('login')

    if request.method == 'POST':
        nueva = request.POST.get('nueva_password')
        confirmar = request.POST.get('confirmar_password')

        if nueva != confirmar:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect(request.path)

        user.set_password(nueva)
        user.save()

        messages.success(request, "Tu contraseña ha sido restablecida correctamente.")
        return redirect('login')

    return render(request, 'autenticacion/restablecer_password.html')
# ------------------------------
# Función para cambiar contraseña (usuario autenticado)
# ------------------------------
@login_required
def cambiar_password_view(request):
    # Limpiar mensajes antiguos al cargar la vista en GET
    if request.method == 'GET':
        storage = messages.get_messages(request)
        storage.used = True
    
    perfil = Perfil.objects.filter(usuario=request.user).first()
    es_cambio_obligatorio = perfil.debe_cambiar_clave if perfil else False
    
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
        
        # RQ-USR-04: Validar política de robustez
        if len(nueva_password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return redirect('cambiar_password')
        
        import re
        if not re.search(r'[A-Z]', nueva_password):
            messages.error(request, "La contraseña debe contener al menos una letra mayúscula.")
            return redirect('cambiar_password')
        
        if not re.search(r'[a-z]', nueva_password):
            messages.error(request, "La contraseña debe contener al menos una letra minúscula.")
            return redirect('cambiar_password')
        
        if not re.search(r'[0-9]', nueva_password):
            messages.error(request, "La contraseña debe contener al menos un número.")
            return redirect('cambiar_password')
        
        if not re.search(r'[!@#$%&*(),.?":{}|<>]', nueva_password):
            messages.error(request, "La contraseña debe contener al menos un carácter especial.")
            return redirect('cambiar_password')

        # Cambiar contraseña
        request.user.set_password(nueva_password)
        request.user.save()
        
        # RQ-USR-04: Desmarcar flag de cambio obligatorio
        if perfil and perfil.debe_cambiar_clave:
            perfil.debe_cambiar_clave = False
            perfil.save()
        
        messages.success(request, "Tu contraseña ha sido cambiada exitosamente. Por favor, inicia sesión nuevamente.")
        logout(request)
        return redirect('login')

    return render(request, 'autenticacion/cambiar_password.html', {
        'es_cambio_obligatorio': es_cambio_obligatorio
    })

# ------------------------------
# Cerrar sesión
# ------------------------------
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

