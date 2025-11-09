from django import forms
from django.core.exceptions import ValidationError
from .models import Producto
from datetime import date

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = "__all__"
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese nombre del producto"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción del producto"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "stock_actual": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "lote": forms.TextInput(attrs={"class": "form-control", "placeholder": "Código de lote"}),
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "stock": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        if len(nombre) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        return nombre

    def clean_categoria(self):
        categoria = self.cleaned_data["categoria"]
        if not categoria:
            raise ValidationError("Debes seleccionar una categoría.")
        return categoria

    def clean_descripcion(self):
        descripcion = self.cleaned_data["descripcion"]
        if descripcion and len(descripcion) > 500:
            raise ValidationError("La descripción no puede superar los 500 caracteres.")
        return descripcion

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock_actual(self):
        stock_actual = self.cleaned_data["stock_actual"]
        if stock_actual < 0:
            raise ValidationError("El stock no puede ser negativo.")
        return stock_actual

    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data["fecha_vencimiento"]
        if fecha_vencimiento and fecha_vencimiento < date.today():
            raise ValidationError("La fecha de vencimiento no puede ser anterior a hoy.")
        return fecha_vencimiento

    def clean_lote(self):
        lote = str(self.cleaned_data.get("lote", "")).strip()

        if not lote:
            raise ValidationError("El campo Lote no puede estar en blanco.")
        if lote == "0":
            raise ValidationError("El lote no puede tener el valor 0.")
        if len(lote) > 50:
            raise ValidationError("El lote no puede superar los 50 caracteres.")
        
        return lote

    def clean_proveedor(self):
        proveedor = self.cleaned_data["proveedor"]
        if not proveedor:
            raise ValidationError("Debes seleccionar un proveedor.")
        return proveedor

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock not in dict(Producto.STOCK_CHOICES):
            raise ValidationError("El estado de stock no es válido.")
        return stock
