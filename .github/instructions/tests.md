# Instruções — Estratégia de Testes

## Framework
- **pytest** + **pytest-django** como runner principal.
- Django TestCase para testes que precisam de transações.
- Fixtures do pytest para setup reutilizável.

## Estrutura de Testes
```
tests/
├── conftest.py            ← Fixtures globais (usuário, categorias, etc.)
├── test_models.py         ← Testes de models (validações, __str__, etc.)
├── test_views.py          ← Testes de views (status codes, redirecionamentos)
├── test_forms.py          ← Testes de formulários (validação, clean)
├── test_services.py       ← Testes de lógica de negócio
└── test_filters.py        ← Testes de filtros e buscas
```

## Cobertura Mínima
- **Models**: criação, validação, `__str__`, relacionamentos.
- **Views**: autenticação requerida, GET/POST, redirecionamentos.
- **Forms**: validação de campos obrigatórios, regras de negócio.
- **Services**: cálculo de saldo, agregações, exportações.
- **Isolamento**: garantir que usuário A não vê dados do usuário B.

## Fixtures Padrão (conftest.py)
```python
@pytest.fixture
def usuario(db):
    """Cria um usuário padrão para testes."""
    ...

@pytest.fixture
def usuario_inativo(db):
    """Cria um usuário inativo para testar bloqueio."""
    ...

@pytest.fixture
def superusuario(db):
    """Cria um superusuário para testes admin."""
    ...

@pytest.fixture
def categorias(db, usuario):
    """Cria categorias padrão vinculadas ao usuário."""
    ...
```

## Regras
- Todo teste deve rodar isolado — sem dependência de ordem.
- Testar isolamento multi-tenant: criar dados com usuário A, verificar que usuário B não os vê.
- Testar fluxos de conta bloqueada.
- Testar permissões do superusuário.
- Nomear testes descritivamente: `test_usuario_inativo_ve_tela_bloqueio`.
