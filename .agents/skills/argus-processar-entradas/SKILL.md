---
name: argus-processar-entradas
description: Roda a rotina de OCR Inteligente (Gemini Vision) para fatiar, ler, deduplicar e organizar as Fichas de Inscrição Manuais e Comprovantes em PDF.
---

# Skill: Processar Entradas (OCR Inteligente)

Use esta skill sempre que o usuário pedir para o ARGUS "processar as fichas", "ler as fichas manuais", "ler os comprovantes" ou "rodar o OCR".

## 1. O que este script faz?
O comando Django `processar_entradas`:
- Vasculha as pastas `media/entradas/inscricoes-manuais/nao-processadas` e `media/entradas/comprovantes-pagamento/nao-processadas`.
- Abre cada PDF ou Imagem e fatia página por página (usando `PyMuPDF`).
- Usa a **Gemini Vision API** para ler os formulários preenchidos à mão e comprovantes de transferência.
- **Fichas Manuais**: Verifica no banco de dados se a dupla já existe. Se não existir, cria uma nova. Salva o PDF fatiado em `media/arquivadas/inscricoes-manuais` com o nome `ficha_dupla_<ID>_<TIMESTAMP>.pdf` e vincula o registro `FichaInscricao` à `Dupla`.
- **Comprovantes**: Verifica se consegue ler o nome ou encontrar a dupla. Vincula e salva em `media/arquivadas/comprovantes-pagamento`.
- **Originais**: Arquivos processados com sucesso recebem o prefixo `lido_<TIMESTAMP>_` e vão para a pasta `processadas/`. Arquivos ilegíveis ou com múltiplas inscrições onde uma falhou vão para `revisao-pendente/`.

## 2. Como Executar

Antes de rodar, verifique com o usuário se a variável de ambiente `GEMINI_API_KEY` está configurada ou se ele deseja fornecê-la temporariamente para esta execução.

Comando para rodar:
```powershell
python manage.py processar_entradas
```

### Se faltar a Chave (API Key)
Se o comando reclamar que a variável `GEMINI_API_KEY` não foi encontrada, oriente o usuário a rodar no terminal dele (PowerShell):
`$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"`

Ou peça a chave no chat e você mesmo pode setá-la temporariamente na execução do comando.

## 3. Pós-Execução
- Avise o usuário sobre quantas páginas foram lidas e se houve criação de novas duplas.
- Peça para ele verificar o painel e também checar a pasta `revisao-pendente` para ver se alguma página precisará de intervenção manual (ou seja, se a caligrafia estava tão ruim que a IA não conseguiu ler).
