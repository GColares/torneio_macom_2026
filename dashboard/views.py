from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Dupla, Potencia, Mesa, FilaEspera, Partida
import os
import json
from datetime import date

def index(request):
    return render(request, 'index.html')

def api_metrics(request):
    duplas = Dupla.objects.filter(valido=True, purgado=False)
    total_duplas = duplas.count()
    
    confirmados = 0
    confirmados_manual = 0
    confirmados_eletronico = 0
    pendentes = 0
    total_eletronico = 0
    total_manual = 0
    
    # Garantir que as três potências sempre apareçam nos relatórios
    potencia_count = {
        'Grande Loja Maçônica do Amazonas (GLOMAM)': 0,
        'Grande Oriente do Brasil – Amazonas (GOB-AM)': 0,
        'Grande Oriente Amazonense (GOA)': 0
    }
    
    tabela_duplas = {}
    tabela_jogadores = {}
    
    for obj in duplas:
        if obj.origem == 'Manual':
            total_manual += 1
            if obj.status_pagamento == 'Confirmado':
                confirmados_manual += 1
        else:
            total_eletronico += 1
            if obj.status_pagamento == 'Confirmado':
                confirmados_eletronico += 1
                
        if obj.status_pagamento == 'Confirmado':
            confirmados += 1
        else:
            pendentes += 1
            
        pot1 = obj.potencia_jogador1.nome_completo if obj.potencia_jogador1 else 'Não Informado'
        pot2 = obj.potencia_jogador2.nome_completo if obj.potencia_jogador2 else 'Não Informado'
        loja_base = obj.loja_jogador1.strip() if obj.loja_jogador1 else 'Não Informado'
        
        if not pot1: pot1 = 'Não Informado'
        if not pot2: pot2 = 'Não Informado'
        if not loja_base: loja_base = 'Não Informado'
        
        potencia_count[pot1] = potencia_count.get(pot1, 0) + 1
            
        # Tabela 1: Inscrições (Duplas) por loja e potencia (usando J1)
        chave_dupla = f"{loja_base} - {pot1}"
        if chave_dupla not in tabela_duplas:
            tabela_duplas[chave_dupla] = {'loja': loja_base, 'potencia': pot1, 'quantidade': 0}
        tabela_duplas[chave_dupla]['quantidade'] += 1
        
        # Tabela 2: Lista Nominal (Agrupada por Loja e Potência do J1)
        chave_j1 = f"{loja_base} - {pot1}"
        if chave_j1 not in tabela_jogadores:
            tabela_jogadores[chave_j1] = {'loja': loja_base, 'potencia': pot1, 'quantidade': 0, 'nomes_duplas': []}
        
        tabela_jogadores[chave_j1]['quantidade'] += 1
        nome2_fmt = obj.nome_jogador2 if (obj.nome_jogador2 and obj.nome_jogador2.strip()) else 'Sem parceiro'
        tabela_jogadores[chave_j1]['nomes_duplas'].append(f"{obj.nome_jogador1} & {nome2_fmt}")

    if not potencia_count and total_duplas > 0:
        potencia_count = {"Não Informado": total_duplas}

    metas = []
    for m in Potencia.objects.all():
        metas.append({
            'potencia': m.nome_completo,
            'meta': m.meta_inscricoes
        })

    # Ordenação: Primeiro por Potência, depois por Loja
    lista_duplas = sorted(list(tabela_duplas.values()), key=lambda x: (x['potencia'], x['loja']))
    lista_jogadores = sorted(list(tabela_jogadores.values()), key=lambda x: (x['potencia'], x['loja']))

    return JsonResponse({
        "file_name": "Banco de Dados (Filtro Testes: ON)",
        "total": total_duplas,
        "total_manual": total_manual,
        "total_eletronico": total_eletronico,
        "confirmados": confirmados,
        "confirmados_manual": confirmados_manual,
        "confirmados_eletronico": confirmados_eletronico,
        "pendentes": pendentes,
        "potencia": potencia_count,
        "metas": metas,
        "tabela_duplas": lista_duplas,
        "tabela_jogadores": lista_jogadores
    })

def gestao(request):
    duplas = Dupla.objects.filter(purgado=False).order_by('-id')
    
    q = request.GET.get('q', '').strip()
    if q:
        duplas = duplas.filter(
            Q(nome_jogador1__icontains=q) | 
            Q(nome_jogador2__icontains=q) |
            Q(loja_jogador1__icontains=q)
        )
        
    status = request.GET.get('status', '')
    if status:
        duplas = duplas.filter(status_pagamento=status)
        
    potencia_id = request.GET.get('potencia', '')
    if potencia_id:
        duplas = duplas.filter(potencia_jogador1__id=potencia_id)
        
    origem = request.GET.get('origem', '')
    if origem:
        duplas = duplas.filter(origem__icontains=origem)
        
    potencias = Potencia.objects.all()
    
    context = {
        'duplas': duplas,
        'potencias': potencias,
        'q': q,
        'status_filter': status,
        'potencia_filter': potencia_id,
        'origem_filter': origem
    }
    return render(request, 'gestao.html', context)

def revisao_pagamentos(request):
    """Página para tratamento manual de comprovantes não identificados automaticamente."""
    pasta_revisao = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static', 'img', 'comprovantes-pagamento', 'revisao-pendente'
    )
    extensoes = {'.pdf', '.jpg', '.jpeg', '.png'}
    arquivos = []
    if os.path.exists(pasta_revisao):
        for f in sorted(os.listdir(pasta_revisao)):
            if os.path.splitext(f)[1].lower() in extensoes:
                arquivos.append(f)

    duplas_pendentes = Dupla.objects.filter(
        status_pagamento='Pendente', valido=True, purgado=False
    ).order_by('nome_jogador1')

    context = {
        'arquivos': arquivos,
        'duplas_pendentes': duplas_pendentes,
        'total_revisao': len(arquivos),
    }
    return render(request, 'revisao_pagamentos.html', context)

@csrf_exempt
@require_POST
def api_confirmar_revisao(request):
    """Vincula um comprovante da pasta revisao-pendente a uma dupla e confirma o pagamento."""
    try:
        data = json.loads(request.body)
        dupla_id = data.get('dupla_id')
        arquivo = data.get('arquivo')
        data_pgto = data.get('data_pagamento', str(date.today()))

        if not dupla_id or not arquivo:
            return JsonResponse({'ok': False, 'erro': 'dupla_id e arquivo são obrigatórios.'}, status=400)

        dupla = Dupla.objects.get(id=dupla_id)

        # Caminho da pasta revisão
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_revisao = os.path.join(base_dir, 'static', 'img', 'comprovantes-pagamento', 'revisao-pendente')
        pasta_confirmados = os.path.join(base_dir, 'static', 'img', 'comprovantes-pagamento')

        origem = os.path.join(pasta_revisao, arquivo)
        destino = os.path.join(pasta_confirmados, arquivo)

        if not os.path.exists(origem):
            return JsonResponse({'ok': False, 'erro': f'Arquivo não encontrado: {arquivo}'}, status=404)

        # Mover para a pasta principal de comprovantes
        os.rename(origem, destino)

        # Atualizar dupla
        dupla.status_pagamento = 'Confirmado'
        dupla.comprovante = f'comprovantes-pagamento/{arquivo}'
        dupla.pagador_comprovante   = data.get('pagador', '').strip() or None
        dupla.banco_comprovante     = data.get('banco', '').strip() or None
        dupla.documento_comprovante = data.get('documento', '').strip() or None
        try:
            dupla.data_pagamento = date.fromisoformat(data_pgto)
        except Exception:
            dupla.data_pagamento = date.today()
        dupla.save()

        return JsonResponse({
            'ok': True,
            'mensagem': f'Pagamento de {dupla.nome_jogador1} confirmado com sucesso!',
            'dupla_id': dupla.id,
            'arquivo': arquivo,
        })

    except Dupla.DoesNotExist:
        return JsonResponse({'ok': False, 'erro': 'Dupla não encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_descartar_revisao(request):
    """Move arquivo de revisão para uma subpasta 'descartados' sem vincular a nenhuma dupla."""
    try:
        data = json.loads(request.body)
        arquivo = data.get('arquivo')
        if not arquivo:
            return JsonResponse({'ok': False, 'erro': 'arquivo é obrigatório.'}, status=400)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_revisao = os.path.join(base_dir, 'static', 'img', 'comprovantes-pagamento', 'revisao-pendente')
        pasta_descartados = os.path.join(pasta_revisao, 'descartados')
        os.makedirs(pasta_descartados, exist_ok=True)

        origem = os.path.join(pasta_revisao, arquivo)
        destino = os.path.join(pasta_descartados, arquivo)

        if not os.path.exists(origem):
            return JsonResponse({'ok': False, 'erro': f'Arquivo não encontrado: {arquivo}'}, status=404)

        os.rename(origem, destino)
        return JsonResponse({'ok': True, 'mensagem': f'{arquivo} descartado.'})

    except Exception as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=500)

def api_duplas(request):
    duplas = Dupla.objects.filter(purgado=False).order_by('-id')
    data = []
    for d in duplas:
        data.append({
            'id': d.id,
            'j1': d.nome_jogador1,
            'j2': d.nome_jogador2,
            'loja': d.loja_jogador1,
            'potencia': d.potencia_jogador1.nome_completo if d.potencia_jogador1 else '',
            'valido': d.valido,
            'status_pagamento': d.status_pagamento,
            'data_hora': d.data_hora,
            'origem': d.origem
        })
    return JsonResponse({'duplas': data})

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_get_dupla(request, dupla_id):
    try:
        d = Dupla.objects.get(id=dupla_id)
        data = {
            'id': d.id,
            'nome_jogador1': d.nome_jogador1,
            'apelido_jogador1': d.apelido_jogador1 or '',
            'cim_jogador1': d.cim_jogador1 or '',
            'idade_jogador1': d.idade_jogador1 or '',
            'profissao_jogador1': d.profissao_jogador1 or '',
            'telefone_jogador1': d.telefone_jogador1 or '',
            'email_jogador1': d.email_jogador1 or '',
            'loja_jogador1': d.loja_jogador1 or '',
            'potencia_jogador1_id': d.potencia_jogador1.id if d.potencia_jogador1 else '',
            
            'nome_jogador2': d.nome_jogador2 or '',
            'apelido_jogador2': d.apelido_jogador2 or '',
            'cim_jogador2': d.cim_jogador2 or '',
            'idade_jogador2': d.idade_jogador2 or '',
            'profissao_jogador2': d.profissao_jogador2 or '',
            'telefone_jogador2': d.telefone_jogador2 or '',
            'email_jogador2': d.email_jogador2 or '',
            'loja_jogador2': d.loja_jogador2 or '',
            'potencia_jogador2_id': d.potencia_jogador2.id if d.potencia_jogador2 else '',
            
            'acompanhantes_adultos': d.acompanhantes_adultos or 0,
            'acompanhantes_criancas': d.acompanhantes_criancas or 0,
            
            'origem': d.origem,
            'valido': d.valido,
            'status_pagamento': d.status_pagamento,
            'comprovante_url': d.comprovante.url if d.comprovante else '',
            'data_pagamento': d.data_pagamento.strftime('%Y-%m-%d') if d.data_pagamento else '',
            'pagador_comprovante': d.pagador_comprovante or '',
            'banco_comprovante': d.banco_comprovante or '',
            'documento_comprovante': d.documento_comprovante or '',
        }
        return JsonResponse({'success': True, 'dupla': data})
    except Dupla.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Dupla não encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def api_update_dupla(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.POST.dict()

            dupla = Dupla.objects.get(id=body['id'])
            
            if 'valido' in body:
                valido_val = body['valido']
                if isinstance(valido_val, str):
                    dupla.valido = (valido_val.lower() == 'true')
                else:
                    dupla.valido = bool(valido_val)
                    
            if 'status_pagamento' in body:
                dupla.status_pagamento = body['status_pagamento']
                
            if 'nome_jogador1' in body: dupla.nome_jogador1 = body['nome_jogador1']
            if 'apelido_jogador1' in body: dupla.apelido_jogador1 = body['apelido_jogador1']
            if 'cim_jogador1' in body: dupla.cim_jogador1 = body['cim_jogador1']
            if 'idade_jogador1' in body: dupla.idade_jogador1 = body['idade_jogador1'] if str(body['idade_jogador1']).strip() else None
            if 'profissao_jogador1' in body: dupla.profissao_jogador1 = body['profissao_jogador1']
            if 'telefone_jogador1' in body: dupla.telefone_jogador1 = body['telefone_jogador1']
            if 'email_jogador1' in body: dupla.email_jogador1 = body['email_jogador1']
            if 'loja_jogador1' in body: dupla.loja_jogador1 = body['loja_jogador1']
            if 'potencia_jogador1_id' in body:
                pot_id = body['potencia_jogador1_id']
                dupla.potencia_jogador1 = Potencia.objects.get(id=pot_id) if pot_id else None
                
            if 'nome_jogador2' in body: dupla.nome_jogador2 = body['nome_jogador2']
            if 'apelido_jogador2' in body: dupla.apelido_jogador2 = body['apelido_jogador2']
            if 'cim_jogador2' in body: dupla.cim_jogador2 = body['cim_jogador2']
            if 'idade_jogador2' in body: dupla.idade_jogador2 = body['idade_jogador2'] if str(body['idade_jogador2']).strip() else None
            if 'profissao_jogador2' in body: dupla.profissao_jogador2 = body['profissao_jogador2']
            if 'telefone_jogador2' in body: dupla.telefone_jogador2 = body['telefone_jogador2']
            if 'email_jogador2' in body: dupla.email_jogador2 = body['email_jogador2']
            if 'loja_jogador2' in body: dupla.loja_jogador2 = body['loja_jogador2']
            if 'potencia_jogador2_id' in body:
                pot_id = body['potencia_jogador2_id']
                dupla.potencia_jogador2 = Potencia.objects.get(id=pot_id) if pot_id else None
                
            if 'acompanhantes_adultos' in body: dupla.acompanhantes_adultos = body['acompanhantes_adultos'] or 0
            if 'acompanhantes_criancas' in body: dupla.acompanhantes_criancas = body['acompanhantes_criancas'] or 0
                
            if 'origem' in body: dupla.origem = body['origem']
            
            if 'data_pagamento' in body:
                if body['data_pagamento']:
                    try:
                        dupla.data_pagamento = date.fromisoformat(body['data_pagamento'])
                    except Exception:
                        pass
                else:
                    dupla.data_pagamento = None
            if 'pagador_comprovante' in body: dupla.pagador_comprovante = body['pagador_comprovante']
            if 'banco_comprovante' in body: dupla.banco_comprovante = body['banco_comprovante']
            if 'documento_comprovante' in body: dupla.documento_comprovante = body['documento_comprovante']
            
            if request.FILES.get('comprovante'):
                dupla.comprovante = request.FILES['comprovante']

            dupla.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@csrf_exempt
def api_delete_duplas(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            ids = body.get('ids', [])
            Dupla.objects.filter(id__in=ids).update(purgado=True)
            return JsonResponse({'success': True, 'deleted': len(ids)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@csrf_exempt
def api_metas(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            action = body.get('action')
            if action == 'delete':
                Potencia.objects.filter(id=body['id']).delete()
            else:
                potencia = body.get('potencia')
                meta_quantidade = int(body.get('meta_quantidade', 0))
                # Tentativa de atualizar caso exista, mas o formulário atual manda o nome_completo em 'potencia'
                obj, created = Potencia.objects.get_or_create(nome_completo=potencia, defaults={'sigla': potencia[:50], 'meta_inscricoes': meta_quantidade})
                if not created:
                    obj.meta_inscricoes = meta_quantidade
                    obj.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    metas = [{'id': m.id, 'potencia': m.nome_completo, 'meta': m.meta_inscricoes} for m in Potencia.objects.all()]
    return JsonResponse({'metas': metas})

from .models import Mesa, FilaEspera, Partida

def torneio_view(request):
    return render(request, 'torneio.html')

@csrf_exempt
def api_torneio_state(request):
    # Garante a existência de 16 mesas
    if Mesa.objects.count() < 16:
        for i in range(1, 17):
            Mesa.objects.get_or_create(numero=i)
            
    if request.method == 'POST':
        # Aqui ficará a lógica de iniciar partida, encerrar partida, etc.
        pass
        
    mesas = []
    for m in Mesa.objects.all().order_by('numero'):
        # Verifica se tem partida ativa na mesa
        partida = Partida.objects.filter(mesa=m, data_fim__isnull=True).last()
        partida_data = None
        if partida:
            partida_data = {
                'id': partida.id,
                'dupla_a': str(partida.dupla_a),
                'dupla_b': str(partida.dupla_b),
                'inicio': partida.data_inicio.isoformat()
            }
            
        mesas.append({
            'id': m.id,
            'numero': m.numero,
            'ocupada': m.ocupada,
            'partida': partida_data
        })
        
    fila = []
    for f in FilaEspera.objects.all().order_by('posicao'):
        fila.append({
            'posicao': f.posicao,
            'dupla': str(f.dupla),
            'dupla_id': f.dupla.id
        })
        
    return JsonResponse({
        'mesas': mesas,
        'fila': fila
    })
import csv
import os

@csrf_exempt
def api_sync_csv(request):
    if request.method == 'POST':
        from django.conf import settings
        csv_path = os.path.join(settings.BASE_DIR, 'Inscrição no evento', 'Inscrição no evento.csv')
        if not os.path.exists(csv_path):
            return JsonResponse({'success': False, 'error': 'Arquivo CSV no encontrado no caminho esperado.'})
        
        inserted_count = 0
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Pula o cabe�alho
                
                for row in reader:
                    if not row or not row[1].strip():
                        continue
                        
                    nome_j1 = row[1].strip()
                    nome_j2 = row[13].strip() if len(row) > 13 else ''
                    
                    # Deduplica��o (verifica se j� existe dupla com mesmos nomes)
                    if Dupla.objects.filter(nome_jogador1=nome_j1, nome_jogador2=nome_j2).exists():
                        continue
                    
                    # Extra��o dos acompanhantes
                    acomp_j1_ad = int(row[11]) if len(row) > 11 and row[11].strip().isdigit() else 0
                    acomp_j1_cr = int(row[12]) if len(row) > 12 and row[12].strip().isdigit() else 0
                    acomp_j2_ad = int(row[23]) if len(row) > 23 and row[23].strip().isdigit() else 0
                    acomp_j2_cr = int(row[24]) if len(row) > 24 and row[24].strip().isdigit() else 0
                    
                    # Idades
                    idade_j1 = int(row[4]) if len(row) > 4 and row[4].strip().isdigit() else None
                    idade_j2 = int(row[16]) if len(row) > 16 and row[16].strip().isdigit() else None
                    
                    # Tratamento de Pot�ncia (Match aproximado pelo nome)
                    pot1_str = row[9].strip() if len(row) > 9 else ''
                    pot2_str = row[21].strip() if len(row) > 21 else ''
                    
                    pot1_obj = None
                    pot2_obj = None
                    if pot1_str:
                        for p in Potencia.objects.all():
                            if p.nome_completo in pot1_str or p.sigla in pot1_str:
                                pot1_obj = p
                                break
                    if pot2_str:
                        for p in Potencia.objects.all():
                            if p.nome_completo in pot2_str or p.sigla in pot2_str:
                                pot2_obj = p
                                break
                                
                    Dupla.objects.create(
                        origem='Eletrônico',
                        valido=False,
                        status_pagamento='Pendente',
                        
                        nome_jogador1=nome_j1,
                        apelido_jogador1=row[2].strip() if len(row) > 2 else '',
                        cim_jogador1=row[3].strip() if len(row) > 3 else '',
                        idade_jogador1=idade_j1,
                        profissao_jogador1=row[5].strip() if len(row) > 5 else '',
                        telefone_jogador1=row[6].strip() if len(row) > 6 else '',
                        email_jogador1=row[7].strip() if len(row) > 7 else '',
                        loja_jogador1=row[8].strip() if len(row) > 8 else '',
                        potencia_jogador1=pot1_obj,
                        
                        nome_jogador2=nome_j2,
                        apelido_jogador2=row[14].strip() if len(row) > 14 else '',
                        cim_jogador2=row[15].strip() if len(row) > 15 else '',
                        idade_jogador2=idade_j2,
                        profissao_jogador2=row[17].strip() if len(row) > 17 else '',
                        telefone_jogador2=row[18].strip() if len(row) > 18 else '',
                        email_jogador2=row[19].strip() if len(row) > 19 else '',
                        loja_jogador2=row[20].strip() if len(row) > 20 else '',
                        potencia_jogador2=pot2_obj,
                        
                        acompanhantes_adultos=acomp_j1_ad + acomp_j2_ad,
                        acompanhantes_criancas=acomp_j1_cr + acomp_j2_cr,
                    )
                    inserted_count += 1
                    
            return JsonResponse({'success': True, 'inserted': inserted_count})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})
