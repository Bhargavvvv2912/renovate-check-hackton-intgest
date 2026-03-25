# Onboarding — Gestão Financeira SaaS

## Bem-vindo ao Projeto!
Este documento ajuda novos desenvolvedores (e o Copilot) a entender rapidamente o projeto.

## O que é o Projeto?
Sistema de **gestão financeira pessoal** no modelo **SaaS**, onde cada cliente tem sua conta isolada para registrar receitas, despesas e acompanhar seu saldo.

## Estrutura do Repositório
```
.github/
├── copilot-instructions.md    ← Regras globais do Copilot (sempre ativas)
├── PLANO-DE-PROJETO.MD        ← Plano geral do projeto
├── instructions/              ← Instruções por área (backend, frontend, etc.)
├── context/                   ← Contexto de negócio (regras, glossário, restrições)
├── agents/                    ← Agentes especializados do Copilot
├── prompts/                   ← Templates de prompts reutilizáveis
├── plans/                     ← Planos de features (active/done)
└── docs/                      ← Documentação do projeto
```

## Como Rodar (quando o projeto estiver implementado)
```bash
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Aplicar migrations
python manage.py migrate

# 4. Carregar dados demo
python manage.py seed_data

# 5. Iniciar servidor
python manage.py runserver
```

## Como Usar os Agentes Copilot
1. **Pedido simples**: faça o pedido normalmente — o Senior roteia.
2. **Feature completa**: copie `plans/_template.md` → `plans/active/nome.md`, preencha e peça "execute o plano nome".
3. **Bug**: use o template em `prompts/fix-bug.md`.
4. **Testes**: use o template em `prompts/write-tests.md`.

## Links Rápidos
| O quê | Onde |
|-------|------|
| Regras globais | `.github/copilot-instructions.md` |
| Regras de negócio | `.github/context/business-rules.md` |
| Glossário | `.github/context/domain-glossary.md` |
| Restrições técnicas | `.github/context/tech-constraints.md` |
| Índice de instruções | `.github/instructions/central.md` |
| Agentes disponíveis | `.github/agents/manifest.json` |

## Stack
| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.12+ |
| Framework | Django 5.x |
| Banco | SQLite |
| Frontend | Templates Django + Tailwind CSS |
| Testes | pytest + pytest-django |
| IA | GitHub Copilot |
