# Regra: Documentos Virtuais em Auditorias (Virtual Documents)

Sempre que o sistema precisar lidar com a ausência de um arquivo físico (upload) em uma interface de auditoria (Split-View ou semelhante), aplique as seguintes diretrizes:

1. **Nunca exiba "Telas Vazias":** Ao invés de exibir mensagens como "Sem arquivo anexado" na área de visualização, gere um **Documento Virtual HTML**.
2. **Design Oficial:** O documento virtual deve possuir estética de um documento oficial (Bordas, Marca d'água, Logo da instituição, assinaturas de responsáveis).
3. **Live Preview (Two-Way Data Binding):** O documento virtual deve puxar os dados iniciais do banco, mas **DEVE atualizar em tempo real** sempre que o usuário modificar qualquer campo correspondente no formulário de edição (usando eventos como `input` ou `change` no Javascript). O documento virtual deve refletir exatamente o que está preenchido no cadastro atual, atuando como um espelho instantâneo.
4. **Sem Persistência de Lixo:** Documentos Virtuais devem ser renderizados apenas no Frontend (via DOM/JavaScript ou Templates Django). **NUNCA** gere PDFs usando backend (reportlab/pdfkit) para salvar em disco apenas para preencher essa lacuna, a menos que seja um requisito expresso de arquivamento legal.
5. **Funcionalidade de Impressão (Opcional):** Se o usuário precisar do arquivo físico, deve-se utilizar a impressão nativa do navegador (`window.print()` estilizado com `@media print`) focado na `div` do recibo.
