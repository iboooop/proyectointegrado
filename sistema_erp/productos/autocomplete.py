from dal import autocomplete
from .models import Producto
import json

class ProductoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.q:
            return Producto.objects.none()

        qs = Producto.objects.filter(nombre__icontains=self.q)
        return qs

    def get_result_label(self, item):
        # Usamos el nombre de campo correcto del modelo: 'perishable'
        return f"{item.nombre}##{json.dumps(item.perishable)}"

    def get_results(self, context):
        """
        Sobrescribimos este método para procesar el dato extra.
        """
        return [
            {
                'id': self.get_result_value(result),
                'text': self.get_result_label(result).split('##')[0],
                # Renombramos la clave a 'es_perecible' para que coincida con el JavaScript
                'es_perecible': json.loads(self.get_result_label(result).split('##')[1]),
            }
            for result in context['object_list']
        ]