---
name: github-bom-dia
description: "Rotina completa de início do dia (Chegada). Sincroniza o código, instala bibliotecas, roda migrações e restaura backups do banco."
---

# Instruções de Execução

Sempre que o usuário enviar o comando "bom dia" (ex: "bom dia", "pode começar"), você deverá preparar o ambiente local com base nas últimas atualizações do GitHub.

Siga os passos rigorosamente nesta ordem:

1. **Ler o Diário de Bordo:**
   - OBRIGATORIAMENTE leia o arquivo `diario_de_bordo.md` na raiz do projeto (crie se não existir) para se contextualizar sobre o status atual do projeto e o que está pendente para o dia de hoje.
2. **Sincronizar Código (Pull):**
   - Execute o comando para baixar as novidades da nuvem: `git pull --rebase`
3. **Sincronizar Pacotes (Requirements):**
   - Execute a instalação do que houver de novo no requirements: `pip install -r requirements.txt`
4. **Sincronizar Estrutura do Banco (Migrações):**
   - Execute as migrações para que a estrutura acompanhe o código: `python manage.py migrate`
5. **Acionar Restauração de Dados (Restauração Opcional):**
   - Verifique a pasta `backups/` e encontre o arquivo `.sqlite3` com o maior prefixo numérico (ex: `003_db_backup...`).
   - Se encontrar um backup, avise o usuário qual foi o backup mais recente que existe na pasta. Em seguida, **PERGUNTE** ao usuário se ele deseja injetar (restaurar) esse backup no banco atual.
   - **SE O USUÁRIO CONFIRMAR A INJEÇÃO:**
     - Restaure copiando/substituindo o arquivo sobre o `db.sqlite3` original na raiz do projeto.
6. **Reportar ao Usuário:**
   - Deseje um bom dia de trabalho, resuma brevemente o que você leu no diário de bordo e confirme que o ambiente está totalmente sincronizado!
