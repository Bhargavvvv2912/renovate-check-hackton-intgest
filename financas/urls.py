from django.urls import path

from financas import views

app_name = 'financas'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Receitas
    path('receitas/', views.ReceitaListView.as_view(), name='receita_lista'),
    path('receitas/nova/', views.ReceitaCreateView.as_view(), name='receita_criar'),
    path('receitas/<int:pk>/editar/', views.ReceitaUpdateView.as_view(), name='receita_editar'),
    path('receitas/<int:pk>/excluir/', views.ReceitaDeleteView.as_view(), name='receita_excluir'),

    # Despesas
    path('despesas/', views.DespesaListView.as_view(), name='despesa_lista'),
    path('despesas/nova/', views.DespesaCreateView.as_view(), name='despesa_criar'),
    path('despesas/<int:pk>/editar/', views.DespesaUpdateView.as_view(), name='despesa_editar'),
    path('despesas/<int:pk>/excluir/', views.DespesaDeleteView.as_view(), name='despesa_excluir'),

    # Categorias
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/nova/', views.CategoriaCreateView.as_view(), name='categoria_criar'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/excluir/', views.CategoriaDeleteView.as_view(), name='categoria_excluir'),

    # Alertas e Orçamento
    path('alertas/configuracao/', views.configuracao_alertas_view, name='configuracao_alertas'),
    path('orcamento/', views.OrcamentoListView.as_view(), name='orcamento_lista'),
    path('orcamento/novo/', views.OrcamentoCreateView.as_view(), name='orcamento_criar'),
    path('orcamento/<int:pk>/editar/', views.OrcamentoUpdateView.as_view(), name='orcamento_editar'),
    path('orcamento/<int:pk>/excluir/', views.OrcamentoDeleteView.as_view(), name='orcamento_excluir'),

    # Exportação
    path('exportar/<str:tipo>/<str:formato>/', views.exportar_view, name='exportar'),

    # Calendário / Heat Zone
    path('calendario/', views.calendario_view, name='calendario'),
    path('calendario/<int:ano>/<int:mes>/', views.calendario_view, name='calendario_mes'),
    path('calendario/<int:ano>/<int:mes>/<int:dia>/', views.detalhes_dia_view, name='calendario_dia'),
]
