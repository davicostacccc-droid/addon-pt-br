# AzerothVoz 0.3.0 — mais missões no Vale das Provações

Preserva a interface e as falas da 0.2.1, aprovada pelo jogador, e acrescenta
14 etapas narradas de cinco missões. Agora são 11 missões e 30 etapas de missão.

| ID | Missão | NPC inicial | Etapas novas |
|---|---|---|---|
| 792 | Familiares vis | Zureetha Fargaze | Apresentação, andamento, conclusão |
| 794 | Medalhão da Burning Blade | Zureetha Fargaze | Apresentação, andamento, conclusão |
| 805 | Apresente-se na vila de Sen'jin | Zureetha Fargaze | Apresentação e conclusão com Master Gadrin |
| 5441 | Peões preguiçosos | Foreman Thazz'ril | Apresentação, andamento, conclusão |
| 6394 | A picareta de Thazz'ril | Foreman Thazz'ril | Apresentação, andamento, conclusão |

Os nomes de itens, NPCs e alguns locais permanecem como no cliente inglês.
As falas novas usam Piper Faber local, sem serviço pago. Esta ainda é uma voz
padrão compartilhada, inclusive para Zureetha; vozes por personagem seguem pendentes.
As gravações anteriores foram mantidas sem alterações.

## Instalação e teste

1. Feche o WoW e guarde uma cópia da pasta AzerothVoz anterior.
2. Extraia o ZIP em Interface/AddOns. O caminho final deve ser
   Interface/AddOns/AzerothVoz/AzerothVoz.toc.
3. No jogo, teste `/avoz previa 792`, `/avoz previa 794`, `/avoz previa 805`,
   `/avoz previa 5441` e `/avoz previa 6394`. As prévias funcionam longe dos NPCs.
4. Converse com Zureetha Fargaze ou Foreman Thazz'ril e abra uma missão disponível.
   Confira tradução na janela do jogo, narração, Repetir e Parar.
5. Confira se fechar a janela interrompe a fala. Teste também Gornek para verificar
   que o comportamento já aprovado continua funcionando.

Prévia não altera o progresso da missão. A detecção real exige o mesmo NPC, evento e
texto de origem; variantes do servidor podem precisar de outro registro.
Sem progresso registrado para 805 porque a fonte não contém esse diálogo.

Verificações automáticas usam Lua 5.1 com APIs simuladas e decodificam os MP3s.
A versão 0.3.0 ainda depende de confirmação do jogador no cliente 12340.

Para reproduzir a compilação local, preserve o pacote 0.2.1 em
dist/durotar-0.2.1/AzerothVoz, o arquivo expected-records.json da 0.2.0 e o modelo
Piper Faber em models/. Execute `python tools/build_durotar_extension.py`.
O script recusa sobrescrever uma saída existente e reaproveita o cache de voz.
