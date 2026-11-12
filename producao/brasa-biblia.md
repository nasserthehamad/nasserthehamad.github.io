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

**Fios para o Ep. 5:** o que a expedição acha na floresta (outra vila? quem acendeu a luz?), o que significa a runa da pedra
e o nome do bruxo sem nome.

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
