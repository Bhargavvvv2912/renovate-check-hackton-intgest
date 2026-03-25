---
titulo: "Módulo 4 — Balança de Receitas × Despesas por Dia"
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
  - ".github/plans/active/modulo-3-heatzone.md"
---

# Plano: Módulo 4 — Balança de Receitas × Despesas por Dia

## Objetivo
Exibir, dentro do calendário financeiro (segunda aba), o equilíbrio diário entre receitas e despesas de forma visual e interativa, utilizando mini gráficos de pizza em cada dia do calendário.

## Análise de Impacto

### Arquivos existentes que serão MODIFICADOS
| Arquivo | Alteração |
|---------|-----------|
| `financas/services.py` | Adicionar função de balança diária |
| `financas/views.py` | Alterar `calendario_view` para fornecer dados da aba receita×despesa |

### Arquivos NOVOS que serão criados
| Arquivo | Descrição |
|---------|-----------|
| `templates/components/calendario_receita_despesa.html` | Componente do calendário com gráficos de pizza |
| `static/js/calendario_pizza.js` | JS para renderizar mini gráficos de pizza por dia |

### Arquivos COMPARTILHADOS com Módulo 3 (já criados)
| Arquivo | Uso |
|---------|-----|
| `templates/financas/calendario.html` | Tela principal — já suporta abas |
| `templates/components/calendario_abas.html` | Componente de abas — já suporta esta aba |

## Lógica de Cálculo

### Fórmula por Dia
```
receitas_dia = SUM(receitas do dia)
despesas_dia = SUM(despesas do dia)
total_dia = receitas_dia + despesas_dia

percentual_receita = (receitas_dia / total_dia) × 100
percentual_despesa = (despesas_dia / total_dia) × 100
```

### Classificação Visual
| Cenário | Cor Receita | Cor Despesa | Comportamento |
|---------|-------------|-------------|---------------|
| Só receitas | 🟢 100% | — | Pizza verde completa |
| Mais receita que despesa | 🟢 70% | 🔴 30% | Pizza majoritariamente verde |
| Equilíbrio | 🟢 50% | 🔴 50% | Pizza meio a meio |
| Mais despesa que receita | 🟢 30% | 🔴 70% | Pizza majoritariamente vermelha |
| Só despesas | — | 🔴 100% | Pizza vermelha completa |
| Sem lançamento | — | — | Célula vazia (cinza claro) |

## Escopo

### Backend — Services (financas/services.py)

- [ ] **`gerar_dados_balanca_diaria(user, mes, ano)`**
  - Para cada dia do mês, calcular:
    - Total de receitas do dia
    - Total de despesas do dia
    - Percentual de receitas (sobre total do dia)
    - Percentual de despesas (sobre total do dia)
  - Retornar dict por dia:
    ```python
    {
        1: {
            'receitas': Decimal('500.00'),
            'despesas': Decimal('200.00'),
            'total': Decimal('700.00'),
            'percentual_receita': 71.4,
            'percentual_despesa': 28.6,
            'tem_dados': True,
        },
        2: {
            'receitas': Decimal('0'),
            'despesas': Decimal('0'),
            'total': Decimal('0'),
            'percentual_receita': 0,
            'percentual_despesa': 0,
            'tem_dados': False,
        },
        ...
    }
    ```
  - Usar `annotate` com `TruncDay` para eficiência (2 queries: uma para receitas, uma para despesas)
  - Isolamento obrigatório por `user_id`

- [ ] **`obter_resumo_balanca_mensal(user, mes, ano)`**
  - Calcular totais agregados do mês:
    - Total de receitas do mês
    - Total de despesas do mês
    - Saldo do mês
    - Dias com receita > despesa (dias "verdes")
    - Dias com despesa > receita (dias "vermelhos")
    - Dias equilibrados
  - Retornar dict para exibir resumo abaixo do calendário

### Backend — Views

- [ ] **Alterar `calendario_view`** — Adicionar dados da aba receita×despesa
  - Quando `aba_ativa == 'receita_despesa'`:
    - Chamar `gerar_dados_balanca_diaria(user, mes, ano)`
    - Chamar `obter_resumo_balanca_mensal(user, mes, ano)`
    - Adicionar ao contexto: `dados_balanca`, `resumo_balanca`
  - Carregar dados apenas da aba ativa (evitar cálculos desnecessários)
  - O contexto da view fica:
    ```python
    contexto = {
        'mes': mes,
        'ano': ano,
        'aba_ativa': aba,
        # Aba Heat Zone (Módulo 3)
        'dados_heatmap': ... if aba == 'heatzone' else None,
        'insights': ... if aba == 'heatzone' else None,
        # Aba Receita × Despesa (Módulo 4)
        'dados_balanca': ... if aba == 'receita_despesa' else None,
        'resumo_balanca': ... if aba == 'receita_despesa' else None,
    }
    ```

### Backend — URLs

- [ ] Nenhuma URL nova — reutiliza as URLs do Módulo 3 (`/financas/calendario/`) com parâmetro `?aba=receita_despesa`

### Frontend — Templates

- [ ] **`templates/components/calendario_receita_despesa.html`** — Calendário com mini gráficos de pizza
  - **Grid**: 7 colunas (Seg-Dom) × N linhas (semanas do mês)
  - **Cada célula COM dados**:
    - Número do dia (topo esquerdo)
    - Mini gráfico de pizza (SVG ou Canvas, centralizado)
    - % receita em verde, % despesa em vermelho
    - Cursor pointer, clicável
  - **Cada célula SEM dados**:
    - Número do dia
    - Fundo cinza claro (`bg-gray-50`)
    - Sem gráfico
  - **Legenda**:
    - 🟢 Receita / 🔴 Despesa
  - **Modal/painel** de detalhes ao clicar em um dia:
    - Reutilizar o mesmo painel do Módulo 3 (`obter_detalhes_dia`)
    - Exibir receitas e despesas separadas
    - Exibir percentuais e totais
  - **Resumo mensal** abaixo do calendário:
    - Cards: Total Receitas | Total Despesas | Saldo do Mês
    - Contadores: X dias verdes | Y dias vermelhos
  - **Responsivo**: em mobile, mini pizzas menores ou substituídas por barras coloridas

- [ ] **Ajustar `templates/financas/calendario.html`**
  - Adicionar `{% include 'components/calendario_receita_despesa.html' %}` no bloco de conteúdo da aba receita_despesa
  - Garantir que apenas o conteúdo da aba ativa é renderizado

### Frontend — JavaScript

- [ ] **`static/js/calendario_pizza.js`** — Mini gráficos de pizza
  - **Opção A (recomendada): SVG inline** — cada mini pizza é um `<svg>` com arcos
    - Vantagem: leve, sem dependência, renderizado no servidor via template
    - Cada célula recebe os percentuais como `data-*` attributes
    - JS preenche os SVGs no `DOMContentLoaded`
  - **Opção B: Chart.js mini** — reutilizar Chart.js (já no projeto)
    - Desvantagem: criar ~31 instâncias de gráfico pode ser pesado
  - **Decisão**: usar SVG inline (Opção A) para performance
  - Ao clicar em um dia: mostrar modal de detalhes (reutilizar do Módulo 3)

### Frontend — CSS

- [ ] Estilos para o SVG das mini pizzas
  - Cores: verde (`#22c55e`) para receita, vermelho (`#ef4444`) para despesa
  - Transição suave no hover (scale up do gráfico)
  - Responsivo: tamanho do SVG adapta ao container

### Testes

- [ ] **`tests/test_services.py`** — Testes para funções de balança
  - `gerar_dados_balanca_diaria`:
    - Dia com receitas e despesas → percentuais corretos
    - Dia só com receitas → 100% receita
    - Dia só com despesas → 100% despesa
    - Dia sem lançamentos → `tem_dados: False`
    - Mês completo → todos os dias preenchidos
    - Isolamento por user_id
  - `obter_resumo_balanca_mensal`:
    - Totais calculados corretamente
    - Contagem de dias verdes/vermelhos precisa
    - Isolamento por user_id

- [ ] **`tests/test_views_financas.py`** — Testes para aba receita×despesa
  - `calendario_view` com `?aba=receita_despesa`: contexto contém `dados_balanca`
  - Dados calculados corretamente
  - Requer autenticação
  - Isolamento por user_id

- [ ] **`tests/conftest.py`** — Fixtures
  - Reutilizar fixtures do Módulo 3 (despesas distribuídas)
  - Adicionar receitas distribuídas em vários dias para testar balança

### Infra

- [ ] Nenhuma dependência nova
- [ ] Nenhuma migration necessária
- [ ] Nenhum model novo

## Critérios de Aceite
1. [ ] Aba "Receita × Despesa" funciona no calendário
2. [ ] Cada dia com lançamentos exibe mini gráfico de pizza
3. [ ] Cores: verde para receita, vermelho para despesa
4. [ ] Percentuais calculados corretamente
5. [ ] Ao clicar em um dia, exibe detalhes das transações
6. [ ] Dias sem lançamento exibem célula vazia
7. [ ] Resumo mensal é exibido abaixo do calendário
8. [ ] Responsivo em mobile
9. [ ] Isolamento por user_id em todas as queries
10. [ ] Testes passam com 100% de cobertura dos cenários

## Dependências
- **Módulo 3 (Heat Zone)** — OBRIGATÓRIO implementar antes. Este módulo reutiliza:
  - Tela `calendario.html` e sistema de abas
  - Componente `calendario_abas.html`
  - Função `obter_detalhes_dia` para o modal de clique
  - View `calendario_view` (que será estendida)
  - URLs do calendário

## Ordem de Implementação
1. Services (balança diária → resumo mensal)
2. Views (alterar calendario_view)
3. Templates (componente receita_despesa → integração no calendario)
4. JavaScript (mini pizzas SVG)
5. Testes

## Notas
- O SVG de mini pizza pode ser gerado diretamente no template Django usando a fórmula de arco SVG:
  ```html
  <svg viewBox="0 0 36 36" class="w-10 h-10">
    <circle cx="18" cy="18" r="16" fill="#ef4444" />
    <path d="M18 2 A16 16 0 {{ large_arc }} 1 {{ end_x }} {{ end_y }} L18 18"
          fill="#22c55e" />
  </svg>
  ```
  Onde `large_arc` e as coordenadas são calculadas no backend com base no percentual.
- Para simplificar, o backend pode pré-calcular as coordenadas SVG e passá-las diretamente ao template via contexto, eliminando a necessidade de JavaScript para os gráficos.
- Alternativa mais simples ao SVG: usar `conic-gradient` CSS para criar os gráficos de pizza puramente com CSS — requer menos código e funciona bem para gráficos simples.
- Se o dia tiver valor total = 0 (sem lançamentos), não renderizar gráfico nenhum.
- Os mini gráficos devem ser pequenos (40×40px) para caber na célula do calendário sem poluir visualmente.

---
**Criado em**: 2026-03-25
**Concluído em**: —
