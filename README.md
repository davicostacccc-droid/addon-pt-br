# AzerothVoz PT-BR — 0.5.0-beta1 Northrend e Roleplay

**Beta local:** `dist/AzerothVoz-0.5.0-beta1-Northrend-Roleplay-12340.zip`. Amplia a cobertura de Northrend preservando Kalimdor, com traduções importadas experimentalmente e narração local. Acrescenta uma apresentação central opcional com modelo 3D do interlocutor quando disponível, texto rolável, entrada suave e controles. Não cobre 100% das missões ou de todas as etapas. [Instalação e teste](docs/BETA-NORTHREND-RP.md). A versão ainda aguarda confirmação no cliente; a beta Kalimdor anterior continua preservada em `dist/AzerothVoz-0.4.0-beta1-Kalimdor-12340.zip`.

As contagens regionais e combinadas estão em `COBERTURA.json` no pacote; cobertura não certifica a exatidão de cada tradução. A confirmação do jogador das versões anteriores não valida a interface 3D nova. A [análise dos guias Zygor/RestedXP e APIs antigas](docs/GUIAS-E-ROLEPLAY.md) explica as referências consultadas. O [resumo da beta Kalimdor anterior](data/beta-kalimdor-0.4.0-summary.json) continua disponível para comparação.

Recorte atual: **1.903 de 2.087 IDs de Northrend** com ao menos uma etapa, sendo 772 com todas as etapas de diálogo da referência. O pacote combinado tem 3.696 IDs com alguma etapa e 6.685 etapas distintas. Faltam 184 IDs regionais e há missões parciais. As novas vozes usam timbre padrão; o 3D usa a unidade real da conversa e símbolo neutro nas prévias sem NPC. Consulte o [resumo de verificação 0.5.0](data/beta-northrend-0.5.0-summary.json).

Este repositório contém código, ferramentas, textos próprios revisados e testes. Os catálogos completos importados da beta, ZIPs instaláveis gerados localmente, áudios de terceiros, modelos e capturas não fazem parte do Git. Baixar apenas o código não fornece automaticamente todos os textos e áudios do pacote local. As traduções importadas da beta não foram todas revisadas manualmente e as novas vozes usam um timbre padrão compartilhado.

Tradução e narração para **WoW original 3.3.5a, build 12340**. O addon usa textos e MP3 locais. O programa Python prepara os pacotes no Windows com Piper, um sintetizador neural que funciona offline depois do download inicial.

Não é uma tradução completa do WoW. O pacote inicial 0.1.0 continha apenas a demonstração e uma saudação de McBride; a atualização Gornek acrescentou a fala capturada pelo jogador. Os procedimentos de geração básica abaixo continuam disponíveis; o novo recorte Durotar usa fontes e ferramentas adicionais descritas em `docs/INTEGRACAO-PACOTE-PTBR.md`.

## Teste rápido: beta Northrend e Roleplay

1. Feche o WoW completamente.
2. Extraia `dist/AzerothVoz-0.5.0-beta1-Northrend-Roleplay-12340.zip`. Guarde uma cópia da pasta anterior antes de substituir **AzerothVoz** em `SuaPastaWoW/Interface/AddOns/`.
3. O caminho final precisa ser `Interface/AddOns/AzerothVoz/AzerothVoz.toc`.
4. Na seleção de personagens, ative AzerothVoz. Para o primeiro teste, desative outros addons de tradução/voz para evitar duas narrações ou disputa pelos textos.
5. Entre no jogo e digite `/avoz demo`. Uma janela deve exibir a demonstração em português e a voz deve tocar. É um texto demonstrativo criado para este projeto.
6. Digite `/avoz` para as configurações e teste o volume, ativar/desativar a voz e o botão Parar.
7. Use `/avoz cobertura` para consultar o recorte instalado e `/avoz rp on` para a apresentação central. As prévias funcionam longe dos NPCs, com símbolo neutro no lugar do modelo. Depois abra missões disponíveis normalmente para testar a detecção real e o 3D do interlocutor. `/avoz rp off` volta ao modo anterior; `/avoz modelo off` conserva a moldura sem 3D.

O script `scripts/Instalar.ps1` original usa a saída antiga `dist/release`; para o teste atual, utilize o ZIP indicado acima. Nenhum script foi executado contra sua instalação do WoW.

## Bases e cobertura

A [análise consolidada das fontes](docs/FONTES-CONSOLIDADAS.md) reúne AzerothCore, Questie, WotLKDB, Cavern of Time, traduções e áudios. O cruzamento local identificou 2.952 IDs com candidatos a texto e alguma gravação; eles ainda exigem revisão e não representam cobertura instalada. A ferramenta `tools/analyze_source_coverage.py` reproduz o inventário sem executar código externo.

A beta usa `tools/prepare_kalimdor_beta.py --region northrend` para selecionar e filtrar os candidatos locais, `tools/build_kalimdor_beta.py` com versão/região e pacote anterior para sintetizar com cache, e `tools/verify_kalimdor_beta.py --roleplay` para validar a entrega e criar o ZIP. O leitor `tools/read_lua_data.py` aceita somente tabelas literais; não executa os addons externos. Os comandos de geração básica abaixo continuam separados desse fluxo experimental.

## Comandos no jogo

| Comando | Ação |
|---|---|
| `/avoz` | Abre configurações em Interface |
| `/avoz cobertura` | Informa a cobertura parcial do pacote instalado |
| `/avoz rp on` / `/avoz rp off` | Ativa/desativa a moldura central de roleplay |
| `/avoz modelo on` / `/avoz modelo off` | Ativa/desativa o modelo 3D da moldura |
| `/avoz demo` | Mostra texto e reproduz a voz da demonstração |
| `/avoz parar` | Para a narração e restaura o volume anterior |
| `/avoz off` / `/avoz on` | Desativa / ativa o addon |
| `/avoz exportar` | Abre uma caixa de texto: Ctrl+C copia as falas sem tradução em JSON |

A tradução usa a janela nativa quando ela está visível e recebe o texto do pacote, com uma pequena barra Repetir/Parar. O leitor próprio com rolagem continua para prévias, falas pendentes e interfaces substitutas. `/avoz janela on` permite exibi-lo também junto da janela do jogo. O layout e a compatibilidade com outros addons precisam ser conferidos no cliente.

**Áudio e volume:** este protótipo usa o canal Música (`PlayMusic` / `StopMusic`), para poder interromper a fala sem depender de identificadores de som modernos. Durante a narração, a música ambiente é substituída e seu volume é temporariamente alterado. Ao fechar, parar ou terminar, o addon restaura o volume e a configuração anterior de Música. Não retoma a posição exata da trilha ambiente; o cliente controla o retorno da música de zona. A opção geral de som do WoW precisa estar ligada.

## Gerar um pacote no Windows

O ZIP pronto dispensa Python para jogar. Para gerar novos pacotes, use Python 3.12 e PowerShell na pasta deste projeto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/download_voice.py
.\.venv\Scripts\python.exe tools/build_pack.py --out dist/meu-pacote/AzerothVoz
```

`scripts/Preparar.ps1` reúne os comandos para a primeira geração em `dist/release/AzerothVoz`. Escolha sempre uma pasta de saída **nova**: o gerador recusa sobrescrever um pacote existente. O download inicial usa internet; geração e conversão de áudio são locais, sem serviço pago e sem chave de API.

O cache em `cache/` identifica a fala pelo texto narrado, pelo conteúdo do modelo e configuração de voz, pela versão do Piper e pelo formato de áudio. Repetir a geração em outra saída reutiliza MP3s válidos; não precisa sintetizar novamente. Não apague o cache se quiser reaproveitá-lo. O catálogo JSON revisado funciona como cache de tradução. A atribuição opcional de vozes por NPC fica em um JSON `{ "197": "C:/modelos/outra-voz.onnx" }`, passado por `--voice-map arquivo.json`. Cada modelo precisa de seu `.onnx.json`. Não se inferem raça ou personalidade de informações indisponíveis.

## Acrescentar diálogos reais

1. Converse com o NPC com captura ligada em `/avoz`.
2. Use `/avoz exportar`, copie com Ctrl+C e salve como `local-captures/capturas.json`, em UTF-8. A pasta é ignorada pelo Git. O texto pode conter informações inseridas pelo servidor; revise antes de compartilhar.
3. Importe em uma fila nova:

```powershell
.\.venv\Scripts\python.exe tools/import_captures.py local-captures/capturas.json --out local-captures/fila.json
```

4. Preencha `translation` em português. Preserve nomes próprios e `$n`. Campos opcionais: `title` (título traduzido), `objectives` (objetivos traduzidos), `spoken` (versão específica para narração). Sem `spoken`, a voz lê a tradução, usando “aventureiro” no lugar de `$n`; o texto exibido usa seu nome.
5. Para tradução automática local opcional, é necessário já ter Ollama e um modelo local instalado:

```powershell
.\.venv\Scripts\python.exe tools/translate_local.py local-captures/fila.json --model NOME-EXATO-LOCAL:TAG --out local-captures/traduzido.json
```

Essa integração opcional ainda não foi executada contra uma instalação real do Ollama. Não baixa modelos automaticamente. Revise cada tradução e remova `review_required` após conferir os termos; o gerador recusa falas ainda marcadas para revisão. Uma falha interrompe o lote, preservando a saída parcial; ela pode ser usada como nova entrada com outro arquivo de saída.

6. Gere o pacote apontando `--catalog` para o JSON revisado. Ele conterá as falas desse catálogo; para manter a demo e outros pacotes, reúna os registros em um só `lines[]` sem duplicatas.
7. Instale com o jogo fechado. Para substituir uma versão existente, faça backup manual após confirmar a atualização. Não há atualização de arquivo em tempo real nesta versão.

Eventos cobertos: descrição da missão (`QUEST_DETAIL`), andamento (`QUEST_PROGRESS`), conclusão (`QUEST_COMPLETE`), gossip (`GOSSIP_SHOW`) e saudação (`QUEST_GREETING`). O evento e o texto completo diferenciam as etapas. O ID de quest, quando encontrado sem ambiguidade no diário, é capturado como metadado; não é necessário supor que `GetQuestID` esteja disponível antes da aceitação.

## Limitações e segurança

- Addons do cliente original não têm HTTP, acesso arbitrário a arquivos ou execução de programas Windows. O addon não faz chamadas de IA dentro do jogo.
- SavedVariables são gravadas pelo cliente ao sair ou recarregar a interface; não são um canal de comunicação contínuo. O JSON pode ser copiado manualmente durante a sessão.
- Lua, listas de arquivos e manifestos novos exigem recarga/novo carregamento; a descoberta de novos áudios durante a sessão não está comprovada aqui. Instalar com o jogo fechado é o procedimento de teste.
- Sem injeção, leitura de memória do jogo, DLL, alteração de executável, automação de ações do personagem ou mensagens a outros jogadores.
- A correspondência exige NPC, evento e texto equivalente após normalizar apenas caixa ASCII e espaços. O hash é só um índice; o texto é conferido novamente. Não se escolhe “a fala mais parecida”. Variantes de servidor precisam de registros próprios.
- Há até 1.000 falas pendentes persistidas em SavedVariables, sem varrer bancos inteiros a cada frame. A limpeza manual deve ser decidida pelo usuário.
- A reprodução externa em tempo real por captura de tela/OCR ou protocolo visual é uma possibilidade a investigar; não foi implementada ou comprovada. Este pacote não depende disso.

## Testes de desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes usam **Lua 5.1 real**, através de Lupa, com APIs do jogo simuladas. Conferem eventos, GUIDs, seleção exata, exportação JSON, controles de volume e encerramento. Isso não substitui testes no cliente. Consulte `docs/TESTE-NO-JOGO.md` e `docs/DIAGNOSTICO.md`.

## Organização

`addon/AzerothVoz/`: Lua e TOC; `data/`: textos revisados; `tools/`: gerador/importador/tradutor; `scripts/`: preparação e instalação; `tests/`: testes automatizados; `docs/`: diagnóstico e teste manual; `dist/`: pacotes gerados; `models/` e `cache/`: arquivos locais ignorados pelo Git.

Referências: [QuestTradutor](https://github.com/leoaviana/questtradutor), [QuestVoice](https://github.com/faralaks/wow-questvoice), [FrameXML 3.3.5](https://github.com/wowgaming/3.3.5-interface-files), [Piper](https://github.com/OHF-Voice/piper1-gpl). Veja `THIRD_PARTY.md`. Para reprodução local, siga os requisitos e as fontes indicadas na documentação; modelos e gravações externas são obtidos separadamente, respeitando suas condições de uso.
