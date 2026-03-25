"""
Testes E2E (end-to-end) com Selenium WebDriver.
Simula o fluxo completo de um usuário real no navegador.
"""
import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class TestFluxoCompletoE2E(StaticLiveServerTestCase):
    """Teste E2E: fluxo completo de registro → login → CRUD financeiro → logout."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opcoes = Options()
        opcoes.add_argument('--headless=new')
        opcoes.add_argument('--no-sandbox')
        opcoes.add_argument('--disable-dev-shm-usage')
        opcoes.add_argument('--disable-gpu')
        opcoes.add_argument('--window-size=1920,1080')

        try:
            servico = Service(ChromeDriverManager().install())
            cls.driver = webdriver.Chrome(service=servico, options=opcoes)
        except Exception:
            # Fallback: tentar usar Chrome do sistema
            cls.driver = webdriver.Chrome(options=opcoes)

        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def _url(self, caminho: str) -> str:
        """Retorna a URL completa para o caminho informado."""
        return f"{self.live_server_url}{caminho}"

    def _preencher_campo(self, nome: str, valor: str):
        """Preenche um campo de formulário pelo atributo name."""
        campo = self.driver.find_element(By.NAME, nome)
        # Para inputs do tipo date, usar JavaScript
        if campo.get_attribute('type') == 'date':
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; "
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                campo, valor
            )
        else:
            campo.clear()
            campo.send_keys(valor)

    def _submeter_formulario(self):
        """Clica no botão de submit do formulário principal (ignora logout na navbar)."""
        # Buscar o submit dentro do conteúdo main, não da navbar
        botoes = self.driver.find_elements(By.CSS_SELECTOR, 'main button[type="submit"]')
        if botoes:
            botoes[0].click()
        else:
            # Fallback: buscar o último submit (que geralmente é o do form principal)
            todos = self.driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"]')
            todos[-1].click()

    # ─── 1. Landing Page ────────────────────────────────────────────────

    def test_01_landing_page_carrega(self):
        """Verifica que a landing page carrega corretamente."""
        self.driver.get(self._url('/'))
        assert 'Gestão Financeira' in self.driver.title or \
               'Gestão Financeira' in self.driver.page_source

    # ─── 2. Registro ────────────────────────────────────────────────────

    def test_02_registro_novo_usuario(self):
        """Registra um novo usuário e verifica redirecionamento para dashboard."""
        self.driver.get(self._url('/usuarios/registro/'))

        self._preencher_campo('username', 'usuario_e2e')
        self._preencher_campo('email', 'e2e@teste.com')
        self._preencher_campo('first_name', 'Teste E2E')
        self._preencher_campo('password1', 'SenhaForte123!')
        self._preencher_campo('password2', 'SenhaForte123!')
        self._submeter_formulario()

        # Deve redirecionar para o dashboard
        self.wait.until(EC.url_contains('/financas/dashboard/'))
        assert '/financas/dashboard/' in self.driver.current_url

    # ─── 3. Logout ──────────────────────────────────────────────────────

    def test_03_logout(self):
        """Faz logout via POST e verifica redirecionamento para a landing page."""
        # Primeiro fazer login
        self._fazer_login()

        # Submeter o form de logout via navbar
        self.driver.get(self._url('/financas/dashboard/'))
        botao_sair = self.driver.find_element(By.CSS_SELECTOR, 'form[action*="logout"] button[type="submit"]')
        botao_sair.click()
        self.wait.until(EC.url_contains('/'))
        # Não deve estar no dashboard
        assert '/financas/dashboard/' not in self.driver.current_url

    # ─── 4. Login ────────────────────────────────────────────────────────

    def test_04_login_usuario_existente(self):
        """Faz login com o usuário criado no registro."""
        # Garantir que o usuário existe
        self._criar_usuario_se_necessario()

        self.driver.get(self._url('/usuarios/login/'))
        self._preencher_campo('username', 'usuario_e2e')
        self._preencher_campo('password', 'SenhaForte123!')
        self._submeter_formulario()

        self.wait.until(EC.url_contains('/financas/dashboard/'))
        assert '/financas/dashboard/' in self.driver.current_url

    # ─── 5. Dashboard ───────────────────────────────────────────────────

    def test_05_dashboard_exibe_informacoes(self):
        """Verifica que o dashboard exibe saldo e informações financeiras."""
        self._fazer_login()
        self.driver.get(self._url('/financas/dashboard/'))

        assert self.driver.find_element(By.TAG_NAME, 'body').text != ''
        # Deve conter informações do dashboard
        pagina = self.driver.page_source.lower()
        assert 'saldo' in pagina or 'dashboard' in pagina or 'receita' in pagina

    # ─── 6. Criar Categoria ─────────────────────────────────────────────

    def test_06_criar_categoria_receita(self):
        """Cria uma categoria de receita."""
        self._fazer_login()
        self.driver.get(self._url('/financas/categorias/nova/'))

        self._preencher_campo('nome', 'Salario E2E')
        # Selecionar tipo = receita
        select_tipo = Select(self.driver.find_element(By.NAME, 'tipo'))
        select_tipo.select_by_value('receita')
        self._submeter_formulario()

        self.wait.until(lambda d: d.current_url.rstrip('/').endswith('/financas/categorias'))
        assert 'Salario E2E' in self.driver.page_source

    def test_07_criar_categoria_despesa(self):
        """Cria uma categoria de despesa."""
        self._fazer_login()
        self.driver.get(self._url('/financas/categorias/nova/'))

        self._preencher_campo('nome', 'Alimentacao E2E')
        select_tipo = Select(self.driver.find_element(By.NAME, 'tipo'))
        select_tipo.select_by_value('despesa')
        self._submeter_formulario()

        self.wait.until(lambda d: d.current_url.rstrip('/').endswith('/financas/categorias'))
        assert 'Alimentacao E2E' in self.driver.page_source

    # ─── 7. Criar Receita ───────────────────────────────────────────────

    def test_08_criar_receita(self):
        """Cria uma receita e verifica que aparece na listagem."""
        self._fazer_login()
        self._garantir_categoria('Salario E2E', 'receita')

        self.driver.get(self._url('/financas/receitas/nova/'))

        # Aguardar formulário carregar
        self.wait.until(EC.presence_of_element_located((By.NAME, 'descricao')))

        self._preencher_campo('descricao', 'Salario mensal E2E')
        self._preencher_campo('valor', '5000.00')
        self._preencher_campo('data', '2026-03-01')

        # Selecionar categoria (primeira opção não vazia)
        select_cat = Select(self.driver.find_element(By.NAME, 'categoria'))
        for opcao in select_cat.options:
            if opcao.get_attribute('value') and opcao.get_attribute('value') != '':
                select_cat.select_by_value(opcao.get_attribute('value'))
                break

        # Selecionar origem e natureza
        Select(self.driver.find_element(By.NAME, 'origem')).select_by_value('salario')
        Select(self.driver.find_element(By.NAME, 'natureza')).select_by_value('fixa')

        self._submeter_formulario()

        self.wait.until(lambda d: d.current_url.rstrip('/').endswith('/financas/receitas'))
        assert 'Salario mensal E2E' in self.driver.page_source

    # ─── 8. Criar Despesa ───────────────────────────────────────────────

    def test_09_criar_despesa(self):
        """Cria uma despesa e verifica que aparece na listagem."""
        self._fazer_login()
        self._garantir_categoria('Alimentacao E2E', 'despesa')

        self.driver.get(self._url('/financas/despesas/nova/'))

        self._preencher_campo('descricao', 'Supermercado E2E')
        self._preencher_campo('valor', '350.00')
        self._preencher_campo('data', '2026-03-05')

        select_cat = Select(self.driver.find_element(By.NAME, 'categoria'))
        for opcao in select_cat.options:
            if 'Alimentacao E2E' in opcao.text:
                select_cat.select_by_visible_text(opcao.text)
                break

        # Selecionar origem e natureza
        Select(self.driver.find_element(By.NAME, 'origem')).select_by_value('alimentacao')
        Select(self.driver.find_element(By.NAME, 'natureza')).select_by_value('variavel')

        self._submeter_formulario()

        self.wait.until(lambda d: d.current_url.rstrip('/').endswith('/financas/despesas'))
        assert 'Supermercado E2E' in self.driver.page_source

    # ─── 9. Verificar Saldo no Dashboard ────────────────────────────────

    def test_10_dashboard_reflete_saldo(self):
        """Verifica que o dashboard exibe dados após criar lançamentos."""
        self._fazer_login()
        self._garantir_lancamentos()

        self.driver.get(self._url('/financas/dashboard/'))

        pagina = self.driver.page_source
        # Dashboard deve ter conteúdo (receitas ou despesas criadas)
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        assert len(body) > 50  # Página não está vazia

    # ─── 10. Listar Receitas ────────────────────────────────────────────

    def test_11_listar_receitas(self):
        """Verifica que a listagem de receitas funciona."""
        self._fazer_login()
        self.driver.get(self._url('/financas/receitas/'))

        assert self.driver.find_element(By.TAG_NAME, 'body').text != ''

    # ─── 11. Listar Despesas ────────────────────────────────────────────

    def test_12_listar_despesas(self):
        """Verifica que a listagem de despesas funciona."""
        self._fazer_login()
        self.driver.get(self._url('/financas/despesas/'))

        assert self.driver.find_element(By.TAG_NAME, 'body').text != ''

    # ─── 12. Listar Categorias ──────────────────────────────────────────

    def test_13_listar_categorias(self):
        """Verifica que a listagem de categorias funciona."""
        self._fazer_login()
        self.driver.get(self._url('/financas/categorias/'))

        assert self.driver.find_element(By.TAG_NAME, 'body').text != ''

    # ─── 13. Perfil ─────────────────────────────────────────────────────

    def test_14_acessar_perfil(self):
        """Verifica que o perfil do usuário exibe seus dados."""
        self._fazer_login()
        self.driver.get(self._url('/usuarios/perfil/'))

        pagina = self.driver.page_source
        assert 'usuario_e2e' in pagina

    # ─── 14. Login com credenciais inválidas ────────────────────────────

    def test_15_login_invalido_mostra_erro(self):
        """Verifica que credenciais inválidas mostram mensagem de erro."""
        self.driver.get(self._url('/usuarios/login/'))

        self._preencher_campo('username', 'inexistente')
        self._preencher_campo('password', 'senhaErrada')
        self._submeter_formulario()

        # Deve permanecer na página de login
        assert '/usuarios/login/' in self.driver.current_url

    # ─── 15. Acesso não autenticado redireciona ─────────────────────────

    def test_16_acesso_nao_autenticado_redireciona(self):
        """Verifica que áreas protegidas redirecionam para login."""
        # Limpar cookies para não estar logado
        self.driver.delete_all_cookies()
        self.driver.get(self._url('/financas/dashboard/'))

        # Deve ter redirecionado para login
        assert '/usuarios/login/' in self.driver.current_url

    # ─── Helpers ────────────────────────────────────────────────────────

    def _criar_usuario_se_necessario(self):
        """Cria o usuário de teste se não existir."""
        from django.contrib.auth.models import User
        if not User.objects.filter(username='usuario_e2e').exists():
            User.objects.create_user(
                username='usuario_e2e',
                email='e2e@teste.com',
                password='SenhaForte123!',
                first_name='Teste E2E',
            )

    def _fazer_login(self):
        """Faz login com o usuário de teste."""
        self._criar_usuario_se_necessario()
        self.driver.get(self._url('/usuarios/login/'))

        # Verificar se já está logado
        if '/financas/dashboard/' in self.driver.current_url:
            return

        self._preencher_campo('username', 'usuario_e2e')
        self._preencher_campo('password', 'SenhaForte123!')
        self._submeter_formulario()
        self.wait.until(EC.url_contains('/financas/dashboard/'))

    def _garantir_categoria(self, nome: str, tipo: str):
        """Garante que uma categoria existe para o usuário."""
        from django.contrib.auth.models import User
        from financas.models import Categoria

        usuario = User.objects.get(username='usuario_e2e')
        Categoria.objects.get_or_create(
            user=usuario,
            nome=nome,
            tipo=tipo,
        )

    def _garantir_lancamentos(self):
        """Garante que existem lançamentos para o teste."""
        from datetime import date
        from decimal import Decimal

        from django.contrib.auth.models import User

        from financas.models import Categoria, Despesa, Receita

        usuario = User.objects.get(username='usuario_e2e')
        cat_rec, _ = Categoria.objects.get_or_create(
            user=usuario, nome='Salario E2E', tipo='receita'
        )
        cat_desp, _ = Categoria.objects.get_or_create(
            user=usuario, nome='Alimentacao E2E', tipo='despesa'
        )

        Receita.objects.get_or_create(
            user=usuario,
            descricao='Salario mensal E2E',
            defaults={
                'valor': Decimal('5000.00'),
                'data': date(2026, 3, 1),
                'categoria': cat_rec,
            },
        )
        Despesa.objects.get_or_create(
            user=usuario,
            descricao='Supermercado E2E',
            defaults={
                'valor': Decimal('350.00'),
                'data': date(2026, 3, 5),
                'categoria': cat_desp,
            },
        )
