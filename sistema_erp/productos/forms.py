from django import forms
from django.core.exceptions import ValidationError
from .models import Producto, CategoriaProducto
from proveedores.models import Proveedor

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "sku",
            "ean_upc",
            "nombre",
            "descripcion",
            "categoria",
            "marca",
            "modelo",
            "uom_compra",
            "uom_venta",
            "factor_conversion",
            "costo_estandar",
            "precio_venta",
            "impuesto_iva",
            "stock_minimo",
            "stock_maximo",
            "punto_reorden",
            "perishable",
            "control_por_lote",
            "control_por_serie",
            "proveedor",
            "imagen",          
            "imagen_url",
            "ficha_tecnica_url",
            "activo",
        ]
        widgets = {
            "sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 16,
                    "placeholder": "SKU único",
                }
            ),
            "ean_upc": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 13,
                    "placeholder": "EAN (13) o UPC (12)",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 255,
                    "placeholder": "Nombre del producto",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "maxlength": 255,
                    "placeholder": "Descripción (opcional)",
                }
            ),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "marca": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 100,
                    "placeholder": "Marca (opcional)",
                }
            ),
            "modelo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 100,
                    "placeholder": "Modelo (opcional)",
                }
            ),
            "uom_compra": forms.Select(attrs={"class": "form-select"}),
            "uom_venta": forms.Select(attrs={"class": "form-select"}),
            "factor_conversion": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "step": "0.001"}
            ),
            "costo_estandar": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01"}
            ),
            "precio_venta": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01"}
            ),
            "impuesto_iva": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01"}
            ),
            "stock_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "stock_maximo": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "punto_reorden": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "perishable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "control_por_lote": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "control_por_serie": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "imagen_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "ficha_tecnica_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    # --------- Validaciones ---------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categoria_obj = None

        # Si viene categoría en datos de formulario (POST/GET)
        cat_codigo = self.data.get("categoria") if self.data else None
        if cat_codigo:
            categoria_obj = CategoriaProducto.objects.filter(codigo=cat_codigo).first()
        elif self.instance and getattr(self.instance, "categoria", None):
            categoria_obj = CategoriaProducto.objects.filter(codigo=self.instance.categoria).first()

        if categoria_obj:
            self.fields["proveedor"].queryset = Proveedor.objects.filter(
                categorias=categoria_obj,
                estado="ACTIVO",
            ).distinct()
        else:
            # Sin categoría elegida, no mostramos proveedores todavía
            self.fields["proveedor"].queryset = Proveedor.objects.none()

    def clean_sku(self):
        sku = self.cleaned_data["sku"]
        if not sku:
            raise ValidationError("El SKU es obligatorio.")
        if len(sku) > 16:
            raise ValidationError("El SKU no puede superar los 16 caracteres.")
        if not sku.isalnum():
            raise ValidationError("El SKU solo puede contener letras y números.")
        if Producto.objects.filter(sku=sku).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise ValidationError("El SKU ingresado ya existe. Debe ser único.")
        return sku

    def clean_ean_upc(self):
        ean_upc = self.cleaned_data.get("ean_upc", "")
        if ean_upc:
            if not ean_upc.isdigit():
                raise ValidationError("El EAN/UPC solo puede contener números.")
            if len(ean_upc) not in [12, 13]:
                raise ValidationError("El EAN debe tener 13 dígitos o el UPC 12 dígitos.")
            if Producto.objects.filter(ean_upc=ean_upc).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists():
                raise ValidationError("El EAN/UPC ingresado ya existe. Debe ser único.")
        return ean_upc

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre or len(nombre) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        if len(nombre) > 255:
            raise ValidationError("El nombre no puede superar los 255 caracteres.")
        import re
        # Permitir letras (incluye acentos y Ñ), números y espacios
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$', nombre):
            raise ValidationError("Ingrese solo letras, números y espacios en el nombre.")
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion", "")
        if descripcion and len(descripcion) > 255:
            raise ValidationError("La descripción no puede superar los 255 caracteres.")
        return descripcion

    def clean_marca(self):
        marca = self.cleaned_data.get("marca", "").strip()
        if marca and len(marca) < 3:
            raise ValidationError("La marca debe tener al menos 3 letras.")
        return marca

    def clean_modelo(self):
        modelo = self.cleaned_data.get("modelo", "").strip()
        if modelo and len(modelo) < 3:
            raise ValidationError("El modelo debe tener al menos 3 letras.")
        return modelo

    def clean_categoria(self):
        categoria = self.cleaned_data["categoria"]
        if not categoria:
            raise ValidationError("Debes seleccionar una categoría.")
        return categoria

    def clean_uom_compra(self):
        uom = self.cleaned_data["uom_compra"]
        if not uom:
            raise ValidationError("Debes seleccionar la unidad de compra.")
        return uom

    def clean_uom_venta(self):
        uom = self.cleaned_data["uom_venta"]
        if not uom:
            raise ValidationError("Debes seleccionar la unidad de venta.")
        return uom

    def clean_factor_conversion(self):
        factor = self.cleaned_data["factor_conversion"]
        if factor is None or factor <= 0:
            raise ValidationError("El factor de conversión debe ser mayor a 0.")
        return factor

    def clean_costo_estandar(self):
        costo = self.cleaned_data.get("costo_estandar")
        if costo is not None and costo < 0:
            raise ValidationError("El costo estándar no puede ser negativo.")
        return costo

    def clean_precio_venta(self):
        precio = self.cleaned_data.get("precio_venta")
        if precio is not None and precio < 0:
            raise ValidationError("El precio de venta no puede ser negativo.")
        return precio

    def clean_impuesto_iva(self):
        iva = self.cleaned_data["impuesto_iva"]
        if iva is None or iva < 0 or iva > 100:
            raise ValidationError("El IVA debe estar entre 0 y 100.")
        return iva

    def clean_stock_minimo(self):
        stock_minimo = self.cleaned_data["stock_minimo"]
        if stock_minimo is None or stock_minimo < 0:
            raise ValidationError("El stock mínimo no puede ser negativo.")
        return stock_minimo

    def clean_stock_maximo(self):
        stock_maximo = self.cleaned_data.get("stock_maximo")
        if stock_maximo is not None and stock_maximo < 0:
            raise ValidationError("El stock máximo no puede ser negativo.")
        return stock_maximo

    def clean_punto_reorden(self):
        punto = self.cleaned_data.get("punto_reorden")
        if punto is not None and punto < 0:
            raise ValidationError("El punto de reorden no puede ser negativo.")
        return punto

    def clean(self):
        cleaned = super().clean()
        return cleaned