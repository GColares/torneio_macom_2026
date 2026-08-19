# Regra: Gestão da Tríade de Entidades

No escopo arquitetural do projeto, o domínio não é composto apenas por inscrições ("Duplas"). É mandatório que o sistema ofereça visibilidade para a **Tríade de Entidades**:
1. `Dupla` (Inscrição)
2. `Comprovante` (Arquivo e validação financeira)
3. `FichaInscricao` (Arquivo físico/digitalizado da ficha)

Sempre que projetar melhorias de relatórios, métricas e dashboards, o sistema deve ser capaz de auditar **vínculos e orfandade**:
- Quantos comprovantes existem e não estão amarrados a uma dupla (Órfãos)?
- Quantas fichas não estão amarradas a uma dupla (Órfãs)?
- Quantas duplas estão deficientes (sem arquivo de comprovante ou sem ficha obrigatória)?

Além disso, as interfaces de gestão (`gestao_comprovantes` e `gestao_fichas`) devem obrigatoriamente seguir a regra de **Auditoria Visual Facilitada**:
- **Central de Comprovantes**: Deve categorizar explicitamente os registros em 3 estados: "Aguardando Inscrição/Órfão" (sem dupla), "Pendente" (vinculado a dupla não confirmada) e "Validado" (vinculado a dupla confirmada).
- **Central de Fichas**: A tabela não deve exibir apenas nomes de arquivos, mas focar na "Prova Real do OCR", exibindo sempre uma miniatura visual (thumbnail) do documento físico lado a lado com os dados transcritos da Dupla vinculada.
- **Visualização e Edição Nativa (UX)**: Todos os documentos (PDF/Imagens) DEVEM ser abertos dentro da própria tela utilizando um Modal (não redirecionar o usuário para outra aba). Além disso, os Modais de Intervenção Humana (Edição) devem OBRIGATORIAMENTE utilizar o padrão **Split-View** (Tela Dividida): a prévia visual do arquivo original deve ser exibida lado a lado com os campos do formulário para permitir que o humano transcreva e audite as informações sem perder o arquivo de vista.
- **Densidade de Dados na Edição**: O formulário lateral de intervenção não deve ser minimalista. No caso de Comprovantes, deve expor para edição todos os dados financeiros (Banco, Valor, ID da Transação, Data/Hora precisas) e exibir visualmente os dados de leitura da dupla atual (Número, J1, J2) para garantir segurança antes da alteração de vínculos.

Esta visibilidade previne vazamento financeiro (comprovantes pagos que foram perdidos) e fraudes (inscrições confirmadas sem lastro de comprovante físico).
Adicionalmente: Seja sempre proativo em propor melhorias de visibilidade (auditoria de banco), segurança e antifraude durante as sessões de evolução do sistema.
