# Regra: Validação do Workspace no Início de Cada Sessão

Ao iniciar qualquer conversa neste projeto, a IA DEVE verificar
se o workspace aberto é a pasta correta do projeto.

## Como verificar

O workspace correto é `C:\JAPA\torneio_macom_2026`.
Os sinais de que o workspace CORRETO está aberto são:
- Presença do arquivo `manage.py` na raiz do workspace
- Presença da pasta `macom_project/` na raiz
- Presença da pasta `.agents/` na raiz

Se QUALQUER um desses sinais estiver ausente, a IA deve:

1. **PARAR imediatamente** antes de executar qualquer tarefa
2. **Avisar o usuário** com a seguinte mensagem:

> ⚠️ **Workspace incorreto detectado!**
> O aplicativo parece estar aberto em uma pasta errada.
> A pasta correta do projeto é: `C:\JAPA\torneio_macom_2026`
> Por favor, feche e reabra o Antigravity selecionando a pasta correta antes de continuar.

3. **Não criar arquivos, não rodar git, não criar worktrees** até que o workspace seja corrigido.

## Por que isso é importante

Abrir a IA em uma pasta pai (ex: `C:\JAPA`) pode causar:
- Criação automática de Git Worktrees em locais indesejados
- Perda de contexto sobre a estrutura real do projeto
- Comandos git executados no repositório errado
