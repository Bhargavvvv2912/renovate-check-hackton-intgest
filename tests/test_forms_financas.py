import datetime
from decimal import Decimal

import pytest

from financas.forms import CategoriaForm, ConfiguracaoAlertaForm, DespesaForm, OrcamentoForm, ReceitaForm
from financas.models import Categoria


# =============================================================================
# CategoriaForm
# =============================================================================

class TestCategoriaForm:
    """Testes para o formulário de Categoria."""

    def test_categoria_form_valido(self):
        form = CategoriaForm(data={'nome': 'Freelance', 'tipo': 'receita'})
        assert form.is_valid()

    def test_categoria_form_nome_obrigatorio(self):
        form = CategoriaForm(data={'nome': '', 'tipo': 'receita'})
        assert not form.is_valid()
        assert 'nome' in form.errors

    def test_categoria_form_tipo_obrigatorio(self):
        form = CategoriaForm(data={'nome': 'Teste', 'tipo': ''})
        assert not form.is_valid()
        assert 'tipo' in form.errors


# =============================================================================
# ReceitaForm
# =============================================================================

class TestReceitaForm:
    """Testes para o formulário de Receita."""

    @pytest.mark.django_db
    def test_receita_form_valido(self, usuario, categoria_receita):
        form = ReceitaForm(
            data={
                'descricao': 'Freelance março',
                'valor': '1500.00',
                'data': '2026-03-10',
                'categoria': categoria_receita.pk,
                'origem': 'freelance',
                'natureza': 'variavel',
            },
            user=usuario,
        )
        assert form.is_valid(), form.errors

    @pytest.mark.django_db
    def test_receita_form_valor_zero_invalido(self, usuario, categoria_receita):
        form = ReceitaForm(
            data={
                'descricao': 'Receita zero',
                'valor': '0.00',
                'data': '2026-03-10',
                'categoria': categoria_receita.pk,
                'origem': 'outros',
                'natureza': 'variavel',
            },
            user=usuario,
        )
        assert not form.is_valid()
        assert 'valor' in form.errors

    @pytest.mark.django_db
    def test_receita_form_campos_obrigatorios(self):
        form = ReceitaForm(data={})
        assert not form.is_valid()
        for campo in ('descricao', 'valor', 'data', 'categoria'):
            assert campo in form.errors

    @pytest.mark.django_db
    def test_receita_form_filtra_categorias_por_usuario(
        self, usuario, outro_usuario, categoria_receita,
    ):
        """O form deve exibir apenas categorias do tipo receita do usuário."""
        # Categoria de outro usuário não deve aparecer
        Categoria.objects.create(
            user=outro_usuario, nome='Salário', tipo=Categoria.TipoCategoria.RECEITA,
        )
        # Categoria despesa do próprio usuário não deve aparecer
        Categoria.objects.create(
            user=usuario, nome='Transporte', tipo=Categoria.TipoCategoria.DESPESA,
        )

        form = ReceitaForm(user=usuario)
        qs_categorias = form.fields['categoria'].queryset
        assert categoria_receita in qs_categorias
        assert qs_categorias.count() == 1


# =============================================================================
# DespesaForm
# =============================================================================

class TestDespesaForm:
    """Testes para o formulário de Despesa."""

    @pytest.mark.django_db
    def test_despesa_form_valido(self, usuario, categoria_despesa):
        form = DespesaForm(
            data={
                'descricao': 'Conta de luz',
                'valor': '200.00',
                'data': '2026-03-15',
                'categoria': categoria_despesa.pk,
                'origem': 'moradia',
                'natureza': 'fixa',
            },
            user=usuario,
        )
        assert form.is_valid(), form.errors

    @pytest.mark.django_db
    def test_despesa_form_valor_negativo_invalido(self, usuario, categoria_despesa):
        form = DespesaForm(
            data={
                'descricao': 'Despesa negativa',
                'valor': '-50.00',
                'data': '2026-03-15',
                'categoria': categoria_despesa.pk,
                'origem': 'outros',
                'natureza': 'variavel',
            },
            user=usuario,
        )
        assert not form.is_valid()
        assert 'valor' in form.errors


# =============================================================================
# OrcamentoForm
# =============================================================================

class TestOrcamentoForm:
    """Testes para o formulário de Orçamento."""

    def test_orcamento_form_valido(self):
        """Dados válidos devem ser aceitos."""
        form = OrcamentoForm(data={'mes': 3, 'ano': 2026, 'valor': '3000.00'})
        assert form.is_valid(), form.errors

    def test_orcamento_form_mes_invalido(self):
        """Mês 0 e mês 13 devem ser inválidos."""
        form_zero = OrcamentoForm(data={'mes': 0, 'ano': 2026, 'valor': '1000.00'})
        assert not form_zero.is_valid()

        form_treze = OrcamentoForm(data={'mes': 13, 'ano': 2026, 'valor': '1000.00'})
        assert not form_treze.is_valid()

    def test_orcamento_form_valor_negativo(self):
        """Valor negativo deve ser inválido."""
        form = OrcamentoForm(data={'mes': 3, 'ano': 2026, 'valor': '-100.00'})
        assert not form.is_valid()
        assert 'valor' in form.errors


# =============================================================================
# ConfiguracaoAlertaForm
# =============================================================================

class TestConfiguracaoAlertaForm:
    """Testes para o formulário de Configuração de Alertas."""

    def test_configuracao_alerta_form_valido(self):
        """Dados válidos devem ser aceitos."""
        form = ConfiguracaoAlertaForm(data={
            'alerta_orcamento_ativo': True,
            'limiar_orcamento': 80,
            'alerta_gasto_acelerado_ativo': True,
            'alerta_saldo_baixo_ativo': True,
            'limite_saldo_minimo': '100.00',
        })
        assert form.is_valid(), form.errors
