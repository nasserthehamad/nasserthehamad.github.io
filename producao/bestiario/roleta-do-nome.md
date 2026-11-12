# Bestiário de Brasa (Roleta do Nome) — bíblia da série

Segunda série diária do @vcescolheaoub, criada em 12/11 para postar 2 vídeos por dia junto com o **Brasa**.
Ideia aprovada pelo Nasser ("baita ideia"). A mecânica de roleta com porcentagens e pontos totais também foi pedido dele.

**Contexto (Nasser, 12/11):** é o **bestiário do Brasa**. As criaturas povoam a floresta do outro lado da ponte e **têm
chance de aparecer na história** do Brasa, o que é um prêmio a mais pra quem comenta.
- No vídeo: "VIVE NA FLORESTA DE BRASA" embaixo do nome da espécie, a luz turquesa piscando na floresta do fundo, e o fim
  "COMENTA SEU NOME E SUA CRIATURA PODE APARECER NA HISTÓRIA DE BRASA".
- Na capa: "BESTIÁRIO DE BRASA #001".
- No Brasa: a expedição da Rafaela (Ep. 4) entrou na floresta, e criaturas do bestiário podem cruzar o caminho dela
  (sempre as de quem comentou, de preferência épicas e lendárias).

## A ideia em uma frase
Cada nome comentado passa por **6 roletas com porcentagem**, e no fim choca uma **criatura em pixel art** com **PODER TOTAL**.
O mesmo nome dá sempre a mesma criatura.

## Por que esta série
- Os números de 11/11 mostraram que a conta cresce quando **o comentário vira conteúdo**: o Brasa trouxe 32 seguidores por
  mil views; as séries de votação A/B trouxeram 1 a 3.
- **Sem narração.** Sobram ~1.900 créditos na ElevenLabs, o suficiente pra uns 3 episódios narrados do Brasa. Esta série usa só
  texto na tela, trilha 8-bit e efeitos.
- A raridade gera comentário ("saí lendário!") e marcação de amigos.

## Formato (~21 s, 1 nome por vídeo)
1. Desde o 1º quadro: "QUAL CRIATURA É O SEU NOME?" + o nome grande, com a roleta já girando.
2. Roletas, cada uma com a % na fatia e o resultado grande no centro quando para:
   **ELEMENTO → RARIDADE → FORMA → FORÇA → VELOCIDADE → MAGIA.**
   Cada resultado vira uma ficha embaixo (valor e %).
   - Se a raridade der ÉPICO ou LENDÁRIO, o nome da raridade explode grande na tela. É o pico do vídeo.
3. O ovo cai, treme e choca. Aparece a criatura com o **nome da espécie na cor da raridade**, e o **PODER TOTAL** sobe contando.
4. Fim: "COMENTA SEU NOME / E SUA CRIATURA PODE APARECER / NA HISTÓRIA DE BRASA". O final emenda no começo (loop).

## Probabilidades (fixas e mostradas nas fatias)
| Roleta | Fatias |
| --- | --- |
| Elemento | Fogo 18 · Água 18 · Planta 18 · Pedra 14 · Raio 12 · Gelo 10 · Sombra 6 · Cristal 4 |
| Raridade | **Comum 40 (cinza) · Incomum 30 (verde) · Raro 17 (azul) · Épico 9 (roxo) · Lendário 4 (laranja)** |
| Forma | Bolha · Fera · Ave · Dragão · Golem (20 cada) |
| Força, Velocidade, Magia | 1 a 10, com pesos 4 · 6 · 9 · 12 · 15 · 15 · 13 · 11 · 9 · 6 % |

**Poder total** = (força + velocidade + magia) / 30 × 70, arredondado, mais o bônus de raridade
(Comum 0 · Incomum 8 · Raro 15 · Épico 22 · Lendário 30). Vai de 7 a 100.

**Nome da espécie** = o nome até a 2ª vogal + o sufixo do elemento (flama, maré, folha, rocha, raio, breu, neve, cristal).
Ex.: Letícia + Fogo = LETIFLAMA.

Todo resultado sai de um hash do nome normalizado (minúsculo e sem acento), com uma "semente" diferente por roleta.
Por isso é justo e repetível: "Leticia" e "Letícia" dão a mesma criatura.

## Episódios
| # | Nome | Resultado | Poder | Postado |
| --- | --- | --- | --- | --- |
| 001 | Letícia | Fogo 18% · **LENDÁRIO 4%** · Golem · F5 V5 M6 → LETIFLAMA | 67 | piloto, 12/11 às 19h (proposta) |

O piloto usa um nome comum na faixa de 18 a 34 anos e escolhido por dar Lendário, pra estrear forte.
Daqui pra frente, os nomes **vêm dos comentários, na ordem de chegada**.

## Regras
- Só o primeiro nome, como a pessoa escreveu. Nunca o @ ou a foto. Pular nomes ofensivos e nomes de famosos.
- Fixar o comentário: "Comenta só o seu nome 👇 Os próximos vídeos giram a roleta dos nomes daqui."
- Se a fila crescer muito: fazer um vídeo de "rodada relâmpago", com 3 nomes por vídeo e roletas mais rápidas.
- Ligação com o Brasa: as criaturas vivem na floresta do outro lado da ponte. A expedição da Rafaela pode encontrá-las.

## Código
`producao/bestiario/` no GitHub:
- `creature.py`: o gerador. Roletas, traços e o desenho 40x40 com contorno e sombra.
- `roleta.py`: o vídeo. Roda com `NAME=<nome> python3 roleta.py`, e o resultado sai em `out/bestiario-<nome>.mp4`.
- `capa.py`: a capa.
