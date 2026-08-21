# Regra: Hierarquia de Status da Inscrição

O campo `status_inscricao` da classe `Dupla` possui uma hierarquia lógica. Ações de validação de documentos não podem rebaixar inscrições.

1. **Hierarquia:** `Inscrita` > `Validada` > `Pendente` / `Pendente Ficha` / `Pendente Pagamento`.
2. **Botões de Ação:** Nas listagens (como `gestao_fichas.html`), botões de "Validar Ficha" ou similares DEVEM ficar ocultos caso o status atual seja `Validada` ou `Inscrita`.
3. **Bloqueio de Downgrade no JS/Backend:** Se uma função JS como `validarFicha()` for disparada, ela deve primeiro verificar o status atual (`window.currentDuplaStatus`). Se já for `Inscrita`, deve bloquear o envio ou exibir um aviso de que a ação é desnecessária.

Condicional recomendada no Django Template para exibir ações de validação:
`{% if f.dupla and f.dupla.status_inscricao not in 'Validada,Inscrita,Cancelada' %}`
