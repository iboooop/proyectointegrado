from django import forms
from django.core.exceptions import ValidationError
from .models import MovimientoInventario

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = "__all__"

    def clean_producto(self):
        producto = self.cleaned_data["producto"]
        if not producto:
            raise ValidationError("Debes seleccionar un producto.")
        return producto

    def clean_proveedor(self):
        proveedor = self.cleaned_data["proveedor"]
        # El proveedor puede ser opcional, pero puedes validar si lo necesitas
        return proveedor

    def clean_usuario(self):
        usuario = self.cleaned_data["usuario"]
        if not usuario:
            raise ValidationError("Debes seleccionar un usuario.")
        return usuario

    def clean_perfil(self):
        perfil = self.cleaned_data["perfil"]
        # El perfil puede ser opcional, pero puedes validar si lo necesitas
        return perfil

    def clean_tipo(self):
        tipo = self.cleaned_data["tipo"]
        if tipo not in dict(MovimientoInventario.TIPO_MOVIMIENTO):
            raise ValidationError("El tipo de movimiento no es válido.")
        return tipo

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad is None or cantidad == "":
            raise ValidationError("Debes ingresar una cantidad.")
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad

    def clean_observaciones(self):
        observaciones = self.cleaned_data["observaciones"]
        if observaciones and len(observaciones) > 500:
            raise ValidationError("Las observaciones no pueden superar los 500 caracteres.")
        return observaciones