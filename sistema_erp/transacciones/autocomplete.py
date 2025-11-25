from dal import autocomplete
from .models import Bodega

class BodegaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.q:
            return Bodega.objects.none()

        # Busca bodegas cuyo nombre contenga el texto ingresado
        qs = Bodega.objects.filter(nombre__icontains=self.q)
        return qs