# Pacote Gornek — 24/10/2026

Acrescenta a fala de conversa do Gornek (NPC 3143), capturada pelo jogador no evento GOSSIP_SHOW. Preserva a demonstração e a saudação de McBride do primeiro pacote. É uma atualização do conteúdo do protótipo 0.1.0; não altera o código do addon.

## Atualizar

1. Feche completamente o WoW.
2. Guarde uma cópia da pasta AzerothVoz que você instalou anteriormente.
3. Extraia a pasta AzerothVoz deste novo ZIP para Interface/AddOns, substituindo a versão anterior quando solicitado.
4. Abra o jogo e converse novamente com Gornek. A saudação capturada deve aparecer em português e ser narrada.

O pacote inclui esta fala específica. O evento GOSSIP_SHOW é a conversa inicial, antes de selecionar a missão. A descrição, o andamento e a conclusão da missão são outros textos; abra a missão e use /avoz exportar para capturá-los também.

O teste de correspondência em Lua 5.1, a geração neural local, a decodificação MP3 e a integridade do ZIP são verificáveis fora do jogo. A reprodução desta nova fala no cliente depende da confirmação do jogador.
