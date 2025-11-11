from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.db.models import Q
import openpyxl
from django.http import HttpResponse
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

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(rut__icontains=q) |
                Q(telefono__icontains=q) |
                Q(email__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['page_size'] = int(self.request.GET.get('page_size', self.paginate_by))
        context['page_sizes'] = [5, 10, 25, 50, 100]
        context['sort'] = self.request.GET.get('sort', '')
        context['dir'] = self.request.GET.get('dir', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        request = self.request
        if request.GET.get('partial') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.response_class(
                request=request,
                template='clientes/partials/cliente_table.html',
                context=context,
                using=self.template_engine,
                **response_kwargs
            )
        return super().render_to_response(context, **response_kwargs)


class ClienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_add.html"
    success_url = reverse_lazy("clientes_list")
    success_message = "Cliente creado correctamente."


class ClienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_edit.html"
    success_url = reverse_lazy("clientes_list")
    success_message = "Cliente actualizado correctamente."

    # Si tu URL usa otro nombre para el PK (por ejemplo 'id'), ajusta:
    # pk_url_kwarg = 'id'


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
        return redirect(reverse_lazy("clientes_list"))
    

def clientes_export(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clientes"
    ws.append(['ID', 'Nombre', 'RUT', 'Teléfono', 'Email', 'Fecha creación'])

    # Filtro igual que en la lista
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q) |
            Q(rut__icontains=q) |
            Q(telefono__icontains=q) |
            Q(email__icontains=q)
        )

    for c in clientes:
        ws.append([
            c.pk,
            c.nombre,
            c.rut,
            c.telefono,
            c.email,
            c.fecha_creacion.strftime('%d/%m/%Y %H:%M') if c.fecha_creacion else ''
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=clientes.xlsx'
    wb.save(response)
    return response