"""
Management command para popular o banco com dados de demonstração.

Uso:
    python manage.py popular_dados
    python manage.py popular_dados --usuario demo
    python manage.py popular_dados --limpar
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from financas.models import Categoria, ConfiguracaoAlerta, Despesa, Orcamento, Receita


CATEGORIAS_RECEITA = [
    'Salário',
    'Freelance',
    'Investimentos',
    'Aluguel Recebido',
    'Vendas Online',
    'Restituição IR',
    'Outros',
]

CATEGORIAS_DESPESA = [
    'Alimentação',
    'Transporte',
    'Moradia',
    'Saúde',
    'Educação',
    'Lazer',
    'Roupas',
    'Conta de Luz',
    'Conta de Água',
    'Internet',
    'Plano de Saúde',
    'Outros',
]

RECEITAS_FIXAS = [
    ('Salário Mensal', Decimal('6500.00'), 'salario', 'fixa', 'Salário'),
    ('Renda de Aluguel', Decimal('1200.00'), 'outros', 'fixa', 'Aluguel Recebido'),
]

RECEITAS_VARIAVEIS = [
    ('Freelance Web Design', Decimal('800.00'), 'freelance', 'variavel', 'Freelance'),
    ('Dividendos', Decimal('350.00'), 'investimento', 'variavel', 'Investimentos'),
    ('Venda de Cursos', Decimal('450.00'), 'outros', 'variavel', 'Vendas Online'),
    ('Consultoria', Decimal('1500.00'), 'freelance', 'eventual', 'Freelance'),
    ('Restituição IR', Decimal('2300.00'), 'outros', 'eventual', 'Restituição IR'),
    ('Bonus Semestral', Decimal('3000.00'), 'salario', 'eventual', 'Salário'),
]

DESPESAS_FIXAS = [
    ('Aluguel', Decimal('1800.00'), 'moradia', 'fixa', 'Moradia'),
    ('Plano de Saúde', Decimal('420.00'), 'saude', 'fixa', 'Plano de Saúde'),
    ('Internet Fibra', Decimal('99.90'), 'outros', 'fixa', 'Internet'),
    ('Conta de Água', Decimal('65.00'), 'outros', 'fixa', 'Conta de Água'),
    ('Conta de Luz', Decimal('180.00'), 'outros', 'fixa', 'Conta de Luz'),
    ('Mensalidade Academia', Decimal('89.90'), 'saude', 'fixa', 'Saúde'),
    ('Escola Filhos', Decimal('650.00'), 'educacao', 'fixa', 'Educação'),
    ('Streaming (Netflix+Spotify)', Decimal('59.90'), 'lazer', 'fixa', 'Lazer'),
    ('Seguro do Carro', Decimal('220.00'), 'transporte', 'fixa', 'Transporte'),
]

DESPESAS_VARIAVEIS = [
    ('Supermercado', Decimal('750.00'), 'alimentacao', 'variavel', 'Alimentação'),
    ('Combustível', Decimal('280.00'), 'transporte', 'variavel', 'Transporte'),
    ('Restaurantes', Decimal('320.00'), 'alimentacao', 'variavel', 'Alimentação'),
    ('Farmácia', Decimal('85.00'), 'saude', 'variavel', 'Saúde'),
    ('Estacionamento', Decimal('45.00'), 'transporte', 'variavel', 'Transporte'),
    ('Roupas e Calçados', Decimal('190.00'), 'outros', 'variavel', 'Roupas'),
    ('Lazer e Entretenimento', Decimal('250.00'), 'lazer', 'variavel', 'Lazer'),
    ('Material Escolar', Decimal('120.00'), 'educacao', 'variavel', 'Educação'),
]

DESPESAS_EVENTUAIS = [
    ('Consulta Médica Especialista', Decimal('350.00'), 'saude', 'eventual', 'Saúde'),
    ('Manutenção Carro', Decimal('480.00'), 'transporte', 'eventual', 'Transporte'),
    ('Viagem de Férias', Decimal('2500.00'), 'lazer', 'eventual', 'Lazer'),
    ('Reforma Banheiro', Decimal('3200.00'), 'moradia', 'eventual', 'Moradia'),
    ('Curso Online', Decimal('299.00'), 'educacao', 'eventual', 'Educação'),
    ('Presente Aniversário', Decimal('150.00'), 'outros', 'eventual', 'Outros'),
    ('Multa de Trânsito', Decimal('330.00'), 'transporte', 'eventual', 'Transporte'),
    ('Conserto Eletrodoméstico', Decimal('210.00'), 'moradia', 'eventual', 'Moradia'),
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de demonstração para 2025 e 2026.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            default='demo',
            help='Username do usuário demo (padrão: demo)',
        )
        parser.add_argument(
            '--senha',
            type=str,
            default='demo@1234',
            help='Senha do usuário demo (padrão: demo@1234)',
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove todos os dados do usuário antes de popular',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['usuario']
        senha = options['senha']

        # Criar ou recuperar usuário demo
        usuario, criado = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@demo.com',
                'first_name': 'Usuário',
                'last_name': 'Demo',
                'is_active': True,
            },
        )
        if criado:
            usuario.set_password(senha)
            usuario.save()
            self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado com senha "{senha}"'))
        else:
            self.stdout.write(f'Usando usuário existente "{username}"')

        if options['limpar']:
            self._limpar_dados(usuario)

        # Criar categorias
        cats_receita = self._criar_categorias(usuario, CATEGORIAS_RECEITA, 'receita')
        cats_despesa = self._criar_categorias(usuario, CATEGORIAS_DESPESA, 'despesa')
        self.stdout.write(f'  {len(cats_receita)} categorias de receita, {len(cats_despesa)} de despesa criadas.')

        # Criar lançamentos para 2025 (jan a dez) e 2026 (jan a mar)
        total_receitas = 0
        total_despesas = 0
        total_orcamentos = 0

        for ano in [2025, 2026]:
            meses = range(1, 13) if ano == 2025 else range(1, 4)  # 2026 até março
            for mes in meses:
                r, d = self._popular_mes(usuario, ano, mes, cats_receita, cats_despesa)
                total_receitas += r
                total_despesas += d
                orcamento_valor = Decimal('5000.00') + Decimal(random.randint(-200, 500))
                Orcamento.objects.get_or_create(
                    user=usuario,
                    mes=mes,
                    ano=ano,
                    defaults={'valor': orcamento_valor},
                )
                total_orcamentos += 1

        # Configuração de alertas
        ConfiguracaoAlerta.objects.get_or_create(
            user=usuario,
            defaults={
                'alerta_orcamento_ativo': True,
                'limiar_orcamento': 80,
                'alerta_gasto_acelerado_ativo': True,
                'alerta_saldo_baixo_ativo': True,
                'limite_saldo_minimo': Decimal('500.00'),
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f'\nDados de demonstração populados com sucesso!'
            f'\n  Receitas: {total_receitas}'
            f'\n  Despesas: {total_despesas}'
            f'\n  Orçamentos: {total_orcamentos}'
            f'\n\nAcesse com: username="{username}" / senha="{senha}"'
        ))

    def _limpar_dados(self, usuario: User) -> None:
        """Remove todos os dados financeiros do usuário."""
        Receita.objects.filter(user=usuario).delete()
        Despesa.objects.filter(user=usuario).delete()
        Orcamento.objects.filter(user=usuario).delete()
        Categoria.objects.filter(user=usuario).delete()
        ConfiguracaoAlerta.objects.filter(user=usuario).delete()
        self.stdout.write(self.style.WARNING(f'Dados do usuário "{usuario.username}" removidos.'))

    def _criar_categorias(self, usuario: User, nomes: list[str], tipo: str) -> dict[str, Categoria]:
        """Cria categorias e retorna dicionário nome → instância."""
        resultado = {}
        for nome in nomes:
            cat, _ = Categoria.objects.get_or_create(
                user=usuario,
                nome=nome,
                tipo=tipo,
            )
            resultado[nome] = cat
        return resultado

    def _dia_aleatorio(self, ano: int, mes: int) -> date:
        """Retorna uma data aleatória no mês."""
        import calendar
        _, ultimo_dia = calendar.monthrange(ano, mes)
        return date(ano, mes, random.randint(1, ultimo_dia))

    def _popular_mes(
        self,
        usuario: User,
        ano: int,
        mes: int,
        cats_receita: dict,
        cats_despesa: dict,
    ) -> tuple[int, int]:
        """Cria receitas e despesas para um mês específico."""
        total_r = 0
        total_d = 0

        # Receitas fixas (sempre existem)
        for descricao, valor_base, origem, natureza, cat_nome in RECEITAS_FIXAS:
            variacao = Decimal(str(round(random.uniform(-0.02, 0.02), 4)))
            valor = (valor_base * (1 + variacao)).quantize(Decimal('0.01'))
            Receita.objects.get_or_create(
                user=usuario,
                descricao=descricao,
                data=date(ano, mes, 5),
                defaults={
                    'valor': valor,
                    'categoria': cats_receita.get(cat_nome, next(iter(cats_receita.values()))),
                    'origem': origem,
                    'natureza': natureza,
                },
            )
            total_r += 1

        # Receitas variáveis (probabilidade de ocorrer)
        for descricao, valor_base, origem, natureza, cat_nome in RECEITAS_VARIAVEIS:
            if natureza == 'eventual' and random.random() > 0.25:
                continue
            if natureza == 'variavel' and random.random() > 0.6:
                continue
            variacao = Decimal(str(round(random.uniform(-0.15, 0.20), 4)))
            valor = (valor_base * (1 + variacao)).quantize(Decimal('0.01'))
            if valor < Decimal('0.01'):
                valor = Decimal('0.01')
            Receita.objects.get_or_create(
                user=usuario,
                descricao=f'{descricao} {mes:02d}/{ano}',
                data=self._dia_aleatorio(ano, mes),
                defaults={
                    'valor': valor,
                    'categoria': cats_receita.get(cat_nome, next(iter(cats_receita.values()))),
                    'origem': origem,
                    'natureza': natureza,
                },
            )
            total_r += 1

        # Despesas fixas
        for descricao, valor_base, origem, natureza, cat_nome in DESPESAS_FIXAS:
            variacao = Decimal(str(round(random.uniform(-0.01, 0.05), 4)))
            valor = (valor_base * (1 + variacao)).quantize(Decimal('0.01'))
            if valor < Decimal('0.01'):
                valor = Decimal('0.01')
            dia = random.randint(1, 10)
            Despesa.objects.get_or_create(
                user=usuario,
                descricao=descricao,
                data=date(ano, mes, dia),
                defaults={
                    'valor': valor,
                    'categoria': cats_despesa.get(cat_nome, next(iter(cats_despesa.values()))),
                    'origem': origem,
                    'natureza': natureza,
                },
            )
            total_d += 1

        # Despesas variáveis
        for descricao, valor_base, origem, natureza, cat_nome in DESPESAS_VARIAVEIS:
            qtd = random.randint(1, 3)
            for i in range(qtd):
                variacao = Decimal(str(round(random.uniform(-0.20, 0.30), 4)))
                valor = (valor_base * (1 + variacao)).quantize(Decimal('0.01'))
                if valor < Decimal('0.01'):
                    valor = Decimal('0.01')
                Despesa.objects.get_or_create(
                    user=usuario,
                    descricao=f'{descricao} ({i + 1})',
                    data=self._dia_aleatorio(ano, mes),
                    defaults={
                        'valor': valor,
                        'categoria': cats_despesa.get(cat_nome, next(iter(cats_despesa.values()))),
                        'origem': origem,
                        'natureza': natureza,
                    },
                )
                total_d += 1

        # Despesas eventuais (baixa frequência)
        for descricao, valor_base, origem, natureza, cat_nome in DESPESAS_EVENTUAIS:
            if random.random() > 0.20:
                continue
            variacao = Decimal(str(round(random.uniform(-0.10, 0.25), 4)))
            valor = (valor_base * (1 + variacao)).quantize(Decimal('0.01'))
            if valor < Decimal('0.01'):
                valor = Decimal('0.01')
            Despesa.objects.get_or_create(
                user=usuario,
                descricao=f'{descricao} {mes:02d}/{ano}',
                data=self._dia_aleatorio(ano, mes),
                defaults={
                    'valor': valor,
                    'categoria': cats_despesa.get(cat_nome, next(iter(cats_despesa.values()))),
                    'origem': origem,
                    'natureza': natureza,
                },
            )
            total_d += 1

        return total_r, total_d
