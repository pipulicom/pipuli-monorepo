# Regras Estritas

## ❌ NUNCA Faça

### 1. NUNCA hardcode mensagens
**Motivo:** Tínhamos mensagens duplicadas em 13 arquivos  
**Use:** `ErrorMessages.*` ou `SuccessMessages.*`

### 2. NUNCA valide auth manualmente
**Motivo:** 8 linhas duplicadas em cada workflow  
**Use:** `@require_auth` decorator

### 3. NUNCA use magic numbers
**Motivo:** Dificulta manutenção  
**Use:** `constants.py`

### 4. NUNCA valide inline
**Motivo:** Duplicação entre create/update  
**Use:** Validators centralizados

### 5. NUNCA importe inline
**Motivo:** Dificulta leitura  
**Use:** Imports no topo

### 6. NUNCA use classe base Workflow
**Motivo:** Foi removida (commit 2240eb5)  
**Use:** Funções diretas com decorators

### 7. NUNCA misture PT/EN
**Motivo:** Inconsistência de UX  
**Use:** Inglês criativo sempre

### 8. NUNCA delete diretamente
**Motivo:** Perda de dados  
**Use:** Soft-delete com `deletedAt`

### 9. NUNCA esqueça type hints
**Motivo:** Dificulta debug  
**Use:** `Dict[str, Any]`, `Logger`, etc

### 10. NUNCA retorne dict customizado
**Motivo:** Inconsistência de API  
**Use:** `success_response()` ou `error_response()`

---

## ✅ SEMPRE Faça

### 1. SEMPRE use @require_auth
Em workflows que precisam de autenticação

### 2. SEMPRE use validators centralizados
Para validações de input

### 3. SEMPRE use messages.py
Para todas as mensagens

### 4. SEMPRE use constants.py
Para valores fixos

### 5. SEMPRE organize imports no topo
Na ordem: stdlib → third-party → local

### 6. SEMPRE adicione docstrings
Com Args e Returns documentados

### 7. SEMPRE faça log com contexto
Inclua IDs, UIDs, tipos, etc

### 8. SEMPRE use type hints
Em todas as funções

### 9. SEMPRE verifique soft-delete
Antes de update/delete

### 10. SEMPRE retorne responses padronizados
`success_response()` ou `error_response()`

---

## 📝 Exemplos de Erros Comuns

### Erro 1: Mensagem hardcoded
```python
# ❌ ERRADO
return error_response(
    error="validation_error",
    message="Name is too short"
)

# ✅ CERTO
return error_response(
    error="validation_error",
    message=ErrorMessages.NAME_TOO_SHORT
)
```

### Erro 2: Auth manual
```python
# ❌ ERRADO
def execute(data, config, logger):
    auth_data = data.get("_auth")
    if not auth_data:
        return error_response(...)
    uid = auth_data.get("uid")

# ✅ CERTO
@require_auth
def execute(data, config, logger):
    uid = data["_uid"]
```

### Erro 3: Magic number
```python
# ❌ ERRADO
if len(name) < 2:
    ...

# ✅ CERTO
from constants import MIN_NAME_LENGTH
if len(name) < MIN_NAME_LENGTH:
    ...
```

### Erro 4: Validação inline
```python
# ❌ ERRADO
if not name or len(name) < 2:
    return error_response(...)
if asset_type not in ["INVESTMENT", "PROPERTY"]:
    return error_response(...)

# ✅ CERTO
from .asset_validator import validate_asset_fields
is_valid, error = validate_asset_fields(name=name, asset_type=asset_type)
if not is_valid:
    return error
```

### Erro 5: Import inline
```python
# ❌ ERRADO
def execute(data, config, logger):
    from .validator import validate_fields  # ❌

# ✅ CERTO
from .validator import validate_fields  # No topo

def execute(data, config, logger):
    ...
```
