from django.db import models

class Dupla(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmado', 'Confirmado'),
    ]

    STATUS_INSCRICAO_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Validada', 'Validada'),
        ('Inscrita', 'Inscrita'),
        ('Cancelada', 'Cancelada'),
        ('Teste', 'Teste'),
        ('Impugnada', 'Impugnada'),
        ('Eliminada', 'Eliminada'),
    ]
    status_inscricao = models.CharField(
        'Status da Inscrição',
        max_length=20,
        choices=STATUS_INSCRICAO_CHOICES,
        default='Pendente'
    )
    purgado = models.BooleanField('Registro Purgado?', default=False, help_text='Marcado quando o usuário deleta a inscrição na UI')
    origem = models.CharField(
        'Origem da Inscrição',
        max_length=50,
        choices=[('Eletrônico', 'Eletrônico (Google Forms)'), ('Manual', 'Ficha Manual (Física)')],
        default='Eletrônico'
    )
    data_hora = models.CharField('Data da Inscrição', max_length=100, blank=True, null=True)
    credenciamento = models.IntegerField('Nº Credenciamento', null=True, blank=True, help_text='Número físico dado à dupla na entrada do evento')
    
    nome_jogador1 = models.CharField(max_length=200, verbose_name="Nome J1")
    apelido_jogador1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apelido J1")
    cim_jogador1 = models.CharField(max_length=50, blank=True, null=True, verbose_name="CIM J1")
    idade_jogador1 = models.PositiveIntegerField('Idade J1', blank=True, null=True)
    profissao_jogador1 = models.CharField('Profissão J1', max_length=150, blank=True, null=True)
    telefone_jogador1 = models.CharField('Telefone J1', max_length=20, blank=True, null=True)
    email_jogador1 = models.EmailField('E-mail J1', blank=True, null=True)
    potencia_jogador1 = models.ForeignKey('Potencia', on_delete=models.SET_NULL, null=True, blank=True, related_name='jogadores1')
    loja_jogador1 = models.CharField('Loja Jogador 1', max_length=200, blank=True, null=True)
    
    nome_jogador2 = models.CharField('Nome Jogador 2', max_length=200, blank=True, null=True)
    apelido_jogador2 = models.CharField('Apelido J2', max_length=100, blank=True, null=True)
    cim_jogador2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="CIM J2")
    idade_jogador2 = models.PositiveIntegerField('Idade J2', blank=True, null=True)
    profissao_jogador2 = models.CharField('Profissão J2', max_length=150, blank=True, null=True)
    telefone_jogador2 = models.CharField('Telefone J2', max_length=20, blank=True, null=True)
    email_jogador2 = models.EmailField('E-mail J2', blank=True, null=True)
    potencia_jogador2 = models.ForeignKey('Potencia', on_delete=models.SET_NULL, null=True, blank=True, related_name='jogadores2')
    loja_jogador2 = models.CharField('Loja Jogador 2', max_length=200, blank=True, null=True)
    
    acompanhantes_j1_adultos = models.PositiveIntegerField('Adultos J1', default=0)
    acompanhantes_j1_criancas = models.PositiveIntegerField('Crianças J1', default=0)
    acompanhantes_j2_adultos = models.PositiveIntegerField('Adultos J2', default=0)
    acompanhantes_j2_criancas = models.PositiveIntegerField('Crianças J2', default=0)
    
    status_pagamento = models.CharField(
        'Status do Pagamento',
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='Pendente'
    )
    comprovante = models.OneToOneField('Comprovante', on_delete=models.SET_NULL, null=True, blank=True, related_name='dupla')
    ficha_inscricao = models.OneToOneField('FichaInscricao', on_delete=models.SET_NULL, null=True, blank=True, related_name='dupla')

    class Meta:
        verbose_name = 'Dupla'
        verbose_name_plural = 'Duplas'
        unique_together = ('nome_jogador1', 'nome_jogador2', 'data_hora')


    @property
    def codigo_exibicao(self):
        return self.credenciamento if self.credenciamento else self.id

    def __str__(self):
        j2 = self.nome_jogador2 if self.nome_jogador2 else "Sem parceiro"
        return f"{self.nome_jogador1} & {j2}"

import os
from django.utils import timezone

def upload_comprovante_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'arquivadas/comprovantes-pagamento/comprovante_{timezone.now().strftime("%Y%m%d_%H%M%S")}{ext}'

def upload_ficha_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'arquivadas/inscricoes-manuais/ficha_{timezone.now().strftime("%Y%m%d_%H%M%S")}{ext}'

class Comprovante(models.Model):
    TIPO_CHOICES = [
        ('BANCARIO', 'Comprovante Bancário'),
        ('RECIBO', 'Recibo Sistêmico'),
    ]
    tipo = models.CharField('Tipo de Registro', max_length=20, choices=TIPO_CHOICES, default='BANCARIO')
    arquivo = models.FileField('Arquivo do Comprovante', upload_to=upload_comprovante_path, null=True, blank=True)
    pagador = models.CharField('Nome do Pagador', max_length=300, blank=True, null=True)
    banco = models.CharField('Banco', max_length=200, blank=True, null=True)
    valor = models.DecimalField('Valor Declarado', max_digits=10, decimal_places=2, blank=True, null=True)
    identificador = models.CharField('ID da Transação', max_length=200, blank=True, null=True)
    data_hora = models.DateTimeField('Data e Hora do Pagamento')
    data_upload = models.DateTimeField(auto_now_add=True)

class FichaInscricao(models.Model):
    arquivo = models.FileField('Ficha Digitalizada', upload_to=upload_ficha_path)
    data_upload = models.DateTimeField(auto_now_add=True)

class Potencia(models.Model):
    nome_completo = models.CharField('Nome Completo', max_length=200, unique=True)
    sigla = models.CharField('Sigla', max_length=50, unique=True)
    meta_inscricoes = models.PositiveIntegerField('Meta de Inscrições', default=0)

    class Meta:
        verbose_name = 'Potência'
        verbose_name_plural = 'Potências'


    @property
    def codigo_exibicao(self):
        return self.credenciamento if self.credenciamento else self.id

    def __str__(self):
        return self.sigla

class Arbitro(models.Model):
    nome = models.CharField('Nome', max_length=200)

    class Meta:
        verbose_name = 'Árbitro'
        verbose_name_plural = 'Árbitros'


    @property
    def codigo_exibicao(self):
        return self.credenciamento if self.credenciamento else self.id

    def __str__(self):
        return self.nome

class Mesa(models.Model):
    numero = models.PositiveIntegerField('Número da Mesa', unique=True)
    arbitro = models.ForeignKey(Arbitro, on_delete=models.SET_NULL, null=True, blank=True, related_name='mesas')

    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'


    @property
    def codigo_exibicao(self):
        return self.credenciamento if self.credenciamento else self.id

    def __str__(self):
        return f"Mesa {self.numero}"

class FilaEspera(models.Model):
    dupla = models.OneToOneField(Dupla, on_delete=models.CASCADE, related_name='fila')
    posicao = models.PositiveIntegerField('Posição na Fila')
    data_entrada = models.DateTimeField('Data/Hora de Entrada', auto_now_add=True)

    class Meta:
        verbose_name = 'Fila de Espera'
        verbose_name_plural = 'Fila de Espera'
        ordering = ['posicao', 'data_entrada']


    @property
    def codigo_exibicao(self):
        return self.credenciamento if self.credenciamento else self.id

    def __str__(self):
        return f"{self.posicao}º - {self.dupla}"

class Confronto(models.Model):
    STATUS_CHOICES = [
        ('Em Andamento', 'Em Andamento'),
        ('Finalizado', 'Finalizado'),
    ]

    numero_jogo = models.AutoField('Número do Jogo', primary_key=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, related_name='confrontos')
    dupla_a = models.ForeignKey(Dupla, on_delete=models.CASCADE, related_name='confrontos_como_a')
    dupla_b = models.ForeignKey(Dupla, on_delete=models.CASCADE, related_name='confrontos_como_b')
    
    pontos_a = models.PositiveIntegerField('Pontos Dupla A', blank=True, null=True)
    pontos_b = models.IntegerField('Pontos B', null=True, blank=True)
    gato_a = models.BooleanField('Infração Gato (A)', default=False)
    gato_b = models.BooleanField('Infração Gato (B)', default=False)
    
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='Em Andamento')
    
    data_inicio = models.DateTimeField('Início', auto_now_add=True)
    data_fim = models.DateTimeField('Fim', blank=True, null=True)

    class Meta:
        verbose_name = 'Confronto'
        verbose_name_plural = 'Confrontos'


    @property
    def codigo_exibicao(self):
        return self.credenciamento if self.credenciamento else self.id

    def __str__(self):
        return f"Jogo #{self.numero_jogo} - {self.dupla_a} vs {self.dupla_b}"
