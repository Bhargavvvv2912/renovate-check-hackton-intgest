import calendar
import csv
import io
import statistics
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.db.models import QuerySet, Sum
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from financas.models import ConfiguracaoAlerta, Despesa, Orcamento, Receita


NOMES_MESES = {
    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro',
}


def calcular_saldo(user: User) -> dict[str, Decimal]:
    """Calcula o saldo geral do usuário (receitas - despesas)."""
    total_receitas = (
        Receita.objects.filter(user=user).aggregate(total=Sum('valor'))['total']
        or Decimal('0')
    )
    total_despesas = (
        Despesa.objects.filter(user=user).aggregate(total=Sum('valor'))['total']
        or Decimal('0')
    )
    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': total_receitas - total_despesas,
    }


def calcular_saldo_por_periodo(
    user: User, data_inicio, data_fim,
) -> dict[str, Decimal]:
    """Calcula o saldo do usuário em um período específico."""
    total_receitas = (
        Receita.objects.filter(user=user, data__gte=data_inicio, data__lte=data_fim)
        .aggregate(total=Sum('valor'))['total']
        or Decimal('0')
    )
    total_despesas = (
        Despesa.objects.filter(user=user, data__gte=data_inicio, data__lte=data_fim)
        .aggregate(total=Sum('valor'))['total']
        or Decimal('0')
    )
    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': total_receitas - total_despesas,
    }


def resumo_por_categoria(
    user: User,
    tipo: str,
    data_inicio=None,
    data_fim=None,
) -> list[dict[str, Any]]:
    """Retorna lista de categorias com seus totais para o tipo informado."""
    modelo = Receita if tipo == 'receita' else Despesa
    qs = modelo.objects.filter(user=user)

    if data_inicio:
        qs = qs.filter(data__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data__lte=data_fim)

    return list(
        qs.values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )


def exportar_json(user: User, tipo: str, queryset: QuerySet) -> JsonResponse:
    """Exporta lançamentos em formato JSON."""
    dados = list(
        queryset.filter(user=user).values(
            'descricao', 'valor', 'data', 'categoria__nome', 'origem', 'natureza',
        )
    )
    # Converter datas e decimais para string
    for item in dados:
        item['valor'] = str(item['valor'])
        item['data'] = str(item['data'])

    return JsonResponse({'tipo': tipo, 'lancamentos': dados}, json_dumps_params={'ensure_ascii': False})


def exportar_csv(user: User, tipo: str, queryset: QuerySet) -> HttpResponse:
    """Exporta lançamentos em formato CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{tipo}s.csv"'
    response.write('\ufeff')  # BOM para Excel reconhecer UTF-8

    writer = csv.writer(response)
    writer.writerow(['Descrição', 'Valor', 'Data', 'Categoria', 'Origem', 'Natureza'])

    for item in queryset.filter(user=user).select_related('categoria'):
        writer.writerow([
            item.descricao,
            str(item.valor),
            item.data.strftime('%d/%m/%Y'),
            item.categoria.nome,
            item.get_origem_display(),
            item.get_natureza_display(),
        ])

    return response


def exportar_pdf(user: User, tipo: str, queryset: QuerySet) -> HttpResponse:
    """Exporta lançamentos em formato PDF usando reportlab."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{tipo}s.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos: list = []
    estilos = getSampleStyleSheet()

    # Título
    titulo = f'Relatório de {tipo.capitalize()}s'
    elementos.append(Paragraph(titulo, estilos['Title']))
    elementos.append(Spacer(1, 0.5 * cm))

    # Dados da tabela
    cabecalho = ['Descrição', 'Valor (R$)', 'Data', 'Categoria', 'Origem', 'Natureza']
    dados_tabela = [cabecalho]

    for item in queryset.filter(user=user).select_related('categoria'):
        dados_tabela.append([
            item.descricao[:40],
            f'{item.valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            item.data.strftime('%d/%m/%Y'),
            item.categoria.nome,
            item.get_origem_display(),
            item.get_natureza_display(),
        ])

    if len(dados_tabela) > 1:
        tabela = Table(dados_tabela, repeatRows=1)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elementos.append(tabela)
    else:
        elementos.append(Paragraph('Nenhum lançamento encontrado.', estilos['Normal']))

    doc.build(elementos)
    response.write(buffer.getvalue())
    buffer.close()

    return response


# ─── Previsão de Saldo ──────────────────────────────────────────────────────


def ultimo_dia_do_mes(ano: int, mes: int) -> date:
    """Retorna o último dia do mês informado."""
    _, ultimo_dia = calendar.monthrange(ano, mes)
    return date(ano, mes, ultimo_dia)


def _meses_anteriores(mes: int, ano: int, quantidade: int = 3) -> list[tuple[int, int]]:
    """Retorna lista de tuplas (ano, mês) dos meses anteriores ao informado."""
    resultado: list[tuple[int, int]] = []
    for i in range(1, quantidade + 1):
        m = mes - i
        a = ano
        while m <= 0:
            m += 12
            a -= 1
        resultado.append((a, m))
    return resultado


def _identificar_lancamentos_fixos_pendentes(
    modelo: type, user: User, mes: int, ano: int,
) -> Decimal:
    """
    Identifica lançamentos fixos recorrentes que ainda não foram registrados no mês.

    Analisa os últimos 3 meses para detectar padrões de recorrência.
    Considera recorrente se apareceu em pelo menos 2 dos 3 meses distintos.
    Retorna a soma dos valores médios pendentes.

    Args:
        modelo: classe do model (Receita ou Despesa).
        user: usuário autenticado.
        mes: mês de referência.
        ano: ano de referência.
    """
    meses_ant = _meses_anteriores(mes, ano)

    # Buscar lançamentos fixos dos últimos 3 meses em UMA ÚNICA query
    data_inicio = date(meses_ant[-1][0], meses_ant[-1][1], 1)
    data_fim = ultimo_dia_do_mes(meses_ant[0][0], meses_ant[0][1])

    lancamentos = modelo.objects.filter(
        user=user,
        natureza='fixa',
        data__gte=data_inicio,
        data__lte=data_fim,
    ).values_list('descricao', 'categoria_id', 'valor', 'data')

    # Agrupar por chave (descricao, categoria_id)
    por_chave: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for descricao, categoria_id, valor, data_lanc in lancamentos:
        chave = (descricao, categoria_id)
        mes_lanc = (data_lanc.year, data_lanc.month)
        por_chave[chave].append({'valor': valor, 'mes': mes_lanc})

    # Identificar recorrentes (presentes em >= 2 meses distintos)
    recorrentes: dict[tuple[str, int], Decimal] = {}
    for chave, items in por_chave.items():
        meses_distintos = {item['mes'] for item in items}
        if len(meses_distintos) >= 2:
            total = sum(item['valor'] for item in items)
            media = total / len(items)
            recorrentes[chave] = media

    if not recorrentes:
        return Decimal('0')

    # Verificar quais NÃO possuem lançamento no mês/ano informado (batch)
    primeiro_dia_atual = date(ano, mes, 1)
    ultimo_dia_atual = ultimo_dia_do_mes(ano, mes)

    existentes_no_mes = set(
        modelo.objects.filter(
            user=user,
            data__gte=primeiro_dia_atual,
            data__lte=ultimo_dia_atual,
        ).values_list('descricao', 'categoria_id')
    )

    total_pendente = Decimal('0')
    for chave, valor_medio in recorrentes.items():
        if chave not in existentes_no_mes:
            total_pendente += valor_medio

    return total_pendente


def identificar_despesas_fixas_pendentes(user: User, mes: int, ano: int) -> Decimal:
    """Identifica despesas fixas recorrentes pendentes no mês informado."""
    return _identificar_lancamentos_fixos_pendentes(Despesa, user, mes, ano)


def identificar_receitas_previstas_pendentes(user: User, mes: int, ano: int) -> Decimal:
    """Identifica receitas fixas recorrentes pendentes no mês informado."""
    return _identificar_lancamentos_fixos_pendentes(Receita, user, mes, ano)


def calcular_media_diaria_gastos_variaveis(user: User) -> Decimal:
    """
    Calcula a média diária de gastos variáveis dos últimos 90 dias.

    Retorna Decimal('0') se houver menos de 5 lançamentos no período.
    """
    hoje = date.today()
    data_inicio = hoje - timedelta(days=90)

    despesas = Despesa.objects.filter(
        user=user,
        natureza='variavel',
        data__gte=data_inicio,
        data__lte=hoje,
    )

    if despesas.count() < 5:
        return Decimal('0')

    total = despesas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    return total / Decimal('90')


def calcular_previsao_saldo(
    user: User,
    mes: int | None = None,
    ano: int | None = None,
) -> dict:
    """
    Calcula a previsão de saldo até o final do mês.

    Considera despesas fixas pendentes, gastos variáveis projetados
    e receitas previstas para estimar o saldo ao fim do mês.
    """
    hoje = date.today()
    if mes is None:
        mes = hoje.month
    if ano is None:
        ano = hoje.year

    primeiro_dia_mes = date(ano, mes, 1)
    ultimo_dia_mes = ultimo_dia_do_mes(ano, mes)

    # Calcular data de referência e dias restantes conforme o período
    if ano == hoje.year and mes == hoje.month:
        data_referencia = hoje
        dias_restantes = max(0, (ultimo_dia_mes - hoje).days)
    elif date(ano, mes, 1) > hoje:
        data_referencia = primeiro_dia_mes
        dias_restantes = (ultimo_dia_mes - primeiro_dia_mes).days
    else:
        data_referencia = ultimo_dia_mes
        dias_restantes = 0

    # Verificar se há dados suficientes (lançamentos nos últimos 3 meses)
    data_3_meses_atras = hoje - timedelta(days=90)
    tem_receitas = Receita.objects.filter(
        user=user, data__gte=data_3_meses_atras,
    ).exists()
    tem_despesas = Despesa.objects.filter(
        user=user, data__gte=data_3_meses_atras,
    ).exists()
    dados_suficientes = tem_receitas or tem_despesas

    # Saldo atual do mês
    saldo_periodo = calcular_saldo_por_periodo(user, primeiro_dia_mes, data_referencia)
    saldo_atual = saldo_periodo['saldo']

    # Despesas fixas pendentes
    despesas_fixas_pendentes = identificar_despesas_fixas_pendentes(user, mes, ano)

    # Gastos variáveis projetados
    media_diaria = calcular_media_diaria_gastos_variaveis(user)
    gastos_variaveis_projetados = media_diaria * Decimal(str(dias_restantes))

    # Receitas previstas pendentes
    receitas_previstas = identificar_receitas_previstas_pendentes(user, mes, ano)

    # Saldo projetado
    saldo_projetado = (
        saldo_atual
        - despesas_fixas_pendentes
        - gastos_variaveis_projetados
        + receitas_previstas
    )

    return {
        'saldo_atual': saldo_atual,
        'despesas_fixas_pendentes': despesas_fixas_pendentes,
        'gastos_variaveis_projetados': gastos_variaveis_projetados,
        'receitas_previstas': receitas_previstas,
        'saldo_projetado': saldo_projetado,
        'dias_restantes': dias_restantes,
        'negativo': saldo_projetado < 0,
        'dados_suficientes': dados_suficientes,
    }


# ─── Alertas Inteligentes ───────────────────────────────────────────────────


def verificar_alerta_orcamento(user: User, mes: int, ano: int, config=None) -> dict:
    """
    Verifica se o gasto do mês atingiu o limiar do orçamento.

    Retorna dict com status do alerta, percentual consumido e mensagem.
    """
    if config is None:
        config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)
    if not config.alerta_orcamento_ativo:
        return {'ativo': False}

    try:
        orcamento = Orcamento.objects.get(user=user, mes=mes, ano=ano)
    except Orcamento.DoesNotExist:
        return {'ativo': False, 'sem_orcamento': True}

    # Total de despesas no mês
    primeiro_dia = date(ano, mes, 1)
    ult_dia = ultimo_dia_do_mes(ano, mes)
    total_despesas = (
        Despesa.objects.filter(user=user, data__gte=primeiro_dia, data__lte=ult_dia)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )

    percentual = (total_despesas / orcamento.valor * 100) if orcamento.valor > 0 else Decimal('0')

    if percentual >= config.limiar_orcamento:
        return {
            'ativo': True,
            'tipo': 'orcamento',
            'icone': '🔔',
            'percentual': round(percentual, 1),
            'limiar': config.limiar_orcamento,
            'total_despesas': total_despesas,
            'valor_orcamento': orcamento.valor,
            'mensagem': f'Você já consumiu {round(percentual, 1)}% do seu orçamento de {NOMES_MESES.get(mes, "")}.',
            'nivel': 'critico' if percentual >= 100 else 'aviso',
        }
    return {'ativo': False, 'percentual': round(percentual, 1)}


def verificar_alerta_gasto_acelerado(user: User, config=None) -> dict:
    """
    Verifica se o ritmo de gastos na semana atual está acima da média histórica.

    Compara gasto semanal atual com a média das últimas 12 semanas.
    """
    if config is None:
        config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)
    if not config.alerta_gasto_acelerado_ativo:
        return {'ativo': False}

    hoje = date.today()
    # Início da semana atual (segunda-feira)
    inicio_semana = hoje - timedelta(days=hoje.weekday())

    # Gasto da semana atual
    gasto_semana = (
        Despesa.objects.filter(user=user, data__gte=inicio_semana, data__lte=hoje)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )

    # Média semanal das últimas 12 semanas (excluindo semana atual)
    data_12_semanas = inicio_semana - timedelta(weeks=12)
    total_historico = (
        Despesa.objects.filter(user=user, data__gte=data_12_semanas, data__lt=inicio_semana)
        .aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )

    # Se não há histórico suficiente
    if total_historico == 0:
        return {'ativo': False, 'dados_insuficientes': True}

    media_semanal = total_historico / Decimal('12')

    # Proporção do gasto atual vs dias decorridos na semana
    dias_na_semana = (hoje - inicio_semana).days + 1
    gasto_projetado_semana = gasto_semana / Decimal(str(dias_na_semana)) * Decimal('7')

    # Se gasto projetado > 120% da média → alerta
    if gasto_projetado_semana > media_semanal * Decimal('1.2'):
        return {
            'ativo': True,
            'tipo': 'gasto_acelerado',
            'icone': '⚡',
            'gasto_semana': gasto_semana,
            'media_semanal': round(media_semanal, 2),
            'mensagem': 'Você está gastando mais rápido do que o normal esta semana.',
            'nivel': 'aviso',
        }
    return {'ativo': False, 'gasto_semana': gasto_semana, 'media_semanal': round(media_semanal, 2)}


def verificar_alerta_saldo_baixo(user: User, mes: int, ano: int, config=None, previsao=None) -> dict:
    """
    Verifica se o saldo projetado ao fim do mês está abaixo do limite definido.

    Reutiliza calcular_previsao_saldo do Módulo 2.
    """
    if config is None:
        config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)
    if not config.alerta_saldo_baixo_ativo:
        return {'ativo': False}

    if previsao is None:
        previsao = calcular_previsao_saldo(user, mes, ano)

    if not previsao['dados_suficientes']:
        return {'ativo': False, 'dados_insuficientes': True}

    if previsao['saldo_projetado'] < config.limite_saldo_minimo:
        return {
            'ativo': True,
            'tipo': 'saldo_baixo',
            'icone': '⚠️',
            'saldo_projetado': previsao['saldo_projetado'],
            'limite': config.limite_saldo_minimo,
            'mensagem': f'Seu saldo projetado (R$ {previsao["saldo_projetado"]:.2f}) está abaixo do limite de R$ {config.limite_saldo_minimo:.2f}.',
            'nivel': 'critico' if previsao['negativo'] else 'aviso',
        }
    return {'ativo': False, 'saldo_projetado': previsao['saldo_projetado']}


def obter_todos_alertas(user: User, previsao=None) -> list[dict]:
    """
    Agrupa todos os alertas ativos do usuário em uma lista unificada.

    Retorna lista de dicts prontos para o template.
    """
    hoje = date.today()
    alertas: list[dict] = []

    config, _ = ConfiguracaoAlerta.objects.get_or_create(user=user)

    alerta_orc = verificar_alerta_orcamento(user, hoje.month, hoje.year, config=config)
    if alerta_orc.get('ativo'):
        alertas.append(alerta_orc)

    alerta_gasto = verificar_alerta_gasto_acelerado(user, config=config)
    if alerta_gasto.get('ativo'):
        alertas.append(alerta_gasto)

    alerta_saldo = verificar_alerta_saldo_baixo(
        user, hoje.month, hoje.year, config=config, previsao=previsao,
    )
    if alerta_saldo.get('ativo'):
        alertas.append(alerta_saldo)

    # Ordenar: críticos primeiro, depois avisos
    alertas.sort(key=lambda a: 0 if a.get('nivel') == 'critico' else 1)

    return alertas


# ─── Detecção de Padrões (Heat Zone) ────────────────────────────────────────

CORES_HEATMAP = {
    0: 'bg-gray-100',
    1: 'bg-green-200',
    2: 'bg-yellow-200',
    3: 'bg-orange-300',
    4: 'bg-red-400',
}

NOMES_DIAS = {
    2: 'segunda',
    3: 'terça',
    4: 'quarta',
    5: 'quinta',
    6: 'sexta',
    7: 'sábado',
    1: 'domingo',
}


def gerar_dados_heatmap(user: User, mes: int, ano: int) -> dict[int, dict]:
    """Gera dados do heatmap de despesas por dia do mês."""
    despesas_por_dia = (
        Despesa.objects.filter(user=user, data__year=ano, data__month=mes)
        .values('data')
        .annotate(total=Sum('valor'))
    )

    totais_por_dia: dict[int, Decimal] = {}
    for item in despesas_por_dia:
        totais_por_dia[item['data'].day] = item['total']

    # Calcular quartis para níveis de intensidade
    valores = [v for v in totais_por_dia.values() if v > 0]

    if len(valores) >= 4:
        quartis = statistics.quantiles(valores, n=4)
        q1, q2, q3 = quartis[0], quartis[1], quartis[2]
    elif valores:
        # Abordagem simples: dividir em faixas iguais
        minimo = min(valores)
        maximo = max(valores)
        faixa = (maximo - minimo) / Decimal('3') if maximo > minimo else Decimal('1')
        q1 = minimo + faixa
        q2 = minimo + faixa * 2
        q3 = minimo + faixa * 3
    else:
        q1 = q2 = q3 = Decimal('0')

    def _nivel(total: Decimal) -> int:
        if total <= 0:
            return 0
        if total <= q1:
            return 1
        if total <= q2:
            return 2
        if total <= q3:
            return 3
        return 4

    _, ultimo = calendar.monthrange(ano, mes)
    dados: dict[int, dict] = {}
    for dia in range(1, ultimo + 1):
        total = totais_por_dia.get(dia, Decimal('0'))
        nivel = _nivel(total)
        dados[dia] = {
            'total': total,
            'nivel': nivel,
            'cor': CORES_HEATMAP[nivel],
        }

    return dados


def obter_detalhes_dia(user: User, data: date) -> dict:
    """Busca despesas e receitas de um dia específico."""
    despesas = Despesa.objects.filter(user=user, data=data).select_related('categoria')
    receitas = Receita.objects.filter(user=user, data=data).select_related('categoria')

    lista_despesas = [
        {'descricao': d.descricao, 'valor': d.valor, 'categoria': d.categoria.nome}
        for d in despesas
    ]
    lista_receitas = [
        {'descricao': r.descricao, 'valor': r.valor, 'categoria': r.categoria.nome}
        for r in receitas
    ]

    total_despesas = sum(d['valor'] for d in lista_despesas) if lista_despesas else Decimal('0')
    total_receitas = sum(r['valor'] for r in lista_receitas) if lista_receitas else Decimal('0')

    return {
        'despesas': lista_despesas,
        'receitas': lista_receitas,
        'total_despesas': total_despesas,
        'total_receitas': total_receitas,
    }


def analisar_padrao_dia_semana(user: User, meses: int = 3) -> dict:
    """Analisa padrão de gastos por dia da semana nos últimos meses."""
    hoje = date.today()
    data_inicio = hoje - timedelta(days=meses * 30)

    despesas = Despesa.objects.filter(
        user=user, data__gte=data_inicio, data__lte=hoje,
    )

    if despesas.count() < 5:
        return {'dados_suficientes': False, 'mensagem': 'Dados insuficientes para análise.'}

    # Agrupar por dia da semana (Django: 1=dom, 2=seg, ..., 7=sáb)
    por_dia_semana = (
        despesas.values('data__week_day')
        .annotate(total=Sum('valor'))
    )

    media_por_dia: dict[str, Decimal] = {}
    for item in por_dia_semana:
        dia_num = item['data__week_day']
        nome = NOMES_DIAS.get(dia_num, str(dia_num))
        media_por_dia[nome] = item['total'] / Decimal(str(meses))

    if not media_por_dia:
        return {'dados_suficientes': False, 'mensagem': 'Dados insuficientes para análise.'}

    dia_maior_gasto = max(media_por_dia, key=media_por_dia.get)
    media_geral = sum(media_por_dia.values()) / Decimal(str(len(media_por_dia)))
    percentual_acima = int(
        ((media_por_dia[dia_maior_gasto] - media_geral) / media_geral * 100)
        if media_geral > 0 else 0
    )

    return {
        'dia_maior_gasto': dia_maior_gasto,
        'percentual_acima': percentual_acima,
        'media_por_dia': media_por_dia,
        'mensagem': f'Você gasta mais às {dia_maior_gasto}s — {percentual_acima}% acima da média.',
        'dados_suficientes': True,
    }


def analisar_padrao_categoria(user: User, mes: int, ano: int) -> dict:
    """Analisa qual categoria domina os gastos no mês."""
    data_inicio = date(ano, mes, 1)
    data_fim = ultimo_dia_do_mes(ano, mes)

    resumo = resumo_por_categoria(user, 'despesa', data_inicio=data_inicio, data_fim=data_fim)

    if not resumo:
        return {'dados_suficientes': False, 'mensagem': 'Sem despesas no período.'}

    total = sum(item['total'] for item in resumo)
    categorias = []
    for item in resumo:
        percentual = int(item['total'] / total * 100) if total > 0 else 0
        categorias.append({
            'nome': item['categoria__nome'],
            'total': item['total'],
            'percentual': percentual,
        })

    categoria_dominante = categorias[0]['nome']
    percentual_dominante = categorias[0]['percentual']

    return {
        'categoria_dominante': categoria_dominante,
        'percentual': percentual_dominante,
        'categorias': categorias,
        'mensagem': f'{categoria_dominante} representa {percentual_dominante}% dos seus gastos.',
        'dados_suficientes': True,
    }


def analisar_padrao_mensal(user: User, meses: int = 3) -> dict:
    """Compara gastos do mês atual com o mês anterior."""
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # Mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual

    primeiro_dia_atual = date(ano_atual, mes_atual, 1)
    ultimo_dia_atual = ultimo_dia_do_mes(ano_atual, mes_atual)
    primeiro_dia_anterior = date(ano_anterior, mes_anterior, 1)
    ultimo_dia_anterior = ultimo_dia_do_mes(ano_anterior, mes_anterior)

    total_atual = (
        Despesa.objects.filter(
            user=user, data__gte=primeiro_dia_atual, data__lte=ultimo_dia_atual,
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )

    total_anterior = (
        Despesa.objects.filter(
            user=user, data__gte=primeiro_dia_anterior, data__lte=ultimo_dia_anterior,
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    )

    if total_anterior == 0:
        return {'dados_suficientes': False, 'mensagem': 'Sem dados do mês anterior para comparação.'}

    variacao = int((total_atual - total_anterior) / total_anterior * 100)
    direcao = 'aumento' if variacao >= 0 else 'redução'

    nome_atual = NOMES_MESES.get(mes_atual, '')
    nome_anterior = NOMES_MESES.get(mes_anterior, '')

    return {
        'variacao': abs(variacao),
        'direcao': direcao,
        'mes_atual': nome_atual,
        'mes_anterior': nome_anterior,
        'mensagem': f'{direcao.capitalize()} de {abs(variacao)}% em relação a {nome_anterior}.',
        'dados_suficientes': True,
    }


def obter_todos_insights(user: User, mes: int, ano: int) -> list[dict]:
    """Agrega todos os insights de padrões para o usuário."""
    insights: list[dict] = []

    analise_dia = analisar_padrao_dia_semana(user)
    if analise_dia.get('dados_suficientes'):
        insights.append({
            'tipo': 'dia_semana',
            'icone': '📅',
            'mensagem': analise_dia['mensagem'],
            'dados': analise_dia,
        })

    analise_cat = analisar_padrao_categoria(user, mes, ano)
    if analise_cat.get('dados_suficientes'):
        insights.append({
            'tipo': 'categoria',
            'icone': '📊',
            'mensagem': analise_cat['mensagem'],
            'dados': analise_cat,
        })

    analise_mensal = analisar_padrao_mensal(user)
    if analise_mensal.get('dados_suficientes'):
        insights.append({
            'tipo': 'mensal',
            'icone': '📈',
            'mensagem': analise_mensal['mensagem'],
            'dados': analise_mensal,
        })

    return insights


# ─── Balança de Receitas × Despesas por Dia ─────────────────────────────────


def gerar_dados_balanca_diaria(user: User, mes: int, ano: int) -> dict[int, dict]:
    """Gera dados de receitas vs despesas para cada dia do mês."""
    # Queries eficientes com agregação por data
    receitas_por_dia = {
        item['data'].day: item['total']
        for item in Receita.objects.filter(
            user=user, data__year=ano, data__month=mes,
        ).values('data').annotate(total=Sum('valor'))
    }

    despesas_por_dia = {
        item['data'].day: item['total']
        for item in Despesa.objects.filter(
            user=user, data__year=ano, data__month=mes,
        ).values('data').annotate(total=Sum('valor'))
    }

    _, ultimo_dia = calendar.monthrange(ano, mes)
    dados: dict[int, dict] = {}

    for dia in range(1, ultimo_dia + 1):
        receitas = receitas_por_dia.get(dia, Decimal('0'))
        despesas = despesas_por_dia.get(dia, Decimal('0'))
        total = receitas + despesas
        tem_dados = total > 0

        if tem_dados:
            percentual_receita = round(float(receitas / total * 100), 1)
            percentual_despesa = round(100 - percentual_receita, 1)
        else:
            percentual_receita = 0
            percentual_despesa = 0

        dados[dia] = {
            'receitas': receitas,
            'despesas': despesas,
            'total': total,
            'percentual_receita': percentual_receita,
            'percentual_despesa': percentual_despesa,
            'tem_dados': tem_dados,
        }

    return dados


def obter_resumo_balanca_mensal(user: User, mes: int, ano: int, dados_diarios: dict | None = None) -> dict:
    """Calcula resumo mensal da balança receitas vs despesas."""
    if dados_diarios is None:
        dados_diarios = gerar_dados_balanca_diaria(user, mes, ano)

    total_receitas = sum(
        (dia_info['receitas'] for dia_info in dados_diarios.values()), Decimal('0'),
    )
    total_despesas = sum(
        (dia_info['despesas'] for dia_info in dados_diarios.values()), Decimal('0'),
    )
    saldo = total_receitas - total_despesas

    dias_verdes = 0
    dias_vermelhos = 0
    dias_equilibrados = 0

    for dia_info in dados_diarios.values():
        if not dia_info['tem_dados']:
            continue
        if dia_info['receitas'] > dia_info['despesas']:
            dias_verdes += 1
        elif dia_info['despesas'] > dia_info['receitas']:
            dias_vermelhos += 1
        elif dia_info['receitas'] == dia_info['despesas'] and dia_info['receitas'] > 0:
            dias_equilibrados += 1

    return {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': saldo,
        'dias_verdes': dias_verdes,
        'dias_vermelhos': dias_vermelhos,
        'dias_equilibrados': dias_equilibrados,
        'positivo': saldo >= 0,
    }
