# AzerothVoz 0.2.1 — ajuste da interface

Esta versão mantém as seis missões, os 16 registros de etapas e os áudios do pacote 0.2.0. O foco é a experiência de leitura vista na gravação fornecida pelo jogador.

## O que mudou

- Quando o texto traduzido está aplicado na janela de missão/conversa do jogo e ela está visível, a janela extra deixa de aparecer automaticamente.
- Uma barra pequena com **Repetir** e **Parar** aparece abaixo da janela do jogo.
- Rótulos da janela padrão, como Objetivos, Recompensas, Aceitar, Recusar e Concluir missão, são traduzidos quando a fala pertence ao pacote.
- Fechar a janela nativa interrompe a fala também quando sua visibilidade desaparece sem o evento de encerramento esperado.
- Desligar o addon restaura os textos alterados por ele, preservando atualizações posteriores de outros addons. Os scripts de clique dos botões não são substituídos.
- Se uma interface substituta não expuser uma janela nativa visível, o leitor extra continua como alternativa. Ele também permanece disponível nas prévias e para avisar sobre falas ausentes.

## Atualizar

1. Feche completamente o WoW.
2. Guarde uma cópia da pasta AzerothVoz instalada.
3. Extraia a nova pasta AzerothVoz para Interface/AddOns, substituindo a anterior quando solicitado.
4. Ative AzerothVoz. O addon AzerothVozTeste não é necessário.

## Teste principal

Abra a conversa do Gornek e depois selecione Dentes cortantes ou outra missão já incluída. Confira:

- O texto traduzido aparece em apenas uma janela, com Repetir/Parar abaixo dela?
- Os títulos de seção e os botões ficaram em português?
- Repetir reinicia a fala correta e Parar interrompe?
- Ao fechar a conversa/missão, a barra some e a voz para?
- O botão Aceitar/Concluir continua com a ação normal? Não é necessário aceitar uma missão só para testar sua tradução.

Se a sua interface personalizada não mostrar o texto em português, use `/avoz janela on` para exibir o leitor adicional. `/avoz janela off` retorna ao modo automático, que tenta evitar duplicação e conserva a alternativa quando a janela padrão não está disponível. Essa opção também está em `/avoz`.

Comandos úteis:

```
/avoz previa
/avoz repetir
/avoz parar
/avoz janela on
/avoz janela off
```

As prévias mantêm sua própria janela, pois podem ser executadas longe de um NPC.

## Limites deste ajuste

O rastreador de objetivos, nomes de itens e rótulos criados por outros addons ainda podem permanecer em inglês. Não foram alterados globalmente os textos do cliente ou a instalação do WoW. O comportamento com a interface personalizada da gravação precisa do teste do jogador.

As vozes são as mesmas da versão 0.2.0. Padronizar a voz de cada NPC, aproximar palavra por palavra o texto da gravação e ampliar a cobertura continuam pendentes. A gravação anterior confirmou o texto e a narração da saudação de Gornek e da apresentação de Dentes cortantes, mas não validou todas as etapas das seis missões.

A 0.2.1 foi verificada fora do jogo e ainda aguarda confirmação no cliente. A cobertura das missões está no documento COBERTURA-0.2.0.md incluído nesta pasta.
