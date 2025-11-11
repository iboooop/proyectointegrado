from django.shortcuts import redirect
from django.urls import resolve
from django.conf import settings

EXEMPT_PATHS = {
    '/autenticacion/login/',
    '/autenticacion/registro/',
    '/autenticacion/recuperar/',
}
# Paths que empiezan por estos prefijos también se excluyen (static, media, admin)
EXEMPT_PREFIXES = (
    '/static/', '/media/', '/admin/',
)

class LoginRequiredMiddleware:
    """Redirige a login si el usuario no está autenticado.

    Se excluyen rutas de autenticación y recursos estáticos.
    El handler 404 y vistas que no requieren auth se mostrarán solo si están exentas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not request.user.is_authenticated:
            if not self._is_exempt(path):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)

    def _is_exempt(self, path: str) -> bool:
        if path in EXEMPT_PATHS:
            return True
        for prefix in EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return True
        return False
