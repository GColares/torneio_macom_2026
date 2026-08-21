# Regra: Parsing de Datas de Formulários

Sempre que receber datas de campos HTML `<input type="datetime-local">` em views ou APIs do Django:

1. **Evite `datetime.strptime`:** Não use `datetime.strptime` com formatos estritos (como `"%Y-%m-%dT%H:%M:%S"`), pois falharão se o navegador omitir os segundos (ex: envio de `2026-08-21T10:41`).
2. **Use `parse_datetime`:** Utilize obrigatoriamente a função nativa `parse_datetime` do Django, que possui suporte oficial e flexível a formatos ISO.

```python
from django.utils.dateparse import parse_datetime
from django.utils import timezone

data_hora_str = request.POST.get('data_hora')
data_hora = parse_datetime(data_hora_str) if data_hora_str else None

if not data_hora:
    data_hora = timezone.now() # Fallback apenas se vazio ou inválido
```
