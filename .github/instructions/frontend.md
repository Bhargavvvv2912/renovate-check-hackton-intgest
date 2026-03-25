# Instruções — Frontend (Templates + Tailwind + Design System)

## Stack de Frontend
- **Templates Django** com herança (`{% extends "base.html" %}`).
- **Tailwind CSS** via CDN com config customizada em `base.html`.
- **CSS Variables** para cores (design system em `static/css/design-system.css`).
- **Lucide Icons** para todos os ícones — **NUNCA usar emojis**.
- **Sem frameworks JS SPA** (React, Vue, Angular proibidos).
- JavaScript vanilla apenas quando necessário (gráficos, toggle de tema, sidebar).

## Design System

### Paleta de Cores (variáveis CSS)
O sistema usa variáveis CSS com suporte a modo claro e escuro via `data-theme`:
- `var(--color-background)` — fundo da página
- `var(--color-surface)` — fundo de áreas secundárias
- `var(--color-surface-elevated)` — fundo de cards e elementos elevados
- `var(--color-border)` / `var(--color-border-subtle)` — bordas
- `var(--color-primary)` / `var(--color-primary-hover)` / `var(--color-primary-muted)` — verde principal
- `var(--color-text-primary)` / `var(--color-text-secondary)` / `var(--color-text-disabled)` — texto
- `var(--color-success)` / `var(--color-danger)` / `var(--color-warning)` / `var(--color-info)` — estados
- `var(--color-chart-1..4)` — cores de gráficos

### Tipografia
- **DM Sans** (`font-display`) — Títulos e valores monetários grandes
- **IBM Plex Sans** (`font-body`) — Corpo, labels, tabelas
- **IBM Plex Mono** (`font-mono`) — Valores numéricos

### Regras Absolutas
| PROIBIDO | SUBSTITUTO OBRIGATÓRIO |
|---|---|
| `linear-gradient` / `radial-gradient` | Cores sólidas com variáveis CSS |
| Emojis (🟢 📈 ✅ etc.) | Ícones Lucide com `aria-label` |
| Cores hardcoded (`#fff`, `green`) | Variáveis CSS (`var(--color-primary)`) |
| Sombras coloridas / glow | `box-shadow` monocromático sutil |
| Animações sem `prefers-reduced-motion` | Respeitar media query |

## Estrutura de Templates
```
templates/
├── base.html              ← Layout master com sidebar, header, tema
├── landing.html           ← Landing page pública (visitantes)
├── components/            ← Partials reutilizáveis
│   ├── alertas.html       ← Alertas inteligentes
│   ├── previsao_saldo.html← Previsão de saldo
│   └── calendario_receita_despesa.html
├── financas/
│   ├── dashboard.html     ← Dashboard principal
│   ├── receita_lista.html / receita_form.html / receita_confirmar_exclusao.html
│   ├── despesa_lista.html / despesa_form.html / despesa_confirmar_exclusao.html
│   ├── categoria_lista.html / categoria_form.html / categoria_confirmar_exclusao.html
│   ├── orcamento_lista.html / orcamento_form.html / orcamento_confirmar_exclusao.html
│   ├── configuracao_alertas.html
│   ├── calendario.html
│   └── detalhes_dia.html
└── usuarios/
    ├── login.html / registro.html / perfil.html
    ├── conta_bloqueada.html
    └── admin/dashboard.html
```

## Layout
- **Usuário autenticado**: Layout com sidebar lateral (220px / 64px colapsada) + header + conteúdo
- **Visitante**: Header simples com logo + botões Entrar/Criar Conta

### Sidebar
- Fundo: `var(--color-surface)`, borda direita `var(--color-border)`
- Ícones Lucide 20px, cor `var(--color-text-secondary)`
- Item ativo: fundo `var(--color-primary-muted)`, cor `var(--color-primary)`
- Responsividade: Desktop (sidebar), Tablet (colapsada), Mobile (drawer)

### Toggle de Tema
- Ícone `sun` (tema escuro) / `moon` (tema claro) no header
- Persistência via `localStorage`
- Respeita `prefers-color-scheme`
- Anúncio via `aria-live="polite"` ao trocar tema

## Padrões de Componentes

### Cards de Métricas
- `rounded-xl border` com `background-color: var(--color-surface-elevated)`
- Valor: `font-mono font-bold text-2xl`
- Label: `text-sm` + `var(--color-text-secondary)`
- Ícone Lucide no canto superior direito (ex: `trending-up`, `trending-down`)

### Tabelas
- Header com `var(--color-primary)` + texto branco
- Linhas com hover: `var(--color-surface)`
- Valores monetários: `font-mono`
- Badges de status: pills com cores sólidas

### Botões
- Primário: `background: var(--color-primary)`, texto branco, `rounded-xl`
- Secundário: `border: 1px solid var(--color-border)`, texto `var(--color-text-primary)`
- Hover via `onmouseover/onmouseout` com variáveis CSS
- Mínimo 44x44px para acessibilidade

### Formulários
- Inputs com `background-color: var(--color-surface)`, `border: var(--color-border)`
- Focus: `border-color: var(--color-primary)` + box-shadow
- Labels claros, erros inline em `var(--color-danger)`

## Gráficos
- Chart.js com cores do design system (`var(--color-chart-1..4)`)
- `borderWidth: 0` em doughnut charts
- Grid com `var(--color-border-subtle)`, sem fundo colorido
- Tooltips: fundo `var(--color-surface-elevated)`, borda `var(--color-border)`

## Acessibilidade (WCAG 2.1 AA)
- Contraste mínimo 4.5:1 (texto normal), 3:1 (texto grande)
- `:focus-visible` com `outline: 2px solid var(--color-primary)`
- Status com ícone + cor + texto (nunca só cor)
- `aria-label` em ícones sem texto, `aria-hidden="true"` em ícones decorativos
- Semântica HTML: `<nav>`, `<main>`, `<header>`, `<section>`, `<table>`
- Mínimo 44x44px alvos clicáveis
- `@media (prefers-reduced-motion: reduce)` para desativar animações
