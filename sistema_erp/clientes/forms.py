from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

from .models import Cliente


RUT_REGEX = re.compile(r'^\d{7,8}-?[0-9kK]$')
PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')  # aceptamos prefijo opcional + y entre 7-15 dígitos


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nombre",
            "rut",
            "direccion",
            "telefono",
            "email",
            "estadoCondicion",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "rut": forms.TextInput(attrs={"class": "form-control", "placeholder": "12345678-9"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "+569XXXXXXXX"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}),
            "estadoCondicion": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise ValidationError("El nombre es obligatorio.")
        if len(nombre) < 2:
            raise ValidationError("El nombre es demasiado corto.")
        return nombre

    def clean_rut(self):
        rut = (self.cleaned_data.get("rut") or "").strip()
        if not rut:
            raise ValidationError("El RUT es obligatorio.")
        # Normalizar (quitar puntos y espacios)
        rut_norm = rut.replace(".", "").replace(" ", "")
        rut_norm = rut_norm.upper()
        # Validar formato básico (ej. 12345678-9 o 123456789)
        if not RUT_REGEX.match(rut_norm):
            raise ValidationError("Formato de RUT inválido. Ej: 12345678-9")
        # Guardar en formato sin puntos y con guión
        if "-" not in rut_norm:
            # se asume último carácter es dígito verificador
            rut_norm = rut_norm[:-1] + "-" + rut_norm[-1]
        # Comprobar unicidad
        qs = Cliente.objects.filter(rut=rut_norm)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un cliente con ese RUT.")
        return rut_norm

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise ValidationError("El email es obligatorio.")
        # Validación sintáctica
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Email con formato inválido.")
        # Unicidad (opcional pero recomendable)
        qs = Cliente.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un cliente registrado con ese email.")
        return email.lower()

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        if not telefono:
            # podrías hacer obligatorio si lo deseas; según el modelo está requerido
            raise ValidationError("El teléfono es obligatorio.")
        if not PHONE_REGEX.match(telefono):
            raise ValidationError("Teléfono inválido. Use sólo dígitos, opcional prefijo + y entre 7 y 15 dígitos.")
        return telefono

    def clean(self):
        # Aquí puedes añadir validaciones cruzadas si es necesario (por ejemplo verificar consistencia entre campos)
        cleaned = super().clean()
        return cleaned