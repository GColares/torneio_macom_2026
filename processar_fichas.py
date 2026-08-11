import os
import sys
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macom_project.settings')
django.setup()

from dashboard.models import Dupla, Potencia

# Mapeamento para garantir consistência
def map_potencia(p_str):
    if not p_str: return None
    p_str = p_str.upper()
    if 'GLOMAM' in p_str or 'GRANDE LOJA' in p_str:
        return Potencia.objects.get(sigla='GLOMAM')
    if 'GOB' in p_str or 'GRANDE ORIENTE DO BRASIL' in p_str:
        return Potencia.objects.get(sigla='GOB-AM')
    if 'GOA' in p_str or 'AMAZONENSE' in p_str:
        return Potencia.objects.get(sigla='GOA')
    return None

data = [
    # 18.48.pdf
    ("Daniel da Cunha Santos", "Deus, Lei e Perseverança", "GLOMAM", "Marcos Antonio Ribeiro da Cruz", "Deus, Lei e Perseverança", "GLOMAM", "CamScanner 10-08-2026 18.48.pdf"),
    ("Ewerton da Cruz Gonzaga", "Deus, Lei e Perseverança 09", "GLOMAM", "João Victor da Silva Lima", "Deus, Lei e Perseverança 09", "GLOMAM", "CamScanner 10-08-2026 18.48.pdf"),
    ("Paulo Almeida Filho", "Estrela da Alvorada 40", "GLOMAM", "Roberto Vasconcelos Rodrigues", "Estrela da Alvorada", "GLOMAM", "CamScanner 10-08-2026 18.48.pdf"),
    ("Bernardo Carvalho da Silva", "Deus, Lei e Perseverança N09", "GLOMAM", "Raphael Fontes Rodrigues", "Deus, Lei e Perseverança N09", "GLOMAM", "CamScanner 10-08-2026 18.48.pdf"),
    
    # 18.52.pdf
    ("Bruno Raphael Gomes de Sa Leitao", "Firmeza e Renascensa", "GLOMAM", "Paulo Victor Coelho da Silva", "Firmeza e Renascensa N37", "GLOMAM", "CamScanner 10-08-2026 18.52.pdf"),
    ("Elio de Oliveira Souza Junior", "12 de Janeiro Nº 21", "GLOMAM", "Rociano da Silva Santos", "12 de Janeiro Nº 21", "GLOMAM", "CamScanner 10-08-2026 18.52.pdf"),
    ("Ryan de Souza Amaral", "Rei Salomão 44", "GLOMAM", "Antonio Lucian Maranguape de Sa", "Rei Salomão 44", "GLOMAM", "CamScanner 10-08-2026 18.52.pdf"),
]

def run():
    print("Processando 7 fichas encontradas nos PDFs...\n")
    processed = 0
    invalids = 0

    for j1, l1, p1, j2, l2, p2, file_src in data:
        pot1 = map_potencia(p1)
        pot2 = map_potencia(p2)
        
        # Simple duplicate check
        is_valid = True
        exists = Dupla.objects.filter(nome_jogador1__iexact=j1).exists() or Dupla.objects.filter(nome_jogador2__iexact=j1).exists()
        if exists:
            is_valid = False
            
        Dupla.objects.create(
            nome_jogador1=j1,
            loja_jogador1=l1,
            potencia_jogador1=pot1,
            nome_jogador2=j2,
            loja_jogador2=l2,
            potencia_jogador2=pot2,
            origem='Manual',
            valido=is_valid,
            status_pagamento='Confirmado'
        )
        
        if is_valid:
            print(f"[OK] Inserido: {j1} & {j2} ({pot1.sigla})")
            processed += 1
        else:
            print(f"[ALERTA] Risco de Duplicidade: {j1} & {j2}")
            invalids += 1
            
    # Rename PDFs
    img_dir = r"C:\Projetos\torneio_macom_2026\static\img\inscricoes-manuais"
    for file in os.listdir(img_dir):
        if file.startswith("CamScanner") and file.endswith(".pdf"):
            old_path = os.path.join(img_dir, file)
            new_path = os.path.join(img_dir, "processada_" + file.replace("CamScanner ", ""))
            shutil.move(old_path, new_path)
            
    print(f"\nResumo: {processed} fichas processadas com sucesso. {invalids} marcadas como inválidas por segurança.")

if __name__ == '__main__':
    run()
