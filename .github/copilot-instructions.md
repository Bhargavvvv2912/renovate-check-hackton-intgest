# Regras Globais do Projeto — Gestão Financeira SaaS

> Este arquivo é lido automaticamente em toda conversa com o Copilot.
> Define regras invioláveis válidas para qualquer agente ou contexto.

## Idioma
- Toda comunicação, comentários de código, variáveis, docstrings e mensagens de commit devem ser em **português brasileiro (pt-BR)**.
- Nomes de classes, funções e variáveis seguem convenções Python (snake_case), mas podem usar termos em português quando melhorar a legibilidade do domínio.

## Stack Obrigatória
| Camada     | Tecnologia           |
|------------|----------------------|
| Linguagem  | Python 3.12+         |
| Framework  | Django 5.x           |
| Banco      | SQLite               |
| Front-end  | Templates Django + Tailwind CSS |
| Editor     | VS Code              |
| IA         | GitHub Copilot        |

## Proibições Absolutas
- **NUNCA** usar Django REST Framework.
- **NUNCA** usar Docker ou qualquer containerização.
- **NUNCA** usar React ou qualquer framework JS SPA.
- **NUNCA** usar Celery ou filas de tarefas.
- **NUNCA** configurar ambiente de produção — a aplicação roda **somente local**.
- **NUNCA** fazer commit automático sem aprovação explícita do usuário.
- **NUNCA** incluir segredos, senhas ou chaves no código-fonte.
- **NUNCA** usar o admin nativo do Django (`/admin/`) — toda interface deve ser construída com templates próprios.
- **NUNCA** executar ações destrutivas (drop, delete em massa, reset) sem confirmação do usuário.

## Arquitetura Multi-Tenant (por user_id)
- O sistema é **SaaS** com isolamento por `user_id`.
- **Toda** tabela de dados de negócio deve conter um campo `user_id` (FK para User).
- Queries devem **sempre** filtrar por `user_id` do usuário autenticado.
- Existe um **superusuário** que administra todos os clientes via dashboard próprio.
- Clientes inativos devem ver uma tela de bloqueio solicitando contato com suporte.

## Padrões de Código
- Seguir PEP 8.
- Usar type hints quando possível.
- Models devem ter `__str__` e `class Meta` definidos.
- Views baseadas em classe (CBV) são preferidas, mas function-based views (FBV) são aceitas quando mais simples.
- Forms devem usar Django Forms/ModelForms com validação server-side.
- Templates devem estender um `base.html` com estrutura Tailwind.

## Segurança
- Autenticação obrigatória para todas as rotas exceto landing page, login e registro.
- Proteção CSRF em todos os formulários.
- Validação e sanitização de inputs no servidor.
- Nunca expor IDs internos desnecessariamente.

## Fluxo Obrigatório Pós-Implementação (Code Review Automático)
- **Após toda alteração finalizada** por qualquer agente (backend, frontend, infra, planner), o agente **CodeReview** deve ser acionado automaticamente.
- O CodeReview **analisa e reporta** problemas de segurança, qualidade, convenções e isolamento multi-tenant. Ele **NÃO edita código** — apenas diagnostica.
- Quando o CodeReview encontra problemas, o **Senior delega a correção ao subagent especializado** (backend, frontend, etc.).
- Após a correção, o **CodeReview revisa novamente** — este ciclo repete até aprovação total.
- Fluxo:
  1. Subagent implementa → entrega código.
  2. **CodeReview** → revisa e reporta problemas encontrados.
  3. Se reprovado → **Senior delega ao subagent especializado** para corrigir.
  4. **CodeReview** revisa novamente (loop até aprovado).
  5. **TestAgent** → cria/roda testes para validar.
  6. Se testes falham → subagent corrige + CodeReview revisa.
  7. Suíte global de testes (`pytest`) ao final de cada feature.
- Este fluxo é **inviolável** — nenhuma implementação é considerada concluída sem passar pelo CodeReview.

## Navegação de Contexto
- Para instruções detalhadas por área, consulte `.github/instructions/central.md`.
- Para regras de negócio, consulte `.github/context/business-rules.md`.
- Para glossário do domínio, consulte `.github/context/domain-glossary.md`.
- Para decisões técnicas, consulte `.github/context/tech-constraints.md`.
