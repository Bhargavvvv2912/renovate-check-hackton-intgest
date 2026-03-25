# Glossário do Domínio — Gestão Financeira

## Termos do Sistema

| Termo | Definição |
|-------|-----------|
| **Lançamento** | Registro financeiro genérico (receita ou despesa) |
| **Receita** | Entrada de dinheiro — qualquer valor que o usuário recebe |
| **Despesa** | Saída de dinheiro — qualquer gasto ou pagamento |
| **Categoria** | Classificação de um lançamento (ex: Alimentação, Transporte, Salário) |
| **Saldo** | Diferença entre total de receitas e total de despesas |
| **Origem** | Fonte de uma receita (ex: Salário, Freelance, Investimento) |
| **Natureza** | Tipo econômico do lançamento (ex: Fixa, Variável, Eventual) |
| **Período** | Intervalo de datas usado em filtros (mensal, anual, customizado) |

## Termos de Arquitetura

| Termo | Definição |
|-------|-----------|
| **Multi-tenant** | Isolamento de dados por `user_id` — cada usuário vê apenas seus dados |
| **user_id** | Chave estrangeira para `User` presente em todas as tabelas de negócio |
| **Superusuário** | Administrador do sistema que gerencia todos os clientes |
| **Cliente** | Usuário final do sistema SaaS (1 conta = 1 pessoa) |
| **Conta bloqueada** | Estado `is_active=False` — usuário não consegue acessar o sistema |
| **Landing page** | Página pública inicial (`/`) com apresentação, login e registro |
| **Dashboard** | Painel resumido com saldo, gráficos e indicadores financeiros |
| **Seed** | Dados iniciais para demonstração, populados via management command |

## Termos Técnicos

| Termo | Definição |
|-------|-----------|
| **CBV** | Class-Based View — views Django baseadas em classe |
| **FBV** | Function-Based View — views Django baseadas em função |
| **ModelForm** | Formulário Django gerado automaticamente a partir de um model |
| **Management command** | Comando Django executado via `python manage.py <comando>` |
| **Fixture** | Dados de teste reutilizáveis (pytest fixtures) |
| **Aggregation** | Cálculo via banco de dados (Sum, Count, Avg) no Django ORM |
