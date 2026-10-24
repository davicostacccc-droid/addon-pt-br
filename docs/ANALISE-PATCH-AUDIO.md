# Análise do patch fornecido — 24/10/2026

## Conclusão

O arquivo ajuda como fonte local de gravações e referências de personagens, mas não deve ser tratado como uma dublagem completa de quests nem como conteúdo integralmente fiel à época do WotLK. A instalação no cliente não foi feita ou validada.

O jogador forneceu `[3.3.5a]patch-6 (noMaps) v1.rar`, de 504.434.900 bytes. Ele contém somente `patch-6.MPQ`, de 520.277.192 bytes. Foi extraído para research/patch-audio/, preservando o RAR e a instalação do jogo. Nenhum Lua/XML embutido foi executado. O MPQ não possui listfile acessível ao leitor utilizado.

SHA-256 do MPQ: `544ccfbfd9319939e84ce051b357a2d99b783428946fc6fdf4db019fb0b2922d`.

## Inventário real

Foram inspecionadas as assinaturas do primeiro setor dos blocos ativos. Há 15.847 entradas na tabela de blocos, sendo uma sem conteúdo ativo.

| Tipo reconhecido pela assinatura | Quantidade |
|---|---:|
| RIFF/WAV | 11.704 |
| MP3 | 11 |
| Tabelas DBC | 57 |
| Texturas BLP | 4.055 |
| Lua/texto/legendas | 13 |
| XML de interface | 4 |
| Outros | 2 |

Uma lista pública de caminhos de sons de 3.3.5a permitiu associar **11.378 blocos** a nomes conhecidos. Outros quatro caminhos de interface foram confirmados separadamente. Isso é associação por hashes do MPQ, não inferência de personagem por nome de arquivo extraído ao acaso.

Lista usada: https://github.com/fondlez/wow-sounds/blob/main/wotlk/wow-sounds-ALL-wotlk-3.3.5a.csv

Entre os caminhos reconhecidos estão saudações da Jaina e do Thrall, diálogos/eventos de vários personagens, sons de personagens jogáveis e onze narrações de introdução de raça/classe. Não foi encontrado caminho com o nome Gornek nessa lista identificada; isso não prova que nenhum som genérico usado por ele exista.

Foram confirmados os caminhos DBFilesClient/Spell.dbc, Achievement.dbc, QuestInfo.dbc, QuestSort.dbc, CreatureFamily.dbc, ChrRaces.dbc, Faction.dbc e SkillLine.dbc. QuestInfo e QuestSort são tabelas auxiliares; sua presença não significa que o arquivo contenha todos os textos de missões enviados pelo servidor.

O patch também contém GlobalStrings.lua, GlueStrings.lua e alterações de arquivos de login/interface. Portanto, ele não contém apenas áudio. Não foi feito comparativo integral desses arquivos com o FrameXML original.

## Amostras verificadas

Quatro amostras foram extraídas e decodificadas fora do jogo. Reconhecimento de fala foi executado localmente com faster-whisper 1.2.1 / modelo tiny multilíngue, CPU int8. As transcrições são automáticas e contêm erros; não são legendas revisadas nem prova da identidade dos dubladores.

- **JainaProudmooreGreeting01.wav:** detecção de português com probabilidade aproximada de 0,998. O reconhecimento indica uma saudação a Theramore e menção a ajudar a Aliança.
- **ThrallGreeting02.wav:** português, probabilidade aproximada de 0,676; indica uma saudação a Orgrimmar e referência a servir à Horda. Precisa de conferência auditiva para transcrição exata.
- **ThrallGreeting01.wav:** classificação automática inconclusiva. O modelo indicou outro idioma com confiança baixa; falas curtas ou em língua fictícia não são confiáveis para identificação automática.
- **Primeiros 25 segundos de OrcNarration.mp3:** português, probabilidade aproximada de 0,995. A transcrição menciona Cataclismo, Thrall deixando a liderança e Garrosh assumindo como chefe guerreiro. Esse trecho descreve uma situação posterior à época de WotLK, mesmo estando no caminho antigo de áudio.

A evidência permite afirmar que existem gravações em português e pelo menos uma introdução com conteúdo de época posterior. Não foi verificado o idioma de todos os 11.715 arquivos com assinatura de áudio, a origem oficial das gravações, a identidade dos locutores ou a cobertura de todas as falas de missões.

## Uso para o AzerothVoz

1. Catalogar as falas existentes por personagem, finalidade e texto efetivamente pronunciado.
2. Preferir gravações existentes quando o diálogo e a época corresponderem ao conteúdo do cliente/servidor.
3. Distinguir saudações genéricas, falas de combate, cenas e narração de quests. Uma saudação não pode substituir a leitura de uma missão inteira.
4. Para textos sem gravação correspondente, continuar a geração local com vozes selecionadas por personagem. O modelo Faber do protótipo é genérico e o simples fornecimento deste patch não altera sua identidade vocal nem o transforma num gerador das vozes encontradas.
5. Conferir raça, gênero quando conhecido, ritmo e caráter da interpretação para melhorar a consistência. Fidelidade ao conteúdo de 3.3.5 deve ter prioridade sobre a reutilização indiscriminada de introduções posteriores.

Os arquivos de áudio, MPQ, lista de nomes e transcrições ficam somente em research/, ignorado pelo Git. Não foram incorporados ao ZIP do addon nem publicados. Antes de redistribuir gravações do patch, é necessário conhecer sua origem e condições de uso. A análise local não determina uma licença de redistribuição.

## Reproduzir o inventário

O leitor opcional é tools/inspect_mpq.py, instalado com requirements-research.txt. Usa mpyq apenas para ler tabelas e hashes; não abre o jogo, escreve no MPQ ou instala conteúdo.

```powershell
.\.venv\Scripts\python.exe tools/inspect_mpq.py research/patch-audio/patch-6.MPQ --names research/patch-audio/wotlk-sounds.csv --out research/patch-audio/nova-auditoria.json
```

Relatórios locais: audit-final.json, identified.json e sample-transcriptions.json em research/patch-audio/. A inspeção de assinaturas não substitui validação de todos os setores/CRCs e reprodução de todos os sons. O arquivo anexado não foi instalado e sua compatibilidade prática permanece pendente.
