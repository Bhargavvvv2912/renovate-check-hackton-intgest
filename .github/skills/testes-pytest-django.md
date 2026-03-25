# Skill: Testes Django com pytest — Padrões do Projeto

> Referência obrigatória para o TestAgent ao criar testes para este projeto.

---

## 1. Configuração (setup.cfg já configurado)

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

Rodar (ignorar e2e que requer browser):
```bash
venv\Scripts\python.exe -m pytest tests/ --ignore=tests/test_e2e.py --tb=short -q
```

---

## 2. Estrutura de Arquivos de Teste

```
tests/
├── conftest.py             ← Fixtures compartilhadas entre todos os testes
├── test_models.py          ← Testes de validação, constraints, __str__
├── test_services.py        ← Testes de lógica de negócio
├── test_views_financas.py  ← Testes de views (HTTP, contexto, redirecionamento)
├── test_forms_financas.py  ← Testes de validação de formulários
├── test_filters.py         ← Testes de filtros django-filter
├── test_usuarios.py        ← Testes de autenticação e usuários
└── test_e2e.py             ← Ignorar: requer Selenium/browser
```

---

## 3. Fixtures do conftest.py — Disponíveis em todos os testes

```python
# Usuários
usuario          # User(username='testuser', password='testpass')
outro_usuario    # User(username='outrousuario') — para testes de isolamento
usuario_inativo  # User(is_active=False)
superusuario     # User(is_superuser=True)

# Clientes HTTP autenticados
client_logado         # Client() com usuario logado
client_superusuario   # Client() com superusuario logado

# Dados financeiros de `usuario`
categoria_receita      # Categoria(nome='Salário', tipo=RECEITA, user=usuario)
categoria_despesa      # Categoria(nome='Alimentação', tipo=DESPESA, user=usuario)
receita                # Receita(valor=5000, data=2026-03-01, user=usuario)
despesa                # Despesa(valor=350, data=2026-03-05, user=usuario)

# Dados de outro_usuario (para testes de isolamento)
categoria_receita_outro
categoria_despesa_outro

# Módulo 1 — Alertas
orcamento              # Orcamento(mes=3, ano=2026, valor=3000, user=usuario)
configuracao_alerta    # ConfiguracaoAlerta defaults (user=usuario)
```

---

## 4. Padrão de Classe de Teste

```python
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User
from financas.models import Receita, Despesa, Categoria

@pytest.mark.django_db
class TestNomeDoModulo:
    """Descrição clara da classe."""

    def test_caso_basico(self, usuario, categoria_receita):
        """Descrever o que este teste verifica."""
        receita = Receita.objects.create(
            user=usuario,
            descricao='Salário',
            valor=Decimal('5000.00'),
            data=date(2026, 3, 1),
            categoria=categoria_receita,
        )
        assert receita.pk is not None
        assert receita.user == usuario
```

---

## 5. Testes de Models — Checklist

```python
@pytest.mark.django_db
class TestOrcamentoModel:

    def test_criar(self, usuario):
        """Criação básica — verifica campos e __str__."""
        orc = Orcamento.objects.create(user=usuario, mes=3, ano=2026, valor=Decimal('3000'))
        assert orc.pk is not None
        assert 'Orçamento' in str(orc)

    def test_unique_constraint(self, usuario):
        """Constraint de unicidade lança IntegrityError."""
        from django.db import IntegrityError
        Orcamento.objects.create(user=usuario, mes=3, ano=2026, valor=Decimal('3000'))
        with pytest.raises(IntegrityError):
            Orcamento.objects.create(user=usuario, mes=3, ano=2026, valor=Decimal('5000'))

    def test_validator_campo_invalido(self, usuario):
        """Validators de campo disparam ValidationError via full_clean()."""
        from django.core.exceptions import ValidationError
        orc = Orcamento(user=usuario, mes=0, ano=2026, valor=Decimal('3000'))  # mes=0 inválido
        with pytest.raises(ValidationError):
            orc.full_clean()  # IMPORTANTE: chamar full_clean() para validators Django

    def test_str(self, orcamento):
        """__str__ retorna texto legível."""
        assert str(orcamento) != ''
```

---

## 6. Testes de Services — Checklist

```python
@pytest.mark.django_db
class TestCalcularSaldo:

    def test_sem_lancamentos_retorna_zero(self, usuario):
        saldo = calcular_saldo(usuario)
        assert saldo['total_receitas'] == Decimal('0')
        assert saldo['saldo'] == Decimal('0')

    def test_calculo_correto(self, usuario, receita, despesa):
        saldo = calcular_saldo(usuario)
        assert saldo['total_receitas'] == Decimal('5000.00')
        assert saldo['total_despesas'] == Decimal('350.00')
        assert saldo['saldo'] == Decimal('4650.00')

    def test_isolamento_multitenant(self, usuario, outro_usuario, receita, categoria_receita_outro):
        """OBRIGATÓRIO em todo service — dados de outro user não vazam."""
        Receita.objects.create(
            user=outro_usuario, descricao='Receita outro', valor=Decimal('9000'),
            data=date.today(), categoria=categoria_receita_outro,
        )
        saldo_usuario = calcular_saldo(usuario)
        saldo_outro = calcular_saldo(outro_usuario)
        # Cada usuário vê apenas seus próprios dados
        assert saldo_usuario['total_receitas'] == Decimal('5000.00')
        assert saldo_outro['total_receitas'] == Decimal('9000.00')
```

---

## 7. Testes de Views — HTTP e Contexto

```python
@pytest.mark.django_db
class TestDashboardView:

    def test_retorna_200_autenticado(self, client_logado):
        resposta = client_logado.get('/financas/dashboard/')
        assert resposta.status_code == 200

    def test_redirect_nao_autenticado(self, client):
        resposta = client.get('/financas/dashboard/')
        assert resposta.status_code == 302
        assert '/login/' in resposta['Location']

    def test_contexto_contem_saldo(self, client_logado):
        resposta = client_logado.get('/financas/dashboard/')
        assert 'saldo' in resposta.context
        assert 'total_receitas' in resposta.context['saldo']

@pytest.mark.django_db
class TestReceitaViews:

    def test_criar_receita_post_valido(self, client_logado, categoria_receita):
        """POST válido cria receita e redireciona."""
        dados = {
            'descricao': 'Salário', 'valor': '5000.00',
            'data': '2026-03-01', 'categoria': categoria_receita.pk,
            'origem': 'salario', 'natureza': 'fixa',
        }
        resposta = client_logado.post('/financas/receitas/nova/', dados)
        assert resposta.status_code == 302  # redirect após sucesso
        assert Receita.objects.filter(descricao='Salário').exists()

    def test_editar_receita_outro_usuario_retorna_404(self, client_logado, outro_usuario, categoria_receita_outro):
        """Usuário não pode editar dados de outro usuário."""
        receita_outro = Receita.objects.create(
            user=outro_usuario, descricao='Receita alheia', valor=Decimal('100'),
            data=date.today(), categoria=categoria_receita_outro,
        )
        resposta = client_logado.get(f'/financas/receitas/{receita_outro.pk}/editar/')
        assert resposta.status_code == 404  # isolamento garantido
```

---

## 8. Testes de Forms

```python
@pytest.mark.django_db
class TestReceitaForm:

    def test_form_valido(self, usuario, categoria_receita):
        dados = {
            'descricao': 'Salário', 'valor': '5000.00',
            'data': '2026-03-01', 'categoria': categoria_receita.pk,
            'origem': 'salario', 'natureza': 'fixa',
        }
        form = ReceitaForm(data=dados, user=usuario)
        assert form.is_valid(), form.errors

    def test_valor_zero_invalido(self, usuario, categoria_receita):
        dados = {'descricao': 'Test', 'valor': '0.00', 'data': '2026-03-01',
                 'categoria': categoria_receita.pk, 'origem': 'outros', 'natureza': 'variavel'}
        form = ReceitaForm(data=dados, user=usuario)
        assert not form.is_valid()
        assert 'valor' in form.errors

    def test_categorias_filtradas_por_usuario(self, usuario, outro_usuario,
                                               categoria_receita, categoria_receita_outro):
        """Form não deve expor categorias de outros usuários."""
        form = ReceitaForm(user=usuario)
        qs = form.fields['categoria'].queryset
        assert categoria_receita in qs
        assert categoria_receita_outro not in qs  # isolamento no form
```

---

## 9. Isolamento Multi-Tenant — Padrão Mínimo por Classe de Service

Todo `TestAlgumaCoisa` de service **deve** incluir pelo menos um teste:

```python
def test_isolamento_usuario(self, usuario, outro_usuario, categoria_despesa_outro):
    """Dados de outro_usuario não aparecem para usuario."""
    # Criar dados para outro_usuario
    Despesa.objects.create(
        user=outro_usuario, descricao='Despesa alheia',
        valor=Decimal('9999.00'), data=date.today(),
        categoria=categoria_despesa_outro,
    )
    # Verificar que usuario não vê
    resultado = funcao_testada(usuario, ...)
    assert resultado == valor_esperado_sem_dados_alheios
```

---

## 10. Dicas Importantes

```python
# Data atual em testes — serviços como analisar_padrao_dia_semana
# usam date.today() internamente — criar dados com datas recentes:
from datetime import date, timedelta
hoje = date.today()
data_recente = hoje - timedelta(days=5)

# full_clean() dispara validators de field — OBRIGATÓRIO para testar validators:
obj = Orcamento(user=usuario, mes=0, ...)
with pytest.raises(ValidationError):
    obj.full_clean()  # valida; .save() NÃO dispara validators

# Verificar queries duplicadas (assertNumQueries)
from django.test.utils import CaptureQueriesContext
from django.db import connection
with CaptureQueriesContext(connection) as ctx:
    resultado = minha_funcao(usuario)
assert len(ctx.captured_queries) <= 4  # limite esperado

# Importar modelos nos testes de services
from financas.services import (
    calcular_saldo, calcular_previsao_saldo,
    verificar_alerta_orcamento, obter_todos_alertas,
    gerar_dados_heatmap, obter_todos_insights,
    gerar_dados_balanca_diaria,
)
```

---

## 11. Convenções de Nomenclatura

| Teste | Padrão |
|-------|--------|
| Sucesso básico | `test_criar_receita` |
| Caso inválido | `test_valor_zero_invalido` |
| Isolamento | `test_isolamento_usuario` ou `test_nao_ve_dados_alheios` |
| Edge case | `test_sem_dados_retorna_zero` |
| Autenticação | `test_redirect_nao_autenticado` |
| 404 por acesso alheio | `test_outro_usuario_retorna_404` |
