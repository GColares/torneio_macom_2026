from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.models import Dupla
import os
import shutil
import unidecode
import re
from datetime import datetime

class Command(BaseCommand):
    help = 'Processa comprovantes de pagamento usando OCR/Extrato de PDF e vincula às duplas.'

    def handle(self, *args, **options):
        # Configurar dependências de OCR
        try:
            import pdfplumber
            import pytesseract
            from PIL import Image
        except ImportError:
            self.stdout.write(self.style.ERROR("Bibliotecas ausentes! Instale pdfplumber, pytesseract, Pillow e unidecode."))
            return

        # Configurar caminho do tesseract no Windows
        tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            self.stdout.write(self.style.WARNING(f"Atenção: tesseract.exe não encontrado em {tesseract_cmd}. Se o pytesseract falhar, instale o Tesseract OCR ou defina o PATH."))

        # Diretórios
        base_img_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'comprovantes-pagamento')
        revisao_dir = os.path.join(base_img_dir, 'revisao-pendente')
        media_comprovantes_dir = os.path.join(settings.MEDIA_ROOT, 'comprovantes-pagamento')
        os.makedirs(revisao_dir, exist_ok=True)
        os.makedirs(media_comprovantes_dir, exist_ok=True)

        if not os.path.exists(base_img_dir):
            self.stdout.write(self.style.ERROR(f"Diretório não encontrado: {base_img_dir}"))
            return

        duplas_pendentes = Dupla.objects.filter(status_pagamento='Pendente', purgado=False)
        self.stdout.write(f"Duplas pendentes encontradas: {duplas_pendentes.count()}")

        # --- PRÉ-PROCESSAMENTO: Fatiamento de PDFs Multipáginas ---
        arquivos_para_fatiar = [f for f in os.listdir(base_img_dir) if os.path.isfile(os.path.join(base_img_dir, f)) and f.lower().endswith('.pdf')]
        
        for arquivo in arquivos_para_fatiar:
            caminho = os.path.join(base_img_dir, arquivo)
            try:
                from pypdf import PdfReader, PdfWriter
                import io
                with open(caminho, 'rb') as f_in:
                    file_data = f_in.read()
                    
                reader = PdfReader(io.BytesIO(file_data))
                if len(reader.pages) > 1:
                    self.stdout.write(f"Fatiando PDF multipágina: {arquivo} ({len(reader.pages)} páginas)")
                    for i, page in enumerate(reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)
                        novo_nome = f"{os.path.splitext(arquivo)[0]}_pag{i+1}.pdf"
                        novo_caminho = os.path.join(base_img_dir, novo_nome)
                        with open(novo_caminho, "wb") as f_out:
                            writer.write(f_out)
                    deletar_original = True
                else:
                    deletar_original = False
                
                if deletar_original:
                    os.remove(caminho) # Remove o original após fatiar
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao fatiar {arquivo}: {e}"))
                
        # Lista atualizada de arquivos na pasta principal (após o fatiamento)
        arquivos = [f for f in os.listdir(base_img_dir) if os.path.isfile(os.path.join(base_img_dir, f))]
        
        if not arquivos:
            self.stdout.write(self.style.SUCCESS("Nenhum arquivo solto para processar."))
            return

        sucesso = 0
        falha = 0

        for arquivo in arquivos:
            caminho_arquivo = os.path.join(base_img_dir, arquivo)
            extensao = arquivo.lower().split('.')[-1]
            texto_extraido = ""

            self.stdout.write(f"Processando {arquivo}...")

            try:
                if extensao == 'pdf':
                    with pdfplumber.open(caminho_arquivo) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                texto_extraido += text + "\n"
                elif extensao in ['jpg', 'jpeg', 'png']:
                    texto_extraido = pytesseract.image_to_string(Image.open(caminho_arquivo))
                else:
                    self.stdout.write(self.style.WARNING(f"Extensão não suportada ({extensao}). Movendo para revisão."))
                    self.mover_para_revisao(caminho_arquivo, revisao_dir, arquivo)
                    falha += 1
                    continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao ler {arquivo}: {e}"))
                self.mover_para_revisao(caminho_arquivo, revisao_dir, arquivo)
                falha += 1
                continue
                
            texto_limpo = self.limpar_texto(texto_extraido)
            if not texto_limpo:
                self.stdout.write(self.style.WARNING(f"Nenhum texto extraído de {arquivo}. Movendo para revisão."))
                self.mover_para_revisao(caminho_arquivo, revisao_dir, arquivo)
                falha += 1
                continue

            # Buscar correspondência
            dupla_encontrada = None
            for dupla in duplas_pendentes:
                nome1 = self.limpar_texto(dupla.nome_jogador1) if dupla.nome_jogador1 else ""
                nome2 = self.limpar_texto(dupla.nome_jogador2) if dupla.nome_jogador2 else ""
                
                # Checagem flexível: exige pelo menos primeiro e último nome, ou o nome completo
                if self.nome_combina(nome1, texto_limpo) or self.nome_combina(nome2, texto_limpo):
                    dupla_encontrada = dupla
                    break
            
            if dupla_encontrada:
                meta = self.extrair_metadados(texto_extraido)
                # Vincula e atualiza
                dupla_encontrada.status_pagamento = 'Confirmado'
                if meta['data']: dupla_encontrada.data_pagamento = meta['data']
                if meta['banco']: dupla_encontrada.banco_comprovante = meta['banco']
                if meta['documento']: dupla_encontrada.documento_comprovante = meta['documento']
                dupla_encontrada.pagador_comprovante = dupla_encontrada.nome_jogador1 # A heurística apenas confirmou o nome do jogador
                
                # Move e renomeia para a pasta media com o ID
                novo_nome = f"comprovante_{dupla_encontrada.id}.{extensao}"
                destino_media = os.path.join(media_comprovantes_dir, novo_nome)
                if os.path.exists(destino_media):
                    os.remove(destino_media)
                shutil.move(caminho_arquivo, destino_media)
                
                dupla_encontrada.comprovante = f'comprovantes-pagamento/{novo_nome}'
                dupla_encontrada.save()
                
                self.stdout.write(self.style.SUCCESS(f"-> VINCULADO a dupla ID {dupla_encontrada.id} ({dupla_encontrada.nome_jogador1})"))
                sucesso += 1
            else:
                self.stdout.write(self.style.WARNING(f"-> Sem correspondência. Movendo {arquivo} para revisão."))
                self.mover_para_revisao(caminho_arquivo, revisao_dir, arquivo)
                falha += 1

        self.stdout.write(self.style.SUCCESS(f"\nResumo: {sucesso} vinculados com sucesso, {falha} movidos para revisão manual."))

    def extrair_metadados(self, texto):
        meta = {'data': None, 'banco': None, 'documento': None}
        
        # 1. Data (DD/MM/YYYY)
        match_data = re.search(r'\b(\d{2})[/.-](\d{2})[/.-](\d{4})\b', texto)
        if match_data:
            try:
                dia, mes, ano = match_data.groups()
                meta['data'] = f"{ano}-{mes}-{dia}"
            except:
                pass
                
        # 2. Banco
        bancos = [
            'Nubank', 'Itaú', 'Itau', 'Bradesco', 'Santander', 'Banco do Brasil', 
            'Caixa', 'CEF', 'Inter', 'C6', 'PagSeguro', 'Mercado Pago', 'PicPay', 
            'Sicredi', 'Sicoob', 'BTG', 'Safra', 'Votorantim', 'Original', 'Cora', 'Neon'
        ]
        texto_lower = texto.lower()
        for banco in bancos:
            if banco.lower() in texto_lower:
                meta['banco'] = banco
                break
                
        # 3. Documento / Transação
        match_doc = re.search(r'(?i)(?:id(?:\s+da\s+transa[çc][ãa]o)?|transa[çc][ãa]o|controle|autentica[çc][ãa]o|documento)\s*[:\-]?\s*([A-Za-z0-9]{10,})', texto)
        if match_doc:
            meta['documento'] = match_doc.group(1)
            
        return meta

    def limpar_texto(self, texto):
        if not texto:
            return ""
        return unidecode.unidecode(texto).lower().replace('\n', ' ').strip()

    def nome_combina(self, nome, texto_ocr):
        if not nome:
            return False
        # Remove conectivos
        partes = [p for p in nome.split() if p not in ['da', 'de', 'do', 'das', 'dos']]
        if len(partes) >= 2:
            # Pelo menos primeiro e último nome
            primeiro = partes[0]
            ultimo = partes[-1]
            if (primeiro in texto_ocr) and (ultimo in texto_ocr):
                return True
        elif len(partes) == 1:
            if partes[0] in texto_ocr:
                return True
        return False

    def mover_para_revisao(self, origem, pasta_destino, arquivo):
        destino = os.path.join(pasta_destino, arquivo)
        # Se já existir um arquivo com mesmo nome na revisão, pode sobrescrever ou ignorar
        # O ideal seria renomear, mas vamos apenas sobreescrever por simplicidade
        if os.path.exists(destino):
            os.remove(destino)
        shutil.move(origem, destino)
