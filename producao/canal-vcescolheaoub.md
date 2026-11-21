# Canal @vcescolheaoub — "Você Escolhe A ou B"

**Desde 12/11 são 2 posts por dia.** O Bestiário/Roleta do Nome do almoço foi pausado em 13/11, e nesse dia o Brasa Ep. 5 saiu no almoço. Desde 09/11 o carro-chefe é o BRASA (reino em pixel art em que cada seguidor vira morador; bíblia em
`claude/series/brasa.md`). As séries de votação A/B terminaram: Quem Bate à Porta em 08/11 e A Marmita Sumiu em 11/11.
O plano de 08/11 ("Golpe ou não?" e "Escolhe e paga o preço", Claude Doc https://claude.ai/artifact/N2nV84GJFyGFRKWJogUzGS)
não chegou a ser postado.

**Perfil só do Brasa (16/11, pedido do Nasser):** tudo que não é do Brasa virou "Somente eu" pelo TikTok Studio.
- **Privados (10):** 10.000 Passos Dia 1, os 5 da Marmita (incluindo o final, que só citava o Brasa no fim) e os 4 da Porta.
- **Públicos (9):** Brasa Ep. 1 a 6, Bestiário #001 (Florora), a fogueira e o cercado das ovelhas.
- A série 10.000 Passos fica parada.
- No Studio a lista é virtual: depois de trocar a privacidade, o seletor às vezes volta a mostrar "Todos". Pra conferir,
  recarregar a página e rolar até o fim.

- **Conta:** pessoal, pública. O @vcescolheaoub continua.
  - **Nome exibido:** vai virar **"Reino de Brasa"** (escolha do Nasser em 12/11). O TikTok só libera trocar o nome depois de
    12/11, e a troca é uma vez a cada 7 dias. Trocar a partir de 13/11.
  - **Bio (desde 21/11, escolha do Nasser):** "um reino que cresce a cada seguidor / comenta teu nome e entra na história", sem emoji.
    A anterior (12/11) ainda falava do Bestiário: "🔥 Cada seguidor vira morador de Brasa / 🎰 Comenta seu nome: vira criatura".
    Trocar a bio pelo navegador: Editar Perfil → Descrição → Salvar. A página recarrega e às vezes ainda mostra a bio antiga; conferir de novo depois de recarregar.
  - **Foto:** o logo "chama com castelo" (pixel art; `producao/logo/logo-a.png`). Também foram feitos um "B" com chama e um
    brasão com coroa. Uma chama com olhos foi descartada por lembrar o Calcifer.
- **Postagem:** pelo app, ou pelo TikTok Studio na web, no navegador do app do Claude (desde 11/11; o Nasser só escolhe o
  arquivo). Pelo Metricool o vídeo não é distribuído.
  - **Pedido do Nasser (15/11): legenda e comentário pra fixar sempre em bloco de código**, pra copiar fácil no celular.
    Quando ele for postar pelo celular: mandar vídeo + capa (e salvar na pasta Downloads) e os dois textos em blocos separados.
- **Métricas:** o Claude lê direto no TikTok Studio (navegador do app, conta logada). Dados brutos em
  `producao/metricas/tiktok-AAAA-MM-DD.json` no GitHub.

## Séries

| Série | Formato | Status | Bíblia |
| --- | --- | --- | --- |
| **Brasa** | reino pixel art, narrado (Jhony Tygas) | Ep. 4 em 12/11 à noite. Em andamento, 1 por dia. | `claude/series/brasa.md` |
| **10.000 Passos** | POV pixel art (tela 180x320; `RES=1` volta pra 90x160): herói com espada numa trilha de pedra na floresta. Cada seguidor = 1 passo; cada vídeo anda dos seguidores de ontem até os de hoje. Abre com "DISSERAM PRA ELE NÃO IR LÁ… MAS ELE CONTINUA ANDANDO", placa "VOLTE" na beira da trilha e uma torre brilhando no fim (o objetivo, 10.000). Sem voz. | Ideia do Nasser em 13/11. Dia 1 = 74 passos (`videos/passos-dia1.mp4`, código `producao/passos/passos.py`, rodar com `N=<seguidores> PREV=<ontem> DIA=<n>`). **Dia 1 publicado em 13/11 às 19h01 pelo Studio web (ID 7707779619792981269), sem selo de IA e sem música (pedido do Nasser: só os efeitos sonoros).** Amanhã: `PREV=74`. 1ª hora (20h05): 35 views, 3 curtidas, 0 comentários, 0 seguidores novos; tempo médio 5,3 s (de 17 s), 12,5% até o fim; ficam 63% no 1º segundo, 46% aos 3 s, 21% aos 10 s; Para Você 96% (só gente de fora). **Pro Dia 2: começar andando já no 1º quadro (no Dia 1 o 1º segundo era parado), com a placa VOLTE mais perto da câmera logo no início.** | — |
| **Bestiário de Brasa** (Roleta do Nome) | 6 roletas com % → criatura pixel + poder total, sem voz | #001 (Jonas, MUSGUR, lendário, 93) em 12/11 no almoço. Pausada em 13/11 (flopou). | `claude/series/roleta-do-nome.md` |
| A Marmita Sumiu | comédia narrada, votação A/B | Encerrada: final publicado em 11/11 às 19h58 | `claude/series/a-marmita-sumiu.md` |
| Quem Bate à Porta | suspense narrado, votação A/B | Encerrada em 08/11 | `claude/series/quem-bate-a-porta.md` |
| O Pix Errado | narrada | Não postada | `claude/series/o-pix-errado.md` |

## Métricas em 11/11, 20h (TikTok Studio)

**Conta:** 65 seguidores (+34 em 7 dias). Nos últimos 7 dias: 4,7 mil views, 229 visitas ao perfil, 233 curtidas, 70 comentários,
4 compartilhamentos e 2,2 mil espectadores (quase todos novos).
- **De onde vêm:** Para Você 94%, perfil 6%, busca 0,3%. O feed "Seguindo" dá 0%.
- **Buscas que trouxeram gente:** "vc escolhe a ou b" (33%) e variações do nome do perfil.
- **Quem assiste:** 52% mulheres e 47% homens. 18–24 anos são 45%, 25–34 são 30%. Brasil 99%.
- Gênero, idade e horários dos **seguidores** só aparecem a partir de 100 seguidores.

| Vídeo | Postado | Duração | Views | Tempo médio | Até o fim | Ficam 3 s | Ficam 10 s | Seguidores | Coment. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Brasa 3 | 11/11 12h31 | 44 s | 592 | 11,3 s | 9,1% | 48% | 26% | 7 | 18 |
| Brasa 2 | 10/11 18h37 | 41 s | 684 | 10,6 s | 5,7% | 51% | 27% | 12 | 28 |
| Brasa 1 | 09/11 20h05 | 26 s | 520 | 10,5 s | 12,1% | 50% | 21% | **38** | 23 |
| Marmita 4 | 09/11 12h11 | 30 s | 202 | 10,9 s | 12,5% | 58% | 33% | 1 | 3 |
| Porta 4 | 08/11 19h22 | 36 s | 210 | 6,0 s | 2,3% | 36% | 16% | 0 | 0 |
| Marmita 3 | 08/11 11h05 | 31 s | 829 | 8,9 s | 10,1% | 53% | 25% | 0 | 5 |
| Porta 3 | 07/11 22h15 | 36 s | 361 | 5,4 s | 3,5% | 29% | 12% | 0 | 0 |
| Marmita 2 | 07/11 9h17 | 33 s | 658 | 10,6 s | 7,6% | 58% | 29% | 0 | 3 |
| Porta 2 | 06/11 17h31 | 38 s | 288 | 6,8 s | 3,9% | 36% | 18% | 0 | 4 |
| Marmita 1 | 06/11 11h29 | 31 s | 634 | 13,0 s | 12,1% | 57% | 34% | 7 | 8 |
| Porta 1 | 05/11 18h37 | 38 s | 610 | 7,3 s | 5,7% | 37% | 16% | 2 | 2 |

**Por série:**
- **Brasa:** 32 seguidores e 38 comentários a cada 1.000 views.
- **Marmita:** 3,4 seguidores e 8 comentários a cada 1.000 views.
- **Porta:** 1,4 seguidor e 4 comentários a cada 1.000 views.

## Aprendizados
- **O Brasa é o que traz seguidor.** É 10 vezes mais que a Marmita por view, porque seguir é o "ingresso" pra virar morador.
  - O Ep. 1 sozinho trouxe 38.
  - A conversão cai a cada episódio (73 → 18 → 12 por mil). Quem já seguiu não segue de novo, e o vídeo precisa convencer gente nova.
- **Todo vídeo para em 200–800 views:** é o primeiro lote do Para Você, e nenhum foi liberado para um público maior.
- **O que decide isso são os 3 primeiros segundos.**
  - No Brasa, metade sai até os 3 s e 20% saem já no primeiro segundo.
  - A Marmita segurava mais (57–58% aos 3 s), porque a primeira cena tinha conflito.
  - Na Porta saía quase todo mundo (29–37%).
- **Brasa narrado longo (41–44 s):**
  - O tempo médio fica em ~11 s, igual ao Ep. 1 de 26 s, e quase ninguém vê a chamada de nomes do fim (18% aos 20 s, 5% no fim).
  - A recompensa (o nome na tela) só chega pra quem já é morador.
- **Comentário rende no Brasa** (30–44 por mil). Na Marmita e na Porta, quase ninguém comentou.
- Voz de IA animada, telas realistas, "vocês escolheram B" e pedidos no fim: valem as observações do estudo de 08/11.
- **Texto que sai em nome do Nasser (respostas, comentário fixado):** sem emoji, tudo minúsculo e solto, com "kkk" e "teu".
  Pedido dele em 12/11: emoji "fica com muita cara de IA".
  - Ex.: "fofinha mas tem 63 de poder hein kkk fala teu nome aqui que ele vira carta no próximo sorteio".
  - Fixar comentário só dá pelo app do celular. No TikTok Studio e na página do vídeo no navegador só tem Responder e Excluir.
  - **Como responder pelo navegador (combinado em 12/11):** clicar com o mouse em "Responder" e em "Publicar", nunca por script.
    Digitar como teclado. Fazer em lotes pequenos, com intervalo entre as respostas, e nada de dezenas seguidas.
    - Motivo: o navegador se identifica como "Claude" e um clique por script é detectável. As regras do TikTok proíbem
      interação automatizada.
    - Não usar `execCommand('insertText')` no campo de resposta: derrubou o painel de comentários ("Algo deu errado").
- **Bestiário #001 (12/11, 12h35), com 1h25 no ar:** 22 views (o Brasa Ep. 3 fez 51 na 1ª hora no mesmo horário).
  - Retenção aos 2 s: 48%, contra 58–60% no Brasa. Do 5º segundo em diante, igual ao Brasa.
  - Média de 10 s assistidos de 25; 7% veem até o fim.
  - Suspeita: o começo com cartas pequenas prende pouco. No #002, abrir com o ovo/criatura e encurtar o sorteio para ~2,5 s.

## Análise de 16/11 (19 vídeos, 83 seguidores)
| Vídeo | Views | Fica 3 s | Fica 10 s | Tempo médio | Seguidores | Coment. |
| --- | --- | --- | --- | --- | --- | --- |
| Brasa 1 (26 s) | 585 | 50% | 22% | 10,3 s | **40** | 24 |
| Brasa 2 (41 s) | 743 | 50% | 27% | 10,7 s | 13 | 32 |
| Brasa 3 (44 s) | 655 | 49% | 28% | 13,2 s | 7 | 22 |
| Brasa 4 (33 s) | 632 | 47% | 25% | 9,3 s | 6 | 11 |
| Brasa 5 (26 s, promovido) | 11,7 mil | 20% | 5% | 3,2 s | 6 | 8 |
| Brasa 6 (26 s) | 282 | 35% | 8% | 4,5 s | 0 | 3 |
| Fogueira (25 s) | 1.005 | **60%** | **41%** | 11,3 s | 0 | 1 |
| 10.000 Passos (17 s) | 673 | 46% | 21% | 5,3 s | 0 | 0 |
| Bestiário (25 s) | 192 | 31% | 14% | 5,6 s | 1 | 1 |

**O que funciona:**
- A promessa "segue que tu vira morador": o Ep. 1, que só falava isso, trouxe 40 dos 83 seguidores.
- Moradores comentam e voltam: os que mais comentam são justamente os que aparecem no vídeo.
- O "será que…?" com física (a fogueira) segura gente de fora como nenhum outro: 60% aos 3 s, e ganhou um 2º lote do
  Para Você.

**O que não funciona:**
- **Cada episódio do Brasa converte menos** (68 → 17 → 11 → 9,5 → 0 seguidores por mil views). A história ficou de
  "quem já mora": viajante, runa, pegadas não dizem nada pra quem chega agora, e a promessa sumiu do começo. O Ep. 6
  perdeu metade das pessoas entre o 1º e o 3º segundo.
- **A fogueira prende, mas não pede nada:** sem nome e sem promessa na tela, deu 0 seguidor.
- **Promoção com objetivo de views:** 11,7 mil views de gente que sai no 1º segundo, só 6 seguidores.
- **Séries paralelas** (Passos, Bestiário, memes): ninguém comenta, 0–1 seguidor, e dividem o perfil.

**Próximo teste:** juntar os dois. O gancho da fogueira/cercado no 1º segundo e a promessa do Ep. 1 na tela ("comenta teu
nome que tu vira ovelha/morador"), com os nomes de quem comentou aparecendo no vídeo seguinte. Nos episódios do Brasa,
repetir a promessa nos primeiros 2 s e fazer cada um entendível sem ter visto os anteriores.

## "Flopamos?" — situação em 19/11 (85 seguidores)
Números diários da conta no Studio. 18/11 e 19/11 ainda não estavam calculados.

| Dia | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Views | 927 | 1.091 | 958 | 741 | 939 | 1.302 | 899 | 913 | 8.146* | 5.245* | 1.074 | 671 |
| Seguidores novos | 5 | 0 | 2 | 1 | 26 | 31 | 2 | 7 | 5 | 1 | 3 | 0 |
| Visitas ao perfil | 60 | 34 | 33 | 30 | 70 | 87 | 28 | 32 | 52 | 28 | 19 | 8 |

\* promoção paga do Brasa Ep. 5.

**Leitura: o canal não flopou, estagnou.**
- Não é shadowban. Cada vídeo novo ainda ganha o primeiro lote do Para Você: a copa de lava fez 126 views em 12 h, e as
  views voltaram de manhã depois de zerar de madrugada.
- Nenhum vídeo passa desse primeiro lote (200–1.000 views). As views por dia ficam em ~700–1.300 desde 06/11.
- O que caiu foi a conversão:
  - 57 dos 85 seguidores vieram em 10–11/11, com o Brasa Ep. 1 ("segue que tu vira morador").
  - Desde então são 0 a 7 seguidores por dia.
  - As visitas ao perfil caíram de 70–87 para 8 por dia.
  - Os vídeos de física seguram mais gente, mas não pedem nada.

**Proposta de 19/11:** copa/corrida com o nome de quem comentou em cada bolinha, pedindo "comenta teu nome e entra na
próxima copa". Junta a retenção da física com o motivo para comentar e seguir.

**Como puxar isso no Studio:** pedir `{insigh_type:'vv_history'|'net_follower_history'|'pv_history'|'reached_audience_history'|'follower_num_history', days:N, end_days:0}`
no mesmo endpoint de insight. Cada item vem como `{status, value}` em ordem de data, e os últimos 1–2 dias chegam com
`status: 2` (ainda não calculados).

## Tendências do TikTok (13/11)
**No próprio TikTok (Studio → Inspiração, filtro Brasil, 12h):** ENEM domina ("Chego no Enem" 79M, "redação sobre SUS" 54M,
"Comida pro ENEM" 33M), depois Vasco x Palmeiras, F1 em Interlagos e Teleton. Na aba "Recomendado" (contas parecidas com a
nossa): animações curtas "Neste mundo…" com reviravolta no fim (até 409K), histórias animadas de Roblox (300–470K) e #rpgdemesa.
- "O reino nos memes" (#1 "go go go" com o guarda) foi feito e o Nasser não gostou; a série do almoço virou a **10.000 Passos**.

**Pela web, antes do navegador voltar:**
- **Histórias animadas em partes** ("Zombie Outbreak Survival Stories"): narradas em 2ª pessoa, em lugares conhecidos,
  numeradas, com gancho no fim e pergunta pro público escolher. É o formato do Brasa. Vale numerar bem ("EP. 5") e terminar
  com pergunta (no Ep. 5: "de quem são as pegadas?").
- **"Why would I deceive you?"**: áudio sério sobre algo que vai dar errado. Serve pra uma piada curta do reino.
- **"Go go go"** e **"Answer in one word"**: áudios em alta, fáceis de adaptar.
- **Dame Hombro** (Bulin 47): dancinha de ombro, a mais citada no Brasil.
- Fontes: newengen.com/insights/tiktok-trends, ramd.am/blog/trends-tiktok, anijam.ai/blog/tiktok-trends.

## Próximos passos (proposta de 11/11)
- **Brasa com 25–30 s.**
  - Ação e mistério no primeiro segundo, com o "ESTE REINO TEM N MORADORES" por cima da ação, não numa cena parada.
  - Moradores novos num desfile rápido (6–8 s).
  - O Livro do Reino completo no último quadro: dá pra pausar e se achar, o que também gera replay.
- **Meta de 100 seguidores:** libera os dados dos seguidores e vira o episódio do castelo.
- **Ler as métricas 24 h depois de cada post** (o Claude puxa direto do Studio) e comparar com esta tabela.
