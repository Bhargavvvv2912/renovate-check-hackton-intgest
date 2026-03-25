# Decisões Técnicas e Restrições — Gestão Financeira

## Decisões Arquiteturais

### 1. Isolamento por user_id (não por schema/banco separado)
- **Decisão**: Multi-tenancy via campo `user_id` em cada tabela.
- **Motivo**: Simplicidade para aplicação local com SQLite. Não há necessidade de isolamento por schema.
- **Impacto**: Toda query deve filtrar por `user_id`. Mixins e decorators devem garantir isso.

### 2. Models separados para Receita e Despesa
- **Decisão**: Não usar um único model "Lançamento" com campo tipo.
- **Motivo**: Flexibilidade para campos específicos de cada tipo (ex: origem em receitas).
- **Impacto**: Saldo calculado como `sum(receitas) - sum(despesas)`.

### 3. Templates Django + Tailwind (sem SPA)
- **Decisão**: SSR com templates Django e Tailwind CSS.
- **Motivo**: Proibição de React/SPA. Simplicidade e velocidade de desenvolvimento.
- **Impacto**: JavaScript apenas para interações pontuais (gráficos, modais).

### 4. SQLite como banco de dados
- **Decisão**: Não usar PostgreSQL ou outro banco.
- **Motivo**: Aplicação local, sem necessidade de concorrência pesada.
- **Impacto**: Evitar operações que não são bem suportadas pelo SQLite (ex: JsonField complexo).

### 5. Sem admin nativo do Django
- **Decisão**: Toda interface administrativa construída com templates próprios.
- **Motivo**: Requisito do projeto — UX personalizada é prioridade.
- **Impacto**: Criar views e templates para gestão de usuários pelo superusuário.

### 6. Sem Docker / sem produção
- **Decisão**: Executar apenas localmente com `python manage.py runserver`.
- **Motivo**: Projeto para apresentação local (hackathon).
- **Impacto**: Setup via venv + requirements.txt.

## Restrições Técnicas

| Restrição | Motivo |
|-----------|--------|
| Sem DRF | Não é API REST — é aplicação web com templates |
| Sem Celery | Não há processamento assíncrono necessário |
| Sem Docker | Aplicação roda apenas local |
| Sem React/Vue/Angular | Frontend é SSR com templates Django |
| Sem deploy em produção | Apresentação local apenas |
| Sem `/admin/` Django | Interfaces próprias obrigatórias |
| SQLite apenas | Sem necessidade de banco robusto |
| Python 3.12+ | Versão mínima para recursos modernos |
| Django 5.x | Versão estável mais recente |

## Bibliotecas Permitidas
- **Django** — framework web
- **Tailwind CSS** — estilização (CDN ou build)
- **Chart.js** — gráficos no frontend
- **pytest / pytest-django** — testes
- **ReportLab ou WeasyPrint** — geração de PDF
- **django-filter** — filtros avançados (opcional)
- Outras bibliotecas Python conforme necessidade, desde que não violem as restrições.
