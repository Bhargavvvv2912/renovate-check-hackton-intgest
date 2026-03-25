# Instruções — Frontend (Templates + Tailwind)

## Stack de Frontend
- **Templates Django** com herança (`{% extends "base.html" %}`).
- **Tailwind CSS** via CDN ou build local.
- **Sem frameworks JS SPA** (React, Vue, Angular proibidos).
- JavaScript vanilla apenas quando necessário (gráficos, interações simples).

## Estrutura de Templates
```
templates/
├── base.html              ← Layout master com Tailwind, navbar, footer
├── landing.html           ← Landing page pública (index "/")
├── components/            ← Partials reutilizáveis
│   ├── _navbar.html
│   ├── _footer.html
│   ├── _messages.html     ← Alertas/toasts do Django messages
│   ├── _pagination.html
│   └── _modal_confirm.html
├── financas/
│   ├── dashboard.html
│   ├── receita_list.html
│   ├── receita_form.html
│   ├── despesa_list.html
│   ├── despesa_form.html
│   └── exportar.html
└── usuarios/
    ├── login.html
    ├── registro.html
    ├── perfil.html
    ├── conta_bloqueada.html
    └── admin/
        ├── dashboard_admin.html
        └── lista_usuarios.html
```

## Padrões de UI/UX
- **UX é prioridade máxima** — interfaces devem ser intuitivas e limpas.
- Usar classes utilitárias do Tailwind consistentemente.
- Responsividade mobile-first obrigatória.
- Feedback visual para todas as ações (mensagens de sucesso/erro).
- Confirmação antes de exclusões (modal ou página de confirmação).
- Formulários com labels claros, placeholders e mensagens de erro inline.

## Landing Page
- Rota: `/` (index).
- Deve conter: apresentação do sistema, botão de login, botão de registro.
- Design atrativo e profissional.

## Conta Bloqueada
- Quando `user.is_active == False`, redirecionar para tela de bloqueio.
- Mensagem clara: "Sua conta está bloqueada. Entre em contato com o suporte."

## Gráficos
- Usar Chart.js ou biblioteca JS leve para gráficos simples.
- Gráficos no dashboard: receitas vs despesas, evolução do saldo, por categoria.

## Acessibilidade
- Atributos `aria-label` em elementos interativos.
- Contraste adequado de cores.
- Navegação por teclado funcional.
