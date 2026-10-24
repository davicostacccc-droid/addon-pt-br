# Entrega local 0.1.0

Criada em 24/10/2026. Alvo: **cliente original 3.3.5a / 12340**.

| Etapa | Resultado |
|---|---|
| Análise dos dois repositórios | Concluída no escopo documentado em DIAGNOSTICO.md |
| Arquitetura | Pacotes locais, addon Lua 5.1, preparador Python Windows |
| Protótipo | Demonstração própria + saudação do NPC 197 em dois tipos de janela |
| Integração | Cache por conteúdo, leitor, tradução nativa básica, controles de voz/volume, captura e exportação |
| Testes automáticos | 25 testes aprovados; Lua 5.1 real com APIs simuladas |
| Síntese neural real | 2 MP3s distintos produzidos com Piper/Faber pt_BR; 3 registros de diálogo |
| Cache real | Segunda geração: 0 sínteses novas, 3 registros reutilizados |
| Decodificação e pacote | Verificação pelo script verify_release.py; relatório em VERIFICACAO-RELEASE.json após empacotar |
| Teste no WoW | **Pendente da confirmação do jogador** |
| Tradução local com Ollama | Integração opcional escrita; sem validação contra modelo/serviço reais |
| GitHub | Criação autorizada pelo usuário; bloqueada por falta de ferramenta para criar repositório e de aprovação do controle do computador para Chrome |

## Arquivos de entrega

- `dist/AzerothVoz-0.1.0-12340.zip`: addon instalável, incluindo MP3s e instruções.
- `dist/AzerothVoz-0.1.0-fontes.zip`: código, testes, documentação e catálogo. Sem capturas, modelos, ambiente Python ou arquivos de pesquisa.
- `dist/release/AzerothVoz/`: addon descompactado.

As pastas fornecidas originalmente foram preservadas. Não foi procurada nem modificada uma instalação do WoW. O script de instalação foi preparado e teve sua sintaxe conferida, mas não foi executado contra a instalação do jogador. Nenhuma chave de API foi criada ou usada e nenhum serviço de IA pago foi chamado.

## Voz utilizada

Faber medium pt_BR, Piper 1.4.2. A model card declara dataset CC0, um locutor e amostragem de 22.050 Hz. O modelo é ajustado a partir de lessac medium. Não se está afirmando auditoria completa de toda a cadeia de treinamento.

SHA-256 do modelo ONNX: `858555e3a064209c57088fe6bd70c4c3dc54d03eaa00c45d5ecaf43a33f95aa7`.

SHA-256 da configuração: `7e694de195ae3fc36dd732c445eb04fb49b649854893cb5506b978f0d50a1d6f`.

O modelo fica apenas em `models/` e não é incluído no addon ou nos fontes compactados. O pacote de vozes pode ser regenerado com as ferramentas e o modelo correspondente.

## Continuação

O teste inicial é `/avoz demo`. O passo seguinte é confirmar texto, áudio, volume e encerramento dentro do cliente. Depois, uma captura JSON de uma missão da região em que o jogador está permitirá preparar o primeiro pacote de quest com descrição, progresso e conclusão correspondentes ao servidor.

O projeto ainda não é uma tradução integral do jogo. Não há ponte em tempo real com aplicativo externo, catálogo amplo, vozes por raça/gênero ou publicação remota concluída.
