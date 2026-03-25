# Skill: Services e Lógica de Negócio — Padrões do Projeto

> Padrões obrigatórios para estruturar a camada de serviços (`services.py`) neste projeto SaaS.

---

## 1. Princípio Fundamental

A lógica de negócio **não fica nas views**. Views são finas: recebem request, delegam para services, retornam response.

```python
# ❌ Lógica na view — NUNCA
@login_required
def dashboard_view(request):
    total = Despesa.objects.filter(user=request.user).aggregate(...)['total'] or 0
    media = total / 30
    # ... calculando na view

# ✅ View delega para service
@login_required
def dashboard_view(request):
    saldo = calcular_saldo(request.user)
    previsao = calcular_previsao_saldo(request.user)
    return render(request, 'financas/dashboard.html', {'saldo': saldo, 'previsao': previsao})
```

---

## 2. Assinatura Padrão de Service

```python
# Services SEMPRE recebem user como primeiro parâmetro
def nome_do_service(user: User, ...) -> tipo_retorno:
    """
    Docstring breve em português explicando o que faz.
    """
    # Toda query joga user no filtro
    qs = Modelo.objects.filter(user=user, ...)
```

---

## 3. Services de Agregação (Saldo, Totais)

```python
def calcular_saldo(user: User) -> dict[str, Decimal]:
    """Calcula saldo atual do usuário."""
    total_receitas = (
        Receita.objects.filter(user=user)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )
    total_despesas = (
        Despesa.objects.filter(user=user)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )
    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': total_receitas - total_despesas,
    }

def calcular_saldo_por_periodo(user: User, data_inicio: date, data_fim: date) -> dict[str, Decimal]:
    """Saldo em um intervalo de datas."""
    total_receitas = (
        Receita.objects
        .filter(user=user, data__gte=data_inicio, data__lte=data_fim)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )
    total_despesas = (
        Despesa.objects
        .filter(user=user, data__gte=data_inicio, data__lte=data_fim)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )
    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': total_receitas - total_despesas,
    }
```

---

## 4. Funções Auxiliares Privadas (prefixo _)

Funções internas, não expostas como API pública do módulo:

```python
def _meses_anteriores(mes: int, ano: int, quantidade: int = 3) -> list[tuple[int, int]]:
    """Retorna lista de (ano, mes) dos N meses anteriores."""
    resultado = []
    for i in range(1, quantidade + 1):
        m = mes - i
        a = ano
        while m <= 0:
            m += 12
            a -= 1
        resultado.append((a, m))
    return resultado

def _identificar_lancamentos_fixos_pendentes(modelo, user: User, mes: int, ano: int) -> Decimal:
    """Genérico: identifica lançamentos fixos recorrentes ausentes no mês atual."""
    # Padrão do projeto: batch query + set lookup (sem N+1)
    ...
```

---

## 5. Services com Parâmetros Opcionais (anti-N+1)

Quando múltiplos services compartilham dados, passar como parâmetros opcionais:

```python
# ❌ Cada função faz suas próprias queries = redundante
def verificar_alerta_saldo_baixo(user, mes, ano):
    previsao = calcular_previsao_saldo(user, mes, ano)  # queries aqui
    config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)  # query aqui
    ...

# ✅ Recebe dados já calculados como parâmetros opcionais
def verificar_alerta_saldo_baixo(user, mes, ano, config=None, previsao=None):
    if config is None:
        config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)
    if previsao is None:
        previsao = calcular_previsao_saldo(user, mes, ano)
    ...

# ✅ Função orquestradora carrega tudo uma vez
def obter_todos_alertas(user: User, previsao=None) -> list[dict]:
    config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)  # 1 query
    alerta_orc = verificar_alerta_orcamento(user, ..., config=config)  # reutiliza config
    alerta_saldo = verificar_alerta_saldo_baixo(user, ..., config=config, previsao=previsao)  # reutiliza
    ...
```

---

## 6. Services de Exportação

```python
def exportar_csv(user: User, tipo: str, queryset: QuerySet) -> HttpResponse:
    """Exporta lançamentos para CSV — sempre filtrado por user."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{tipo}s.csv"'
    response.write('\ufeff')  # BOM para Excel
    writer = csv.writer(response)
    writer.writerow(['Descrição', 'Valor', 'Data', 'Categoria'])
    for item in queryset.filter(user=user).select_related('categoria'):
        writer.writerow([item.descricao, str(item.valor), item.data, item.categoria.nome])
    return response
```

---

## 7. Padrões de Retorno

Sempre retornar dicts com chaves descritivas e `dados_suficientes` quando aplicável:

```python
# Para análises/previsões:
return {
    'saldo_projetado': saldo_projetado,
    'dias_restantes': dias_restantes,
    'negativo': saldo_projetado < 0,
    'dados_suficientes': dados_suficientes,  # bool — view pode verificar antes de exibir
}

# Para alertas:
return {
    'ativo': True,        # bool — component verifica antes de exibir
    'tipo': 'orcamento',  # identificador para template
    'icone': '🔔',
    'nivel': 'aviso',     # 'aviso' ou 'critico' — controla cor do card
    'mensagem': '...',    # texto pronto para o usuário
    'percentual': 85.3,   # dados extras para barra de progresso, etc.
}

# Se inativo/sem dados:
return {'ativo': False}
return {'dados_suficientes': False, 'mensagem': 'Dados insuficientes para análise.'}
```

---

## 8. Constantes de Módulo

Definir no topo do `services.py`, após imports:

```python
NOMES_MESES = {
    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro',
}

NOMES_DIAS = {
    2: 'segunda', 3: 'terça', 4: 'quarta', 5: 'quinta',
    6: 'sexta', 7: 'sábado', 1: 'domingo',
}

CORES_HEATMAP = {0: 'bg-gray-100', 1: 'bg-green-200', 2: 'bg-yellow-200',
                 3: 'bg-orange-300', 4: 'bg-red-400'}
```

---

## 9. Organização do services.py com Seções

```python
# ─── Saldo e Resumo ────────────────────────────────────────────────────────
def calcular_saldo(user): ...
def resumo_por_categoria(user, tipo, ...): ...

# ─── Exportação ───────────────────────────────────────────────────────────
def exportar_json(user, tipo, queryset): ...
def exportar_csv(user, tipo, queryset): ...
def exportar_pdf(user, tipo, queryset): ...

# ─── Previsão de Saldo ────────────────────────────────────────────────────
def ultimo_dia_do_mes(ano, mes): ...
def _meses_anteriores(mes, ano, quantidade=3): ...
def _identificar_lancamentos_fixos_pendentes(modelo, user, mes, ano): ...
def identificar_despesas_fixas_pendentes(user, mes, ano): ...
def calcular_previsao_saldo(user, mes=None, ano=None): ...

# ─── Alertas Inteligentes ─────────────────────────────────────────────────
def verificar_alerta_orcamento(user, mes, ano, config=None): ...
def verificar_alerta_gasto_acelerado(user, config=None): ...
def obter_todos_alertas(user, previsao=None): ...

# ─── Detecção de Padrões (HeatZone) ──────────────────────────────────────
def gerar_dados_heatmap(user, mes, ano): ...
def analisar_padrao_dia_semana(user, meses=3): ...
def obter_todos_insights(user, mes, ano): ...
```

---

## 10. Tratamento de Edge Cases

```python
# Division by zero — sempre proteger
percentual = (total_despesas / orcamento.valor * 100) if orcamento.valor > 0 else Decimal('0')

# Aggregate pode retornar None — usar `or Decimal('0')`
total = qs.aggregate(total=Sum('valor'))['total'] or Decimal('0')

# Count antes de operar com listas/media
if despesas.count() < 5:
    return Decimal('0')

# statistics.quantiles precisa de >= 4 valores
if len(valores) >= 4:
    quartis = statistics.quantiles(valores, n=4)
else:
    # fallback simples
    ...
```
