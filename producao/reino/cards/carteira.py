#!/usr/bin/env python3
"""Carteirinha de morador de Brasa: python3 cards/carteira.py "Nome" "Função" numero [fundador]"""
import sys, os, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import world2 as W
import folk as FK

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(os.path.dirname(HERE), 'fonts', 'JerseyFix.ttf')


def f(sz):
    return ImageFont.truetype(FONT, sz)


def card(name, role, num, founder=True, out=None):
    spr = FK.make_folk(name, role, 0)
    if 'adestr' in FK.norm(role):
        dog = FK.make_dog(0)
        big = np.zeros((spr.shape[0], spr.shape[1] + 10, 4), np.float32)
        big[:, :spr.shape[1]] = spr
        dh, dw = dog.shape[:2]
        rows = np.nonzero(spr[..., 3].any(axis=1))[0]
        yb = rows.max() + 1
        sub = big[yb - dh:yb, spr.shape[1] - 6:spr.shape[1] - 6 + dw]
        m = dog[..., 3] > 0
        sub[m] = dog[m]
        spr = big
    ys, xs = np.nonzero(spr[..., 3] > 0)
    spr = spr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = spr.shape[:2]
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = spr[..., :3].astype(np.uint8)
    rgba[..., 3] = (spr[..., 3] > 0) * 255
    sc = min(12, 300 // w, 420 // h)
    por = Image.fromarray(rgba, 'RGBA').resize((w * sc, h * sc), Image.NEAREST)
    CW, CH = 1080, 1350
    im = Image.new('RGB', (CW, CH), (24, 18, 40))
    d = ImageDraw.Draw(im)
    # cartão de pergaminho com borda em degraus
    x0, y0, x1, y1, b = 70, 120, 1010, 1230, 12
    d.rectangle((x0 + b, y0, x1 - b, y1), fill=(92, 58, 34))
    d.rectangle((x0, y0 + b, x1, y1 - b), fill=(92, 58, 34))
    d.rectangle((x0 + b, y0 + b, x1 - b, y1 - b), fill=(240, 222, 182))
    d.rectangle((x0 + 2 * b, y0 + 2 * b, x1 - 2 * b, y1 - 2 * b), outline=(196, 160, 110), width=4)
    # faixa do topo
    d.rectangle((x0 + b, y0 + b, x1 - b, y0 + 150), fill=(178, 46, 42))
    d.text((CW / 2, y0 + 50), 'REINO DE BRASA', font=f(84), fill=(255, 220, 120), anchor='mm')
    d.text((CW / 2, y0 + 116), 'CARTEIRA DE MORADOR', font=f(52), fill=(255, 240, 220), anchor='mm')
    # retrato
    px, py = 130, 330
    d.rectangle((px - 10, py - 10, px + 330, py + 470), fill=(92, 58, 34))
    d.rectangle((px, py, px + 320, py + 460), fill=(126, 182, 222))
    d.rectangle((px, py + 340, px + 320, py + 460), fill=(116, 176, 84))
    im.paste(por, (px + 160 - por.width // 2, py + 445 - por.height), por)
    # dados
    tx = 510
    d.text((tx, 350), 'NOME', font=f(44), fill=(140, 100, 64))
    nm = name.upper()
    sz = 120
    while f(sz).getlength(nm) > 440 and sz > 50:
        sz -= 6
    d.text((tx, 395), nm, font=f(sz), fill=(40, 26, 20))
    d.text((tx, 545), 'FUNÇÃO', font=f(44), fill=(140, 100, 64))
    rl = role.upper()
    sz = 86
    words = rl.split()
    lines = [rl]
    if f(60).getlength(rl) > 440 and len(words) > 1:
        lines = [' '.join(words[:len(words) // 2 + 1]), ' '.join(words[len(words) // 2 + 1:])]
    sz = 86 if len(lines) == 1 else 50
    while max(f(sz).getlength(l) for l in lines) > 440 and sz > 36:
        sz -= 4
    for k, l in enumerate(lines):
        d.text((tx, 590 + k * (sz + 4)), l, font=f(sz), fill=(178, 46, 42))
    d.text((tx, 715), 'MORADOR NÚMERO', font=f(44), fill=(140, 100, 64))
    d.text((tx, 760), f'{num:03d}', font=f(96), fill=(40, 26, 20))
    if founder:
        d.rectangle((130, 860, 950, 960), fill=(255, 208, 72))
        d.rectangle((140, 870, 940, 950), outline=(178, 120, 30), width=4)
        g = FK.gender(role)
        lab = {'f': 'FUNDADORA DO REINO', 'm': 'FUNDADOR DO REINO'}.get(g, 'FUNDADOR(A) DO REINO')
        d.text((CW / 2, 910), lab, font=f(64), fill=(92, 50, 20), anchor='mm')
        for cx in (210, 870):   # chamas em pixel
            for (ddx, ddy, c) in [(0, -24, 1), (-6, -12, 1), (0, -12, 1), (6, -12, 1), (-12, 0, 1), (-6, 0, 2), (0, 0, 2),
                                  (6, 0, 2), (12, 0, 1), (-6, 12, 1), (0, 12, 2), (6, 12, 1)]:
                col = (220, 70, 40) if c == 1 else (255, 150, 40)
                d.rectangle((cx + ddx - 3, 910 + ddy - 6, cx + ddx + 3, 910 + ddy + 6), fill=col)
    d.text((CW / 2, 1040), 'Chegou na primeira noite, em volta da fogueira.', font=f(50), fill=(110, 80, 56), anchor='mm')
    d.text((CW / 2, 1130), 'BRASA · EP. 1 · 09/11/2026', font=f(46), fill=(140, 100, 64), anchor='mm')
    d.text((CW / 2, 1290), '@vcescolheaoub', font=f(48), fill=(200, 190, 220), anchor='mm')
    out = out or os.path.join(HERE, f'carteira-{num:03d}.png')
    im.save(out)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    print(card(a[0], a[1], int(a[2]), founder=(len(a) < 4 or a[3] != '0')))
