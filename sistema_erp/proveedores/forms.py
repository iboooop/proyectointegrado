import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'rut', 'razon_social', 'nombre_fantasia', 'correo', 'telefono', 
            'sitio_web', 'direccion', 'ciudad', 'pais', 'plazo_pago', 'moneda', 
            'descuento', 'proveedor_preferente', 'lead_time', 'observaciones'
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese nombre del proveedor"}),
            "rut": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 12.345.678-K"}),
            "razon_social": forms.TextInput(attrs={"class": "form-control", "placeholder": "Razón Social Ltda."}),
            "nombre_fantasia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de Fantasía"}),
            "contacto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del contacto principal"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: +56912345678"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Dirección comercial"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "pais": forms.Select(attrs={"class": "form-select"}),
            "moneda": forms.Select(attrs={"class": "form-select"}),
            "plazo_pago": forms.Select(attrs={"class": "form-select"}),
            "descuento": forms.NumberInput(attrs={"class": "form-control"}),
            "proveedor_preferente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "lead_time": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise ValidationError("Este campo es requerido.")
        if len(nombre) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        return nombre

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            raise ValidationError("Este campo es requerido.")

        # 1. Validación de formato con Expresión Regular (Regex)
        #    Formato: XX.XXX.XXX-Y donde Y es un dígito o K/k
        pattern = r'^\d{2}\.\d{3}\.\d{3}-[\dkK]$'
        if not re.match(pattern, rut):
            raise ValidationError("El formato del RUT debe ser XX.XXX.XXX-K (ej: 12.345.678-K).")

        # 2. Validación de unicidad
        #    self.instance.pk existe si estamos editando un proveedor.
        #    Si estamos creando (self.instance.pk es None), buscamos cualquier proveedor con ese RUT.
        #    Si estamos editando, buscamos proveedores con ese RUT que NO sean el que estamos editando.
        query = Proveedor.objects.filter(rut__iexact=rut)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise ValidationError("Ya existe un proveedor con este RUT en la base de datos.")

        return rut.upper() # Guardar siempre el RUT en mayúsculas

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
