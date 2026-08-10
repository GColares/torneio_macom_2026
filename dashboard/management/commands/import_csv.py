import os
import csv
import glob
from django.core.management.base import BaseCommand
from dashboard.models import Dupla
from django.conf import settings

class Command(BaseCommand):
    help = 'Importa as duplas do arquivo CSV sem sobrescrever dados vitais.'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'Inscrição no evento')
        list_of_files = glob.glob(os.path.join(data_dir, '*.csv'))
        
        if not list_of_files:
            self.stdout.write(self.style.WARNING('Nenhum arquivo CSV encontrado.'))
            return
            
        latest_file = max(list_of_files, key=os.path.getctime)
        self.stdout.write(f'Importando dados de: {os.path.basename(latest_file)}')
        
        count_created = 0
        count_updated = 0
        
        with open(latest_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                return
            
            nome_indices = [i for i, h in enumerate(headers) if 'nome completo' in h.lower() or 'nome' in h.lower()]
            potencia_indices = [i for i, h in enumerate(headers) if 'potência' in h.lower() or 'potencia' in h.lower()]
            loja_indices = [i for i, h in enumerate(headers) if 'loja' in h.lower()]
            data_idx = next((i for i, h in enumerate(headers) if 'data' in h.lower() or 'carimbo' in h.lower()), None)
            
            for row in reader:
                if not row or len(row) == 0:
                    continue
                    
                data_hora = row[data_idx] if data_idx is not None and data_idx < len(row) else ''
                
                nome1 = row[nome_indices[0]] if len(nome_indices) > 0 and nome_indices[0] < len(row) else ''
                nome2 = row[nome_indices[1]] if len(nome_indices) > 1 and nome_indices[1] < len(row) else ''
                
                pot1 = row[potencia_indices[0]] if len(potencia_indices) > 0 and potencia_indices[0] < len(row) else 'Não Informado'
                pot2 = row[potencia_indices[1]] if len(potencia_indices) > 1 and potencia_indices[1] < len(row) else 'Não Informado'
                
                loja1 = row[loja_indices[0]] if len(loja_indices) > 0 and loja_indices[0] < len(row) else 'Não Informado'
                loja2 = row[loja_indices[1]] if len(loja_indices) > 1 and loja_indices[1] < len(row) else 'Não Informado'

                if not pot1.strip(): pot1 = 'Não Informado'
                if not pot2.strip(): pot2 = 'Não Informado'
                if not loja1.strip(): loja1 = 'Não Informado'
                if not loja2.strip(): loja2 = 'Não Informado'
                
                if not nome1.strip():
                    continue 
                
                obj, created = Dupla.objects.get_or_create(
                    nome_jogador1=nome1,
                    nome_jogador2=nome2,
                    data_hora=data_hora,
                    defaults={
                        'potencia_jogador1': pot1,
                        'potencia_jogador2': pot2,
                        'loja_jogador1': loja1,
                        'loja_jogador2': loja2,
                    }
                )
                
                if created:
                    count_created += 1
                else:
                    obj.potencia_jogador1 = pot1
                    obj.potencia_jogador2 = pot2
                    obj.loja_jogador1 = loja1
                    obj.loja_jogador2 = loja2
                    obj.save()
                    count_updated += 1
                    
        self.stdout.write(self.style.SUCCESS(f'Sucesso! {count_created} novas. {count_updated} atualizadas.'))
