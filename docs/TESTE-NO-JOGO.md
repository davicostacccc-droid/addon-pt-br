# Teste guiado — cliente 3.3.5a / 12340

Este roteiro está **pendente de execução pelo jogador**. Nenhum item abaixo foi marcado como aprovado no jogo.

1. Feche o WoW. Extraia o ZIP e copie a pasta AzerothVoz para Interface/AddOns. Não deve haver uma segunda pasta AzerothVoz aninhada.
2. Para este teste inicial, deixe desativados QuestVoice, ForeverVO e outros addons de voz/tradução. Você pode reativá-los depois para investigar compatibilidade.
3. Entre no jogo. Deve aparecer a mensagem “AzerothVoz: Protótipo 0.1.0 carregado”. Se não aparecer, confira a seleção de addons e a pasta.
4. Digite `/run print(GetBuildInfo())`. O resultado esperado inclui `3.3.5`, `12340` e `30300`. Um cliente diferente é recusado pelo addon.
5. Use `/avoz demo`. Confira o texto em português, os acentos e a voz. O áudio dura cerca de dez segundos. Arraste a janela pela região livre e confira rolagem/botões.
6. Repita a demo e clique **Parar** durante a fala. Ela deve parar e o volume anterior de Música deve voltar. O mesmo deve ocorrer com **Fechar**.
7. Use `/avoz`, desligue a voz e rode a demo: deve haver texto sem áudio. Ligue novamente e teste o controle de volume durante a fala.
8. Para o teste real, procure **Marshal McBride**, NPC 197, na abadia de Northshire. Se ele abrir a saudação correspondente ao pacote, confira tradução e narração. Se abrir uma missão em inglês, ela ainda não está incluída: deve aparecer “Tradução pendente”, sem tocar uma fala diferente.
9. Abra e feche rapidamente o diálogo; abra outra janela de missão em seguida. Não deve tocar uma fala anterior por causa de atraso, nem continuar a narração depois do encerramento correspondente.
10. Abra uma missão ainda não coberta e use `/avoz exportar`. Copie com Ctrl+C e envie o JSON para preparar um pacote real. Se a caixa estiver vazia de registros, informe qual NPC/diálogo foi aberto. Missões de itens, objetos ou compartilhadas podem ser ignoradas por não terem NPC válido neste protótipo.
11. Saia normalmente ou use `/reload` após capturar uma fala e confirme que ela continua em `/avoz exportar`. Configurações também devem persistir.
12. Reative os outros addons um de cada vez, se desejar testar convivência. O suporte a interfaces substitutas ainda não foi validado.

Se houver erro Lua, ative a exibição com `/console scriptErrors 1`, recarregue e envie o texto exato do erro. Informe também o resultado do build, o nome do NPC, qual comando/evento ocorreu e se o som geral estava ativado.

Para retornar com o resultado, basta dizer:

- `/avoz demo`: texto apareceu? Acentos corretos? Voz tocou?
- Volume e Parar: funcionaram? Música voltou?
- McBride ou outro NPC: o que apareceu?
- Houve erro Lua? Qual?

Não é necessário instalar Python ou executar o gerador para testar o ZIP pronto.
