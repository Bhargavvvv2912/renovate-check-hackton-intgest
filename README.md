# FinançasPro — Sistema de Gestão Financeira Pessoal

Sistema SaaS multi-tenant de gestão financeira pessoal construído com Django 5, SQLite e Tailwind CSS. Permite controlar receitas, despesas, orçamentos e receber alertas inteligentes sobre a saúde financeira.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Estrutura do .github](#estrutura-do-github)
- [Instalação e Setup](#instalação-e-setup)
- [Dados de Demonstração (Seed)](#dados-de-demonstração-seed)
- [Rodando o Servidor](#rodando-o-servidor)
- [Rodando os Testes](#rodando-os-testes)
- [Arquitetura Multi-Tenant](#arquitetura-multi-tenant)
- [Fluxo de Navegação](#fluxo-de-navegação)
- [Modelos de Dados](#modelos-de-dados)
- [Credenciais Padrão](#credenciais-padrão)

---

## Visão Geral

O **FinançasPro** é um sistema web local de gestão financeira pessoal. Cada usuário tem acesso exclusivo apenas aos próprios dados (isolamento por `user_id`). Um superusuário pode administrar todas as contas via dashboard próprio.

---

## Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| **Landing Page** | Página pública de apresentação do sistema com CTA para registro e login |
| **Autenticação** | Registro, login, logout e perfil de usuário |
| **Dashboard** | Resumo financeiro do mês: saldo, receitas, despesas e previsão |
| **Receitas** | CRUD completo com categorias, origem, natureza e filtros |
| **Despesas** | CRUD completo com categorias, origem, natureza e filtros |
| **Categorias** | Gerenciamento de categorias personalizadas por tipo (receita/despesa) |
| **Orçamento** | Definição de limite mensal de gastos com acompanhamento em tempo real |
| **Calendário** | Visualização de lançamentos em formato calendário com drill-down por dia |
| **Alertas** | Avisos automáticos de orçamento excedido, gastos acelerados e saldo baixo |
| **Admin** | Dashboard do superusuário para ativar/desativar contas de clientes |
| **Conta Bloqueada** | Tela de bloqueio para usuários inativos |

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12+ |
| Framework | Django 5.1.4 |
| Banco de Dados | SQLite 3 |
| Front-end | Templates Django + Tailwind CSS (CDN) |
| Ícones | Lucide Icons |
| Filtros | django-filter 24.3 |
| Testes | pytest 8.3.4 + pytest-django 4.9.0 |
| Cobertura | coverage 7.6.9 |
| Relatórios | ReportLab 4.2.5 |

> ℹ️ Sem Docker, sem React, sem DRF, sem Celery. Roda 100% local.

---

## Estrutura do Projeto

```
HACKTON/
├── manage.py                    # Entry point Django
├── requirements.txt             # Dependências Python
├── setup.cfg                    # Configuração do pytest
├── db.sqlite3                   # Banco de dados SQLite
│
├── core/                        # Configuração central do Django
│   ├── settings.py              # Configurações gerais
│   ├── urls.py                  # URLs raiz (landing + usuarios + financas)
│   ├── asgi.py
│   └── wsgi.py
│
├── financas/                    # App principal — lógica financeira
│   ├── models.py                # Categoria, Receita, Despesa, Orcamento, ConfiguracaoAlerta
│   ├── views.py                 # Views CBV e FBV para todos os módulos
│   ├── forms.py                 # Formulários Django com validação server-side
│   ├── services.py              # Regras de negócio (alertas, resumos financeiros)
│   ├── filters.py               # Filtros django-filter para receitas e despesas
│   ├── context_processors.py   # Injeta alertas em todos os templates
│   ├── urls.py                  # URLs do módulo financeiro
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py                 # Testes unitários legados
│   └── management/
│       └── commands/
│           └── popular_dados.py # Comando para popular banco com dados de demo
│   └── migrations/
│
├── usuarios/                    # App de autenticação e gestão de usuários
│   ├── models.py
│   ├── views.py                 # landing_page, login, registro, perfil, admin
│   ├── forms.py                 # LoginForm, RegistroForm
│   ├── middleware.py            # ContaBloqueadaMiddleware
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
│
├── templates/                   # Todos os templates HTML
│   ├── base.html                # Template base (sidebar autenticado / header público)
│   ├── landing.html             # Página inicial pública
│   ├── components/              # Componentes reutilizáveis (alertas, calendário, previsão)
│   ├── financas/                # Templates do módulo financeiro
│   └── usuarios/                # Templates de autenticação e admin
│
├── static/                      # Arquivos estáticos
│   ├── css/design-system.css    # Design system com variáveis CSS (temas light/dark)
│   └── js/
│       ├── sidebar.js           # Comportamento da sidebar (collapse, mobile)
│       └── theme-toggle.js      # Toggle de tema claro/escuro
│
├── tests/                       # Suite de testes automatizados
│   ├── conftest.py              # Fixtures compartilhadas (pytest)
│   ├── test_models.py           # Testes de models
│   ├── test_views_financas.py   # Testes de views financeiras
│   ├── test_forms_financas.py   # Testes de formulários
│   ├── test_services.py         # Testes de serviços e regras de negócio
│   ├── test_filters.py          # Testes de filtros
│   ├── test_usuarios.py         # Testes de autenticação e usuários
│   └── test_e2e.py              # Testes end-to-end (Selenium)
│
└── .github/                     # Documentação e configuração do projeto
    ├── copilot-instructions.md  # Regras globais para o Copilot
    ├── PLANO-DE-PROJETO.MD      # Plano geral do projeto
    ├── agents/                  # Definições dos agentes IA
    ├── context/                 # Contexto de negócio e domínio
    │   ├── business-rules.md    # Regras de negócio detalhadas
    │   ├── domain-glossary.md   # Glossário de termos do domínio
    │   └── tech-constraints.md  # Restrições técnicas
    ├── docs/                    # Documentação técnica adicional
    ├── instructions/            # Instruções por área (backend, frontend, infra, testes)
    │   ├── central.md           # Índice mestre de skills
    │   ├── backend.md
    │   ├── frontend.md
    │   ├── infra.md
    │   └── tests.md
    ├── plans/                   # Planos de features ativas
    ├── prompts/                 # Prompts reutilizáveis
    └── skills/                  # Skills especializadas para agentes IA
```

---

## Estrutura do .github

A pasta `.github` centraliza toda a documentação técnica e de negócio do projeto, além de configurar o comportamento do GitHub Copilot:

| Arquivo/Pasta | Propósito |
|---------------|-----------|
| `copilot-instructions.md` | Regras globais invioláveis para todos os agentes (idioma, stack, proibições, arquitetura multi-tenant) |
| `PLANO-DE-PROJETO.MD` | Roadmap e planejamento geral do projeto |
| `agents/` | Definições dos agentes especializados (Senior, Backend, Frontend, TestAgent, CodeReview, etc.) |
| `context/business-rules.md` | Regras de negócio do domínio financeiro |
| `context/domain-glossary.md` | Glossário com terminologia do projeto |
| `context/tech-constraints.md` | Restrições técnicas e decisões arquiteturais |
| `instructions/central.md` | Índice mestre — ponto de entrada para todos os agentes |
| `instructions/backend.md` | Guia para desenvolvimento Django (models, views, services) |
| `instructions/frontend.md` | Guia para templates e Tailwind CSS |
| `instructions/infra.md` | Guia de setup do ambiente local |
| `instructions/tests.md` | Guia de testes com pytest-django |
| `plans/` | Planos estruturados de features para execução pelos agentes |
| `skills/` | Conhecimento especializado reutilizável (ORM, Tailwind, testes) |

---

## Instalação e Setup

### Pré-requisitos

- Python 3.12+
- Windows / macOS / Linux

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd HACKTON
```

### 2. Criar e ativar o ambiente virtual

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o banco de dados

```bash
python manage.py migrate
```

### 5. Criar o superusuário (administrador)

```bash
python manage.py createsuperuser
```

---

## Dados de Demonstração (Seed)

Para popular o banco com dados realistas de 2025 e 2026 (receitas, despesas, orçamentos e categorias), use o comando:

```bash
# Criar usuário demo com dados para 2025 e 2026
python manage.py popular_dados

# Personalizar usuário e senha
python manage.py popular_dados --usuario meunome --senha minhasenha

# Limpar dados existentes e repopular
python manage.py popular_dados --limpar
```

**Credenciais padrão do usuário demo:**
- **Username:** `demo`
- **Senha:** `demo@1234`

O comando cria:
- Categorias de receita e despesa
- Receitas fixas, variáveis e eventuais para cada mês
- Despesas fixas, variáveis e eventuais para cada mês
- Orçamentos mensais
- Configuração de alertas

---

## Rodando o Servidor

```bash
# Ativar venv (se necessário)
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Rodar o servidor de desenvolvimento
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000/**

---

## Rodando os Testes

O projeto usa **pytest** com **pytest-django**.

### Rodar todos os testes

```bash
pytest
```

### Rodar com output detalhado

```bash
pytest -v
```

### Rodar testes de um módulo específico

```bash
# Apenas testes de models
pytest tests/test_models.py -v

# Apenas testes de views
pytest tests/test_views_financas.py -v

# Apenas testes de serviços
pytest tests/test_services.py -v

# Apenas testes de formulários
pytest tests/test_forms_financas.py -v

# Apenas testes de filtros
pytest tests/test_filters.py -v

# Apenas testes de usuários
pytest tests/test_usuarios.py -v
```

### Rodar com cobertura de código

```bash
# Relatório no terminal
pytest --cov=financas --cov=usuarios --cov-report=term-missing

# Relatório HTML (abre em browser)
pytest --cov=financas --cov=usuarios --cov-report=html
# Depois abrir: htmlcov/index.html
```

### Rodar testes E2E (Selenium)

> ⚠️ Requer ChromeDriver instalado e servidor rodando em background.

```bash
pytest tests/test_e2e.py -v
```

### Configuração do pytest

O arquivo `setup.cfg` contém:
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
```

---

## Arquitetura Multi-Tenant

O sistema implementa isolamento de dados por `user_id`:

- **Toda** tabela de negócio herda de `BaseModel` que possui FK para `User`
- **Toda** query filtra por `user=request.user`
- Um usuário **nunca** acessa dados de outro
- O superusuário acessa o admin via `/usuarios/admin-dashboard/` (sem usar o admin nativo do Django)
- Usuários inativos são redirecionados para `/usuarios/conta-bloqueada/` pelo middleware

```
User
 ├── Categoria (receita/despesa)
 ├── Receita → Categoria
 ├── Despesa → Categoria
 ├── Orcamento (mes/ano/valor)
 └── ConfiguracaoAlerta
```

---

## Fluxo de Navegação

```
/ (landing)
 ├── /usuarios/login/          → Dashboard (autenticado)
 ├── /usuarios/registro/       → Dashboard (cria conta + login automático)
 │
 ├── /financas/dashboard/      → Resumo do mês atual
 ├── /financas/receitas/       → Lista, criar, editar, excluir receitas
 ├── /financas/despesas/       → Lista, criar, editar, excluir despesas
 ├── /financas/categorias/     → Lista, criar, editar, excluir categorias
 ├── /financas/orcamentos/     → Lista, criar, editar, excluir orçamentos
 ├── /financas/calendario/     → Calendário financeiro por mês
 ├── /financas/alertas/        → Configuração e visualização de alertas
 │
 ├── /usuarios/perfil/         → Perfil do usuário
 ├── /usuarios/logout/         → Logout (POST)
 ├── /usuarios/conta-bloqueada/→ Tela de conta bloqueada
 └── /usuarios/admin-dashboard/→ Painel do superusuário (somente superuser)
```

---

## Modelos de Dados

### `Categoria`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| user | FK(User) | Proprietário |
| nome | CharField | Nome da categoria |
| tipo | CharField | `receita` ou `despesa` |

### `Receita`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| user | FK(User) | Proprietário |
| descricao | CharField | Descrição do lançamento |
| valor | DecimalField | Valor (> 0) |
| data | DateField | Data da receita |
| categoria | FK(Categoria) | Categoria (receita) |
| origem | CharField | `salario`, `freelance`, `investimento`, `outros` |
| natureza | CharField | `fixa`, `variavel`, `eventual` |

### `Despesa`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| user | FK(User) | Proprietário |
| descricao | CharField | Descrição do lançamento |
| valor | DecimalField | Valor (> 0) |
| data | DateField | Data da despesa |
| categoria | FK(Categoria) | Categoria (despesa) |
| origem | CharField | `alimentacao`, `transporte`, `moradia`, `lazer`, `educacao`, `saude`, `outros` |
| natureza | CharField | `fixa`, `variavel`, `eventual` |

### `Orcamento`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| user | FK(User) | Proprietário |
| mes | PositiveIntegerField | Mês (1-12) |
| ano | PositiveIntegerField | Ano (2020-2100) |
| valor | DecimalField | Limite mensal de despesas |

### `ConfiguracaoAlerta`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| user | FK(User) | Proprietário (único por usuário) |
| alerta_orcamento_ativo | BooleanField | Avisar ao atingir % do orçamento |
| limiar_orcamento | PositiveIntegerField | Percentual de disparo (1-100%) |
| alerta_gasto_acelerado_ativo | BooleanField | Avisar gastos acelerados |
| alerta_saldo_baixo_ativo | BooleanField | Avisar saldo abaixo do mínimo |
| limite_saldo_minimo | DecimalField | Valor mínimo de saldo |

---

## Credenciais Padrão

| Tipo | Username | Senha |
|------|----------|-------|
| Usuário demo | `demo` | `demo@1234` |
| Superusuário | Definido no `createsuperuser` | — |

> O usuário demo é criado pelo comando `python manage.py popular_dados`.

---

## Temas

O sistema suporta **tema claro e escuro** via variáveis CSS definidas em `static/css/design-system.css`. A preferência é salva no `localStorage` do navegador e respeita a preferência do sistema operacional na primeira visita.

---

## Licença

Projeto desenvolvido para fins educacionais / Hackathon. Todos os direitos reservados.
