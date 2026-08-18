# Regra: Persistência de Estado no DataTables

Sempre que inicializar ou modificar a implementação de uma tabela utilizando a biblioteca **DataTables** (`.DataTable({...})`), você deve OBRIGATORIAMENTE adicionar a configuração:

`stateSave: true`

**Motivo:** Isso garante que a ordenação, paginação e os filtros da tabela sejam persistidos no `localStorage` do navegador do usuário. Assim, quando o usuário clicar para editar um item ou recarregar a página, ele não perderá a página e a ordem em que a tabela estava.
