# Integração do primeiro recorte de quests — 0.2.0

## O que foi realizado

Foi examinado o ZIP público oficial AI_VoiceOverData_Vanilla_ptBR_v0.1.zip, de Darkneo, CurseForge file 6516696. A página pública de download apontou para:

https://mediafilez.forgecdn.net/files/6516/696/AI_VoiceOverData_Vanilla_ptBR_v0.1.zip

Fonte e condições declaradas pelo autor:
https://www.curseforge.com/wow/addons/ai-voiceover-sounds-vanilla-ptbr-lowquality/files/6516696

O arquivo tem 2.084.719.906 bytes. Seu índice central e dez arquivos de metadados foram lidos por HTTP Range; nenhum Lua do pacote foi executado. Ele contém 6.334 MP3s de missões e somente um MP3 de gossip. As tabelas de busca cobrem mais textos do que os áudios disponíveis, portanto tabela presente não é prova de gravação existente. O TOC declara Interface 100000, inadequado para carregar diretamente no cliente original sem uma camada adaptada.

Foram obtidos 15 MP3s candidatos para seis missões: 4641, 788, 789, 790, 804 e 4402. A transferência parcial desse lote, incluindo o índice ZIP, foi de 6.642.989 bytes. Os membros foram conferidos pelo CRC do ZIP. Sua proveniência, hashes e transcrições automáticas ficam em research/voiceover-ptbr/, ignorado pelo Git.

## Dados e revisão

As fontes inglesas e relações de NPCs vieram de AzerothCore, data/sql/base/db_world, tabelas quest_template, quest_offer_reward, quest_request_items, creature_queststarter e creature_questender. Os blobs consultados foram respectivamente:

- quest_template: 9ebf71c00c7be4be350c614b05797e87effc1557
- quest_offer_reward: eedc87c99a17e041633900c8af34f843ee6cfb2d
- quest_request_items: b95b3e30a9dcaa7683b7aa2f376152cd69178c9e
- creature_queststarter: 9964476aac06acceb22960febc325e9392fb5d94
- creature_questender: f6e25c628c09d0a688bf951038918a1d81e7d739

São dados de referência, não uma exportação do servidor do jogador. Diferenças no texto são recusadas pela correspondência integral e ficam disponíveis para captura. O título não é usado sozinho para escolher a missão: duas quests chamadas Sarkoth foram associadas separadamente por NPC e texto.

As traduções do recorte foram escritas/revisadas em data/durotar-translations.json a partir das fontes inglesas. O banco ptBR de 7.872 registros permaneceu em preparação e não foi presumido correto para todo o cliente antigo.

Os 15 áudios foram decodificados e transcritos automaticamente com Whisper tiny local para triagem. A transcrição não é revisão auditiva certificada. Na apresentação de 789 ela indicou dez caudas, enquanto a fonte inglesa exige oito; esse áudio foi substituído por Piper local com oito. A etapa de andamento de 788 não tinha áudio no ZIP e também foi sintetizada. Resultado: **14 áudios externos reutilizados + 2 narrações locais**, formando 16 etapas de seis quests.

As gravações são de um pacote experimental de IA, não são as gravações de Jaina/Thrall do patch anterior. A qualidade precisa ser avaliada pelo jogador. Textos e áudio usam equivalentes de locais/itens em português; nomes ingleses úteis foram mantidos no texto de objetivos para orientar o cliente enUS. Chamadas genéricas como aventureiro no áudio são usadas no lugar do nome/classe do personagem.

## Mudanças no addon

- Nova versão 0.2.0 para TOC 30300 / build 12340.
- Expansão controlada de marcadores de origem $N/$C/$R/$B e gênero $g antes da comparação integral.
- Índice de templates limitado ao NPC e evento, sem busca fuzzy global.
- Prévia manual `/avoz previa` (788), `/avoz previa 4641` ou outro ID do recorte.
- Gameplay continua baseado nos eventos antigos e nos textos reais do cliente. A prévia não aceita ou entrega quests.

## Verificação

32 testes passaram. A entrega gerada foi exercitada em Lua 5.1 com 16 verificações de eventos de quests, conferindo NPC/etapa/ID, tradução, reprodução simulada e encerramento. Foram verificados os dois comandos de prévia e a recusa de texto diferente do servidor. Os 19 arquivos únicos de áudio da entrega foram decodificados e seus hashes/durações conferidos. O ZIP foi comparado byte a byte com a pasta gerada.

O relatório completo fica em dist/durotar-0.2.0/VERIFICACAO.json. Isso não comprova a versão 0.2.0 dentro do jogo; a confirmação é do jogador.

## Arquivos e limites

- Entrega: dist/AzerothVoz-0.2.0-Durotar-12340.zip.
- Pasta gerada: dist/durotar-0.2.0/AzerothVoz.
- Ferramentas: tools/http_range_zip.py, download_durotar_samples.py, build_durotar_pack.py.
- Bases e áudios de terceiros ficam em research/ e dist/, fora do Git. A licença do pacote externo é All Rights Reserved; esta é uma cópia local pequena para avaliação pelo jogador, sem publicação de gravações no GitHub.
- O MPQ e a instalação do jogo não foram alterados.

Não foi implementada geração de falas inéditas em tempo real. O resultado desta etapa é reprodução automática dos registros de um pacote pré-preparado, com captura apenas para ausências/diferenças. A próxima ampliação depende do resultado do teste deste recorte no servidor do jogador.
