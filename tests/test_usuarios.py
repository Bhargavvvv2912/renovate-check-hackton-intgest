import pytest
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, RequestFactory
from django.urls import reverse

from usuarios.forms import LoginForm, RegistroForm
from usuarios.middleware import ContaBloqueadaMiddleware


# =============================================================================
# Views — landing_page
# =============================================================================

class TestLandingPage:
    """Testes para a view landing_page."""

    def test_landing_page_anonimo_retorna_200(self, client: Client, db):
        resposta = client.get(reverse('landing'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_landing_page_logado_redireciona_dashboard(self, client_logado: Client):
        resposta = client_logado.get(reverse('landing'))
        assert resposta.status_code == 302
        assert reverse('financas:dashboard') in resposta.url


# =============================================================================
# Views — registro_view
# =============================================================================

class TestRegistroView:
    """Testes para a view registro_view."""

    def test_registro_get_retorna_200(self, client: Client, db):
        resposta = client.get(reverse('usuarios:registro'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_registro_post_valido_cria_usuario_e_redireciona(self, client: Client):
        dados = {
            'username': 'novousuario',
            'email': 'novo@email.com',
            'first_name': 'Novo',
            'password1': 'Senha@forte456',
            'password2': 'Senha@forte456',
        }
        resposta = client.post(reverse('usuarios:registro'), dados)
        assert resposta.status_code == 302
        assert reverse('financas:dashboard') in resposta.url
        assert User.objects.filter(username='novousuario').exists()

    @pytest.mark.django_db
    def test_registro_post_invalido_mostra_erros(self, client: Client):
        dados = {
            'username': '',
            'email': 'email-invalido',
            'first_name': '',
            'password1': '123',
            'password2': '456',
        }
        resposta = client.post(reverse('usuarios:registro'), dados)
        assert resposta.status_code == 200
        assert resposta.context['form'].errors

    @pytest.mark.django_db
    def test_registro_logado_redireciona_dashboard(self, client_logado: Client):
        resposta = client_logado.get(reverse('usuarios:registro'))
        assert resposta.status_code == 302
        assert reverse('financas:dashboard') in resposta.url


# =============================================================================
# Views — login_view
# =============================================================================

class TestLoginView:
    """Testes para a view login_view."""

    def test_login_get_retorna_200(self, client: Client, db):
        resposta = client.get(reverse('usuarios:login'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_login_post_valido_redireciona_dashboard(self, client: Client, usuario: User):
        dados = {
            'username': 'testuser',
            'password': 'Senha@segura123',
        }
        resposta = client.post(reverse('usuarios:login'), dados)
        assert resposta.status_code == 302
        assert reverse('financas:dashboard') in resposta.url

    @pytest.mark.django_db
    def test_login_post_invalido_mostra_erros(self, client: Client):
        dados = {
            'username': 'inexistente',
            'password': 'senhaerrada',
        }
        resposta = client.post(reverse('usuarios:login'), dados)
        assert resposta.status_code == 200
        assert resposta.context['form'].errors

    @pytest.mark.django_db
    def test_login_logado_redireciona_dashboard(self, client_logado: Client):
        resposta = client_logado.get(reverse('usuarios:login'))
        assert resposta.status_code == 302
        assert reverse('financas:dashboard') in resposta.url


# =============================================================================
# Views — logout_view
# =============================================================================

class TestLogoutView:
    """Testes para a view logout_view."""

    @pytest.mark.django_db
    def test_logout_redireciona_landing(self, client_logado: Client):
        resposta = client_logado.post(reverse('usuarios:logout'))
        assert resposta.status_code == 302
        assert reverse('landing') in resposta.url


# =============================================================================
# Views — perfil_view
# =============================================================================

class TestPerfilView:
    """Testes para a view perfil_view."""

    @pytest.mark.django_db
    def test_perfil_logado_retorna_200(self, client_logado: Client):
        resposta = client_logado.get(reverse('usuarios:perfil'))
        assert resposta.status_code == 200

    def test_perfil_anonimo_redireciona_login(self, client: Client, db):
        resposta = client.get(reverse('usuarios:perfil'))
        assert resposta.status_code == 302
        assert '/usuarios/login/' in resposta.url


# =============================================================================
# Views — conta_bloqueada_view
# =============================================================================

class TestContaBloqueadaView:
    """Testes para a view conta_bloqueada_view."""

    def test_conta_bloqueada_retorna_200(self, client: Client, db):
        resposta = client.get(reverse('usuarios:conta_bloqueada'))
        assert resposta.status_code == 200


# =============================================================================
# Views — admin_dashboard_view
# =============================================================================

class TestAdminDashboardView:
    """Testes para a view admin_dashboard_view."""

    @pytest.mark.django_db
    def test_admin_dashboard_superusuario_retorna_200(self, client_superusuario: Client):
        resposta = client_superusuario.get(reverse('usuarios:admin_dashboard'))
        assert resposta.status_code == 200
        assert 'usuarios' in resposta.context

    @pytest.mark.django_db
    def test_admin_dashboard_usuario_normal_retorna_403(self, client_logado: Client):
        resposta = client_logado.get(reverse('usuarios:admin_dashboard'))
        assert resposta.status_code == 403

    def test_admin_dashboard_anonimo_redireciona_login(self, client: Client, db):
        resposta = client.get(reverse('usuarios:admin_dashboard'))
        assert resposta.status_code == 302
        assert '/usuarios/login/' in resposta.url


# =============================================================================
# Views — admin_toggle_usuario_view
# =============================================================================

class TestAdminToggleUsuarioView:
    """Testes para a view admin_toggle_usuario_view."""

    @pytest.mark.django_db
    def test_toggle_desativa_usuario(self, client_superusuario: Client, usuario: User):
        assert usuario.is_active is True
        url = reverse('usuarios:admin_toggle_usuario', args=[usuario.id])
        resposta = client_superusuario.post(url)
        assert resposta.status_code == 302
        usuario.refresh_from_db()
        assert usuario.is_active is False

    @pytest.mark.django_db
    def test_toggle_ativa_usuario(self, client_superusuario: Client, usuario_inativo: User):
        assert usuario_inativo.is_active is False
        url = reverse('usuarios:admin_toggle_usuario', args=[usuario_inativo.id])
        resposta = client_superusuario.post(url)
        assert resposta.status_code == 302
        usuario_inativo.refresh_from_db()
        assert usuario_inativo.is_active is True

    @pytest.mark.django_db
    def test_toggle_usuario_normal_retorna_403(self, client_logado: Client, usuario: User):
        url = reverse('usuarios:admin_toggle_usuario', args=[usuario.id])
        resposta = client_logado.post(url)
        assert resposta.status_code == 403


# =============================================================================
# Middleware — ContaBloqueadaMiddleware
# =============================================================================

class TestContaBloqueadaMiddleware:
    """Testes para o middleware ContaBloqueadaMiddleware."""

    @pytest.mark.django_db
    def test_usuario_inativo_redireciona_conta_bloqueada(self, usuario_inativo: User):
        factory = RequestFactory()
        request = factory.get(reverse('usuarios:perfil'))
        request.user = usuario_inativo  # simula usuário autenticado mas inativo

        middleware = ContaBloqueadaMiddleware(lambda req: HttpResponse('OK'))
        resposta = middleware(request)
        assert resposta.status_code == 302
        assert reverse('usuarios:conta_bloqueada') in resposta.url

    @pytest.mark.django_db
    def test_usuario_ativo_acessa_normalmente(self, usuario: User):
        factory = RequestFactory()
        request = factory.get(reverse('usuarios:perfil'))
        request.user = usuario

        middleware = ContaBloqueadaMiddleware(lambda req: HttpResponse('OK'))
        resposta = middleware(request)
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_rotas_liberadas_acessiveis_por_inativo(self, usuario_inativo: User):
        factory = RequestFactory()

        rotas_liberadas = [
            reverse('landing'),
            reverse('usuarios:conta_bloqueada'),
            reverse('usuarios:logout'),
            reverse('usuarios:login'),
            reverse('usuarios:registro'),
        ]

        for rota in rotas_liberadas:
            request = factory.get(rota)
            request.user = usuario_inativo
            middleware = ContaBloqueadaMiddleware(lambda req: HttpResponse('OK'))
            resposta = middleware(request)
            # Não deve redirecionar para conta_bloqueada
            assert resposta.status_code == 200, f'Rota {rota} deveria ser liberada para inativos'


# =============================================================================
# Forms — RegistroForm
# =============================================================================

class TestRegistroForm:
    """Testes para o RegistroForm."""

    @pytest.mark.django_db
    def test_registro_form_valido(self):
        dados = {
            'username': 'formuser',
            'email': 'form@email.com',
            'first_name': 'Form',
            'password1': 'Senha@forte456',
            'password2': 'Senha@forte456',
        }
        form = RegistroForm(data=dados)
        assert form.is_valid()

    @pytest.mark.django_db
    def test_registro_form_email_duplicado(self, usuario: User):
        dados = {
            'username': 'outro',
            'email': 'testuser@email.com',  # mesmo e-mail do usuario fixture
            'first_name': 'Outro',
            'password1': 'Senha@forte456',
            'password2': 'Senha@forte456',
        }
        form = RegistroForm(data=dados)
        assert not form.is_valid()
        assert 'email' in form.errors

    @pytest.mark.django_db
    def test_registro_form_campos_obrigatorios(self):
        form = RegistroForm(data={})
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'email' in form.errors
        assert 'first_name' in form.errors
        assert 'password1' in form.errors
        assert 'password2' in form.errors


# =============================================================================
# Forms — LoginForm
# =============================================================================

class TestLoginForm:
    """Testes para o LoginForm."""

    @pytest.mark.django_db
    def test_login_form_valido(self, usuario: User):
        dados = {
            'username': 'testuser',
            'password': 'Senha@segura123',
        }
        form = LoginForm(data=dados)
        assert form.is_valid()
