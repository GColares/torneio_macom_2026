import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macom_project.settings')
django.setup()

from dashboard.models import Confronto, Mesa, Dupla

mesa8 = Mesa.objects.get(numero=8)
dupla_1 = Dupla.objects.get(credenciamento=1)
dupla_17 = Dupla.objects.get(credenciamento=17)
dupla_30 = Dupla.objects.get(credenciamento=30)

# Inserindo Jogo 813 (Mesa 8, Dupla 1 x Dupla 30)
c1 = Confronto.objects.create(
    mesa=mesa8,
    dupla_a=dupla_1,
    dupla_b=dupla_30,
    pontos_a=230,
    pontos_b=115,
    status='Finalizado',
    data_fim=timezone.now()
)
print(f"Inserido: {c1}")

# Inserindo Jogo 815 (Mesa 8, Dupla 17 x Dupla 30)
c2 = Confronto.objects.create(
    mesa=mesa8,
    dupla_a=dupla_17,
    dupla_b=dupla_30,
    pontos_a=265,
    pontos_b=190,
    status='Finalizado',
    data_fim=timezone.now()
)
print(f"Inserido: {c2}")

