# AzerothVoz PT-BR — protótipo 0.2.1

**Pacote local atual:** `dist/AzerothVoz-0.2.1-Durotar-12340.zip`. Mantém 16 etapas de seis missões do Vale das Provações, com ajustes para evitar a janela duplicada e traduzir rótulos/botões da janela nativa. [Teste da interface 0.2.1](docs/TESTE-0.2.1.md) e [cobertura de missões](docs/TESTE-DUROTAR-0.2.0.md). A gravação do jogador confirmou a saudação do Gornek e a apresentação de Dentes cortantes na 0.2.0; o jogador também confirmou que o ajuste 0.2.1 funcionou e ficou bom. As demais etapas ainda não foram todas confirmadas no jogo.

Este repositório contém código, ferramentas, textos revisados e testes. Os ZIPs instaláveis gerados localmente, áudios de terceiros, modelos e capturas não fazem parte do Git. Baixar apenas o código não fornece automaticamente todos os áudios do pacote local.

Tradução e narração para **WoW original 3.3.5a, build 12340**. O addon usa textos e MP3 locais. O programa Python prepara os pacotes no Windows com Piper, um sintetizador neural que funciona offline depois do download inicial.

Não é uma tradução completa do WoW. O pacote inicial 0.1.0 continha apenas a demonstração e uma saudação de McBride; a atualização Gornek acrescentou a fala capturada pelo jogador. Os procedimentos de geração básica abaixo continuam disponíveis; o novo recorte Durotar usa fontes e ferramentas adicionais descritas em `docs/INTEGRACAO-PACOTE-PTBR.md`.

## Teste rápido: pacote atual 0.2.1

1. Feche o WoW completamente.
2. Extraia `dist/AzerothVoz-0.2.1-Durotar-12340.zip`. Guarde uma cópia da pasta anterior antes de substituir **AzerothVoz** em `SuaPastaWoW/Interface/AddOns/`.
3. O caminho final precisa ser `Interface/AddOns/AzerothVoz/AzerothVoz.toc`.
4. Na seleção de personagens, ative AzerothVoz. Para o primeiro teste, desative outros addons de tradução/voz para evitar duas narrações ou disputa pelos textos.
5. Entre no jogo e digite `/avoz demo`. Uma janela deve exibir a demonstração em português e a voz deve tocar. É um texto demonstrativo criado para este projeto.
6. Digite `/avoz` para as configurações e teste o volume, ativar/desativar a voz e o botão Parar.
7. Use `/avoz previa` para testar Dentes cortantes (788) ou abra uma das seis missões listadas em `docs/TESTE-DUROTAR-0.2.0.md` para testar a detecção automática. A saudação anterior de McBride também foi preservada.

O script `scripts/Instalar.ps1` original usa a saída antiga `dist/release`; para o teste atual, utilize o ZIP indicado acima. Nenhum script foi executado contra sua instalação do WoW.

## Comandos no jogo

| Comando | Ação |
|---|---|
| `/avoz` | Abre configurações em Interface |
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
