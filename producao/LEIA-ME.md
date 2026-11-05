# Produção do @vcescolheaoub

Arquivos para refazer ou continuar os vídeos num ambiente novo.

## Restaurar

```bash
git clone --depth 1 https://github.com/nasserthehamad/nasserthehamad.github.io /home/claude/nasserthehamad.github.io
mkdir -p /home/claude/video /home/claude/lunch
cp -r /home/claude/nasserthehamad.github.io/producao/video/* /home/claude/video/
cp -r /home/claude/nasserthehamad.github.io/producao/lunch/* /home/claude/lunch/
# precisa de: python3 com pillow e numpy, ffmpeg, fontes Inter (já no ambiente padrão)
```

`lunch.py` importa `make.py` de `/home/claude/video`, então mantenha essas pastas.

## Pastas

- `video/make.py` — "Quem Bate à Porta" ep. 1 e funções base (legendas, chuva, composição, encode).
- `video/porta_narr.py` — versão narrada da Porta: `python3 porta_narr.py narracao.mp3`.
- `lunch/lunch.py` — "A Marmita Sumiu" ep. 1 (personagens, cenas). `python3 lunch.py preview|render`.
- `lunch/laudio.py` — trilha animada + efeitos + narração (lê `timing.json`).
- `lunch/nar.py` — divide a narração por cena e gera `timing.json`: `python3 nar.py narracao.mp3`.
- `lunch/stickers.py` — folha com 5 estilos de figurinha (referência).
- `marmita-biblia.md` — arco dos 5 episódios da Marmita, elenco e regras.

## Fluxo de um episódio

1. Roteiro (6 cenas) a partir da bíblia + opção vencedora.
2. Narração no ElevenLabs (voz Luiz Henrique) → baixar mp3 (domínio `elevenlabsusercontent.com` liberado).
3. `nar.py` → `timing.json`; `lunch.py render`; `laudio.py`; juntar com ffmpeg.
4. Copiar para `videos/` deste repositório, commit e push → link `https://nasserthehamad.github.io/videos/<arquivo>.mp4`.
5. Agendar no Metricool (marca 7899577, TikTok, `isAigc: true`) após confirmação do dono da conta.
