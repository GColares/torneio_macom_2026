---
trigger: always_on
description: Garante o uso de caminhos relativos em projetos Django para evitar quebra ao mudar de ambiente.
---

# Regra: Uso de Caminhos Dinâmicos (Dynamic Paths)

Ao escrever scripts Python ou views para este projeto Django:

1. **NUNCA** utilize caminhos absolutos *hardcoded* apontando para pastas locais específicas (ex: `C:\Projetos\...`, `D:\...`, `/var/www/...`).
2. **SEMPRE** utilize a configuração `settings.BASE_DIR` combinada com `os.path.join` (ou objetos `Path`) para referenciar arquivos que estão dentro do projeto.
3. Se estiver em um script de gerência (`management/commands`) ou qualquer arquivo Django, importe:
   ```python
   from django.conf import settings
   import os
   caminho_arquivo = os.path.join(settings.BASE_DIR, 'Pasta', 'arquivo.ext')
   ```

Isso garante que o projeto continue funcionando independente de qual máquina (ou sistema operacional) o repositório for clonado.
