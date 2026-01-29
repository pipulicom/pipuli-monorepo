# Agent Instructions

**IMPORTANTE:** Leia este diretório ANTES de fazer mudanças no código.

## 📚 Ordem de Leitura

1. **`patterns.md`** - Padrões obrigatórios de código
2. **`rules.md`** - O que NUNCA fazer
3. **`architecture.md`** - Como o sistema funciona
4. **`examples/`** - Código de referência

## 🎯 Quando Consultar

- ✅ Antes de criar novos workflows
- ✅ Antes de refatorar código existente
- ✅ Quando tiver dúvidas sobre padrões
- ✅ Ao adicionar novas features
- ✅ Ao revisar código

## 🔄 Manutenção

Este diretório deve ser atualizado quando:
- Novos padrões são criados (ex: novo decorator)
- Decisões arquiteturais mudam (ex: remover classe base)
- Novas mensagens/constants são adicionadas
- Novos validators são criados

**Responsabilidade:** Agente de IA deve atualizar `.agent/` ao fazer mudanças estruturais.

## 📁 Estrutura

```
.agent/
  ├── README.md           ← Você está aqui
  ├── patterns.md         ← Padrões obrigatórios
  ├── rules.md            ← NUNCA/SEMPRE
  ├── architecture.md     ← Como funciona
  └── examples/
      ├── workflow.py     ← Template de workflow
      └── validator.py    ← Template de validator
```
