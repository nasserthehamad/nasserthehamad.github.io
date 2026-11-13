# Brasa — bíblia da série

Criada em 09/11 a partir de uma referência do Instagram (página "brukmont": cada seguidor vira morador de um reino em
pixel art). **Aproveitamos só a mecânica.** Arte, nome, mundo e história são nossos. Perfil: @vcescolheaoub.
O nome foi escolhido pelo Nasser em 09/11; "Bifúrcia" foi descartado.

## A ideia em uma frase
Um reino que começou numa fogueira e **cresce a cada seguidor**. Cada seguidor vira morador, e quem se apresenta nos
comentários ganha nome e função na história.

## Regras
- **Sem votação A/B.** Decidido em 09/11: nossos votos nunca pegaram, e o pedido precisa ser um só.
- **Um pedido só:** "Comenta seu nome e sua função." Exemplo na tela: "Lia, ferreira".
- **Abertura fixa de todo episódio (pedido do Nasser em 10/11, depois de o Ep. 2 sair sem ela):** "ESTE REINO TEM N MORADORES."
  - N é o número real de seguidores, que o Nasser confirma antes de renderizar.
  - O número já aparece certo **desde o primeiro quadro**, com todos os moradores na tela (nada de contador começando em 0,
    que vira a capa automática e estraga o gancho). Só os brilhos dos que chegaram pulsam.
- **O número do gancho é sempre o real:** "Este perfil tem X seguidores." Confirmar com o Nasser antes de renderizar.
- **Só ganha nome quem comenta pedindo.** Ninguém aparece no vídeo sem ter se apresentado.
- **Quem não segue não mora na vila (pedido do Nasser em 12/11, vale do Ep. 5 em diante).**
  - Antes de cada episódio, cruzar quem comentou com os seguidores.
  - O TikTok web só mostra os ~30 seguidores mais recentes, mas isso cobre quem chegou desde o episódio anterior. A lista sai
    da resposta de `/api/user/list` (scene=67) quando se abre "Seguidores" no perfil, no navegador do app.
  - Se algum morador novo não seguir, o fim do episódio leva o aviso **"QUEM NÃO SEGUE NÃO MORA NA VILA"**. Pode dizer
    quantos são, mas sem citar nomes.
  - Checagem de 12/11, com os 30 mais recentes: Caio, Amanda (escriba) e Luiza provavelmente não seguem. Os moradores antigos
    (Rafaela, Alerrandro, Julielen e Robson) não dá pra confirmar.
- **Narração:** a referência tem narração de IA, então os episódios saem narrados (voz Jhony Tygas `FhdOWgf0bSw3HKWefhlq`,
  `eleven_v4`), com a música bem baixa por baixo da voz. **Só gasta ElevenLabs quando o Nasser disser.** Primeiro sai a versão
  sem voz (texto na tela, fonte pixel Jersey 10, trilha 8-bit e efeitos).
- **Duração:** 25 a 30 s, com o final emendando no começo (loop). Os Eps. 2 e 3 (41–44 s) não seguraram mais gente que o Ep. 1 (26 s).
- **Gancho:** sem spoiler.
- **Áudio:** postar com o original, sem música do app por cima.
- **Visual:** pixel art detalhado (canvas 360x640, ampliado 3x/4x/5x), vista de lado, tipo diorama (a referência é vista de cima). A bandeira do reino é vermelha com uma chama.

## O mundo
- **Centro:** a praça com a fogueira, numa encruzilhada de estradas com placas de madeira.
  - A estrada da esquerda leva "ao mundo".
  - O caminho da direita leva à **ponte** sobre o rio.
- **Do outro lado da ponte:** uma floresta escura. No Ep. 1, **alguém acendeu uma luz** ali (turquesa, piscando).
  - É o mistério de fundo da série. Avança um pouco por episódio e não deve ser explicado cedo.

## Moradores por @ (conferir ANTES de responder qualquer comentário)
O apelido que aparece no TikTok quase nunca é o nome do morador (ex.: "sleep" é a Luiza, "inuyashazinho" é a Lívia).
**Regra (Nasser, 13/11):** antes de responder, procurar o @ do comentário nesta tabela. Se não estiver, buscar o @ nos
comentários de todos os episódios pela API (`/api/comment/list/`) antes de tratar a pessoa como nova.
Lista gerada em 13/11 a partir dos comentários dos Eps. 1–5 e do Bestiário (também em `producao/reino/arrobas.json`).
Quem comentou sem pedir personagem, como @lorena_ferreira167 ("six seven"), não é morador.

| @ | Morador | Função / quando entrou |
| --- | --- | --- |
| @ajulielen | Julielen | arqueóloga e musicista (fundadora que faltou) |
| @inuyashazinho | Lívia | construtora de casas (fundadora 002) |
| @bielpvh_566 | Gabriel | ferreiro (fundador) |
| @nana017850 | Naty | confeiteira (fundadora) |
| @ana.sofia3341 | Ana Sofia | adestradora de cão de caça (fundadora) |
| @rainhab.s | Raviela | cavaleira (fundadora) |
| @rafa_09864 | Rafael | pescador (fundador) |
| @emanuel_mccall | Emanuel | bibliotecário (fundador) |
| @victorgdeamorimco | Victor | fazendeiro (fundador) |
| @miguewkdc1o | Antônio | padeiro (fundador) |
| @izabelly15o | Izabelly | caçadora (fundadora) |
| @cini.facco | Francini | padeira (fundadora) |
| @pearl_ka | Cristal | guarda (fundadora) |
| @rafaelasky08 | Rafaela | aventureira, lidera a expedição (fundadora) |
| @m4yhs.ilk3 | Maria | costureira (fundadora) |
| @meu.mundinho47 | Gustavo | açougueiro (fundador) |
| @robson.luis.dias8 | Robson | ajudante de coleta (fundador que faltou) |
| @kellythais20 | Kelly | artesã (Ep. 2) |
| @._izabelle_1 | Izabelle | médica (Ep. 2) |
| @gab08913 | Oliveti | bruxa de poções (Ep. 2) |
| @alerrandro7161 | Alerrandro | escultor, fez a estátua (Ep. 2) |
| @justlolobeinglolo | Lorena | filósofa (Ep. 2) |
| @rubensfreitas916 | Rubens | bruxo de visões (Ep. 2) |
| @vivi_oooy | Viviane | artista (Ep. 2) |
| @kittycat.cathe | Cathe | mago de previsões (Ep. 2) |
| @joao.gabriel2017 | João | ferreiro (Ep. 2) |
| @0i0i0ioiroi | Bernardo | mágico curandeiro (Ep. 2) |
| @samuelaquino6147 | Samuel | minerador (Ep. 2) |
| @yasmimmoto | Yasmim + Cauby + Aurora | cantora; também pediu Cauby (matemático) e Aurora (dançarina) (Ep. 2) |
| @caua_cruzz | Cauã | arqueiro (Ep. 2) |
| @rafaeltg280 | Valdemir | vaqueiro (Ep. 2) |
| @seivialguns | Laura | louca (Ep. 2) |
| @ovetes5 | Nic | bobo da corte (Ep. 2) |
| @fao.seu.trabalho | Clara | enfermeira (Ep. 2) |
| @dottbananot | Giovanni | alquimista (Ep. 2) |
| @hanna_h10 | Hanna | padeira (Ep. 4) |
| @amanda.paz.gonalv | Amanda | açougueira (Ep. 4) |
| @giovannagabrieli | Giovanna | apotecária (Ep. 4) |
| @mariaerduada111213 | Lila | pediu "por favor" (Ep. 4) |
| @_miraculosos_m | Caio | padre (Ep. 4) |
| @priestlyvibes | Andréa | desbravadora, na expedição (Ep. 4) |
| @mdangell | Yuki | veterinário (Ep. 4) |
| @lumin_hort | Ester | curandeira (Ep. 4) |
| @friren1000 | Lavinia | feiticeira (Ep. 4) |
| @creppy.candy | Amanda (#2) | artista e comerciante de tecidos (Ep. 4) |
| @amandssousasilver | Amanda (#3) | escriba (Ep. 4) |
| @mariaruthrochadac | Trubel | cozinheira (Ep. 4) |
| @sleep_moon12 | Luiza | bruxa no Ep. 4, santa no Ep. 5 |
| @alexandragoveia | Alexandra | exploradora e diplomata, na expedição (Ep. 4) |
| @pepzecomz | Pepze | o bruxo "???" do Ep. 4, ganhou nome no Ep. 5 |
| @mthsgs | Matheus | botânico (Ep. 4) |
| @sabrinaxavier129 | Sabrina | fazendeira (Ep. 4) |
| @cubo3a086 | cubo | guarda da vila (Ep. 5) |
| @deloxy987 | Delox | curandeiro de ervas (Ep. 5) |
| @leitoradiscreta | Vitória | banqueira (Ep. 5) |
| @orenjimsst | Meize | artista da vila (Ep. 5) |
| @eninh.a | Miyuki | taverneira (Ep. 5) |

**Erros que essa tabela evita:** a Lívia (@inuyashazinho) foi tratada como nova no Ep. 4, e a Luiza (@sleep_moon12) no
Ep. 5 ("aeeee" respondido com convite). As duas receberam uma 2ª resposta corrigindo.

## Ep. 1, "A Fundação" (09/11, 20h)
1. O perfil tem 7 seguidores: chegam 7 moradores, um a um.
2. "Bem-vindos a BRASA, um reino que cresce a cada seguidor."
3. Fogueira ao anoitecer: "…e 7 moradores sem nome. Só ganha nome quem se apresenta." Aparece o crachá
   "SEU NOME / SUA FUNÇÃO".
4. "E além da ponte… alguém acendeu uma luz." Os moradores reagem com um "!".
5. "Comenta seu nome e sua função. Os primeiros viram FUNDADORES."

Arquivos: `videos/brasa-ep1-hd.mp4` e `producao/capas/capa-brasa-ep1-hd.jpg`. Código em `producao/reino/` (versão detalhada: `world2.py` e `ep1hd.py`, canvas 360x640,
rodando com `N=<seguidores>` e `NAME=BRASA`).

## Ep. 2, "Os Fundadores" (atualizado em 10/11 às 18h com 15 fundadores; o perfil tinha 32 seguidores)
Os 15 fundadores, pela ordem dos comentários no Ep. 1:

| Nº | Nome | Função |
| --- | --- | --- |
| 001 | Gabriel | ferreiro |
| 002 | Lívia | construtora de casas (ela "constrói" o reino no timelapse) |
| 003 | Naty | confeiteira |
| 004 | Ana Sofia | adestradora de cão de caça (tem um cachorro) |
| 005 | Raviela | cavaleira (quer ser rainha depois de derrotar o inimigo que quer destruir o reino) |
| 006 | Rafael | pescador |
| 007 | Emanuel | bibliotecário |
| 008 | Victor | fazendeiro |
| 009 | Antônio | padeiro |
| 010 | Izabelly | caçadora |
| 011 | Francini | padeira |
| 012 | Cristal | guarda (função neutra: sem "o/a", "fundador(a)") |
| 013 | Rafaela | aventureira, "responsável por trazer recursos aos moradores" (boa candidata a atravessar a ponte no Ep. 3) |
| 014 | Maria | costureira |
| 015 | Gustavo | açougueiro |

Roteiro:
1. "Vocês comentaram o nome… e viraram moradores."
2. Chamada: 0,55 s por pessoa, com nome grande, função e "Morador 00X · Fundador(a)".
3. Timelapse "Com a Lívia construindo, o reino começou a crescer": Forja do Gabriel, Padaria (Antônio, Francini e Naty), Biblioteca do Emanuel,
   Píer do Rafael, Horta do Victor e o lampião da ponte.
4. Juramento da Raviela: "Vou derrotar o inimigo que quer destruir o reino… e um dia serei rainha."
5. "Naquela noite, a Cristal vigiava a ponte… e a luz estava mais perto."
6. "Comenta seu nome e sua função. Os próximos moram aqui."
7. Livro do Reino com os 15 nomes.

Arquivos: `videos/brasa-ep2.mp4` e `producao/capas/capa-brasa-ep2.jpg`. Carrossel em `producao/reino/cards/fundadores/`.

Código:
- `folk.py`: boneco por nome e função (chapéus, ferramentas e o cachorro da adestradora).
- `build.py`: construções.
- `ep2.py`: o episódio.

**Fios para o Ep. 3:** o inimigo da Raviela (é a luz?), a Cristal de guarda na ponte e os cães da Ana Sofia farejando.

## Ep. 3, "As Pegadas" (11/11; o perfil tinha 44 seguidores)
Os 20 moradores novos, pela ordem dos comentários no Ep. 2 (os outros 9 seguidores ainda não se apresentaram e aparecem sem nome):

| Nº | Nome | Função |
| --- | --- | --- |
| 016 | Kelly | artesã |
| 017 | Izabelle | médica |
| 018 | Oliveti | bruxa (poções) |
| 019 | Alerrandro | escultor |
| 020 | Lorena | filósofa/pensadora |
| 021 | Rubens | bruxo (visões e espíritos) |
| 022 | Viviane | artista |
| 023 | Cathe | mago (previsões/visões) |
| 024 | João | ferreiro |
| 025 | Bernardo | mágico curandeiro |
| 026 | Samuel | minerador |
| 027 | Cauby | matemático |
| 028 | Cauã | arqueiro |
| 029 | Valdemir | vaqueiro |
| 030 | Yasmim | cantora |
| 031 | Aurora | dançarina |
| 032 | Laura | louca |
| 033 | Nic | bobo da corte |
| 034 | Clara | enfermeira |
| 035 | Giovanni | alquimista |

Roteiro (24 s, sem voz por enquanto):
1. "ESTE REINO TEM 44 MORADORES." Os 44 já estão na praça desde o primeiro quadro.
2. **Meta coletiva:** "COM 100 MORADORES, A GENTE CONSTRÓI O CASTELO." Aparece o contorno do castelo, e a barra
   "MORADORES 44/100" fica no fim do vídeo.
3. "A Rafaela voltou da floresta com ervas pra chás e remédios… mas alguém seguiu ela." Pegadas brilhando atrás dela na ponte.
4. "O cão da Ana Sofia farejou as pegadas… e elas vão até o reino." O cão segue a trilha, e a Ana Sofia reage com um "!".
   (Compensa o Ep. 2, onde ela ficou escondida atrás da multidão na chamada.)
5. "Chegaram 20 moradores novos:" eles vão para um palco na frente da fogueira, 4 por vez, com foco de luz e crachá
   (nome e função) **embaixo dos pés**, pra ninguém ficar escondido.
6. "SEGUE e comenta seu nome e sua função pra virar morador." Barra 44/100 e castelo ao fundo; o final emenda no começo.

Versão narrada (11/11): `videos/brasa-ep3-narrado.mp4`, com 44 s. A voz Jhony Tygas foi gerada pelo Nasser no site, porque o
conector da ElevenLabs teve o plano grátis bloqueado ("atividade incomum"). O áudio está em `producao/reino/voz/ep3b.mp3` e o
tempo de cada cena em `voz/timing3.json` (BT = início de cada grupo de 4 nomes; D2/D3/D4/D6 = quando entra a 2ª linha da legenda).
Na chamada, o narrador lê os 20 nomes em 5 grupos de 4, no mesmo momento em que cada grupo sobe ao palco.

Arquivos: `videos/brasa-ep3.mp4` e `producao/capas/capa-brasa-ep3.jpg`. Código: `producao/reino/ep3.py`
(rodando com `N=<seguidores>`; `TIMING3=<json>` com S2, S3, S3B, S4, S4B, S5, S6 e TEND sincroniza com uma narração).

**Fios para o Ep. 4:** de quem são as pegadas (a luz da ponte?), o inimigo da Raviela, os bruxos e magos novos (Oliveti, Rubens,
Cathe e Bernardo) tendo visões, e o castelo como meta (a barra sobe a cada episódio).

## Ep. 4, "A Estátua" (12/11, para 19h; o perfil tinha 67 seguidores)
Primeiro episódio no **formato curto** (25,6 s), feito a partir das métricas de 11/11: ação no 1º segundo, o número de
moradores escrito por cima da cena e os nomes num desfile rápido.

Os 2 fundadores que ficaram de fora (comentaram no Ep. 1 antes de o Ep. 2 sair) e os 17 novos, pela ordem dos comentários:

| Nº | Nome | Função |
| --- | --- | --- |
| 036 | Julielen | arqueóloga e musicista (fundador(a) esquecido(a) no Ep. 2) |
| 037 | Robson | ajudante de coleta (fundador(a) esquecido(a) no Ep. 2) |
| 038 | Hanna | padeira |
| 039 | Amanda | açougueira |
| 040 | Giovanna | apotecária |
| 041 | Lila | ??? (não disse a função) |
| 042 | Caio | padre |
| 043 | Andréa | desbravadora |
| 044 | Yuki | veterinário |
| 045 | Ester | curandeira |
| 046 | Lavinia | feiticeira |
| 047 | Amanda | artista e comerciante de tecidos |
| 048 | Amanda | escriba |
| 049 | Trubel | cozinheira |
| 050 | Luiza | bruxa |
| 051 | Alexandra | exploradora e diplomata |
| 052 | ??? (pepze_comZ, não disse o nome) | bruxo |
| 053 | Matheus | botânico |
| 054 | Sabrina | fazendeira |

Roteiro:
1. "ESTE REINO TEM 67 MORADORES." Já no 1º segundo o pano vermelho com a chama voa da estátua.
2. "O Alerrandro esculpiu os fundadores." A estátua mostra Gabriel, Raviela e Lívia em pedra (ideia do próprio Alerrandro nos comentários).
3. "E gravou 2 nomes que faltavam: Julielen e Robson." Os dois vão até a estátua e recebem o selo de FUNDADORES.
4. "A Julielen cavou a base da estátua… e achou isso." Ela é arqueóloga: acha uma pedra antiga com uma runa turquesa, da
   mesma cor da luz da floresta, e os moradores reagem com "!".
5. "Chegaram 17 moradores novos:" eles vão ao palco em grupos de 4, 4, 3, 3 e 3, com crachá. A Lila aparece com função "???",
   e o bruxo sem nome com nome "???".
6. "A Rafaela, a Andréa e a Alexandra levaram a pedra… pra procurar outras vilas." Ideia da Rafaela nos comentários; a
   Andréa (desbravadora) e a Alexandra (exploradora) são os destaques novos.
7. "SEGUE e comenta seu nome e sua função pra virar morador." Barra 67/100 e o castelo ao fundo.

Arquivos: `videos/brasa-ep4.mp4`, `producao/capas/capa-brasa-ep4.jpg` e código `producao/reino/ep4.py` (`N=<seguidores>`;
`TIMING4=<json>` com S2, S2B, S3, S3B, S5, S4, S4B, S6, TEND e BT pra encaixar narração). Capa: `capa4.py`.

**Moradores novos já anotados pro Ep. 5 (os dois seguem):** "cubo" (comerciante, depois guarda da vila) e "Delox"
(curandeiro especializado em ervas medicinais).
Depois das respostas, chegou no Ep. 3 (12/11, à tarde): "Vitória Banqueira", do perfil "Leitora discreta". Entra no
Ep. 5. Ela não aparece entre quem seguiu desde a noite de 11/11, então a resposta levou o aviso de seguir.

**Respostas aos comentários: o Nasser liberou responder todos (12/11, 19h15).**
- Toda pessoa que comenta nome e função num episódio recebe resposta dizendo em qual episódio entra. Ela entra na fila
  aqui na bíblia.
- Se a pessoa não segue, a resposta leva "segue o perfil, do ep 5 em diante quem não segue não mora na vila".
- Comentário sem nome ("amo esses vídeos", "aeee") recebe um agradecimento curto + quando sai o próximo episódio.
- **Quem comemora que apareceu ("eu apareci", "minha biblioteca", "eu entrei") SEMPRE recebe resposta**, mesmo em
  episódio antigo. Pedido do Nasser em 13/11: "senão fica chato". A resposta lembra o papel da pessoa no reino.
- Jeito de escrever: sem emoji, minúsculo, "tu/teu", "kkk", e variar o fim das frases pra não ficar repetido.
- Jeito de postar: clicar com o mouse em "Responder" e "Publicar", digitar como teclado, com intervalo entre uma resposta
  e outra e em lotes pequenos (ver claude/canais/vcescolheaoub.md).

**Respostas já dadas:**
- Ep. 3: os 21 comentários (14h30) e a Vitória (17h20).
- Ep. 2: a Vitória (19h20), com "já te anotei, tu entra no ep 5 como banqueira".
- Ep. 1: o cubo (19h25), com "anotado, tu entra no ep 5 como guarda da vila, que foi o que tu pediu no ep 3".
- Os comentários antigos dos Eps. 1 e 2, de quem já virou morador nos Eps. 2 a 4, não foram respondidos um por um.
- Ep. 4 (20h30), os 5 comentários:
  - Miyuki: "anotada, tu entra no ep 5 como dona da taverna. e pode deixar que confusão na taverna vai ter kkk".
  - "nossa vilinha tá crescendo": "tá sim, faltam 33 pro castelo. comenta teu nome e tua função que tu entra no ep 5".
  - Ruth/Trubel: "entrou sim, a trubel cozinheira oficial do reino kkk".
  - Yuki: "apareceu sim, o veterinário do reino tá na área".
  - Lorena: "a filósofa do reino aprovou kkk".

**Fila do Ep. 5 (até 12/11, 20h30):**

| Nome | Função | Segue? |
| --- | --- | --- |
| cubo | guarda da vila (antes: comerciante) | sim |
| Delox | curandeiro de ervas medicinais | sim |
| Vitória | banqueira | não aparece entre os recentes |
| Miyuki | dona de uma taverna | sim (eninh.a) |
| Pepze, o bruxo de chapéu do Ep. 4 | volta com nome (ele mesmo disse "pepze_comZ") | sim |
| Meize | artista que desenha e registra os acontecimentos da vila | não aparece entre os 30 recentes (recebeu o aviso) |
| Luiza (já é moradora) | **troca de função: de bruxa vira santa** | sim (passou a seguir) |

Ideia de história: a Miyuki pediu "tiro, porrada e bomba na minha taverninha". Dá uma briga na taverna, ou a pedra
brilhando lá dentro.

**Ep. 4 publicado em 12/11 às 19h17** (ID 7707412652410096904). Na 1ª hora:
- 52 views, contra 54 do Ep. 2 e 51 do Ep. 3.
- 12 curtidas, 2 compartilhamentos e 5 comentários.
- Retenção: 76% no 1º segundo, 57% no 2º, 44% no 5º e 28% no 10º.
- **Tempo médio assistido: 15,5 s, o melhor da série** (Ep. 3: 13,0 s; Ep. 2: 10,7 s).

**Ep. 4 com 3h no ar (22h30):** 478 views, 43 curtidas, 5 compartilhamentos, 3 salvamentos e 10 comentários.
- Views por hora: 54, 90, 301. O Ep. 2 fez 54, 82, 366, então é a mesma curva.
- 5 seguidores novos vieram do vídeo. O perfil foi de 67 pra 73.
- Com a distribuição mais ampla, o tempo médio caiu pra 8,4 s. Retenção: 80% no 1º segundo, 58% no 2º.
- Respostas (22h30): Alexandra ("o que a expedição achar na floresta sai no ep 5"), Luiza (vira santa), "six seven"
  (convite pra comentar nome e função), Meize (entra no ep 5, com aviso de seguir) e Pepze (o bruxo volta com nome).

**Ep. 4 na manhã de 13/11 (07h):** 584 views, 50 curtidas, 5 compartilhamentos e 11 comentários.
- A distribuição parou de madrugada. Views por hora: 54, 90, 301, 85, 33, 14 e quase nada depois.
- Perfil com 73 seguidores.
- Julielen comentou "eu achei uma pedra!!!! tô feliz". Resposta: "achou e agora a vila inteira quer saber o que essa
  pedra faz kkk no ep 5 tem mais".
- Ep. 2 (13/11, 07h40), as comemorações que tinham ficado sem resposta:
  - Emanuel, "MINHA BIBLIOTECA": "a biblioteca do emanuel é ponto turístico do reino já kkk".
  - Ana Sofia, "eu": "tu mesma, fundadora e dona do cão de caça mais famoso do reino".
  Todas as outras comemorações (Eps. 3 e 4) já tinham resposta.
- **13/11, 07h45–08h40: "comente todos os comentários, pronto".** Foram respondidos todos os comentários antigos que
  estavam sem resposta: 21 no Ep. 1 e 27 no Ep. 2. Cada resposta diz o número de morador e em qual episódio a pessoa
  apareceu.
  - O João e o Alerrandro (Ep. 2) não carregam na página do vídeo no navegador. Foram respondidos pelo painel do Studio
    (Comentários → buscar → Responder abre o vídeo com todos os comentários).
  - Correção: a "nossa vilinha tá crescendo" (Ep. 4) é da **Lívia, fundadora 002**, e ontem foi respondida como se fosse
    nova. Ganhou uma 2ª resposta: "pera, tu é a lívia, a construtora fundadora kkk tua estátua tá aí no ep 4".
    **Antes de responder, conferir na tabela se a pessoa já é moradora.**
  - Conferência às 08h40, pelo servidor: zero comentários sem resposta nos Eps. 1 (46), 2 (58), 3 (44) e 4 (23) e no
    Bestiário (3).

**Respostas no Ep. 3 (12/11, 14h30):** os 21 comentários foram respondidos, sem emoji, dizendo quem está no Ep. 4 e quem
entra no Ep. 5.
- O bruxo sem nome (pepze_comZ) foi convidado a dizer o nome, que ele ganha no Ep. 5.
- Amanda (escriba) e Luiza receberam junto o aviso "segue o perfil, do ep 5 em diante quem não segue não mora na vila".

**Fios para o Ep. 5:** o que a expedição acha na floresta (outra vila? quem acendeu a luz?), o que significa a runa da pedra
e o nome do bruxo sem nome.

## Ep. 5, "A Taverna" (13/11, no almoço; o perfil tinha 73 seguidores)
Sem voz, 26,8 s. Código: `producao/reino/ep5.py` (`N=<seguidores>`) e capa `capa5.py`.
**Publicado em 13/11 às 12h24** pelo Nasser, sem narração (ID 7707677278490184966).
Com 1h16 no ar (13h40): 45 views, 7 curtidas, 2 compartilhamentos, 3 comentários e 1 seguidor novo (perfil com 74).
- **Tempo médio de 21,3 s, o melhor da série** (o Ep. 4 tinha 15,5 s na 1ª hora). 33% veem até o fim (Ep. 3: 9%).
- Ficam 82% no 1º segundo, 51% aos 3 s e 27% aos 10 s. Origem: Para Você 65%, perfil 16%.
- Respostas (sem emoji, clicando com o mouse):
  - Miyuki ("BORA AGITAR ESSA CIDADEE!!"): "agitou até demais kkk primeiro dia de taverna e já teve briga. e agora tem pegada
    brilhando lá dentro, fica de olho".
  - Pepze ("ai sos era eu eu sempre soube", com print do crachá "ERA O ???"): "era tu sim kkk o bruxo misterioso agora tem
    nome. e aí, tu sabe de quem são as pegadas na taverna?".
  - sleep (@sleep_moon12, "aeeee" às 16h57) foi respondida como nova por engano; ela é a **Luiza**. Correção às 20h10:
    "pera, tu é a luiza kkk já é moradora sim, apareceu no palco agora como santa, com auréola e tudo".
Com 4h no ar (16h20): **118 views** (por hora: 42, 29, 25, 20), 13 curtidas, 2 compartilhamentos, 1 seguidor novo (74).
- O Ep. 4, postado às 19h, tinha 478 views com 3h (por hora: 54, 90, 301). O Ep. 5 não foi empurrado para um público maior.
- Tempo médio caiu de 21,9 s na 1ª hora para 4,1 s na 4ª hora (total 13,3 s); 19% veem até o fim.
  Na 1ª hora quem assistia era morador; depois veio gente de fora pelo Para Você (81%), e 56% saem antes dos 3 s.
- Aprendizados: (1) almoço rende menos que 19h pro Brasa; (2) a abertura com o castelo e "ESTE REINO TEM 73 MORADORES"
  não segura quem não conhece. **No Ep. 6, abrir com ação (briga, pegadas, algo acontecendo) no 1º segundo.**
Arquivos: `videos/brasa-ep5.mp4` e `producao/capas/capa-brasa-ep5.jpg`.

Roteiro:
1. Abre na vila de dia: o contorno do castelo se desenha até **73%** (a meta é 100) com "ESTE REINO TEM 73 MORADORES."
   e depois "FALTAM 27 PRO CASTELO." O resto do castelo fica bem apagado, pra mostrar quanto falta.
2. Floresta à noite: a pedra guia a expedição (Rafaela, Andréa e Alexandra) até **ruínas de outra vila** (muros quebrados,
   coluna caída, calçamento antigo). Uma laje de pedra tem **o mesmo símbolo da pedra**, e ele acende quando elas chegam.
3. Palco na praça (entardecer), com crachá embaixo dos pés:
   - "CHEGARAM 5 MORADORES NOVOS:" cubo (guarda), Delox (curandeiro), Vitória (banqueira), Meize (artista) e Miyuki (taverneira).
   - "E 2 NOVIDADES:" Luiza ("AGORA É SANTA", com auréola) e Pepze ("ERA O ???", o bruxo de chapéu do Ep. 4).
4. "A MIYUKI ABRIU UMA TAVERNA…" (à direita da estrada, abaixo da horta) "…E NO PRIMEIRO DIA JÁ TEVE BRIGA."
   Nuvem de poeira de desenho animado, canecas e tábuas voando, "PÁ! POF! CRÁS! TUM!", tela tremendo. Quem briga são 3
   moradores sem nome (ninguém identificado apanha).
5. "QUANDO A POEIRA BAIXOU…" os 3 estão tontos no chão, o guarda cubo chega atrasado, e **pegadas brilhando, iguais às do
   Ep. 3, entram na taverna**. A Miyuki e o cubo ficam com "?".
6. Final: "QUEM NÃO SEGUE NÃO MORA NA VILA." + barra 73/100 + "COMENTA TEU NOME E TUA FUNÇÃO".

Decisões do Nasser (13/11):
- "Ainda é cedo para monstros": nada de criaturas do Bestiário no Brasa por enquanto.
- A Vitória e a Meize entram mesmo sem seguir, mas a frase "quem não segue não mora na vila" continua no fim.
- Ep. 5 saiu no almoço, no lugar do "PAUSA O VÍDEO".

Bonecos novos em `folk.py`: banqueira (colete com botões dourados, óculos e saco de moedas), taverneira (avental, lenço e
caneca) e santa (roupa branca e auréola). `NEW_EP5` e `EP5_CHANGES` (Luiza vira santa; "???#bruxo" vira Pepze).

**Fios para o Ep. 6:** de quem são as pegadas que entraram na taverna, quem morava nas ruínas e por que elas têm o símbolo
da pedra, e quem começou a briga.

## Bestiário de Brasa (série irmã, desde 12/11)
As criaturas da floresta do outro lado da ponte saem da série **Bestiário de Brasa**, a "Roleta do Nome", às 19h
(bíblia: `claude/series/roleta-do-nome.md`). Cada nome comentado lá vira uma criatura com raridade e poder.
Elas **podem aparecer na história**: a expedição da Rafaela pode encontrar criaturas de quem comentou, de preferência
épicas e lendárias, com o nome da espécie e do "dono".

## Próximos episódios (rascunho)
- **Ep. 4 em diante:**
  - cada episódio traz moradores novos com nome, mais uma construção ou acontecimento e um passo do mistério;
  - quando o perfil bater uma marca (50, 100…), sai um episódio especial de "festa". Em 100 sai o episódio do castelo.

## Recompensas para quem participa (decidido em 09/11)
Todo mundo que se apresenta ganha alguma coisa. O nível muda conforme o número de comentários:
- **Todo morador:**
  - um boneco único gerado a partir do nome (sempre o mesmo boneco para a mesma pessoa);
  - aparece no próximo episódio com crachá de nome e função;
  - entra no **Livro do Reino**, a cartela final com todos os nomes (dá pra pausar e se achar).
- **Fundadores (quem comentou no Ep. 1):** selo de FUNDADOR(A) para sempre na carteirinha e uma chama no crachá.
- **Carteirinha de morador:** imagem com o boneco, o nome, a função, o número de morador e a data
  (código em `producao/reino/cards/carteira.py`).
  - Sai num **post de fotos (carrossel)**, um por episódio.
  - Por ser uma imagem "minha", é o que a pessoa compartilha.
- **Função vira construção:** quando várias pessoas escolhem uma função, ela vira um prédio com o nome de quem a pediu
  (ex.: "Forja da Lia", "Padaria do João").
- **Destaques:** de 1 a 3 moradores por episódio viram personagens da história (ex.: quem atravessa a ponte).
- **Resposta:** cada comentário recebe um "Bem-vindo(a) a Brasa, Fulano, nosso(a) [função]!".

### Cuidados
- Usar só o nome e a função que a pessoa escreveu. Nunca a foto do perfil nem o @, a não ser que ela peça.
- Pular nomes ou funções ofensivos.
- A ordem de chegada define o número de morador.

## Rotina de produção
1. Na manhã seguinte ao post, o Nasser manda print dos comentários (nome e função).
2. Listar os fundadores na ordem dos comentários e escrever a história do episódio com eles.
3. Atualizar o número de seguidores e renderizar.
4. Fixar o comentário de exemplo e responder cada morador ("Bem-vindo(a) a Brasa, Fulano!").
