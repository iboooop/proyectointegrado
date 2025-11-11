from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

from .models import Cliente

# Si tienes un forms.py con ClienteForm, reemplaza la definición siguiente por:
# from .forms import ClienteForm
try:
    from .forms import ClienteForm  # type: ignore
except Exception:
    class ClienteForm(forms.ModelForm):
        class Meta:
            model = Cliente
            fields = [
                "nombre",
                "rut",
                "direccion",
                "telefono",
                "email",
                "estadoCondicion",
            ]


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 25


class ClienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_add.html"
    success_message = "Cliente creado correctamente."

    def get_success_url(self):
        return reverse('clientes:clientes_detail', args=[self.object.pk])


class ClienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_edit.html"
    success_message = "Cliente actualizado correctamente."

    def get_success_url(self):
        return reverse('clientes:clientes_detail', args=[self.object.pk])


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"


class ClienteDeleteView(LoginRequiredMixin, View):
    """
    Eliminación via POST. Las plantillas usan formularios sencillos con method="post".
    """
    def post(self, request, pk=None, *args, **kwargs):
        cliente = get_object_or_404(Cliente, pk=pk)
        nombre = str(cliente)
        cliente.delete()
        messages.success(request, f'Cliente "{nombre}" eliminado correctamente.')
        return redirect('clientes:clientes_list')