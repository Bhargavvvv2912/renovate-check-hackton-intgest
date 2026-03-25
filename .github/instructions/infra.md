# Instruções — Infraestrutura Local

## Ambiente de Desenvolvimento
- **Somente execução local** — sem deploy em produção.
- Ambiente virtual Python (`venv`) obrigatório.
- SQLite como banco de dados (arquivo `db.sqlite3`).
- Sem Docker, sem containerização.

## Setup do Projeto
```bash
# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrations
python manage.py migrate

# Carregar dados de demonstração (seed)
python manage.py seed_data

# Iniciar servidor
python manage.py runserver
```

## requirements.txt
- Manter atualizado com todas as dependências.
- Usar versões pinadas (`Django==5.x.x`).
- Incluir dependências de teste (`pytest`, `pytest-django`, etc.).

## Configurações Django (settings.py)
- `DEBUG = True` (ambiente local).
- `ALLOWED_HOSTS = ['localhost', '127.0.0.1']`.
- `LANGUAGE_CODE = 'pt-br'`.
- `TIME_ZONE = 'America/Sao_Paulo'`.
- Static files configurados para servir localmente.

## Seed de Dados
- Criar management command `seed_data` para popular o banco com dados de demonstração.
- Incluir: categorias padrão, usuário demo, lançamentos de exemplo.
- Deve ser idempotente (executar múltiplas vezes sem duplicar).

## Verificação para Apresentação
1. `pip install -r requirements.txt` — sem erros.
2. `python manage.py migrate` — migrations aplicadas.
3. `python manage.py runserver` — aplicação inicia.
4. Testes automatizados passam.

## Arquivos Ignorados (.gitignore)
```
venv/
db.sqlite3
__pycache__/
*.pyc
.env
*.sqlite3
node_modules/
```
