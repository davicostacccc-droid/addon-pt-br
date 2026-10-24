# Referências, autoria e dependências

O código Lua/Python do AzerothVoz é uma implementação nova. Até a versão 0.3.0, QuestTradutor foi usado como referência de eventos e estrutura, sem incorporar seu banco. A beta 0.4.0 prepara localmente candidatos de tradução do QuestTradutor e do dump de localização ptBR, com atribuição de origem e revisão ainda incompleta. Os bancos completos e o catálogo importado ficam em research/ e dist/, ignorados pelo Git. Não foi encontrada uma licença explícita do banco QuestTradutor na árvore consultada; sua publicação em massa continua pendente de esclarecer os termos com os autores (leoaviana/Platine). Nenhum código de QuestTradutor ou Questie foi incorporado ou executado pelos importadores. O ZIP local experimental não deve ser tratado como autorização para republicar bancos ou áudios de terceiros.

QuestVoice: https://github.com/faralaks/wow-questvoice — referência para reprodução de MP3, GUID antigo e mapeamento de gossip. O registro do NPC 197 no catálogo foi identificado a partir de seu índice. A tradução e a narração em português foram feitas para este protótipo. Não foram incorporadas as bibliotecas Ace nem os áudios ingleses. Conservamos a licença da referência abaixo.

Textos, personagens e nomes de World of Warcraft pertencem aos respectivos titulares. A licença do software de referência não transfere automaticamente direitos sobre conteúdo do jogo ou vozes. O protótipo não é afiliado à Blizzard.

FrameXML: https://github.com/wowgaming/3.3.5-interface-files — consulta de nomes de funções/eventos/globais antigos. Nenhum desses arquivos está no pacote instalável. ForeverVO, fornecido na pasta REFERENCIA, foi inspecionado para comparação; nenhuma API moderna ou arquivo dele foi incorporado.

Piper 1.4.2: https://github.com/OHF-Voice/piper1-gpl — GPL-3.0-or-later. Instalado separadamente em .venv; não acompanha o addon. Faber medium: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium — a model card consultada declara dataset CC0 e informa ajuste a partir da voz lessac medium. A model card e hashes dos arquivos ficam em models/ e um registro é incluído na documentação da entrega; não redistribuímos o modelo ONNX no ZIP do addon.

imageio-ffmpeg 0.6.0: https://github.com/imageio/imageio-ffmpeg — wrapper BSD-2-Clause; o executável FFmpeg tem suas próprias condições de licença. É instalado separadamente para converter WAV em MP3; não acompanha o addon. Lupa 2.6: https://github.com/scoder/lupa — licença estilo MIT, apenas testes. As demais dependências são resolvidas pelo pip e ficam registradas em requirements-lock.txt.

MIT License (referência QuestVoice)

Copyright (c) 2023 Vladislav Faralaks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
