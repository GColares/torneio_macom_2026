# Regra: Isolamento de Tema em Relatórios (Print UX)

Sempre que construir ou modificar telas de **Relatórios** (telas feitas para impressão em papel ou exportação para PDF, como `relatorios.html`), aplique as seguintes diretrizes de UX/CSS:

1. **Tema Claro Obrigatório (Isolamento):**
   Como o sistema utiliza Modo Escuro global (`data-bs-theme="dark"`), as tabelas normais herdarão fundo escuro. Para telas de relatório simulando papel A4, OBRIGATORIAMENTE encapsule o container principal de impressão com `data-bs-theme="light"` e utilize a classe `.table-light` nas tabelas.
   - Isso garante texto escuro sobre fundo claro e evita o "sumiço" das letras no efeito de hover.

2. **Área de Impressão (Media Print):**
   Mantenha a regra `@media print` no topo do arquivo que esconde a barra lateral (`.sidebar`) e forçosamente ajusta bordas de tabela para `#ddd` e letras para `#000` absoluto. 

Nunca crie relatórios gerenciais com fundo escuro, pois isso consome muita tinta nas impressoras corporativas e dificulta a visualização sobre telas brancas.
