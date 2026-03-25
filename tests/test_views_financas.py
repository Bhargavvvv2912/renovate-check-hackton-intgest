import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from financas.models import Categoria, Despesa, Orcamento, Receita


# =============================================================================
# Dashboard
# =============================================================================

class TestDashboardView:
    """Testes para a view do dashboard."""

    @pytest.mark.django_db
    def test_dashboard_logado_retorna_200(self, client_logado):
        resposta = client_logado.get(reverse('financas:dashboard'))
        assert resposta.status_code == 200

    def test_dashboard_anonimo_redireciona_login(self, client, db):
        resposta = client.get(reverse('financas:dashboard'))
        assert resposta.status_code == 302
        assert '/usuarios/login/' in resposta.url

    @pytest.mark.django_db
    def test_dashboard_exibe_saldo(self, client_logado, receita, despesa):
        resposta = client_logado.get(reverse('financas:dashboard'))
        assert resposta.status_code == 200
        assert 'saldo' in resposta.context


# =============================================================================
# Receitas CRUD
# =============================================================================

class TestReceitaViews:
    """Testes para as views CRUD de Receita."""

    @pytest.mark.django_db
    def test_receita_lista_logado_retorna_200(self, client_logado):
        resposta = client_logado.get(reverse('financas:receita_lista'))
        assert resposta.status_code == 200

    def test_receita_lista_anonimo_redireciona_login(self, client, db):
        resposta = client.get(reverse('financas:receita_lista'))
        assert resposta.status_code == 302

    @pytest.mark.django_db
    def test_receita_criar_get_retorna_200(self, client_logado):
        resposta = client_logado.get(reverse('financas:receita_criar'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_receita_criar_post_valido_redireciona(self, client_logado, usuario, categoria_receita):
        dados = {
            'descricao': 'Freelance novo',
            'valor': '2000.00',
            'data': '2026-03-20',
            'categoria': categoria_receita.pk,
            'origem': 'freelance',
            'natureza': 'variavel',
        }
        resposta = client_logado.post(reverse('financas:receita_criar'), dados)
        assert resposta.status_code == 302
        assert Receita.objects.filter(user=usuario, descricao='Freelance novo').exists()

    @pytest.mark.django_db
    def test_receita_editar_propria_retorna_200(self, client_logado, receita):
        url = reverse('financas:receita_editar', kwargs={'pk': receita.pk})
        resposta = client_logado.get(url)
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_receita_editar_alheia_retorna_404(self, client_logado, outro_usuario):
        """Usuário não pode editar receita de outro usuário."""
        cat = Categoria.objects.create(
            user=outro_usuario, nome='Salário', tipo=Categoria.TipoCategoria.RECEITA,
        )
        receita_alheia = Receita.objects.create(
            user=outro_usuario,
            descricao='Receita alheia',
            valor=Decimal('1000.00'),
            data=datetime.date(2026, 3, 1),
            categoria=cat,
        )
        url = reverse('financas:receita_editar', kwargs={'pk': receita_alheia.pk})
        resposta = client_logado.get(url)
        assert resposta.status_code == 404

    @pytest.mark.django_db
    def test_receita_excluir_propria_funciona(self, client_logado, receita):
        url = reverse('financas:receita_excluir', kwargs={'pk': receita.pk})
        resposta = client_logado.post(url)
        assert resposta.status_code == 302
        assert not Receita.objects.filter(pk=receita.pk).exists()

    @pytest.mark.django_db
    def test_receita_excluir_alheia_retorna_404(self, client_logado, outro_usuario):
        """Usuário não pode excluir receita de outro usuário."""
        cat = Categoria.objects.create(
            user=outro_usuario, nome='Investimento', tipo=Categoria.TipoCategoria.RECEITA,
        )
        receita_alheia = Receita.objects.create(
            user=outro_usuario,
            descricao='Receita alheia',
            valor=Decimal('500.00'),
            data=datetime.date(2026, 3, 1),
            categoria=cat,
        )
        url = reverse('financas:receita_excluir', kwargs={'pk': receita_alheia.pk})
        resposta = client_logado.post(url)
        assert resposta.status_code == 404


# =============================================================================
# Despesas CRUD
# =============================================================================

class TestDespesaViews:
    """Testes para as views CRUD de Despesa."""

    @pytest.mark.django_db
    def test_despesa_lista_logado_retorna_200(self, client_logado):
        resposta = client_logado.get(reverse('financas:despesa_lista'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_despesa_criar_post_valido_redireciona(self, client_logado, usuario, categoria_despesa):
        dados = {
            'descricao': 'Farmácia',
            'valor': '120.00',
            'data': '2026-03-18',
            'categoria': categoria_despesa.pk,
            'origem': 'saude',
            'natureza': 'eventual',
        }
        resposta = client_logado.post(reverse('financas:despesa_criar'), dados)
        assert resposta.status_code == 302
        assert Despesa.objects.filter(user=usuario, descricao='Farmácia').exists()

    @pytest.mark.django_db
    def test_despesa_editar_alheia_retorna_404(self, client_logado, outro_usuario):
        """Usuário não pode editar despesa de outro usuário."""
        cat = Categoria.objects.create(
            user=outro_usuario, nome='Transporte', tipo=Categoria.TipoCategoria.DESPESA,
        )
        despesa_alheia = Despesa.objects.create(
            user=outro_usuario,
            descricao='Uber',
            valor=Decimal('30.00'),
            data=datetime.date(2026, 3, 10),
            categoria=cat,
        )
        url = reverse('financas:despesa_editar', kwargs={'pk': despesa_alheia.pk})
        resposta = client_logado.get(url)
        assert resposta.status_code == 404

    @pytest.mark.django_db
    def test_despesa_excluir_alheia_retorna_404(self, client_logado, outro_usuario):
        """Usuário não pode excluir despesa de outro usuário."""
        cat = Categoria.objects.create(
            user=outro_usuario, nome='Lazer', tipo=Categoria.TipoCategoria.DESPESA,
        )
        despesa_alheia = Despesa.objects.create(
            user=outro_usuario,
            descricao='Cinema',
            valor=Decimal('40.00'),
            data=datetime.date(2026, 3, 12),
            categoria=cat,
        )
        url = reverse('financas:despesa_excluir', kwargs={'pk': despesa_alheia.pk})
        resposta = client_logado.post(url)
        assert resposta.status_code == 404


# =============================================================================
# Categorias CRUD
# =============================================================================

class TestCategoriaViews:
    """Testes para as views CRUD de Categoria."""

    @pytest.mark.django_db
    def test_categoria_lista_logado_retorna_200(self, client_logado):
        resposta = client_logado.get(reverse('financas:categoria_lista'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_categoria_criar_post_valido_redireciona(self, client_logado, usuario):
        dados = {'nome': 'Educação', 'tipo': 'despesa'}
        resposta = client_logado.post(reverse('financas:categoria_criar'), dados)
        assert resposta.status_code == 302
        assert Categoria.objects.filter(user=usuario, nome='Educação').exists()

    @pytest.mark.django_db
    def test_categoria_editar_alheia_retorna_404(self, client_logado, outro_usuario):
        """Usuário não pode editar categoria de outro usuário."""
        cat_alheia = Categoria.objects.create(
            user=outro_usuario, nome='Moradia', tipo=Categoria.TipoCategoria.DESPESA,
        )
        url = reverse('financas:categoria_editar', kwargs={'pk': cat_alheia.pk})
        resposta = client_logado.get(url)
        assert resposta.status_code == 404

    @pytest.mark.django_db
    def test_categoria_excluir_retorna_200(self, client_logado, categoria_receita):
        """GET da página de confirmação de exclusão retorna 200."""
        url = reverse('financas:categoria_excluir', kwargs={'pk': categoria_receita.pk})
        resposta = client_logado.get(url)
        assert resposta.status_code == 200


# =============================================================================
# Exportação
# =============================================================================

class TestExportarViews:
    """Testes para as views de exportação."""

    @pytest.mark.django_db
    def test_exportar_json_retorna_200(self, client_logado, receita):
        url = reverse('financas:exportar', kwargs={'tipo': 'receita', 'formato': 'json'})
        resposta = client_logado.get(url)
        assert resposta.status_code == 200
        assert resposta['Content-Type'] == 'application/json'

    @pytest.mark.django_db
    def test_exportar_csv_retorna_200(self, client_logado, receita):
        url = reverse('financas:exportar', kwargs={'tipo': 'receita', 'formato': 'csv'})
        resposta = client_logado.get(url)
        assert resposta.status_code == 200
        assert 'text/csv' in resposta['Content-Type']

    @pytest.mark.django_db
    def test_exportar_pdf_retorna_200(self, client_logado, receita):
        url = reverse('financas:exportar', kwargs={'tipo': 'receita', 'formato': 'pdf'})
        resposta = client_logado.get(url)
        assert resposta.status_code == 200
        assert resposta['Content-Type'] == 'application/pdf'

    @pytest.mark.django_db
    def test_exportar_tipo_invalido_retorna_404(self, client_logado):
        url = reverse('financas:exportar', kwargs={'tipo': 'invalido', 'formato': 'json'})
        resposta = client_logado.get(url)
        assert resposta.status_code == 404

    @pytest.mark.django_db
    def test_exportar_formato_invalido_retorna_404(self, client_logado):
        url = reverse('financas:exportar', kwargs={'tipo': 'receita', 'formato': 'xml'})
        resposta = client_logado.get(url)
        assert resposta.status_code == 404


# =============================================================================
# Configuração de Alertas
# =============================================================================

class TestConfiguracaoAlertasView:
    """Testes para a view de configuração de alertas."""

    @pytest.mark.django_db
    def test_get_configuracao(self, client_logado):
        """GET deve retornar 200 e renderizar formulário."""
        resposta = client_logado.get(reverse('financas:configuracao_alertas'))
        assert resposta.status_code == 200
        assert 'form' in resposta.context

    @pytest.mark.django_db
    def test_post_configuracao(self, client_logado):
        """POST com dados válidos deve salvar e redirecionar."""
        dados = {
            'alerta_orcamento_ativo': True,
            'limiar_orcamento': 90,
            'alerta_gasto_acelerado_ativo': True,
            'alerta_saldo_baixo_ativo': False,
            'limite_saldo_minimo': '200.00',
        }
        resposta = client_logado.post(reverse('financas:configuracao_alertas'), dados)
        assert resposta.status_code == 302


# =============================================================================
# Orçamento CRUD
# =============================================================================

class TestOrcamentoViews:
    """Testes para as views CRUD de Orçamento."""

    @pytest.mark.django_db
    def test_lista(self, client_logado):
        """GET da lista deve retornar 200."""
        resposta = client_logado.get(reverse('financas:orcamento_lista'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_criar(self, client_logado, usuario):
        """POST com dados válidos deve criar orçamento e redirecionar."""
        dados = {'mes': 6, 'ano': 2026, 'valor': '2500.00'}
        resposta = client_logado.post(reverse('financas:orcamento_criar'), dados)
        assert resposta.status_code == 302
        assert Orcamento.objects.filter(user=usuario, mes=6, ano=2026).exists()

    @pytest.mark.django_db
    def test_editar(self, client_logado, orcamento):
        """POST de edição deve atualizar o orçamento."""
        url = reverse('financas:orcamento_editar', kwargs={'pk': orcamento.pk})
        dados = {'mes': 3, 'ano': 2026, 'valor': '4000.00'}
        resposta = client_logado.post(url, dados)
        assert resposta.status_code == 302
        orcamento.refresh_from_db()
        assert orcamento.valor == Decimal('4000.00')

    @pytest.mark.django_db
    def test_excluir(self, client_logado, orcamento):
        """POST de exclusão deve remover o orçamento."""
        url = reverse('financas:orcamento_excluir', kwargs={'pk': orcamento.pk})
        resposta = client_logado.post(url)
        assert resposta.status_code == 302
        assert not Orcamento.objects.filter(pk=orcamento.pk).exists()

    @pytest.mark.django_db
    def test_editar_orcamento_outro_usuario(self, client_logado, outro_usuario):
        """Não deve permitir editar orçamento de outro usuário → 404."""
        orc_outro = Orcamento.objects.create(
            user=outro_usuario, mes=5, ano=2026, valor=Decimal('2000.00'),
        )
        url = reverse('financas:orcamento_editar', kwargs={'pk': orc_outro.pk})
        resposta = client_logado.get(url)
        assert resposta.status_code == 404

    @pytest.mark.django_db
    def test_excluir_orcamento_outro_usuario(self, client_logado, outro_usuario):
        """Não deve permitir excluir orçamento de outro usuário → 404."""
        orc_outro = Orcamento.objects.create(
            user=outro_usuario, mes=5, ano=2026, valor=Decimal('2000.00'),
        )
        url = reverse('financas:orcamento_excluir', kwargs={'pk': orc_outro.pk})
        resposta = client_logado.post(url)
        assert resposta.status_code == 404


# =============================================================================
# Calendário (Heat Zone) — Módulo 3
# =============================================================================

class TestCalendarioViews:
    """Testes para as views do calendário (Heat Zone)."""

    @pytest.mark.django_db
    def test_calendario_view_status_200(self, client_logado):
        """GET /financas/calendario/ → 200."""
        resposta = client_logado.get(reverse('financas:calendario'))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_calendario_view_com_mes_ano(self, client_logado):
        """GET /financas/calendario/2026/3/ → 200, contexto com mes=3."""
        resposta = client_logado.get(reverse('financas:calendario_mes', kwargs={'ano': 2026, 'mes': 3}))
        assert resposta.status_code == 200
        assert resposta.context['mes'] == 3

    def test_calendario_view_redirect_anonimo(self, client, db):
        """Sem login → redirect para login."""
        resposta = client.get(reverse('financas:calendario'))
        assert resposta.status_code == 302
        assert '/usuarios/login/' in resposta.url

    @pytest.mark.django_db
    def test_detalhes_dia_status_200(self, client_logado):
        """GET /financas/calendario/2026/3/5/ → 200."""
        resposta = client_logado.get(reverse('financas:calendario_dia', kwargs={'ano': 2026, 'mes': 3, 'dia': 5}))
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_detalhes_dia_invalido_404(self, client_logado):
        """GET /financas/calendario/2026/2/30/ → 404."""
        resposta = client_logado.get(reverse('financas:calendario_dia', kwargs={'ano': 2026, 'mes': 2, 'dia': 30}))
        assert resposta.status_code == 404

    @pytest.mark.django_db
    def test_detalhes_dia_isolamento(self, client_logado, usuario, outro_usuario):
        """Detalhes de um dia não mostra dados de outro_usuario."""
        cat_outro = Categoria.objects.create(user=outro_usuario, nome='Outro', tipo=Categoria.TipoCategoria.DESPESA)
        Despesa.objects.create(user=outro_usuario, descricao='Gasto alheio', valor=Decimal('999.00'),
            data=datetime.date(2026, 3, 5), categoria=cat_outro)

        resposta = client_logado.get(reverse('financas:calendario_dia', kwargs={'ano': 2026, 'mes': 3, 'dia': 5}))
        assert resposta.status_code == 200
        # A despesa do outro_usuario não deve aparecer no contexto
        detalhes = resposta.context.get('detalhes', {})
        assert detalhes.get('total_despesas', Decimal('0')) == Decimal('0')


# =============================================================================
# Balança Views
# =============================================================================

class TestBalancaViews:
    """Testes para views da aba receita_despesa no calendário."""

    @pytest.mark.django_db
    def test_calendario_aba_receita_despesa(self, client_logado, receita, despesa):
        """GET com ?aba=receita_despesa → 200 + contexto tem dados_balanca."""
        resposta = client_logado.get(
            reverse('financas:calendario') + '?aba=receita_despesa&mes=3&ano=2026',
        )
        assert resposta.status_code == 200
        assert 'dados_balanca' in resposta.context
        assert 'resumo_balanca' in resposta.context

    @pytest.mark.django_db
    def test_calendario_mes_invalido_nao_crasheia(self, client_logado):
        """GET com ?mes=abc → 200 (fallback para mês atual)."""
        resposta = client_logado.get(
            reverse('financas:calendario') + '?mes=abc&ano=2026',
        )
        assert resposta.status_code == 200

    @pytest.mark.django_db
    def test_calendario_aba_invalida_fallback(self, client_logado):
        """GET com ?aba=xyz → 200 + aba_ativa=heatzone."""
        resposta = client_logado.get(
            reverse('financas:calendario') + '?aba=xyz',
        )
        assert resposta.status_code == 200
        assert resposta.context.get('aba_ativa') == 'heatzone'
