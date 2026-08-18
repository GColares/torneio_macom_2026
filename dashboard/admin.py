from django.contrib import admin
from .models import Dupla, Potencia, Mesa, FilaEspera, Partida

@admin.register(Dupla)
class DuplaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status_inscricao', 'purgado', 'loja_jogador1', 'potencia_jogador1', 'status_pagamento')
    list_filter = ('status_inscricao', 'purgado', 'status_pagamento', 'potencia_jogador1', 'potencia_jogador2')
    search_fields = ('nome_jogador1', 'nome_jogador2', 'loja_jogador1', 'loja_jogador2')
    list_editable = ('status_pagamento', 'status_inscricao')

@admin.register(Potencia)
class PotenciaAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'sigla', 'meta_inscricoes')
    list_editable = ('meta_inscricoes',)

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'ocupada')
    list_editable = ('ocupada',)

@admin.register(FilaEspera)
class FilaEsperaAdmin(admin.ModelAdmin):
    list_display = ('dupla', 'posicao', 'data_entrada')
    list_editable = ('posicao',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'dupla_a', 'dupla_b', 'vencedor', 'tipo_vitoria', 'data_inicio')
    list_filter = ('tipo_vitoria',)
