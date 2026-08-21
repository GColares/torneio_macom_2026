---
description: Regras para verificação de dados vazios em requests HTTP.
---

# Regra: Verificação de Chaves Vazias no Backend

Sempre que ler um dicionário do tipo `request.POST`, `request.FILES` ou `body` (JSON) no Django para determinar se um objeto relacionado deve ser criado ou editado:

1. **Nunca use apenas `in`:** Jamais utilize a verificação `if 'campo' in body:` para campos de formulário que podem vir em branco (strings vazias `""`). O frontend frequentemente envia a chave com valor vazio em submissões AJAX e forms FormData.
2. **Avalie o conteúdo (Truthy):** Sempre utilize `.get('campo', '').strip()` para garantir que o campo possui conteúdo real antes de disparar lógicas de criação de registros relacionados (ex: faturas, logs, comprovantes, etc).

**Errado:**
```python
if 'data_pagamento' in body or request.FILES.get('arquivo'):
    # Vai dar falso positivo se data_pagamento vier como string vazia ""
    criar_comprovante()
```

**Correto:**
```python
if body.get('data_pagamento', '').strip() or request.FILES.get('arquivo'):
    # Só entra se tiver texto ou arquivo real
    criar_comprovante()
```
