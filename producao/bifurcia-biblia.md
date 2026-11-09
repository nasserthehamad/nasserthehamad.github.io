# Bifúrcia — bíblia da série

Criada em 09/11 a partir de uma referência do Instagram (página "brukmont": cada seguidor vira morador de um reino em
pixel art). **Aproveitamos só a mecânica.** Arte, nome, mundo e regras são nossos. Perfil: @vcescolheaoub.

## A ideia em uma frase
Um reino numa **bifurcação de estrada** (placa **A ←  → B**), onde **cada seguidor vira morador**, e os moradores
decidem tudo no A ou B.

## Regras
- **O número do gancho é sempre o real**: "Este perfil tem X seguidores." Confirmar com o Nasser antes de renderizar.
- **Só ganha nome quem comenta pedindo.** Ninguém aparece no vídeo sem ter se apresentado nos comentários.
- **Formato do comentário:** nome, função e voto (ex.: "Lia, ferreira, A").
- **Sem narrador.** Só texto na tela (fonte pixel Jersey 10), trilha 8-bit sintetizada e efeitos. Não gasta ElevenLabs.
- Duração entre 20 e 25 s. O final emenda no começo (loop).
- O gancho não dá spoiler e não sugere o voto.
- Postar com o áudio original, sem música do app por cima.
- Visual: vista de lado, tipo diorama (a referência é vista de cima). Cores das opções: **A = turquesa, B = laranja**.

## O mundo
- **Centro:** praça com fogueira na bifurcação. A placa A aponta para a estrada da esquerda ("o mundo"). A placa B aponta
  para a **ponte**.
- **Do outro lado da ponte:** floresta escura. Desde o Ep. 1 aparece ali uma **luz misteriosa** (turquesa, piscando),
  sem nenhum texto explicando. É o mistério de fundo da série. Não explicar cedo.
- **Bandeira do reino:** metade turquesa (A), metade laranja (B).

## Ep. 1, "A Fundação" (09/11, 20h)
- O perfil tem 7 seguidores, então chegam 7 moradores sem nome e ficam em volta da fogueira.
- "Só ganha nome quem se apresenta" vem com o crachá "SEU NOME / SUA FUNÇÃO".
- 1ª decisão: **A) Taverna × B) Muralha**.
- Pedido no fim: "Comenta seu nome, sua função e seu voto. Os primeiros viram FUNDADORES."
- Arquivos: `videos/bifurcia-ep1.mp4` e `producao/capas/capa-bifurcia-ep1.jpg`. Código em `producao/reino/`
  (`world.py` + `ep1.py`, com `N=<seguidores>`).

## Próximos episódios (rascunho)
- **Ep. 2, "Os Fundadores":** os comentaristas aparecem com nome e função (crachás). Os fundadores constroem o que venceu
  (taverna ou muralha). À noite, a luz do outro lado da ponte **chega mais perto**.
  - Próxima decisão: **A) atravessar a ponte × B) trancar a ponte**.
- **Ep. 3 em diante:** cada episódio traz moradores novos com nome, uma construção ou acontecimento e uma decisão A/B.
  O mistério da luz anda um pouquinho por episódio.

## Rotina de produção
1. Na manhã seguinte ao post, o Nasser manda print dos comentários (nome, função e voto).
2. Contar os votos e listar os fundadores, na ordem dos comentários.
3. Atualizar o número de seguidores e renderizar.
4. Fixar o comentário de exemplo e responder cada morador ("Bem-vindo(a) a Bifúrcia, Fulano!").
