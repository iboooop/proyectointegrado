from django import forms
from django.core.exceptions import ValidationError
from .models import MovimientoInventario

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = [
            'producto', 'proveedor', 'fecha', 'estado', 'tipo',
            'cantidad', 'lote', 'serie', 'fecha_vencimiento', 'doc_referencia',
            'doc_referencia_file', 'motivo', 'observaciones'
        ]
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'doc_referencia_file': forms.FileInput(attrs={'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # etiquetas y campos de bodegas eliminados (app 'bodegas' removida)

        # Asegurarse de que los campos referenciados existan en el form antes de ajustar labels
        if 'fecha' in self.fields:
            self.fields['fecha'].label = 'Fecha y hora'
        if 'tipo' in self.fields:
            self.fields['tipo'].label = 'Tipo de movimiento'
        if 'estado' in self.fields:
            self.fields['estado'].label = 'Estado del movimiento'
        if 'cantidad' in self.fields:
            self.fields['cantidad'].label = 'Cantidad'
        if 'producto' in self.fields:
            self.fields['producto'].label = 'Producto (SKU)'
        if 'proveedor' in self.fields:
            self.fields['proveedor'].label = 'Proveedor'
        if 'doc_referencia' in self.fields:
            self.fields['doc_referencia'].label = 'Documento de referencia'
        if 'motivo' in self.fields:
            self.fields['motivo'].label = 'Motivo'

        # Captura automática de fecha/hora inicial
        if 'fecha' in self.fields and not self.initial.get('fecha') and not self.data:
            from django.utils import timezone
            now = timezone.localtime()
            # widget datetime-local espera formato 'YYYY-MM-DDTHH:MM'
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