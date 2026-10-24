# AzerothVoz 0.5.0-beta1 — Northrend e modo roleplay

Cliente alvo: World of Warcraft original 3.3.5a, build 12340.

Esta beta amplia a cobertura de Northrend e preserva o pacote de Kalimdor.
Não representa 100% de todas as missões e gossips. COBERTURA.json informa o recorte
regional e a cobertura combinada; COBERTURA-ANTERIOR.json preserva a análise anterior.
Traduções importadas continuam experimentais, sem revisão manual completa.
As novas falas usam a voz padrão Piper Faber local, sem serviço pago.

## Apresentação roleplay

Use `/avoz rp on` para ativar a moldura central com texto, nome do interlocutor e
modelo 3D quando a unidade de diálogo estiver disponível. `/avoz rp off` volta à
interface anterior. O modo pode ser escolhido também nas configurações `/avoz`.
O roleplay vem ativado por padrão nesta beta, caso ainda não haja uma preferência
salva. O painel pode ser arrastado para não cobrir controles da interface.

Há entrada suave, controles de texto e indicador de reprodução. O modelo usa a
unidade real da conversa somente quando seu ID corresponde à fala selecionada.
Se não há unidade válida, aparece um símbolo neutro; o addon não inventa um rosto.
Isso ocorre, por exemplo, em prévias feitas longe do NPC ou missões de objetos.

O gesto de fala usa uma sequência genérica do modelo, quando disponível. Não há
sincronização exata de fonemas ou dos lábios com o áudio. Formatos de criaturas e
patches de modelos podem exigir ajustes de enquadramento. Há alternativa sem 3D.

O modo não aceita, entrega ou escolhe missões/recompensas; essas ações continuam
na janela do jogo. Não é movida a câmera do mundo nem ocultado todo o HUD.
Fechar a conversa, desligar o addon ou entrar em combate encerra a apresentação.
Repetir e Parar controlam o áudio; fechar a apresentação volta ao texto normal.

## Instalação e teste

1. Feche o WoW completamente e guarde a pasta AzerothVoz anterior.
2. Extraia a pasta AzerothVoz deste ZIP para Interface/AddOns.
3. Ative AzerothVoz. No primeiro teste, desative outros tradutores/narradores.
4. Use `/avoz demo`, `/avoz cobertura` e `/avoz rp on`.
5. Converse com um NPC de uma missão incluída e confira nome, texto e modelo.
6. Teste Repetir, Parar, fechar a conversa e `/avoz rp off`.

As prévias `/avoz previa ID` funcionam longe dos NPCs, mas não exibem um modelo
de uma unidade inexistente. Elas não alteram o progresso das missões.

Se houver falha no 3D, use `/avoz modelo off` para manter a moldura e o texto sem
o modelo. `/avoz modelo on` tenta o modelo novamente na próxima fala.

## Cobertura e limites

O recorte considera as zonas de Northrend, Dalaran, algumas instâncias e missões
relacionadas a NPCs dessas regiões. Não é um censo garantido do servidor Warmane.
IDs com ao menos uma etapa não são necessariamente missões completas.

Há correspondência pelo texto inglês completo, NPC e título quando necessário.
Variantes do servidor e traduções ausentes continuam disponíveis para captura com
`/avoz exportar`. A captura existente é de textos; o addon não grava vídeos.

O pacote usa áudios pré-gerados; não consulta IA nem internet durante o jogo.
Modelo, texto e áudio não foram certificados no cliente real: testes automatizados
usam Lua 5.1 com APIs simuladas e verificam os arquivos de áudio.

Os bancos e gravações externos ficam fora do GitHub. Veja THIRD_PARTY.md.
