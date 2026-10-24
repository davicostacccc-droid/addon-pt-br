# Diagnóstico técnico — 24/10/2026

**Conclusão:** um addon de tradução e dublagem PT-BR é viável no cliente original 3.3.5a / 12340 com conteúdo pré-processado. Os dois repositórios fornecidos já se destinam ao cliente antigo. Nenhum deles oferece tradução por IA e síntese neural em tempo real dentro do jogo. A comunicação contínua entre addon e auxiliar Windows não foi demonstrada nesta análise e não é requisito do primeiro protótipo.

## Evidências consultadas

| Fonte | Revisão / arquivo | Resultado da leitura |
|---|---|---|
| [QuestTradutor](https://github.com/leoaviana/QuestTradutor/tree/8e48b175cb48fe500a2af49a61fac21dc618aa63) | commit `8e48b175cb48fe500a2af49a61fac21dc618aa63`; `QuestTradutor.lua`, `Init/QuestTradutorInit.lua`, TOC e árvore | Base Lua pronta; sem chamada de IA |
| [QuestVoice](https://github.com/faralaks/wow-questvoice/tree/ef0b633e35dd32d83b1b6e21bd03de9454ebd832) | commit `ef0b633e35dd32d83b1b6e21bd03de9454ebd832`; cópia local fornecida v1.0.4; Lua principal, índices, busca fuzzy, TOC, licença | MP3s previamente preparados; eventos e GUID antigos |
| [FrameXML 3.3.5](https://github.com/wowgaming/3.3.5-interface-files) | `QuestFrame.lua`, `QuestInfo.lua`, `GossipFrame.lua`, `AudioOptionsPanels.lua`, consultados em 24/10/2026 | Nomes dos eventos, getters e componentes de interface antigos |
| ForeverVO da pasta REFERENCIA | TOC v0.1.10; `Core/Audio.lua`, `Capture.lua`, `Events.lua`, `Util.lua` | Referência moderna: depende de `C_CVar`, `C_Map`, GUID com hífens e identificadores de som; não é diretamente compatível |
| [Piper CLI](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md) e pacote instalado 1.4.2 | API Python `PiperVoice.load` / `synthesize_wav` exercitada com o modelo Faber | Geração neural real realizada offline |
| [Voz Faber](https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium) | `MODEL_CARD`, ONNX e JSON baixados com SHA-256 registrado em `models/provenance.json` | pt_BR, um locutor, 22.050 Hz; model card declara dataset CC0 |
| [API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md) | `/api/tags` e `/api/generate` | Integração opcional escrita; não validada contra serviço real neste computador |

O FrameXML é um espelho de código da interface, não uma execução do binário 12340 nem uma especificação completa das funções C do cliente. Portanto, leitura de código e testes simulados não comprovam áudio e layout no jogo. Fontes de referência baixadas para pesquisa foram preservadas separadamente e não entram no addon ou no repositório preparado.

## QuestTradutor: funcionamento e limites

- O TOC usa `Interface: 30300`, como esperado para WotLK 3.3.x, e carrega bancos Lua antes da inicialização.
- `QuestData_BR.lua` tem aproximadamente 8,7 MB na árvore consultada; `Gossip_BR.lua`, 1,8 MB; `QuestList.lua`, 0,5 MB. A estrutura prevê título, descrição, objetivos, progresso e conclusão por ID. Esses tamanhos são de arquivo, não uma medição de memória consumida no cliente.
- O código usa `GetQuestText`, `GetObjectiveText`, `GetProgressText`, `GetRewardText` e getters do diário. Preenche FontStrings da interface e expande marcadores do jogador.
- A resolução de ID busca o nono retorno de `GetQuestLogTitle`; fora do diário, recorre a listas por título e mecanismos adicionais para títulos duplicados. `GetQuestID` só aparece em um caminho condicionado a configuração: não é uma API que esta implementação assume disponível no cliente original.
- Gossip usa hash próprio, normalização de marcadores e `GS_Gossip`; há tratamento adicional de botões de opções e integrações com outras interfaces. Esse hash não é intercambiável com o índice do QuestVoice ou do AzerothVoz.
- Há um recurso de divulgação por chat (`SendChatMessage`) com configuração inicial habilitada. Ele não foi reaproveitado. O novo addon não envia mensagens a jogadores ou canais.
- O TOC observado persiste configurações; algumas tabelas internas de coleta não estão declaradas ali. Não se deve assumir que todo dado faltante coletado por ele persista entre sessões.
- Não foi encontrada licença explícita na árvore consultada. Não incorporamos sua base de traduções nem fontes. Não fizemos auditoria linguística de milhões de caracteres do banco; cobertura e qualidade não foram presumidas.

**Reaproveitamento possível:** usar o addon original separadamente ou, após esclarecer a licença, escrever um importador do banco. Isso pode aumentar muito a cobertura, mas exige revisão dos marcadores, diferenças por servidor e autorização de redistribuição. A primeira versão não modifica o QuestTradutor.

## QuestVoice: funcionamento e limites

- O TOC também declara `30300`. O Lua principal embute AceAddon/AceEvent/AceTimer, ouve `QUEST_ACCEPTED`, `QUEST_COMPLETE` e `GOSSIP_SHOW`, e cria botões de reprodução para o diário/gossip com adaptações a QuestGuru e Carbonite.
- `BuildVoiceAndDescription` monta caminhos `voices/quest/ID-accept.mp3`, `ID-complete.mp3` e `voices/gossip/HASH.mp3`. `Main:Play` chama `PlaySoundFile(voice)` com apenas o caminho, sem canal ou identificador de interrupção moderno.
- Para aceitação e seleção no diário, usa o nono retorno de `GetQuestLogTitle`. Para conclusão, busca a missão pelo título no diário: títulos iguais podem selecionar a missão errada e uma missão fora do diário não será resolvida por esse método.
- Para gossip, lê `UnitGUID('target')` no formato hexadecimal antigo e extrai o entry do NPC. O alvo selecionado pode diferir do interlocutor; o novo addon usa `npc`/`questnpc`, coerentes com FrameXML.
- `GossipToVoice` retorna diretamente a única fala cadastrada quando só existe uma opção, mesmo se o texto não corresponder. Se existem várias, a busca Levenshtein escolhe a menor distância sem limiar de rejeição.
- A matriz de distância usa tempo/memória proporcionais ao produto dos comprimentos dos dois textos, repetido por candidato. O novo addon faz uma busca indexada e verificação integral em vez dessa busca aproximada.
- `Main.played` evita repetição de uma fala de gossip durante a sessão, mas não é um cache gerador de IA. O temporizador chama `Play` usando campos mutáveis do objeto, podendo tocar uma fala mais nova se o diálogo mudar antes do atraso.
- Não há configuração de volume da narração, tradução, gerador TTS nem persistência de traduções nesse código principal.
- A árvore local fornecida contém código e índices; não contém o pacote de vozes inglesas. Não foi necessário baixar esse conteúdo.
- A licença do projeto é MIT; bibliotecas e conteúdo têm atribuições próprias. Os áudios ingleses não foram reutilizados.

**Reaproveitamento escolhido:** padrões comprovados no código de eventos antigos, identificação por GUID hexadecimal e caminhos de MP3. A lógica do protótipo foi escrita separadamente para evitar globais genéricas, a dependência de Ace e seleção aproximada de texto.

## Respostas às limitações solicitadas

| Pergunta | Diagnóstico e solução adotada |
|---|---|
| Lua pode chamar IA externa diretamente? | A sandbox de addon não oferece cliente HTTP, sockets, execução de processo ou arquivo arbitrário. IA roda fora do jogo. Não se usa `SendAddonMessage` como ponte para internet. |
| Precisa de auxiliar Windows? | Para gerar traduções/vozes, sim: ferramentas Python. Para ouvir pacotes já instalados, não. O primeiro auxiliar é um preparador de pacotes, sem processo permanente durante o jogo. |
| Áudio dinâmico recém-criado pode tocar? | O QuestVoice demonstra a abordagem de caminho para MP3 pré-instalado. O comportamento de arquivos novos ou substituídos durante a sessão não foi comprovado. O procedimento adotado exige jogo fechado na instalação. |
| Como identificar a missão antes de aceitar? | Sem inventar um `GetQuestID`: NPC + evento + texto normalizado, com verificação de texto integral. Um mesmo texto/locutor/etapa pode compartilhar áudio. O ID do diário é metadado quando único. |
| Como distinguir diálogos do mesmo NPC? | Cada texto tem seu registro. Mudança de pontuação, trecho ou marcador precisa de registro correspondente. Hash só seleciona o grupo; não autoriza a fala sem comparação integral. |
| Como sincronizar com a janela? | Captura do texto na chegada do evento; apresentação após 0,05 s para permitir atualização nativa. Fecha/para ao receber os eventos de encerramento correspondentes. Sem timers externos ou polling de rede. |
| Dá para parar a fala e controlar volume? | Neste protótipo, `PlayMusic`/`StopMusic` e `Sound_MusicVolume`, compartilhando o canal Música. Não se pressupõem retorno de handle de `PlaySoundFile`, `StopSound(handle)` ou canal Dialog moderno. A existência e o comportamento no binário precisam do teste do jogador. |
| Como saber se o arquivo foi ouvido? | Não há confirmação de reprodução pelo retorno de `PlayMusic` usada aqui. O gerador verifica existência, integridade e decodificação do pacote; só o teste no cliente confirma a reprodução. |
| Atualiza traduções/cache sem reiniciar? | Configurações em memória: imediatamente. Catálogo/manifesto Lua: novo carregamento de addon; o protótipo pede fechar o cliente para atualizar o pacote completo. SavedVariables não é um canal contínuo. |
| Tradução em tempo real? | Não implementada no cliente. Pacotes revisados são instantâneos após instalados; falas desconhecidas podem ser copiadas como JSON para processamento fora do jogo. |
| Reprodução externa sincronizada? | Exigiria uma ponte de eventos observável: OCR de tela, protocolo visual exibido por frames ou algum log explicitamente suportado. Cada alternativa exige prova no build original e estudo de foco/latência. Não presumimos leitura contínua de SavedVariables ou logs de chat como solução pronta. |
| Voz por raça/gênero/personagem? | Mapa explícito de NPC para modelo fornece consistência. O primeiro pacote tem uma voz. Não se presume que `UnitRace` descreva corretamente todos os NPCs, nem que personalidade possa ser obtida pela API. |

## Arquitetura implementada

1. **Catálogo JSON revisado:** texto de origem, NPC, evento, tradução, título/objetivos e texto falado opcionais. Traduções já preenchidas não são retraduzidas.
2. **Preparador Windows offline:** valida dados, resolve modelos por NPC, gera WAV neural com Piper, converte para MP3, guarda duração e SHA-256.
3. **Cache por conteúdo:** inclui texto, hashes do modelo e configuração, versão do motor e codificação. Arquivos íntegros são reutilizados. O modelo não precisa ser carregado quando todas as falas já estão em cache.
4. **Pacote Lua + MP3:** índice pré-computável por texto, exportado como literais escapados; nenhum JSON de captura é executado como código Lua.
5. **Addon 30300:** valida build 12340; observa cinco eventos antigos; usa janela própria e atualizações da interface padrão; controla reprodução e restaura volume no encerramento normal. Um crash antes de persistir SavedVariables não garante recuperação automática de configurações transitórias.
6. **Captura/exportação:** até 1.000 registros; JSON copiado manualmente. Não envia dados a terceiros. Nome do personagem é convertido em `$n` quando localizado como palavra; diálogos podem conter outras informações do servidor, por isso a revisão antes de compartilhar é necessária.

## O que ainda depende de confirmação

No cliente original: reprodução pelo canal Música, momento de volta da trilha ambiente, layout nativo, acentos, botões, eventos de transição, `questnpc`, variante exata da saudação no servidor, interação com outros addons e desempenho real. Integração com Ollama, vozes adicionais e expansão do banco são próximas etapas; não foram apresentadas como testadas.

O ZIP inicial é pequeno e contém duas gravações únicas: a demonstração própria e a saudação de McBride, compartilhada entre dois eventos. Não há cobertura automática de todas as missões. O próximo passo é o jogador validar `/avoz demo` e fornecer a captura de uma missão real da área em que joga, para gerar o primeiro pacote correspondente ao servidor e personagem.
