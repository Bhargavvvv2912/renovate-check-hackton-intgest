# Instruções — Backend (Django)

## Estrutura do Projeto
```
projeto/
├── manage.py
├── core/                  ← Projeto Django principal (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── financas/              ← App principal de gestão financeira
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── services.py        ← Lógica de negócio isolada
│   ├── filters.py         ← Filtros customizados
│   └── templates/financas/
├── usuarios/              ← App de autenticação e gestão de usuários
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/usuarios/
└── templates/             ← Templates globais (base.html, landing)
```

## Models
- Cada model de negócio **deve** ter campo `user_id` (ForeignKey para User).
- Criar models separados para **Receita** e **Despesa** com campos: origem, natureza, data, valor, descrição, categoria.
- Model **Categoria** deve ser compartilhável ou por usuário, conforme regra de negócio.
- Todos os models devem implementar `__str__`, `class Meta` com `ordering` e `verbose_name`.
- Usar `created_at` e `updated_at` com `auto_now_add` e `auto_now`.
- Ter uma BaseModel para armazenar informações que tem em todos os tenants e evitar duplicação de codigo.


## Views
- Preferir CBVs (ListView, CreateView, UpdateView, DeleteView) para CRUD.
- FBVs aceitas para lógica mais simples (dashboard, landing).
- **Toda view** que acessa dados de negócio deve filtrar por `request.user`.
- Usar `LoginRequiredMixin` ou `@login_required` em todas as views protegidas.
- Views do superusuário devem verificar `request.user.is_superuser`.

## Services
- Lógica de negócio complexa deve ficar em `services.py`, não nas views.
- Cálculo de saldo, agregações e exportações são responsabilidade de services.
- Services recebem o `user` como parâmetro para garantir isolamento.

## Forms
- Usar ModelForm para CRUD.
- Validações de negócio no método `clean()` ou `clean_<field>()`.
- Nunca confiar em validação apenas no frontend.

## URLs
- Namespaces por app: `financas:`, `usuarios:`.
- Usar `path()` com nomes descritivos.

## Exportação de Dados
- Formatos obrigatórios: JSON, CSV, PDF.
- Sempre filtrar por `user_id` na exportação.
