import django_filters
from django import forms

from financas.models import Categoria, Despesa, Orcamento, Receita

_DATE_WIDGET = forms.DateInput(attrs={'type': 'date'})


class ReceitaFilter(django_filters.FilterSet):
    """Filtro para listagem de receitas."""
    data_inicio = django_filters.DateFilter(
        field_name='data', lookup_expr='gte', label='Data início',
        widget=_DATE_WIDGET,
    )
    data_fim = django_filters.DateFilter(
        field_name='data', lookup_expr='lte', label='Data fim',
        widget=_DATE_WIDGET,
    )
    descricao = django_filters.CharFilter(
        field_name='descricao', lookup_expr='icontains', label='Descrição',
    )
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.none(), label='Categoria',
    )

    class Meta:
        model = Receita
        fields = ['data_inicio', 'data_fim', 'categoria', 'descricao']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.filters['categoria'].queryset = Categoria.objects.filter(
                user=user, tipo=Categoria.TipoCategoria.RECEITA,
            )


class DespesaFilter(django_filters.FilterSet):
    """Filtro para listagem de despesas."""
    data_inicio = django_filters.DateFilter(
        field_name='data', lookup_expr='gte', label='Data início',
        widget=_DATE_WIDGET,
    )
    data_fim = django_filters.DateFilter(
        field_name='data', lookup_expr='lte', label='Data fim',
        widget=_DATE_WIDGET,
    )
    descricao = django_filters.CharFilter(
        field_name='descricao', lookup_expr='icontains', label='Descrição',
    )
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.none(), label='Categoria',
    )

    class Meta:
        model = Despesa
        fields = ['data_inicio', 'data_fim', 'categoria', 'descricao']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.filters['categoria'].queryset = Categoria.objects.filter(
                user=user, tipo=Categoria.TipoCategoria.DESPESA,
            )


class CategoriaFilter(django_filters.FilterSet):
    """Filtro para listagem de categorias."""
    nome = django_filters.CharFilter(
        field_name='nome', lookup_expr='icontains', label='Nome',
    )
    tipo = django_filters.ChoiceFilter(
        choices=[('', 'Todos'), ('receita', 'Receita'), ('despesa', 'Despesa')],
        label='Tipo',
        empty_label=None,
    )

    class Meta:
        model = Categoria
        fields = ['nome', 'tipo']


class OrcamentoFilter(django_filters.FilterSet):
    """Filtro para listagem de orçamentos."""
    mes = django_filters.ChoiceFilter(
        choices=[('', 'Todos')] + [(str(i), f'{i:02d}') for i in range(1, 13)],
        label='Mês',
        empty_label=None,
    )
    ano = django_filters.NumberFilter(
        field_name='ano', lookup_expr='exact', label='Ano',
    )

    class Meta:
        model = Orcamento
        fields = ['mes', 'ano']
