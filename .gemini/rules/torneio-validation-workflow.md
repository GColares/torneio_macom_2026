---
name: Fluxo de Validação de Inscrições (Torneio Macom)
description: Regras de negócio sobre o status de validade das duplas.
---
# Regras de Validade de Inscrição

Ao criar scripts, importar dados ou adicionar novas funcionalidades ao projeto Torneio Macom 2026, siga estritamente este fluxo de trabalho:

1. **Estado Inicial**: Toda e qualquer nova inscrição (Dupla) deve ser inserida no banco de dados com `valido = False`. Nenhuma inscrição nasce válida por padrão.
2. **Aprovação Manual**: A alteração para `valido = True` é uma prerrogativa estritamente humana e manual. Ela ocorre apenas após o organizador cruzar e confirmar os dados do comprovante de pagamento e os dados da dupla.
3. **Bloqueio de Automação**: Scripts de OCR, sincronizadores de CSV e Webhooks de pagamento não têm permissão para alterar o campo `valido` para `True`. A automação financeira deve limitar-se a atualizar o `status_pagamento` (Pendente -> Confirmado) e os metadados do comprovante, mas a Inscrição (`valido`) continua aguardando o clique humano na interface de gestão.
