# AzerothVoz 0.2.0 — Vale das Provações

Este pacote identifica e traduz automaticamente as etapas incluídas de **seis missões**, com 16 registros de diálogo de missão. Também preserva a demonstração, a saudação do Gornek e os registros de McBride da versão anterior.

| Missão | ID | Personagens | Etapas incluídas |
|---|---:|---|---|
| Seu lugar no mundo | 4641 | Kaltunk / Gornek | Apresentação e entrega |
| Dentes cortantes | 788 | Gornek | Apresentação, andamento e entrega |
| A ferroada do escorpídeo | 789 | Gornek | Apresentação, andamento e entrega |
| Sarkoth | 790 | Hana'zua | Apresentação, andamento e entrega |
| Sarkoth | 804 | Hana'zua / Gornek | Apresentação e entrega |
| A surpresa de sabra de Galgar | 4402 | Galgar | Apresentação, andamento e entrega |

## Instalar

1. Feche o WoW completamente.
2. Guarde uma cópia da pasta AzerothVoz que você instalou anteriormente.
3. Extraia a pasta AzerothVoz deste ZIP para Interface/AddOns, substituindo a versão anterior quando solicitado. Não coloque uma pasta AzerothVoz dentro de outra.
4. Ative AzerothVoz. Pode desativar AzerothVozTeste; ele não é necessário para este pacote.
5. Entre com um personagem no Vale das Provações e abra uma das missões listadas. A fala correspondente deve aparecer em português e tocar automaticamente. Abrir a lista de missões não é o mesmo que selecionar uma missão.

Para ouvir uma prévia de qualquer lugar, mesmo se já completou as missões:

```
/avoz previa
/avoz previa 4641
/avoz previa 4402
```

Sem número, a prévia usa a missão 788. A prévia exibe o texto e toca a apresentação da missão; não aceita, entrega ou altera missões do personagem. Ela confirma reprodução, mas não substitui o teste de detecção ao conversar com os NPCs.

## O que conferir

- Ao selecionar a missão no NPC, o título, o texto e os objetivos aparecem em português?
- O áudio corresponde à etapa aberta? Andamento e conclusão são diferentes da apresentação.
- Seu nome aparece no texto sem marcadores como $N ou $B?
- A fala para ao fechar o diálogo? /avoz parar também deve funcionar.
- A voz é agradável e compreensível? Estes áudios de missões vêm de um pacote experimental de IA e não são as gravações de Jaina/Thrall que foram aprovadas no teste anterior.

Os textos foram traduzidos e revisados a partir das fontes inglesas e relações de NPCs do AzerothCore. A correspondência ainda exige o texto completo, depois de resolver nome/classe/raça/quebras de linha conhecidos. Se o servidor apresentar uma variante, a fala fica pendente, sem escolher outra por aproximação.

## Origem e correções

14 etapas reutilizam áudios do pacote experimental ptBR de Darkneo, arquivo CurseForge 6516696. A estrutura foi examinada sem executar seu addon moderno, cujo TOC declara Interface 100000. O player deste pacote é o AzerothVoz para 30300 / build 12340.

Foram geradas localmente duas etapas com Piper Faber: andamento de Dentes cortantes, ausente no pacote consultado; e apresentação de A ferroada do escorpídeo, pois a transcrição automática do áudio de origem indicava dez caudas e a fonte inglesa consultada pede oito. Essa transcrição foi usada como triagem e não é uma transcrição auditiva certificada. O texto exibido preserva os nomes dos personagens e inclui nomes ingleses úteis de locais/itens.

As 7.872 traduções importadas anteriormente ainda não foram todas integradas: este ZIP é um recorte verificável para avançar sem exigir capturas manuais de cada fala. Não é tradução ou dublagem completa de todo o jogo. As gravações de terceiros ficam na entrega local; não foram publicadas no GitHub. Não instale o MPQ completo para este teste.

Este pacote passou por testes fora do jogo; a versão 0.2.0 ainda aguarda sua confirmação no cliente. Se alguma missão ficar em inglês, use /avoz exportar e informe o NPC e a etapa; isso permite tratar a diferença de servidor.
