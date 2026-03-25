from django import forms

from financas.models import Categoria, ConfiguracaoAlerta, Despesa, Orcamento, Receita

# Classes CSS Tailwind reutilizáveis para widgets
CLASSE_INPUT = (
    'w-full rounded-lg border border-gray-300 px-4 py-2 '
    'focus:border-blue-500 focus:ring-blue-500'
)
CLASSE_SELECT = CLASSE_INPUT


class CategoriaForm(forms.ModelForm):
    """Formulário para criação e edição de categorias."""

    class Meta:
        model = Categoria
        fields = ['nome', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': CLASSE_INPUT,
                'placeholder': 'Nome da categoria',
            }),
            'tipo': forms.Select(attrs={'class': CLASSE_SELECT}),
        }


class ReceitaForm(forms.ModelForm):
    """Formulário para criação e edição de receitas."""

    class Meta:
        model = Receita
        fields = ['descricao', 'valor', 'data', 'categoria', 'origem', 'natureza']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': CLASSE_INPUT,
                'placeholder': 'Descrição da receita',
            }),
            'valor': forms.NumberInput(attrs={
                'class': CLASSE_INPUT,
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0.01',
            }),
            'data': forms.DateInput(attrs={
                'class': CLASSE_INPUT,
                'type': 'date',
            }),
            'categoria': forms.Select(attrs={'class': CLASSE_SELECT}),
            'origem': forms.Select(attrs={'class': CLASSE_SELECT}),
            'natureza': forms.Select(attrs={'class': CLASSE_SELECT}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(
                user=user, tipo=Categoria.TipoCategoria.RECEITA,
            )
        else:
            self.fields['categoria'].queryset = Categoria.objects.none()

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise forms.ValidationError('O valor deve ser maior que zero.')
        return valor


class DespesaForm(forms.ModelForm):
    """Formulário para criação e edição de despesas."""

    class Meta:
        model = Despesa
        fields = ['descricao', 'valor', 'data', 'categoria', 'origem', 'natureza']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': CLASSE_INPUT,
                'placeholder': 'Descrição da despesa',
            }),
            'valor': forms.NumberInput(attrs={
                'class': CLASSE_INPUT,
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0.01',
            }),
            'data': forms.DateInput(attrs={
                'class': CLASSE_INPUT,
                'type': 'date',
            }),
            'categoria': forms.Select(attrs={'class': CLASSE_SELECT}),
            'origem': forms.Select(attrs={'class': CLASSE_SELECT}),
            'natureza': forms.Select(attrs={'class': CLASSE_SELECT}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(
                user=user, tipo=Categoria.TipoCategoria.DESPESA,
            )
        else:
            self.fields['categoria'].queryset = Categoria.objects.none()

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise forms.ValidationError('O valor deve ser maior que zero.')
        return valor


class ConfiguracaoAlertaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoAlerta
        fields = [
            'alerta_orcamento_ativo', 'limiar_orcamento',
            'alerta_gasto_acelerado_ativo',
            'alerta_saldo_baixo_ativo', 'limite_saldo_minimo',
        ]
        widgets = {
            'alerta_orcamento_ativo': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500'}),
            'limiar_orcamento': forms.NumberInput(attrs={'class': CLASSE_INPUT, 'min': '1', 'max': '100', 'step': '1'}),
            'alerta_gasto_acelerado_ativo': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500'}),
            'alerta_saldo_baixo_ativo': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500'}),
            'limite_saldo_minimo': forms.NumberInput(attrs={'class': CLASSE_INPUT, 'min': '0', 'step': '0.01'}),
        }


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['mes', 'ano', 'valor']
        widgets = {
            'mes': forms.Select(
                choices=[(i, f'{i:02d}') for i in range(1, 13)],
                attrs={'class': CLASSE_SELECT},
            ),
            'ano': forms.NumberInput(attrs={'class': CLASSE_INPUT, 'min': '2020', 'max': '2100'}),
            'valor': forms.NumberInput(attrs={'class': CLASSE_INPUT, 'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean_mes(self):
        mes = self.cleaned_data.get('mes')
        if mes is not None and not (1 <= mes <= 12):
            raise forms.ValidationError('Mês deve estar entre 1 e 12.')
        return mes

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise forms.ValidationError('O valor deve ser maior que zero.')
        return valor

    def clean(self):
        cleaned = super().clean()
        mes = cleaned.get('mes')
        ano = cleaned.get('ano')
        if mes and ano and self._user:
            qs = Orcamento.objects.filter(user=self._user, mes=mes, ano=ano)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f'Já existe um orçamento cadastrado para {mes:02d}/{ano}. Edite o orçamento existente.'
                )
        return cleaned
