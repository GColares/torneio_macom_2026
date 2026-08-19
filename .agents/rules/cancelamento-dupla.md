# Regra: Ciclo de Vida e Cancelamento de Inscrições

No contexto do Torneio Maçônico, as entidades `Comprovante` (Pagamento) e `FichaInscricao` existem de forma independente da entidade `Dupla`. O vínculo entre eles é apenas relacional.

Sempre que implementar regras de edição, exclusão lógica ou alteração de status:
1. **Desvínculo no Cancelamento**: Se uma `Dupla` for rebaixada para o status `status_inscricao = 'Cancelada'`, o sistema deve **obrigatoriamente romper os laços** com seus arquivos. 
2. **Ação Técnica**: Atribua `None` (null) às foreign keys/OneToOneFields (`dupla.comprovante = None` e `dupla.ficha_inscricao = None`).
3. **Objetivo**: Isso garante que os documentos (que são independentes) retornem para o "pool" de arquivos órfãos (ex: aba de "Revisão Pendente"), podendo ser analisados novamente ou vinculados a uma dupla válida. Nunca exclua os objetos originais de arquivo físico e de banco a menos que explicitamente solicitado.
