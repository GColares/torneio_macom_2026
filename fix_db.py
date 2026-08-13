from dashboard.models import Dupla
Dupla.objects.filter(origem__startswith='Eletr').update(origem='Eletr\u00f4nico')
print("Fix executado")
