from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

from .models import Bodega

# Si tienes un forms.py con BodegaForm, reemplaza la definición siguiente por:
# from .forms import BodegaForm
try:
    from .forms import BodegaForm  # type: ignore
except Exception:
    class BodegaForm(forms.ModelForm):
        class Meta:
            model = Bodega
            fields = [
                "codigo",
                "nombre",
                "direccion",
                "telefono",
                "responsable",
                "capacidad_maxima",
                "tipo",
                "estado",
            ]


class BodegaListView(LoginRequiredMixin, ListView):
    model = Bodega
    template_name = "bodegas/bodega_list.html"
    context_object_name = "bodegas"
    paginate_by = 25


class BodegaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Bodega
    form_class = BodegaForm
    template_name = "bodegas/bodega_add.html"
    success_url = reverse_lazy("bodegas_list")
    success_message = "Bodega creada correctamente."


class BodegaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Bodega
    form_class = BodegaForm
    template_name = "bodegas/bodega_edit.html"
    success_url = reverse_lazy("bodegas_list")
    success_message = "Bodega actualizada correctamente."

    # Si tu URL usa otro nombre para el PK (por ejemplo 'id'), ajusta:
    # pk_url_kwarg = 'id'


class BodegaDetailView(LoginRequiredMixin, DetailView):
    model = Bodega
    template_name = "bodegas/bodega_detail.html"
    context_object_name = "bodega"
    # Igual que arriba: si tu URL usa 'id' cambia pk_url_kwarg = 'id'


class BodegaDeleteView(LoginRequiredMixin, View):
    """
    Maneja eliminación via POST (útil si usas botones o formularios sencillos en list/detail).
    Las plantillas que te pasé muestran un form POST para eliminar; esta vista acepta ese POST.
    """
    def post(self, request, pk=None, *args, **kwargs):
        # Asegúrate de que el name() en urls.py pase 'pk' o cambia a 'id' según corresponda.
        obj = get_object_or_404(Bodega, pk=pk)
        nombre = str(obj)
        obj.delete()
        messages.success(request, f'Bodega "{nombre}" eliminada correctamente.')
        return redirect(reverse_lazy("bodegas_list"))