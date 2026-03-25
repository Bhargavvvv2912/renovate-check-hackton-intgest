# Skill: Segurança Multi-Tenant — Padrões do Projeto

> Regras de segurança invioláveis para isolamento de dados entre usuários (SaaS multi-tenant por user_id).

---

## 1. Regra de Ouro

**Todo dado de negócio pertence a um usuário. Nunca retornar dados de outro usuário.**

```python
# ❌ VULNERABILIDADE CRÍTICA: dados de todos os usuários
def dashboard_view(request):
    receitas = Receita.objects.all()  # NUNCA

# ✅ CORRETO: apenas dados do usuário autenticado
def dashboard_view(request):
    receitas = Receita.objects.filter(user=request.user)
```

---

## 2. Autenticação Obrigatória

Toda view que acessa dados de negócio **deve** exigir login:

```python
# FBVs — usar decorator
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    ...

# CBVs — usar mixin
from django.contrib.auth.mixins import LoginRequiredMixin

class ReceitaListView(LoginRequiredMixin, ListView):
    model = Receita
    # LoginRequiredMixin deve ser o PRIMEIRO na herança
```

Exceções permitidas (sem login): `landing page`, `login`, `registro`.

---

## 3. UsuarioQuerysetMixin — Proteção em CBVs

```python
class UsuarioQuerysetMixin(LoginRequiredMixin):
    """
    Mixin que garante isolamento por user_id em todas as CBVs.
    Usar em TODA view CRUD que herda ListView, DetailView, UpdateView, DeleteView.
    """
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

# Uso:
class DespesaUpdateView(UsuarioQuerysetMixin, UpdateView):
    model = Despesa
    # Se user tentar editar despesa de outro: automaticamente 404
    # porque get_queryset filtra pelo usuário correto
```

---

## 4. Proteção no form_valid de CreateView

```python
class ReceitaCreateView(LoginRequiredMixin, CreateView):
    model = Receita
    form_class = ReceitaForm

    def form_valid(self, form):
        form.instance.user = self.request.user  # SEMPRE setar o user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # para filtrar categorias no form
        return kwargs
```

---

## 5. FBVs — Verificação Explícita de Propriedade

```python
from django.shortcuts import get_object_or_404

@login_required
def receita_editar_view(request, pk):
    # get_object_or_404 com user garante 404 para objetos de outros usuários
    receita = get_object_or_404(Receita, pk=pk, user=request.user)
    ...

# ❌ NUNCA assim — expõe dados de outros usuários
receita = get_object_or_404(Receita, pk=pk)  # sem verificar user
```

---

## 6. Services — user como Parâmetro

```python
# Services nunca acessam request — recebem user explicitamente
# Isso garante que o chamador (view) é responsável por passar o user correto

def calcular_saldo(user: User) -> dict:
    # A responsabilidade de passar request.user é da view
    return Receita.objects.filter(user=user).aggregate(...)
```

---

## 7. Categorias e Dados Compartilhados

```python
# Categorias pertencem ao usuário — filtrar sempre
class ReceitaForm(ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # ✅ Apenas categorias do usuário logado
            self.fields['categoria'].queryset = Categoria.objects.filter(
                user=user, tipo=Categoria.TipoCategoria.RECEITA
            )
        else:
            self.fields['categoria'].queryset = Categoria.objects.none()
```

---

## 8. Proteção CSRF

Obrigatório em todos os formulários POST:

```html
<!-- Template: OBRIGATÓRIO em todo <form method="post"> -->
<form method="post">
  {% csrf_token %}
  ...
</form>
```

Django por padrão rejeita POSTs sem token CSRF (middleware ativo em settings).

---

## 9. Validação Server-Side — Nunca Confiar no Frontend

```python
class OrcamentoForm(ModelForm):
    def clean_mes(self):
        mes = self.cleaned_data.get('mes')
        if mes is not None and (mes < 1 or mes > 12):
            raise ValidationError('Mês deve estar entre 1 e 12.')
        return mes

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise ValidationError('O valor deve ser maior que zero.')
        return valor
```

---

## 10. Superusuário — Acesso Administrativo

```python
@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied  # 403
    # Superusuário pode ver todos os usuários
    usuarios = User.objects.all().order_by('-date_joined')
    ...
```

---

## 11. Middleware de Conta Bloqueada

O projeto possui `ContaBloqueadaMiddleware` em `usuarios/middleware.py`:

```python
# Views públicas que não precisam de verificação de bloqueio:
URLS_LIVRES = ['/usuarios/login/', '/usuarios/registro/', '/']

class ContaBloqueadaMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            if request.path not in URLS_LIVRES:
                return redirect('usuarios:conta_bloqueada')
        return self.get_response(request)
```

---

## 12. Exposição de IDs Internos

```python
# ✅ Usar PKs em URLs — aceitável pois UsuarioQuerysetMixin protege
path('despesas/<int:pk>/editar/', views.DespesaUpdateView.as_view())

# ✅ Se pk se validado com user=request.user, está seguro
despesa = get_object_or_404(Despesa, pk=pk, user=request.user)

# ❌ Nunca expor dados sensíveis de outros usuários em respostas JSON
# ❌ Nunca incluir informações de outros usuarios em templates
```

---

## 13. Checklist de Segurança — Por Arquivo

| Arquivo | Verificação |
|---------|-------------|
| `views.py` | `@login_required` ou `LoginRequiredMixin` em toda view protegida |
| `views.py` CBV Create | `form.instance.user = request.user` no `form_valid` |
| `views.py` CBV List/Update/Delete | `UsuarioQuerysetMixin` ou `.filter(user=request.user)` |
| `services.py` | `user` como parâmetro, todas as queries com `filter(user=user)` |
| `forms.py` | Categorias filtradas por `user` no `__init__` |
| Templates | `{% csrf_token %}` em todo `<form method="post">` |
| `urls.py` | Rotas admin protegidas com `is_superuser` na view |
