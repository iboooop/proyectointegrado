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
        # Excluimos usuario y perfil; se asignan en la vista al guardar
        fields = [
            'fecha', 'tipo', 'cantidad', 'producto', 'proveedor', 'bodega',
            'manejo_lotes', 'lote', 'manejo_series', 'serie', 'perecible', 'fecha_vencimiento',
            'doc_referencia', 'motivo', 'observaciones'
        ]
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'bodega': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'manejo_lotes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manejo_series': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'perecible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lote'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serie'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OC-123 / FAC-456 / GUIA-789'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diferencia inventario, devolución cliente, etc.'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas de operación, recibo, daño, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholder y etiquetas amigables
        self.fields['producto'].label = 'Producto'
        self.fields['proveedor'].label = 'Proveedor'
        if 'bodega' in self.fields:
            self.fields['bodega'].label = 'Bodega'
        self.fields['tipo'].label = 'Tipo'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['fecha'].label = 'Fecha'
        self.fields['manejo_lotes'].label = 'manejo por lotes'
        self.fields['manejo_series'].label = 'manejo por series'
        self.fields['perecible'].label = 'perecible (vencimiento)'
        self.fields['doc_referencia'].label = 'doc_referencia'
        self.fields['motivo'].label = 'motivo (ajustes/devoluciones)'

    def clean_producto(self):
        producto = self.cleaned_data["producto"]
        if not producto:
            raise ValidationError("Debes seleccionar un producto.")
        return producto

    def clean_proveedor(self):
        proveedor = self.cleaned_data["proveedor"]
        # El proveedor puede ser opcional, pero puedes validar si lo necesitas
        return proveedor

    # usuario y perfil no se validan aquí; se asignan en la vista

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

    def clean(self):
        cleaned = super().clean()
        manejo_lotes = cleaned.get('manejo_lotes')
        manejo_series = cleaned.get('manejo_series')
        perecible = cleaned.get('perecible')

        lote = cleaned.get('lote')
        serie = cleaned.get('serie')
        fecha_venc = cleaned.get('fecha_vencimiento')

        # Requerimientos condicionales
        if manejo_lotes and not lote:
            self.add_error('lote', 'Debes indicar el lote cuando el manejo por lotes está activo.')
        if not manejo_lotes:
            cleaned['lote'] = ''

        if manejo_series and not serie:
            self.add_error('serie', 'Debes indicar la serie cuando el manejo por series está activo.')
        if not manejo_series:
            cleaned['serie'] = ''

        if perecible and not fecha_venc:
            self.add_error('fecha_vencimiento', 'Debes indicar la fecha de vencimiento cuando es perecible.')
        if not perecible:
            cleaned['fecha_vencimiento'] = None

        return cleaned

    def clean_observaciones(self):
        observaciones = self.cleaned_data["observaciones"]
        if observaciones and len(observaciones) > 500:
            raise ValidationError("Las observaciones no pueden superar los 500 caracteres.")
        return observaciones