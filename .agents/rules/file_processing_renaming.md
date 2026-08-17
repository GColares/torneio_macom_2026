# Regra de Renomeação de Arquivos Processados

Sempre que você (o assistente) ler, analisar ou extrair dados de qualquer arquivo (seja foto, imagem, PDF ou outro formato) que estiver localizado dentro das seguintes pastas (incluindo todas as suas subpastas):
- `img/comprovantes-pagamento`
- `img/inscricoes-manuais`

## 1. Em caso de Sucesso na Leitura
1. Renomeie o arquivo lido adicionando o prefixo `processado_` seguido da data e hora atual no formato `YYYY-MM-DD_HH-MM`.
2. **Padrão:** `processado_YYYY-MM-DD_HH-MM.extensão`.
   - Exemplo: `processado_2026-08-14_17-05.pdf`.
3. **Exceção:** Se o arquivo já começar com `processado_`, não o renomeie.

## 2. Em caso de Falha na Leitura (Arquivo ilegível, borrado, etc.)
1. **Renomeie o arquivo** adicionando o prefixo `falha-leitura_` seguido da data e hora no formato `YYYY-MM-DD_HH-MM`.
   - Exemplo: `falha-leitura_2026-08-14_17-09.pdf`.
2. **Mova o arquivo** para uma subpasta chamada `revisao-pendente/` que deve estar dentro do diretório original onde o arquivo estava.
3. **Notifique o Usuário:** Avise imediatamente no chat qual arquivo falhou e que ele foi enviado para a pasta de revisão pendente.

Isso garante a organização e facilita o tratamento manual posterior das inscrições problemáticas.
