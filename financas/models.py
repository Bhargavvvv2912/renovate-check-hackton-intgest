from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class BaseModel(models.Model):
    """Modelo base abstrato com campos comuns a todas as entidades de negócio."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Categoria(BaseModel):
    """Categoria de lançamento financeiro, vinculada a um tipo (receita ou despesa)."""

    class TipoCategoria(models.TextChoices):
        RECEITA = 'receita', 'Receita'
        DESPESA = 'despesa', 'Despesa'

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=7, choices=TipoCategoria.choices)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'nome', 'tipo'],
                name='categoria_unica_por_usuario',
            )
        ]

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_tipo_display()})"


class Receita(BaseModel):
    """Lançamento de receita do usuário."""

    class Origem(models.TextChoices):
        SALARIO = 'salario', 'Salário'
        FREELANCE = 'freelance', 'Freelance'
        INVESTIMENTO = 'investimento', 'Investimento'
        OUTROS = 'outros', 'Outros'

    class Natureza(models.TextChoices):
        FIXA = 'fixa', 'Fixa'
        VARIAVEL = 'variavel', 'Variável'
        EVENTUAL = 'eventual', 'Eventual'

    descricao = models.CharField('Descrição', max_length=255)
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='O valor deve ser maior que zero.')],
    )
    data = models.DateField('Data')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='receitas',
    )
    origem = models.CharField(max_length=15, choices=Origem.choices, default=Origem.OUTROS)
    natureza = models.CharField(max_length=10, choices=Natureza.choices, default=Natureza.VARIAVEL)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'

    def __str__(self) -> str:
        return f"{self.descricao} - R$ {self.valor}"


class Despesa(BaseModel):
    """Lançamento de despesa do usuário."""

    class Origem(models.TextChoices):
        ALIMENTACAO = 'alimentacao', 'Alimentação'
        TRANSPORTE = 'transporte', 'Transporte'
        MORADIA = 'moradia', 'Moradia'
        LAZER = 'lazer', 'Lazer'
        EDUCACAO = 'educacao', 'Educação'
        SAUDE = 'saude', 'Saúde'
        OUTROS = 'outros', 'Outros'

    class Natureza(models.TextChoices):
        FIXA = 'fixa', 'Fixa'
        VARIAVEL = 'variavel', 'Variável'
        EVENTUAL = 'eventual', 'Eventual'

    descricao = models.CharField('Descrição', max_length=255)
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='O valor deve ser maior que zero.')],
    )
    data = models.DateField('Data')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='despesas',
    )
    origem = models.CharField(max_length=15, choices=Origem.choices, default=Origem.OUTROS)
    natureza = models.CharField(max_length=10, choices=Natureza.choices, default=Natureza.VARIAVEL)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'

    def __str__(self) -> str:
        return f"{self.descricao} - R$ {self.valor}"


class Orcamento(BaseModel):
    """Orçamento mensal definido pelo usuário."""
    mes = models.PositiveIntegerField(
        'Mês',
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    ano = models.PositiveIntegerField(
        'Ano',
        validators=[MinValueValidator(2020), MaxValueValidator(2100)],
    )
    valor = models.DecimalField(
        'Valor',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='O valor deve ser maior que zero.')],
    )

    class Meta:
        ordering = ['-ano', '-mes']
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'mes', 'ano'],
                name='orcamento_unico_por_usuario_mes',
            )
        ]

    def __str__(self) -> str:
        return f"Orçamento {self.mes:02d}/{self.ano} - R$ {self.valor}"


class ConfiguracaoAlerta(BaseModel):
    """Configurações de alertas financeiros do usuário."""
    alerta_orcamento_ativo = models.BooleanField('Alerta de orçamento', default=True)
    limiar_orcamento = models.PositiveIntegerField(
        'Limiar de orçamento (%)', default=80,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    alerta_gasto_acelerado_ativo = models.BooleanField('Alerta de gasto acelerado', default=True)
    alerta_saldo_baixo_ativo = models.BooleanField('Alerta de saldo baixo', default=True)
    limite_saldo_minimo = models.DecimalField(
        'Limite de saldo mínimo',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )

    class Meta:
        verbose_name = 'Configuração de Alerta'
        verbose_name_plural = 'Configurações de Alerta'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='config_alerta_unica_por_usuario',
            )
        ]

    def __str__(self) -> str:
        return f"Alertas de {self.user.username}"
