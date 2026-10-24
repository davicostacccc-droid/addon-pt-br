# AzerothVoz 0.6.0-beta2 — cena de diálogo

Esta atualização redesenha os painéis do AzerothVoz, preservando as missões e todos
os áudios da beta 0.5.0. O alvo continua sendo WoW original 3.3.5a, build 12340.

## Nova apresentação

- Cena maior e centralizada, com tamanho calculado pela resolução e escala da UI.
- Tipografia Arial Narrow do próprio cliente, em tamanho maior para a fala.
- Superfícies escuras limpas, texto claro e controles próprios sem botões vermelhos
  dos templates antigos. Não são alterados os temas dos outros addons.
- Personagem com uma área própria maior, mantendo a unidade real do interlocutor.
- Diálogo em trechos curtos, com transição suave de texto e avanço automático.
- Anterior e Próxima permitem leitura manual; Retomar auto volta ao acompanhamento.
- Objetivos ficam separados, disponíveis em Ver objetivos, sem misturar instruções
  da missão com a fala narrada.
- Relógio e linha de progresso discretos; Ouvir do início reinicia a narração.
- Janela de leitura, controles compactos e configurações seguem o mesmo padrão.
- `/avoz` abre um painel próprio e adaptável de configurações. Nas opções nativas
  do jogo permanece um atalho para esse painel.

O avanço dos trechos é estimado pela duração do áudio e tamanho do texto; não é
alinhamento por palavra nem sincronização de fonemas. Navegar por páginas não
salta para outro ponto do áudio. Parar interrompe a fala; não é uma pausa retomável.

Minimizar mantém o áudio e mostra os controles junto à janela do jogo. Modo padrão
desativa a cena. Aceitar missão e escolher recompensa continuam na janela nativa.
Para reposicionar a cena durante uma conversa, use `/avoz centralizar`. Cada nova
conversa começa centralizada; é possível arrastar a cena durante a leitura.

## Instalação e teste

1. Feche o WoW e guarde a pasta AzerothVoz anterior.
2. Extraia a pasta AzerothVoz do ZIP completo em Interface/AddOns.
3. Use `/avoz rp on` e converse com um NPC de uma missão incluída.
4. Confira tamanho, posição, legibilidade, passagem de trechos e modelo do NPC.
5. Teste Anterior/Próxima, Retomar auto, Ver objetivos, Parar e Ouvir do início.
6. Confira se Minimizar permite usar Aceitar e as recompensas normalmente.
7. Use `/avoz` para testar os novos controles de apresentação, voz e tradução.

Prévia longe do NPC conserva uma mensagem neutra na área do personagem. O modelo
3D usa a unidade da conversa quando disponível. Gestos e enquadramento variam com
os modelos e patches HD do cliente, como na beta anterior.

## Conteúdo e verificação

A cobertura permanece: 1.903 IDs de Northrend com ao menos uma etapa; 772 com todas
as etapas de diálogo da referência; 184 IDs regionais ainda sem cobertura. O pacote
combinado preserva 3.696 IDs com alguma etapa e 6.353 MP3s. Traduções da beta ainda
podem precisar de revisão e as vozes novas usam um timbre padrão.

Os testes automáticos verificam navegação, preservação de caracteres UTF-8,
alternância manual/automática, escala da interface, controles e encerramento.
Os MP3s são preservados por hash, sem nova síntese. A nova aparência no cliente
real ainda depende da confirmação do jogador. A imagem enviada mostra o modelo
3D na interface anterior, sem validar automaticamente esta atualização.

Nenhuma modificação foi aplicada automaticamente à instalação do WoW.
