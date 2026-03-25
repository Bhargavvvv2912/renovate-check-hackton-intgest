# Índice Mestre de Navegação — Instructions

> Este arquivo serve como ponto de entrada para localizar rapidamente as instruções de cada área do projeto.

## Mapa de Instruções

| Arquivo | Área | Descrição |
|---------|------|-----------|
| `backend.md` | Backend | Padrões Django, models, views, services, forms |
| `frontend.md` | Frontend | Templates, Tailwind CSS, componentes UI, acessibilidade |
| `infra.md` | Infraestrutura | Ambiente local, dependências, configuração |
| `tests.md` | Testes | Estratégia de testes, cobertura, fixtures |

## Mapa de Contexto

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `../context/business-rules.md` | Negócio | Regras de negócio centrais do sistema financeiro |
| `../context/domain-glossary.md` | Glossário | Vocabulário e termos do domínio |
| `../context/tech-constraints.md` | Técnico | Decisões arquiteturais e restrições |

## Mapa de Agentes

| Agente | Arquivo | Papel |
|--------|---------|-------|
| Senior | `../agents/senior.agent.md` | Orquestrador principal, roteia tarefas |
| Backend | `../agents/subagent-backend.md` | Especialista Django |
| Frontend | `../agents/subagent-frontend.md` | Especialista UI/Templates |
| Infra | `../agents/subagent-infra.md` | Especialista infraestrutura local |
| Planner | `../agents/subagent-planner.md` | Executor de features completas |
| TestAgent | `../agents/TestAgent.agent.md` | Especialista em testes |
| Explore | `../agents/Explore.agent.md` | Exploração rápida do código |

## Mapa de Skills

| Skill | Arquivo | Quem usa |
|-------|---------|----------|
| Django ORM Otimizações | `../skills/django-orm-otimizacoes.md` | subagent-backend |
| Tailwind + Django Templates | `../skills/tailwind-django-templates.md` | subagent-frontend |
| Services & Business Logic | `../skills/django-services-patterns.md` | subagent-backend |
| Segurança Multi-Tenant | `../skills/seguranca-multitenant.md` | subagent-backend, CodeReview |
| Testes Django + pytest | `../skills/testes-pytest-django.md` | TestAgent |

## Como Usar
1. **Pedido simples** → Senior lê `central.md`, identifica a área, carrega o contexto necessário e delega ao subagent correto.
2. **Feature completa** → Copie `../plans/_template.md` para `../plans/active/`, preencha e peça "execute o plano X".
3. **Dúvida de domínio** → Consulte `../context/domain-glossary.md` e `../context/business-rules.md`.

## Fluxo Obrigatório Pós-Implementação

> **Regra inviolável**: após TODA alteração finalizada por um subagent, o fluxo abaixo deve ser seguido.

```
Subagent implementa
    ↓
CodeReview (obrigatório)
    ├── Analisa segurança, qualidade, convenções, isolamento multi-tenant
    ├── Gera relatório com problemas e correções sugeridas
    └── NÃO edita código — apenas diagnostica e reporta
    ↓
Problemas encontrados?
    ├── Sim → Senior delega ao subagent especializado para corrigir
    │         ↓
    │    CodeReview revisa novamente (loop até aprovado)
    └── Não → ✅ Aprovado
    ↓
TestAgent (obrigatório)
    ├── Cria e roda testes do módulo alterado
    └── Se falhas → subagent corrige + CodeReview revisa
    ↓
Suíte global (pytest) ao final de cada feature
    ↓
Feature concluída ✅
```

### Agentes envolvidos no fluxo

| Etapa | Agente | Ação |
|-------|--------|------|
| 1. Implementação | subagent-backend/frontend/infra | Cria/edita código |
| 2. Revisão | **CodeReview** | Analisa e reporta problemas (read-only) |
| 3. Correção | subagent especializado | Corrige problemas apontados pelo CodeReview |
| 4. Re-revisão | **CodeReview** | Revisa novamente (loop até aprovado) |
| 5. Testes | **TestAgent** | Cria e roda testes |
| 6. Validação global | **TestAgent** | Roda `pytest` completo |
