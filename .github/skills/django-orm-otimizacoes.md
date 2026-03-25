# Skill: Otimizações de ORM Django

> Referência obrigatória para o subagent-backend sempre que escrever queries com relacionamentos, agregações ou filtros complexos.

---

## 1. select_related — JOINs para ForeignKey e OneToOne

Use quando o model tem ForeignKey e você vai acessar o objeto relacionado no template ou na lógica.

```python
# ❌ Problema: N+1 queries — 1 query para despesas + N queries para categorias
despesas = Despesa.objects.filter(user=user)
for d in despesas:
    print(d.categoria.nome)  # query extra a cada iteração

# ✅ Correto: 1 único JOIN
despesas = Despesa.objects.filter(user=user).select_related('categoria')
for d in despesas:
    print(d.categoria.nome)  # já carregado, sem query extra
```

### Quando usar
- Acessar `despesa.categoria`, `receita.user`, `lancamento.categoria.nome` em loops
- CBVs ListView com template que exibe categoria
- `select_related` funciona com ForeignKey e OneToOne

```python
# Encadeado: relacionamentos em profundidade
Despesa.objects.filter(user=user).select_related('categoria', 'user')

# Em CBV
class DespesaListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return (
            Despesa.objects
            .filter(user=self.request.user)
            .select_related('categoria')
            .order_by('-data')
        )
```

---

## 2. prefetch_related — Para ManyToMany e ForeignKey reverso

Use quando um objeto tem muitos objetos relacionados (um-para-muitos, M2M).

```python
# ❌ N+1: busca receitas de cada categoria separadamente
categorias = Categoria.objects.filter(user=user)
for cat in categorias:
    print(cat.receitas.all())  # query por categoria

# ✅ 2 queries: 1 para categorias + 1 para todas as receitas (mapeadas em Python)
categorias = Categoria.objects.filter(user=user).prefetch_related('receitas')
for cat in categorias:
    print(cat.receitas.all())  # já carregado
```

### Prefetch com filtro (Prefetch object)
```python
from django.db.models import Prefetch

# Apenas despesas fixas de cada categoria
categorias = Categoria.objects.filter(user=user).prefetch_related(
    Prefetch(
        'despesas',
        queryset=Despesa.objects.filter(natureza='fixa').order_by('-data'),
        to_attr='despesas_fixas',  # acesso como cat.despesas_fixas
    )
)
```

---

## 3. annotate — Agrega dados diretamente na query

Use para calcular totais, contagens e médias sem trazer todos os objetos para Python.

```python
from django.db.models import Sum, Count, Avg, Max, Min, F, Q

# ❌ Ineficiente: traz todos os objetos para somar em Python
despesas = Despesa.objects.filter(user=user)
total = sum(d.valor for d in despesas)

# ✅ Eficiente: a soma acontece no banco de dados
total = Despesa.objects.filter(user=user).aggregate(total=Sum('valor'))['total'] or Decimal('0')

# Agrupamento com annotate — total por categoria
resumo = (
    Despesa.objects
    .filter(user=user)
    .values('categoria__nome')
    .annotate(total=Sum('valor'), quantidade=Count('id'))
    .order_by('-total')
)

# Agrupamento por dia do mês
from django.db.models.functions import TruncDate
gastos_por_dia = (
    Despesa.objects
    .filter(user=user, data__year=ano, data__month=mes)
    .values('data')
    .annotate(total=Sum('valor'))
    .order_by('data')
)

# Agrupamento por dia da semana (1=dom, 2=seg, ..., 7=sáb no Django)
from django.db.models.functions import ExtractWeekDay
gastos_por_dia_semana = (
    Despesa.objects
    .filter(user=user)
    .annotate(dia_semana=ExtractWeekDay('data'))
    .values('dia_semana')
    .annotate(total=Sum('valor'))
)
```

### Annotate em queryset de CBV
```python
class CategoriaListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return (
            Categoria.objects
            .filter(user=self.request.user)
            .annotate(
                total_despesas=Sum('despesas__valor'),
                qtd_lancamentos=Count('despesas'),
            )
            .order_by('nome')
        )
```

---

## 4. aggregate — Valores únicos de agregação

Diferença: `annotate` adiciona coluna por linha, `aggregate` retorna um único dict.

```python
from django.db.models import Sum, Count, Avg, Max, Min

resultado = Receita.objects.filter(user=user).aggregate(
    total=Sum('valor'),
    qtd=Count('id'),
    media=Avg('valor'),
    maior=Max('valor'),
    menor=Min('valor'),
)
# resultado = {'total': Decimal('15000'), 'qtd': 3, ...}
```

---

## 5. F expressions — Referência a campos no banco

Use para comparar ou operar em campos do próprio model, sem trazer para Python.

```python
from django.db.models import F

# Despesas onde valor é maior que o valor médio do mês anterior (hipotético)
# Mais útil: atualização em massa sem carregar objetos
Despesa.objects.filter(user=user).update(valor=F('valor') * Decimal('1.1'))

# Filtro com campo calculado
from django.db.models import ExpressionWrapper, DecimalField
despesas_com_percentual = Despesa.objects.filter(user=user).annotate(
    percentual=ExpressionWrapper(
        F('valor') / total * 100,
        output_field=DecimalField()
    )
)
```

---

## 6. Q objects — Consultas OR, NOT e combinadas

```python
from django.db.models import Q

# OR entre filtros
lancamentos = Despesa.objects.filter(
    Q(natureza='fixa') | Q(valor__gte=Decimal('1000')),
    user=user
)

# NOT
despesas_nao_fixas = Despesa.objects.filter(
    user=user
).exclude(natureza='fixa')

# Combinação complexa
resultado = Receita.objects.filter(
    (Q(origem='salario') | Q(origem='freelance')) & Q(valor__gte=Decimal('500')),
    user=user,
    data__year=2026,
)
```

---

## 7. only() e defer() — Carregar apenas campos necessários

```python
# Carregar apenas campos usados (evita SELECT *)
receitas = (
    Receita.objects
    .filter(user=user)
    .only('id', 'descricao', 'valor', 'data')  # outros campos carregados sob demanda
)

# Excluir campos pesados (ex: campo TextField)
despesas = Despesa.objects.filter(user=user).defer('observacoes')
```

---

## 8. exists() vs count() — Para verificação booleana

```python
# ❌ Lento: carrega objetos desnecessariamente
if Receita.objects.filter(user=user, data__month=mes):
    ...

# ❌ Ainda ruim: conta todos quando só precisa saber "tem algum?"
if Receita.objects.filter(user=user).count() > 0:
    ...

# ✅ Eficiente: para em 1 resultado
if Receita.objects.filter(user=user, data__month=mes).exists():
    ...
```

---

## 9. Padrões do projeto — Isolamento Multi-Tenant obrigatório

Todo queryset DEVE incluir `user=user` ou `user=request.user`:

```python
# ✅ Services recebem user como parâmetro
def calcular_saldo(user: User) -> dict[str, Decimal]:
    total_receitas = (
        Receita.objects
        .filter(user=user)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )
    total_despesas = (
        Despesa.objects
        .filter(user=user)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )
    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': total_receitas - total_despesas,
    }

# ✅ UsuarioQuerysetMixin em CBVs
class UsuarioQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class DespesaListView(UsuarioQuerysetMixin, ListView):
    model = Despesa
    # get_queryset já filtra por user automaticamente
```

---

## 10. Batch queries — Evitar N+1 com sets e dicts

Padrão usado no projeto (em `_identificar_lancamentos_fixos_pendentes`):

```python
# ❌ N+1: query dentro de loop
for chave in recorrentes:
    if Despesa.objects.filter(user=user, descricao=chave).exists():
        ...

# ✅ 1 query: busca tudo e faz lookup em Python com set
existentes = set(
    Despesa.objects
    .filter(user=user, data__gte=primeiro_dia, data__lte=ultimo_dia)
    .values_list('descricao', 'categoria_id')
)
for chave in recorrentes:
    if chave not in existentes:  # lookup O(1) em set
        total_pendente += recorrentes[chave]
```

---

## 11. Dicas de performance para este projeto

| Situação | Solução |
|----------|---------|
| Template exibe `despesa.categoria.nome` em loop | `select_related('categoria')` |
| Dashboard com total de receitas e despesas | `aggregate(total=Sum('valor'))` |
| Calendário: total por dia do mês | `.values('data').annotate(total=Sum('valor'))` |
| Verificar se tem lançamento no mês | `.exists()` |
| Agrupar por categoria | `.values('categoria__nome').annotate(total=Sum('valor'))` |
| Alertas: verificar orçamento | `aggregate(total=Sum('valor'))` — 1 query só |
| Identificar fixos recorrentes | batch query + defaultdict (ver services.py) |
| Previsão de saldo | `calcular_media_diaria_gastos_variaveis` com count threshold |
