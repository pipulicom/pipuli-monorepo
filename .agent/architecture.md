# Arquitetura

## Padrão: Gateway → Workflow → Service

```
Request → Gateway → Workflow → Service → Database
          (auth)    (logic)    (infra)
```

### Gateway (`gateway/`)
- Valida `X-API-Key`
- Valida `Authorization` token (se configurado)
- Injeta `_auth` no request data
- Roteia para workflow correto
- **NÃO** contém lógica de negócio

### Workflows (`workflows/{project}/`)
- Valida input usando validators
- Contém lógica de negócio
- Orquestra services
- Retorna responses padronizados
- Cada workflow é uma função `execute(data, config, logger)`

### Services (`services/`)
- Wrappers de infraestrutura
- `DatabaseService` - Firestore wrapper
- `ValidationService` - Validações genéricas
- `Logger` - Structured logging
- Reutilizáveis entre workflows

---

## Estrutura de Projeto

```
workflows/
  pipuli_asset_mngmt/
    __init__.py              ← Registra workflows
    create_asset.py          ← Workflow
    update_asset.py
    delete_asset.py
    create_asset_movement.py
    update_asset_movement.py
    delete_asset_movement.py
    get_asset_movements.py
    get_user_dashboard.py
    consolidate_month.py
    auth_login.py
    asset_validator.py       ← Validator
    movement_validator.py
```

---

## Decisões Arquiteturais

### Por que removemos classe base Workflow?
- **Antes:** `workflows.base.Workflow` para reduzir duplicação
- **Problema:** Adicionava complexidade desnecessária
- **Solução:** Validators centralizados + decorators
- **Resultado:** Código mais simples e direto
- **Commit:** 2240eb5

### Por que centralizamos mensagens?
- **Problema:** Mensagens duplicadas em 13 workflows
- **Solução:** `messages.py` com todas as mensagens
- **Benefício:** Mudanças em 1 lugar, tom de voz consistente
- **Commit:** 2240eb5

### Por que usamos @require_auth decorator?
- **Problema:** 8 linhas de validação auth em cada workflow
- **Solução:** Decorator que valida e injeta `_uid`
- **Benefício:** ~100 linhas eliminadas, menos bugs
- **Commit:** 22adbf7

### Por que validators separados?
- **Problema:** Validações duplicadas entre create/update
- **Solução:** Validators com flag `required=True/False`
- **Benefício:** Validações idênticas, DRY principle
- **Commit:** 2240eb5

---

## Padrões de Dados

### Request Padrão
```json
{
  "_auth": {
    "uid": "user123",
    "email": "user@example.com"
  },
  "field1": "value1",
  "field2": "value2"
}
```

**Nota:** `_auth` é injetado pelo Gateway após validar o token Firebase.

### Response Padrão (Sucesso)
```json
{
  "success": true,
  "message": "Creative success message",
  "data": {
    "id": "resource_id",
    "field": "value",
    "createdAt": "2025-12-06T12:00:00Z"
  }
}
```

### Response Padrão (Erro)
```json
{
  "success": false,
  "error": "error_type",
  "message": "Creative error message"
}
```

**Error Types:**
- `validation_error` - Input inválido
- `unauthorized` - Auth falhou
- `not_found` - Recurso não encontrado
- `forbidden` - Operação não permitida
- `database_error` - Erro no Firestore

---

## Soft-Delete Pattern

Todos os recursos usam soft-delete:
- Campo `deletedAt` (ISO timestamp ou `null`)
- Queries filtram `deletedAt == null`
- Delete = `update({deletedAt: now()})`
- Update/Get verificam `deletedAt` antes de operar

**Exemplo:**
```python
# Criar
resource_data = {
    "field": value,
    "createdAt": datetime.now(timezone.utc).isoformat(),
    "deletedAt": None
}

# Deletar
db.update(path, {
    "deletedAt": datetime.now(timezone.utc).isoformat()
})

# Verificar antes de update
if existing.get("deletedAt"):
    return error_response(
        error="not_found",
        message=ErrorMessages.RESOURCE_DELETED
    )
```

---

## Fluxo de Request

1. **Client** envia request para `/api/{project_id}/{workflow_name}`
2. **Gateway** valida API Key
3. **Gateway** valida Authorization token (se configurado)
4. **Gateway** injeta `_auth` no request data
5. **Handler** importa workflow dinamicamente
6. **Workflow** valida input usando validator
7. **Workflow** executa lógica de negócio
8. **Service** interage com Firestore
9. **Workflow** retorna response padronizado
10. **Gateway** retorna JSON para client

---

## Configuração de Projeto

Cada projeto tem um arquivo `configs/{project_id}.json`:

```json
{
  "project_id": "pipuli-asset-mngmt",
  "auth_project_id": "pipuli-frontend",
  "database": {
    "database_id": "pipuli-asset-mngmt-db"
  }
}
```

**Campos:**
- `project_id` - ID do projeto (kebab-case)
- `auth_project_id` - Firebase project para auth (opcional)
- `database.database_id` - Firestore database ID

---

## Naming Conventions

- **Project IDs:** kebab-case (`pipuli-asset-mngmt`)
- **Python packages:** snake_case (`pipuli_asset_mngmt`)
- **Config files:** kebab-case (`pipuli-asset-mngmt.json`)
- **Workflow files:** snake_case (`create_asset.py`)
- **Functions:** snake_case (`validate_asset_fields`)
- **Classes:** PascalCase (`ErrorMessages`)
- **Constants:** UPPER_SNAKE_CASE (`MIN_NAME_LENGTH`)
