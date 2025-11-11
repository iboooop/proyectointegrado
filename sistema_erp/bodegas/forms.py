from django import forms
from django.core.exceptions import ValidationError
import re

from .models import Bodega


CODE_REGEX = re.compile(r'^[A-Z0-9\-]{3,20}$')   # letras (mayúsculas), números y guiones, 3-20 chars
PHONE_REGEX = re.compile(r'^\+?\d{6,15}$')       # aceptamos entre 6 y 15 dígitos (prefijo opcional)


class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = [
            "codigo",
            "nombre",
            "direccion",
            "telefono",
            "responsable",
            "capacidad_maxima",
            "tipo",
            "estado",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "COD-01"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la bodega"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "+56..."}),
            "responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del responsable"}),
            "capacidad_maxima": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_codigo(self):
        codigo = (self.cleaned_data.get("codigo") or "").strip().upper()
        if not codigo:
            raise ValidationError("El código es obligatorio.")
        if not CODE_REGEX.match(codigo):
            raise ValidationError("Código inválido. Use letras y números (mayúsculas) y opcional guiones, 3-20 caracteres.")
        qs = Bodega.objects.filter(codigo=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una bodega con ese código.")
        return codigo

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise ValidationError("El nombre es obligatorio.")
        if len(nombre) < 2:
            raise ValidationError("El nombre es demasiado corto.")
        return nombre

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        # En modelo telefono puede estar en blanco; lo aceptamos vacío
        if not telefono:
            return telefono
        if not PHONE_REGEX.match(telefono):
            raise ValidationError("Teléfono inválido. Use sólo dígitos, opcional prefijo + y entre 6 y 15 dígitos.")
        return telefono

    def clean_capacidad_maxima(self):
        capacidad = self.cleaned_data.get("capacidad_maxima")
        if capacidad is None:
            return 0
        try:
            capacidad = int(capacidad)
        except (TypeError, ValueError):
            raise ValidationError("Capacidad debe ser un número entero.")
        if capacidad < 0:
            raise ValidationError("Capacidad máxima no puede ser negativa.")
        return capacidad

    def clean(self):
        cleaned = super().clean()
        # ejemplo de validación cruzada:
        nombre = cleaned.get("nombre")
        responsable = cleaned.get("responsable")
        if nombre and responsable and nombre.lower() == responsable.lower():
            # solo una recomendación, no es error crítico; si prefieres quitarlo, coméntalo
            self.add_error("responsable", "El responsable no debería coincidir exactamente con el nombre de la bodega.")
        return cleaned