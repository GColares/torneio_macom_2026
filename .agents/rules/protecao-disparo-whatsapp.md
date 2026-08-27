---
description: Restrição de segurança e desligamento obrigatório de robôs (Kill-Switch) no WhatsApp
---

# Regra: Proteção e Trava de Disparos no WhatsApp

1. **PROIBIDO EM NÚMEROS PESSOAIS:** Nunca execute scripts de disparo em massa (como a pesquisa de satisfação) enquanto a Evolution API estiver conectada a um número de WhatsApp pessoal em uso.
2. **ESPERAR CHIP OFICIAL:** O envio real para a base de contatos (os 73 jogadores) está estritamente bloqueado até que o chip oficial da FAD seja adquirido e configurado com gatilho irrestrito ("All").
3. **AMBIENTE DE TESTE:** Simulações e testes do Typebot podem ser feitos utilizando números secundários controlados ou através de senhas rigorosas (\Keyword\), blindando as conversas particulares de interferências do robô.
4. **TRAVA OBRIGATÓRIA PÓS-TESTE (KILL-SWITCH):** Assim que o usuário informar que os testes com Typebot terminaram (ou caso o usuário se despeça com "Até amanhã"), você **deve obrigatoriamente** desativar e excluir todos os gatilhos da Evolution API rodando um comando no banco de dados (\DELETE FROM "Typebot";\ via container \volution-postgres\) e reiniciar a API. Isso impede que o robô continue ativo em background e responda à família ou a grupos do usuário.
