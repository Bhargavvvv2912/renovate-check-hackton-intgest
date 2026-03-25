# Prompt: Criar Feature

## Uso
Use este prompt quando precisar implementar uma nova funcionalidade no sistema.

## Template
```
Preciso criar a feature: [NOME DA FEATURE]

## Objetivo
[Descreva o que a feature deve fazer]

## Escopo
- Backend: [models, views, services necessários]
- Frontend: [templates, componentes necessários]
- Testes: [cenários a serem testados]

## Critérios de Aceite
- [ ] [Critério 1]
- [ ] [Critério 2]
- [ ] [Critério 3]

## Contexto Adicional
[Regras de negócio específicas, referências a telas existentes, etc.]
```

## Instruções para o Agente
1. Carregar `business-rules.md` e `tech-constraints.md`.
2. Verificar se existem models/views relacionados.
3. Implementar backend primeiro, depois frontend.
4. Criar testes para a feature.
5. Garantir isolamento por `user_id`.
