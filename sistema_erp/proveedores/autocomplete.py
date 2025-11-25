from dal import autocomplete
from .models import Proveedor

class ProveedorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.q:
            return Proveedor.objects.none()

        # Busca proveedores cuyo nombre contenga el texto ingresado
        qs = Proveedor.objects.filter(nombre__icontains=self.q)
        return qs