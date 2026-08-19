# Regra: Ordenação Master das Duplas / Inscrições

Ao desenvolver qualquer recurso que liste, exporte, classifique ou consulte inscrições (Duplas) no projeto Torneio Maçônico:

1. **A Regra de Ouro**: A ordem cronológica da criação e garantia da vaga de uma dupla **NÃO** é dada pela data do preenchimento da ficha, mas sim **pelo momento exato do pagamento**.
2. **Chave de Ordenação**: Toda query de Django (ORM), script JavaScript (DataTables) ou exportação deve ser obrigatoriamente ordenada de forma **Ascendente** (do mais antigo/primeiro a pagar para o mais novo) usando o atributo da data do pagamento. 
   - No Django ORM: `order_by(F('comprovante__data_hora').asc(nulls_last=True))`
3. **Tratamento de Exceções**: Inscrições sem pagamento (ou cujo comprovante ainda não foi lido ou preenchido) devem ser classificadas **no final absoluto da lista**, garantindo que as prioridades sejam dadas somente a quem já pagou.
   - Em HTML/DataTables: Use atributos de ordenação customizados (`data-sort`) definindo um número absurdamente alto (ex: `99999999999999`) para inscrições pendentes.
