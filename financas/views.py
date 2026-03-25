from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

import calendar
from datetime import date

from financas.filters import CategoriaFilter, DespesaFilter, OrcamentoFilter, ReceitaFilter
from financas.forms import CategoriaForm, ConfiguracaoAlertaForm, DespesaForm, OrcamentoForm, ReceitaForm
from financas.models import Categoria, ConfiguracaoAlerta, Despesa, Orcamento, Receita
from financas.services import (
    calcular_previsao_saldo,
    calcular_saldo,
    exportar_csv,
    exportar_json,
    exportar_pdf,
    gerar_dados_balanca_diaria,
    gerar_dados_heatmap,
    obter_detalhes_dia,
    obter_resumo_balanca_mensal,
    obter_todos_insights,
    resumo_por_categoria,
    NOMES_MESES,
)


# ─── Dashboard ──────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """Painel principal com saldo, totais e dados para gráficos."""
    usuario = request.user
    saldo = calcular_saldo(usuario)

    # Dados para gráficos por categoria
    resumo_receitas = resumo_por_categoria(usuario, 'receita')
    resumo_despesas = resumo_por_categoria(usuario, 'despesa')

    # Dados para gráficos — passados como dicts Python para o json_script serializar corretamente
    dados_grafico_barras = {
        'receitas': float(saldo['total_receitas']),
        'despesas': float(saldo['total_despesas']),
    }
    dados_pizza_receitas = {
        'labels': [item['categoria__nome'] for item in resumo_receitas],
        'valores': [float(item['total']) for item in resumo_receitas],
    }
    dados_pizza_despesas = {
        'labels': [item['categoria__nome'] for item in resumo_despesas],
        'valores': [float(item['total']) for item in resumo_despesas],
    }

    # Últimos lançamentos (5 de cada)
    ultimas_receitas = Receita.objects.filter(user=usuario).select_related('categoria')[:5]
    ultimas_despesas = Despesa.objects.filter(user=usuario).select_related('categoria')[:5]

    # Previsão de saldo até o fim do mês
    previsao = calcular_previsao_saldo(usuario)

    contexto = {
        'saldo': saldo,
        'resumo_receitas': resumo_receitas,
        'resumo_despesas': resumo_despesas,
        'ultimas_receitas': ultimas_receitas,
        'ultimas_despesas': ultimas_despesas,
        'previsao': previsao,
        'dados_grafico_barras': dados_grafico_barras,
        'dados_pizza_receitas': dados_pizza_receitas,
        'dados_pizza_despesas': dados_pizza_despesas,
    }
    return render(request, 'financas/dashboard.html', contexto)


# ─── Mixins ─────────────────────────────────────────────────────────────────

class UsuarioQuerysetMixin(LoginRequiredMixin):
    """Mixin que filtra o queryset pelo usuário autenticado."""

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


# ─── Receitas ───────────────────────────────────────────────────────────────

class ReceitaListView(UsuarioQuerysetMixin, ListView):
    model = Receita
    template_name = 'financas/receita_lista.html'
    context_object_name = 'receitas'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('categoria')
        self.filtro = ReceitaFilter(self.request.GET, queryset=qs, user=self.request.user)
        return self.filtro.qs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['filtro'] = self.filtro
        contexto['filtros_ativos'] = any(v for v in self.request.GET.values() if v)
        return contexto


class ReceitaCreateView(UsuarioQuerysetMixin, CreateView):
    model = Receita
    form_class = ReceitaForm
    template_name = 'financas/receita_form.html'
    success_url = reverse_lazy('financas:receita_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Receita criada com sucesso!')
        return super().form_valid(form)


class ReceitaUpdateView(UsuarioQuerysetMixin, UpdateView):
    model = Receita
    form_class = ReceitaForm
    template_name = 'financas/receita_form.html'
    success_url = reverse_lazy('financas:receita_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Receita atualizada com sucesso!')
        return super().form_valid(form)


class ReceitaDeleteView(UsuarioQuerysetMixin, DeleteView):
    model = Receita
    template_name = 'financas/receita_confirmar_exclusao.html'
    success_url = reverse_lazy('financas:receita_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Receita excluída com sucesso!')
        return super().form_valid(form)


# ─── Despesas ───────────────────────────────────────────────────────────────

class DespesaListView(UsuarioQuerysetMixin, ListView):
    model = Despesa
    template_name = 'financas/despesa_lista.html'
    context_object_name = 'despesas'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('categoria')
        self.filtro = DespesaFilter(self.request.GET, queryset=qs, user=self.request.user)
        return self.filtro.qs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['filtro'] = self.filtro
        contexto['filtros_ativos'] = any(v for v in self.request.GET.values() if v)
        return contexto


class DespesaCreateView(UsuarioQuerysetMixin, CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'financas/despesa_form.html'
    success_url = reverse_lazy('financas:despesa_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Despesa criada com sucesso!')
        return super().form_valid(form)


class DespesaUpdateView(UsuarioQuerysetMixin, UpdateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'financas/despesa_form.html'
    success_url = reverse_lazy('financas:despesa_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Despesa atualizada com sucesso!')
        return super().form_valid(form)


class DespesaDeleteView(UsuarioQuerysetMixin, DeleteView):
    model = Despesa
    template_name = 'financas/despesa_confirmar_exclusao.html'
    success_url = reverse_lazy('financas:despesa_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Despesa excluída com sucesso!')
        return super().form_valid(form)


# ─── Categorias ─────────────────────────────────────────────────────────────

class CategoriaListView(UsuarioQuerysetMixin, ListView):
    model = Categoria
    template_name = 'financas/categoria_lista.html'
    context_object_name = 'categorias'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        self.filtro = CategoriaFilter(self.request.GET, queryset=qs)
        return self.filtro.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro'] = self.filtro
        ctx['filtros_ativos'] = any(v for v in self.request.GET.values() if v)
        return ctx


class CategoriaCreateView(UsuarioQuerysetMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'financas/categoria_form.html'
    success_url = reverse_lazy('financas:categoria_lista')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)


class CategoriaUpdateView(UsuarioQuerysetMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'financas/categoria_form.html'
    success_url = reverse_lazy('financas:categoria_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)


class CategoriaDeleteView(UsuarioQuerysetMixin, DeleteView):
    model = Categoria
    template_name = 'financas/categoria_confirmar_exclusao.html'
    success_url = reverse_lazy('financas:categoria_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria excluída com sucesso!')
        return super().form_valid(form)


# ─── Alertas ────────────────────────────────────────────────────────────────

@login_required
def configuracao_alertas_view(request):
    """Configuração dos limiares de alerta do usuário."""
    config, _ = ConfiguracaoAlerta.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ConfiguracaoAlertaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações de alerta salvas com sucesso!')
            return redirect('financas:configuracao_alertas')
    else:
        form = ConfiguracaoAlertaForm(instance=config)
    return render(request, 'financas/configuracao_alertas.html', {'form': form})


class OrcamentoListView(UsuarioQuerysetMixin, ListView):
    model = Orcamento
    template_name = 'financas/orcamento_lista.html'
    context_object_name = 'orcamentos'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        self.filtro = OrcamentoFilter(self.request.GET, queryset=qs)
        return self.filtro.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro'] = self.filtro
        ctx['filtros_ativos'] = any(v for v in self.request.GET.values() if v)
        return ctx


class OrcamentoCreateView(UsuarioQuerysetMixin, CreateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'financas/orcamento_form.html'
    success_url = reverse_lazy('financas:orcamento_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Orçamento criado com sucesso!')
        return super().form_valid(form)


class OrcamentoUpdateView(UsuarioQuerysetMixin, UpdateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'financas/orcamento_form.html'
    success_url = reverse_lazy('financas:orcamento_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Orçamento atualizado com sucesso!')
        return super().form_valid(form)


class OrcamentoDeleteView(UsuarioQuerysetMixin, DeleteView):
    model = Orcamento
    template_name = 'financas/orcamento_confirmar_exclusao.html'
    success_url = reverse_lazy('financas:orcamento_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Orçamento excluído com sucesso!')
        return super().form_valid(form)


# ─── Exportação ─────────────────────────────────────────────────────────────

@login_required
def exportar_view(request, tipo: str, formato: str):
    """Exporta lançamentos filtrados em JSON, CSV ou PDF."""
    if tipo not in ('receita', 'despesa'):
        raise Http404('Tipo inválido.')
    if formato not in ('json', 'csv', 'pdf'):
        raise Http404('Formato inválido.')

    modelo = Receita if tipo == 'receita' else Despesa
    filtro_cls = ReceitaFilter if tipo == 'receita' else DespesaFilter

    qs = modelo.objects.filter(user=request.user).select_related('categoria')
    filtro = filtro_cls(request.GET, queryset=qs, user=request.user)
    qs_filtrado = filtro.qs

    funcoes_exportacao = {
        'json': exportar_json,
        'csv': exportar_csv,
        'pdf': exportar_pdf,
    }

    return funcoes_exportacao[formato](request.user, tipo, qs_filtrado)


# ─── Calendário / Heat Zone ────────────────────────────────────────────────

@login_required
def calendario_view(request, mes=None, ano=None):
    """Visualização do calendário com heatmap de despesas."""
    hoje = date.today()

    if mes is None:
        try:
            mes = int(request.GET.get('mes', hoje.month))
        except (ValueError, TypeError):
            mes = hoje.month
    if ano is None:
        try:
            ano = int(request.GET.get('ano', hoje.year))
        except (ValueError, TypeError):
            ano = hoje.year

    # Validar parâmetros
    if not (1 <= mes <= 12) or not (2020 <= ano <= 2100):
        mes, ano = hoje.month, hoje.year

    aba = request.GET.get('aba', 'heatzone')
    if aba not in ('heatzone', 'receita_despesa'):
        aba = 'heatzone'

    # Navegação entre meses
    if mes == 1:
        mes_anterior, ano_anterior = 12, ano - 1
    else:
        mes_anterior, ano_anterior = mes - 1, ano

    if mes == 12:
        proximo_mes, proximo_ano = 1, ano + 1
    else:
        proximo_mes, proximo_ano = mes + 1, ano

    meses_opcoes = list(NOMES_MESES.items())  # [(1, 'janeiro'), ...]
    anos_opcoes = list(range(2020, date.today().year + 3))

    contexto = {
        'mes': mes,
        'ano': ano,
        'mes_nome': NOMES_MESES.get(mes, ''),
        'aba_ativa': aba,
        'mes_anterior': mes_anterior,
        'ano_anterior': ano_anterior,
        'proximo_mes': proximo_mes,
        'proximo_ano': proximo_ano,
        'meses_opcoes': meses_opcoes,
        'anos_opcoes': anos_opcoes,
    }

    if aba == 'heatzone':
        dados_heatmap = gerar_dados_heatmap(request.user, mes, ano)
        insights = obter_todos_insights(request.user, mes, ano)

        # Montar grid de semanas para o template
        cal = calendar.monthcalendar(ano, mes)
        semanas = []
        for semana in cal:
            dias_semana = []
            for dia in semana:
                if dia == 0:
                    dias_semana.append(None)
                else:
                    dias_semana.append({
                        'dia': dia,
                        **dados_heatmap.get(dia, {'total': 0, 'nivel': 0, 'cor': 'bg-gray-100'}),
                    })
            semanas.append(dias_semana)

        contexto['dados_heatmap'] = dados_heatmap
        contexto['insights'] = insights
        contexto['semanas'] = semanas

    elif aba == 'receita_despesa':
        dados_balanca = gerar_dados_balanca_diaria(request.user, mes, ano)
        resumo_balanca = obter_resumo_balanca_mensal(request.user, mes, ano, dados_diarios=dados_balanca)

        # Montar grid de semanas para balança
        cal = calendar.monthcalendar(ano, mes)
        semanas_balanca = []
        for semana in cal:
            dias_semana = []
            for dia in semana:
                if dia == 0:
                    dias_semana.append(None)
                else:
                    dias_semana.append({
                        'dia': dia,
                        **dados_balanca.get(dia, {
                            'receitas': 0, 'despesas': 0, 'total': 0,
                            'percentual_receita': 0, 'percentual_despesa': 0,
                            'tem_dados': False,
                        }),
                    })
            semanas_balanca.append(dias_semana)

        contexto['dados_balanca'] = dados_balanca
        contexto['resumo_balanca'] = resumo_balanca
        contexto['semanas_balanca'] = semanas_balanca

    return render(request, 'financas/calendario.html', contexto)


@login_required
def detalhes_dia_view(request, ano, mes, dia):
    """Detalhes de receitas e despesas de um dia específico."""
    try:
        data = date(ano, mes, dia)
    except ValueError:
        raise Http404('Data inválida.')

    detalhes = obter_detalhes_dia(request.user, data)

    return render(request, 'financas/detalhes_dia.html', {
        'detalhes': detalhes,
        'data': data,
    })
