---
titulo: "Módulo 3 — Detecção de Padrões (Heat Zone)"
status: "planejado"
prioridade: "média"
context_files:
  - ".github/context/business-rules.md"
  - ".github/context/tech-constraints.md"
  - ".github/context/domain-glossary.md"
  - "financas/models.py"
  - "financas/services.py"
  - "financas/views.py"
  - "financas/urls.py"
  - "templates/base.html"
---

# Plano: Módulo 3 — Detecção de Padrões (Heat Zone)

## Objetivo
Gerar insights automáticos sobre o comportamento financeiro do usuário ao longo do tempo, com visualização em calendário de intensidade (heat map) e mensagens contextualizadas. Este módulo compartilha a tela de calendário com o Módulo 4, separados por abas.

## Análise de Impacto

### Arquivos existentes que serão MODIFICADOS
| Arquivo | Alteração |
|---------|-----------|
| `financas/services.py` | Adicionar funções de análise de padrões |
| `financas/views.py` | Adicionar views de calendário e API de dados |
| `financas/urls.py` | Adicionar rotas de calendário |
| `templates/base.html` | Adicionar link "Calendário" na navbar |

### Arquivos NOVOS que serão criados
| Arquivo | Descrição |
|---------|-----------|
| `templates/financas/calendario.html` | Tela principal com abas Heat Zone e Receita×Despesa |
| `templates/components/calendario_heatzone.html` | Componente do calendário com heat map |
| `templates/components/calendario_abas.html` | Componente de navegação por abas |
| `templates/components/insights.html` | Componente de mensagens de insights |
| `static/js/calendario.js` | JS para interatividade do calendário |
| `static/css/calendario.css` | CSS adicional para cores do heat map |

## Lógica de Análise

### Agrupamento por Dia da Semana
```python
def analisar_padrao_dia_semana(user, meses=3):
    # Agrupar despesas dos últimos N meses por dia da semana (0=seg, 6=dom)
    # Calcular média de gasto por dia da semana
    # Identificar dia com maior gasto
    # Calcular percentual acima da média geral
    # Gerar insight: "Você gasta X% mais aos {dia}s"
```

### Agrupamento por Categoria
```python
def analisar_padrao_categoria(user, mes, ano):
    # Agrupar despesas do mês por categoria
    # Calcular percentual de cada categoria sobre o total
    # Identificar categoria dominante
    # Gerar insight: "{Categoria} representa X% dos seus gastos este mês"
```

### Agrupamento por Período Mensal
```python
def analisar_padrao_mensal(user, meses=3):
    # Calcular total de despesas mês a mês
    # Comparar mês atual com mês anterior
    # Calcular variação percentual
    # Gerar insight: "Seus gastos em {mês} foram X% maiores que em {mês_anterior}"
```

### Dados do Heat Map
```python
def gerar_dados_heatmap(user, mes, ano):
    # Para cada dia do mês, calcular total de despesas
    # Classificar intensidade em 5 níveis:
    #   0: sem gasto (cinza claro)
    #   1: gasto baixo (verde claro)
    #   2: gasto moderado (amarelo)
    #   3: gasto alto (laranja)
    #   4: gasto muito alto (vermelho)
    # Níveis baseados em quartis dos gastos do mês
    # Retornar dict {dia: {total, nivel, despesas_detalhadas}}
```

## Escopo

### Backend — Services (financas/services.py)

- [ ] **`gerar_dados_heatmap(user, mes, ano)`**
  - Buscar todas as despesas do mês com `annotate` por dia
  - Calcular quartis para definir níveis de intensidade
  - Retornar dict com dados por dia: `{1: {'total': 150.00, 'nivel': 2, 'cor': '#fbbf24'}, ...}`
  - Dias sem gasto retornam nível 0

- [ ] **`obter_detalhes_dia(user, data)`**
  - Buscar todas as despesas e receitas de um dia específico
  - Retornar listas separadas com detalhes (descrição, valor, categoria)
  - Usado quando o usuário clica em um dia do calendário

- [ ] **`analisar_padrao_dia_semana(user, meses=3)`**
  - Agrupar despesas por `data__week_day` (Django: 1=dom, 7=sáb)
  - Calcular média por dia da semana
  - Identificar dia com maior gasto e percentual acima da média
  - Retornar dict com análise e mensagem de insight
  - Exemplo: `{"dia_maior_gasto": "sábado", "percentual_acima": 35, "mensagem": "Você gasta 35% mais aos sábados."}`

- [ ] **`analisar_padrao_categoria(user, mes, ano)`**
  - Reutilizar `resumo_por_categoria` existente
  - Calcular percentual de cada categoria sobre total
  - Identificar categoria dominante
  - Retornar dict com análise e mensagem
  - Exemplo: `{"categoria_dominante": "Alimentação", "percentual": 42, "mensagem": "Alimentação representa 42% dos seus gastos este mês."}`

- [ ] **`analisar_padrao_mensal(user, meses=3)`**
  - Calcular total de despesas por mês
  - Comparar mês atual com anterior
  - Calcular variação percentual
  - Retornar dict com análise e mensagem
  - Exemplo: `{"variacao": 18, "direcao": "aumento", "mensagem": "Seus gastos em março foram 18% maiores que em fevereiro."}`

- [ ] **`obter_todos_insights(user, mes, ano)`**
  - Agregar os 3 tipos de análise em lista unificada
  - Filtrar insights relevantes (ignorar se dados insuficientes)
  - Retornar lista de dicts prontos para o template

### Backend — Views

- [ ] **`calendario_view(request)`** — FBV principal do calendário
  - Parâmetros GET: `mes`, `ano` (default: mês/ano atual)
  - Navegação: botões ◀ mês anterior / próximo mês ▶
  - Carregar dados do heat map e insights
  - Renderizar `financas/calendario.html`
  - Contexto: `{'dados_heatmap': ..., 'insights': ..., 'mes': ..., 'ano': ..., 'aba_ativa': 'heatzone'}`

- [ ] **`detalhes_dia_view(request, ano, mes, dia)`** — Detalhes ao clicar em um dia
  - Retornar HTML parcial (para uso com HTMX/fetch) ou página completa
  - Decisão: usar JavaScript puro com dados embutidos no HTML para evitar dependência extra
  - Alternativa: embutir dados de detalhes no JSON do calendário e exibir com JS ao clicar

### Backend — URLs

- [ ] `financas/calendario/` → `calendario_view` → nome: `calendario`
- [ ] `financas/calendario/<int:ano>/<int:mes>/` → `calendario_view` → nome: `calendario_mes`
- [ ] `financas/calendario/<int:ano>/<int:mes>/<int:dia>/` → `detalhes_dia_view` → nome: `calendario_dia`

### Frontend — Templates

- [ ] **`templates/financas/calendario.html`** — Tela principal
  - Extends `base.html`
  - Título: "Calendário Financeiro"
  - Navegação de mês (◀ Fevereiro 2026 | Março 2026 | Abril 2026 ▶)
  - Componente de abas: `{% include 'components/calendario_abas.html' %}`
  - Conteúdo da aba ativa:
    - Heat Zone: `{% include 'components/calendario_heatzone.html' %}`
    - Receita×Despesa: `{% include 'components/calendario_receita_despesa.html' %}` (Módulo 4)

- [ ] **`templates/components/calendario_abas.html`** — Navegação por abas
  ```html
  <div class="border-b border-gray-200 mb-6">
    <nav class="flex space-x-4">
      <a href="?aba=heatzone&mes={{mes}}&ano={{ano}}"
         class="{% if aba_ativa == 'heatzone' %}border-blue-500 text-blue-600{% else %}...{% endif %} 
                px-4 py-2 border-b-2 font-medium text-sm">
        🔥 Heat Zone
      </a>
      <a href="?aba=receita_despesa&mes={{mes}}&ano={{ano}}"
         class="...">
        ⚖️ Receita × Despesa
      </a>
    </nav>
  </div>
  ```

- [ ] **`templates/components/calendario_heatzone.html`** — Calendário heat map
  - **Grid**: 7 colunas (Seg-Dom) × N linhas (semanas do mês)
  - **Cada célula**:
    - Número do dia
    - Cor de fundo baseada no nível de intensidade
    - Tooltip com valor total ao hover
    - Cursor pointer, clicável
  - **Escala de cores** (Tailwind):
    - Nível 0: `bg-gray-100` (sem gasto)
    - Nível 1: `bg-green-200` (baixo)
    - Nível 2: `bg-yellow-200` (moderado)
    - Nível 3: `bg-orange-300` (alto)
    - Nível 4: `bg-red-400` (muito alto)
  - **Legenda**: barra com as 5 cores e labels
  - **Modal/painel** de detalhes ao clicar em um dia:
    - Lista de despesas do dia com descrição, categoria, valor
    - Total do dia
    - Animação de abertura suave

- [ ] **`templates/components/insights.html`** — Mensagens de insights
  - Cards com ícone por tipo:
    - 📅 Padrão por dia da semana
    - 📊 Padrão por categoria
    - 📈 Padrão mensal
  - Background neutro (azul claro/cinza)
  - Exibido abaixo do calendário

- [ ] **`templates/base.html`** — Adicionar link na navbar
  - Adicionar "Calendário" entre "Despesas" e "Categorias" no menu
  - Ícone: 📅

### Frontend — JavaScript

- [ ] **`static/js/calendario.js`** — Interatividade
  - Ao clicar em uma célula do calendário:
    - Mostrar painel lateral ou modal com detalhes do dia
    - Dados embutidos como `data-*` attributes ou JSON no template
  - Ao hover: mostrar tooltip com total
  - Animação de transição entre abas (se necessário)
  - **SEM framework JS** — vanilla JavaScript puro

### Frontend — CSS

- [ ] **`static/css/calendario.css`** — Estilos adicionais
  - Transições suaves para hover nos dias
  - Estilo do tooltip
  - Animação do modal de detalhes
  - Responsivo: em mobile, grid pode virar lista

### Testes

- [ ] **`tests/test_services.py`** — Testes para funções de padrões
  - `gerar_dados_heatmap`:
    - Mês com gastos variados → níveis calculados por quartil
    - Mês sem gastos → todos nível 0
    - Isolamento por user_id
  - `analisar_padrao_dia_semana`:
    - Cenário com padrão claro (ex: muito gasto no sábado)
    - Cenário sem dados suficientes
  - `analisar_padrao_categoria`:
    - Cenário com categoria dominante clara
    - Cenário com distribuição equilibrada
  - `analisar_padrao_mensal`:
    - Cenário com aumento mês a mês
    - Cenário com redução
    - Cenário com apenas 1 mês de dados
  - `obter_detalhes_dia`:
    - Dia com lançamentos → retorna lista completa
    - Dia sem lançamentos → retorna listas vazias
    - Isolamento por user_id

- [ ] **`tests/test_views_financas.py`** — Testes para views do calendário
  - `calendario_view`: retorna 200, contexto contém dados corretos
  - Navegação entre meses funciona
  - Parâmetro de aba funciona
  - `detalhes_dia_view`: retorna 200 com dados corretos
  - Requer autenticação
  - Isolamento por user_id

- [ ] **`tests/conftest.py`** — Fixtures
  - Fixtures com despesas distribuídas em vários dias/semanas
  - Fixtures com histórico de 3 meses

### Infra

- [ ] Nenhuma dependência nova
- [ ] Nenhuma migration necessária (usa models existentes)
- [ ] Criar diretórios `static/js/` e `static/css/` se não existirem (já existem na estrutura)

## Critérios de Aceite
1. [ ] Calendário exibe heat map com cores de intensidade por dia
2. [ ] Ao clicar em um dia, exibe detalhamento de gastos
3. [ ] Insights são gerados automaticamente (dia da semana, categoria, mensal)
4. [ ] Navegação entre meses funciona (◀ ▶)
5. [ ] Abas Heat Zone / Receita×Despesa funcionam
6. [ ] Escala de cores é baseada em quartis dos dados reais
7. [ ] Legenda de cores é exibida
8. [ ] Link "Calendário" aparece na navbar
9. [ ] Isolamento por user_id em todas as queries
10. [ ] Responsivo em mobile
11. [ ] Testes passam com 100% de cobertura dos cenários

## Dependências
- Nenhuma dependência de outros módulos novos
- Usa models existentes (`Despesa`, `Receita`, `Categoria`)
- Usa serviço existente `resumo_por_categoria`
- **É dependência do Módulo 4** — compartilham a tela de calendário e sistema de abas

## Ordem de Implementação
1. Services (heatmap → detalhes dia → padrões → insights)
2. Views + URLs
3. Templates (abas → heatmap → insights → integração)
4. JavaScript (interatividade do calendário)
5. CSS (estilos complementares)
6. Testes

## Notas
- Os dados do heat map devem ser embutidos no HTML como atributos `data-*` em cada célula, evitando chamadas AJAX desnecessárias (o sistema roda local, performance não é problema).
- O cálculo de quartis para os níveis de intensidade: Q1=25%, Q2=50%, Q3=75%. Valores abaixo de Q1=nível 1, Q1-Q2=nível 2, Q2-Q3=nível 3, acima Q3=nível 4.
- Se o mês tiver menos de 4 dias com gastos, exibir mensagem "Dados insuficientes para gerar heat map".
- Os insights devem ser gerados mesmo com poucos dados, mas com mensagens adaptadas (ex: "Ainda não há dados suficientes para identificar padrões semanais").
- Este módulo e o Módulo 4 compartilham a mesma URL base (`/financas/calendario/`) e são diferenciados pelo parâmetro `?aba=heatzone` ou `?aba=receita_despesa`.

---
**Criado em**: 2026-03-25
**Concluído em**: —
