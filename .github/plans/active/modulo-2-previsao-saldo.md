---
titulo: "Módulo 2 — Previsão de Saldo até o Fim do Mês"
status: "planejado"
prioridade: "alta"
context_files:
  - ".github/context/business-rules.md"
  - ".github/context/tech-constraints.md"
  - ".github/context/domain-glossary.md"
  - "financas/models.py"
  - "financas/services.py"
  - "financas/views.py"
  - "financas/urls.py"
  - "templates/financas/dashboard.html"
---

# Plano: Módulo 2 — Previsão de Saldo até o Fim do Mês

## Objetivo
Responder à pergunta "vou ficar no vermelho?" com base em dados reais e projetados. Exibir no dashboard um card com o saldo projetado para o final do mês, considerando despesas fixas pendentes, média de gastos variáveis e receitas esperadas.

## Análise de Impacto

### Arquivos existentes que serão MODIFICADOS
| Arquivo | Alteração |
|---------|-----------|
| `financas/services.py` | Adicionar funções de projeção de saldo |
| `financas/views.py` | Alterar `dashboard_view` para incluir projeção no contexto |
| `templates/financas/dashboard.html` | Adicionar card de previsão de saldo |

### Arquivos NOVOS que serão criados
| Arquivo | Descrição |
|---------|-----------|
| `templates/components/previsao_saldo.html` | Componente visual do card de previsão |

## Lógica de Cálculo

### Fórmula
```
saldo_projetado = saldo_atual
                  - despesas_fixas_restantes
                  - media_gastos_variaveis_restantes
                  + receitas_previstas_restantes
```

### Detalhamento dos Componentes
| Componente | Descrição | Cálculo |
|------------|-----------|---------|
| **Saldo atual** | Valor disponível no momento da consulta | `calcular_saldo(user)['saldo']` — já existe em services.py |
| **Despesas fixas restantes** | Compromissos conhecidos com `natureza='fixa'` ainda não lançados no mês | Filtrar despesas fixas históricas (meses anteriores) que não possuem lançamento equivalente no mês atual |
| **Média de gastos variáveis restantes** | Baseada em histórico dos últimos 3 meses | Calcular média diária de despesas variáveis × dias restantes no mês |
| **Receitas previstas restantes** | Salário, recorrências e outras receitas esperadas | Receitas fixas históricas que ainda não foram lançadas no mês atual |

### Algoritmo Detalhado

```python
def calcular_previsao_saldo(user, mes, ano):
    hoje = date.today()
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = ultimo_dia_do_mes(ano, mes)
    dias_restantes = (ultimo_dia - hoje).days
    
    # 1. Saldo atual (receitas - despesas até hoje no mês)
    saldo_atual = calcular_saldo_por_periodo(user, primeiro_dia, hoje)
    
    # 2. Despesas fixas restantes
    # Buscar despesas fixas dos últimos 3 meses
    # Verificar quais NÃO foram lançadas neste mês ainda
    despesas_fixas_pendentes = identificar_despesas_fixas_pendentes(user, mes, ano)
    
    # 3. Média de gastos variáveis (dos últimos 3 meses)
    media_diaria_variavel = calcular_media_diaria_gastos_variaveis(user)
    gastos_variaveis_projetados = media_diaria_variavel * dias_restantes
    
    # 4. Receitas previstas restantes
    receitas_previstas = identificar_receitas_previstas_pendentes(user, mes, ano)
    
    # Projeção final
    saldo_projetado = (
        saldo_atual['saldo']
        - despesas_fixas_pendentes
        - gastos_variaveis_projetados
        + receitas_previstas
    )
    
    return {
        'saldo_atual': saldo_atual['saldo'],
        'despesas_fixas_pendentes': despesas_fixas_pendentes,
        'gastos_variaveis_projetados': gastos_variaveis_projetados,
        'receitas_previstas': receitas_previstas,
        'saldo_projetado': saldo_projetado,
        'dias_restantes': dias_restantes,
        'negativo': saldo_projetado < 0,
    }
```

## Escopo

### Backend — Services (financas/services.py)

- [ ] **`identificar_despesas_fixas_pendentes(user, mes, ano)`**
  - Buscar despesas com `natureza='fixa'` dos últimos 3 meses que se repetem
  - Agrupar por `descricao` + `categoria` para identificar recorrências
  - Verificar quais não possuem lançamento equivalente no mês atual
  - Retornar soma dos valores pendentes
  - Regra: considerar apenas despesas que apareceram em pelo menos 2 dos últimos 3 meses

- [ ] **`identificar_receitas_previstas_pendentes(user, mes, ano)`**
  - Mesma lógica das despesas fixas, mas para receitas com `natureza='fixa'`
  - Buscar receitas fixas recorrentes dos últimos 3 meses
  - Verificar quais ainda não foram lançadas no mês atual
  - Retornar soma dos valores previstos

- [ ] **`calcular_media_diaria_gastos_variaveis(user)`**
  - Filtrar despesas com `natureza='variavel'` dos últimos 3 meses
  - Calcular total de dias no período
  - Retornar média diária = total_variavel / total_dias
  - Se não houver dados, retornar Decimal('0')

- [ ] **`calcular_previsao_saldo(user, mes=None, ano=None)`**
  - Orquestrar os 3 sub-cálculos acima
  - Parâmetros `mes` e `ano` defaultam para mês/ano atual
  - Retornar dict completo com todos os componentes da projeção
  - Incluir flag `negativo` quando saldo projetado < 0

- [ ] **`ultimo_dia_do_mes(ano, mes)`** — Função utilitária
  - Retornar o último dia do mês (28, 29, 30 ou 31)
  - Usar `calendar.monthrange`

### Backend — Views

- [ ] **Alterar `dashboard_view`** — Adicionar `previsao` ao contexto
  ```python
  previsao = calcular_previsao_saldo(usuario)
  contexto['previsao'] = previsao
  ```

### Frontend — Templates

- [ ] **`templates/components/previsao_saldo.html`** — Card de previsão
  - **Layout**: Card com título "Previsão de Saldo — Fim do Mês"
  - **Conteúdo**:
    - Saldo projetado em destaque (grande, negrito)
    - Cor verde se positivo, vermelho se negativo
    - Breakdown dos componentes em lista:
      - Saldo atual: R$ X.XXX,XX
      - (-) Despesas fixas pendentes: R$ X.XXX,XX
      - (-) Gastos variáveis projetados: R$ X.XXX,XX
      - (+) Receitas previstas: R$ X.XXX,XX
      - = Saldo projetado: R$ X.XXX,XX
    - Texto "X dias restantes no mês"
  - **Alerta visual**: Se saldo negativo, exibir banner vermelho com "⚠️ Atenção: você pode ficar no vermelho!"
  - **Responsivo** com Tailwind

- [ ] **`templates/financas/dashboard.html`** — Integrar card de previsão
  - Adicionar `{% include 'components/previsao_saldo.html' %}` após os cards de resumo (saldo, receitas, despesas) e antes dos gráficos
  - Card ocupa largura total (span-3 no grid)

### Testes

- [ ] **`tests/test_services.py`** — Testes para funções de projeção
  - `identificar_despesas_fixas_pendentes`:
    - Cenário com despesas fixas recorrentes → retorna soma correta
    - Cenário com despesas já lançadas no mês → exclui do resultado
    - Cenário sem histórico → retorna 0
  - `identificar_receitas_previstas_pendentes`:
    - Cenário com receitas fixas recorrentes → retorna soma correta
    - Cenário com receitas já lançadas → exclui
  - `calcular_media_diaria_gastos_variaveis`:
    - Cenário com dados → retorna média correta
    - Cenário sem dados → retorna 0
  - `calcular_previsao_saldo`:
    - Cenário saldo positivo projetado
    - Cenário saldo negativo projetado
    - Cenário sem dados suficientes
  - **Isolamento**: cada teste verifica que dados de outro user_id são ignorados

- [ ] **`tests/test_views_financas.py`** — Dashboard inclui previsão
  - Verifica que `previsao` está no contexto
  - Verifica que valores são coerentes

- [ ] **`tests/conftest.py`** — Adicionar fixtures
  - Fixtures com despesas fixas recorrentes em meses anteriores
  - Fixtures com receitas fixas recorrentes
  - Fixtures com despesas variáveis em período de 3 meses

### Infra

- [ ] Nenhum model novo (usa dados existentes de Receita e Despesa)
- [ ] Nenhuma dependência nova (usa `calendar` da stdlib)
- [ ] Nenhuma migration necessária

## Critérios de Aceite
1. [ ] Dashboard exibe card de previsão de saldo
2. [ ] Saldo projetado é calculado corretamente com os 4 componentes
3. [ ] Alerta visual aparece quando saldo projetado é negativo
4. [ ] Breakdown dos componentes é exibido
5. [ ] Dias restantes no mês é exibido corretamente
6. [ ] Funciona corretamente em qualquer dia do mês
7. [ ] Isolamento por user_id garantido em todas as queries
8. [ ] Cenário sem histórico suficiente exibe mensagem informativa
9. [ ] Testes passam com 100% de cobertura dos cenários

## Dependências
- Nenhuma dependência de outros módulos novos. Usa models existentes (`Receita`, `Despesa`) e serviços existentes (`calcular_saldo`, `calcular_saldo_por_periodo`).
- **Este módulo é dependência do Módulo 1** (Alertas Inteligentes) — o alerta de saldo baixo reutiliza `calcular_previsao_saldo`.

## Ordem de Implementação
1. Services (funções utilitárias → sub-cálculos → função principal)
2. Views (alterar dashboard_view)
3. Templates (componente → integração no dashboard)
4. Testes

## Notas
- A lógica de identificação de despesas/receitas recorrentes é baseada em padrão de repetição: um lançamento que aparece em pelo menos 2 dos últimos 3 meses, com mesmo `descricao` e `categoria`, é considerado recorrente.
- Para o primeiro mês de uso do sistema (sem histórico), exibir mensagem "Dados insuficientes para projeção — continue registrando seus lançamentos".
- A média de gastos variáveis deve excluir meses com menos de 5 lançamentos, para evitar distorção.
- Considerar usar `calendar.monthrange` para calcular o último dia do mês corretamente (incluindo anos bissextos).
- **Recomendação de ordem global**: Implementar este módulo ANTES do Módulo 1, pois o alerta de saldo baixo depende da projeção de saldo.

---
**Criado em**: 2026-03-25
**Concluído em**: —
