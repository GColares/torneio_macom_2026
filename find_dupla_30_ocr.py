import os
import glob
from PIL import Image
import pytesseract
from tqdm import tqdm

image_paths = glob.glob('resultados/**/*.jpeg', recursive=True)
print(f'Iniciando varredura com Tesseract OCR em {len(image_paths)} sumulas...')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

found = []
for path in tqdm(image_paths):
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img).upper()
        # Look for "30" or "33" in the text
        if '30' in text or '33' in text or 'TRINTA' in text:
            print(f'\n[ACHOU?] Arquivo: {path} pode conter a Dupla 30/33!')
            found.append(path)
    except Exception as e:
        pass

print('\n--- SÚMULAS SUSPEITAS DE TEREM A DUPLA 30 ---')
for f in found:
    print(f)
