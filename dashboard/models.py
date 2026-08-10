from django.db import models

class Dupla(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmado', 'Confirmado'),
    ]

    valido = models.BooleanField('Inscrição Válida?', default=True, help_text='Desmarque se for um teste')
    purgado = models.BooleanField('Registro Purgado?', default=False, help_text='Marcado quando o usuário deleta a inscrição na UI')
    data_hora = models.CharField('Data da Inscrição', max_length=100, blank=True, null=True)
    
    nome_jogador1 = models.CharField('Nome Jogador 1', max_length=200)
    potencia_jogador1 = models.CharField('Potência Jogador 1', max_length=100, blank=True, null=True)
    loja_jogador1 = models.CharField('Loja Jogador 1', max_length=200, blank=True, null=True)
    
    nome_jogador2 = models.CharField('Nome Jogador 2', max_length=200, blank=True, null=True)
    potencia_jogador2 = models.CharField('Potência Jogador 2', max_length=100, blank=True, null=True)
    loja_jogador2 = models.CharField('Loja Jogador 2', max_length=200, blank=True, null=True)
    
    status_pagamento = models.CharField(
        'Status do Pagamento',
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='Pendente'
    )

    class Meta:
        verbose_name = 'Dupla'
        verbose_name_plural = 'Duplas'
        unique_together = ('nome_jogador1', 'nome_jogador2', 'data_hora')

    def __str__(self):
        j2 = self.nome_jogador2 if self.nome_jogador2 else "Sem parceiro"
        return f"{self.nome_jogador1} & {j2}"

class MetaPotencia(models.Model):
    potencia = models.CharField('Potência', max_length=100, unique=True)
    meta_quantidade = models.PositiveIntegerField('Meta (Quantidade)', default=0)

    class Meta:
        verbose_name = 'Meta por Potência'
        verbose_name_plural = 'Metas por Potência'

    def __str__(self):
        return f"{self.potencia}: {self.meta_quantidade}"
