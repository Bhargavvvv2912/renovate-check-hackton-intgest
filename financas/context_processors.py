from financas.services import obter_todos_alertas


def alertas_context(request):
    """Injeta alertas do usuário em todos os templates."""
    if request.user.is_authenticated:
        return {'alertas': obter_todos_alertas(request.user)}
    return {}
