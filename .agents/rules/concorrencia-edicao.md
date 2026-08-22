---
description: Regra de segurança obrigatória para trabalho simultâneo (Pair Programming).
---

# Regra: Concorrência e Aviso de Bloqueio de Teclado

Sempre que o agente e o usuário estiverem trabalhando juntos no mesmo projeto, o agente DEVE seguir estritamente o protocolo abaixo para evitar perda acidental de código humano:

## 1. O Protocolo de "Mãos ao Alto" (Bloqueio de Teclado)
- **ANTES** de realizar modificações estruturais grandes (ex: sobrescrever um arquivo inteiro como `views.py`, `models.py` ou `urls.py`), o agente **NÃO DEVE** executar a ação no mesmo turno.
- O agente deve primeiro enviar uma mensagem clara ao usuário dizendo: *"🛑 BLOQUEIO DE TECLADO: Vou reescrever o arquivo X agora. Por favor, salve o que estiver fazendo e confirme para eu prosseguir."*
- O agente só deve executar a modificação no arquivo após a confirmação do usuário.

## 2. Edições Silenciosas (Seguras)
- O agente só tem permissão para alterar código silenciosamente (sem pedir bloqueio de teclado) se estiver usando ferramentas de edição cirúrgicas (substituição de bloco/linha específica), garantindo que apenas uma pequena fração do código mude e que o Git consiga fazer o merge caso haja conflito.

## 3. Rede de Segurança (Git)
- O agente deve realizar `git commit` após entregas funcionais para garantir que o usuário tenha um ponto de restauração fácil caso aconteça algum acidente.
