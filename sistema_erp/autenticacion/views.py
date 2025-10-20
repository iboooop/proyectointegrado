from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import LoginForm, RegistroForm
from django.contrib import messages  

# Lista simulada de usuarios
USUARIOS_SIMULADOS = [
    {"usuario": "admin", "email": "admin@example.com", "password": "admin123", "rol": "ADMIN"},
    {"usuario": "bodega1", "email": "bodega1@example.com", "password": "bodega123", "rol": "BODEGA"},
    {"usuario": "ventas1", "email": "ventas1@example.com", "password": "ventas123", "rol": "VENTAS"},
]

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            rol = form.cleaned_data['rol']
            telefono = form.cleaned_data.get('telefono')
            area = form.cleaned_data.get('area')

            # Verificar duplicados en la lista simulada
            if any(u["usuario"] == usuario or u["email"] == email for u in USUARIOS_SIMULADOS):
                messages.error(request, "El usuario o email ya existe.")
                return redirect('registro')

            # Agregar usuario a la lista simulada
            USUARIOS_SIMULADOS.append({
                "usuario": usuario,
                "email": email,
                "password": password,
                "rol": rol,
                "telefono": telefono,
                "area": area,
            })
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('registro')
        else:
            # Capturar errores del formulario y convertirlos en mensajes flash
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = RegistroForm()
    return render(request, 'autenticacion/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario_o_email = form.cleaned_data['usuario_o_email']
            password = form.cleaned_data['password']
            # Validar credenciales en la lista simulada
            for usuario in USUARIOS_SIMULADOS:
                if (usuario["usuario"] == usuario_o_email or usuario["email"] == usuario_o_email) and usuario["password"] == password:
                    request.session['usuario'] = usuario["usuario"]
                    request.session['rol'] = usuario["rol"]
                    return redirect('dashboard')  # Redirigir al dashboard
            # Mostrar mensaje flash si las credenciales son inválidas
            messages.error(request, "Credenciales inválidas. Por favor, inténtalo de nuevo.")
        else:
            messages.error(request, "Por favor, completa todos los campos correctamente.")
    else:
        form = LoginForm()
    return render(request, 'autenticacion/login.html', {'form': form})

def recuperar_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Validar email en la lista simulada
        for usuario in USUARIOS_SIMULADOS:
            if usuario["email"] == email:
                messages.success(request, f"Se ha enviado un enlace de recuperación a {email}")
                return redirect('recuperar_password')  # Redirigir para mostrar el mensaje
        messages.error(request, "El email no está registrado")
        return redirect('recuperar_password')  # Redirigir para mostrar el mensaje
    return render(request, 'autenticacion/recuperar_password.html')

def dashboard_view(request):
    usuario = request.session.get('usuario')
    rol = request.session.get('rol')
    if not usuario or not rol:
        return redirect('login')  # Redirigir al login si no hay sesión
    return render(request, 'autenticacion/dashboard.html', {'usuario': usuario, 'rol': rol})