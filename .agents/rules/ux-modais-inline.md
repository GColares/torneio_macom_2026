# Regra: UX para Auditoria e Edição de Arquivos (Modais Inline)

Sempre que criar botões em tabelas para auditar, visualizar ou editar arquivos anexos a um registro (como Fichas de Inscrição, Comprovantes, etc.), siga estritamente estas diretrizes:

1. **Evite Redirecionamentos:** Não utilize tags `<a>` para redirecionar o usuário para outra URL ou página isolada.
2. **Utilize Modais "Split-View":** Construa ou reutilize um Modal do Bootstrap que divida a tela em dois:
   - Lado esquerdo: Visualizador nativo do arquivo (Iframe para PDF ou tag `<img>`).
   - Lado direito: Formulário de edição dos dados associados (Status, Vínculos, etc).
3. **Isolamento de Componentes:** Extraia o HTML e o JS do modal para a pasta `templates/partials/` para poder incluí-los (`{% include %}`) em múltiplas telas (ex: na tela de Gestão, na tela específica de Arquivos, etc) mantendo a mesma funcionalidade sem poluir o código.
4. **Alimentação via API (Fetch):** Ao invés de popular o botão com dezenas de propriedades `data-*`, o JS do modal deve fazer um GET na API (ex: `/api/entidade/<id>/`) para preencher os campos do lado direito, garantindo que os dados estejam sempre atualizados.
