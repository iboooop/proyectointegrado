from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError
from .models import MovimientoInventario, Bodega

# --- AÑADE ESTE DICCIONARIO QUE FALTA ---
WIDGETS_MOVIMIENTO = {
    'producto': autocomplete.ModelSelect2(
        url='producto-autocomplete',
        attrs={
            'data-placeholder': 'Busca un producto por nombre o SKU...',
            'data-html': True,
        }
    ),
    'proveedor': autocomplete.ModelSelect2(
        url='proveedor-autocomplete',
        attrs={'data-placeholder': 'Busca un proveedor por nombre...'}
    ),
    'bodega_origen': autocomplete.ModelSelect2(
        url='bodega-autocomplete',
        attrs={'data-placeholder': 'Busca una bodega...'}
    ),
    'bodega_destino': autocomplete.ModelSelect2(
        url='bodega-autocomplete',
        attrs={'data-placeholder': 'Busca una bodega...'}
    ),
    # --- AÑADE ESTE WIDGET PARA EL CAMPO DE FECHA ---
    'fecha_vencimiento': forms.DateInput(
        attrs={
            'type': 'date',
        }
    ),
    # --- FIN DE LA ADICIÓN ---
}
# --- FIN DE LA ADICIÓN ---

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        exclude = ['usuario', 'perfil', 'fecha_activacion', 'fecha_desactivacion']
        widgets = WIDGETS_MOVIMIENTO

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- REEMPLAZA EL BLOQUE DE ESTILOS ANTERIOR POR ESTE ---
        for field_name, field in self.fields.items():
            widget = field.widget
            # No aplicar clases a los widgets de autocompletado (Select2)
            if 'autocomplete' in str(type(widget)).lower():
                continue

            # Aplicar 'form-select' a los campos de selección (dropdowns)
            if isinstance(widget, forms.Select):
                widget.attrs.update({'class': 'form-select'})
            # Aplicar 'form-control' al resto de campos (texto, número, fecha, etc.)
            else:
                widget.attrs.update({'class': 'form-control'})
        # --- FIN DEL REEMPLAZO ---

        # Filtrar solo bodegas activas para los selects
        self.fields['bodega_origen'].queryset = Bodega.objects.filter(estado='ACTIVO')
        self.fields['bodega_destino'].queryset = Bodega.objects.filter(estado='ACTIVO')
        
        # Agregar clase is-invalid a campos con errores
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                widget_attrs = field.widget.attrs
                current_class = widget_attrs.get('class', '')
                widget_attrs['class'] = f"{current_class} is-invalid".strip()
        
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
        if 'bodega_origen' in self.fields:
            self.fields['bodega_origen'].label = 'Bodega origen'
        if 'bodega_destino' in self.fields:
            self.fields['bodega_destino'].label = 'Bodega destino'
            self.fields['bodega_destino'].required = False
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

        from django.utils import timezone
        ahora = timezone.now()

        if fecha < ahora:
            raise ValidationError("La fecha del movimiento no puede ser anterior a la fecha y hora actual.")
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
    
    def clean_bodega_origen(self):
        bodega_origen = self.cleaned_data.get("bodega_origen")
        if not bodega_origen:
            raise ValidationError("Debes seleccionar una bodega de origen.")
        if bodega_origen.estado != 'ACTIVO':
            raise ValidationError("La bodega de origen debe estar activa.")
        return bodega_origen

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

        tipo = cleaned.get("tipo")
        bodega_origen = cleaned.get("bodega_origen")
        bodega_destino = cleaned.get("bodega_destino")
        
        # Validación para transferencias
        if tipo == 'TRANSFERENCIA':
            if not bodega_destino:
                self.add_error("bodega_destino", "Para transferencias debes especificar la bodega de destino.")
            elif bodega_origen and bodega_destino and bodega_origen.id == bodega_destino.id:
                self.add_error("bodega_destino", "La bodega de destino no puede ser la misma que la bodega de origen.")
            if bodega_destino and bodega_destino.estado != 'ACTIVO':
                self.add_error("bodega_destino", "La bodega de destino debe estar activa.")
        
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


# --- AÑADE ESTA CLASE AL FINAL DEL ARCHIVO ---
class MovimientoInventarioEditForm(MovimientoInventarioForm):
    """
    Formulario para editar un movimiento. Hereda la configuración del formulario
    de creación, pero ajusta la validación de la fecha.
    """
    class Meta(MovimientoInventarioForm.Meta):
        # Hereda los widgets y exclusiones del padre.
        # No es necesario redefinir nada aquí si es igual.
        pass

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if not fecha:
            raise ValidationError("Debes ingresar la fecha del movimiento.")
        # En la edición, no validamos que la fecha sea futura. Simplemente la retornamos.
        return fecha