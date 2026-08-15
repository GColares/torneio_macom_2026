---
name: Arquitetura de Arquivos e OCR (Torneio Macom)
description: Regras para processamento, fatiamento e armazenamento de arquivos em lote.
---
# Regras de Processamento de Arquivos

1. **Pastas de Entrada (Caixa de Entrada)**:
   - Formulários Físicos: `static/img/inscricoes-manuais`
   - Comprovantes: `static/img/comprovantes-pagamento`
2. **Separação (Fatiamento)**:
   - Todo PDF lido das pastas de entrada deve ser tratado assumindo que pode ser um lote (Batch).
   - O PDF multipáginas deve ser dividido em arquivos de 1 única página em uma pasta temporária (ou na própria pasta de entrada) antes de passar pelo OCR, pois cada inscrição/comprovante ocupa exatamente 1 folha.
3. **Armazenamento e Nomenclatura (Media)**:
   - Ao vincular com sucesso um arquivo a uma `Dupla`, o arquivo deve ser movido imediatamente para `MEDIA_ROOT`.
   - É estritamente obrigatório renomear o arquivo utilizando o ID da dupla para evitar colisões. 
   - Padrão: `media/inscricoes/inscricao_{id}.ext` e `media/comprovantes-pagamento/comprovante_{id}.ext`.
4. **Anexos da Inscrição**:
   - Inscrições Eletrônicas possuem 1 anexo (no banco: `comprovante`): Comprovante de Pagamento.
   - Inscrições Manuais possuem 2 anexos (no banco: `ficha_inscricao` e `comprovante`): Ficha de Inscrição + Comprovante de Pagamento.
