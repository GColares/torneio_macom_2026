---
name: comando-placar
description: Rotina para o comando /placar que processa novas pastas de súmulas usando o Vision.
---
# Comando: /placar

Sempre que o usuário digitar `placar` ou `/placar`, você deve executar esta rotina.

## Objetivo
Verificar o diretório `resultados/`, identificar **quaisquer novas imagens de súmulas adicionadas** (processamento incremental/tempo real), informar ao usuário, e lançá-las no banco. **Você NÃO deve esperar que uma rodada esteja completa (todas as mesas terminarem) para processar os arquivos.**

## Conceito de "Rodada" (Ciclos de Atualização)
* As pastas nomeadas como `rodada X` servem **apenas para controle de ciclos de atualização (batches)** da organização, e não representam uma rodada cronológica rígida.
* É perfeitamente normal e esperado que uma mesma dupla tenha **múltiplas súmulas** inseridas dentro da mesma pasta de rodada (ex: jogos atrasados sendo entregues junto com jogos atuais). 
* Você deve processar todos os confrontos identificados na pasta de forma independente, sem achar que há um conflito cronológico apenas porque a dupla jogou duas vezes na mesma "rodada".

## Nomenclatura dos Arquivos

* **Padrão:** O usuário nomeará as imagens no formato `{mesa}{rodada}` (ex: `11.jpeg` = Mesa 1, Rodada 1).
* **Súmulas Suspeitas (Quarentena):** Arquivos nomeados com uma letra repetida (ex: `xx.jpeg`, `yy.jpeg`) indicam súmulas com suspeita de erro do árbitro.
  * **REGRA:** Estas súmulas suspeitas **NÃO devem ser processadas nem inseridas no placar**.
  * **REGRA:** Ao final da execução do comando, você **DEVE listar** essas súmulas na sua resposta para que o usuário não as perca de vista e averigue posteriormente.

## Passos

1.  **Listar Diretórios:** Liste as pastas dentro de `resultados/` (ex: `rodada 1`, `rodada 2 e 3`).
2.  **Informar Status Inicial:** Liste os novos arquivos encontrados. Avise ao usuário que fará a leitura do que está disponível até o momento.
    *   Exemplo de fala: *"Até agora só temos o resultado da Rodada 1. Localizei a pasta `rodada 2 e 3` e vou fazer a leitura das novas súmulas!"*
3.  **Ler Súmulas:** Faça a leitura das novas imagens adicionadas e as converta em registros no banco. (Lembre-se de pular as súmulas suspeitas como `xx.jpeg`).
    *   O script deve usar o prompt para extrair: `mesa`, `jogo`, `da` (Dupla A), `db` (Dupla B), `pa` (Pontos A), `pb` (Pontos B), `ga` (Gato A), `gb` (Gato B).
    *   Deduplicar e proteger contra injeção dupla.
4.  **Confirmar:** Após o processamento, resuma para o usuário quantas partidas foram processadas, **liste explicitamente os arquivos suspeitos (ex: `xx.jpeg`) que ficaram de quarentena**, e peça para ele conferir o Telão.
