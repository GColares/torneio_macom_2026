---
name: github-ate-amanha
description: "Rotina completa de encerramento do dia (Saída). Faz o backup do banco, salva as dependências e envia o código para a nuvem."
---

# Instruções de Execução

Sempre que o usuário enviar o comando "ate-amanha" (ex: "até amanhã", "ate amanha", "encerrar dia"), você deverá executar a rotina de empacotamento e envio do projeto para a nuvem.

Siga os passos rigorosamente nesta ordem:

1. **Atualizar Regras de Negócio e Diário:**
   - Se houve alguma descoberta ou regra nova de negócios discutida hoje, documente-a.
   - Atualize OBRIGATORIAMENTE o arquivo `diario_de_bordo.md` na raiz do projeto. NUNCA sobrescreva apagando o histórico anterior. INSERIR a nova entrada (com a data atual, o que foi feito e o que está pendente) logo abaixo do título principal.
2. **Geração de Backup de Segurança:**
   - Garanta que a pasta `backups/` existe na raiz do projeto.
   - Determine o próximo ID sequencial (NNN) analisando a pasta `backups/` e faça a cópia do `db.sqlite3` adotando a regra de nomenclatura NNN: `NNN_db_backup_YYYY-MM-DD_HH-MM.sqlite3`.
3. **Salvar Pacotes (Requirements):**
   - Execute a exportação das dependências: `pip freeze > requirements.txt`
4. **Verificar o Status e Adicionar:**
   - Execute `git status` e depois `git add .`.
5. **Gerar Commit:**
   - Formule uma mensagem curta de fechamento do dia e execute `git commit -m "Fechamento do dia: resumo"`.
6. **Sincronizar (Pull):**
   - Execute `git pull --rebase`.
7. **Enviar para o GitHub (Push):**
   - Não execute o `git push` diretamente se houver risco de travar por credencial (ambiente headless). Em vez disso, avise o usuário para abrir o terminal dele e digitar `git push`.
8. **Reportar ao Usuário:**
   - Após finalizar, deseje um bom descanso e confirme que tudo foi salvo e enviado com sucesso.
