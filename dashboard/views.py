from django.shortcuts import render
from django.http import JsonResponse
from .models import Dupla, MetaPotencia

def index(request):
    return render(request, 'index.html')

def api_metrics(request):
    duplas = Dupla.objects.filter(valido=True, purgado=False)
    total_duplas = duplas.count()
    
    confirmados = 0
    pendentes = 0
    
    # Garantir que as três potências sempre apareçam nos relatórios
    potencia_count = {
        'Grande Loja Maçônica do Amazonas (GLOMAM)': 0,
        'Grande Oriente do Brasil – Amazonas (GOB-AM)': 0,
        'Grande Oriente Amazonense (GOA)': 0
    }
    
    tabela_duplas = {}
    tabela_jogadores = {}
    
    for obj in duplas:
        if obj.status_pagamento == 'Confirmado':
            confirmados += 1
        else:
            pendentes += 1
            
        pot1 = obj.potencia_jogador1.strip() if obj.potencia_jogador1 else 'Não Informado'
        pot2 = obj.potencia_jogador2.strip() if obj.potencia_jogador2 else 'Não Informado'
        loja_base = obj.loja_jogador1.strip() if obj.loja_jogador1 else 'Não Informado'
        
        if not pot1: pot1 = 'Não Informado'
        if not pot2: pot2 = 'Não Informado'
        if not loja_base: loja_base = 'Não Informado'
        
        potencia_count[pot1] = potencia_count.get(pot1, 0) + 1
        if obj.nome_jogador2 and obj.nome_jogador2.strip():
            potencia_count[pot2] = potencia_count.get(pot2, 0) + 1
            
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
    for m in MetaPotencia.objects.all():
        metas.append({
            'potencia': m.potencia,
            'meta': m.meta_quantidade
        })

    # Ordenação: Primeiro por Potência, depois por Loja
    lista_duplas = sorted(list(tabela_duplas.values()), key=lambda x: (x['potencia'], x['loja']))
    lista_jogadores = sorted(list(tabela_jogadores.values()), key=lambda x: (x['potencia'], x['loja']))

    return JsonResponse({
        "file_name": "Banco de Dados (Filtro Testes: ON)",
        "total": total_duplas,
        "confirmados": confirmados,
        "pendentes": pendentes,
        "potencia": potencia_count,
        "metas": metas,
        "tabela_duplas": lista_duplas,
        "tabela_jogadores": lista_jogadores
    })

def gestao(request):
    return render(request, 'gestao.html')

def api_duplas(request):
    duplas = Dupla.objects.filter(purgado=False).order_by('-id')
    data = []
    for d in duplas:
        data.append({
            'id': d.id,
            'j1': d.nome_jogador1,
            'j2': d.nome_jogador2,
            'loja': d.loja_jogador1,
            'potencia': d.potencia_jogador1,
            'valido': d.valido,
            'status_pagamento': d.status_pagamento,
            'data_hora': d.data_hora
        })
    return JsonResponse({'duplas': data})

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_update_dupla(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            dupla = Dupla.objects.get(id=body['id'])
            if 'valido' in body:
                dupla.valido = body['valido']
            if 'status_pagamento' in body:
                dupla.status_pagamento = body['status_pagamento']
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
                MetaPotencia.objects.filter(id=body['id']).delete()
            else:
                potencia = body.get('potencia')
                meta_quantidade = int(body.get('meta_quantidade', 0))
                obj, created = MetaPotencia.objects.get_or_create(potencia=potencia, defaults={'meta_quantidade': meta_quantidade})
                if not created:
                    obj.meta_quantidade = meta_quantidade
                    obj.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    metas = [{'id': m.id, 'potencia': m.potencia, 'meta': m.meta_quantidade} for m in MetaPotencia.objects.all()]
    return JsonResponse({'metas': metas})
