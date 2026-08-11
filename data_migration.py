import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macom_project.settings')
django.setup()

from dashboard.models import Potencia, Dupla

def run():
    p1, _ = Potencia.objects.get_or_create(sigla='GLOMAM', defaults={'nome_completo': 'Grande Loja Maçônica do Amazonas (GLOMAM)'})
    p2, _ = Potencia.objects.get_or_create(sigla='GOB-AM', defaults={'nome_completo': 'Grande Oriente do Brasil – Amazonas (GOB-AM)'})
    p3, _ = Potencia.objects.get_or_create(sigla='GOA', defaults={'nome_completo': 'Grande Oriente Amazonense (GOA)'})
    
    # We will use contains matching due to encoding issues in the DB potentially, or just try exact match
    mapping = {
        'Grande Loja Maçônica do Amazonas (GLOMAM)': p1,
        'Grande Oriente do Brasil – Amazonas (GOB-AM)': p2,
        'Grande Oriente Amazonense (GOA)': p3,
        'GLOMAM': p1,
        'GOB-AM': p2,
        'GOA': p3
    }
    
    count = 0
    for d in Dupla.objects.all():
        updated = False
        
        if d.potencia_jogador1:
            for k, v in mapping.items():
                if k in d.potencia_jogador1:
                    d.potencia_obj1 = v
                    updated = True
                    break
                    
        if d.potencia_jogador2:
            for k, v in mapping.items():
                if k in d.potencia_jogador2:
                    d.potencia_obj2 = v
                    updated = True
                    break
                    
        if updated:
            d.save()
            count += 1
            
    print(f'Linked {count} duplas.')

if __name__ == '__main__':
    run()
