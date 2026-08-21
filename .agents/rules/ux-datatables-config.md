# Regra: Configuração Padrão do DataTables (UX)

Sempre que inicializar ou modificar a implementação de uma tabela utilizando a biblioteca **DataTables** (`.DataTable({...})`), você deve OBRIGATORIAMENTE adicionar as seguintes configurações:

1. `stateSave: true`
   **Motivo:** Garante que a ordenação, paginação e os filtros sejam persistidos no `localStorage`. Ao recarregar a página ou editar um item, o usuário não perde sua posição atual.

2. `pageLength: 50`
   **Motivo:** Para aumentar a densidade de dados na tela, reduzindo a necessidade de navegação por páginas.

**Exemplo:**
```javascript
$('#minhaTabela').DataTable({
    stateSave: true,
    pageLength: 50,
    language: { url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json' }
});
```
