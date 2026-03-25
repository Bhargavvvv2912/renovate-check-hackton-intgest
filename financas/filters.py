import django_filters

from financas.models import Categoria, Despesa, Receita


class ReceitaFilter(django_filters.FilterSet):
    """Filtro para listagem de receitas."""
    data_inicio = django_filters.DateFilter(
        field_name='data', lookup_expr='gte', label='Data início',
    )
    data_fim = django_filters.DateFilter(
        field_name='data', lookup_expr='lte', label='Data fim',
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
    )
    data_fim = django_filters.DateFilter(
        field_name='data', lookup_expr='lte', label='Data fim',
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
