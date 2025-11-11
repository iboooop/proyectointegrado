from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import Perfil
import re

# ------------------ FORMULARIO USUARIO ------------------
class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la contraseña'}),
        required=False,
        label="Contraseña"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme la contraseña'}),
        required=False,
        label="Confirmar Contraseña"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese los nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese los apellidos'}),
        }

    # --- VALIDACIONES ---
    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        # Si está editando y no cambió el username, no forzar validaciones adicionales
        if self.instance.pk and username == (self.instance.username or '').strip():
            return username

        if len(username) < 3:
            raise ValidationError("El username debe tener al menos 3 caracteres.")

        # Validación estándar de Django para username
        username_validator = UnicodeUsernameValidator()
        try:
            username_validator(username)
        except ValidationError:
            raise ValidationError("El username solo puede contener letras, números y . @ + - _")

        qs = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("El username ya está en uso.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        # Si está editando y no cambió el email, no forzar validación extra
        if self.instance.pk and email.lower() == (getattr(self.instance, 'email', '') or '').lower():
            return email
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("El correo electrónico ya está registrado.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        # Si está editando y no cambió, permitir el valor tal cual
        if self.instance.pk and first_name == (self.instance.first_name or '').strip():
            return first_name
        # No permitir números en el nombre
        if re.search(r"\d", first_name or ''):
            raise ValidationError("El nombre no debe contener números.")
        if len(first_name) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        # Si está editando y no cambió, permitir el valor tal cual
        if self.instance.pk and last_name == (self.instance.last_name or '').strip():
            return last_name
        # No permitir números en el apellido
        if re.search(r"\d", last_name or ''):
            raise ValidationError("El apellido no debe contener números.")
        if len(last_name) < 3:
            raise ValidationError("El apellido debe tener al menos 3 caracteres.")
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        # Solo exigir contraseña en creación
        if not self.instance.pk and not password:
            raise ValidationError({'password': "Debe ingresar una contraseña para crear el usuario."})

        # Validaciones mínimas para cambio de contraseña (solo si se intenta cambiar)
        if password or confirm:
            if password != confirm:
                raise ValidationError({'confirm_password': "Las contraseñas no coinciden."})
            if len(password or '') < 8:
                raise ValidationError({'password': "La contraseña debe tener al menos 8 caracteres."})
            if not re.search(r'[A-Z]', password or ''):
                raise ValidationError({'password': "Debe incluir al menos una letra mayúscula."})
            if not re.search(r'[0-9]', password or ''):
                raise ValidationError({'password': "Debe incluir al menos un número."})
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            # Establecer password solo si se envió
            user.set_password(password)
        elif not self.instance.pk:
            raise ValidationError("Debe establecer una contraseña para el usuario.")

        if commit:
            user.save()
        return user


# ------------------ FORMULARIO PERFIL ------------------
class PerfilForm(forms.ModelForm):

    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Avatar (máx 2MB, JPG/PNG)"
    )
    sesiones_activas = forms.IntegerField(widget=forms.HiddenInput(), initial=0, required=False)

    class Meta:
        model = Perfil
        fields = ['telefono', 'rol', 'estado', 'mfa_habilitado', 'avatar', 'sesiones_activas']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'mfa_habilitado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if hasattr(avatar, 'content_type'):
                main, sub = avatar.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'jpg', 'png']):
                    raise ValidationError('Solo se permiten imágenes JPG o PNG.')
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('El tamaño máximo permitido es 2MB.')
        return avatar

    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if rol not in dict(Perfil.ROLES):
            raise ValidationError("El rol seleccionado no es válido.")
        return rol

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            if not telefono.isdigit():
                raise ValidationError("El teléfono debe contener solo números.")
            if not (7 <= len(telefono) <= 15):
                raise ValidationError("El teléfono debe tener entre 7 y 15 dígitos.")
        return telefono

    def clean_sesiones_activas(self):
        sesiones = self.cleaned_data.get('sesiones_activas') or 0
        if sesiones < 0:
            raise ValidationError("Las sesiones activas no pueden ser negativas.")
        return sesiones
