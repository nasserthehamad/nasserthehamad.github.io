#!/usr/bin/env python3
"""Gera as carteirinhas dos fundadores + capa do carrossel."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import carteira as C
import folk as FK

out = os.path.join(HERE, 'fundadores')
os.makedirs(out, exist_ok=True)
paths = []
for i, (n, r) in enumerate(FK.FOUNDERS):
    paths.append(C.card(n, r, i + 1, True, os.path.join(out, f'{i + 2:02d}-carteira-{i + 1:03d}-{FK.norm(n).replace(" ", "-")}.png')))
# capa
CW, CH = 1080, 1350
im = Image.new('RGB', (CW, CH), (24, 18, 40))
d = ImageDraw.Draw(im)
f = C.f
d.rectangle((0, 0, CW, 330), fill=(178, 46, 42))
d.text((CW / 2, 110), 'REINO DE BRASA', font=f(120), fill=(255, 220, 120), anchor='mm')
d.text((CW / 2, 230), 'AS CARTEIRINHAS DOS FUNDADORES', font=f(66), fill=(255, 240, 220), anchor='mm')
row = [FK.make_folk(n, r, 0) for n, r in FK.FOUNDERS]
sc = 7
y_base = 760
for k, s in enumerate(row):
    ys, xs = np.nonzero(s[..., 3] > 0)
    s = s[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgba = np.zeros(s.shape, np.uint8)
    rgba[..., :3] = s[..., :3]; rgba[..., 3] = (s[..., 3] > 0) * 255
    p = Image.fromarray(rgba, 'RGBA').resize((s.shape[1] * sc, s.shape[0] * sc), Image.NEAREST)
    row_ = 0 if k < 6 else 1
    col_ = k if k < 6 else k - 6
    n_in = 6 if row_ == 0 else 5
    xx = int(CW / 2 + (col_ - (n_in - 1) / 2) * 168 - p.width / 2)
    yb = y_base + row_ * 250
    im.paste(p, (xx, yb - p.height), p)
d.text((CW / 2, 1120), 'Achou a sua? Arrasta pro lado!', font=f(70), fill=(255, 255, 255), anchor='mm')
d.text((CW / 2, 1200), 'Comenta seu nome e sua função pra ganhar a próxima.', font=f(50), fill=(200, 190, 220), anchor='mm')
d.text((CW / 2, 1300), '@vcescolheaoub', font=f(48), fill=(200, 190, 220), anchor='mm')
capa = os.path.join(out, '01-capa.png')
im.save(capa)
print(capa)
for p in paths:
    print(p)
