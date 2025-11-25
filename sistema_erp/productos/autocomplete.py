from dal import autocomplete
from .models import Producto

class ProductoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # No filtrar si el usuario no ha escrito nada
        if not self.q:
            return Producto.objects.none()

        qs = Producto.objects.all()

        # Filtrar por nombre o código
        qs = qs.filter(nombre__icontains=self.q)
        
        return qs