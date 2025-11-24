from django import forms
from django.core.exceptions import ValidationError
from .models import MovimientoInventario


class MovimientoInventarioForm(forms.ModelForm):
    # Fecha y hora capturadas automáticamente, pero visibles/formateadas
    fecha = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'step': '60',
            },
            format='%Y-%m-%dT%H:%M',
        ),
        required=True,
    )

    class Meta:
        model = MovimientoInventario
        fields = [
<<<<<<< HEAD

            'fecha', 'tipo', 'cantidad', 'producto', 'proveedor', 'usuario', 'perfil', 'observaciones'

=======
            'fecha',
            'tipo',
            'estado',
            'cantidad',
            'producto',
            'proveedor',
            'bodega_origen',
            'bodega_destino',
            'manejo_lotes',
            'manejo_series',
            'perecible',
            'lote',
            'serie',
            'fecha_vencimiento',
            'doc_referencia',
            'doc_referencia_file',
            'motivo',
            'observaciones',
>>>>>>> origin/feature/production-TC
        ]

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'bodega_origen': forms.Select(attrs={'class': 'form-select'}),
            'bodega_destino': forms.Select(attrs={'class': 'form-select'}),
            'manejo_lotes': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_manejo_lotes'}),
            'manejo_series': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_manejo_series'}),
            'perecible': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_perecible'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº factura, guía, nota de crédito, orden, etc.'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diferencia inventario, devolución cliente, etc.'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas de operación, recibo, daño, etc.'}),


        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fecha'].label = 'Fecha y hora'
        self.fields['tipo'].label = 'Tipo de movimiento'
        self.fields['estado'].label = 'Estado del movimiento'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['producto'].label = 'Producto (SKU)'
        self.fields['proveedor'].label = 'Proveedor'
        self.fields['bodega_origen'].label = 'Bodega origen'
        self.fields['bodega_destino'].label = 'Bodega a transferir'
        self.fields['doc_referencia'].label = 'Documento de referencia'
        self.fields['motivo'].label = 'Motivo'

        # Captura automática de fecha/hora inicial
        if not self.initial.get('fecha') and not self.data:
            from django.utils import timezone

            now = timezone.localtime()
            self.initial['fecha'] = now.strftime('%Y-%m-%dT%H:%M')

    # ---------- Validaciones ----------
    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if not fecha:
            raise ValidationError("Debes ingresar la fecha del movimiento.")

        from datetime import date

        if fecha.date() < date.today():
            raise ValidationError("La fecha del movimiento no puede ser anterior al día de hoy.")
        return fecha

    def clean_producto(self):
        producto = self.cleaned_data.get("producto")
        if not producto:
            raise ValidationError("Debes seleccionar un producto.")
        return producto

    def clean_proveedor(self):
        proveedor = self.cleaned_data.get("proveedor")
        if not proveedor:
            raise ValidationError("Debes seleccionar un proveedor asociado al producto.")
        return proveedor

    def clean_tipo(self):
        tipo = self.cleaned_data.get("tipo")
        if tipo not in dict(MovimientoInventario.TIPO_MOVIMIENTO):
            raise ValidationError("El tipo de movimiento no es válido.")
        return tipo

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad")
        if cantidad is None or cantidad == "":
            raise ValidationError("Debes ingresar una cantidad.")
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad

    def clean_bodega(self):
        bodega = self.cleaned_data.get("bodega")
        if not bodega:
            raise ValidationError("Debes seleccionar la bodega desde donde se realiza el movimiento.")
        return bodega

    def clean_doc_referencia(self):
        doc = self.cleaned_data.get("doc_referencia", "").strip()
        if not doc:
            raise ValidationError("El documento de referencia es obligatorio.")
        return doc

    def clean_motivo(self):
        motivo = self.cleaned_data.get("motivo", "").strip()
        if not motivo:
            raise ValidationError("El motivo es obligatorio.")
        return motivo

    def clean(self):
        cleaned = super().clean()

        # Validaciones de lote/serie/fecha
        lote = cleaned.get("lote", "").strip()
        serie = cleaned.get("serie", "").strip()
        fecha_venc = cleaned.get("fecha_vencimiento")
        perecible = cleaned.get("perecible")

        if not lote:
            self.add_error("lote", "Debes ingresar el lote.")
        if not serie:
            self.add_error("serie", "Debes ingresar la serie.")
        # fecha de vencimiento solo obligatoria si es perecible
        if perecible and not fecha_venc:
            self.add_error("fecha_vencimiento", "Debes ingresar la fecha de vencimiento para productos perecibles.")

        observaciones = cleaned.get("observaciones", "")
        if observaciones and len(observaciones) > 500:
            self.add_error("observaciones", "Las observaciones no pueden superar los 500 caracteres.")

        return cleaned