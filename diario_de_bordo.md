# Diário de Bordo 🚀

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
