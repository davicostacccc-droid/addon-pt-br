# Importação em lote — investigação de 24/10/2026

O jogador confirmou que se referia ao site Wowhead, sem um arquivo local de banco de dados. O objetivo é reduzir a captura manual a exceções, preparando catálogos amplos fora do jogo.

## Wowhead

Foram encontradas páginas WotLK em português com descrições, objetivos e conclusão de missões. A consulta direta ao NPC Gornek e a outras páginas retornou verificação antirrobô. Não foi comprovado acesso a um export completo ou uma API pública para todo o catálogo. Não se realizou coleta em massa nem se contornou a verificação.

Um catálogo de nomes de NPCs não garante a disponibilidade dos textos de suas conversas. A associação deve usar IDs de quest/NPC, etapa e texto de origem; nomes são apenas auxiliares. IDs compartilhados entre versões também não garantem que os objetivos, quantidades ou diálogos sejam iguais.

Fontes consultadas:

- https://www.wowhead.com/wotlk/pt
- https://www.wowhead.com/wotlk/pt/npcs
- https://www.wowhead.com/wotlk/pt/quest=13158
- https://www.wowhead.com/wotlk/pt/npc=3143

## Base alternativa já importada para análise

Um colaborador do AzerothCore publicou um dump ptBR de quest_template_locale, capturado no Wrath Classic e adaptado à estrutura do AzerothCore. Foi baixada a revisão fixa e importada localmente como dados, sem executar SQL, sem servidor de banco e sem modificar o WoW.

- Indicação e contexto: https://github.com/azerothcore/azerothcore-wotlk/issues/14209
- Fonte: https://gist.github.com/heyitsbench/ab41711d41c6eb137d053100c51841da
- Revisão: 609cfda4cbdece4044e0fc1b07abdf89223a0bce
- Arquivo: acstruclocdump-ptbr.sql
- SHA-256: a7fdd9065429a87eae327c60afe8a158f984735d2cdaf5dc86259b71ecbc5cc7
- Registros ptBR únicos importados: **7.872**.
- Todos informam VerifiedBuild **47168**, não 12340.
- Títulos não vazios: 7.871; descrições não vazias: 6.780; objetivos não vazios: 6.778.
- Há campos ainda em inglês. A contagem de não vazios não representa quantidade de traduções completas ou corretas.
- CompletedText é texto de estado/conclusão do diário, não deve ser confundido com a fala de entrega GetRewardText. Progresso e recompensa precisam das tabelas e fontes correspondentes.
- O dump contém apenas quest_template_locale. Não contém gossip, cadastro completo de NPCs, relações de ofertantes/finalizadores nem áudio.
- Alguns nomes foram localizados; será necessário conciliar essa opção com a preferência do jogador por preservar nomes no cliente inglês.

Os arquivos e o JSON importado ficam em research/, ignorado pelo Git. Não foram incluídos em um novo addon, compactados para distribuição ou publicados no GitHub. A fonte não foi tratada como licença automática para redistribuir todo o conteúdo; a publicação e as atribuições precisam ser avaliadas quando o pacote estiver pronto.

## Ferramenta criada

tools/import_quest_locale_sql.py lê somente literais de INSERT INTO quest_template_locale, preserva marcadores e identifica IDs duplicados. Não executa os comandos do SQL. Produz um índice JSON de preparação e um relatório que declara playable=false. Os testes cobrem aspas, vírgulas, marcadores, duplicatas e rejeição de expressões executáveis.

```powershell
.\.venv\Scripts\python.exe tools/import_quest_locale_sql.py research/acstruclocdump-ptbr.sql --out research/outra-importacao --source-url https://gist.github.com/heyitsbench/ab41711d41c6eb137d053100c51841da
```

Resultados atuais: research/ptbr-staging/quest-translations.json e audit.json. A suíte passou com **29 testes** após a adição do importador.

## Trabalho restante para transformar em pacote jogável

1. Cruzar com os textos ingleses, IDs e relações de NPCs de uma base 3.3.5 adequada.
2. Separar diferenças de Classic/servidor e campos vazios ou em inglês.
3. Adaptar os marcadores de nome, classe, raça, gênero e quebras de linha, preservando o sentido e a correspondência.
4. Obter/importar separadamente as falas de progresso, recompensa e gossip.
5. Gerar as vozes somente para registros validados, em lotes com cache; agrupar os pacotes por região para facilitar downloads e testes.

Essa etapa é uma importação e auditoria reais, ainda não uma ampliação instalada da cobertura do addon. A versão Gornek permanece intacta e utilizável enquanto se prepara a base maior.
