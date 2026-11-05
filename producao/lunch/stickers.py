#!/usr/bin/env python3
"""Five sticker-style takes on Léo (surprised), white outline, on one contact sheet."""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/video')
from make import P, F, vgrad, down

S = 2
CW, CH = 440, 540
SKIN, SKIN_D = (158, 104, 70), (128, 80, 52)
HAIR, SHIRT, PANTS = (30, 22, 20), (70, 182, 122), (54, 80, 150)
INK, WHITE, BLUSH, MOUTH, TONGUE = (24, 20, 26), (255, 255, 255), (214, 110, 110), (96, 24, 36), (236, 110, 126)

def canvas():
    im = Image.new('RGBA', (CW * S, CH * S), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def circ(d, cx, cy, r, **k): d.ellipse(P(cx - r, cy - r, cx + r, cy + r), **k)

def glints(d, cx, cy, r):
    circ(d, cx - r * 0.35, cy - r * 0.4, r * 0.32, fill=WHITE); circ(d, cx + r * 0.3, cy + r * 0.3, r * 0.14, fill=WHITE)

def curls(d, cx, cy, R, r, a0=190, a1=350, step=20, **k):
    for a in range(a0, a1 + 1, step):
        ar = math.radians(a); circ(d, cx + R * math.cos(ar), cy + R * math.sin(ar), r, **k)

def masked_fill(im, shape_fn, region_fn, color):
    m1 = Image.new('L', im.size, 0); shape_fn(ImageDraw.Draw(m1))
    m2 = Image.new('L', im.size, 0); region_fn(ImageDraw.Draw(m2))
    im.paste(color + (255,), (0, 0), ImageChops.multiply(m1, m2))

# 1 — Cabeção fofo (chibi)
def s1():
    im, d = canvas()
    for x in (186, 234): d.rounded_rectangle(P(x - 18, 420, x + 18, 482), radius=14 * S, fill=PANTS)
    for x in (182, 238): d.ellipse(P(x - 30, 466, x + 30, 498), fill=(246, 246, 248))
    d.rounded_rectangle(P(158, 330, 282, 440), radius=44 * S, fill=SHIRT)
    for sx in (-1, 1):
        x = 220 + sx * 78
        d.rounded_rectangle(P(x - 17, 312, x + 17, 384), radius=17 * S, fill=SKIN)
        circ(d, x, 312, 20, fill=SKIN)
    circ(d, 92, 222, 22, fill=SKIN); circ(d, 348, 222, 22, fill=SKIN)
    circ(d, 220, 205, 132, fill=SKIN)
    curls(d, 220, 196, 124, 46, 192, 348, 16, fill=HAIR)
    for (cx, cy, r) in [(170, 84, 50), (220, 72, 54), (270, 84, 50)]: circ(d, cx, cy, r, fill=HAIR)
    for cx in (176, 264):
        d.ellipse(P(cx - 22, 196, cx + 22, 262), fill=INK); glints(d, cx, 222, 22)
    for cx in (150, 290): d.ellipse(P(cx - 22, 268, cx + 22, 286), fill=BLUSH)
    d.ellipse(P(207, 280, 233, 312), fill=MOUTH)
    for (x0, y0, x1, y1) in [(338, 70, 362, 30), (366, 96, 404, 70), (376, 132, 418, 124)]:
        d.line(P(x0, y0, x1, y1), fill=INK, width=9 * S)
    return down(im)

# 2 — Meme exagerado (black ink outline)
def s2():
    im, d = canvas(); o = dict(outline=INK, width=6 * S)
    d.rounded_rectangle(P(140, 380, 300, 540), radius=60 * S, fill=SHIRT, **o)
    for (cx, cy) in [(78, 300), (362, 300)]:
        d.rounded_rectangle(P(cx - 34, cy - 50, cx + 34, cy + 40), radius=30 * S, fill=SKIN, **o)
        for k in range(-1, 2): d.line(P(cx + k * 15, cy - 46, cx + k * 15, cy - 20), fill=INK, width=4 * S)
    d.ellipse(P(96, 92, 344, 392), fill=SKIN, **o)
    d.ellipse(P(108, 40, 332, 176), fill=HAIR, **o)
    curls(d, 220, 160, 112, 42, 186, 354, 21, fill=HAIR, **o)
    for (cx, cy, r) in [(160, 62, 46), (220, 46, 50), (280, 62, 46)]: circ(d, cx, cy, r, fill=HAIR, **o)
    d.ellipse(P(120, 165, 214, 265), fill=WHITE, **o); d.ellipse(P(226, 160, 324, 265), fill=WHITE, **o)
    circ(d, 168, 216, 8, fill=INK); circ(d, 274, 214, 8, fill=INK)
    d.ellipse(P(160, 282, 280, 380), fill=MOUTH, **o)
    d.chord(P(176, 284, 264, 312), 180, 360, fill=WHITE)
    d.ellipse(P(190, 336, 250, 374), fill=TONGUE)
    d.ellipse(P(160, 282, 280, 380), outline=INK, width=6 * S)
    for (x, y) in [(82, 150), (360, 140)]:
        d.polygon(P(x, y - 30, x - 14, y, x + 14, y), fill=(150, 210, 255), outline=INK, width=3 * S)
        circ(d, x, y + 4, 15, fill=(150, 210, 255), outline=INK, width=3 * S)
    return down(im)

# 3 — Feijãozinho
def s3():
    im, d = canvas()
    for x in (192, 248): d.rounded_rectangle(P(x - 14, 440, x + 14, 496), radius=12 * S, fill=PANTS)
    for x in (188, 252): d.ellipse(P(x - 24, 484, x + 24, 510), fill=(246, 246, 248))
    for sx in (-1, 1):
        x = 220 + sx * 102
        d.rounded_rectangle(P(x - 16, 300, x + 16, 392), radius=16 * S, fill=SKIN)
    bean = lambda dd: dd.rounded_rectangle(P(130, 100, 310, 456), radius=90 * S, fill=255)
    d.rounded_rectangle(P(130, 100, 310, 456), radius=90 * S, fill=SKIN)
    masked_fill(im, bean, lambda dd: dd.rectangle(P(0, 300, CW, CH), fill=255), SHIRT)
    d = ImageDraw.Draw(im)
    for (cx, cy, r) in [(184, 104, 30), (220, 88, 34), (256, 104, 30), (204, 92, 26), (238, 92, 26)]: circ(d, cx, cy, r, fill=HAIR)
    for cx in (192, 248): circ(d, cx, 196, 13, fill=INK); circ(d, cx - 4, 191, 4, fill=WHITE)
    d.arc(P(174, 152, 210, 172), 200, 340, fill=INK, width=6 * S); d.arc(P(230, 152, 266, 172), 200, 340, fill=INK, width=6 * S)
    for cx in (170, 270): d.ellipse(P(cx - 16, 222, cx + 16, 236), fill=BLUSH)
    d.ellipse(P(206, 230, 234, 266), fill=MOUTH)
    return down(im)

# 4 — Só a cara (busto)
def s4():
    im, d = canvas()
    d.rounded_rectangle(P(70, 400, 370, 600), radius=90 * S, fill=SHIRT)
    d.rectangle(P(190, 360, 250, 420), fill=SKIN_D)
    head = lambda dd: dd.ellipse(P(104, 96, 336, 384), fill=255)
    d.ellipse(P(104, 96, 336, 384), fill=SKIN)
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).ellipse(P(276, 100, 440, 400), fill=255)
    hm = Image.new('L', im.size, 0); ImageDraw.Draw(hm).ellipse(P(104, 96, 336, 384), fill=255)
    im.paste((144, 93, 62, 255), (0, 0), ImageChops.multiply(sh, hm)); d = ImageDraw.Draw(im)
    curls(d, 220, 176, 118, 40, 190, 350, 16, fill=HAIR)
    for (cx, cy, r) in [(164, 82, 46), (220, 68, 50), (276, 82, 46)]: circ(d, cx, cy, r, fill=HAIR)
    for cx in (176, 266):
        d.ellipse(P(cx - 32, 196, cx + 32, 250), fill=WHITE)
        circ(d, cx, 224, 20, fill=(96, 58, 34)); circ(d, cx, 224, 10, fill=INK); circ(d, cx - 7, 216, 5, fill=WHITE)
        d.arc(P(cx - 34, 194, cx + 34, 252), 200, 340, fill=INK, width=6 * S)
    d.line(P(140, 172, 204, 160), fill=HAIR, width=10 * S); d.line(P(236, 160, 300, 172), fill=HAIR, width=10 * S)
    d.arc(P(204, 250, 236, 290), 280, 80, fill=SKIN_D, width=6 * S)
    d.ellipse(P(176, 300, 264, 366), fill=MOUTH)
    d.chord(P(190, 300, 250, 322), 180, 360, fill=WHITE)
    d.ellipse(P(198, 336, 242, 362), fill=TONGUE)
    for (cx, ang) in [(110, 12), (330, -12)]:
        hand = Image.new('RGBA', (140 * S, 170 * S), (0, 0, 0, 0)); hd = ImageDraw.Draw(hand)
        hd.rounded_rectangle(P(20, 20, 120, 150), radius=44 * S, fill=SKIN)
        for k in (45, 70, 95): hd.line(P(k, 26, k, 70), fill=SKIN_D, width=4 * S)
        hand = hand.rotate(ang, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(hand, tuple(P(cx - hand.width / S / 2, 250)))
    return down(im)

# 5 — Traço de caneta (ink line + offset flat colour)
def wobble(pts, amp=1.6, seed=0):
    rng = random.Random(seed)
    return [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp)) for x, y in pts]

def ell(cx, cy, rx, ry, n=48, a0=0, a1=360):
    return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]

def s5():
    im, d = canvas()
    off = (7, 6)
    shapes = [
        (ell(220, 156, 78, 84), SKIN),
        ([(150, 260), (290, 260), (318, 420), (122, 420)], SHIRT),
        ([(150, 420), (212, 420), (206, 500), (160, 500)], PANTS),
        ([(228, 420), (290, 420), (282, 500), (234, 500)], PANTS),
        ([(150, 268), (110, 330), (124, 360), (160, 312)], SHIRT),
        ([(290, 268), (330, 200), (354, 214), (300, 312)], SHIRT),
    ]
    for pts, col in shapes:
        d.polygon([tuple(P(x + off[0], y + off[1])) for x, y in pts], fill=col)
    hair = []
    for a in range(180, 361, 18):
        hair += ell(220 + 84 * math.cos(math.radians(a)), 150 + 84 * math.sin(math.radians(a)), 26, 26, 12, a - 90, a + 90)
    d.polygon([tuple(P(x + off[0], y + off[1])) for x, y in hair + ell(220, 118, 80, 16, 14, 0, 180)], fill=HAIR)
    for (cx, cy) in [(116, 372), (348, 200)]: circ(d, cx + off[0], cy + off[1], 20, fill=SKIN)
    for (cx, cy) in [(180, 508), (262, 508)]: d.ellipse(P(cx - 32 + off[0], cy - 14 + off[1], cx + 32 + off[0], cy + 14 + off[1]), fill=(246, 246, 248))
    lw = 5 * S
    def poly(pts, closed=True, seed=0):
        q = wobble(pts + (pts[:1] if closed else []), seed=seed)
        d.line([tuple(P(x, y)) for x, y in q], fill=INK, width=lw, joint='curve')
    for i, (pts, _) in enumerate(shapes): poly(pts, seed=i)
    for a in range(180, 361, 18):
        poly(ell(220 + 84 * math.cos(math.radians(a)), 150 + 84 * math.sin(math.radians(a)), 26, 26, 12, a - 70, a + 70), closed=False, seed=a)
    for i, (cx, cy) in enumerate([(116, 372), (348, 200)]): poly(ell(cx, cy, 20, 20, 16), seed=40 + i)
    for i, (cx, cy) in enumerate([(180, 508), (262, 508)]): poly(ell(cx, cy, 32, 14, 20), seed=50 + i)
    poly(ell(220, 118, 80, 16, 14, 0, 180), closed=False, seed=63)
    for cx in (192, 248): circ(d, cx, 172, 9, fill=INK)
    poly(ell(192, 154, 16, 7, 10, 200, 340), closed=False, seed=60); poly(ell(248, 150, 16, 7, 10, 200, 340), closed=False, seed=61)
    poly(ell(220, 210, 12, 16, 20), seed=62)
    for (x0, y0, x1, y1) in [(306, 92, 326, 62), (322, 116, 352, 100)]: poly([(x0, y0), (x1, y1)], closed=False, seed=x0)
    return down(im)

def sticker(sp, grow=11):
    pad = 40
    big = Image.new('RGBA', (sp.width + 2 * pad, sp.height + 2 * pad), (0, 0, 0, 0)); big.alpha_composite(sp, (pad, pad))
    a = big.getchannel('A').point(lambda v: 255 if v > 40 else 0)
    for _ in range(grow): a = a.filter(ImageFilter.MaxFilter(3))
    a = a.filter(ImageFilter.GaussianBlur(1.0))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    sh = a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.35))
    shl = Image.new('RGBA', big.size, (10, 30, 34, 0)); shl.putalpha(sh)
    out.paste(shl, (0, 10), shl)
    ol = Image.new('RGBA', big.size, (255, 255, 255, 0)); ol.putalpha(a)
    out.alpha_composite(ol); out.alpha_composite(big)
    return out

if __name__ == '__main__':
    names = ['Cabeção fofo', 'Meme exagerado', 'Feijãozinho', 'Só a cara', 'Traço de caneta']
    sts = [sticker(f()) for f in (s1, s2, s3, s4, s5)]
    SW, SH = 1500, 1260
    sheet = vgrad(SW, SH, (44, 156, 156), (20, 104, 110)).convert('RGBA')
    d = ImageDraw.Draw(sheet)
    d.text((SW // 2, 70), 'Qual estilo de figurinha?', font=F('InterDisplay-ExtraBold', 58), fill=WHITE, anchor='mm',
           stroke_width=5, stroke_fill=INK)
    cells = [(260, 420), (750, 420), (1240, 420), (505, 940), (995, 940)]
    for i, ((cx, cy), st, nm) in enumerate(zip(cells, sts, names)):
        sc = 400 / st.height
        s2_ = st.resize((int(st.width * sc), int(st.height * sc)), Image.LANCZOS)
        sheet.alpha_composite(s2_, (int(cx - s2_.width / 2), int(cy - s2_.height / 2 - 10)))
        lab = f'{i + 1}  {nm}'
        f = F('InterDisplay-ExtraBold', 40)
        tw = f.getlength(lab)
        x0 = cx - tw / 2 - 26
        d.rounded_rectangle((x0, cy + 200, x0 + tw + 52, cy + 262), radius=31, fill=(22, 24, 34))
        d.text((cx, cy + 232), lab, font=f, fill=WHITE, anchor='mm')
        d.text((x0 + 26 + f.getlength(f'{i + 1}') / 2, cy + 232), f'{i + 1}', font=f, fill=(255, 204, 77), anchor='mm')
    sheet.convert('RGB').save('/home/claude/lunch/estilos-figurinha.png')
    print('ok')
