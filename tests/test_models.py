import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from financas.models import Categoria, ConfiguracaoAlerta, Despesa, Orcamento, Receita


# =============================================================================
# Categoria
# =============================================================================

class TestCategoriaModel:
    """Testes para o model Categoria."""

    @pytest.mark.django_db
    def test_criar_categoria_valida(self, usuario):
        categoria = Categoria.objects.create(
            user=usuario,
            nome='Investimentos',
            tipo=Categoria.TipoCategoria.RECEITA,
        )
        assert categoria.pk is not None
        assert categoria.nome == 'Investimentos'
        assert categoria.tipo == 'receita'
        assert categoria.user == usuario

    @pytest.mark.django_db
    def test_categoria_str(self, categoria_receita):
        assert str(categoria_receita) == 'Salário (Receita)'

    @pytest.mark.django_db
    def test_categoria_str_despesa(self, categoria_despesa):
        assert str(categoria_despesa) == 'Alimentação (Despesa)'

    @pytest.mark.django_db
    def test_categoria_unica_por_usuario(self, usuario, categoria_receita):
        """Não permite duas categorias com mesmo nome+tipo para o mesmo usuário."""
        with pytest.raises(IntegrityError):
            Categoria.objects.create(
                user=usuario,
                nome='Salário',
                tipo=Categoria.TipoCategoria.RECEITA,
            )

    @pytest.mark.django_db
    def test_categoria_mesmo_nome_usuarios_diferentes(self, usuario, outro_usuario):
        """Usuários diferentes podem ter categorias com o mesmo nome e tipo."""
        Categoria.objects.create(
            user=usuario, nome='Freelance', tipo=Categoria.TipoCategoria.RECEITA,
        )
        cat2 = Categoria.objects.create(
            user=outro_usuario, nome='Freelance', tipo=Categoria.TipoCategoria.RECEITA,
        )
        assert cat2.pk is not None

    @pytest.mark.django_db
    def test_categoria_tipo_invalido(self, usuario):
        """Tipo fora dos choices deve falhar na validação."""
        categoria = Categoria(
            user=usuario,
            nome='Invalida',
            tipo='invalido',
        )
        with pytest.raises(ValidationError):
            categoria.full_clean()


# =============================================================================
# Receita
# =============================================================================

class TestReceitaModel:
    """Testes para o model Receita."""

    @pytest.mark.django_db
    def test_criar_receita_valida(self, receita):
        assert receita.pk is not None
        assert receita.descricao == 'Salário mensal'
        assert receita.valor == Decimal('5000.00')

    @pytest.mark.django_db
    def test_receita_str(self, receita):
        assert str(receita) == 'Salário mensal - R$ 5000.00'

    @pytest.mark.django_db
    def test_receita_valor_positivo(self, usuario, categoria_receita):
        """Valor deve ser maior que zero (MinValueValidator)."""
        rec = Receita(
            user=usuario,
            descricao='Receita inválida',
            valor=Decimal('0.00'),
            data=datetime.date(2026, 3, 1),
            categoria=categoria_receita,
        )
        with pytest.raises(ValidationError):
            rec.full_clean()

    @pytest.mark.django_db
    def test_receita_valor_negativo(self, usuario, categoria_receita):
        """Valor negativo também deve falhar."""
        rec = Receita(
            user=usuario,
            descricao='Receita negativa',
            valor=Decimal('-100.00'),
            data=datetime.date(2026, 3, 1),
            categoria=categoria_receita,
        )
        with pytest.raises(ValidationError):
            rec.full_clean()

    @pytest.mark.django_db
    def test_receita_ordering(self, usuario, categoria_receita):
        """Receitas devem ser ordenadas pela data mais recente primeiro."""
        r1 = Receita.objects.create(
            user=usuario, descricao='Antiga', valor=Decimal('100.00'),
            data=datetime.date(2026, 1, 1), categoria=categoria_receita,
        )
        r2 = Receita.objects.create(
            user=usuario, descricao='Recente', valor=Decimal('200.00'),
            data=datetime.date(2026, 3, 15), categoria=categoria_receita,
        )
        receitas = list(Receita.objects.filter(user=usuario))
        assert receitas[0] == r2
        assert receitas[1] == r1


# =============================================================================
# Despesa
# =============================================================================

class TestDespesaModel:
    """Testes para o model Despesa."""

    @pytest.mark.django_db
    def test_criar_despesa_valida(self, despesa):
        assert despesa.pk is not None
        assert despesa.descricao == 'Supermercado'
        assert despesa.valor == Decimal('350.00')

    @pytest.mark.django_db
    def test_despesa_str(self, despesa):
        assert str(despesa) == 'Supermercado - R$ 350.00'

    @pytest.mark.django_db
    def test_despesa_valor_positivo(self, usuario, categoria_despesa):
        """Valor deve ser maior que zero (MinValueValidator)."""
        desp = Despesa(
            user=usuario,
            descricao='Despesa inválida',
            valor=Decimal('0.00'),
            data=datetime.date(2026, 3, 1),
            categoria=categoria_despesa,
        )
        with pytest.raises(ValidationError):
            desp.full_clean()

    @pytest.mark.django_db
    def test_despesa_valor_negativo(self, usuario, categoria_despesa):
        """Valor negativo também deve falhar."""
        desp = Despesa(
            user=usuario,
            descricao='Despesa negativa',
            valor=Decimal('-50.00'),
            data=datetime.date(2026, 3, 1),
            categoria=categoria_despesa,
        )
        with pytest.raises(ValidationError):
            desp.full_clean()

    @pytest.mark.django_db
    def test_despesa_ordering(self, usuario, categoria_despesa):
        """Despesas devem ser ordenadas pela data mais recente primeiro."""
        d1 = Despesa.objects.create(
            user=usuario, descricao='Antiga', valor=Decimal('80.00'),
            data=datetime.date(2026, 1, 10), categoria=categoria_despesa,
        )
        d2 = Despesa.objects.create(
            user=usuario, descricao='Recente', valor=Decimal('120.00'),
            data=datetime.date(2026, 3, 20), categoria=categoria_despesa,
        )
        despesas = list(Despesa.objects.filter(user=usuario))
        assert despesas[0] == d2
        assert despesas[1] == d1


# =============================================================================
# Orçamento
# =============================================================================

class TestOrcamentoModel:
    """Testes para o model Orcamento."""

    @pytest.mark.django_db
    def test_criar_orcamento(self, orcamento):
        """Criação básica de orçamento e __str__."""
        assert orcamento.pk is not None
        assert orcamento.mes == 3
        assert orcamento.ano == 2026
        assert orcamento.valor == Decimal('3000.00')
        assert str(orcamento) == 'Orçamento 03/2026 - R$ 3000.00'

    @pytest.mark.django_db
    def test_orcamento_constraint_unico(self, usuario, orcamento):
        """Mesmo user+mes+ano deve gerar IntegrityError."""
        with pytest.raises(IntegrityError):
            Orcamento.objects.create(
                user=usuario, mes=3, ano=2026, valor=Decimal('5000.00'),
            )

    @pytest.mark.django_db
    def test_orcamento_validator_mes_invalido(self, usuario):
        """Mês 0 e mês 13 devem gerar ValidationError."""
        orc_zero = Orcamento(user=usuario, mes=0, ano=2026, valor=Decimal('1000.00'))
        with pytest.raises(ValidationError):
            orc_zero.full_clean()

        orc_treze = Orcamento(user=usuario, mes=13, ano=2026, valor=Decimal('1000.00'))
        with pytest.raises(ValidationError):
            orc_treze.full_clean()

    @pytest.mark.django_db
    def test_orcamento_validator_ano_invalido(self, usuario):
        """Ano 2019 deve gerar ValidationError."""
        orc = Orcamento(user=usuario, mes=1, ano=2019, valor=Decimal('1000.00'))
        with pytest.raises(ValidationError):
            orc.full_clean()

    @pytest.mark.django_db
    def test_orcamento_valor_negativo(self, usuario):
        """Valor negativo deve gerar ValidationError."""
        orc = Orcamento(user=usuario, mes=1, ano=2026, valor=Decimal('-100.00'))
        with pytest.raises(ValidationError):
            orc.full_clean()


# =============================================================================
# ConfiguracaoAlerta
# =============================================================================

class TestConfiguracaoAlertaModel:
    """Testes para o model ConfiguracaoAlerta."""

    @pytest.mark.django_db
    def test_criar_configuracao(self, configuracao_alerta, usuario):
        """Criação de configuração e __str__."""
        assert configuracao_alerta.pk is not None
        assert str(configuracao_alerta) == f'Alertas de {usuario.username}'

    @pytest.mark.django_db
    def test_configuracao_constraint_unica(self, usuario, configuracao_alerta):
        """Mesmo user deve gerar IntegrityError."""
        with pytest.raises(IntegrityError):
            ConfiguracaoAlerta.objects.create(user=usuario)

    @pytest.mark.django_db
    def test_configuracao_defaults(self, configuracao_alerta):
        """Valores default devem estar corretos."""
        assert configuracao_alerta.alerta_orcamento_ativo is True
        assert configuracao_alerta.limiar_orcamento == 80
        assert configuracao_alerta.alerta_gasto_acelerado_ativo is True
        assert configuracao_alerta.alerta_saldo_baixo_ativo is True
        assert configuracao_alerta.limite_saldo_minimo == Decimal('0.00')
