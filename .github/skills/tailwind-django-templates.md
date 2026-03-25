# Skill: Tailwind CSS + Django Templates — Padrões e Combinações

> Referência obrigatória para o subagent-frontend. Contém os padrões visuais do projeto, componentes prontos e combinações de classes Tailwind para cada contexto.

---

## Paleta de Cores do Projeto

| Uso | Classes Tailwind |
|-----|----------------|
| Primária (azul) | `blue-600`, `blue-700`, `blue-50` |
| Sucesso / Receita | `green-600`, `green-50`, `green-100` |
| Perigo / Despesa | `red-500`, `red-600`, `red-50` |
| Aviso / Alerta | `yellow-400`, `yellow-50`, `amber-500` |
| Neutro / Fundo | `gray-50`, `gray-100`, `gray-200` |
| Texto principal | `gray-800`, `gray-900` |
| Texto secundário | `gray-500`, `gray-600` |
| Bordas | `border-gray-200`, `border-gray-300` |

---

## 1. Layout Base — Estrutura de Página

```html
{% extends "base.html" %}
{% block titulo %}Título da Página{% endblock %}
{% block conteudo %}

<div class="space-y-6">

  <!-- Cabeçalho de seção -->
  <div class="flex items-center justify-between">
    <h1 class="text-2xl font-bold text-gray-800">Título Principal</h1>
    <a href="{% url 'financas:receita_criar' %}"
       class="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg
              hover:bg-blue-700 transition text-sm font-medium shadow-sm">
      + Nova Receita
    </a>
  </div>

  <!-- Conteúdo principal -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <!-- ... -->
  </div>

</div>
{% endblock %}
```

---

## 2. Cards de KPI / Resumo (Dashboard)

```html
<!-- Grid responsivo de cards -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

  <!-- Card Receitas (verde) -->
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm font-medium text-gray-500">Total Receitas</span>
      <span class="text-green-500 text-xl">↑</span>
    </div>
    <p class="text-2xl font-bold text-green-600">
      R$ {{ saldo.total_receitas|floatformat:2 }}
    </p>
    <p class="text-xs text-gray-400 mt-1">Mês atual</p>
  </div>

  <!-- Card Despesas (vermelho) -->
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm font-medium text-gray-500">Total Despesas</span>
      <span class="text-red-500 text-xl">↓</span>
    </div>
    <p class="text-2xl font-bold text-red-600">
      R$ {{ saldo.total_despesas|floatformat:2 }}
    </p>
    <p class="text-xs text-gray-400 mt-1">Mês atual</p>
  </div>

  <!-- Card Saldo (dinâmico: verde se positivo, vermelho se negativo) -->
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm font-medium text-gray-500">Saldo</span>
      <span class="text-blue-500 text-xl">=</span>
    </div>
    <p class="text-2xl font-bold {% if saldo.saldo >= 0 %}text-green-600{% else %}text-red-600{% endif %}">
      R$ {{ saldo.saldo|floatformat:2 }}
    </p>
    <p class="text-xs text-gray-400 mt-1">Receitas − Despesas</p>
  </div>

</div>
```

---

## 3. Tabela de Lançamentos — Lista Padrão

```html
<div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">

  <!-- Cabeçalho da tabela -->
  <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
    <h2 class="text-base font-semibold text-gray-800">Últimos Lançamentos</h2>
    <a href="{% url 'financas:receita_lista' %}"
       class="text-sm text-blue-600 hover:underline">Ver todos →</a>
  </div>

  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 text-xs text-gray-500 uppercase tracking-wider">
        <tr>
          <th class="px-5 py-3 text-left">Descrição</th>
          <th class="px-5 py-3 text-left">Categoria</th>
          <th class="px-5 py-3 text-left">Data</th>
          <th class="px-5 py-3 text-right">Valor</th>
          <th class="px-5 py-3 text-center">Ações</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        {% for item in receitas %}
        <tr class="hover:bg-gray-50 transition-colors">
          <td class="px-5 py-3 font-medium text-gray-800">{{ item.descricao }}</td>
          <td class="px-5 py-3">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs
                         bg-green-100 text-green-700 font-medium">
              {{ item.categoria.nome }}
            </span>
          </td>
          <td class="px-5 py-3 text-gray-500">{{ item.data|date:"d/m/Y" }}</td>
          <td class="px-5 py-3 text-right font-semibold text-green-600">
            R$ {{ item.valor|floatformat:2 }}
          </td>
          <td class="px-5 py-3 text-center">
            <div class="flex items-center justify-center gap-2">
              <a href="{% url 'financas:receita_editar' item.pk %}"
                 class="text-blue-600 hover:text-blue-800 text-xs font-medium">Editar</a>
              <a href="{% url 'financas:receita_excluir' item.pk %}"
                 class="text-red-500 hover:text-red-700 text-xs font-medium">Excluir</a>
            </div>
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="5" class="px-5 py-10 text-center text-gray-400">
            Nenhum lançamento encontrado.
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
```

---

## 4. Formulários — Padrão do Projeto

```html
<div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
  <h2 class="text-lg font-semibold text-gray-800 mb-5">Nova Receita</h2>

  <form method="post" class="space-y-4">
    {% csrf_token %}

    <!-- Campo individual -->
    <div>
      <label for="{{ form.descricao.id_for_label }}"
             class="block text-sm font-medium text-gray-700 mb-1">
        Descrição
      </label>
      <input type="text"
             name="{{ form.descricao.html_name }}"
             id="{{ form.descricao.id_for_label }}"
             value="{{ form.descricao.value|default:'' }}"
             placeholder="Ex: Salário mensal"
             class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                    focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                    transition outline-none
                    {% if form.descricao.errors %}border-red-400 bg-red-50{% endif %}">
      {% if form.descricao.errors %}
      <p class="mt-1 text-xs text-red-500">{{ form.descricao.errors|join:", " }}</p>
      {% endif %}
    </div>

    <!-- Campo valor com prefixo R$ -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Valor</label>
      <div class="relative">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm font-medium">R$</span>
        <input type="number" step="0.01" min="0.01"
               name="{{ form.valor.html_name }}"
               value="{{ form.valor.value|default:'' }}"
               class="w-full pl-9 pr-4 py-2.5 rounded-lg border border-gray-300 text-sm
                      focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition">
      </div>
      {% if form.valor.errors %}
      <p class="mt-1 text-xs text-red-500">{{ form.valor.errors|join:", " }}</p>
      {% endif %}
    </div>

    <!-- Grid 2 colunas para campos menores -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Data</label>
        <input type="date" name="{{ form.data.html_name }}"
               value="{{ form.data.value|default:'' }}"
               class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                      focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
        <select name="{{ form.categoria.html_name }}"
                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                       focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition bg-white">
          {% for val, label in form.categoria.field.choices %}
          <option value="{{ val }}" {% if form.categoria.value == val|stringformat:"s" %}selected{% endif %}>
            {{ label }}
          </option>
          {% endfor %}
        </select>
      </div>
    </div>

    <!-- Botões de ação -->
    <div class="flex items-center gap-3 pt-2">
      <button type="submit"
              class="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium
                     hover:bg-blue-700 transition shadow-sm">
        Salvar
      </button>
      <a href="{% url 'financas:receita_lista' %}"
         class="px-6 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-800 transition">
        Cancelar
      </a>
    </div>
  </form>
</div>
```

---

## 5. Alertas e Mensagens do Django

```html
<!-- Toasts de mensagem (base.html ou component) -->
{% if messages %}
<div class="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
  {% for message in messages %}
  <div class="flex items-start gap-3 p-4 rounded-xl shadow-lg border
              {% if message.tags == 'success' %}bg-green-50 border-green-200 text-green-800
              {% elif message.tags == 'error' %}bg-red-50 border-red-200 text-red-800
              {% elif message.tags == 'warning' %}bg-yellow-50 border-yellow-200 text-yellow-800
              {% else %}bg-blue-50 border-blue-200 text-blue-800{% endif %}">
    <span class="text-lg">
      {% if message.tags == 'success' %}✅{% elif message.tags == 'error' %}❌
      {% elif message.tags == 'warning' %}⚠️{% else %}ℹ️{% endif %}
    </span>
    <p class="text-sm font-medium">{{ message }}</p>
  </div>
  {% endfor %}
</div>
{% endif %}
```

---

## 6. Badges e Tags de Estado

```html
<!-- Badge de categoria/origem -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
             bg-blue-100 text-blue-700">
  {{ categoria.nome }}
</span>

<!-- Badge de natureza (fixa/variável) -->
{% if despesa.natureza == 'fixa' %}
<span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
  Fixa
</span>
{% elif despesa.natureza == 'variavel' %}
<span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
  Variável
</span>
{% else %}
<span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
  Eventual
</span>
{% endif %}

<!-- Badge de saldo positivo/negativo -->
<span class="font-semibold {% if valor >= 0 %}text-green-600{% else %}text-red-600{% endif %}">
  R$ {{ valor|floatformat:2 }}
</span>
```

---

## 7. Cards de Alerta — Componente alertas.html

```html
<!-- Card de alerta crítico (borda vermelha) -->
<div class="flex items-start gap-3 p-4 bg-white rounded-xl border-l-4 border-red-500 shadow-sm">
  <span class="text-xl shrink-0">⚠️</span>
  <div class="flex-1 min-w-0">
    <p class="text-sm font-semibold text-gray-800">Alerta Crítico</p>
    <p class="text-sm text-gray-600 mt-0.5">{{ alerta.mensagem }}</p>
    {% if alerta.percentual %}
    <!-- Barra de progresso -->
    <div class="mt-2">
      <div class="flex justify-between text-xs text-gray-500 mb-1">
        <span>{{ alerta.percentual }}% do orçamento</span>
        <span>{{ alerta.limiar }}% limite</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="h-2 rounded-full transition-all
                    {% if alerta.percentual >= 100 %}bg-red-500{% else %}bg-yellow-400{% endif %}"
             style="width: {{ alerta.percentual|floatformat:0 }}%">
        </div>
      </div>
    </div>
    {% endif %}
  </div>
</div>

<!-- Card de alerta aviso (borda amarela) -->
<div class="flex items-start gap-3 p-4 bg-white rounded-xl border-l-4 border-yellow-400 shadow-sm">
  <span class="text-xl shrink-0">{{ alerta.icone }}</span>
  <p class="text-sm text-gray-700">{{ alerta.mensagem }}</p>
</div>
```

---

## 8. Empty State — Quando não há dados

```html
<div class="py-16 text-center">
  <div class="text-5xl mb-3">📭</div>
  <h3 class="text-base font-semibold text-gray-700 mb-1">Nenhum lançamento encontrado</h3>
  <p class="text-sm text-gray-500 mb-5">Comece adicionando sua primeira receita.</p>
  <a href="{% url 'financas:receita_criar' %}"
     class="inline-flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5
            rounded-lg text-sm font-medium hover:bg-blue-700 transition shadow-sm">
    + Adicionar Receita
  </a>
</div>
```

---

## 9. Paginação

```html
{% if page_obj.has_other_pages %}
<div class="flex items-center justify-center gap-2 mt-4">
  {% if page_obj.has_previous %}
  <a href="?page={{ page_obj.previous_page_number }}"
     class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 text-gray-600
            hover:bg-gray-50 transition">← Anterior</a>
  {% endif %}

  <span class="text-sm text-gray-500">
    Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
  </span>

  {% if page_obj.has_next %}
  <a href="?page={{ page_obj.next_page_number }}"
     class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 text-gray-600
            hover:bg-gray-50 transition">Próxima →</a>
  {% endif %}
</div>
{% endif %}
```

---

## 10. Modal de Confirmação de Exclusão

```html
<!-- Página de confirmação (template padrão do projeto) -->
<div class="max-w-md mx-auto">
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-8 text-center">
    <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
      <span class="text-2xl">🗑️</span>
    </div>
    <h2 class="text-lg font-semibold text-gray-800 mb-2">Confirmar Exclusão</h2>
    <p class="text-sm text-gray-500 mb-6">
      Tem certeza que deseja excluir
      <strong class="text-gray-800">"{{ object }}"</strong>?
      Esta ação não pode ser desfeita.
    </p>
    <form method="post" class="flex items-center justify-center gap-3">
      {% csrf_token %}
      <button type="submit"
              class="bg-red-600 text-white px-5 py-2 rounded-lg text-sm font-medium
                     hover:bg-red-700 transition">
        Sim, excluir
      </button>
      <a href="{{ cancel_url }}"
         class="px-5 py-2 text-sm font-medium text-gray-600 rounded-lg border border-gray-300
                hover:bg-gray-50 transition">
        Cancelar
      </a>
    </form>
  </div>
</div>
```

---

## 11. Navbar — Padrão do Projeto

```html
<nav class="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex h-16 items-center justify-between">

      <!-- Logo -->
      <a href="{% url 'financas:dashboard' %}"
         class="text-xl font-bold text-blue-600 tracking-tight">
        💰 FinançasPRO
      </a>

      <!-- Links desktop -->
      <div class="hidden md:flex items-center gap-1">
        <a href="{% url 'financas:dashboard' %}"
           class="px-3 py-2 text-sm font-medium rounded-lg
                  {% if request.resolver_match.url_name == 'dashboard' %}
                    text-blue-600 bg-blue-50{% else %}text-gray-600 hover:text-gray-900 hover:bg-gray-50{% endif %}
                  transition">
          📊 Dashboard
        </a>
        <!-- Adicionar links com padrão acima -->
      </div>

      <!-- Usuário + badge alertas -->
      <div class="flex items-center gap-3">
        {% if alertas %}
        <a href="{% url 'financas:configuracao_alertas' %}"
           class="relative p-2 text-gray-500 hover:text-gray-700 transition">
          🔔
          <span class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white
                       text-[10px] font-bold rounded-full flex items-center justify-center">
            {{ alertas|length }}
          </span>
        </a>
        {% endif %}
        <span class="text-sm text-gray-600 hidden md:block">{{ request.user.username }}</span>
        <a href="{% url 'usuarios:logout' %}"
           class="text-sm text-gray-500 hover:text-red-600 transition">Sair</a>
      </div>

    </div>
  </div>
</nav>
```

---

## 12. Previsão de Saldo — Card (Componente)

```html
<!-- Positivo -->
<div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
  <h3 class="text-sm font-semibold text-gray-600 mb-3">📈 Previsão de Saldo</h3>
  <p class="text-3xl font-bold {% if previsao.negativo %}text-red-600{% else %}text-green-600{% endif %}">
    R$ {{ previsao.saldo_projetado|floatformat:2 }}
  </p>
  {% if previsao.negativo %}
  <div class="mt-3 p-2 bg-red-50 rounded-lg text-xs text-red-700 font-medium">
    ⚠️ Saldo projetado negativo ao final do mês
  </div>
  {% endif %}
  <div class="mt-3 space-y-1 text-xs text-gray-500">
    <div class="flex justify-between">
      <span>Saldo atual</span>
      <span class="font-medium text-gray-700">R$ {{ previsao.saldo_atual|floatformat:2 }}</span>
    </div>
    <div class="flex justify-between text-red-500">
      <span>Despesas fixas pendentes</span>
      <span>− R$ {{ previsao.despesas_fixas_pendentes|floatformat:2 }}</span>
    </div>
    <div class="flex justify-between text-green-600">
      <span>Receitas previstas</span>
      <span>+ R$ {{ previsao.receitas_previstas|floatformat:2 }}</span>
    </div>
  </div>
</div>
```

---

## 13. Responsividade Mobile-First — Padrões

```html
<!-- Grid responsivo padrão -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">

<!-- Tabela: scroll horizontal em mobile -->
<div class="overflow-x-auto -mx-4 sm:mx-0">
  <table class="min-w-full">...</table>
</div>

<!-- Texto que some em mobile pequeno -->
<span class="hidden sm:inline">Texto longo</span>
<span class="sm:hidden">Abrev.</span>

<!-- Stack vertical em mobile, horizontal em desktop -->
<div class="flex flex-col sm:flex-row items-start sm:items-center gap-3">
```

---

## 14. Filtros de Busca — Formulário Inline

```html
<form method="get" class="flex flex-col sm:flex-row gap-3 mb-6">
  <input type="text" name="q" value="{{ request.GET.q }}"
         placeholder="Buscar por descrição..."
         class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition">
  <select name="categoria"
          class="rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition">
    <option value="">Todas as categorias</option>
    {% for cat in categorias %}
    <option value="{{ cat.pk }}" {% if request.GET.categoria == cat.pk|stringformat:"s" %}selected{% endif %}>
      {{ cat.nome }}
    </option>
    {% endfor %}
  </select>
  <button type="submit"
          class="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium
                 hover:bg-blue-700 transition whitespace-nowrap">
    Filtrar
  </button>
  {% if request.GET %}
  <a href="?"
     class="px-4 py-2.5 text-sm text-gray-500 border border-gray-300 rounded-lg
            hover:bg-gray-50 transition whitespace-nowrap">
    Limpar
  </a>
  {% endif %}
</form>
```
