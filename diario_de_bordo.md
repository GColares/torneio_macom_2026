# Diário de Bordo

### 22/08/2026
- **O que foi feito:**
  - **Implementação do Painel de Jogos (Gestão e Exibição):** Criada uma nova tela 'Split-Screen' (\`/painel/\`) para ser exibida no telão do evento e usada pela organização. A tela conta com a grade de 16 mesas de jogo à esquerda e o Ranking interativo à direita.
  - **Refatoração do Backend de Confrontos:** A tabela \`Partida\` foi substituída por \`Confronto\` (numeração sequencial). Implementadas APIs \`/api/torneio/state/\`, \`/api/torneio/ranking/\` e controles de Início/Encerramento das partidas (lidando automaticamente com a lista de espera e os pontos).
  - **Cálculo Dinâmico de Pontuação:** A regra de negócio foi internalizada; o ranking é classificado via: Vitórias > PG > PP > Saldo de Pontos, calculando o tipo de vitória (Simples, Capote, Rolha, Lisa) com base nos pontos perdidos.
  - **UX/UI:** O link "Chaves" do menu lateral foi desligado da aba painel de jogos. Foi adicionado um botão de acesso rápido verde ("Acessar Telão") exclusivamente na página inicial (Dashboard).
- **Pendente:**
  - (Mantidos os anteriores) Realizar limpezas de inscrições pendentes e possíveis polimentos pré-evento.

### 21/08/2026
- **O que foi feito:**
  - **Recibo Virtual & Live Preview:** Implementado espelhamento instantâneo via JS (two-way data binding) entre o modal de edição de Comprovantes e o visualizador HTML simulando um documento.
  - **Formatação Dinâmica do Recibo:** Adicionada regra (domain-formatacao-recibos.md) para renderizar o nome dos dois jogadores em linhas separadas e destacar o código (parse nativo do datalist de vínculo).
  - **Visibilidade Incondicional de Evidências:** Criada a regra (ux-visibilidade-evidencias.md) garantindo que documentos sistêmicos (ex: Recibos Virtuais) apareçam como atalhos coloridos nas tabelas de auditoria (gestao.html), ao lado dos anexos físicos.
  - **Parsing Flexível de Datas:** Ajuste em `api_criar_comprovante` para usar `parse_datetime` do Django (backend-parse-datas.md), resolvendo o bug onde os segundos omitidos pelo browser anulavam a data digitada pelo usuário.
  - **Regra de Downgrade Lógico:** Bloqueio aplicado em `gestao_fichas.html` e `js_ficha_unificado.html` para impedir que o botão "Validar Ficha" rebaixe uma inscrição que já esteja totalmente `Inscrita` (domain-status-inscricao.md).
  - **Arquitetura OCR e Rastreabilidade:** Consolidada a regra de manter cardinalidade e não renomear lotes de originais de forma destrutiva. O histórico é rastreado por um *Timestamp de Lote* entre as pastas `entradas/processadas/` e `arquivadas/`.
  - **Leitura Nativa Manual:** Realizada inserção manual de dupla com base na visão do Agente no PDF após falha de chave de API externa.
- **Pendente:**
  - (Mantidos os anteriores) Limpeza de registros fantasmas, cobrança de inscrições.
### 20/08/2026 (Noite)
- **O que foi feito:**
  - Implementação de funcionalidade de "Lixeira" (Soft-Delete) na tabela principal para purgar inscrições duplicadas.
  - Fix: Correção de bug de métricas (Cards não somando) devido a erro JS residual e filtros muito rígidos.
  - OCR Manual Direto: Executada a extração de relatório de pagamentos diretamente pelos agentes sem utilizar o ARGUS.
  - Refatoração Massiva (UI/UX): Unificação total dos modais de Comprovante de Pagamento da tela de Gestão e de Pagamentos, concentrando tudo num modal único (com Busca Rápida de vínculo, Lado-a-lado com Imagem e Status Completos).
  - Inserção de atalhos em lupa para auditoria imediata de fichas manuais, e atalho nos comprovantes para visualização das pastas locais vinculadas.
  - Fix Crítico: Resolução do fuso horário UTC x Manaus na desserialização de datas nos retornos da API.
- **Pendente:**
  - O usuário ainda precisará decidir se deseja que o Agente automatize as confirmações no Banco de Dados a partir da leitura do OCR (Extrato de Pagamentos processado).
  - Limpar as inscrições "fantasmas" (IDs 15 e 16) conforme previamente solicitado em sessão anterior.


### 20/08/2026
- **O que foi feito:**
  - Aplicação de backup 011 do banco.
  - Fix: Botões 'Excluir' e 'Editar' da tela principal (remoção de falha de injeção de dicionário nas views).
  - Ajuste de nomenclatura: 'ID' -> 'Código', 'Nº / Número da dupla' -> 'Ordem' (Em templates HTML e criação da regra .agents/rules/nomenclatura.md).
  - Tabela principal: Correção da ordenação monetária do Valor Declarado e inserção da coluna Banco. 
  - Tabela principal: Estado de paginação/ordenação salvo via stateSave (DataTables).
  - Feature: Criação completa da tela de Relatórios com ordenação (DataTables), filtros reativos (Geral, Potência, Loja) e otimização pesada com CSS para impressão em papel.
- **O que está pendente:**
  - Remoção de comprovantes órfãos (arquivos sem registro no banco).
  - Tratamento de inscrições pendentes para geração de dashboard da Tríade.

### [ 2026-08-19 ] - Auditoria Visual e UI/UX da Tríade
- **Visualização Nativa:** Abolimos os links cegos para novas abas. Arquivos (Pix e Fichas) agora renderizam miniaturas (Iframes/Imagens) diretamente na tabela.
- **Intervenção Humana (Split-View):** Implementamos o 'Split-View Modal' nas centrais. O usuário agora pode corrigir os dados falhos do OCR enquanto lê o documento lado a lado no mesmo pop-up.
- **Higienização de Inputs:** Backend adaptado para aceitar formatação brasileira de moedas (conversão de vírgula para ponto) e tolerância a datas/valores nulos.
- **Proteção Anti-Fantasma:** Tratamento contra ValueError nos templates para registros que perderam seus arquivos físicos, mantendo o sistema em pé e alertando visualmente o usuário ('Sem Arquivo').
- **Status:** Fluxos de vinculação manual na gestão finalizados. A revisão em massa já é funcional.
 🚀

---\n\n## 18 de Agosto de 2026

### Resultados do Dia
- **Native File Ingestion & OCR**: Pivotamos o modelo de extração. O sistema agora lê PDFs e extrai as fichas de forma nativa e local via scripts Python e modelos de visão, abandonando chaves de API externas. Os status das inscrições foram padronizados (Pendente, Validada, etc).
- **Correção da Autenticação Git Headless**: Diagnóstico de travamento do git push no processo de background (devido à falta de UI do Git Credential Manager). Implementação de uma nova Regra obrigando instruções manuais para o usuário rodar push.
- **Data e Hora de Inscrição**: O comprovante ganhou precisão de segundos, e seu momento de pagamento tornou-se oficialmente o *Ordenador Master* da Listagem de Inscrições.
- **Número Dinâmico de Inscrição (Nº)**: O ID de banco de dados foi ocultado e substituído por uma numeração baseada estritamente no ranking cronológico do pagamento.
- **Painel de Auditoria da Tríade**: Criada uma regra de arquitetura para a **Tríade de Entidades** (Dupla, Comprovante, Ficha). Implantado um painel no topo da Gestão mostrando totais, vínculos e arquivos órfãos.
- **Desvínculo no Cancelamento**: Criada regra onde alterar uma inscrição para 'Cancelada' ou 'Purgada' rompe automaticamente os laços com seus arquivos (comprovante/ficha), devolvendo-os ao pool de órfãos.

### Próximos Passos
- Apagar os comprovantes fantasmas/órfãos detectados na varredura.
- Iniciar a cobrança/tratamento das inscrições pendentes baseadas no Dashboard da Tríade.

---



## 17 de Agosto de 2026

### Resultados do Dia
- **Refatoração de Skills de Rotina**: A regra genérica de rotinas diárias foi dividida e convertida em três *skills* autônomas especializadas (`github-bom-dia`, `github-salvar`, `github-ate-amanha`), adaptadas ao ambiente SQLite e aos padrões do projeto `torneio_macom_2026`.
- **Organização de Regras da IA**: O ambiente do Antigravity foi reorganizado para interpretar corretamente as regras inseridas em `.agents/rules/` e as novas skills em `.agents/skills/`.

### Próximos Passos
- (Mantidos os anteriores) Refinar validação OCR e ajustar estatísticas do painel.

---
## 14 de Agosto de 2026 - Sessão de Fechamento

### Resultados do Dia
- **Blindagem do Diário de Bordo**: Atualização nas regras globais e locais da IA para impedir peremptoriamente a exclusão ou sobrescrita do arquivo de Diário de Bordo. A regra agora exige a preservação rigorosa do histórico.
- **Rotina de Backup**: O processo de finalização do expediente ("Até amanhã") agora engatilha compulsoriamente (1) backup em cópia do banco de dados SQLite e (2) um commit no Git antes da despedida.

### Próximos Passos
- (Mantidos os anteriores) Refinar validação OCR e ajustar estatísticas do painel.

---

## 14 de Agosto de 2026

### Resultados do Dia
- **Sistema de Aprovação Manual**: Implementada a interface no `gestao.html` para aprovação rigorosamente manual de inscrições via botão (laranja/verde neon) dentro do modal do comprovante, bloqueando aprovação via automações.
- **Identidade Visual**: Ajustados os tons para verde neon (`#00ff66`) nas badges e alertas de sucesso por toda a interface de gestão.
- **Anexos Múltiplos no Banco**: Adicionado o campo `ficha_inscricao` no modelo `Dupla` e criadas migrações, separando o comprovante de pagamento da ficha de inscrição para as duplas manuais.
- **Processamento Híbrido de OCR**: Atualizado o motor de inteligência que lê as imagens. A estratégia agora usa o `PyMuPDF` (fitz) para gerar imagens em alta resolução de PDFs escaneados, e também cruza a extração de texto do Tesseract com o **nome do arquivo**.

### Decisões e Cuidados
- **Arquitetura de Arquivos**: Adotada a regra estrita `.gemini/rules/torneio-file-architecture.md` (entrada em `static/img/...` e destino renomeado com ID em `media/...`).
- **Problema de Travamento no Windows (WinError 32)**: Encontramos um gargalo onde o leitor de PDF travava o arquivo impedindo a exclusão ou movimentação. A solução foi adotar a leitura por `io.BytesIO` (memória) isolando o arquivo original, e passar a **mover** o original para uma subpasta `processados` ao invés de tentar deletá-lo logo após o fatiamento.
- **PDF de Imagem vs Texto**: O `pdfplumber` foi substituído pelo `PyMuPDF` para ler PDFs das inscrições manuais, pois essas fichas são essencialmente fotos escaneadas dentro de um container PDF.
- **Regras Globais da IA**: Extraímos a regra do Diário de Bordo para o diretório global da máquina (`~/.gemini/config/rules/diario-bordo.md`), permitindo que a prática seja reaproveitada nativamente em outros projetos.

### Próximos Passos
- Refinar a correspondência do OCR (talvez melhorar a validação fuzzy) para os arquivos que ainda caem na `revisao-pendente` por causa de caligrafia muito difícil de ler.
- Começar a lapidar as estatísticas do painel ou avançar com a interface pública das chaves do torneio, conforme a próxima solicitação do desenvolvedor.
