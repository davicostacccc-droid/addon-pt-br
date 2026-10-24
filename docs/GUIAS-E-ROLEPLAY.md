# Referências de guias e apresentação em 3D — 24/10/2026

## Guias fornecidos pelo jogador

Foram consultados os repositórios indicados, sem instalar addons, executar seus
scripts ou incorporar seus recursos de automação ao AzerothVoz.

- [ZygorGuidesPlus](https://github.com/ErebusAres/ZygorGuidesPlus_3.3.5a-WOTLK):
  o README informa origem comunitária para TrinityCore e recomenda outro projeto
  Remaster como sucessor. A árvore inclui arquivos de guias CATA e MOP; a amostra
  CATA tem passos para monge e IDs posteriores a WotLK. Não é uma base homogênea
  do cliente 12340 apesar do nome do repositório.
- [RestedXP backport](https://github.com/PottedSalame/RestedXP_RXPGuides-WotLK_3.3.5a):
  o README declara build 12340, testes sobretudo em AzerothCore e guias de ambas as
  facções até nível 80. A árvore tem coleções de diversas eras. Foram inspecionados
  especificamente Guides/WotLK/Alliance-Leveling.lua e Horde-Leveling.lua.

Os passos usam comandos como accept/turnin, IDs e instruções curtas de rota. Isso
é útil para conferir identidade e sequência de missões. Não substitui os textos
completos dos diálogos de apresentação, andamento e conclusão ou o áudio ptBR.

## Cruzamento pontual por arquivo

| Amostra | IDs de aceitar/entregar distintos | Coincidem com a seleção de Northrend |
|---|---:|---:|
| Zygor Alliance CATA | 3.920 | 919 |
| Zygor Horde CATA | 4.202 | 905 |
| RestedXP WotLK Alliance | 758 | 742 |
| RestedXP WotLK Horde | 722 | 704 |

As contagens não devem ser somadas: há IDs repetidos entre arquivos e facções.
São resultados de leitura textual de uma amostra, não um inventário completo de
todas as rotas, disponibilidade no servidor ou validação das traduções.

Metadados e hashes ficam em data/guide-reference-summary.json; os arquivos externos
completos ficam em research/ e não são publicados no GitHub do AzerothVoz.
Nenhum passo de autoaceitação, entrega automática ou escolha de recompensa foi
adicionado. Zygor e RestedXP continuam independentes e não são dependências.

## Evidências para o modo roleplay no cliente antigo

- [FrameXML 3.3.5: PetPaperDollFrame.lua](https://github.com/wowgaming/3.3.5-interface-files/blob/main/PetPaperDollFrame.lua)
  usa SetUnit para o modelo de unidade e SetCreature no quadro de companheiros.
- [Esquema UI.xsd da mesma versão](https://github.com/wowgaming/3.3.5-interface-files/blob/main/UI.xsd)
  define PlayerModel, StatusBar e o script OnAnimFinished.
- [Inventário de métodos registrados no cliente 3.3.5](https://github.com/brues-code/ClassicAPI/blob/master/docs/BlizzardScriptAPI_3.3.5.md)
  lista SetUnit em PlayerModel e SetSequence, SetCamera, SetFacing e GetModel em Model.
- [SharedDefines.h do AzerothCore](https://github.com/azerothcore/azerothcore-wotlk/blob/master/src/server/shared/SharedDefines.h)
  identifica ANIM_STAND como 0 e ANIM_EMOTE_TALK como 60.

Essas referências sustentam as APIs escolhidas; não substituem teste no cliente.
Não foram usados ModelScene, SetPortraitZoom ou métodos de câmera exclusivos de
versões modernas. O cliente e seus executáveis não foram modificados ou inspecionados
em memória pelo projeto. A leitura do inventário acima é somente consulta documental.

## Comportamento implementado

O modelo usa SetUnit com o token de diálogo capturado no evento, somente quando
o GUID ainda corresponde ao ID do NPC da fala. Não troca o alvo do personagem.
Fora da conversa ou sem modelo carregado, usa símbolo neutro. Não usa SetCreature
para adivinhar modelos de NPCs distantes nem baixa arquivos de personagem.

Uma transição de opacidade destaca a moldura central. Um gesto genérico de fala
acompanha o estado do áudio; a barra usa sua duração. Não há análise de fonemas ou
sincronização exata dos lábios. Modelos não humanoides ou de patches HD podem
precisar de enquadramento específico; o usuário pode desativar o 3D.

O painel é arrastável, tem texto rolável e controles de Repetir/Parar/Minimizar.
Minimizar mantém a fala e devolve foco à janela nativa. Modo normal desativa a
apresentação. Aceitar missão e escolher recompensa continuam na interface do jogo.
Combate, fim de conversa, logout e desativação limpam modelo e fundo de destaque.

A captura existente salva textos ausentes, não vídeos. Não foi iniciada gravação
da tela, acessado microfone ou criada captura de mídia para esse recurso.

Os testes usam modelo simulado e Lua 5.1. Verificam GUID divergente, ausência/falha
de modelo, prévia sem NPC, alternância de modo e preservação das ações nativas.
O gesto e o enquadramento no WoW real aguardam a confirmação do jogador.
