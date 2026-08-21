import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macom_project.settings')
django.setup()

from dashboard.models import Dupla

duplas = Dupla.objects.filter(purgado=False)
seen = {}
duplicates = []

for d in duplas:
    name1 = d.nome_jogador1.strip().lower() if d.nome_jogador1 else ''
    name2 = d.nome_jogador2.strip().lower() if d.nome_jogador2 else ''
    names = tuple(sorted([name1, name2]))
    
    if names in seen:
        seen[names].append(d)
        if names not in duplicates:
            duplicates.append(names)
    else:
        seen[names] = [d]

for names in duplicates:
    if not names[0] and not names[1]:
        continue # Ignore empty names
    print(f'=== Possible Duplicate group for {names} ===')
    for d in seen[names]:
        print(f'  ID: {d.id} | J1: {d.nome_jogador1} | J2: {d.nome_jogador2} | Origem: {d.origem}')

# Also fuzzy match (just J1)
print("\\n=== Checking for J1 name collisions (Possible typo) ===")
j1_seen = {}
j1_dups = []
for d in duplas:
    name1 = d.nome_jogador1.strip().lower() if d.nome_jogador1 else ''
    if not name1: continue
    
    first_name = name1.split()[0]
    last_name = name1.split()[-1] if len(name1.split()) > 1 else ''
    key = f"{first_name} {last_name}"
    
    if key in j1_seen:
        j1_seen[key].append(d)
        if key not in j1_dups: j1_dups.append(key)
    else:
        j1_seen[key] = [d]

for key in j1_dups:
    # If the exact (J1, J2) was already flagged, skip
    if len(j1_seen[key]) > 1:
        print(f'Possible J1 collision: {key}')
        for d in j1_seen[key]:
            print(f'  ID: {d.id} | J1: {d.nome_jogador1} | J2: {d.nome_jogador2}')
