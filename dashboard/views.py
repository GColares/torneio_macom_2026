from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Dupla, Potencia, Mesa, FilaEspera, Partida
import os
import json
from datetime import date, datetime

def index(request):
    return render(request, 'index.html')

def api_metrics(request):
    duplas = Dupla.objects.filter(purgado=False).exclude(status_inscricao__in=['Cancelada', 'Eliminada', 'Impugnada', 'Teste'])
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


    from django.db.models import Q
    from .models import Comprovante, FichaInscricao
    
    # ---------------------------------------------------------
    # MÉTRICAS DA TRÍADE DE ENTIDADES (Regra de Negócio)
    # ---------------------------------------------------------
    todas_duplas = Dupla.objects.filter(purgado=False)
    
    # Comprovantes
    total_comprovantes = Comprovante.objects.count()
    comprovantes_vinculados = Comprovante.objects.filter(dupla__isnull=False).count()
    comprovantes_orfaos = Comprovante.objects.filter(dupla__isnull=True).count()
    
    # Fichas (Físicas/Manuais)
    total_fichas = FichaInscricao.objects.count()
    fichas_vinculadas = FichaInscricao.objects.filter(dupla__isnull=False).count()
    fichas_orfaos = FichaInscricao.objects.filter(dupla__isnull=True).count()
    
    # Inscrições (Duplas)
    duplas_total = todas_duplas.count()
    duplas_sem_comprovante = todas_duplas.filter(comprovante__isnull=True).count()
    duplas_manuais_sem_ficha = todas_duplas.filter(origem='Manual', ficha_inscricao__isnull=True).count()
    
    # Completas = tem comprovante E (se for manual, tem que ter ficha)
    duplas_completas = todas_duplas.exclude(
        Q(comprovante__isnull=True) | 
        Q(origem='Manual', ficha_inscricao__isnull=True)
    ).count()

    triade_metrics = {
        'comprovantes': {'total': total_comprovantes, 'vinculados': comprovantes_vinculados, 'orfaos': comprovantes_orfaos},
        'fichas': {'total': total_fichas, 'vinculados': fichas_vinculadas, 'orfaos': fichas_orfaos},
        'duplas': {'total': duplas_total, 'sem_comprovante': duplas_sem_comprovante, 'manuais_sem_ficha': duplas_manuais_sem_ficha, 'completas': duplas_completas}
    }
    # ---------------------------------------------------------

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
        "triade": triade_metrics,
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
    from django.db.models import F

    duplas = Dupla.objects.filter(purgado=False).order_by(F('comprovante__data_hora').asc(nulls_last=True), 'id')
    
    # Calcula o ranking absoluto (Número da Dupla) ignorando filtros do painel
    rank_dict = {}
    rank = 1
    for d in duplas:
        if d.comprovante_id and d.comprovante.data_hora:
            rank_dict[d.id] = rank
            rank += 1

    
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
    

    # Injeta o número calculado em cada objeto (avalia a queryset)
    duplas_list = list(duplas)
    for d in duplas_list:
        d.numero = rank_dict.get(d.id, None)

    context = {
        'duplas': duplas_list,

        'potencias': potencias,
        'q': q,
        'status_filter': status,
        'potencia_filter': potencia_id,
        'origem_filter': origem
    }
    return render(request, 'gestao.html', context)


def gestao_comprovantes(request):
    """Painel Central de Comprovantes."""
    from .models import Comprovante, Dupla
    comprovantes = Comprovante.objects.all().order_by('-data_hora')
    duplas = Dupla.objects.filter(purgado=False).order_by('id')
    return render(request, 'gestao_comprovantes.html', {'comprovantes': comprovantes, 'duplas': duplas})

def gestao_fichas(request):
    """Painel Central de Fichas Digitais."""
    from .models import FichaInscricao, Potencia
    fichas = FichaInscricao.objects.all().order_by('-id')
    potencias = Potencia.objects.all()
    return render(request, 'gestao_fichas.html', {'fichas': fichas, 'potencias': potencias})


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
            return JsonResponse({
        'ok': False, 'erro': 'dupla_id e arquivo são obrigatórios.'}, status=400)

        dupla = Dupla.objects.get(id=dupla_id)

        # Caminho da pasta revisão
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_revisao = os.path.join(base_dir, 'media', 'entradas', 'comprovantes-pagamento', 'revisao-pendente')
        pasta_confirmados = os.path.join(base_dir, 'media', 'arquivadas', 'comprovantes-pagamento')

        origem = os.path.join(pasta_revisao, arquivo)
        destino = os.path.join(pasta_confirmados, arquivo)

        if not os.path.exists(origem):
            return JsonResponse({
        'ok': False, 'erro': f'Arquivo não encontrado: {arquivo}'}, status=404)

        # Mover para a pasta principal de comprovantes
        os.rename(origem, destino)

        # Atualizar dupla e criar comprovante
        from .models import Comprovante
        from django.utils import timezone
        
        c = dupla.comprovante
        if not c:
            c = Comprovante()
            
        c.arquivo.name = f'arquivadas/comprovantes-pagamento/{arquivo}'
        c.pagador = data.get('pagador', '').strip() or None
        c.banco = data.get('banco', '').strip() or None
        c.identificador = data.get('documento', '').strip() or None
        
        try:
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(data_pgto)
            if not parsed:
                from datetime import date
                parsed = date.fromisoformat(data_pgto)
            c.data_hora = parsed
        except Exception:
            c.data_hora = timezone.now()
            
        c.save()
        
        dupla.status_pagamento = 'Confirmado'
        dupla.comprovante = c
        dupla.save()

        return JsonResponse({
        'ok': True,
            'mensagem': f'Pagamento de {dupla.nome_jogador1} confirmado com sucesso!',
            'dupla_id': dupla.id,
            'arquivo': arquivo,
        })

    except Dupla.DoesNotExist:
        return JsonResponse({
        'ok': False, 'erro': 'Dupla não encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({
        'ok': False, 'erro': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_descartar_revisao(request):
    """Move arquivo de revisão para uma subpasta 'descartados' sem vincular a nenhuma dupla."""
    try:
        data = json.loads(request.body)
        arquivo = data.get('arquivo')
        if not arquivo:
            return JsonResponse({
        'ok': False, 'erro': 'arquivo é obrigatório.'}, status=400)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_revisao = os.path.join(base_dir, 'media', 'entradas', 'comprovantes-pagamento', 'revisao-pendente')
        pasta_descartados = os.path.join(pasta_revisao, 'descartados')
        os.makedirs(pasta_descartados, exist_ok=True)

        origem = os.path.join(pasta_revisao, arquivo)
        destino = os.path.join(pasta_descartados, arquivo)

        if not os.path.exists(origem):
            return JsonResponse({
        'ok': False, 'erro': f'Arquivo não encontrado: {arquivo}'}, status=404)

        os.rename(origem, destino)
        return JsonResponse({
        'ok': True, 'mensagem': f'{arquivo} descartado.'})

    except Exception as e:
        return JsonResponse({
        'ok': False, 'erro': str(e)}, status=500)

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
            'status_inscricao': d.status_inscricao,
            'status_pagamento': d.status_pagamento,
            'data_hora': d.data_hora,
            'origem': d.origem
        })
    return JsonResponse({
        'duplas': data})

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
            
            'acompanhantes_j1_adultos': d.acompanhantes_j1_adultos or 0, 'acompanhantes_j2_adultos': d.acompanhantes_j2_adultos or 0,
            'acompanhantes_j1_criancas': d.acompanhantes_j1_criancas or 0, 'acompanhantes_j2_criancas': d.acompanhantes_j2_criancas or 0,
            
            'origem': d.origem,
            'status_inscricao': d.status_inscricao,
            'status_pagamento': d.status_pagamento,
            'comprovante_url': d.comprovante.arquivo.url if d.comprovante and d.comprovante.arquivo else '',
            'ficha_url': d.ficha_inscricao.arquivo.url if d.ficha_inscricao and d.ficha_inscricao.arquivo else '',
            'data_pagamento': __import__('django').utils.timezone.localtime(d.comprovante.data_hora).strftime('%Y-%m-%dT%H:%M:%S') if d.comprovante and d.comprovante.data_hora else '',
            'pagador_comprovante': d.comprovante.pagador if d.comprovante else '',
            'banco_comprovante': d.comprovante.banco if d.comprovante else '',
            'documento_comprovante': d.comprovante.identificador if d.comprovante else '',
        }
        return JsonResponse({
        'success': True, 'dupla': data})
    except Dupla.DoesNotExist:
        return JsonResponse({
        'success': False, 'error': 'Dupla não encontrada'})
    except Exception as e:
        return JsonResponse({
        'success': False, 'error': str(e)})

@csrf_exempt
def api_update_dupla(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.POST.dict()

            dupla = Dupla.objects.get(id=body['id'])
            
            if 'status_inscricao' in body:
                dupla.status_inscricao = body['status_inscricao']
                    
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
                
            if 'acompanhantes_j1_adultos' in body: dupla.acompanhantes_j1_adultos = body['acompanhantes_j1_adultos'] or 0
            if 'acompanhantes_j1_criancas' in body: dupla.acompanhantes_j1_criancas = body['acompanhantes_j1_criancas'] or 0
            if 'acompanhantes_j2_adultos' in body: dupla.acompanhantes_j2_adultos = body['acompanhantes_j2_adultos'] or 0
            if 'acompanhantes_j2_criancas' in body: dupla.acompanhantes_j2_criancas = body['acompanhantes_j2_criancas'] or 0
                
            if 'origem' in body: dupla.origem = body['origem']
            
            if 'data_pagamento' in body or 'pagador_comprovante' in body or 'banco_comprovante' in body or 'documento_comprovante' in body or request.FILES.get('comprovante'):
                from .models import Comprovante
                from django.utils import timezone
                if not dupla.comprovante:
                    c = Comprovante(data_hora=timezone.now())
                    c.save()
                    dupla.comprovante = c

                if 'data_pagamento' in body and body['data_pagamento']:
                    try:
                        from django.utils.dateparse import parse_datetime
                        parsed = parse_datetime(body['data_pagamento'])
                        if not parsed:
                            from datetime import date
                            parsed = date.fromisoformat(body['data_pagamento'])
                        dupla.comprovante.data_hora = parsed
                    except Exception:
                        pass
                
                if 'pagador_comprovante' in body: dupla.comprovante.pagador = body['pagador_comprovante']
                if 'banco_comprovante' in body: dupla.comprovante.banco = body['banco_comprovante']
                if 'documento_comprovante' in body: dupla.comprovante.identificador = body['documento_comprovante']
                
                if request.FILES.get('comprovante'):
                    dupla.comprovante.arquivo = request.FILES['comprovante']
                
                dupla.comprovante.save()

            if request.FILES.get('ficha_inscricao'):
                from .models import FichaInscricao
                if not dupla.ficha_inscricao:
                    dupla.ficha_inscricao = FichaInscricao.objects.create()
                dupla.ficha_inscricao.arquivo = request.FILES['ficha_inscricao']
                dupla.ficha_inscricao.save()
            if dupla.status_inscricao == 'Cancelada':
                dupla.comprovante = None
                dupla.ficha_inscricao = None
                dupla.status_pagamento = 'Pendente'

            dupla.save()
            return JsonResponse({
        'success': True})
        except Exception as e:
            return JsonResponse({
        'success': False, 'error': str(e)})
    return JsonResponse({
        'success': False})

@csrf_exempt
def api_delete_duplas(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            ids = body.get('ids', [])
            Dupla.objects.filter(id__in=ids).update(
                purgado=True,
                comprovante=None,
                ficha_inscricao=None,
                status_pagamento='Pendente'
            )
            return JsonResponse({
        'success': True, 'deleted': len(ids)})
        except Exception as e:
            return JsonResponse({
        'success': False, 'error': str(e)})
    return JsonResponse({
        'success': False})

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
            return JsonResponse({
        'success': True})
        except Exception as e:
            return JsonResponse({
        'success': False, 'error': str(e)})
            
    metas = [{'id': m.id, 'potencia': m.nome_completo, 'meta': m.meta_inscricoes} for m in Potencia.objects.all()]
    return JsonResponse({
        'metas': metas})

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
            return JsonResponse({
        'success': False, 'error': 'Arquivo CSV no encontrado no caminho esperado.'})
        
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
                        status_inscricao='Pendente',
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
                        
                        acompanhantes_j1_adultos=acomp_j1_ad, acompanhantes_j2_adultos=acomp_j2_ad,
                        acompanhantes_j1_criancas=acomp_j1_cr, acompanhantes_j2_criancas=acomp_j2_cr,
                    )
                    inserted_count += 1
                    
            return JsonResponse({
        'success': True, 'inserted': inserted_count})
        except Exception as e:
            return JsonResponse({
        'success': False, 'error': str(e)})
    return JsonResponse({
        'success': False})

@csrf_exempt
def api_update_comprovante(request):
    """Atualiza os dados de um comprovante e ajusta o seu vínculo com a dupla."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comp_id = data.get('id')
            if not comp_id:
                return JsonResponse({'status': 'error', 'message': 'ID do comprovante não fornecido'}, status=400)
                
            from .models import Comprovante, Dupla
            comp = Comprovante.objects.get(id=comp_id)
            
            # Atualiza dados básicos
            if 'valor' in data:
                val_str = str(data['valor']).strip()
                if val_str:
                    comp.valor = val_str.replace(',', '.')
                else:
                    comp.valor = None
            if 'banco' in data: comp.banco = data['banco']
            if 'pagador' in data: comp.pagador = data['pagador']
            if 'identificador' in data: comp.identificador = data['identificador']
            if 'data_hora' in data and data['data_hora']:
                from django.utils.dateparse import parse_datetime
                parsed_dt = parse_datetime(data['data_hora'])
                if parsed_dt:
                    comp.data_hora = parsed_dt
            comp.save()

            # Lida com o vínculo
            novo_dupla_id = data.get('dupla_id')
            
            # Se já tinha dupla antes, precisamos ver se mudou
            try:
                dupla_antiga = comp.dupla
            except:
                dupla_antiga = None
                
            if str(novo_dupla_id).strip():
                try:
                    dupla_nova = Dupla.objects.get(id=novo_dupla_id)
                    if dupla_antiga and dupla_antiga.id != dupla_nova.id:
                        # Desvincula a antiga
                        dupla_antiga.comprovante = None
                        dupla_antiga.status_pagamento = 'Pendente'
                        dupla_antiga.save()
                    # Vincula a nova (fica como Pendente até que confirmem, a não ser que queiram validar na hora)
                    dupla_nova.comprovante = comp
                    dupla_nova.save()
                except Dupla.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Dupla informada não existe.'}, status=404)
            else:
                # Foi enviado em branco, então desvincula se houver
                if dupla_antiga:
                    dupla_antiga.comprovante = None
                    dupla_antiga.status_pagamento = 'Pendente'
                    dupla_antiga.save()
                    
            # Se houver dupla vinculada (antiga ou nova), atualiza os status
            try:
                dupla_atual = comp.dupla
                if 'status_pagamento' in data: dupla_atual.status_pagamento = data['status_pagamento']
                if 'status_inscricao' in data: dupla_atual.status_inscricao = data['status_inscricao']
                dupla_atual.save()
            except:
                pass

            return JsonResponse({'status': 'success', 'message': 'Comprovante atualizado.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def api_update_ficha(request):
    """Atualiza o vínculo da ficha física com a dupla e os dados da dupla em si."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ficha_id = data.get('id')
            if not ficha_id:
                return JsonResponse({'status': 'error', 'message': 'ID da ficha não fornecido'}, status=400)
                
            from .models import FichaInscricao, Dupla, Potencia
            ficha = FichaInscricao.objects.get(id=ficha_id)

            novo_dupla_id = data.get('dupla_id')
            
            try:
                dupla_antiga = ficha.dupla
            except:
                dupla_antiga = None
                
            dupla_alvo = None
            if str(novo_dupla_id).strip():
                try:
                    dupla_nova = Dupla.objects.get(id=novo_dupla_id)
                    if dupla_antiga and dupla_antiga.id != dupla_nova.id:
                        dupla_antiga.ficha_inscricao = None
                        if dupla_antiga.status_inscricao == 'Validada':
                            dupla_antiga.status_inscricao = 'Pendente Ficha'
                        dupla_antiga.save()
                    dupla_nova.ficha_inscricao = ficha
                    dupla_nova.save()
                    dupla_alvo = dupla_nova
                except Dupla.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Dupla informada não existe.'}, status=404)
            else:
                if dupla_antiga:
                    dupla_antiga.ficha_inscricao = None
                    if dupla_antiga.status_inscricao == 'Validada':
                        dupla_antiga.status_inscricao = 'Pendente Ficha'
                    dupla_antiga.save()

            # Update all fields if a dupla is linked
            if dupla_alvo:
                if 'j1_nome' in data: dupla_alvo.nome_jogador1 = data['j1_nome']
                if 'j1_apelido' in data: dupla_alvo.apelido_jogador1 = data['j1_apelido']
                if 'j1_cim' in data: dupla_alvo.cim_jogador1 = data['j1_cim']
                if 'j1_idade' in data: dupla_alvo.idade_jogador1 = data['j1_idade'] if str(data['j1_idade']).strip() else None
                if 'j1_profissao' in data: dupla_alvo.profissao_jogador1 = data['j1_profissao']
                if 'j1_loja' in data: dupla_alvo.loja_jogador1 = data['j1_loja']
                if 'j1_potencia' in data: 
                    pid = str(data['j1_potencia']).strip()
                    dupla_alvo.potencia_jogador1_id = pid if pid else None
                if 'j1_cel' in data: dupla_alvo.telefone_jogador1 = data['j1_cel']
                if 'j1_email' in data: dupla_alvo.email_jogador1 = data['j1_email']

                if 'j2_nome' in data: dupla_alvo.nome_jogador2 = data['j2_nome']
                if 'j2_apelido' in data: dupla_alvo.apelido_jogador2 = data['j2_apelido']
                if 'j2_cim' in data: dupla_alvo.cim_jogador2 = data['j2_cim']
                if 'j2_idade' in data: dupla_alvo.idade_jogador2 = data['j2_idade'] if str(data['j2_idade']).strip() else None
                if 'j2_profissao' in data: dupla_alvo.profissao_jogador2 = data['j2_profissao']
                if 'j2_loja' in data: dupla_alvo.loja_jogador2 = data['j2_loja']
                if 'j2_potencia' in data:
                    pid = str(data['j2_potencia']).strip()
                    dupla_alvo.potencia_jogador2_id = pid if pid else None
                if 'j2_cel' in data: dupla_alvo.telefone_jogador2 = data['j2_cel']
                if 'j2_email' in data: dupla_alvo.email_jogador2 = data['j2_email']

                if 'acomp_j1_adultos' in data: dupla_alvo.acompanhantes_j1_adultos = int(data['acomp_j1_adultos'] or 0)
                if 'acomp_j1_criancas' in data: dupla_alvo.acompanhantes_j1_criancas = int(data['acomp_j1_criancas'] or 0)
                if 'acomp_j2_adultos' in data: dupla_alvo.acompanhantes_j2_adultos = int(data['acomp_j2_adultos'] or 0)
                if 'acomp_j2_criancas' in data: dupla_alvo.acompanhantes_j2_criancas = int(data['acomp_j2_criancas'] or 0)

                dupla_alvo.save()

            return JsonResponse({'status': 'success', 'message': 'Ficha atualizada.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)


@csrf_exempt
def api_criar_comprovante(request):
    """Cria um novo comprovante manualmente através da UI."""
    if request.method == 'POST':
        try:
            from .models import Comprovante
            from datetime import datetime
            
            tipo = request.POST.get('tipo', 'BANCARIO')
            arquivo = request.FILES.get('arquivo')
            
            if tipo == 'BANCARIO' and not arquivo:
                return JsonResponse({'status': 'error', 'message': 'Arquivo não enviado para Comprovante Bancário.'}, status=400)
            
            pagador = request.POST.get('pagador', '').strip()
            valor_str = request.POST.get('valor', '').strip()
            
            if tipo == 'RECIBO' and (not pagador or not valor_str):
                return JsonResponse({'status': 'error', 'message': 'Pagador e Valor são obrigatórios para Recibos Sistêmicos.'}, status=400)
            
            data_hora_str = request.POST.get('data_hora')
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            
            data_hora = parse_datetime(data_hora_str) if data_hora_str else None
            if not data_hora:
                data_hora = timezone.now()
                
            valor_str = request.POST.get('valor', '').strip()
            valor = valor_str.replace(',', '.') if valor_str else None
                
            c = Comprovante(
                tipo=tipo,
                arquivo=arquivo,
                pagador=pagador,
                banco=request.POST.get('banco', ''),
                valor=valor,
                identificador=request.POST.get('identificador', ''),
                data_hora=data_hora
            )
            c.save()

            # Lógica aprendida (/learn): Vincular à dupla e renomear fisicamente para 'arquivadas'
            from .models import Dupla
            dupla_id = request.POST.get('dupla_id')
            if dupla_id and str(dupla_id).isdigit():
                try:
                    dupla = Dupla.objects.get(id=int(dupla_id))
                    dupla.comprovante = c
                    dupla.save()
                except Dupla.DoesNotExist:
                    pass

            import os
            from django.conf import settings
            
            # Recarrega a dupla vinculada (se houver) pelo related_name, se dupla.save() tiver funcionado
            dupla_vinculada = getattr(c, 'dupla', None)
            
            if c.arquivo:
                # Onde o Django salvou originalmente (upload_to padrão)
                caminho_original = c.arquivo.path
                if os.path.exists(caminho_original):
                    extensao = os.path.splitext(caminho_original)[1]
                    timestamp_str = data_hora.strftime("%Y%m%d_%H%M%S")
                    
                    if dupla_vinculada:
                        novo_nome = f'comprovante_dupla_{dupla_vinculada.id}_{timestamp_str}{extensao}'
                    else:
                        novo_nome = f'comprovante_orfao_{timestamp_str}{extensao}'
                        
                    # Pasta destino
                    pasta_arquivadas = os.path.join(settings.MEDIA_ROOT, 'arquivadas', 'comprovantes-pagamento')
                    os.makedirs(pasta_arquivadas, exist_ok=True)
                    
                    novo_caminho_fisico = os.path.join(pasta_arquivadas, novo_nome)
                    
                    # Move o arquivo fisicamente
                    os.rename(caminho_original, novo_caminho_fisico)
                    
                    # Atualiza o caminho no banco de dados (relativo ao MEDIA_ROOT)
                    # No Windows/Linux manter as barras com /
                    c.arquivo.name = f'arquivadas/comprovantes-pagamento/{novo_nome}'
                    c.save(update_fields=['arquivo'])

            return JsonResponse({'status': 'success', 'message': 'Comprovante criado com sucesso.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def api_delete_comprovante(request):
    """Deleta um comprovante e desvincula a dupla (se houver)."""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            comp_id = data.get('id')
            if not comp_id:
                return JsonResponse({'status': 'error', 'message': 'ID do comprovante não fornecido'}, status=400)
                
            from .models import Comprovante, Dupla
            comp = Comprovante.objects.get(id=comp_id)
            
            try:
                dupla = comp.dupla
                if dupla:
                    dupla.status_pagamento = 'Pendente'
                    dupla.save()
            except:
                pass
                
            if comp.arquivo:
                import os
                if os.path.isfile(comp.arquivo.path):
                    os.remove(comp.arquivo.path)
                    
            comp.delete()
            return JsonResponse({'status': 'success', 'message': 'Comprovante deletado com sucesso.'})
        except Comprovante.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Comprovante não encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)


def relatorios(request):
    """Painel de Relatórios para impressão e exportação."""
    from .models import Dupla
    duplas = Dupla.objects.filter(purgado=False).select_related('potencia_jogador1').order_by('potencia_jogador1__nome_completo', 'nome_jogador1')
    
    agrupamento = request.GET.get('agrupamento', 'geral') # geral, potencia, loja
    status = request.GET.get('status', 'todos')
    
    if status == 'confirmados':
        duplas = duplas.filter(status_pagamento='Confirmado')
    elif status == 'pendentes':
        duplas = duplas.filter(status_pagamento='Pendente')

    # Calcula o rank/ordem de quem já pagou, igual na tela de gestão
    duplas_todas = Dupla.objects.filter(purgado=False).order_by('comprovante__data_hora')
    rank_dict = {}
    rank = 1
    for d in duplas_todas:
        if d.comprovante_id and d.comprovante.data_hora:
            rank_dict[d.id] = rank
            rank += 1
            
    # Injeta o número calculado em cada objeto
    duplas_list = list(duplas)
    for d in duplas_list:
        d.numero = rank_dict.get(d.id, None)
        
    context = {
        'duplas': duplas_list,
        'agrupamento': agrupamento,
        'status': status
    }
    return render(request, 'relatorios.html', context)

@csrf_exempt
def api_excluir_dupla(request, dupla_id):
    if request.method == 'POST' or request.method == 'DELETE':
        from .models import Dupla
        try:
            d = Dupla.objects.get(id=dupla_id)
            d.purgado = True
            d.save(update_fields=['purgado'])
            return JsonResponse({'status': 'success', 'message': 'Dupla excluída com sucesso.'})
        except Dupla.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Dupla não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)

def api_get_comprovante(request, comp_id):
    try:
        from .models import Comprovante
        from django.utils import timezone
        c = Comprovante.objects.get(id=comp_id)
        data = {
            'id': c.id,
            'tipo': c.tipo,
            'valor': str(c.valor) if c.valor else '',
            'banco': c.banco or '',
            'pagador': c.pagador or '',
            'identificador': c.identificador or '',
            'data_hora': timezone.localtime(c.data_hora).strftime('%Y-%m-%dT%H:%M:%S') if c.data_hora else '',
            'arquivo_url': c.arquivo.url if c.arquivo else '',
            'dupla_id': c.dupla.id if hasattr(c, 'dupla') else '',
            'dupla_numero': getattr(c.dupla, 'numero', '') if hasattr(c, 'dupla') else '',
            'dupla_j1': c.dupla.nome_jogador1 if hasattr(c, 'dupla') else '',
            'dupla_j2': c.dupla.nome_jogador2 if hasattr(c, 'dupla') else '',
            'status_pagamento': c.dupla.status_pagamento if hasattr(c, 'dupla') else '',
            'status_inscricao': c.dupla.status_inscricao if hasattr(c, 'dupla') else '',
        }
        return JsonResponse({'success': True, 'comprovante': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
