from django import forms
import re

class LoginForm(forms.Form):
    usuario_o_email = forms.CharField(max_length=150, required=True, label="Usuario o correo")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    recordarme = forms.BooleanField(required=False, label="Recordarme")


class RegistroForm(forms.Form):
    usuario = forms.CharField(
        max_length=150,
        required=True,
        label="Usuario",
        min_length=3,
        initial="",
        error_messages={
            'required': "El nombre de usuario es obligatorio.",
            'min_length': "El nombre de usuario debe tener al menos 3 caracteres.",
        }
    )
    email = forms.EmailField(
        required=True,
        label="Correo",
        initial="",
        error_messages={
            'required': "El correo electrónico es obligatorio.",
            'invalid': "Por favor, ingresa un correo electrónico válido.",
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Contraseña",
        initial="",
        min_length=8,
        error_messages={
            'required': "La contraseña es obligatoria.",
            'min_length': "La contraseña debe tener al menos 8 caracteres.",
        }
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Confirmar contraseña",
        initial="",
        error_messages={
            'required': "Debes confirmar la contraseña.",
        }
    )
    rol = forms.ChoiceField(
        choices=[('ADMIN', 'Administrador'), ('BODEGA', 'Bodega'), ('VENTAS', 'Ventas')],
        required=True,
        label="Rol",
        initial="",
        error_messages={
            'required': "El rol es obligatorio.",
        }
    )
    telefono = forms.CharField(
        required=False,
        label="Teléfono",
        initial="",
        error_messages={
            'invalid': "El teléfono debe contener solo números.",
        }
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Validar que la contraseña tenga al menos un número, una letra mayúscula y un carácter especial
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("La contraseña debe contener al menos un carácter especial.")
        return password

    def clean_confirmar_password(self):
        password = self.cleaned_data.get('password')
        confirmar_password = self.cleaned_data.get('confirmar_password')
        if password and confirmar_password and password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return confirmar_password

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solo números.")
            if len(telefono) != 9:  
                raise forms.ValidationError("El teléfono debe tener exactamente 9 dígitos.")
        return telefono