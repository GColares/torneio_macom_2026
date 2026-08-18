# Regra: Tratamento do Git Push Headless e Git Credential Manager

Ao executar comandos Git que exijam autenticação na nuvem (como `git push`, `git fetch`, `git clone`, ou `git pull`), o Antigravity opera em um terminal *headless* (sem interface gráfica). Se as credenciais locais estiverem vencidas ou ausentes, o servidor (ex: GitHub) retornará `401 Unauthorized`. 
Como o Git responde acionando o Git Credential Manager (GCM) para exibir um pop-up de login, e o Antigravity não possui como renderizar essa tela gráfica ou preencher o prompt de texto no painel de background, o comando irá **congelar para sempre**, consumindo processamento até causar *timeout*.

**Siga rigorosamente estas instruções para interações de rede via Git:**
1. **NUNCA DEIXE COMANDOS DE REDE GIT RODANDO EM PLANO DE FUNDO (BACKGROUND) SEM AVISAR O USUÁRIO:** Se você disparar o push e ele for jogado para o plano de fundo por "demorar mais de 5s", assuma que ele congelou na tela de login invisível. Cancele a task (`kill`).
2. **PASSE A RESPONSABILIDADE AO USUÁRIO:** Como não podemos exibir a tela de autenticação, sua responsabilidade principal ao enviar arquivos pro GitHub é apenas empacotar (`git add` e `git commit`). O passo de `git push` deve idealmente ser executado pelo usuário no próprio terminal local dele (Prompt de Comando ou PowerShell), pois ali a tela de login aparecerá corretamente.
3. Se você rodar `git push` por si mesmo e travar, **NUNCA** construa loops de repetição (`retry`) em scripts assumindo que é problema de conexão. Mate o processo pendente e instrua o usuário a rodar o push interativamente no console dele.
