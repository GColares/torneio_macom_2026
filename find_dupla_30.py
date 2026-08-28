import os
import glob
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import time
from tqdm import tqdm

load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = '''Você é um assistente analisando súmulas do torneio de dominó.
Sua missão é UMA SÓ: descobrir se a "DUPLA 30" (ou 33) jogou a partida registrada nesta súmula.
Olhe especificamente para os campos que identificam as duplas (ex: "DUPLA ___").
Se o número 30 NÃO estiver lá, retorne exatamente: NAO
Se a Dupla 30 JOGOU, retorne exatamente o padrão:
SIM | Mesa: [Nº da Mesa] | Duplas: [D1] x [D2] | Placar: [Pontos D1] x [Pontos D2]'''

image_paths = glob.glob('resultados/**/*.jpeg', recursive=True)
print(f'Iniciando varredura em {len(image_paths)} sumulas...')

found = []
for path in tqdm(image_paths):
    try:
        img = Image.open(path)
        response = model.generate_content([prompt, img])
        text = response.text.strip().upper()
        if 'SIM' in text:
            print(f'\n[ACHOU!] Arquivo: {path} -> {text}')
            found.append(f'{path} -> {text}')
        time.sleep(2) # Evitar rate limit
    except Exception as e:
        print(f'\nErro em {path}: {e}')

print('\n--- RESULTADO FINAL DA BUSCA PELA DUPLA 30 ---')
for f in found:
    print(f)
