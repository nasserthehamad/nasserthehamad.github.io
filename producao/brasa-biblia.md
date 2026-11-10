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
- **O número do gancho é sempre o real:** "Este perfil tem X seguidores." Confirmar com o Nasser antes de renderizar.
- **Só ganha nome quem comenta pedindo.** Ninguém aparece no vídeo sem ter se apresentado.
- **Sem narrador:** só texto na tela (fonte pixel Jersey 10), trilha 8-bit sintetizada e efeitos. Não gasta ElevenLabs.
- **Duração:** entre 20 e 25 s, com o final emendando no começo (loop).
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

## Próximos episódios (rascunho)
- **Ep. 2, "Os Fundadores":** os comentaristas aparecem com nome e função (crachás) e fazem a primeira construção, de
  acordo com as funções que escolheram. À noite, a luz do outro lado da ponte **chega mais perto**.
- **Ep. 3 em diante:**
  - cada episódio traz moradores novos com nome, mais uma construção ou acontecimento e um passo do mistério;
  - quando o perfil bater uma marca (50, 100…), sai um episódio especial de "festa".

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
