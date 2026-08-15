---
name: Guia Visual e Cores (Torneio Macom)
description: Diretrizes de UI/UX e paleta de cores para o painel de gestão.
---
# Diretrizes Visuais

Ao criar ou modificar elementos de interface para o Torneio Macom 2026, aplique as seguintes regras estéticas:

1. **Tema Escuro Nativo**: O painel é estritamente Dark Mode (Fundo `#0d1117` e painéis `#161b22`).
2. **Cores de Sucesso (Verde Neon)**: Evite usar o padrão apagado do Bootstrap (`text-success`, `bg-success`). Para mensagens positivas, badges de "Confirmado", botões de "Aprovado", alertas de sucesso, use SEMPRE o Verde Neon/Vivo:
   - Cor do texto/borda: `#00ff66 !important`
   - Background (para badges): `rgba(0, 255, 102, 0.15) !important`
3. **Cores de Alerta (Amarelo/Laranja)**: Use tons fortes para alertas e avisos pendentes (ex: `text-warning`).
4. **Bypass de Cache**: Sempre que criar novas classes CSS vitais de cores personalizadas que o usuário precise ver imediatamente, insira-as no bloco `<style>` interno do HTML (`gestao.html`), e não no `style.css` externo.
