# Backup Versioning Rule

Sempre que criar um backup de banco de dados (como arquivos `.sqlite3`) ou de qualquer outro arquivo importante neste projeto:

1. **Adicione um ID numérico sequencial com 3 dígitos no INÍCIO** do nome do arquivo (ex: `001_`, `002_`).
2. **Formato Padrão:** `NNN_db_backup_YYYY-MM-DD_HH-MM.sqlite3`.
    - Exemplo: `001_db_backup_2026-08-10_23-35.sqlite3`.
3. Para descobrir qual é o próximo número (`NNN`), verifique os arquivos existentes na pasta de backups e incremente o maior número encontrado.
4. Caso não saiba a hora exata do backup, utilize `00-00` no lugar da hora.

Esse prefixo numérico associado à formatação com hifens (para datas) garante clareza visual e facilita a restauração via comandos simples ("restaure o backup 3").
