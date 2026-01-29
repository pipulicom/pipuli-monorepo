# Padrões Obrigatórios

## 1. Autenticação

### ✅ SEMPRE use @require_auth decorator

**Localização:** `decorators.py`  
**Exemplo:** `workflows/pipuli_asset_mngmt/create_asset.py:10`

```python
from decorators import require_auth

@require_auth
def execute(data, config, logger):
    uid = data["_uid"]  # Já validado e injetado pelo decorator
    ...
```

### ❌ NUNCA valide auth manualmente

```python
# ❌ ERRADO
auth_data = data.get("_auth")
if not auth_data:
    return error_response(...)
uid = auth_data.get("uid")
```

---

## 2. Mensagens

### ✅ SEMPRE use messages.py

**Localização:** `messages.py`  
**Classes:** `ErrorMessages`, `SuccessMessages`

```python
from messages import ErrorMessages, SuccessMessages

# Erro
return error_response(
    error="validation_error",
    message=ErrorMessages.NAME_TOO_SHORT
)

# Sucesso
return success_response(
    message=SuccessMessages.ASSET_CREATED,
    data=asset_data
)
```

**Mensagens Disponíveis:**
- `ErrorMessages.UNAUTHORIZED`
- `ErrorMessages.ASSET_NOT_FOUND`
- `ErrorMessages.MOVEMENT_NOT_FOUND`
- `ErrorMessages.NAME_TOO_SHORT`
- `ErrorMessages.INVALID_ASSET_TYPE`
- `ErrorMessages.DB_ERROR_SAVE` (usa `.format(item="...")`)
- `SuccessMessages.ASSET_CREATED`
- `SuccessMessages.MOVEMENT_CREATED`
- Ver `messages.py` para lista completa

### ❌ NUNCA hardcode mensagens

```python
# ❌ ERRADO
message="Asset created successfully"
```

---

## 3. Validadores

### ✅ SEMPRE use validators centralizados

**Localizações:**
- `workflows/pipuli_asset_mngmt/asset_validator.py`
- `workflows/pipuli_asset_mngmt/movement_validator.py`

```python
from .asset_validator import validate_asset_fields

is_valid, error = validate_asset_fields(
    name=name,
    asset_type=asset_type,
    category=category,
    required=True  # True para create, False para update
)
if not is_valid:
    return error
```

**Type Alias:** `ValidationResult = Tuple[bool, Optional[Dict[str, Any]]]`

### ❌ NUNCA valide inline

```python
# ❌ ERRADO
if len(name) < 2:
    return error_response(...)
```

---

## 4. Constants

### ✅ SEMPRE use constants.py

**Localização:** `constants.py`

```python
from constants import MIN_NAME_LENGTH, VALID_ASSET_TYPES

if len(name) < MIN_NAME_LENGTH:
    ...

if asset_type not in VALID_ASSET_TYPES:
    ...
```

**Constants Disponíveis:**
- `MIN_NAME_LENGTH = 2`
- `VALID_ASSET_TYPES = ["INVESTMENT", "PROPERTY"]`
- `MOVEMENT_ID_PREFIX = "mov_"`
- `TIMESTAMP_MULTIPLIER = 1000`

### ❌ NUNCA use magic numbers

```python
# ❌ ERRADO
if len(name) < 2:  # Por que 2?
movement_id = f"mov_{timestamp}"  # Por que "mov_"?
```

---

## 5. Imports

### ✅ SEMPRE organize no topo em ordem específica

```python
# 1. Standard library
from typing import Dict, Any
from datetime import datetime, timezone

# 2. Third-party
from logger.logger import Logger

# 3. Local - response
from response.formatter import success_response, error_response

# 4. Local - services
from services.database import DatabaseService

# 5. Local - helpers
from decorators import require_auth
from messages import ErrorMessages, SuccessMessages
from constants import CONSTANT_NAME

# 6. Local - validators (relative import)
from .resource_validator import validate_fields
```

### ❌ NUNCA importe inline

```python
# ❌ ERRADO
def execute(data, config, logger):
    from .asset_validator import validate_asset_fields  # ❌
```

---

## 6. Soft-Delete

### ✅ SEMPRE use campo deletedAt

```python
# Criar
resource_data = {
    "field": value,
    "createdAt": datetime.now(timezone.utc).isoformat(),
    "deletedAt": None  # Sempre inicializar
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

### ❌ NUNCA delete diretamente

```python
# ❌ ERRADO
db.delete(path)  # Perda de dados!
```

---

## 7. Logging

### ✅ SEMPRE use contexto estruturado

```python
workflow_logger.info(
    "Asset created successfully",
    {"asset_id": asset_id, "uid": uid, "type": asset_type}
)
```

### ❌ NUNCA faça log sem contexto

```python
# ❌ ERRADO
workflow_logger.info("Asset created")  # Sem contexto
```

---

## 8. Type Hints

### ✅ SEMPRE use type hints

```python
def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    ...
```

### ❌ NUNCA omita type hints

```python
# ❌ ERRADO
def execute(data, config, logger):  # Sem types
```

---

## 9. Responses

### ✅ SEMPRE use success_response/error_response

```python
from response.formatter import success_response, error_response

return success_response(message=..., data=...)
return error_response(error=..., message=...)
```

### ❌ NUNCA retorne dict customizado

```python
# ❌ ERRADO
return {"status": "ok", "result": data}
```
