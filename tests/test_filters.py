import datetime
from decimal import Decimal

import pytest

from financas.filters import DespesaFilter, ReceitaFilter
from financas.models import Categoria, Despesa, Receita


@pytest.fixture
def receitas_variadas(db, usuario, categoria_receita):
    """Cria múltiplas receitas com datas e descrições variadas."""
    r1 = Receita.objects.create(
        user=usuario, descricao='Salário janeiro', valor=Decimal('5000.00'),
        data=datetime.date(2026, 1, 5), categoria=categoria_receita,
    )
    r2 = Receita.objects.create(
        user=usuario, descricao='Freelance fevereiro', valor=Decimal('2000.00'),
        data=datetime.date(2026, 2, 15), categoria=categoria_receita,
    )
    r3 = Receita.objects.create(
        user=usuario, descricao='Salário março', valor=Decimal('5000.00'),
        data=datetime.date(2026, 3, 5), categoria=categoria_receita,
    )
    return [r1, r2, r3]


@pytest.fixture
def despesas_variadas(db, usuario, categoria_despesa):
    """Cria múltiplas despesas com datas variadas."""
    d1 = Despesa.objects.create(
        user=usuario, descricao='Supermercado jan', valor=Decimal('400.00'),
        data=datetime.date(2026, 1, 10), categoria=categoria_despesa,
    )
    d2 = Despesa.objects.create(
        user=usuario, descricao='Farmácia fev', valor=Decimal('150.00'),
        data=datetime.date(2026, 2, 20), categoria=categoria_despesa,
    )
    return [d1, d2]


class TestReceitaFilter:
    """Testes para o filtro de receitas."""

    @pytest.mark.django_db
    def test_filtro_receita_por_data_inicio(self, usuario, receitas_variadas):
        qs = Receita.objects.filter(user=usuario)
        filtro = ReceitaFilter(
            data={'data_inicio': '2026-02-01'},
            queryset=qs,
            user=usuario,
        )
        resultado = filtro.qs
        assert resultado.count() == 2
        assert all(r.data >= datetime.date(2026, 2, 1) for r in resultado)

    @pytest.mark.django_db
    def test_filtro_receita_por_data_fim(self, usuario, receitas_variadas):
        qs = Receita.objects.filter(user=usuario)
        filtro = ReceitaFilter(
            data={'data_fim': '2026-01-31'},
            queryset=qs,
            user=usuario,
        )
        resultado = filtro.qs
        assert resultado.count() == 1
        assert resultado.first().descricao == 'Salário janeiro'

    @pytest.mark.django_db
    def test_filtro_receita_por_categoria(self, usuario, categoria_receita, receitas_variadas):
        # Criar outra categoria e uma receita nela
        outra_cat = Categoria.objects.create(
            user=usuario, nome='Investimento', tipo=Categoria.TipoCategoria.RECEITA,
        )
        Receita.objects.create(
            user=usuario, descricao='Dividendos', valor=Decimal('300.00'),
            data=datetime.date(2026, 3, 1), categoria=outra_cat,
        )

        qs = Receita.objects.filter(user=usuario)
        filtro = ReceitaFilter(
            data={'categoria': outra_cat.pk},
            queryset=qs,
            user=usuario,
        )
        resultado = filtro.qs
        assert resultado.count() == 1
        assert resultado.first().descricao == 'Dividendos'

    @pytest.mark.django_db
    def test_filtro_receita_por_descricao(self, usuario, receitas_variadas):
        qs = Receita.objects.filter(user=usuario)
        filtro = ReceitaFilter(
            data={'descricao': 'salário'},
            queryset=qs,
            user=usuario,
        )
        resultado = filtro.qs
        assert resultado.count() == 2
        assert all('Salário' in r.descricao for r in resultado)


class TestDespesaFilter:
    """Testes para o filtro de despesas."""

    @pytest.mark.django_db
    def test_filtro_despesa_por_data_inicio(self, usuario, despesas_variadas):
        qs = Despesa.objects.filter(user=usuario)
        filtro = DespesaFilter(
            data={'data_inicio': '2026-02-01'},
            queryset=qs,
            user=usuario,
        )
        resultado = filtro.qs
        assert resultado.count() == 1
        assert resultado.first().descricao == 'Farmácia fev'
