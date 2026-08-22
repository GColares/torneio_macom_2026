---
name: comando-placar
description: Rotina para o comando /placar que processa novas pastas de súmulas usando o Vision.
---
# Comando: /placar

Sempre que o usuário digitar `placar` ou `/placar`, você deve executar esta rotina.

## Objetivo
Verificar o diretório `resultados/`, identificar pastas de rodadas que ainda não foram processadas, informar ao usuário o status do processamento, e processar as novas imagens de súmulas inserindo-as no banco de dados.

## Passos

1.  **Listar Diretórios:** Liste as pastas dentro de `resultados/` (ex: `rodada 1`, `rodada 2 e 3`).
2.  **Informar Status Inicial:** Avise ao usuário quais rodadas já estão no placar (geralmente as que não possuem arquivos novos ou que você tem registro na conversa) e quais pastas você encontrou de novas rodadas.
    *   Exemplo de fala: *"Até agora só temos o resultado da Rodada 1. Localizei a pasta `rodada 2 e 3` e vou fazer a leitura das novas súmulas!"*
3.  **Ler Súmulas:** Crie e execute um script Python que utilize o `google.generativeai` (Gemini Vision) para ler em lote todas as imagens (`.jpeg`, `.png`, etc.) das novas pastas de rodadas e convertê-las em registros no banco de dados.
    *   O script deve usar o prompt para extrair: `mesa`, `jogo`, `da` (Dupla A), `db` (Dupla B), `pa` (Pontos A), `pb` (Pontos B), `ga` (Gato A), `gb` (Gato B).
    *   Deduplicar e proteger contra injeção dupla.
4.  **Confirmar:** Após o processamento, resuma para o usuário quantas partidas foram processadas e peça para ele conferir o Telão.
