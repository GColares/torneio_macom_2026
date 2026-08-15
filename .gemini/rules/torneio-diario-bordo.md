---
name: Diário de Bordo e Contexto do Projeto
description: Regras para ler e atualizar o diário de bordo sempre que o usuário solicitar ou iniciar/encerrar o dia.
---

# Diário de Bordo (Dev Diary)

O usuário utiliza duas máquinas diferentes e conta com o arquivo `diario_de_bordo.md` na raiz do projeto para sincronizar o contexto, decisões arquiteturais e pendências.

## Gatilhos e Ações

1. **Gatilhos de Leitura ("Ler diário de bordo", "Ver diário", "Bom dia")**:
   - Sempre que o usuário disser "Bom dia" ou pedir para ler o diário, você DEVE usar a ferramenta `view_file` para ler todo o conteúdo de `diario_de_bordo.md`.
   - Após ler, faça um breve resumo super amigável do ponto em que paramos na sessão anterior para contextualizar o início do trabalho.

2. **Gatilhos de Escrita ("Escrever diário de bordo", "Atualizar diário", "Até amanhã")**:
   - Sempre que o usuário disser "Até amanhã" ou pedir para atualizar o diário, você DEVE editar o arquivo `diario_de_bordo.md` e adicionar uma nova entrada com a data atual.
   - A entrada deve conter:
     - **Resultados do Dia**: O que foi construído ou resolvido (resumo técnico e de negócio).
     - **Decisões e Cuidados**: Limitações encontradas, pacotes instalados (ex: PyMuPDF), e arquitetura adotada.
     - **Próximos Passos**: O que ficou para ser feito na próxima sessão.
   - Adicione o conteúdo no TOPO do arquivo, logo abaixo do título principal (ordem cronológica reversa), para que o contexto mais recente seja sempre lido primeiro.
   - Após escrever, despeça-se do usuário adequadamente se o gatilho foi "Até amanhã".
