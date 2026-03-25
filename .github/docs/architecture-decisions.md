# Decisões Arquiteturais — Gestão Financeira SaaS

## Registro de Decisões (ADR)

### ADR-001: Multi-tenancy por user_id
- **Data**: 2026-03-25
- **Status**: Aceita
- **Contexto**: Precisamos isolar dados entre clientes no modelo SaaS.
- **Decisão**: Usar campo `user_id` (FK para User) em todas as tabelas de negócio, filtrando queries por `request.user`.
- **Alternativas descartadas**: Schema separado por tenant (complexo demais para SQLite), banco separado por tenant (desnecessário para escala local).
- **Consequências**: Toda query e toda view deve garantir o filtro. Criar mixins/decorators para padronizar.

### ADR-002: Models separados para Receita e Despesa
- **Data**: 2026-03-25
- **Status**: Aceita
- **Contexto**: Precisamos registrar entradas e saídas financeiras.
- **Decisão**: Criar models `Receita` e `Despesa` separados ao invés de um model `Lancamento` com campo `tipo`.
- **Alternativas descartadas**: Model único com discriminador — menor flexibilidade para campos específicos.
- **Consequências**: Saldo = sum(receitas) - sum(despesas). Queries em dois models nas agregações.

### ADR-003: SSR com Templates Django + Tailwind
- **Data**: 2026-03-25
- **Status**: Aceita
- **Contexto**: Precisamos de interfaces web sem SPA.
- **Decisão**: Server-Side Rendering com templates Django e Tailwind CSS via CDN.
- **Alternativas descartadas**: React (proibido), Bootstrap (menos moderno).
- **Consequências**: JavaScript apenas para interações pontuais (Chart.js, modais).

### ADR-004: Sem admin nativo do Django
- **Data**: 2026-03-25
- **Status**: Aceita
- **Contexto**: UX personalizada é requisito do projeto.
- **Decisão**: Construir toda interface administrativa com templates próprios.
- **Consequências**: Mais trabalho de frontend, mas UX consistente e controlada.

---
*Novas decisões devem seguir o formato ADR acima.*
