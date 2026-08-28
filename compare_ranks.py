import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macom_project.settings')
django.setup()

from dashboard.views import api_torneio_state
from django.http import HttpRequest
from dashboard.models import Confronto

def get_ranks():
    r = HttpRequest()
    r.method = 'GET'
    resp = api_torneio_state(r)
    data = json.loads(resp.content.decode('utf-8'))
    return {d['dupla']: d['rank'] for d in data['leaderboard']}

ranks_with = get_ranks()

# Remove temporariamente os 2 confrontos
c1 = Confronto.objects.filter(dupla_b__credenciamento=30, dupla_a__credenciamento=1).first()
c2 = Confronto.objects.filter(dupla_b__credenciamento=30, dupla_a__credenciamento=17).first()

c1.delete()
c2.delete()

ranks_without = get_ranks()

print('\n--- COMPARAÇÃO DE RANKING ---')
for dupla, r_with in ranks_with.items():
    r_without = ranks_without.get(dupla, None)
    if r_with != r_without:
        print(f"{dupla} mudou! Antes: {r_without} -> Agora: {r_with}")

