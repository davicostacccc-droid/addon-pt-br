# Fontes reunidas para o AzerothVoz

Análise de 24/10/2026. Alvo: cliente original 3.3.5a, build 12340.

## Decisão

As fontes se complementam. A base principal deve continuar sendo o conjunto de
tabelas do AzerothCore, com diálogos separados por etapa e relações por ID.
Questie ajuda a conferir objetivos, relações e cadeias. WotLKDB e Cavern of Time
ajudam a revisar diálogos e resolver dúvidas. As traduções ptBR entram como
candidatas revisáveis; gravações existentes entram somente após conferir a fala.

Isso permite preparar lotes maiores fora do jogo e reproduzi-los automaticamente
no addon. Não resolve tradução inédita em tempo real dentro do cliente antigo.

## O papel de cada fonte

| Fonte | O que ajuda a fornecer | Limite constatado |
|---|---|---|
| AzerothCore WotLK | IDs, texto inglês completo por etapa e NPCs de início/fim | Referência de servidor; Warmane pode ter variantes |
| Questie-335 fornecido | 9.086 registros de missões; objetivos, requisitos, cadeias e tabelas de nomes ptBR | Não contém todos os diálogos ou vozes; parte do ptBR está em inglês |
| WotLKDB | Páginas consultadas com descrição, andamento, conclusão, objetivos e relações | Consulta web; cobertura completa e exportação em massa não verificadas |
| Cavern of Time WotLK | Páginas consultadas com diálogos e relações de NPCs | Pode exibir marcadores já substituídos; não usar HTML como template canônico |
| Wowhead WotLK ptBR | Referência candidata para terminologia e localização | Consulta atual retornou apenas aviso de JavaScript; não foi validado um banco completo exportável |
| Dump ptBR de localização já obtido | 7.872 IDs, dos quais 6.780 têm Details preenchido | Build 47168, Wrath Classic; não garante texto do cliente original; há campos ingleses |
| QuestTradutor | Referência de interface e catálogo separado de quests/gossip | Não foi incorporado; termos de redistribuição do banco seguem por esclarecer |
| QuestVoice | Referência de reprodução no cliente antigo e organização por ID/etapa | Vozes inglesas; o próprio README alerta para textos diferentes e arquivos ausentes |
| Pacote Darkneo ptBR Vanilla | 6.334 MP3s de missões em 3.245 IDs | Não cobre todo WotLK; somente um MP3 de gossip; requer conferir conteúdo e condições de reutilização |
| Patch MPQ fornecido | Gravações e saudações ptBR já avaliadas pelo jogador | Não é uma narração de todas as quests; inclui conteúdo de outras eras |
| Piper local | Criar as falas que faltam sem serviço pago | Naturalidade e vozes por personagem precisam de refinamento |

Não foram somadas as quantidades entre fontes, pois os mesmos IDs aparecem em
vários lugares. Uma tabela de nomes não equivale a um diálogo traduzido.

## Cruzamento real dos arquivos locais

A ferramenta nova lê os índices e SQL como dados, sem executar Lua externo,
conectar a banco de dados ou alterar a instalação do jogo. Resultado:

- 9.464 IDs no quest_template inglês local do AzerothCore.
- 6.735 IDs em comum entre essa base, Questie e Details preenchido na localização ptBR.
- Desses, 2.952 também têm pelo menos um áudio no índice do pacote ptBR Vanilla.
- Desses 2.952, 1.134 têm arquivos para apresentação, andamento e conclusão.

Esses números representam **candidatos para revisão**, não missões prontas.
Details preenchido não prova que o texto esteja integralmente em português.
Nome de MP3 no ZIP não prova que sua fala corresponda à missão 3.3.5a.
Missões sem diálogo de andamento não precisam artificialmente de três etapas.
O arquivo `data/source-coverage-2026-10-24.json` guarda contagens e IDs, sem textos
completos de terceiros. Não inclui inventário integral dos sites.

## Conferências nos novos sites

Foi feita uma amostragem pequena, sem varredura em massa. O acesso de leitura web
falhou em algumas URLs do Cavern of Time; duas páginas foram lidas por HTTP normal,
com resposta 200, sem login e sem executar scripts.

1. Missão 789, Sting of the Scorpid: WotLKDB e Cavern of Time pedem oito caudas.
   Isso reforça a correção anterior do áudio que falava dez.
2. No andamento da mesma missão, Cavern of Time mostra uma classe fixa, warrior;
   WotLKDB conserva o marcador de classe. Importar a frase fixa impediria a
   correspondência correta para outras classes.
3. Missão 805, Report to Sen'jin Village: ambas as fontes mostram descrição e
   conclusão. O Cavern of Time relaciona os NPCs 3145 e 3188, concordando com
   Questie e AzerothCore. As páginas consultadas não exibem etapa de andamento.
4. Missão 788, Cutting Teeth: WotLKDB apresenta as três etapas e oito javalis,
   úteis para conferência do recorte já preparado.

Concordância entre sites não prova independência: eles podem compartilhar a mesma
origem de dados. A captura do texto real no servidor do jogador continua sendo o
critério final para a seleção dentro do jogo.

## Como juntar com segurança técnica

1. Identificar cada registro por questID, etapa, tipo/ID de quem fala e texto inglês
   com seus marcadores preservados. Para gossip, conservar NPC, evento e texto;
   nem todo gossip pertence a uma missão.
2. Guardar fonte, revisão ou hash e data da coleta. Não sobrescrever divergências.
3. Conferir tradução contra o inglês: números, objetivos, nomes, gênero e marcadores.
   CompletedText do diário não deve substituir RewardText do diálogo de conclusão.
4. Confrontar o áudio candidato com a tradução e a etapa; gerar localmente se faltar
   ou divergir. Manter o cache por texto e configuração da voz.
5. Compilar apenas registros revisados em pacotes por região. Usar índices por NPC e
   evento para não percorrer todos os textos durante cada conversa.
6. Testar Lua, seleção de falas, áudio e ZIP; depois solicitar o teste real no jogo.

O registro aprovado do jogador tem prioridade sobre diferenças de referência.
Traduzir títulos iguais por nome apenas continua sendo insuficiente.

## Acesso e reutilização

Cavern of Time apresenta aviso de direitos reservados; sua página Integrate oferece
tooltips para websites. Isso não documenta uma API geral para baixar o banco, nem
uma ponte de rede para addons. O robots.txt do WotLKDB permitiu navegação pública
na consulta atual; isso não constitui licença de redistribuição. Não foi localizada
permissão de exportação/republicação integral durante esta inspeção limitada.

Não houve download em massa dos sites ou cópia de seus bancos para o GitHub.
HTML de pesquisa fica somente em research/. Modelos, capturas, áudios de terceiros
e o MPQ continuam fora do repositório.

## Próxima prioridade

Ampliar a fila por região usando os IDs coincidentes, começando pelas missões em
torno do Vale das Provações e Sen'jin. Revisar primeiro os diálogos, e então gerar
as falas faltantes com uma atribuição explícita de voz por NPC. Os 2.952 candidatos
reduzem a pesquisa manual, mas não eliminam a validação de conteúdo.

Esta etapa acrescenta análise e ferramenta de inventário. A versão jogável continua
sendo 0.3.0, com 11 missões; nenhum desses totais foi instalado automaticamente.

## Reprodução da análise local

```powershell
.\.venv\Scripts\python.exe tools/analyze_source_coverage.py --research research --questie "CAMINHO/Questie-335" --out research/nova-analise.json
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

São necessários os arquivos de pesquisa previamente obtidos. A ferramenta recusa
sobrescrever relatórios existentes e não baixa arquivos nem modifica addons.

## Referências

- [Lista Cavern of Time](https://wotlk.cavernoftime.com/quests=1), [789](https://wotlk.cavernoftime.com/quest=789), [805](https://wotlk.cavernoftime.com/quest=805), [Integrate](https://wotlk.cavernoftime.com/integrate).
- [Lista WotLKDB](https://wotlkdb.com/?quests), [788](https://wotlkdb.com/?quest=788), [789](https://wotlkdb.com/?quest=789), [805](https://wotlkdb.com/?quest=805).
- [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk), [Wowhead ptBR](https://www.wowhead.com/wotlk/pt).
- [Questie ramo 335](https://github.com/Aldori15/Questie/tree/335), [análise da cópia local](ANALISE-QUESTIE.md).
- [QuestTradutor](https://github.com/leoaviana/questtradutor), [QuestVoice](https://github.com/faralaks/wow-questvoice).
- [Dump de localização](https://gist.github.com/heyitsbench/ab41711d41c6eb137d053100c51841da), [integração do pacote ptBR](INTEGRACAO-PACOTE-PTBR.md), [dependências e autoria](../THIRD_PARTY.md).
