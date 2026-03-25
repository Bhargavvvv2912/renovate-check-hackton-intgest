---
titulo: "Plano Mestre — Novos Módulos Financeiros"
status: "planejado"
prioridade: "alta"
context_files:
  - ".github/plans/active/modulo-1-alertas-inteligentes.md"
  - ".github/plans/active/modulo-2-previsao-saldo.md"
  - ".github/plans/active/modulo-3-heatzone.md"
  - ".github/plans/active/modulo-4-receita-x-despesa.md"
---

# Plano Mestre — Novos Módulos Financeiros

## Visão Geral

Implementação de 4 novos módulos no sistema de gestão financeira:

| # | Módulo | Prioridade | Estimativa de Subtarefas |
|---|--------|------------|--------------------------|
| 2 | Previsão de Saldo | Alta | 4 (services, view, template, testes) |
| 1 | Alertas Inteligentes | Alta | 7 (models, migration, services, forms, views, templates, testes) |
| 3 | Detecção de Padrões (Heat Zone) | Média | 6 (services, views, templates, JS, CSS, testes) |
| 4 | Balança Receita × Despesa | Média | 5 (services, view, template, JS, testes) |

**Total**: ~22 subtarefas

## Grafo de Dependências

```
Módulo 2 (Previsão de Saldo)
    │
    ▼
Módulo 1 (Alertas Inteligentes)
    │    depende da função calcular_previsao_saldo()
    │
    ╳ (independente)
    │
Módulo 3 (Heat Zone)
    │
    ▼
Módulo 4 (Receita × Despesa)
         depende da tela, abas, URLs e obter_detalhes_dia()
```

## Ordem de Execução Obrigatória

### Fase 1 — Fundação de Projeção
**Módulo 2: Previsão de Saldo**
1. `subagent-backend` → Services de projeção
2. `subagent-backend` → Alterar dashboard_view
3. `subagent-frontend` → Componente previsao_saldo + integração dashboard
4. `CodeReview` → Revisar
5. `TestAgent` → Testes de services + views

### Fase 2 — Alertas
**Módulo 1: Alertas Inteligentes**
1. `subagent-backend` → Models (Orcamento, ConfiguracaoAlerta) + migration
2. `subagent-backend` → Services de alertas
3. `subagent-backend` → Forms + Views + URLs
4. `subagent-frontend` → Templates (alertas, configuração, orçamento, badge navbar)
5. `CodeReview` → Revisar
6. `TestAgent` → Testes de models, services, views, forms

### Fase 3 — Calendário Heat Zone
**Módulo 3: Detecção de Padrões**
1. `subagent-backend` → Services de padrões e heatmap
2. `subagent-backend` → Views + URLs do calendário
3. `subagent-frontend` → Templates (calendario, abas, heatzone, insights)
4. `subagent-frontend` → JavaScript + CSS do calendário
5. `CodeReview` → Revisar
6. `TestAgent` → Testes de services + views

### Fase 4 — Calendário Receita × Despesa
**Módulo 4: Balança Diária**
1. `subagent-backend` → Services de balança diária
2. `subagent-backend` → Alterar calendario_view
3. `subagent-frontend` → Template do calendário receita×despesa
4. `subagent-frontend` → JavaScript/CSS para mini pizzas
5. `CodeReview` → Revisar
6. `TestAgent` → Testes de services + views

### Fase Final — Validação Global
1. `TestAgent` → Rodar suíte global `pytest`
2. `CodeReview` → Revisão final de toda a feature
3. Gerar checklist de revisão

## Arquivos Impactados (Consolidado)

### Arquivos EXISTENTES que serão modificados
| Arquivo | Módulos |
|---------|---------|
| `financas/models.py` | M1 |
| `financas/services.py` | M1, M2, M3, M4 |
| `financas/views.py` | M1, M2, M3, M4 |
| `financas/urls.py` | M1, M3 |
| `financas/forms.py` | M1 |
| `templates/financas/dashboard.html` | M1, M2 |
| `templates/base.html` | M1, M3 |
| `tests/conftest.py` | M1, M2, M3, M4 |
| `tests/test_services.py` | M1, M2, M3, M4 |
| `tests/test_views_financas.py` | M1, M2, M3, M4 |
| `tests/test_models.py` | M1 |
| `tests/test_forms_financas.py` | M1 |

### Arquivos NOVOS que serão criados
| Arquivo | Módulo |
|---------|--------|
| `templates/financas/configuracao_alertas.html` | M1 |
| `templates/financas/orcamento_form.html` | M1 |
| `templates/financas/calendario.html` | M3 |
| `templates/components/alertas.html` | M1 |
| `templates/components/previsao_saldo.html` | M2 |
| `templates/components/calendario_abas.html` | M3 |
| `templates/components/calendario_heatzone.html` | M3 |
| `templates/components/calendario_receita_despesa.html` | M4 |
| `templates/components/insights.html` | M3 |
| `static/js/calendario.js` | M3 |
| `static/js/calendario_pizza.js` | M4 |
| `static/css/calendario.css` | M3 |
| `financas/migrations/0002_*.py` | M1 (auto) |

## Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Lógica de recorrência incorreta (M2) | Testes com cenários variados (1 mês, 3 meses, sem dados) |
| Performance do heatmap com muito dados | Usar `annotate` + aggregation no banco, evitar N+1 |
| Conflito entre módulos no services.py | Implementar sequencialmente, CodeReview após cada módulo |
| Mini gráficos de pizza complexos no front | Usar conic-gradient CSS como fallback ao SVG |
| Dados insuficientes para projeções | Mensagens informativas em todos os cenários sem dados |

## Notas
- Todos os módulos seguem o padrão existente: isolamento por `user_id`, `BaseModel`, Tailwind CSS.
- Nenhuma dependência externa nova é necessária.
- A única migration necessária é a do Módulo 1 (novos models).
- O `financas/services.py` é o arquivo mais impactado — receberá ~15 novas funções.
- Considerar extrair os services novos em arquivo separado (`financas/services_analise.py`) se o arquivo principal ficar grande demais. Decisão durante a implementação.

---
**Criado em**: 2026-03-25
**Concluído em**: —
