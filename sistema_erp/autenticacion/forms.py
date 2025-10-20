from django import forms

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
        error_messages={
            'required': "El nombre de usuario es obligatorio.",
            'min_length': "El nombre de usuario debe tener al menos 3 caracteres.",
        }
    )
    email = forms.EmailField(
        required=True,
        label="Correo",
        error_messages={
            'required': "El correo electrónico es obligatorio.",
            'invalid': "Por favor, ingresa un correo electrónico válido.",
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Contraseña",
        min_length=6,
        error_messages={
            'required': "La contraseña es obligatoria.",
            'min_length': "La contraseña debe tener al menos 6 caracteres.",
        }
    )
    rol = forms.ChoiceField(
        choices=[('ADMIN', 'Administrador'), ('BODEGA', 'Bodega'), ('VENTAS', 'Ventas')],
        required=True,
        label="Rol",
        error_messages={
            'required': "El rol es obligatorio.",
        }
    )
    telefono = forms.CharField(
        required=False,
        label="Teléfono",
        error_messages={
            'invalid': "El teléfono debe contener solo números.",
        }
    )
    area = forms.ChoiceField(
        choices=[('Administración', 'Administración'), ('Bodega', 'Bodega'), ('Ventas', 'Ventas')],
        required=False,
        label="Área",
        error_messages={
            'invalid': "El área seleccionada no es válida.",
        }
    )

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números.")
        return telefono
