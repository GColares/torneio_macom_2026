from django.contrib import admin
from .models import Dupla, MetaPotencia

@admin.register(Dupla)
class DuplaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'valido', 'purgado', 'loja_jogador1', 'potencia_jogador1', 'status_pagamento')
    list_filter = ('valido', 'purgado', 'status_pagamento', 'potencia_jogador1', 'potencia_jogador2')
    search_fields = ('nome_jogador1', 'nome_jogador2', 'loja_jogador1')
    list_editable = ('status_pagamento', 'valido')

@admin.register(MetaPotencia)
class MetaPotenciaAdmin(admin.ModelAdmin):
    list_display = ('potencia', 'meta_quantidade')
    list_editable = ('meta_quantidade',)
