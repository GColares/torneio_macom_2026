# Regra: Visibilidade Incondicional de Evidências

Em dashboards, tabelas e listagens de auditoria, **todo e qualquer documento de evidência** que exista no banco de dados DEVE exibir um ícone/botão para visualização. 

1. **Evite Condicionais baseadas em Arquivos:** NUNCA condicione a exibição de atalhos de auditoria estritamente à presença de arquivos físicos (`if obj.arquivo`). 
2. **Ícones Diferenciados:**
   - Evidências **Físicas** (com upload): Usar ícones como `<i class="fa-solid fa-paperclip"></i>` ou ícone de PDF (geralmente azuis).
   - Evidências **Virtuais** (sem upload, geradas via sistema): Usar ícones como `<i class="fa-solid fa-file-invoice"></i>` (verdes) para indicar que é um documento sistêmico.
3. Se a entidade possui a evidência associada, o botão DEVE estar lá para abrir o modal unificado.
