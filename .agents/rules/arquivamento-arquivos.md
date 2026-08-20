# Regra: Arquivamento e Renomeação de Uploads Manuais

Sempre que a aplicação (views, scripts, agentes) receber um arquivo físico manualmente (ex: Comprovante de Pagamento, Ficha de Inscrição) através de upload pela UI:

1. A aplicação **não deve** confiar cegamente no salvamento padrão do Django (`upload_to` básico), caso as regras de negócio exijam nomes dinâmicos dependentes de vínculos reversos.
2. É obrigatório identificar se o registro criado possui vínculo com uma `Dupla` ou se é Órfão.
3. Após salvar o arquivo provisoriamente (ou através de manipuladores customizados), o arquivo deve ser movido e renomeado para a pasta definitiva de processadas (`media/arquivadas/...`) seguindo a mesma máscara de padronização do ARGUS:
   - Com vínculo: `<tipo_doc>_dupla_<ID>_<TIMESTAMP>.<ext>`
   - Sem vínculo: `<tipo_doc>_orfao_<TIMESTAMP>.<ext>`
4. O caminho do arquivo no banco de dados deve ser atualizado para refletir o novo destino e nome seguro.
