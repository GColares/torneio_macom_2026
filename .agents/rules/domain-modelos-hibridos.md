# Regra: Modelos Híbridos (Físico vs Virtual)

Sempre que um modelo de domínio (ex: Comprovantes, Fichas) precisar acomodar tanto registros baseados em Arquivos Físicos (Uploads) quanto Registros Virtuais (Sem Arquivo), siga a abordagem de Tabela Única (Single Table):

1. **Evite Herança de Múltiplas Tabelas:** Mantenha apenas o modelo original (ex: `Comprovante`). Não crie tabelas derivadas a menos que a divergência de campos seja extrema.
2. **Campo Discriminador:** Adicione um campo `tipo` (ex: `models.CharField(choices=...)`) para diferenciar a natureza do registro (ex: `BANCARIO` vs `RECIBO`).
3. **Nullable Arquivos:** O campo que armazena o arquivo (ex: `arquivo = models.FileField(...)`) DEVE se tornar `null=True, blank=True` no banco de dados.
4. **Validação Condicional:** A obrigatoriedade dos campos deve ser garantida na camada de interface (Front-end JS) e na camada de visualização (Views/APIs), não diretamente no banco. Por exemplo, se `tipo == 'RECIBO'`, o backend deve recusar a criação caso `pagador` e `valor` não sejam enviados, mesmo que eles sejam `null=True` no banco.
