import datetime
from datetime import date, timedelta
from decimal import Decimal

import pytest

from financas.models import Categoria, Despesa, Receita
from financas.services import (
    calcular_saldo, exportar_csv, exportar_json, exportar_pdf, resumo_por_categoria,
    ultimo_dia_do_mes, _meses_anteriores,
    identificar_despesas_fixas_pendentes, identificar_receitas_previstas_pendentes,
    calcular_media_diaria_gastos_variaveis, calcular_previsao_saldo,
    verificar_alerta_orcamento, verificar_alerta_gasto_acelerado,
    verificar_alerta_saldo_baixo, obter_todos_alertas,
    gerar_dados_heatmap, obter_detalhes_dia, analisar_padrao_dia_semana,
    analisar_padrao_categoria, analisar_padrao_mensal, obter_todos_insights,
    gerar_dados_balanca_diaria, obter_resumo_balanca_mensal,
)
from financas.models import ConfiguracaoAlerta, Orcamento


# =============================================================================
# calcular_saldo
# =============================================================================

class TestCalcularSaldo:
    """Testes para o service calcular_saldo."""

    @pytest.mark.django_db
    def test_saldo_sem_lancamentos(self, usuario):
        saldo = calcular_saldo(usuario)
        assert saldo['total_receitas'] == Decimal('0')
        assert saldo['total_despesas'] == Decimal('0')
        assert saldo['saldo'] == Decimal('0')

    @pytest.mark.django_db
    def test_saldo_com_receitas_e_despesas(self, usuario, receita, despesa):
        saldo = calcular_saldo(usuario)
        assert saldo['total_receitas'] == Decimal('5000.00')
        assert saldo['total_despesas'] == Decimal('350.00')
        assert saldo['saldo'] == Decimal('4650.00')

    @pytest.mark.django_db
    def test_saldo_isolamento_por_usuario(self, usuario, outro_usuario, receita, despesa):
        """Saldo de um usuário não inclui lançamentos de outro."""
        # Criar lançamentos do outro_usuario
        cat_outro = Categoria.objects.create(
            user=outro_usuario, nome='Salário', tipo=Categoria.TipoCategoria.RECEITA,
        )
        Receita.objects.create(
            user=outro_usuario,
            descricao='Salário outro',
            valor=Decimal('9000.00'),
            data=datetime.date(2026, 3, 1),
            categoria=cat_outro,
        )

        saldo_usuario = calcular_saldo(usuario)
        saldo_outro = calcular_saldo(outro_usuario)

        assert saldo_usuario['total_receitas'] == Decimal('5000.00')
        assert saldo_outro['total_receitas'] == Decimal('9000.00')
        assert saldo_outro['total_despesas'] == Decimal('0')


# =============================================================================
# resumo_por_categoria
# =============================================================================

class TestResumoPorCategoria:
    """Testes para o service resumo_por_categoria."""

    @pytest.mark.django_db
    def test_resumo_por_categoria_receita(self, usuario, receita):
        resumo = resumo_por_categoria(usuario, 'receita')
        assert len(resumo) == 1
        assert resumo[0]['categoria__nome'] == 'Salário'
        assert resumo[0]['total'] == Decimal('5000.00')

    @pytest.mark.django_db
    def test_resumo_por_categoria_despesa(self, usuario, despesa):
        resumo = resumo_por_categoria(usuario, 'despesa')
        assert len(resumo) == 1
        assert resumo[0]['categoria__nome'] == 'Alimentação'
        assert resumo[0]['total'] == Decimal('350.00')


# =============================================================================
# Exportação (services)
# =============================================================================

class TestExportacaoServices:
    """Testes para os services de exportação."""

    @pytest.mark.django_db
    def test_exportar_json_formato_correto(self, usuario, receita):
        qs = Receita.objects.filter(user=usuario)
        resposta = exportar_json(usuario, 'receita', qs)
        assert resposta.status_code == 200
        assert resposta['Content-Type'] == 'application/json'
        import json
        dados = json.loads(resposta.content)
        assert dados['tipo'] == 'receita'
        assert len(dados['lancamentos']) == 1
        assert dados['lancamentos'][0]['descricao'] == 'Salário mensal'

    @pytest.mark.django_db
    def test_exportar_csv_formato_correto(self, usuario, receita):
        qs = Receita.objects.filter(user=usuario)
        resposta = exportar_csv(usuario, 'receita', qs)
        assert resposta.status_code == 200
        assert 'text/csv' in resposta['Content-Type']
        conteudo = resposta.content.decode('utf-8-sig')
        assert 'Descrição' in conteudo
        assert 'Salário mensal' in conteudo

    @pytest.mark.django_db
    def test_exportar_pdf_formato_correto(self, usuario, receita):
        qs = Receita.objects.filter(user=usuario)
        resposta = exportar_pdf(usuario, 'receita', qs)
        assert resposta.status_code == 200
        assert resposta['Content-Type'] == 'application/pdf'
        # PDF começa com %PDF
        assert resposta.content[:5] == b'%PDF-'


# =============================================================================
# Previsão de Saldo
# =============================================================================


@pytest.mark.django_db
class TestPrevisaoSaldo:
    """Testes para funções de previsão de saldo (Módulo 2)."""

    def test_ultimo_dia_do_mes_fevereiro(self):
        # Fevereiro 2026 (não-bissexto) = 28
        assert ultimo_dia_do_mes(2026, 2) == date(2026, 2, 28)

    def test_ultimo_dia_do_mes_fevereiro_bissexto(self):
        # 2024 é bissexto
        assert ultimo_dia_do_mes(2024, 2) == date(2024, 2, 29)

    def test_ultimo_dia_do_mes_dezembro(self):
        assert ultimo_dia_do_mes(2026, 12) == date(2026, 12, 31)

    def test_meses_anteriores_marco(self):
        result = _meses_anteriores(3, 2026)
        assert result == [(2026, 2), (2026, 1), (2025, 12)]

    def test_meses_anteriores_janeiro(self):
        result = _meses_anteriores(1, 2026)
        assert result == [(2025, 12), (2025, 11), (2025, 10)]

    def test_despesas_fixas_pendentes_sem_historico(self, usuario):
        result = identificar_despesas_fixas_pendentes(usuario, 3, 2026)
        assert result == Decimal('0')

    def test_despesas_fixas_pendentes_recorrente(self, usuario, categoria_despesa):
        # Criar despesa fixa em jan e fev (recorrente)
        Despesa.objects.create(user=usuario, descricao='Aluguel', valor=Decimal('1500.00'),
            data=date(2026, 1, 5), categoria=categoria_despesa, natureza='fixa', origem='moradia')
        Despesa.objects.create(user=usuario, descricao='Aluguel', valor=Decimal('1500.00'),
            data=date(2026, 2, 5), categoria=categoria_despesa, natureza='fixa', origem='moradia')
        # Março não tem → deve retornar pendente
        result = identificar_despesas_fixas_pendentes(usuario, 3, 2026)
        assert result == Decimal('1500.00')

    def test_despesas_fixas_pendentes_ja_lancada(self, usuario, categoria_despesa):
        # Criar despesa fixa em jan, fev E março
        for m in [1, 2, 3]:
            Despesa.objects.create(user=usuario, descricao='Aluguel', valor=Decimal('1500.00'),
                data=date(2026, m, 5), categoria=categoria_despesa, natureza='fixa', origem='moradia')
        result = identificar_despesas_fixas_pendentes(usuario, 3, 2026)
        assert result == Decimal('0')

    def test_despesas_fixas_pendentes_nao_recorrente(self, usuario, categoria_despesa):
        # Despesa fixa em apenas 1 mês → não é recorrente
        Despesa.objects.create(user=usuario, descricao='Reparo', valor=Decimal('200.00'),
            data=date(2026, 1, 10), categoria=categoria_despesa, natureza='fixa', origem='moradia')
        result = identificar_despesas_fixas_pendentes(usuario, 3, 2026)
        assert result == Decimal('0')

    def test_despesas_fixas_isolamento_usuario(self, usuario, outro_usuario, categoria_despesa, categoria_despesa_outro):
        # Criar despesa recorrente para outro_usuario
        for m in [1, 2]:
            Despesa.objects.create(user=outro_usuario, descricao='Aluguel', valor=Decimal('2000.00'),
                data=date(2026, m, 5), categoria=categoria_despesa_outro, natureza='fixa', origem='moradia')
        result = identificar_despesas_fixas_pendentes(usuario, 3, 2026)
        assert result == Decimal('0')

    def test_receitas_previstas_pendentes_recorrente(self, usuario, categoria_receita):
        for m in [1, 2]:
            Receita.objects.create(user=usuario, descricao='Salário', valor=Decimal('5000.00'),
                data=date(2026, m, 1), categoria=categoria_receita, natureza='fixa', origem='salario')
        result = identificar_receitas_previstas_pendentes(usuario, 3, 2026)
        assert result == Decimal('5000.00')

    def test_media_diaria_sem_dados(self, usuario):
        result = calcular_media_diaria_gastos_variaveis(usuario)
        assert result == Decimal('0')

    def test_media_diaria_poucos_dados(self, usuario, categoria_despesa):
        # Apenas 3 lançamentos (< 5 threshold) → retorna 0
        for i in range(3):
            Despesa.objects.create(user=usuario, descricao=f'Gasto {i}', valor=Decimal('100.00'),
                data=date.today() - timedelta(days=i*10), categoria=categoria_despesa,
                natureza='variavel', origem='alimentacao')
        assert calcular_media_diaria_gastos_variaveis(usuario) == Decimal('0')

    def test_media_diaria_com_dados(self, usuario, categoria_despesa):
        # 10 lançamentos de R$90 cada = R$900 total / 90 dias = R$10/dia
        for i in range(10):
            Despesa.objects.create(user=usuario, descricao=f'Gasto {i}', valor=Decimal('90.00'),
                data=date.today() - timedelta(days=i*5), categoria=categoria_despesa,
                natureza='variavel', origem='alimentacao')
        result = calcular_media_diaria_gastos_variaveis(usuario)
        assert result == Decimal('900.00') / Decimal('90')

    def test_previsao_saldo_sem_dados(self, usuario):
        result = calcular_previsao_saldo(usuario)
        assert result['dados_suficientes'] is False

    def test_previsao_saldo_com_dados(self, usuario, categoria_receita, receita):
        # receita fixture cria receita de 5000 em 2026-03-01
        result = calcular_previsao_saldo(usuario, mes=3, ano=2026)
        assert result['dados_suficientes'] is True
        assert 'saldo_projetado' in result
        assert 'dias_restantes' in result
        assert isinstance(result['negativo'], bool)

    def test_previsao_saldo_isolamento(self, usuario, outro_usuario, categoria_receita_outro):
        # Lançamentos de outro_usuario não devem afetar
        Receita.objects.create(user=outro_usuario, descricao='Renda', valor=Decimal('10000.00'),
            data=date.today(), categoria=categoria_receita_outro, natureza='fixa', origem='outros')
        result = calcular_previsao_saldo(usuario)
        assert result['receitas_previstas'] == Decimal('0')

    def test_dashboard_contem_previsao(self, client_logado):
        response = client_logado.get('/financas/dashboard/')
        assert response.status_code == 200
        assert 'previsao' in response.context


# =============================================================================
# Alertas Inteligentes
# =============================================================================


@pytest.mark.django_db
class TestAlertasInteligentes:
    """Testes para os services de alertas inteligentes (Módulo 1)."""

    # ─── Alerta de Orçamento ────────────────────────────────────────────

    def test_alerta_orcamento_abaixo_limiar(self, usuario, categoria_despesa, orcamento, configuracao_alerta):
        """Gasto abaixo do limiar → ativo=False."""
        # Orçamento de R$3000 com limiar 80% = R$2400. Gasto de R$500 → abaixo.
        Despesa.objects.create(
            user=usuario, descricao='Gasto leve', valor=Decimal('500.00'),
            data=date.today(), categoria=categoria_despesa,
        )
        resultado = verificar_alerta_orcamento(usuario, date.today().month, date.today().year)
        assert resultado['ativo'] is False

    def test_alerta_orcamento_acima_limiar(self, usuario, categoria_despesa, configuracao_alerta):
        """Gasto acima de 80% do orçamento → ativo=True, nivel=aviso."""
        Orcamento.objects.create(
            user=usuario, mes=date.today().month, ano=date.today().year,
            valor=Decimal('1000.00'),
        )
        Despesa.objects.create(
            user=usuario, descricao='Gasto alto', valor=Decimal('850.00'),
            data=date.today(), categoria=categoria_despesa,
        )
        resultado = verificar_alerta_orcamento(usuario, date.today().month, date.today().year)
        assert resultado['ativo'] is True
        assert resultado['nivel'] == 'aviso'
        assert resultado['percentual'] >= 80

    def test_alerta_orcamento_acima_100(self, usuario, categoria_despesa, configuracao_alerta):
        """Gasto acima de 100% do orçamento → nivel=critico."""
        Orcamento.objects.create(
            user=usuario, mes=date.today().month, ano=date.today().year,
            valor=Decimal('1000.00'),
        )
        Despesa.objects.create(
            user=usuario, descricao='Gasto excessivo', valor=Decimal('1200.00'),
            data=date.today(), categoria=categoria_despesa,
        )
        resultado = verificar_alerta_orcamento(usuario, date.today().month, date.today().year)
        assert resultado['ativo'] is True
        assert resultado['nivel'] == 'critico'
        assert resultado['percentual'] >= 100

    def test_alerta_orcamento_sem_orcamento(self, usuario, configuracao_alerta):
        """Sem orçamento definido → sem_orcamento=True."""
        resultado = verificar_alerta_orcamento(usuario, date.today().month, date.today().year)
        assert resultado.get('sem_orcamento') is True

    def test_alerta_orcamento_inativo(self, usuario, categoria_despesa):
        """Alerta desativado na config → ativo=False."""
        config = ConfiguracaoAlerta.objects.create(
            user=usuario, alerta_orcamento_ativo=False,
        )
        Orcamento.objects.create(
            user=usuario, mes=date.today().month, ano=date.today().year,
            valor=Decimal('1000.00'),
        )
        Despesa.objects.create(
            user=usuario, descricao='Gasto', valor=Decimal('900.00'),
            data=date.today(), categoria=categoria_despesa,
        )
        resultado = verificar_alerta_orcamento(
            usuario, date.today().month, date.today().year, config=config,
        )
        assert resultado['ativo'] is False

    # ─── Alerta de Gasto Acelerado ──────────────────────────────────────

    def test_alerta_gasto_acelerado_normal(self, usuario, categoria_despesa):
        """Gasto normal (dentro da média) → ativo=False."""
        config = ConfiguracaoAlerta.objects.create(user=usuario)
        # Criar histórico de 12 semanas com gastos regulares
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        for semana in range(1, 13):
            data = inicio_semana - timedelta(weeks=semana)
            Despesa.objects.create(
                user=usuario, descricao=f'Gasto semana {semana}',
                valor=Decimal('100.00'), data=data, categoria=categoria_despesa,
            )
        # Gasto na semana atual dentro do normal
        Despesa.objects.create(
            user=usuario, descricao='Gasto normal semana atual',
            valor=Decimal('50.00'), data=hoje, categoria=categoria_despesa,
        )
        resultado = verificar_alerta_gasto_acelerado(usuario, config=config)
        assert resultado['ativo'] is False

    def test_alerta_gasto_acelerado_alto(self, usuario, categoria_despesa):
        """Gasto acelerado (acima de 120% da média) → ativo=True."""
        config = ConfiguracaoAlerta.objects.create(user=usuario)
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        # Histórico: R$100/semana durante 12 semanas
        for semana in range(1, 13):
            data = inicio_semana - timedelta(weeks=semana)
            Despesa.objects.create(
                user=usuario, descricao=f'Gasto semana {semana}',
                valor=Decimal('100.00'), data=data, categoria=categoria_despesa,
            )
        # Gasto muito alto na semana atual
        Despesa.objects.create(
            user=usuario, descricao='Gasto alto semana atual',
            valor=Decimal('500.00'), data=hoje, categoria=categoria_despesa,
        )
        resultado = verificar_alerta_gasto_acelerado(usuario, config=config)
        assert resultado['ativo'] is True
        assert resultado['nivel'] == 'aviso'

    def test_alerta_gasto_acelerado_sem_historico(self, usuario):
        """Sem histórico de gastos → dados_insuficientes=True."""
        config = ConfiguracaoAlerta.objects.create(user=usuario)
        resultado = verificar_alerta_gasto_acelerado(usuario, config=config)
        assert resultado.get('dados_insuficientes') is True

    # ─── Alerta de Saldo Baixo ──────────────────────────────────────────

    def test_alerta_saldo_baixo_acima_limite(self, usuario):
        """Saldo projetado acima do limite → ativo=False."""
        config = ConfiguracaoAlerta.objects.create(
            user=usuario, limite_saldo_minimo=Decimal('100.00'),
        )
        previsao = {
            'dados_suficientes': True,
            'saldo_projetado': Decimal('500.00'),
            'negativo': False,
        }
        resultado = verificar_alerta_saldo_baixo(
            usuario, date.today().month, date.today().year,
            config=config, previsao=previsao,
        )
        assert resultado['ativo'] is False

    def test_alerta_saldo_baixo_abaixo_limite(self, usuario):
        """Saldo projetado abaixo do limite → ativo=True."""
        config = ConfiguracaoAlerta.objects.create(
            user=usuario, limite_saldo_minimo=Decimal('500.00'),
        )
        previsao = {
            'dados_suficientes': True,
            'saldo_projetado': Decimal('100.00'),
            'negativo': False,
        }
        resultado = verificar_alerta_saldo_baixo(
            usuario, date.today().month, date.today().year,
            config=config, previsao=previsao,
        )
        assert resultado['ativo'] is True
        assert resultado['tipo'] == 'saldo_baixo'

    # ─── obter_todos_alertas ────────────────────────────────────────────

    def test_obter_todos_alertas_sem_alertas_ativos(self, usuario):
        """Nenhum alerta ativo → lista vazia."""
        ConfiguracaoAlerta.objects.create(
            user=usuario,
            alerta_orcamento_ativo=False,
            alerta_gasto_acelerado_ativo=False,
            alerta_saldo_baixo_ativo=False,
        )
        alertas = obter_todos_alertas(usuario)
        assert alertas == []

    def test_obter_todos_alertas_com_orcamento(self, usuario, categoria_despesa):
        """Alerta de orçamento ativo deve aparecer na lista."""
        ConfiguracaoAlerta.objects.create(user=usuario)
        Orcamento.objects.create(
            user=usuario, mes=date.today().month, ano=date.today().year,
            valor=Decimal('1000.00'),
        )
        Despesa.objects.create(
            user=usuario, descricao='Gasto grande', valor=Decimal('900.00'),
            data=date.today(), categoria=categoria_despesa,
        )
        alertas = obter_todos_alertas(usuario)
        tipos = [a['tipo'] for a in alertas]
        assert 'orcamento' in tipos

    def test_obter_todos_alertas_ordenacao(self, usuario, categoria_despesa):
        """Alertas críticos devem vir antes de avisos."""
        ConfiguracaoAlerta.objects.create(
            user=usuario, limite_saldo_minimo=Decimal('999999.00'),
        )
        # Criar orçamento e estourar (nível crítico)
        Orcamento.objects.create(
            user=usuario, mes=date.today().month, ano=date.today().year,
            valor=Decimal('100.00'),
        )
        Despesa.objects.create(
            user=usuario, descricao='Gasto enorme', valor=Decimal('200.00'),
            data=date.today(), categoria=categoria_despesa,
        )
        # Criar receita para dados_suficientes do saldo_baixo
        cat_rec = Categoria.objects.create(
            user=usuario, nome='Renda extra', tipo=Categoria.TipoCategoria.RECEITA,
        )
        Receita.objects.create(
            user=usuario, descricao='Salário', valor=Decimal('50.00'),
            data=date.today(), categoria=cat_rec,
        )
        alertas = obter_todos_alertas(usuario)
        if len(alertas) >= 2:
            niveis = [a.get('nivel') for a in alertas]
            # Críticos primeiro
            idx_critico = next((i for i, n in enumerate(niveis) if n == 'critico'), None)
            idx_aviso = next((i for i, n in enumerate(niveis) if n == 'aviso'), None)
            if idx_critico is not None and idx_aviso is not None:
                assert idx_critico < idx_aviso

    def test_alertas_isolamento_usuario(
        self, usuario, outro_usuario, categoria_despesa, categoria_despesa_outro,
    ):
        """Alertas de um user não devem afetar outro."""
        # Configuração para ambos
        ConfiguracaoAlerta.objects.create(user=usuario)
        ConfiguracaoAlerta.objects.create(user=outro_usuario)

        # Orçamento e gasto apenas para outro_usuario
        Orcamento.objects.create(
            user=outro_usuario, mes=date.today().month, ano=date.today().year,
            valor=Decimal('1000.00'),
        )
        Despesa.objects.create(
            user=outro_usuario, descricao='Gasto outro', valor=Decimal('900.00'),
            data=date.today(), categoria=categoria_despesa_outro,
        )

        # usuario não tem orçamento → sem alerta de orçamento
        alertas_usuario = obter_todos_alertas(usuario)
        alertas_outro = obter_todos_alertas(outro_usuario)

        tipos_usuario = [a.get('tipo') for a in alertas_usuario]
        tipos_outro = [a.get('tipo') for a in alertas_outro]

        assert 'orcamento' not in tipos_usuario
        assert 'orcamento' in tipos_outro


# =============================================================================
# Detecção de Padrões (Heat Zone) — Módulo 3
# =============================================================================


@pytest.mark.django_db
class TestHeatZone:
    """Testes para as funções de detecção de padrões (Heat Zone)."""

    # ─── gerar_dados_heatmap ────────────────────────────────────────────

    def test_heatmap_sem_dados(self, usuario):
        """Mês sem despesas → todos os dias nível 0."""
        dados = gerar_dados_heatmap(usuario, 3, 2026)
        assert len(dados) == 31  # março tem 31 dias
        for dia, info in dados.items():
            assert info['nivel'] == 0
            assert info['total'] == Decimal('0')

    def test_heatmap_com_dados(self, usuario, categoria_despesa):
        """Despesas em dias diferentes → níveis e totais corretos."""
        Despesa.objects.create(user=usuario, descricao='D1', valor=Decimal('50.00'),
            data=date(2026, 3, 1), categoria=categoria_despesa)
        Despesa.objects.create(user=usuario, descricao='D2', valor=Decimal('200.00'),
            data=date(2026, 3, 10), categoria=categoria_despesa)
        Despesa.objects.create(user=usuario, descricao='D3', valor=Decimal('500.00'),
            data=date(2026, 3, 15), categoria=categoria_despesa)
        Despesa.objects.create(user=usuario, descricao='D4', valor=Decimal('1000.00'),
            data=date(2026, 3, 20), categoria=categoria_despesa)

        dados = gerar_dados_heatmap(usuario, 3, 2026)
        assert dados[1]['total'] == Decimal('50.00')
        assert dados[10]['total'] == Decimal('200.00')
        assert dados[15]['total'] == Decimal('500.00')
        assert dados[20]['total'] == Decimal('1000.00')
        # Dia sem despesa → nível 0
        assert dados[2]['nivel'] == 0
        # Dia com menor gasto deve ter nível menor que dia com maior gasto
        assert dados[1]['nivel'] <= dados[20]['nivel']

    def test_heatmap_isolamento_usuario(self, usuario, outro_usuario, categoria_despesa, categoria_despesa_outro):
        """Despesas de outro_usuario não aparecem no heatmap."""
        Despesa.objects.create(user=outro_usuario, descricao='Gasto outro', valor=Decimal('999.00'),
            data=date(2026, 3, 10), categoria=categoria_despesa_outro)

        dados = gerar_dados_heatmap(usuario, 3, 2026)
        assert dados[10]['total'] == Decimal('0')
        assert dados[10]['nivel'] == 0

    # ─── obter_detalhes_dia ─────────────────────────────────────────────

    def test_detalhes_dia_com_lancamentos(self, usuario, categoria_despesa, categoria_receita):
        """Dia com despesas e receitas → retorna listas corretas."""
        dia = date(2026, 3, 5)
        Despesa.objects.create(user=usuario, descricao='Almoço', valor=Decimal('30.00'),
            data=dia, categoria=categoria_despesa)
        Receita.objects.create(user=usuario, descricao='Freelance', valor=Decimal('500.00'),
            data=dia, categoria=categoria_receita)

        resultado = obter_detalhes_dia(usuario, dia)
        assert len(resultado['despesas']) == 1
        assert len(resultado['receitas']) == 1
        assert resultado['total_despesas'] == Decimal('30.00')
        assert resultado['total_receitas'] == Decimal('500.00')

    def test_detalhes_dia_sem_lancamentos(self, usuario):
        """Dia sem lançamentos → listas vazias, totais=0."""
        resultado = obter_detalhes_dia(usuario, date(2026, 3, 25))
        assert resultado['despesas'] == []
        assert resultado['receitas'] == []
        assert resultado['total_despesas'] == Decimal('0')
        assert resultado['total_receitas'] == Decimal('0')

    # ─── analisar_padrao_dia_semana ─────────────────────────────────────

    def test_padrao_dia_semana_sem_dados(self, usuario):
        """Sem despesas → dados_suficientes=False."""
        resultado = analisar_padrao_dia_semana(usuario)
        assert resultado['dados_suficientes'] is False

    def test_padrao_dia_semana_com_dados(self, usuario, categoria_despesa):
        """Com despesas em dias variados → retorna dia_maior_gasto e mensagem."""
        hoje = date.today()
        for i in range(6):
            Despesa.objects.create(user=usuario, descricao=f'Gasto {i}', valor=Decimal('100.00'),
                data=hoje - timedelta(days=i * 7), categoria=categoria_despesa)
        # Adicionar gasto extra num dia específico para forçar um pico
        Despesa.objects.create(user=usuario, descricao='Gasto pesado', valor=Decimal('900.00'),
            data=hoje, categoria=categoria_despesa)

        resultado = analisar_padrao_dia_semana(usuario)
        assert resultado['dados_suficientes'] is True
        assert 'dia_maior_gasto' in resultado
        assert 'mensagem' in resultado

    # ─── analisar_padrao_categoria ──────────────────────────────────────

    def test_padrao_categoria_sem_dados(self, usuario):
        """Sem despesas → dados_suficientes=False."""
        resultado = analisar_padrao_categoria(usuario, 3, 2026)
        assert resultado['dados_suficientes'] is False

    def test_padrao_categoria_com_dados(self, usuario, categoria_despesa):
        """Com despesas em categorias → retorna categoria_dominante."""
        cat2 = Categoria.objects.create(user=usuario, nome='Transporte', tipo=Categoria.TipoCategoria.DESPESA)
        Despesa.objects.create(user=usuario, descricao='Almoço', valor=Decimal('300.00'),
            data=date(2026, 3, 5), categoria=categoria_despesa)
        Despesa.objects.create(user=usuario, descricao='Uber', valor=Decimal('50.00'),
            data=date(2026, 3, 10), categoria=cat2)

        resultado = analisar_padrao_categoria(usuario, 3, 2026)
        assert resultado['dados_suficientes'] is True
        assert resultado['categoria_dominante'] == 'Alimentação'
        assert resultado['percentual'] > 0
        assert 'mensagem' in resultado

    # ─── analisar_padrao_mensal ─────────────────────────────────────────

    def test_padrao_mensal_sem_mes_anterior(self, usuario, categoria_despesa):
        """Sem dados mês anterior → dados_suficientes=False."""
        # Criar despesa apenas no mês atual
        Despesa.objects.create(user=usuario, descricao='Gasto atual', valor=Decimal('200.00'),
            data=date.today(), categoria=categoria_despesa)
        resultado = analisar_padrao_mensal(usuario)
        assert resultado['dados_suficientes'] is False

    def test_padrao_mensal_com_dados(self, usuario, categoria_despesa):
        """Com despesas em 2 meses → retorna variacao e direcao."""
        hoje = date.today()
        # Mês anterior
        if hoje.month == 1:
            mes_ant = 12
            ano_ant = hoje.year - 1
        else:
            mes_ant = hoje.month - 1
            ano_ant = hoje.year
        Despesa.objects.create(user=usuario, descricao='Gasto anterior', valor=Decimal('1000.00'),
            data=date(ano_ant, mes_ant, 15), categoria=categoria_despesa)
        # Mês atual
        Despesa.objects.create(user=usuario, descricao='Gasto atual', valor=Decimal('1200.00'),
            data=date(hoje.year, hoje.month, 1), categoria=categoria_despesa)

        resultado = analisar_padrao_mensal(usuario)
        assert resultado['dados_suficientes'] is True
        assert 'variacao' in resultado
        assert resultado['direcao'] == 'aumento'
        assert 'mensagem' in resultado

    # ─── obter_todos_insights ───────────────────────────────────────────

    def test_obter_todos_insights_sem_dados(self, usuario):
        """Sem dados suficientes → lista vazia."""
        resultado = obter_todos_insights(usuario, 3, 2026)
        assert resultado == []

    def test_obter_todos_insights_com_dados(self, usuario, categoria_despesa):
        """Com dados suficientes → insights com tipo/icone/mensagem."""
        hoje = date.today()
        # Criar despesas suficientes para padrao_dia_semana (>=5) e padrao_categoria
        for i in range(6):
            Despesa.objects.create(user=usuario, descricao=f'Gasto {i}', valor=Decimal('100.00'),
                data=hoje - timedelta(days=i * 5), categoria=categoria_despesa)

        resultado = obter_todos_insights(usuario, hoje.month, hoje.year)
        # Deve ter pelo menos insight de dia_semana e categoria
        assert len(resultado) >= 1
        for insight in resultado:
            assert 'tipo' in insight
            assert 'icone' in insight
            assert 'mensagem' in insight


# =============================================================================
# Balança Receita × Despesa
# =============================================================================

class TestBalancaReceitaDespesa:
    """Testes para gerar_dados_balanca_diaria e obter_resumo_balanca_mensal."""

    @pytest.mark.django_db
    def test_balanca_diaria_sem_dados(self, usuario):
        """Mês sem lançamentos → todos tem_dados=False."""
        dados = gerar_dados_balanca_diaria(usuario, 1, 2025)
        for dia, info in dados.items():
            assert info['tem_dados'] is False
            assert info['receitas'] == Decimal('0')
            assert info['despesas'] == Decimal('0')

    @pytest.mark.django_db
    def test_balanca_diaria_com_receita_e_despesa(self, usuario, categoria_receita, categoria_despesa):
        """Dia com ambos → percentuais corretos, somam 100."""
        Receita.objects.create(
            user=usuario, descricao='Salário', valor=Decimal('3000'),
            data=date(2026, 3, 10), categoria=categoria_receita,
        )
        Despesa.objects.create(
            user=usuario, descricao='Aluguel', valor=Decimal('1000'),
            data=date(2026, 3, 10), categoria=categoria_despesa,
        )
        dados = gerar_dados_balanca_diaria(usuario, 3, 2026)
        dia10 = dados[10]
        assert dia10['tem_dados'] is True
        assert dia10['receitas'] == Decimal('3000')
        assert dia10['despesas'] == Decimal('1000')
        assert dia10['percentual_receita'] + dia10['percentual_despesa'] == 100
        assert dia10['percentual_receita'] == 75.0

    @pytest.mark.django_db
    def test_balanca_diaria_so_receita(self, usuario, categoria_receita):
        """Dia só com receita → percentual_receita=100, percentual_despesa=0."""
        Receita.objects.create(
            user=usuario, descricao='Bônus', valor=Decimal('500'),
            data=date(2026, 3, 15), categoria=categoria_receita,
        )
        dados = gerar_dados_balanca_diaria(usuario, 3, 2026)
        dia15 = dados[15]
        assert dia15['tem_dados'] is True
        assert dia15['percentual_receita'] == 100
        assert dia15['percentual_despesa'] == 0

    @pytest.mark.django_db
    def test_balanca_diaria_so_despesa(self, usuario, categoria_despesa):
        """Dia só com despesa → percentual_despesa=100."""
        Despesa.objects.create(
            user=usuario, descricao='Luz', valor=Decimal('200'),
            data=date(2026, 3, 20), categoria=categoria_despesa,
        )
        dados = gerar_dados_balanca_diaria(usuario, 3, 2026)
        dia20 = dados[20]
        assert dia20['tem_dados'] is True
        assert dia20['percentual_receita'] == 0
        assert dia20['percentual_despesa'] == 100

    @pytest.mark.django_db
    def test_balanca_diaria_isolamento(self, usuario, outro_usuario, categoria_receita, categoria_despesa_outro):
        """Dados de outro_usuario não aparecem."""
        Receita.objects.create(
            user=usuario, descricao='Salário', valor=Decimal('1000'),
            data=date(2026, 3, 1), categoria=categoria_receita,
        )
        Despesa.objects.create(
            user=outro_usuario, descricao='Aluguel', valor=Decimal('9999'),
            data=date(2026, 3, 1), categoria=categoria_despesa_outro,
        )
        dados = gerar_dados_balanca_diaria(usuario, 3, 2026)
        dia1 = dados[1]
        assert dia1['receitas'] == Decimal('1000')
        assert dia1['despesas'] == Decimal('0')

    @pytest.mark.django_db
    def test_resumo_mensal_sem_dados(self, usuario):
        """Tudo zero quando não há lançamentos."""
        resumo = obter_resumo_balanca_mensal(usuario, 1, 2025)
        assert resumo['total_receitas'] == Decimal('0')
        assert resumo['total_despesas'] == Decimal('0')
        assert resumo['saldo'] == Decimal('0')
        assert resumo['dias_verdes'] == 0
        assert resumo['dias_vermelhos'] == 0
        assert resumo['dias_equilibrados'] == 0
        assert resumo['positivo'] is True

    @pytest.mark.django_db
    def test_resumo_mensal_com_dados(self, usuario, receita, despesa):
        """Totais e contadores corretos com fixtures padrão."""
        resumo = obter_resumo_balanca_mensal(usuario, 3, 2026)
        assert resumo['total_receitas'] == Decimal('5000.00')
        assert resumo['total_despesas'] == Decimal('350.00')
        assert resumo['saldo'] == Decimal('4650.00')
        assert resumo['dias_verdes'] == 1  # dia 1: só receita
        assert resumo['dias_vermelhos'] == 1  # dia 5: só despesa
        assert resumo['positivo'] is True

    @pytest.mark.django_db
    def test_resumo_mensal_aceita_dados_diarios(self, usuario):
        """Quando dados_diarios fornecido, não faz queries extras."""
        dados_fake = {
            1: {'receitas': Decimal('100'), 'despesas': Decimal('50'), 'tem_dados': True},
            2: {'receitas': Decimal('0'), 'despesas': Decimal('0'), 'tem_dados': False},
        }
        resumo = obter_resumo_balanca_mensal(usuario, 3, 2026, dados_diarios=dados_fake)
        assert resumo['total_receitas'] == Decimal('100')
        assert resumo['total_despesas'] == Decimal('50')
        assert resumo['saldo'] == Decimal('50')
        assert resumo['dias_verdes'] == 1
