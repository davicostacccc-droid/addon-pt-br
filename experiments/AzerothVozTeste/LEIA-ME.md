# Teste das vozes do patch

Este é um addon de teste separado: **AzerothVozTeste**. As duas gravações foram extraídas do MPQ fornecido pelo jogador e convertidas para MP3. Não são vozes geradas por IA neste teste; são as gravações existentes no arquivo. A origem e a identidade dos dubladores não foram verificadas.

## Instalar e testar

1. Feche o WoW.
2. Extraia a pasta **AzerothVozTeste** deste ZIP para `SuaPastaWoW/Interface/AddOns/`. Ela fica ao lado de AzerothVoz; não substitua a pasta AzerothVoz.
3. Ative **AzerothVoz - Teste de vozes do patch** na seleção de personagens.
4. Entre no jogo e digite `/avozteste jaina`.
5. Quando a fala terminar, digite `/avozteste thrall`.
6. Para interromper, use `/avozteste parar`. Para volume de 70%, `/avozteste volume 70`.

Você pode testar de qualquer lugar; não precisa encontrar esses NPCs. O teste interrompe a narração do addon principal antes de começar, usa temporariamente o canal Música e restaura volume/configuração ao terminar ou parar. O som geral do WoW precisa estar ligado. Não inicie outras narrações durante cada amostra.

## O que conferir

- As duas vozes tocaram em português?
- A qualidade e o estilo combinam com os personagens?
- Houve cortes, distorção ou volume muito diferente entre elas?
- O comando Parar funcionou e o volume de Música voltou ao anterior?

Este teste não muda automaticamente as vozes dos NPCs nem amplia a tradução das quests. É uma avaliação de duas gravações dentro do cliente 3.3.5a / 12340. O MPQ completo, suas introduções de outras épocas e suas alterações de interface não estão neste pacote.

Para deixar de usar o teste, basta desativar AzerothVozTeste na lista de addons. A confirmação de funcionamento no jogo depende do jogador.
