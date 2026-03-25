---
titulo: "Módulo 1 — Alertas Inteligentes"
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
  - "templates/base.html"
---

# Plano: Módulo 1 — Alertas Inteligentes

## Objetivo
Notificar o usuário proativamente antes de situações financeiras problemáticas, por meio de mensagens interativas e configuráveis exibidas no dashboard. O módulo inclui três tipos de alerta: orçamento, gasto acelerado e saldo baixo previsto.

## Análise de Impacto

### Arquivos existentes que serão MODIFICADOS
| Arquivo | Alteração |
|---------|-----------|
| `financas/models.py` | Adicionar model `ConfiguracaoAlerta` e `Orcamento` |
| `financas/services.py` | Adicionar funções de cálculo de alertas |
| `financas/views.py` | Alterar `dashboard_view` para injetar alertas no contexto |
| `financas/urls.py` | Adicionar rota para configuração de alertas e orçamento |
| `financas/forms.py` | Adicionar `ConfiguracaoAlertaForm` e `OrcamentoForm` |
| `templates/financas/dashboard.html` | Adicionar seção de alertas |
| `templates/base.html` | Adicionar ícone de sino com badge de alertas na navbar |
| `tests/conftest.py` | Adicionar fixtures para alertas |

### Arquivos NOVOS que serão criados
| Arquivo | Descrição |
|---------|-----------|
| `templates/financas/configuracao_alertas.html` | Tela de configuração dos limiares de alerta |
| `templates/financas/orcamento_form.html` | Tela para definir orçamento mensal |
| `templates/components/alertas.html` | Componente reutilizável de exibição de alertas |
| `financas/migrations/0002_alertas.py` | Gerada automaticamente |

## Escopo

### Backend — Models

- [ ] **Model `Orcamento`** — Armazena o orçamento mensal do usuário
  ```python
  class Orcamento(BaseModel):
      mes = models.PositiveIntegerField()  # 1-12
      ano = models.PositiveIntegerField()
      valor = models.DecimalField(max_digits=12, decimal_places=2)
      
      class Meta:
          unique_together = ['user', 'mes', 'ano']
  ```

- [ ] **Model `ConfiguracaoAlerta`** — Preferências de alerta por usuário (1:1 com User)
  ```python
  class ConfiguracaoAlerta(BaseModel):
      # Alerta de orçamento
      alerta_orcamento_ativo = models.BooleanField(default=True)
      limiar_orcamento = models.PositiveIntegerField(default=80)  # percentual
      
      # Alerta de gasto acelerado
      alerta_gasto_acelerado_ativo = models.BooleanField(default=True)
      
      # Alerta de saldo baixo previsto
      alerta_saldo_baixo_ativo = models.BooleanField(default=True)
      limite_saldo_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
      
      class Meta:
          verbose_name = 'Configuração de Alerta'
          verbose_name_plural = 'Configurações de Alerta'
  ```

- [ ] **Migration** — Gerar e aplicar migration para os novos models

### Backend — Services (financas/services.py)

- [ ] **`verificar_alerta_orcamento(user, mes, ano)`**
  - Buscar `Orcamento` do mês/ano
  - Calcular total de despesas do mês
  - Comparar com `limiar_orcamento` da `ConfiguracaoAlerta`
  - Retornar dict com `ativo`, `percentual_consumido`, `mensagem`
  - Exemplo: `{"ativo": True, "percentual": 85, "mensagem": "Você já consumiu 85% do seu orçamento de março."}`

- [ ] **`verificar_alerta_gasto_acelerado(user)`**
  - Calcular gasto da semana atual (seg-dom)
  - Calcular média semanal histórica (últimos 3 meses)
  - Se gasto atual > média × 1.2 (20% acima), gerar alerta
  - Retornar dict com `ativo`, `gasto_semana`, `media_semanal`, `mensagem`
  - Exemplo: `{"ativo": True, "gasto_semana": 850.00, "media_semanal": 600.00, "mensagem": "Você está gastando mais rápido do que o normal esta semana."}`

- [ ] **`verificar_alerta_saldo_baixo(user, mes, ano)`**
  - Calcular saldo projetado no fim do mês (reutilizar lógica do Módulo 2)
  - Comparar com `limite_saldo_minimo` da `ConfiguracaoAlerta`
  - Retornar dict com `ativo`, `saldo_projetado`, `limite`, `mensagem`

- [ ] **`obter_todos_alertas(user)`**
  - Agrupar os 3 alertas em uma lista unificada
  - Garantir que respeita configurações ativo/inativo do usuário
  - Retornar lista de dicts prontos para o template

### Backend — Views

- [ ] **Alterar `dashboard_view`** — Chamar `obter_todos_alertas(user)` e adicionar ao contexto
- [ ] **`ConfiguracaoAlertaView`** — CBV para editar `ConfiguracaoAlerta` (UpdateView ou FBV com get_or_create)
- [ ] **`OrcamentoCreateView` / `OrcamentoUpdateView`** — CRUD de orçamento mensal

### Backend — Forms

- [ ] **`ConfiguracaoAlertaForm`** — ModelForm para `ConfiguracaoAlerta`
  - Campos: `alerta_orcamento_ativo`, `limiar_orcamento`, `alerta_gasto_acelerado_ativo`, `alerta_saldo_baixo_ativo`, `limite_saldo_minimo`
  - Validação: `limiar_orcamento` entre 1-100, `limite_saldo_minimo` >= 0

- [ ] **`OrcamentoForm`** — ModelForm para `Orcamento`
  - Campos: `mes`, `ano`, `valor`
  - Validação: valor > 0, mês entre 1-12

### Backend — URLs

- [ ] `financas/alertas/configuracao/` → `ConfiguracaoAlertaView` → nome: `configuracao_alertas`
- [ ] `financas/orcamento/` → lista de orçamentos → nome: `orcamento_lista`
- [ ] `financas/orcamento/novo/` → criar orçamento → nome: `orcamento_criar`
- [ ] `financas/orcamento/<int:pk>/editar/` → editar orçamento → nome: `orcamento_editar`

### Frontend — Templates

- [ ] **`templates/components/alertas.html`** — Componente de alertas
  - Card com ícone por tipo (🔔 orçamento, ⚡ gasto acelerado, ⚠️ saldo baixo)
  - Cores: amarelo para avisos, vermelho para críticos
  - Barra de progresso para alerta de orçamento
  - Botão "Configurar alertas" → link para configuração
  - Responsivo com Tailwind

- [ ] **`templates/financas/dashboard.html`** — Adicionar seção de alertas
  - Include `components/alertas.html` no topo do dashboard, abaixo dos cards de saldo
  - Exibir alertas ativos de forma destacada

- [ ] **`templates/financas/configuracao_alertas.html`** — Formulário de configuração
  - Switches (toggles) para ativar/desativar cada tipo de alerta
  - Input para limiar de orçamento (slider ou number)
  - Input para limite de saldo mínimo
  - Botão salvar

- [ ] **`templates/financas/orcamento_form.html`** — Formulário de orçamento
  - Campos: mês (select), ano, valor
  - Estilo consistente com os demais forms

- [ ] **`templates/base.html`** — Badge na navbar
  - Ícone de sino (🔔) ao lado do username
  - Badge numérico com quantidade de alertas ativos
  - Link para dashboard com scroll até seção de alertas

### Testes

- [ ] **`tests/test_models.py`** — Testes para `Orcamento` e `ConfiguracaoAlerta`
  - Criação, validação, constraint unique
  - Isolamento por user_id
- [ ] **`tests/test_services.py`** — Testes para funções de alerta
  - `verificar_alerta_orcamento`: cenários com/sem orçamento, abaixo/acima do limiar
  - `verificar_alerta_gasto_acelerado`: cenário normal, cenário acelerado, sem histórico
  - `verificar_alerta_saldo_baixo`: cenário positivo, cenário negativo
  - `obter_todos_alertas`: configurações ativo/inativo respeitadas
- [ ] **`tests/test_views_financas.py`** — Testes para views de alerta
  - Dashboard inclui alertas no contexto
  - Configuração de alertas: GET exibe form, POST salva
  - Orçamento CRUD: criar, editar, validações
  - Isolamento: usuário A não vê orçamento do usuário B
- [ ] **`tests/test_forms_financas.py`** — Testes para forms de alerta
  - `ConfiguracaoAlertaForm`: validação de limiar (1-100)
  - `OrcamentoForm`: validação de valor > 0

### Infra

- [ ] Nenhuma dependência nova necessária
- [ ] Migration para novos models

## Critérios de Aceite
1. [ ] Usuário vê alertas no dashboard quando condições são atendidas
2. [ ] Usuário pode configurar limiares de alerta
3. [ ] Usuário pode definir orçamento mensal
4. [ ] Alerta de orçamento dispara no percentual configurado
5. [ ] Alerta de gasto acelerado compara com média histórica
6. [ ] Alerta de saldo baixo usa projeção de saldo
7. [ ] Alertas desativados não aparecem
8. [ ] Isolamento por user_id em todos os models e queries
9. [ ] Testes passam com 100% de cobertura dos cenários
10. [ ] Navbar mostra badge com quantidade de alertas

## Dependências
- Módulo 2 (Previsão de Saldo) — a lógica de projeção de saldo será reutilizada pelo alerta de saldo baixo. **Recomendação**: implementar Módulo 2 primeiro, ou extrair a lógica de projeção como função compartilhada.

## Ordem de Implementação
1. Models + Migration
2. Services (funções de cálculo)
3. Forms
4. Views + URLs
5. Templates (componente de alertas → dashboard → configuração → orçamento)
6. Testes

## Notas
- A `ConfiguracaoAlerta` deve ser criada automaticamente (get_or_create) quando o usuário acessa a configuração pela primeira vez, evitando setup manual.
- Se o usuário não tiver orçamento definido, o alerta de orçamento não deve disparar (e deve sugerir "Defina seu orçamento").
- A média histórica de gastos semanais deve considerar pelo menos 4 semanas para ser significativa. Se não houver dados suficientes, exibir mensagem informativa.
- Os alertas devem ser calculados em tempo real (sem cache), dado que o sistema roda localmente.

---
**Criado em**: 2026-03-25
**Concluído em**: —
