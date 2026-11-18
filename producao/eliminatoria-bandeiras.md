# "Qual país sobrevive?": eliminatória das bandeiras (18/11)

Ideia do Nasser ("aquelas competições entre bandeiras, eliminatórias"). É um formato viral: cada um torce pelo próprio
país, e os comentários lotam.

## Como funciona
- **A arena:** 32 países em bolinhas (bandeira em pixel art 22x22 recortada em círculo, com brilho), quicando com
  velocidade constante (185 px/s) num cercado redondo do Brasa. A porteira é larga (52°), gira a 1,2 rad/s e tem mourões
  vermelhos. Quem sai pela porteira é eliminado: rola pra fora e some.
- **Os países:** a física não sabe de país nenhum. Os países são distribuídos **depois** da simulação: a bolinha que
  sobra vira o Brasil, a vice vira a Argentina, França e Portugal ficam com 3º e 4º, e o resto é sorteado. Assim dá pra
  escolher a final sem mexer na física. Pedido do Nasser: final Brasil x Argentina.
- **Sorteio 119:**
  - eliminações rápidas no começo (a 8ª aos 3 s, a 16ª aos 7 s);
  - semifinal termina aos 17,9 s;
  - **final Brasil x Argentina com 3,8 s de duelo**, e a Argentina cai aos 21,7 s.
- **Na tela:**
  - "QUAL PAÍS SOBREVIVE?" e "RESTAM N";
  - a cada eliminado, "TCHAU, <PAÍS>" em vermelho;
  - na final, "FINAL" piscando e "BRASIL x ARGENTINA", com a borda pulsando no ritmo do coração;
  - no fim, "CAMPEÃO! BRASIL": a bolinha do Brasil cresce no centro, cai confete verde e amarelo e os 4 moradores pulam.
- **Loop:** as 32 bolinhas voltam pro lugar inicial.
- **Som:**
  - "Na Gruta do Rei da Montanha" (Grieg, domínio público) **acelerando no tempo** (de 0,2 s a 0,088 s por colcheia)
    até a final, com baixo em Si/Fá#;
  - "plop" a cada eliminado e "ooh" da torcida nas 4 últimas;
  - coração na final;
  - no fim, torcida e fanfarra em Si maior.
- **Bandeiras** (`flags.py`): Brasil, Argentina, França, Alemanha, Espanha, Portugal, Itália, Inglaterra, Holanda,
  Bélgica, Croácia, Uruguai, Colômbia, Chile, Paraguai, Peru, México, EUA, Canadá, Japão, Coreia do Sul, China, Índia,
  Rússia, Ucrânia, Polônia, Suécia, Suíça, Turquia, Marrocos, Nigéria e Senegal.
  - Bandeira de país é livre.
  - **Escudo de time de futebol, não**: é marca registrada.
- **Arquivos:** `brasa-bandeiras.mp4` (25,3 s) e `capa-bandeiras.jpg` ("QUAL PAÍS SOBREVIVE? / BRASIL x ARGENTINA", no
  duelo).
- **Rodar:** `python3 bandeiras.py` (`SEED=119`). `PLAN=1` imprime a ordem de saída, e também tem `STILLS=` e `CAPA=1`.
  Pra outro sorteio com bom ritmo: `python3 search2.py 185 52`. Pra mudar quem chega na final, editar o bloco "quem é quem".

## Ideias pra continuar
- Revanche ("a Argentina pediu revanche").
- Copa dos Estados (27 bandeiras dos estados).
- Pedir nos comentários qual país entra na próxima.
