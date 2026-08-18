---
name: argus-leitura-nativa
description: Processa as Fichas de Inscrição e Comprovantes lendo diretamente com a visão do ARGUS e inserindo no banco de dados.
---

# Skill: Leitura Nativa e OCR do ARGUS

Use esta skill quando o usuário pedir para você mesmo ler as fichas e comprovantes (abandonando a API externa).

## Como Executar
1. Use a ferramenta `list_dir` para verificar `media/entradas/inscricoes-manuais/nao-processadas` e `media/entradas/comprovantes-pagamento/nao-processadas`.
2. Para cada arquivo encontrado, use `view_file` para analisar o conteúdo da imagem ou PDF.
3. Extraia o nome do Jogador 1, Jogador 2, Loja, Potência, e no caso de comprovantes: pagador, banco, data.
4. Gere um script Python silencioso (usando o shell do Django) que consulte a `Dupla` pelo nome (criando se não existir).
5. O script deve salvar/renomear o arquivo para `arquivadas` com o ID da dupla e mover o original para `processadas` com o sufixo `lido_`.
6. Após executar, relate ao usuário os IDs criados ou vinculados.
