from django import forms
from django.core.exceptions import ValidationError
from .models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = "__all__"

    def clean_usuario(self):
        usuario = self.cleaned_data["usuario"]
        if not usuario:
            raise ValidationError("Debes seleccionar un usuario.")
        return usuario

    def clean_rol(self):
        rol = self.cleaned_data["rol"]
        if rol not in dict(Perfil.ROLES):
            raise ValidationError("El rol seleccionado no es válido.")
        return rol

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"]
        if telefono and (len(telefono) < 7 or len(telefono) > 15):
            raise ValidationError("El teléfono debe tener entre 7 y 15 dígitos.")
        return telefono

    def clean_area(self):
        area = self.cleaned_data["area"]
        if area and len(area) > 50:
            raise ValidationError("El área no puede superar los 50 caracteres.")
        return area