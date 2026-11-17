# "Será que enche?" — formato de física satisfatória (teste de 15/11)

Referência: Reel do Instagram (@bouncingball0, "Will it fill the whole circle?") mandado pelo Nasser em 15/11.
Aproveitamos só a mecânica, que é genérica. Cores, texto, som e código são nossos.

## Mecânica
- Um anel nasce como um ponto dentro do círculo, quica em linha reta e **cresce a cada batida**.
- Quando encosta na borda, vira uma **camada da parede**, e nasce outro anel. O buraco vai diminuindo e as batidas aceleram
  até virar um "trrrr".
- Cada batida toca uma nota (acordes I–V–vi–IV em ré maior), que sobe conforme o anel cresce. Sem narração, sem ElevenLabs.
- Cores do Brasa: borda amarela, camadas indo para vermelho brasa, miolo branco-quente.
- O final emenda no começo (o círculo se esvazia do centro pra borda).

## Versões feitas em 15/11
| Versão | Duração | O que tem | Arquivo |
| --- | --- | --- | --- |
| v1 | 24 s | só a mecânica, anel rápido (1.600 px/s), 15 camadas | `circulo/out/circulo.mp4` (`render.py` + `sim.py`) |
| v2 suspense | 28,8 s | cronômetro, % cheio, zoom e câmera lenta no fim, coração, tique-taque | `circulo-suspense.mp4` (`render2.py` + `sim2.py`) |
| v3 lenta | 24 s | anel a ~670 px/s, 10 camadas grossas, **sem zoom e sem câmera lenta** | `circulo-lento.mp4` (`render3.py` + `sim2.py`) |
| **Brasa: a fogueira (publicada)** | 24,6 s | a v3 no mundo do Brasa (ver abaixo) | `fogueira.mp4` (`fogueira.py` + `sim2.py`) |

**v3 em detalhe:**
- Título "Será que enche antes do tempo acabar?" e cronômetro de 22,00 correndo desde o 1º quadro.
- "% CHEIO" embaixo do círculo.
- Nos últimos 6 s: cronômetro vermelho, coração acelerando, tique-taque e bordas da tela escurecendo com pulso vermelho.
- O % trava em 99,9% enquanto o miolo enche em silêncio. Depois vem o estouro: "100%" grande e o cronômetro parado em 0,08 (verde).
- O cronômetro é calibrado: `solve_speed` acha a velocidade do anel que faz encher com `SPARE` (0,08 s) de sobra.
- Rodar com `SEED=<n> LIMIT=22 OUT=out/x.mp4 python3 render3.py`. `PLAN=1` só imprime a linha do tempo. Cada seed sai diferente.

**Feedback do Nasser:**
- v1: "precisa de mais suspense".
- v2: "tem que ser mais lento… e sem o zoom e slow".
- Pediu levar pra temática do Brasa. Entre "a runa" e "a fogueira", escolheu **a fogueira** (não mexe na história).

## Versão Brasa: "Será que a fogueira acende antes de anoitecer?" (15/11)
- **Visual:**
  - Pixel art no canvas 360x640 (ampliado 3x), com o gramado, a terra batida, o contorno escuro e a luz pontilhada do
    `world2.py`, e a fonte Jersey com contorno e sombra.
  - A praça de terra tem um anel de 30 pedras. Dentro dele fica a cinza, e é ali que a fagulha quica.
  - 15 moradores em volta, desenhados pelo `folk.py`, sem nome na tela: Gabriel, Lívia, Naty, Ana Sofia, Raviela, Rafael,
    Emanuel, Victor, Antônio, Izabelly, Cristal, Rafaela, Oliveti, Miyuki e Julielen.
- **As camadas** são brasa com textura e frestas escuras: vermelho escuro na borda, amarelo no centro e miolo branco.
  Cada batida solta faíscas.
- **O tempo é o anoitecer:**
  - o TINT do Brasa vai do fim da tarde até a noite no cronômetro de 22 s;
  - a luz das brasas cresce conforme o "% ACESA" sobe, e no fim só a praça fica iluminada.
- **Últimos 6 s:** tique-taque, coração e um zumbido. Depois vem o silêncio enquanto o miolo enche, com o % travado em 99,9%.
- **Final:**
  - clarão e chama grande em pixel (com faíscas subindo);
  - os moradores pulam com "!";
  - aparece "ACENDEU!" em dourado, com o cronômetro parado em 0,08 (turquesa);
  - som de FWOOM e fanfarra 8-bit, com o fogo estalando.
- **Loop:** a chama apaga, as brasas somem do centro pra borda e volta o fim da tarde.
- **Som:** batidas em onda triangular (8-bit), estalos de brasa que aumentam com o %, grilos quando escurece.
- **Capa** (`CAPA=1 python3 fogueira.py`):
  - o quadro de 17,5 s (anoitecendo, quase acesa, sem o final) com uma faixa escurecida atrás do título;
  - título no centro: "SERÁ QUE A / FOGUEIRA / ACENDE? / ANTES DE ANOITECER";
  - arquivo: `capa-brasa-fogueira.jpg`.
- **Rodar:** `SEED=<n> LIMIT=22 OUT=out/x.mp4 python3 fogueira.py`.
  - `PLAN=1` imprime só a linha do tempo, e `STILLS=1,12,21.5` gera quadros de conferência.
  - O script importa `world2` e `folk` de `producao/reino/` (variável `REINO`).

**Publicado em 15/11 às 18h49** pelo TikTok Studio web, no navegador do app (ID 7708518678433778965). O Nasser escolheu o
arquivo, que foi salvo como `brasa-fogueira.mp4` na pasta Downloads dele, e subiu a capa. Logo depois ficou "Conteúdo sob
análise / Somente eu".
- Legenda: "será que a fogueira de brasa acende antes de anoitecer? quem tá em volta são moradores de verdade, comenta teu
  nome e tua função que tu entra no reino #pixelart #satisfatorio #satisfying #reinodebrasa".
- Selo "Conteúdo gerado por IA" ligado, publicação pra Todos, som original.
- Dica do Studio web: o painel do navegador do app é estreito e o botão "Salvar" da capa fica fora da tela. Resolve com
  `resize_window` 1400x900, e depois voltar com `preset: desktop`.

## Resultado do 1º post (16/11, 07h, ~12 h no ar)
- **840 views**, 42 curtidas, 3 salvamentos, 1 comentário. Por hora: 42, 119, **531**, 39, 37, 31… (o TikTok empurrou pra um
  segundo lote na 3ª hora, coisa que só o Brasa Ep. 4 tinha conseguido).
- **A melhor retenção do canal:** 84% passam do 1º segundo, **59% aos 3 s, 41% aos 10 s, 25% aos 20 s**; tempo médio 11,2 s
  de 24,6 s; 24% veem até o fim. Para Você 98%.
- **Seguidores novos pelo vídeo: 0** (o perfil foi de 80 a 83 na noite, mas o Studio não atribui ao vídeo).
- Comentário: a Luiza (@sleep_moon12, moradora) escreveu "acendeu"; respondida.
- Leitura: o formato prende gente de fora muito melhor que os episódios do Brasa, mas sozinho não converte em seguidor.
  Para converter, testar a ideia "cada camada leva o nome de um morador" ou terminar com um gancho do Brasa.

**O código ainda NÃO está no GitHub.** Está só no ambiente do Claude da sessão de 15/11, em `/home/claude/circulo/`, que
pode ser zerado (não existe no ambiente da sessão principal). Antes de usar de novo, subir para `producao/circulo/`.

## Versão 2: "Será que a cerca aguenta?" — o cercado do Valdemir (16/11)
Ideia do Nasser: um cercado redondo com 1 ovelha e uma haste girando no centro. Cada ovelha que a haste prensa vira duas,
até encher e estourar a cerca.
- **Física** (`producao/cercado/sim.py`):
  - ovelhas são círculos de raio 8 dentro de uma cerca de raio 140;
  - a haste gira a 2,4 rad/s, então uma volta leva 2,6 s;
  - a ovelha que bate na frente da haste vira duas (as 3 primeiras sempre, depois 85%, com 0,8 s de espera).
- **Ritmo:**
  - a primeira divisão acontece aos 0,7 s;
  - a contagem dobra no começo (1, 2, 4, 7, 16…) e depois acelera até umas 40 ovelhas por segundo;
  - a cerca estoura com **240 ovelhas** aos 15,8 s, com o cercado cheio de parede a parede.
- **Visual:**
  - pixel art 360x640 ampliado 3x, vista de cima;
  - a cerca de madeira tem 40 postes;
  - com a pressão, a cerca embarriga, os postes entortam, os trilhos racham e soltam lascas, e a tela treme;
  - nos últimos 4 s o contador fica vermelho, a borda pulsa e entra o som de coração.
- **Moradores em volta:** o Valdemir vaqueiro com etiqueta de nome nos primeiros 3,6 s, mais a Luiza, o pixoto, a Yasmim
  e o Gabriel.
- **Estouro:**
  - clarão, os pedaços da cerca voam e as ovelhas fogem pra fora da tela;
  - os moradores pulam com "!";
  - na tela: "A CERCA ESTOUROU! COM 240 OVELHAS";
  - depois vem a chamada "QUANTAS A CERCA NOVA AGUENTA? CHUTA AÍ NOS COMENTÁRIOS".
- **Loop:** a cerca se refaz poste a poste com marteladas, a primeira ovelha volta e a haste cai no mesmo ângulo do
  quadro 1. A duração do vídeo é um múltiplo exato da volta da haste.
- **Som** (sem narração):
  - um blip 8-bit por ovelha nova (acordes D–A–Bm–G, sobe de oitava com a pressão);
  - balidos e rangidos da cerca cada vez mais frequentes;
  - coração nos últimos 4 s;
  - no estouro: estrondo com madeira, fanfarra 8-bit e balidos;
  - ao fundo, vento e passarinhos.
- **Arquivos:** `brasa-cercado.mp4` (20,9 s) e `capa-cercado.jpg` (quadro de 1,2 s antes do estouro, com "SERÁ QUE A /
  CERCA / AGUENTA?").
- **Rodar:** `SEED=2 python3 cercado.py`.
  - Os padrões já estão no código: `NMAX=240 SPEED=140 COOL=0.8 OMEGA=2.4`.
  - `PLAN=1` imprime a linha do tempo, `CAPA=1` gera a capa e `STILLS=8,b-2,b-0.3` gera quadros de conferência (`b-2`
    é 2 s antes do estouro).
  - O script importa `ep1hd`, `folk` e `world2` de `producao/reino/` (variável `REINO`).
- **Testes:**
  - com ovelhas lentas (70 px/s), elas ficavam amontoadas na frente da haste e metade do cercado ficava vazia;
  - a 140 px/s elas se espalham e o cercado enche por igual;
  - com 210 ovelhas ainda sobrava espaço, e 240 é o ponto em que fica lotado.
- **Gancho pra série:** a cada vídeo, uma "cerca nova" que aguenta mais. Quem chutar mais perto pode ganhar uma ovelha com o
  nome no próximo vídeo, o que liga o formato ao Brasa.

## Versão 3: a prensa (16/11, pedido do Nasser)
Feedback da v2: "elas tem que ser prensadas em algum lugar pra se multiplicar, mas tem que ter o fator sorte pra pegar
algumas apenas".
- **Física** (`producao/cercado/sim2.py`):
  - 3 prensas, que são muretas de madeira com chapa de ferro presas na cerca (a -90°, 30° e 150°), indo da cerca até
    80 px pra dentro;
  - a haste é mais curta que o cercado (deixa um vão de 16 px) e tem uma cabeça de ferro na ponta. Ela passa por cima das
    muretas como uma tesoura;
  - a ovelha só vira duas quando encosta na haste e na prensa ao mesmo tempo, com a haste chegando. Uma sai por trás da
    haste e a outra do outro lado do bloco;
  - quem está mais pra dentro ou no vão perto da cerca escapa: é o fator sorte.
- **Ritmo:**
  - a haste gira a 3,4 rad/s e passa numa prensa a cada 0,62 s;
  - pegas por passagem no começo: 1, 0, 0, 1, 1, 0, 1, 2, 2… e no fim +10, +17 de uma vez;
  - a contagem vai 1, 2, 2, 4, 4, 7, 9, 11, 15… e estoura com **230 ovelhas** aos 19,6 s. O vídeo tem 24 s.
- **Na tela:** "+N" dourado sobe da prensa a cada pegada e o bloco brilha no impacto. A frase de regra virou "ESPREMEU NA
  PRENSA, VIROU DUAS".
- **Som:** um "CLAC" de madeira e ferro a cada passagem, com um tom por prensa, e um "ploc" grave quando pega alguém. O
  resto é igual à v2.
- **Arquivos:** `brasa-cercado-prensa.mp4` e `capa-cercado2.jpg`.
- **Rodar:** `python3 cercado2.py`. Os padrões são `SEED=4 OMEGA=3.4 NMAX=230 SPEED=50 GAP=16 LB=80 FLING=0.05`.
- **Testes:**
  - prensa estreita (só no vão perto da cerca): quase nunca pegava, levou 30–40 s pra primeira;
  - prensa comprida com haste sem escorregar (`fling=0`): pegava todas, sem sorte nenhuma;
  - o meio-termo é este, mas cada seed dá um ritmo diferente (seeds 3, 4 e 5 estouram perto de 19,6 s; 1 e 2 demoram mais
    de 25 s).

## O formato da série (16–17/11, combinado com o Nasser)
- **Título:** uma pergunta de sim ou não, "SERÁ QUE…?", que dá pra entender em 1 segundo.
- **Física simples com sorte:** a coisa vai escalando sozinha, sem pedir nada pra quem assiste.
- **Uma contagem na tela:** cronômetro, contador ou cercas que faltam.
  - Nos últimos 6 s: contagem vermelha, coração, tique-taque e a borda da tela pulsando.
- **Final no limite:** dá certo no último instante. Pedido do Nasser: "tem que conseguir no fim certo".
  - A sobra **varia de um episódio pro outro, entre 0,05 e 0,50 s** (pedido de 17/11), pra não ficar sempre 0,08.
  - Fogueira: 0,08. Porco: 0,34. No `porco.py` é `SPARE=`.
- **Som:** cada batida é uma nota. Melodia só de domínio público.
- **Loop:** o fim emenda no começo.
- **O Brasa fica de cenário:** grama do reino e moradores olhando, que pulam com "!" no fim. Nada de pedir nome no vídeo:
  o Nasser acha que o formato viraliza sozinho.
- Sem narração, ~25 s.

## Versão 4: "Será que o porco escapa?" (17/11)
Ideia do Nasser em cima do formato viral "Will the ball escape?" (vídeos com 38 e 67 milhões de views no Shorts).
- **A física** (`producao/porco/sim_porco.py`):
  - 8 cercas redondas pintadas (do vermelho ao rosa), uma dentro da outra, girando em sentidos alternados, cada uma com uma
    porteira aberta;
  - os porcos quicam com velocidade constante (150 px/s) dentro da cerca de dentro que ainda está de pé;
  - quando um porco passa pela porteira, aquela cerca estoura e ele vira dois (+1 porco).
- **Largura das porteiras:** `[41, 34, 32, 37, 51, 50, 53, 31]` px, calibrada pra cada cerca levar ~2,5 s. A última
  porteira é a mais estreita, pra dar suspense.
- **O sorteio 79:**
  - as cercas caem aos 0,8 s, 2,9, 5,4, 8,2, 10,5, 13,5 e 16,6;
  - a última segura 5 s e o porco escapa aos 21,66 s do cronômetro de 22, com **0,34 de sobra**;
  - o tempo foi esticado 0,7% (`WARP`) pra cair exato.
- **Som:**
  - **cada batida na cerca toca a próxima nota de "Für Elise"** (Beethoven, domínio público, timbre de piano ou caixinha
    de música; o tema A, depois o B); são 123 batidas;
  - cerca estourando: craque de madeira + Lá grave + "oinc" do porco novo;
  - nos últimos 6 s: tique-taque e coração;
  - no fim: estrondo, fanfarra e coro de "oinc".
- **Na tela:**
  - "SERÁ QUE O PORCO ESCAPA?", o cronômetro e "FALTAM N CERCAS";
  - nos primeiros 4 s, "PASSOU NA PORTEIRA, VIROU DOIS";
  - a porteira da vez brilha;
  - no final, "ESCAPOU!" com "00,08" verde, os porcos correndo pra fora e o Valdemir, a Luiza, o pixoto e o Edilson
    pulando.
- **Lama** no chiqueiro, com poças e palha.
- **Loop:** as cercas voltam de dentro pra fora e o porco reaparece no meio.
- **Arquivos:** `brasa-porco.mp4` (25,2 s) e `capa-porco.jpg`.
- **Rodar:** `SEED=79 python3 porco.py`. `PLAN=1` imprime a linha do tempo, `STILLS=6,b-0.5` gera quadros de conferência e
  `CAPA=1` gera a capa. Pra outro sorteio, rodar o `search.py` (procura fuga entre 20,6 e 23,2 s com a última cerca
  ≥ 4 s).

## Monetização (15/11)
- O Creator Rewards só paga vídeo com **1 minuto ou mais**. Outros requisitos: 18+, **10 mil seguidores** e 100 mil views em 30 dias.
- Só contam vídeos postados depois da aprovação. Views qualificadas: vindas do Para Você, com mais de 5 s assistidos.
- Decisão: **manter os vídeos curtos (25–30 s) enquanto o objetivo é crescer**, porque esticar derruba a retenção (o Brasa de
  41–44 s segurou menos que o de 26 s). Passar pra 1 minuto perto dos 10 mil seguidores. Este formato aguenta 1 minuto
  (mais camadas e cronômetro de 60 s).

## Ideias guardadas
- **Final contrário:** o tempo zera em 99,9% e não enche ("foi roubado!"), pra puxar comentário.
- **Ligar ao Brasa:** cada camada leva o nome de um morador que comentou ("COMENTA TEU NOME PRA VIRAR CAMADA").
- **A runa** (a outra opção de 15/11): a pedra da runa enche de luz turquesa antes "deles" chegarem. Mexe na história,
  então depende do Nasser.
