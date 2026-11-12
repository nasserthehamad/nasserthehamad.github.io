#!/usr/bin/env python3
"""Logo do perfil (pixel art 48x48 ampliado pra 1056x1056). 3 opções: chama, mascote-chama e brasão."""
import numpy as np
from PIL import Image, ImageDraw

G = 48
SC = 22
OUT = '/home/claude/bestiario/out'
DARK = (22, 14, 40)
OUTL = (14, 8, 24)


def outline(a, col=OUTL):
    op = a[..., 3] > 0
    nb = np.zeros_like(op)
    nb[1:] |= op[:-1]; nb[:-1] |= op[1:]; nb[:, 1:] |= op[:, :-1]; nb[:, :-1] |= op[:, 1:]
    a[~op & nb] = col + (255,)
    return a


def flame(d, cx, by, s=1.0, eyes=False):
    """Chama em camadas; cx = centro, by = base."""
    def P(pts):
        return [(cx + x * s, by - y * s) for x, y in pts]
    d.polygon(P([(-11, 2), (-13, 9), (-11, 16), (-6, 22), (-7, 28), (-2, 25), (0, 33), (4, 26), (8, 29), (8, 22),
                 (12, 16), (13, 9), (11, 2), (6, 0), (-6, 0)]), fill=(206, 52, 40))
    d.polygon(P([(-8, 2), (-10, 8), (-8, 14), (-4, 19), (-3, 24), (0, 21), (2, 26), (5, 20), (9, 14), (10, 8), (8, 2),
                 (4, 1), (-4, 1)]), fill=(255, 128, 40))
    d.polygon(P([(-5, 2), (-6, 7), (-4, 12), (-1, 16), (1, 19), (3, 14), (6, 9), (6, 4), (4, 2)]), fill=(255, 210, 72))
    if not eyes:
        d.polygon(P([(-2, 2), (-3, 5), (-1, 9), (1, 11), (3, 7), (2, 3)]), fill=(255, 246, 196))
    else:
        for ex in (-4.5, 4.5):
            x0, y0 = cx + (ex - 2) * s, by - 10 * s
            d.ellipse((x0, y0, x0 + 4 * s, y0 + 5 * s), fill=(255, 255, 255))
            d.rectangle((x0 + 1.5 * s, y0 + 1.5 * s, x0 + 3 * s, y0 + 4 * s), fill=OUTL)
            d.point((x0 + 1 * s, y0 + 1 * s), fill=(255, 255, 255))
        d.line((cx - 2 * s, by - 4 * s, cx, by - 3 * s, cx + 2 * s, by - 4 * s), fill=OUTL)
        d.point((cx - 7 * s, by - 5 * s), fill=(255, 140, 150)); d.point((cx + 7 * s, by - 5 * s), fill=(255, 140, 150))


def base_circle(col_bg=DARK, ring=(255, 196, 70)):
    im = Image.new('RGBA', (G, G), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, G - 1, G - 1), fill=OUTL)
    d.ellipse((1, 1, G - 2, G - 2), fill=ring)
    d.ellipse((3, 3, G - 4, G - 4), fill=OUTL)
    d.ellipse((4, 4, G - 5, G - 5), fill=col_bg)
    # estrelas e brilho de fundo
    for x, y in ((12, 11), (35, 9), (39, 20), (9, 24), (30, 14)):
        d.point((x, y), fill=(120, 100, 170))
    return im, d


def castle(d, cx, by, col=(46, 30, 78)):
    d.rectangle((cx - 13, by - 7, cx + 13, by), fill=col)
    for x in range(cx - 13, cx + 13, 4):
        d.rectangle((x, by - 9, x + 1, by - 7), fill=col)
    d.rectangle((cx - 17, by - 12, cx - 13, by), fill=col)
    d.rectangle((cx + 13, by - 12, cx + 17, by), fill=col)
    d.rectangle((cx - 3, by - 15, cx + 3, by - 7), fill=col)
    d.polygon([(cx - 4, by - 15), (cx, by - 19), (cx + 4, by - 15)], fill=col)


def opt_a():
    im, d = base_circle()
    castle(d, 24, 41)
    d.rectangle((5, 41, 42, 43), fill=(40, 26, 70))
    fl = Image.new('RGBA', (G, G), (0, 0, 0, 0))
    flame(ImageDraw.Draw(fl), 24, 40, 0.95)
    fa = outline(np.array(fl))
    im.alpha_composite(Image.fromarray(fa))
    return im


def opt_b():
    im, d = base_circle(col_bg=(36, 20, 64))
    L = Image.new('RGBA', (G, G), (0, 0, 0, 0))
    dl = ImageDraw.Draw(L)
    gold, gold_d = (255, 200, 72), (214, 140, 40)
    x0, y0 = 15, 19                       # letra B em pixel (18x22)
    dl.rectangle((x0, y0, x0 + 4, y0 + 21), fill=gold)
    dl.rectangle((x0, y0, x0 + 12, y0 + 3), fill=gold)
    dl.rectangle((x0, y0 + 9, x0 + 13, y0 + 12), fill=gold)
    dl.rectangle((x0, y0 + 18, x0 + 14, y0 + 21), fill=gold)
    dl.rectangle((x0 + 11, y0 + 2, x0 + 15, y0 + 9), fill=gold)
    dl.rectangle((x0 + 12, y0 + 11, x0 + 17, y0 + 19), fill=gold)
    dl.rectangle((x0 + 5, y0 + 4, x0 + 10, y0 + 8), fill=(0, 0, 0, 0))
    dl.rectangle((x0 + 5, y0 + 13, x0 + 11, y0 + 17), fill=(0, 0, 0, 0))
    a = np.array(L)
    m = a[..., 3] > 0
    yy, xx = np.mgrid[0:G, 0:G]
    a[m & ((xx >= x0 + 3) & ((yy == y0 + 3) | (yy == y0 + 12) | (yy == y0 + 21)))] = gold_d + (255,)
    a[m & (xx == x0 + 4)] = gold_d + (255,)
    a = outline(a)
    im.alpha_composite(Image.fromarray(a))
    fl = Image.new('RGBA', (G, G), (0, 0, 0, 0))
    flame(ImageDraw.Draw(fl), 24, 20, 0.48)
    im.alpha_composite(Image.fromarray(outline(np.array(fl))))
    return im


def opt_c():
    im = Image.new('RGBA', (G, G), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, G - 1, G - 1), fill=DARK)
    shield = [(10, 10), (38, 10), (38, 26), (34, 34), (24, 41), (14, 34), (10, 26)]
    d.polygon(shield, fill=(255, 196, 70))
    inner = [(12, 12), (36, 12), (36, 26), (32, 33), (24, 39), (16, 33), (12, 26)]
    d.polygon(inner, fill=(150, 34, 34))
    d.polygon([(24, 12), (36, 12), (36, 26), (32, 33), (24, 39)], fill=(128, 26, 30))
    fl = Image.new('RGBA', (G, G), (0, 0, 0, 0))
    flame(ImageDraw.Draw(fl), 24, 35, 0.62)
    im.alpha_composite(Image.fromarray(np.array(fl)))
    # coroa
    d.polygon([(16, 9), (16, 3), (19, 6), (22, 1), (24, 4), (26, 1), (29, 6), (32, 3), (32, 9)], fill=(255, 214, 72))
    for x in (19, 24, 29):
        d.point((x, 7), fill=(96, 226, 214))
    a = outline(np.array(im))
    return Image.fromarray(a)


def big(im):
    return im.resize((G * SC, G * SC), Image.NEAREST)


if __name__ == '__main__':
    opts = {'a': opt_a(), 'b': opt_b(), 'c': opt_c()}
    for k, im in opts.items():
        bg = Image.new('RGBA', (G, G), DARK + (255,))
        bg.alpha_composite(im)
        big(bg).convert('RGB').save(f'{OUT}/logo-{k}.png')
    # folha de comparação: grande e no tamanho real de foto de perfil (círculo pequeno)
    sheet = Image.new('RGB', (3 * 380, 520), (240, 240, 244))
    dd = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(opts.items()):
        bg = Image.new('RGBA', (G, G), DARK + (255,)); bg.alpha_composite(im)
        L = bg.resize((336, 336), Image.NEAREST)
        m = Image.new('L', L.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 335, 335), fill=255)
        sheet.paste(L, (22 + i * 380, 20), m)
        S = bg.resize((72, 72), Image.LANCZOS)
        ms = Image.new('L', S.size, 0); ImageDraw.Draw(ms).ellipse((0, 0, 71, 71), fill=255)
        sheet.paste(S, (22 + i * 380 + 132, 380), ms)
        dd.text((22 + i * 380 + 160, 470), k.upper(), fill=(20, 20, 30))
    sheet.save('/tmp/claude-0/-home-claude/1ad023e2-0d5f-5b6d-b2b7-ef96b3fdfd1a/scratchpad/logos.png')
    print('ok')
