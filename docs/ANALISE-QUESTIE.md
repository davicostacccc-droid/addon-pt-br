# Questie-335 como referência complementar

Inspeção local em 24/10/2026 da cópia fornecida pelo usuário, identificada no TOC
como 9.9.4-335, Interface 30300. Arquivos somente lidos; nenhum Lua desse addon foi
executado e a instalação não foi modificada.

O README dessa cópia identifica a origem como Aldori15/Questie, ramo 335, e informa
que seus dados miram AzerothCore. Servidores com ajustes próprios podem divergir.

## O que encontramos

Contagem de linhas de registros com chave numérica explícita nos arquivos Wotlk:

| Arquivo | Registros |
|---|---:|
| Database/Wotlk/wotlkQuestDB.lua | 9.086 |
| Localization/lookups/Wotlk/lookupQuests/ptBR.lua | 8.462 |
| Localization/lookups/Wotlk/lookupNpcs/ptBR.lua | 26.450 |
| Localization/lookups/Wotlk/lookupItems/ptBR.lua | 36.742 |

Há 8.276 IDs em comum entre o arquivo base de missões e a tabela ptBR. Isso não
mede traduções completas nem missões efetivamente disponíveis para um personagem.

O esquema questKeys contém nome, NPCs/objetos/itens que iniciam a missão, quem a
conclui, objetivos, requisitos, nível, zona, pré-requisitos e sequência de missões.
Não define os diálogos completos de apresentação, andamento ou recompensa.
O campo objectivesText é um resumo de objetivos, apesar do comentário chamá-lo de
descrição. A tabela de localização tem nomes e textos resumidos; não é um banco
completo de conversas. Por exemplo, os objetivos de 788, 789 e 792 ainda estão em
inglês nessa tabela ptBR. Não foram encontrados MP3, WAV ou OGG nessa pasta.

## Aplicação no AzerothVoz

- Conferir relações por ID, sem usar apenas nomes traduzidos para identificar falas.
- Organizar filas de tradução por região e cadeia de missões.
- Conferir nomes e objetivos, mantendo correspondência com o cliente inglês.
- Continuar obtendo os diálogos completos de fontes adequadas e capturas do servidor.

Conferência pontual das cinco missões novas de 0.3.0: 792, 794 e 805 começam com
3145; 805 termina com 3188; 5441 e 6394 começam e terminam com 11378. Essas relações
batem com a seleção local do AzerothCore usada na compilação.

Nenhum arquivo do Questie foi incorporado ou distribuído no AzerothVoz. A pasta
inspecionada não apresentou licença geral na raiz; licenças de Icons ou Libs não
devem ser presumidas como autorização sobre todo o banco. Antes de uma importação
em massa será necessário localizar e conferir os termos da versão de origem.
Esta constatação não impede consultar a estrutura e conferir os IDs localmente.

A versão 0.3.0 continua independente do Questie. Ela não traduz automaticamente
o rastreador do Questie e sua coexistência real ainda precisa ser testada no jogo.
