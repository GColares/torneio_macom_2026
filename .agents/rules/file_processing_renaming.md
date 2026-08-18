# Regra: Ciclo de Vida de Processamento de Documentos

Sempre que atuar como motor de OCR ou processamento de arquivos para o torneio, você deve obedecer à seguinte arquitetura de diretórios dentro de `media/`:

### Estrutura de Pastas
- **ENTRADAS:** `media/entradas/[inscricoes-manuais|comprovantes-pagamento]/`
  - `/nao-processadas/`: Onde o usuário "joga" os PDFs brutos. É daqui que você lê.
  - `/processadas/`: Para onde você **move o arquivo original** após o sucesso.
  - `/revisao-pendente/`: Para onde você **move o arquivo original** se a leitura falhar.
- **ARQUIVO DEFINITIVO:** `media/arquivadas/[inscricoes-manuais|comprovantes-pagamento]/`

### Comportamento Exigido
1. **Fatiamento (Split):** Se um PDF na pasta `nao-processadas` possuir múltiplas fichas ou comprovantes agrupados, você deve separá-los virtualmente.
2. **Geração:** Salve cada ficha/comprovante fatiado como um arquivo individual em `media/arquivadas/...` nomeando-o com um padrão claro (ex: `[tipo]_dupla_[id]_[datahora].pdf`).
3. **Movimentação do Original:** Terminado o fatiamento e leitura, NUNCA delete o arquivo original. Mova-o da pasta `nao-processadas/` para a pasta `processadas/` (ou `revisao-pendente/` em caso de erro grave de ilegibilidade).
