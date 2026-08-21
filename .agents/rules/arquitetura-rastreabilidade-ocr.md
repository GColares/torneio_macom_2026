# Regra: Rastreabilidade de OCR e Nomenclatura de Arquivos

Para garantir a auditoria entre arquivos brutos (`entradas`) e arquivos fatiados/validados (`arquivadas`), o sistema NÃO deve padronizar a nomenclatura das pastas de forma espelhada, pois a relação é de 1 para N.

1. **Preservação do Original:** Os arquivos em `entradas/processadas` devem preservar seu nome original concatenado com um prefixo de processamento e um *Timestamp de Lote* (Ex: `lido_YYYYMMDD_HHMMSS_original.pdf`).
2. **Rastreabilidade por Timestamp:** Os arquivos resultantes em `arquivadas` DEVEM incorporar o MESMO *Timestamp de Lote* do arquivo de origem que os gerou (Ex: `ficha_dupla_ID_YYYYMMDD_HHMMSS.pdf`). 
3. **Proibição de Renomeação Destrutiva:** NUNCA renomeie um arquivo de entrada (batch) com o ID de uma entidade filha (Dupla), pois isso destrói a árvore genealógica de dados extraídos de arquivos multi-páginas.
