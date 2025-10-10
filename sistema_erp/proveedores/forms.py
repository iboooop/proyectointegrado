from django import forms
from django.core.exceptions import ValidationError
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        if len(nombre) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        return nombre

    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        if len(rut) < 8 or len(rut) > 12:
            raise ValidationError("El RUT debe tener entre 8 y 12 caracteres.")
        return rut

    def clean_contacto(self):
        contacto = self.cleaned_data["contacto"]
        if len(contacto) < 3:
            raise ValidationError("El contacto debe tener al menos 3 caracteres.")
        return contacto

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"]
        if telefono and (len(telefono) < 7 or len(telefono) > 15):
            raise ValidationError("El teléfono debe tener entre 7 y 15 dígitos.")
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data["correo"]
        if correo and "@" not in correo:
            raise ValidationError("Ingrese un correo electrónico válido.")
        return correo

    def clean_direccion(self):
        direccion = self.cleaned_data["direccion"]
        if direccion and len(direccion) > 200:
            raise ValidationError("La dirección no puede superar los 200 caracteres.")
        return direccion

    def clean_estado(self):
        estado = self.cleaned_data["estado"]
        if estado not in dict(Proveedor.ESTADO_CHOICES):
            raise ValidationError("El estado seleccionado no es válido.")
        return estado