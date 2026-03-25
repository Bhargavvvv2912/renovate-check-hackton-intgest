from django.shortcuts import redirect
from django.urls import reverse


class ContaBloqueadaMiddleware:
    """Middleware que redireciona usuários inativos para a tela de conta bloqueada."""

    ROTAS_LIBERADAS = [
        '/usuarios/conta-bloqueada/',
        '/usuarios/logout/',
        '/usuarios/login/',
        '/usuarios/registro/',
        '/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            if request.path not in self.ROTAS_LIBERADAS:
                return redirect(reverse('usuarios:conta_bloqueada'))

        return self.get_response(request)
