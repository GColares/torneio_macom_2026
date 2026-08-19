# Regra: Gestão da Tríade de Entidades

No escopo arquitetural do projeto, o domínio não é composto apenas por inscrições ("Duplas"). É mandatório que o sistema ofereça visibilidade para a **Tríade de Entidades**:
1. `Dupla` (Inscrição)
2. `Comprovante` (Arquivo e validação financeira)
3. `FichaInscricao` (Arquivo físico/digitalizado da ficha)

Sempre que projetar melhorias de relatórios, métricas e dashboards, o sistema deve ser capaz de auditar **vínculos e orfandade**:
- Quantos comprovantes existem e não estão amarrados a uma dupla (Órfãos)?
- Quantas fichas não estão amarradas a uma dupla (Órfãs)?
- Quantas duplas estão deficientes (sem arquivo de comprovante ou sem ficha obrigatória)?

Esta visibilidade previne vazamento financeiro (comprovantes pagos que foram perdidos) e fraudes (inscrições confirmadas sem lastro de comprovante físico).
Adicionalmente: Seja sempre proativo em propor melhorias de visibilidade (auditoria de banco), segurança e antifraude durante as sessões de evolução do sistema.
