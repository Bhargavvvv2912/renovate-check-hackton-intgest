# PLANO DE PROJETO — Gestão Financeira

## Objetivo
Planejamento central para o projeto de gestão financeira. Este documento centraliza stack obrigatória, escopo mínimo, passos de implementação e verificações para apresentação local.

o projeto deve ser um modelo saas, aonde cada cliente deve ter seu proprio ambiente isolado para garantir segunraça.
como é um sistema para gerenciamento pessoal cada client só irá ter 1 usuario.

e os dados serão isolados e separados por um user_id ou seja cada tabela irá ter um campo user_id apontando para seu respectivo user.

deve ter um superusuario que consegue administrar todos os clients/usuarios de forma facil.

podendo inativar clients e caso um client esteja inativo apareça uma mensagem para ele que a conta está bloqueada
e peça para entrar em contato com o suporte.

um dashboard para o superusuario.

uma pagina de cadastro de usuarios para cada pessoa conseguir se cadastrar e criar sua conta e assim conseguindo usar o sistema.

deve ter uma landingpage de apresentação na index "/" com abas para login e registro de uma nova conta.

não ultilizar o administrativo proprio do django, ultilizar templates criados e funcionais!!!
aonde a ux seja o mais importante.


## 1. Stack obrigatória
1. Python
2. Django
3. SQLite
4. VS Code
5. GitHub Copilot
6. Tailwind

## 1.1 Oque é não pode!
1. Django restframework
2. docker ou outras formas de containerização
3. ambiente de produção
4. react
5. celery

> A aplicação deverá ser executada localmente no momento da apresentação.

## 2. Escopo funcional mínimo (entrega base)
1. Cadastro de receitas.
2. Cadastro de despesas.
3. Cadastro ou seleção de categorias.
4. Listagem de lançamentos financeiros.
5. Cálculo automático do saldo atualizado.
6. Edição de registros.
7. Exclusão de registros.
8. Dashboard, resumo ou painel simples.
9. filtros por periodo e datas no dashboard.
10. filtros por período e datas.
11. busca por descrição ou categoria
12. gráficos simples
13. melhor tratamento de erros e validações
14. testes automatizados básicos
15. seed de dados para demonstração
16. README mais completo
17. melhor organização técnica da solução
18. exportação de dados em formatos : json, csv, pdf e outros de sua escolha


## 3. Passos recomendados (alto nível)
- Criar ambiente virtual e `requirements.txt`.
- Inicializar projeto Django e app `financas`.
- Implementar modelos (`Categoria`, `Lancamento`), migrations e CRUD.
- Implementar cálculo de saldo via agregações e atualizações.
- Criar templates simples e um dashboard resumido com tailwind.
- Escrever testes mínimos (models e views principais).
- Documentar execução local no `README.md`.
- Criar models separados para receita e despesas com campos origem, natureza, data, valor e tudo relacionado a eles
consulte a web para caso vc tenha alguma duvida de criação dos models.

## 4. Verificação para apresentação
- `pip install -r requirements.txt` — sem erros.
- `python manage.py migrate` — migrations aplicadas.
- `python manage.py runserver` — aplicação inicia localmente.
- Testes automatizados básicos passam.

## 5. CI / próximo passos
- Documentar templates de prompts do Copilot em `.github/copilot-prompts.md`.

---

(Documento criado para ser colocado em `.github/PLANO-DE-PROJETO.md` no repositório.)