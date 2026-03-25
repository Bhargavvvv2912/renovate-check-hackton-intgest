# Prompt: Revisão de Código

## Uso
Use este prompt para solicitar uma revisão detalhada de código.

## Template
```
Revise o código em: [ARQUIVO OU ÁREA]

## Foco da Revisão
- [ ] Segurança (isolamento user_id, CSRF, validações)
- [ ] Padrões (PEP 8, convenções do projeto)
- [ ] Performance (queries N+1, agregações)
- [ ] UX (feedback ao usuário, mensagens de erro)
- [ ] Testes (cobertura adequada)
```

## Instruções para o Agente
1. Ler o código indicado.
2. Verificar conformidade com `tech-constraints.md` e `business-rules.md`.
3. Checar isolamento por `user_id` em todas as queries.
4. Verificar proteção CSRF em formulários.
5. Identificar queries N+1 ou performance.
6. Verificar tratamento de erros e feedback ao usuário.
7. Listar problemas encontrados com sugestões de correção.
