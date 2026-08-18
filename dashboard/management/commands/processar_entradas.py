import os
import fitz  # PyMuPDF
import json
import time
from datetime import datetime
from PIL import Image
import io
import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from dashboard.models import Dupla, Comprovante, FichaInscricao

class Command(BaseCommand):
    help = 'Processa as entradas de PDFs na pasta media/entradas usando o Gemini Vision'

    def handle(self, *args, **kwargs):
        # Carregar variáveis de ambiente do arquivo .env
        from dotenv import load_dotenv
        load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

        # Configurar Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('ERRO: Variável de ambiente GEMINI_API_KEY não encontrada. Processamento abortado.'))
            return
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')

        base_entradas = os.path.join(settings.MEDIA_ROOT, 'entradas')
        
        self.processar_fichas(os.path.join(base_entradas, 'inscricoes-manuais'), model)
        self.processar_comprovantes(os.path.join(base_entradas, 'comprovantes-pagamento'), model)
        
    def extract_data_from_image(self, model, image, tipo):
        prompt_ficha = """
Você é um leitor de dados. Extraia as seguintes informações desta imagem de Ficha de Inscrição Manual e retorne ESTRITAMENTE em formato JSON, sem crases de formatação markdown (sem ```json):
{
  "nome_jogador1": "Nome completo",
  "nome_jogador2": "Nome completo (ou vazio)",
  "loja": "Loja mencionada",
  "legivel": true
}
Se estiver impossível de ler os nomes, retorne "legivel": false.
"""
        prompt_comprovante = """
Você é um leitor de dados. Extraia as seguintes informações deste Comprovante de Pagamento e retorne ESTRITAMENTE em formato JSON, sem crases de formatação markdown:
{
  "pagador": "Nome de quem pagou/remetente",
  "banco": "Banco",
  "identificador": "Código de transação ou autenticação",
  "nome_jogador1": "Se houver o nome do inscrito na descrição/observação, preencha. Senão vazio",
  "legivel": true
}
Se estiver impossível de ler dados financeiros, retorne "legivel": false.
"""
        try:
            prompt = prompt_ficha if tipo == 'ficha' else prompt_comprovante
            response = model.generate_content([prompt, image])
            texto_limpo = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(texto_limpo)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro na extração LLM: {str(e)}'))
            return {"legivel": False}

    def processar_fichas(self, pasta_raiz, model):
        pasta_nao_processadas = os.path.join(pasta_raiz, 'nao-processadas')
        pasta_processadas = os.path.join(pasta_raiz, 'processadas')
        pasta_revisao = os.path.join(pasta_raiz, 'revisao-pendente')
        pasta_arquivadas = os.path.join(settings.MEDIA_ROOT, 'arquivadas', 'inscricoes-manuais')

        if not os.path.exists(pasta_nao_processadas):
            return

        for filename in os.listdir(pasta_nao_processadas):
            caminho_arquivo = os.path.join(pasta_nao_processadas, filename)
            ext = filename.lower().split('.')[-1]
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                continue

            self.stdout.write(self.style.NOTICE(f'Processando arquivo: {filename}'))
            
            try:
                sucesso_total = True
                
                if ext == 'pdf':
                    doc = fitz.open(caminho_arquivo)
                    for num_page in range(len(doc)):
                        pagina = doc.load_page(num_page)
                        pix = pagina.get_pixmap()
                        img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
                        
                        dados = self.extract_data_from_image(model, img, 'ficha')
                        
                        if not dados.get('legivel', False) or not dados.get('nome_jogador1'):
                            sucesso_total = False
                            self.stdout.write(self.style.WARNING(f' Página {num_page+1} ilegível ou sem J1.'))
                            continue

                        # Deduplicação e Criação da Dupla
                        nome1 = dados['nome_jogador1'].strip()
                        nome2 = dados.get('nome_jogador2', '').strip()
                        loja = dados.get('loja', '').strip()

                        dupla = Dupla.objects.filter(nome_jogador1__iexact=nome1).first()
                        if not dupla:
                            dupla = Dupla.objects.create(
                                nome_jogador1=nome1,
                                nome_jogador2=nome2,
                                loja_jogador1=loja,
                                origem='Manual'
                            )
                            self.stdout.write(self.style.SUCCESS(f'  [NOVA] Dupla criada: ID {dupla.id} - {nome1}'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'  [EXISTENTE] Dupla vinculada: ID {dupla.id} - {nome1}'))

                        # Salvar página individual
                        novo_pdf = fitz.open()
                        novo_pdf.insert_pdf(doc, from_page=num_page, to_page=num_page)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nome_fatiado = f'ficha_dupla_{dupla.id}_{timestamp}.pdf'
                        caminho_fatiado = os.path.join(pasta_arquivadas, nome_fatiado)
                        
                        novo_pdf.save(caminho_fatiado)
                        novo_pdf.close()

                        # Criar registro FichaInscricao
                        if not dupla.ficha_inscricao:
                            ficha_db = FichaInscricao.objects.create()
                            ficha_db.arquivo.name = f'arquivadas/inscricoes-manuais/{nome_fatiado}'
                            ficha_db.save()
                            dupla.ficha_inscricao = ficha_db
                            dupla.save()

                    doc.close()
                else:
                    # É imagem
                    with Image.open(caminho_arquivo) as img:
                        dados = self.extract_data_from_image(model, img, 'ficha')
                        
                        if not dados.get('legivel', False) or not dados.get('nome_jogador1'):
                            sucesso_total = False
                            self.stdout.write(self.style.WARNING(f' Imagem ilegível ou sem J1.'))
                        else:
                            # Deduplicação e Criação da Dupla
                            nome1 = dados['nome_jogador1'].strip()
                            nome2 = dados.get('nome_jogador2', '').strip()
                            loja = dados.get('loja', '').strip()

                            dupla = Dupla.objects.filter(nome_jogador1__iexact=nome1).first()
                            if not dupla:
                                dupla = Dupla.objects.create(
                                    nome_jogador1=nome1,
                                    nome_jogador2=nome2,
                                    loja_jogador1=loja,
                                    origem='Manual'
                                )
                                self.stdout.write(self.style.SUCCESS(f'  [NOVA] Dupla criada: ID {dupla.id} - {nome1}'))
                            else:
                                self.stdout.write(self.style.SUCCESS(f'  [EXISTENTE] Dupla vinculada: ID {dupla.id} - {nome1}'))

                            # Salvar a imagem original como anexo
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nome_fatiado = f'ficha_dupla_{dupla.id}_{timestamp}.{ext}'
                            caminho_fatiado = os.path.join(pasta_arquivadas, nome_fatiado)
                            
                            img.save(caminho_fatiado)

                            # Criar registro FichaInscricao
                            if not dupla.ficha_inscricao:
                                ficha_db = FichaInscricao.objects.create()
                                ficha_db.arquivo.name = f'arquivadas/inscricoes-manuais/{nome_fatiado}'
                                ficha_db.save()
                                dupla.ficha_inscricao = ficha_db
                                dupla.save()

                # Mover original
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                if sucesso_total:
                    novo_nome = f'lido_{timestamp_str}_{filename}'
                    os.rename(caminho_arquivo, os.path.join(pasta_processadas, novo_nome))
                else:
                    os.rename(caminho_arquivo, os.path.join(pasta_revisao, filename))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro fatal ao processar {filename}: {str(e)}'))
                # Mover para revisão
                os.rename(caminho_arquivo, os.path.join(pasta_revisao, filename))

    def processar_comprovantes(self, pasta_raiz, model):
        pasta_nao_processadas = os.path.join(pasta_raiz, 'nao-processadas')
        pasta_processadas = os.path.join(pasta_raiz, 'processadas')
        pasta_revisao = os.path.join(pasta_raiz, 'revisao-pendente')
        pasta_arquivadas = os.path.join(settings.MEDIA_ROOT, 'arquivadas', 'comprovantes-pagamento')

        if not os.path.exists(pasta_nao_processadas):
            return

        for filename in os.listdir(pasta_nao_processadas):
            caminho_arquivo = os.path.join(pasta_nao_processadas, filename)
            ext = filename.lower().split('.')[-1]
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                continue

            self.stdout.write(self.style.NOTICE(f'Processando arquivo: {filename}'))
            
            try:
                sucesso_total = True
                
                if ext == 'pdf':
                    doc = fitz.open(caminho_arquivo)
                    for num_page in range(len(doc)):
                        pagina = doc.load_page(num_page)
                        pix = pagina.get_pixmap()
                        img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
                        
                        dados = self.extract_data_from_image(model, img, 'comprovante')
                        
                        if not dados.get('legivel', False):
                            sucesso_total = False
                            self.stdout.write(self.style.WARNING(f' Página {num_page+1} do comprovante ilegível.'))
                            continue

                        # Tentativa de vincular a uma dupla pelo nome_jogador1 na observação do PIX
                        nome_obs = dados.get('nome_jogador1', '').strip()
                        dupla = None
                        if nome_obs:
                            dupla = Dupla.objects.filter(nome_jogador1__icontains=nome_obs).first()

                        if not dupla:
                            sucesso_total = False
                            self.stdout.write(self.style.WARNING(f'  Página {num_page+1}: Dupla não identificada a partir do pagador.'))
                            continue

                        self.stdout.write(self.style.SUCCESS(f'  [VINCULADO] Pagamento da Dupla: ID {dupla.id}'))

                        # Salvar página individual
                        novo_pdf = fitz.open()
                        novo_pdf.insert_pdf(doc, from_page=num_page, to_page=num_page)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nome_fatiado = f'comprovante_dupla_{dupla.id}_{timestamp}.pdf'
                        caminho_fatiado = os.path.join(pasta_arquivadas, nome_fatiado)
                        
                        novo_pdf.save(caminho_fatiado)
                        novo_pdf.close()

                        # Criar/Atualizar registro Comprovante
                        c = dupla.comprovante
                        if not c:
                            c = Comprovante()
                        
                        c.arquivo.name = f'arquivadas/comprovantes-pagamento/{nome_fatiado}'
                        c.pagador = dados.get('pagador', '')
                        c.banco = dados.get('banco', '')
                        c.identificador = dados.get('identificador', '')
                        c.data_hora = timezone.now()
                        c.save()
                        
                        dupla.comprovante = c
                        dupla.status_pagamento = 'Confirmado'
                        dupla.save()

                    doc.close()
                else:
                    # É imagem
                    with Image.open(caminho_arquivo) as img:
                        dados = self.extract_data_from_image(model, img, 'comprovante')
                        
                        if not dados.get('legivel', False):
                            sucesso_total = False
                            self.stdout.write(self.style.WARNING(f' Imagem do comprovante ilegível.'))
                        else:
                            nome_obs = dados.get('nome_jogador1', '').strip()
                            dupla = None
                            if nome_obs:
                                dupla = Dupla.objects.filter(nome_jogador1__icontains=nome_obs).first()

                            if not dupla:
                                sucesso_total = False
                                self.stdout.write(self.style.WARNING(f'  Imagem: Dupla não identificada a partir do pagador.'))
                            else:
                                self.stdout.write(self.style.SUCCESS(f'  [VINCULADO] Pagamento da Dupla: ID {dupla.id}'))

                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                nome_fatiado = f'comprovante_dupla_{dupla.id}_{timestamp}.{ext}'
                                caminho_fatiado = os.path.join(pasta_arquivadas, nome_fatiado)
                                
                                img.save(caminho_fatiado)

                                c = dupla.comprovante
                                if not c:
                                    c = Comprovante()
                                
                                c.arquivo.name = f'arquivadas/comprovantes-pagamento/{nome_fatiado}'
                                c.pagador = dados.get('pagador', '')
                                c.banco = dados.get('banco', '')
                                c.identificador = dados.get('identificador', '')
                                c.data_hora = timezone.now()
                                c.save()
                                
                                dupla.comprovante = c
                                dupla.status_pagamento = 'Confirmado'
                                dupla.save()

                # Mover original
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                if sucesso_total:
                    novo_nome = f'lido_{timestamp_str}_{filename}'
                    os.rename(caminho_arquivo, os.path.join(pasta_processadas, novo_nome))
                else:
                    # Vai para revisão-pendente (onde a view revisao_pagamentos vai ler)
                    os.rename(caminho_arquivo, os.path.join(pasta_revisao, filename))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro fatal ao processar {filename}: {str(e)}'))
                os.rename(caminho_arquivo, os.path.join(pasta_revisao, filename))
