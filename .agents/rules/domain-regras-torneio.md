---
description: Regras de negócio, UX do mapa de mesas (Telão), nomenclatura de confrontos e apuração do Torneio.
---

# Regra: Controle Visual de Salão, Telão e Súmulas Digitais

Sempre que arquitetar o banco de dados e as views da aba de **Competição** (`torneio.html`), a estrutura deve refletir um fluxo operacional visual projetável (Telão), 100% digital e sob demanda.

## 1. O Mapa do Salão no Telão (UI/UX)
A interface principal será projetada em um telão para o público. Portanto:
- **Design de Alto Contraste:** Uso de cards grandes e legíveis à distância para representar as Mesas.
- **Card da Mesa Vazia (Livre):** Cor indicativa de disponibilidade (ex: verde). 
- **Card da Mesa Ocupada (Em Andamento):** Muda de cor (ex: vermelho). Exibe quem está jogando (Dupla A x Dupla B) em destaque.
- **Encerramento:** O operador (admin) clica na mesa para "Pagar a Súmula" (lançar os pontos), o card volta a ficar Verde.
- A página deve possuir capacidades de *Auto-Refresh* ou atualização via WebSocket para que o público veja as mudanças em tempo real.

## 2. Entidades de Apoio (Mesas e Árbitros)
Para agilizar as aberturas de súmula:
- **Árbitro:** Cadastro contendo o nome do juiz.
- **Mesa:** Cadastro contendo o número da mesa e o Árbitro alocado a ela. 

## 3. Entidade "Confronto" no Banco de Dados
A modelagem do Django (Model `Confronto` - antigo Partida) deve prever:
- `numero_jogo` (Inteiro, sequencial, único).
- `mesa` (ForeignKey para Mesa).
- `dupla_a` (ForeignKey para Dupla).
- `dupla_b` (ForeignKey para Dupla).
- `pontos_a` (Inteiro, nulo até o fim do confronto).
- `pontos_b` (Inteiro, nulo até o fim do confronto).
- `status` (Choices: 'Em Andamento', 'Finalizado').

## 4. Tabela Dinâmica de Classificação (O Leaderboard)
A classificação global (também projetável no telão em abas ou rolagem) agrega os dados de `Confronto.objects.filter(status='Finalizado')`. Colunas:
- **Vitórias:** Confrontos vencidos regularmente.
- **Capotes:** Vitórias onde o adversário fez no máximo 95 pontos.
- **Rolhas:** Vitórias onde o adversário fez exatamente 100 pontos.
- **Lisas:** Vitórias onde o adversário não fez nenhum ponto (0 pontos).
- **Derrotas:** Total de confrontos perdidos.
- **Pontos Feitos (PF):** Soma de todos os pontos marcados pela dupla.
- **Pontos Sofridos (PS):** Soma de todos os pontos marcados contra a dupla.
- **Score (Pts Classificação):** `(Vitórias * 3) + (Capotes * 4) + (Rolhas * 5) + (Lisas * 6)`.

## 5. Critérios de Desempate (Prioridade Estrita)
1. **Maior número total de vitórias** (todas as variações somadas).
2. **Maior número de Pontos Feitos (PF).**
3. **Menor número de Pontos Sofridos (PS).**
4. **Maior Saldo de Pontos** (PF - PS).
*(Empates absolutos dividirão a posição visualmente no sistema).*

## 6. Painel de Backoffice (Configurações do Salão)
Enquanto a rota `/torneio/` serve como o "Telão" (Visão Pública e Operação de Súmulas), deve existir uma interface separada de gerenciamento (Backoffice).
Essa interface deve ficar dentro do painel principal (Admin) e permitirá à organização:
- **Gestão de Árbitros:** Tabela CRUD (Criar, Ler, Atualizar, Deletar) para cadastrar o nome e contato dos árbitros.
- **Gestão de Mesas:** Tabela CRUD para criar as Mesas (1 a 16) e vincular/desvincular o Árbitro de cada mesa. (Isso permite trocar o árbitro no meio do evento se alguém for ao banheiro).
- **Gestão da Fila de Espera (Drag & Drop):** Uma interface que permita listar todas as duplas validadas e ordená-las manualmente (ou automaticamente por ordem de chegada) para definir quem é o 1º da fila, 2º da fila, etc.

## 7. Operação em Multi-Telas (Dual Screen)
A arquitetura do sistema presume que, durante o evento, haverá um uso simultâneo de rotas em abas distintas:
- **O Telão (Visão Pública):** Rodará solto em uma aba para projeção, consumindo dados assíncronos.
- **O Backoffice (Visão Admin):** Rodará em outra aba na máquina do operador, que é quem alimentará e corrigirá os dados do sistema em tempo real sem afetar a navegação do telão.
*(Isto significa que nenhuma ação de backend do painel admin deve dar um "reload" ou redirecionar forçadamente a página do telão de forma síncrona)*

## 8. Cronômetro de Confronto (15 Minutos - Regressivo)
- O tempo máximo por confronto é de 15 minutos e será exibido como uma **contagem regressiva** (Countdown).
- **Mesas Livres:** Devem exibir o relógio estático e pausado em `15:00`.
- **Mesas Ocupadas (Ativas):** Quando o jogo inicia, o cronômetro javascript calcula o tempo decorrido e subtrai dos 15 minutos originais.
- A contagem vai descendo: `14:59`, `14:58`...
- **Tempo Esgotado:** Ao chegar em `00:00`, o relógio trava no zero e a classe de alerta (vermelho piscante) é ativada para que o árbitro encerre a súmula.

## 9. Layout Posicional das Mesas e Rankings (Split Screen)
- **Formato Físico do Salão:** O salão tem exatamente **3 colunas e 4 linhas** (12 mesas ativas).
- O CSS do .mesas-grid deve usar grid-template-columns: repeat(3, 1fr) para espelhar perfeitamente a realidade.
- O layout geral do Telão (	orneio.html) divide a tela horizontalmente (padrão Bootstrap 12-cols):
  - **Lado Esquerdo:** Área exclusiva para as Mesas.
  - **Lado Direito:** Painel fixo lateral contendo a Fila de Espera e o Top 5 de Classificação (Leaderboard).

## 10. Espelhamento de Layout (RTL)
- Como a visão do público exige, a malha de mesas (Esquerda da tela) deve ser renderizada visualmente da Direita para a Esquerda via CSS (direction: rtl;). A Mesa 1 ocupa a extrema direita, e a Mesa 3 ocupa a extrema esquerda do Grid.

## 11. Lista Oficial de Credenciamento Dinâmica
- O evento trabalha com credenciamento (número da dupla dado na porta) como identidade primária, ignorando a ordem original de pagamento.
- Tolerância a Erros: Se um jogador credenciado não for encontrado nos nomes de jogadores, o sistema deve checar o Pagador do comprovante. Se ninguém for encontrado, a dupla é criada e autorizada a jogar sob Alerta, sem travar o campeonato.

## 12. O Gato (Infração) e Capotes Sofridos
- O Gato (jogar pedra em ponta errada) decreta a derrota imediata da dupla infratora, ignorando a contagem de pontos.
- Se o infrator tiver feito até 95 pontos ao cometer o Gato, o adversário ganha os pontos de Capote no Ranking.
- O Motor Matemático separa estatisticamente capotes aplicados de capotes_sofridos.
