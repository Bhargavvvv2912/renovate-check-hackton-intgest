# Regras de Negócio — Gestão Financeira SaaS

## Modelo SaaS
- Cada cliente possui **1 conta = 1 usuário**.
- Dados isolados por `user_id` em todas as tabelas de negócio.
- Superusuário administra todos os clientes via dashboard próprio.

## Usuários e Contas
- **Registro**: qualquer pessoa pode criar uma conta pela landing page.
- **Login**: autenticação por email/username + senha.
- **Bloqueio**: superusuário pode inativar um cliente (`is_active = False`).
- **Conta bloqueada**: usuário inativo vê mensagem de bloqueio e não acessa o sistema.
- **1 usuário = 1 conta**: não há múltiplos usuários por conta.

## Lançamentos Financeiros
- **Receitas**: entradas de dinheiro (salário, freelance, investimentos, outros).
- **Despesas**: saídas de dinheiro (alimentação, transporte, moradia, lazer, outros).
- Models separados para Receita e Despesa.
- Campos obrigatórios: valor, data, categoria, descrição.
- Campos adicionais: origem, natureza.
- Todo lançamento pertence a um `user_id`.

## Categorias
- Categorias podem ser padrão do sistema ou criadas pelo usuário.
- Cada categoria pertence ao `user_id` que a criou.
- Categorias padrão são criadas no seed de dados.

## Saldo
- Saldo = soma(receitas) - soma(despesas) do usuário.
- Calculado dinamicamente via agregações Django (não armazenado).
- Exibido no dashboard com destaque visual.

## Dashboard
- Resumo: saldo atual, total receitas, total despesas.
- Filtros por período (mês, ano, intervalo customizado).
- Gráficos: receitas vs despesas, evolução do saldo, por categoria.
- Visível apenas para o usuário autenticado (dados do próprio user).

## Dashboard do Superusuário
- Lista de todos os clientes/usuários.
- Ações: ativar/inativar contas.
- Visão geral: total de usuários, ativos/inativos.
- Não usa o `/admin/` do Django — interface própria.

## Filtros e Busca
- Filtrar lançamentos por período (data início, data fim).
- Filtrar por categoria.
- Busca por descrição (texto livre).
- Filtros combinados devem funcionar.

## Exportação
- Formatos: JSON, CSV, PDF (e opcionais adicionais).
- Exportação sempre filtrada por `user_id`.
- Deve respeitar os filtros ativos no momento da exportação.

## Validações
- Valor deve ser positivo e maior que zero.
- Data não pode ser futura (regra opcional, definir conforme necessidade).
- Campos obrigatórios devem ter validação server-side.
- Mensagens de erro claras e em português.
