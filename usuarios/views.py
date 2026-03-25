from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.forms import LoginForm, RegistroForm


def landing_page(request):
    """Página inicial (landing page) pública."""
    if request.user.is_authenticated:
        return redirect('financas:dashboard')
    return render(request, 'landing.html')


def registro_view(request):
    """Registro de novo usuário com login automático após criação."""
    if request.user.is_authenticated:
        return redirect('financas:dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('financas:dashboard')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """Login de usuário existente."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('usuarios:admin_dashboard')
        return redirect('financas:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            if usuario.is_superuser:
                return redirect('usuarios:admin_dashboard')
            return redirect('financas:dashboard')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """Logout e redirecionamento para a landing page. Aceita apenas POST."""
    if request.method == 'POST':
        logout(request)
    return redirect('landing')


@login_required
def perfil_view(request):
    """Exibe o perfil do usuário logado."""
    return render(request, 'usuarios/perfil.html')


def conta_bloqueada_view(request):
    """Tela informando que a conta está bloqueada."""
    return render(request, 'usuarios/conta_bloqueada.html')


@login_required
def admin_dashboard_view(request):
    """Dashboard do superusuário — lista todos os usuários."""
    if not request.user.is_superuser:
        return HttpResponseForbidden('Acesso negado.')

    usuarios = User.objects.all().order_by('username')
    total_ativos = usuarios.filter(is_active=True).count()
    total_inativos = usuarios.filter(is_active=False).count()

    contexto = {
        'usuarios': usuarios,
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
    }
    return render(request, 'usuarios/admin/dashboard.html', contexto)


@login_required
def admin_toggle_usuario_view(request, usuario_id: int):
    """Ativa ou desativa um usuário (somente superusuário, via POST)."""
    if not request.user.is_superuser:
        return HttpResponseForbidden('Acesso negado.')

    if request.method != 'POST':
        return HttpResponseForbidden('Método não permitido.')

    usuario = get_object_or_404(User, pk=usuario_id)

    # Impedir que o superusuário desative a si mesmo
    if usuario == request.user:
        return redirect('usuarios:admin_dashboard')

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])
    return redirect('usuarios:admin_dashboard')
