from django import forms
from django.core.exceptions import ValidationError
from .models import MovimientoInventario

class MovimientoInventarioForm(forms.ModelForm):
    # Acepta el formato de input HTML5 "datetime-local" (con T)
    fecha = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'step': '60'}, format='%Y-%m-%dT%H:%M')
    )

    class Meta:
        model = MovimientoInventario
        # Solo los campos solicitados en el formulario
        fields = [
            'fecha', 'tipo', 'cantidad', 'producto', 'proveedor', 'usuario', 'perfil', 'lote', 'observaciones'
        ]
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'perfil': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas de operación, recibo, daño, etc.'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lote (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholder y etiquetas amigables
        self.fields['producto'].label = 'Producto'
        self.fields['proveedor'].label = 'Proveedor'
        self.fields['usuario'].label = 'Usuario'
        self.fields['perfil'].label = 'Perfil'
        self.fields['tipo'].label = 'Tipo'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['fecha'].label = 'Fecha'
        

    def clean_producto(self):
        producto = self.cleaned_data["producto"]
        if not producto:
            raise ValidationError("Debes seleccionar un producto.")
        return producto

    def clean_proveedor(self):
        proveedor = self.cleaned_data["proveedor"]
        # El proveedor puede ser opcional, pero puedes validar si lo necesitas
        return proveedor

    # usuario y perfil se gestionan desde el formulario (usuario requerido por defecto)

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

    # Sin validaciones condicionales del Paso 2: no se usan en el formulario

    def clean_observaciones(self):
        observaciones = self.cleaned_data["observaciones"]
        if observaciones and len(observaciones) > 500:
            raise ValidationError("Las observaciones no pueden superar los 500 caracteres.")
        return observaciones