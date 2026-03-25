import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import Client

from financas.models import Categoria, ConfiguracaoAlerta, Despesa, Orcamento, Receita


@pytest.fixture
def usuario(db) -> User:
    """Cria um usuário normal ativo para testes."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@email.com',
        password='Senha@segura123',
        first_name='Teste',
        is_active=True,
    )


@pytest.fixture
def usuario_inativo(db) -> User:
    """Cria um usuário inativo (conta bloqueada)."""
    return User.objects.create_user(
        username='inativo',
        email='inativo@email.com',
        password='Senha@segura123',
        first_name='Inativo',
        is_active=False,
    )


@pytest.fixture
def superusuario(db) -> User:
    """Cria um superusuário com acesso administrativo."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@email.com',
        password='Senha@segura123',
        first_name='Admin',
    )


@pytest.fixture
def client_logado(client: Client, usuario: User) -> Client:
    """Client autenticado com usuário normal."""
    client.login(username='testuser', password='Senha@segura123')
    return client


@pytest.fixture
def client_superusuario(client: Client, superusuario: User) -> Client:
    """Client autenticado com superusuário."""
    client.login(username='admin', password='Senha@segura123')
    return client


# ─── Fixtures do app financas ───────────────────────────────────────────────

@pytest.fixture
def outro_usuario(db) -> User:
    """Cria outro usuário para testar isolamento multi-tenant."""
    return User.objects.create_user(
        username='outrousuario',
        email='outro@email.com',
        password='Senha@segura123',
        first_name='Outro',
        is_active=True,
    )


@pytest.fixture
def categoria_receita(db, usuario) -> Categoria:
    """Cria uma categoria do tipo receita vinculada ao usuario."""
    return Categoria.objects.create(
        user=usuario,
        nome='Salário',
        tipo=Categoria.TipoCategoria.RECEITA,
    )


@pytest.fixture
def categoria_despesa(db, usuario) -> Categoria:
    """Cria uma categoria do tipo despesa vinculada ao usuario."""
    return Categoria.objects.create(
        user=usuario,
        nome='Alimentação',
        tipo=Categoria.TipoCategoria.DESPESA,
    )


@pytest.fixture
def receita(db, usuario, categoria_receita) -> Receita:
    """Cria uma receita vinculada ao usuario."""
    return Receita.objects.create(
        user=usuario,
        descricao='Salário mensal',
        valor=Decimal('5000.00'),
        data=datetime.date(2026, 3, 1),
        categoria=categoria_receita,
        origem=Receita.Origem.SALARIO,
        natureza=Receita.Natureza.FIXA,
    )


@pytest.fixture
def despesa(db, usuario, categoria_despesa) -> Despesa:
    """Cria uma despesa vinculada ao usuario."""
    return Despesa.objects.create(
        user=usuario,
        descricao='Supermercado',
        valor=Decimal('350.00'),
        data=datetime.date(2026, 3, 5),
        categoria=categoria_despesa,
        origem=Despesa.Origem.ALIMENTACAO,
        natureza=Despesa.Natureza.VARIAVEL,
    )


@pytest.fixture
def categoria_receita_outro(db, outro_usuario) -> Categoria:
    return Categoria.objects.create(user=outro_usuario, nome='Freelance', tipo=Categoria.TipoCategoria.RECEITA)


@pytest.fixture
def categoria_despesa_outro(db, outro_usuario) -> Categoria:
    return Categoria.objects.create(user=outro_usuario, nome='Transporte', tipo=Categoria.TipoCategoria.DESPESA)


@pytest.fixture
def orcamento(db, usuario) -> Orcamento:
    """Cria um orçamento mensal vinculado ao usuario."""
    return Orcamento.objects.create(
        user=usuario,
        mes=3,
        ano=2026,
        valor=Decimal('3000.00'),
    )


@pytest.fixture
def configuracao_alerta(db, usuario) -> ConfiguracaoAlerta:
    """Cria configuração de alertas com valores padrão para o usuario."""
    return ConfiguracaoAlerta.objects.create(user=usuario)
