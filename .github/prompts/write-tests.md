# Prompt: Escrever Testes

## Uso
Use este prompt para solicitar criação de testes automatizados.

## Template
```
Crie testes para: [MÓDULO/FUNCIONALIDADE]

## Tipo de Testes
- [ ] Unitários (models, services)
- [ ] Integração (views, fluxos completos)
- [ ] Isolamento (multi-tenant, user_id)
- [ ] Permissões (login, superusuário, conta bloqueada)

## Cenários Específicos
- [Cenário 1]
- [Cenário 2]
- [Cenário 3]
```

## Instruções para o Agente
1. Carregar `tests.md` para padrões de teste.
2. Carregar `business-rules.md` para cenários de negócio.
3. Criar fixtures necessárias em `conftest.py`.
4. Implementar testes com nomes descritivos em português.
5. Cobrir cenários positivos e negativos.
6. Testar isolamento multi-tenant obrigatoriamente.
7. Executar testes e reportar resultados.
