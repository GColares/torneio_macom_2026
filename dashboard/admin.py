from django.contrib import admin
from .models import Dupla, Potencia, Comprovante, FichaInscricao, Arbitro, Mesa, FilaEspera, Confronto

@admin.register(Dupla)
class DuplaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'credenciamento', 'status_inscricao', 'purgado', 'loja_jogador1', 'potencia_jogador1', 'status_pagamento')
    list_filter = ('status_inscricao', 'purgado', 'status_pagamento', 'potencia_jogador1', 'potencia_jogador2')
    search_fields = ('nome_jogador1', 'nome_jogador2', 'loja_jogador1', 'loja_jogador2')
    list_editable = ('credenciamento', 'status_pagamento', 'status_inscricao')

@admin.register(Potencia)
class PotenciaAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'sigla', 'meta_inscricoes')
    list_editable = ('meta_inscricoes',)

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'arbitro')
    list_editable = ('arbitro',)

@admin.register(FilaEspera)
class FilaEsperaAdmin(admin.ModelAdmin):
    list_display = ('dupla', 'posicao', 'data_entrada')
    list_editable = ('posicao',)

@admin.register(Confronto)
class ConfrontoAdmin(admin.ModelAdmin):
    list_display = ('numero_jogo', 'mesa', 'dupla_a', 'dupla_b', 'pontos_a', 'pontos_b', 'gato_a', 'gato_b', 'get_vencedor', 'status')
    list_filter = ('status', 'mesa')
    search_fields = ('dupla_a__credenciamento', 'dupla_b__credenciamento', 'dupla_a__nome_jogador1', 'dupla_b__nome_jogador1')
    list_editable = ('pontos_a', 'pontos_b', 'gato_a', 'gato_b', 'status')
    ordering = ('-numero_jogo',)

    def get_vencedor(self, obj):
        if obj.gato_a:
            return f"🏆 {obj.dupla_b} (Por Gato)"
        if obj.gato_b:
            return f"🏆 {obj.dupla_a} (Por Gato)"
        if obj.pontos_a is not None and obj.pontos_b is not None:
            if obj.pontos_a > obj.pontos_b:
                return f"🏆 {obj.dupla_a}"
            elif obj.pontos_b > obj.pontos_a:
                return f"🏆 {obj.dupla_b}"
            return "Empate"
        return "-"
    get_vencedor.short_description = "Vencedor"

admin.site.register(Arbitro)
admin.site.register(Comprovante)
admin.site.register(FichaInscricao)
