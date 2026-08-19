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
- **Visualização e Edição Nativa (UX)**: Todos os documentos (PDF/Imagens) DEVEM ser abertos dentro da própria tela utilizando um Modal (não redirecionar o usuário para outra aba). Além disso, todas as linhas da tabela DEVEM possuir um botão "Editar" explícito nas Ações, permitindo intervenção humana (alteração de valores, data ou forçar vínculo com ID de outra dupla).

Esta visibilidade previne vazamento financeiro (comprovantes pagos que foram perdidos) e fraudes (inscrições confirmadas sem lastro de comprovante físico).
Adicionalmente: Seja sempre proativo em propor melhorias de visibilidade (auditoria de banco), segurança e antifraude durante as sessões de evolução do sistema.
