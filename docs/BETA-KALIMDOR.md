# AzerothVoz 0.4.0-beta1 — Kalimdor

Beta ampla para o cliente original 3.3.5a / build 12340. Não é uma promessa de
100% das missões traduzidas, de todas as etapas ou de todos os gossips.
A contagem exata desta compilação está em COBERTURA.json e em `/avoz cobertura`.

## O que está incluído

- Regiões de Kalimdor, capitais, áreas iniciais draeneis, instâncias selecionadas e
  missões de classe/eventos relacionadas a NPCs encontrados nessas áreas.
- Descrições, objetivos e diálogos de andamento/conclusão onde há tradução
  candidata aproveitável. Cada etapa importada recebe narração local.
- As onze missões e gravações já presentes na 0.3.0 foram preservadas.
- Identificação por NPC, texto inglês completo e título original quando necessário.
- Para janelas sem NPC identificado, somente correspondência de texto/título sem
  ambiguidade. Não há dependência de uma API moderna de questID.
- Cache de áudios na preparação; o jogo apenas reproduz MP3s já incluídos.

Traduções novas são importadas de bases existentes, filtradas automaticamente e
**não foram todas revisadas manualmente**. O filtro rejeita cópias inglesas,
marcadores não suportados e algumas divergências numéricas; não detecta todo erro
de tradução, contexto, quantidade por extenso ou conteúdo de outra versão.

As vozes novas usam **Piper Faber pt_BR**, uma voz padrão compartilhada. Ainda não
há timbre próprio para cada NPC nem distinção confiável de raça/gênero. A narração
usa “aventureiro” para marcadores do jogador e uma forma fixa de gênero. O texto
exibido expande nome, classe, raça e marcadores de gênero suportados.

## Instalação

1. Feche completamente o WoW.
2. Guarde uma cópia da pasta AzerothVoz anterior.
3. Extraia a pasta AzerothVoz do ZIP em Interface/AddOns.
4. Confirme o caminho Interface/AddOns/AzerothVoz/AzerothVoz.toc.
5. Ative AzerothVoz. No primeiro teste, desative outros tradutores/narradores.

Este projeto não altera sua instalação automaticamente. Não instale os arquivos
Python, modelos ou ferramentas de pesquisa dentro do jogo.

## Teste rápido

Use `/avoz demo` e `/avoz cobertura`. Para ouvir a apresentação de uma missão já
incluída, use `/avoz previa ID`, por exemplo `/avoz previa 788`. Prévia não aceita
nem conclui missões. Para testar em situações reais, abra missões disponíveis em
Durotar, Mulgore, Teldrassil ou outra região de Kalimdor.

Confira se o texto corresponde à missão, se a voz está em português, se Repetir e
Parar funcionam e se fechar a janela interrompe a fala. Para problemas de interface,
use `/avoz janela on` como alternativa de leitura.

## Lacunas e limites

COBERTURA.json lista IDs sem nenhuma etapa aproveitável e os motivos de etapas
rejeitadas. As etapas preservadas da 0.3.0 têm prioridade sobre essa lista de rejeições
da importação. Missões com ao menos uma etapa não são necessariamente completas.
Algumas quests são históricas, de eventos, desativadas ou alteradas pelo servidor.
A seleção de referência não é um censo garantido do servidor Warmane.

Não foram incluídas traduções inventadas para preencher ausências. Quando não há
correspondência, a interface mostra o original e permite capturar com `/avoz exportar`.
O diário, o rastreador e os nomes de itens/NPCs do cliente não foram traduzidos
globalmente. Gossip genérico só tem as falas já existentes no pacote anterior.

Os arquivos novos são carregados com o cliente fechado. Não há IA, HTTP ou geração
de voz durante o jogo. Os testes automáticos usam Lua 5.1 com APIs simuladas e
validam os arquivos MP3; a beta depende da confirmação do jogador no cliente real.

## Fontes e preparação

Textos ingleses e relações: AzerothCore WotLK. Seleção complementar de NPCs: cópia
local Questie-335. Traduções candidatas: dump ptBR de Wrath Classic e QuestTradutor
(leoaviana/Platine). São referências de versões diferentes, sujeitas a revisão.
Nenhum código desses addons foi executado na importação.

Os bancos completos importados e o catálogo experimental ficam somente em
research/. Não são publicados no GitHub do projeto. O código das ferramentas e
os testes ficam no repositório. As referências de autoria não representam uma
licença para republicar os bancos ou gravações de terceiros.

Para reproduzir localmente, prepare os arquivos de pesquisa, preserve a saída
0.3.0 e o modelo Piper. Execute prepare_kalimdor_beta.py, build_kalimdor_beta.py
e verify_kalimdor_beta.py, escolhendo sempre saídas novas. As ferramentas recusam
sobrescrever entregas existentes e reutilizam o cache local.
