#!/usr/bin/env python3
"""Quem Bate à Porta — Episódio 3 (venceu B: pular o muro). Usage: ep3.py preview|render narr.mp3 [scenes]"""
import os, sys, math, random, subprocess, wave, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/porta2')
import make as M
import ep2 as E
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, tracked, rich_line, WHITE, WARM, RED, INK

W, H, FPS, S = 1080, 1920, 30, 2
OUT = '/home/claude/porta3'
E.OUT = OUT
SR, LEAD = 44100, 0.35
E.LEAD = LEAD
NIGHT_TOP, NIGHT_BOT, SIL = E.NIGHT_TOP, E.NIGHT_BOT, E.SIL
COLD = 1.7

SENTS = {
    'e1': [('Vocês escolheram…', WHITE), ('pular o muro.', RED)],
    'e2': [('A Lia escalou o muro na chuva…', WHITE), ('e caiu no quintal do vizinho.', WHITE)],
    'e3': [('Uma porta se abriu.', WHITE), ('Era o Seu Antônio…', WARM), ('vigia noturno aposentado.', WHITE)],
    'e4': [('“Menina?', WARM), ('Entra…', WARM), ('tá chovendo.”', WARM)],
    'e5': [('O celular vibrou.', WHITE), ('“Não entra.”', WARM), ('E logo depois:', WHITE), ('“Sou eu, Lia. A Bia.”', WARM),
           ('A irmã que sumiu há um ano.', RED)],
}
ORDER = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6']
MINS = {'e1': 3.2, 'e2': 4.6, 'e3': 4.8, 'e4': 3.2, 'e5': 7.0, 'e6': 7.2}
TAIL = {'e1': 0.7, 'e2': 0.8, 'e3': 0.8, 'e4': 0.9, 'e5': 1.2, 'e6': 1.4}
E.SENTS, E.ORDER = SENTS, ORDER

def r30(v): return round(v * 30) / 30
def sc(img, s): return img if abs(s - 1) < 1e-3 else img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
def stt(k, i): return LEAD + T[k]['st'][i]

def rimmed(sp, col, k=0.6, r=5):
    a = sp.getchannel('A'); rim = a.filter(ImageFilter.MaxFilter(r)).filter(ImageFilter.GaussianBlur(3))
    out = Image.new('RGBA', sp.size, col + (0,)); out.putalpha(rim.point(lambda v: int(v * k))); out.alpha_composite(sp); return out

# ------------------------------------------------------------ characters
def build_antonio(arm_deg=20, torch=False, rim=(255, 186, 110)):
    """Stocky silhouette with a watchman cap. arm_deg: right arm angle from straight down (positive = forward/right)."""
    im = Image.new('RGBA', (340 * S, 760 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = SIL + (255,)
    d.rounded_rectangle(P(96, 460, 146, 748), radius=22 * S, fill=c); d.rounded_rectangle(P(160, 460, 210, 748), radius=22 * S, fill=c)
    d.rounded_rectangle(P(70, 196, 236, 476), radius=64 * S, fill=c)
    d.ellipse(P(78, 290, 246, 478), fill=c)
    d.rounded_rectangle(P(48, 214, 88, 452), radius=20 * S, fill=c)
    d.rectangle(P(132, 166, 174, 206), fill=c)
    d.ellipse(P(100, 74, 206, 184), fill=c)
    d.polygon(P(86, 42, 220, 42, 210, 84, 96, 84), fill=c)                     # cap crown
    d.polygon(P(150, 80, 240, 86, 232, 100, 150, 96), fill=c)                  # visor
    sx, sy, L_, wd = 220, 228, 232, 21
    a = math.radians(arm_deg); ex, ey = sx + L_ * math.sin(a), sy + L_ * math.cos(a)
    nx, ny = math.cos(a) * wd, -math.sin(a) * wd
    d.polygon(P(sx - nx, sy - ny, sx + nx, sy + ny, ex + nx, ey + ny, ex - nx, ey - ny), fill=c)
    d.ellipse(P(sx - wd, sy - wd, sx + wd, sy + wd), fill=c); d.ellipse(P(ex - 24, ey - 24, ex + 24, ey + 24), fill=c)
    if torch:
        tx, ty = ex + 30 * math.sin(a), ey + 30 * math.cos(a)
        d.line(P(ex, ey, tx, ty), fill=c, width=26 * S)
    sp = down(im)
    return rimmed(sp, rim, 0.75, 7), (ex, ey)

def lia_sil():
    return E.build_lia()

# ------------------------------------------------------------ e0 cold open (previous cliffhanger)
def setup_e0():
    global E0_BG, E0_RAIN, H1, H2, H0
    E0_BG = vgrad(W, H, (10, 14, 30), (2, 3, 8)).convert('RGBA'); E0_RAIN = M.Rain(31, M.RAIN_OUT)
    def big(txt, size):
        while F('InterDisplay-Black', size).getlength(txt) > 960: size -= 4
        f = F('InterDisplay-Black', size); asc, desc = f.getmetrics(); w = int(f.getlength(txt)) + 40
        im = Image.new('RGBA', (w, asc + desc + 40), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 20), txt, font=f, fill=WHITE, stroke_width=11, stroke_fill=INK); return im
    H1, H2 = big('NÃO VAI', 190), big('PRO GALPÃO.', 190)
    H0 = rich_line([('NÚMERO DESCONHECIDO', WARM)], F('InterDisplay-ExtraBold', 44), stroke=5)

def frame_e0(t):
    im = E0_BG.copy(); im.alpha_composite(E0_RAIN.layer(t))
    s = 1 + 0.25 * (1 - eo(t / 0.25))
    for img, y in ((H1, 700), (H2, 920)):
        i2 = sc(img, s); comp(im, i2, ((W - i2.width) / 2, y - (i2.height - img.height) / 2))
    comp(im, H0, ((W - H0.width) / 2, 610))
    dx = int(round(9 * math.sin(2 * math.pi * 30 * t))) if (0.05 <= t < 0.4 or 0.6 <= t < 0.95) else 0
    if dx: im = Image.fromarray(np.roll(np.asarray(im), dx, axis=1))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    return im.convert('RGB')

# ------------------------------------------------------------ e1 recap
def setup_e1():
    global E1_BG, E1_RAIN, CA1, CB1
    E1_BG = M.build_s6(); E1_RAIN = M.Rain(21, M.RAIN_OUT)
    CA1 = M.card('A', 'Entrar no galpão', WARM, (30, 20, 8), WARM, (30, 20, 8))
    CB1 = M.card('B', 'Pular o muro', RED, (64, 10, 14), (255, 228, 228), WHITE)

def frame_e1(t):
    im = E1_BG.convert('RGBA'); im.alpha_composite(E1_RAIN.layer(t)); im = M.apply_mult(im, MULT)
    sel = stt('e1', 1) - 0.1
    for img, y, t0, side, isB in ((CA1, 640, 0.05, -1, False), (CB1, 870, 0.15, 1, True)):
        if t < t0: continue
        p = eo((t - t0) / 0.35); a = p; s = 1.0
        if t > sel:
            q = eo((t - sel) / 0.3)
            if isB: s = 1 + 0.08 * q
            else: a = p * (1 - 0.7 * q)
        i2 = sc(img, s); x = (W - img.width) / 2 + side * (1 - p) * 160
        comp(im, i2, (x + img.width / 2 - i2.width / 2, y + img.height / 2 - i2.height / 2), a)
    if t > sel:
        q = eo((t - sel) / 0.25); ck = sc(CHECK, 0.5 + 0.5 * q); comp(im, ck, (975 - ck.width / 2, 878 - ck.height / 2), q)
    comp(im, KICK, ((W - KICK.width) // 2, 210)); CAP['e1'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ e2 over the wall
WTOP, WBOT = 760, 1300
def build_e2():
    w, h = W * S, H * S
    img = vgrad(w, h, NIGHT_TOP, NIGHT_BOT, 0, 900 * S)
    d = ImageDraw.Draw(img)
    d.polygon(P(-40, 560, 260, 380, 560, 560), fill=(12, 15, 28)); d.rectangle(P(0, 560, 520, 800), fill=(14, 17, 30))  # Lia's house
    img = glow(img, lambda dd: dd.rectangle(P(330, 600, 410, 680), fill=255), (255, 196, 110), 18 * S)
    d = ImageDraw.Draw(img)
    d.rectangle(P(330, 600, 410, 680), fill=(255, 206, 130)); d.line(P(370, 600, 370, 680), fill=(14, 17, 30), width=5 * S)
    d.rectangle(P(0, WTOP, W, WBOT), fill=(32, 34, 46))
    for y in range(WTOP + 40, WBOT, 56):
        d.line(P(0, y, W, y), fill=(26, 28, 38), width=3 * S)
        off = 0 if (y // 56) % 2 else 60
        for x in range(off, W, 120): d.line(P(x, y, x, y + 56), fill=(26, 28, 38), width=3 * S)
    d.rectangle(P(0, WTOP - 18, W, WTOP + 8), fill=(46, 48, 62))
    img.paste(vgrad(w, (H - WBOT) * S, (16, 24, 20), (4, 6, 6)), (0, WBOT * S)); d = ImageDraw.Draw(img)
    for (a, b, c, e) in [(120, 1450, 380, 1490), (640, 1560, 940, 1610), (300, 1720, 560, 1770)]:
        d.ellipse(P(a, b, c, e), fill=(40, 48, 76))
    d.rounded_rectangle(P(860, 1180, 980, 1310), radius=10 * S, fill=(18, 20, 26))                  # bucket
    d.polygon(P(70, 1310, 110, 1140, 150, 1310), fill=(12, 20, 14)); d.polygon(P(110, 1310, 170, 1100, 220, 1310), fill=(14, 24, 16))
    return down(img).convert('RGBA')

def setup_e2():
    global E2_BG, E2_RAIN, LIA2, RIP
    E2_BG = build_e2(); E2_RAIN = M.Rain(22, M.RAIN_OUT); LIA2 = sc(lia_sil(), 0.82)
    rng = random.Random(4); RIP = [(rng.uniform(120, 960), rng.uniform(1360, 1860), rng.uniform(0, 1)) for _ in range(20)]

def frame_e2(t):
    im = E2_BG.copy()
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, ph in RIP:
        q = (t * 0.9 + ph) % 1.0; r = 6 + 30 * q
        d.ellipse((x - r, y - r * 0.3, x + r, y + r * 0.3), outline=(130, 150, 200, int(110 * (1 - q))), width=2)
    td = stt('e2', 1) - 0.1                       # drop moment
    cx = 600; lw, lh = LIA2.width, LIA2.height
    if t < td:                                     # climbing: behind the wall, rising
        p = eio(clamp((t - LEAD) / max(0.3, td - LEAD - 0.2)))
        top = lerp(WTOP + 20, WTOP - lh * 0.55, p)
        sil = LIA2.crop((0, 0, lw, max(1, int(WTOP - 18 - top))))
        if sil.height > 1: comp(im, sil, (cx - lw / 2, top))
        im.alpha_composite(lay); im.alpha_composite(E2_RAIN.layer(t))
    else:
        q = clamp((t - td) / 0.38)
        feet = lerp(WTOP + lh * 0.45, 1560, q * q)
        squash = 1.0
        if q >= 1:
            k = t - td - 0.38
            squash = 1 - 0.18 * math.exp(-k / 0.12) * (1 if k < 0.5 else 0)
        sp = LIA2.resize((lw, max(1, int(lh * squash))), Image.BILINEAR)
        if q >= 1 and t - td < 1.2:
            k = (t - td - 0.38) / 0.8
            for rr in (0, 0.25):
                kk = clamp(k - rr); r = 40 + 220 * kk
                d.ellipse((cx - r, 1560 - r * 0.22, cx + r, 1560 + r * 0.22), outline=(150, 170, 220, int(200 * (1 - kk))), width=4)
        im.alpha_composite(lay)
        comp(im, sp, (cx - lw / 2, feet - sp.height))
        im.alpha_composite(E2_RAIN.layer(t))
    sx = sy = 0
    if td + 0.38 <= t < td + 0.68:
        k = 1 - (t - td - 0.38) / 0.3; sx = 14 * k * math.sin(2 * math.pi * 29 * t); sy = 10 * k * math.cos(2 * math.pi * 23 * t)
    if sx or sy: im = Image.fromarray(np.roll(np.roll(np.asarray(im), int(sx), axis=1), int(sy), axis=0))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210)); CAP['e2'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ e3 / e4 the neighbour's door
DX0, DX1, DY0, DY1 = 380, 700, 600, 1380
def build_interior(w, h, keys=True, big=False):
    img = vgrad(w, h, (255, 206, 132), (196, 120, 58))
    d = ImageDraw.Draw(img)
    if keys:
        u = 2.2 if big else 1.0
        y0 = int(150 * u); d.rectangle((int(30 * u), y0, w - int(30 * u), y0 + int(16 * u)), fill=(110, 70, 36))
        rng = random.Random(7); n = 9 if big else 7
        for i in range(n):
            x = int(46 * u + i * (w - 92 * u) / (n - 1))
            d.line((x, y0 + 16 * u, x, y0 + 30 * u), fill=(90, 60, 30), width=max(2, int(3 * u)))
            for k in range(rng.randint(1, 3)):
                kx = x + (k - 1) * 9 * u; ky = y0 + 30 * u
                d.ellipse((kx - 7 * u, ky, kx + 7 * u, ky + 14 * u), outline=(250, 236, 180), width=max(2, int(3 * u)))
                d.line((kx, ky + 14 * u, kx, ky + 40 * u), fill=(250, 236, 180), width=max(2, int(4 * u)))
                d.line((kx, ky + 32 * u, kx + 7 * u, ky + 32 * u), fill=(250, 236, 180), width=max(2, int(3 * u)))
            tag = rng.randint(1, 60)
            d.rectangle((x - 13 * u, y0 + 74 * u, x + 13 * u, y0 + 94 * u), fill=(255, 250, 236))
            d.text((x, y0 + 84 * u), str(tag), font=F('Inter-SemiBold', int(14 * u)), fill=(90, 60, 30), anchor='mm')
    return img

def build_e3():
    w, h = W * S, H * S
    img = vgrad(w, h, (24, 26, 38), (14, 15, 22))
    d = ImageDraw.Draw(img)
    for y in range(0, 1400, 46): d.line(P(0, y, W, y), fill=(19, 20, 30), width=3 * S)
    d.rectangle(P(DX0 - 26, DY0 - 26, DX1 + 26, DY1), fill=(40, 38, 46))
    d.rectangle(P(790, 760, 980, 920), fill=(10, 12, 18)); d.rectangle(P(780, 750, 990, 930), outline=(40, 38, 46), width=10 * S)
    img.paste(vgrad(w, (H - 1400) * S, (22, 22, 28), (6, 6, 8)), (0, 1400 * S)); d = ImageDraw.Draw(img)
    d.rectangle(P(DX0 - 60, 1380, DX1 + 60, 1420), fill=(34, 32, 38))
    return down(img).convert('RGBA')

def build_door3():
    dw, dh = DX1 - DX0, DY1 - DY0
    im = Image.new('RGBA', (dw * S, dh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, dw * S - 1, dh * S - 1), fill=(48, 36, 30))
    for (a, b, c, e) in [(40, 40, dw - 40, 330), (40, 400, dw - 40, dh - 40)]:
        d.rectangle(P(a, b, c, e), outline=(36, 26, 22), width=8 * S)
    d.ellipse(P(dw - 64, 400, dw - 30, 434), fill=(150, 116, 66))
    return down(im)

def setup_e3():
    global E3_BG, DOOR3, INT3, E3_RAIN, ANT_T, ANT_HAND, LIA_FG, BEAM
    E3_BG = build_e3(); DOOR3 = build_door3()
    INT3 = down(build_interior((DX1 - DX0) * S, (DY1 - DY0) * S)).convert('RGBA')
    E3_RAIN = M.Rain(23, M.RAIN_OUT)
    from PIL import ImageOps
    ANT_T, hand = build_antonio(52, torch=True)
    ANT_HAND = (ANT_T.width - hand[0], hand[1])
    ANT_T = sc(ImageOps.mirror(ANT_T), 0.92)
    LIA_FG = sc(lia_sil(), 1.9)

def frame_e3(t):
    im = E3_BG.copy()
    t_open = stt('e3', 0) + 0.15
    th = 0.0 if t < t_open else eio((t - t_open) / 0.7) * math.radians(100)
    op = math.sin(min(th, math.pi / 2))
    dw, dh = DX1 - DX0, DY1 - DY0
    if op > 0:
        spill = Image.new('L', (W, H), 0)
        ImageDraw.Draw(spill).polygon([(DX0, DY1), (DX1, DY1), (980, H), (60, H)], fill=int(150 * op))
        spill = spill.filter(ImageFilter.GaussianBlur(34))
        light = Image.new('RGBA', (W, H), (255, 180, 100, 0)); light.putalpha(spill); im.alpha_composite(light)
        im.alpha_composite(INT3, (DX0, DY0))
        ta = stt('e3', 1) - 0.3                    # Antônio steps into the doorway
        if t >= ta:
            p = eo(clamp((t - ta) / 0.6)); s = lerp(0.82, 1.0, p)
            a2 = sc(ANT_T, s)
            comp(im, a2, (DX0 + dw / 2 - a2.width / 2 - 10, DY1 - a2.height + 6), p)
            if t >= ta + 0.5:                      # torch beam
                q = eo(clamp((t - ta - 0.5) / 0.3)); fl = 0.85 + 0.15 * math.sin(t * 37) * math.sin(t * 13)
                hx = DX0 + dw / 2 - a2.width / 2 - 10 + ANT_HAND[0] * 0.92 * s - 30 * s; hy = DY1 - a2.height + 6 + ANT_HAND[1] * 0.92 * s + 20 * s
                beam = Image.new('L', (W, H), 0)
                ImageDraw.Draw(beam).polygon([(hx, hy - 10), (hx, hy + 10), (60, 1900), (-260, 1500)], fill=int(110 * q * fl))
                beam = beam.filter(ImageFilter.GaussianBlur(26))
                lb = Image.new('RGBA', (W, H), (255, 236, 190, 0)); lb.putalpha(beam); im.alpha_composite(lb)
    c = math.cos(th); hh = int(dh * (1 + 0.08 * math.sin(th))); yy = DY0 - (hh - dh) // 2
    if th == 0: im.alpha_composite(DOOR3, (DX0, DY0))
    elif c > 0.003: im.alpha_composite(E.M_shade(DOOR3.resize((max(1, int(dw * c)), hh), Image.BILINEAR), 1 - 0.4 * math.sin(th)), (DX0, yy))
    elif c < -0.003:
        wi = int(dw * -c); comp(im, E.M_shade(DOOR3.resize((wi, hh), Image.BILINEAR), 0.45), (DX0 - wi, yy))
    im.alpha_composite(E3_RAIN.layer(t))
    comp(im, LIA_FG, (-170, H - LIA_FG.height + 260))  # Lia from behind, foreground left
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210)); CAP['e3'].draw(im, t)
    return im.convert('RGB')

QX0, QX1, QY0, QY1 = 170, 910, 330, 1560
def setup_e4():
    global E4_BG, E4_RAIN, ANT_POSES
    w, h = W * S, H * S
    img = vgrad(w, h, (22, 24, 34), (12, 13, 20)); d = ImageDraw.Draw(img)
    d.rectangle(P(QX0 - 50, QY0 - 50, QX1 + 50, QY1 + 40), fill=(40, 38, 46))
    inter = build_interior((QX1 - QX0) * S, (QY1 - QY0) * S, keys=True, big=True)
    img.paste(inter, (QX0 * S, QY0 * S))
    img.paste(vgrad(w, (H - QY1 - 40) * S, (30, 26, 26), (8, 7, 8)), (0, (QY1 + 40) * S))
    E4_BG = down(img).convert('RGBA'); E4_RAIN = M.Rain(24, M.RAIN_OUT)
    ANT_POSES = [sc(build_antonio(a)[0], 1.72) for a in (100, 112, 124, 136)]

def frame_e4(t):
    im = E4_BG.copy()
    z = 1 + 0.06 * eio(t / DURS['e4'])
    k = int((t * 6)) % 6; k = [0, 1, 2, 3, 2, 1][k] if t > stt('e4', 1) - 0.2 else 0
    a = ANT_POSES[k]
    comp(im, a, (540 - a.width / 2 + 24, QY1 + 30 - a.height))
    rain = E4_RAIN.layer(t); im.alpha_composite(rain)
    l, tp = 540 * (1 - 1 / z), 900 * (1 - 1 / z)
    im = im.resize((W, H), Image.BILINEAR, box=(l, tp, l + W / z, tp + H / z))
    im = M.apply_mult(im, VIG)
    comp(im, KICK, ((W - KICK.width) // 2, 210)); CAP['e4'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ e5 the phone
def build_poster():
    w, h = 560, 700
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rectangle((26, 30, 26 + w, 30 + h), fill=170)
    im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 20 + w, 20 + h), fill=(244, 240, 228))
    d.rectangle((20, 20, 20 + w, 130), fill=(196, 30, 40))
    d.text((20 + w / 2, 76), 'DESAPARECIDA', font=F('InterDisplay-Black', 66), fill=WHITE, anchor='mm')
    d.rectangle((150, 160, 450, 480), fill=(200, 196, 186))
    d.ellipse((240, 210, 360, 330), fill=(70, 66, 70)); d.rounded_rectangle((200, 320, 400, 480), radius=60, fill=(70, 66, 70))
    d.text((20 + w / 2, 540), 'BIA', font=F('InterDisplay-Black', 84), fill=(30, 26, 30), anchor='mm')
    d.text((20 + w / 2, 620), 'vista pela última vez às 3h17', font=F('Inter-SemiBold', 34), fill=(80, 70, 70), anchor='mm')
    d.text((20 + w / 2, 672), 'há 1 ano', font=F('InterDisplay-ExtraBold', 38), fill=(196, 30, 40), anchor='mm')
    return im.rotate(-4, resample=Image.BICUBIC, expand=True)

def setup_e5():
    global E5_BG, PHONE, NO1, NO2, N_ENT, N_ENT_H, N_BIA, N_BIA_H, E5_RAIN, DROPS, POSTER, NO1H
    E5_BG = vgrad(W, H, (10, 14, 30), (4, 5, 10)).convert('RGBA')
    E5_BG = glow(E5_BG.convert('RGB'), lambda d: d.rectangle(M.PH, fill=255), (40, 50, 110), 90).convert('RGBA')
    _, PHONE = M.build_phone('3:24')
    NO1, NO1H = M.notif_card('não vai pro galpão.')
    NO2, _ = M.notif_card('quem tá batendo na sua porta não sou eu.')
    N_ENT, N_ENT_H = M.notif_card('não entra.')
    N_BIA, N_BIA_H = M.notif_card('sou eu, lia. a bia.')
    E5_RAIN = M.Rain(25, M.RAIN_OUT); DROPS = E.DROPS if hasattr(E, 'DROPS') else None
    POSTER = build_poster()

def frame_e5(t):
    im = E5_BG.copy(); im.alpha_composite(E5_RAIN.layer(t))
    t1, t2, t3 = stt('e5', 1) - 0.25, stt('e5', 3) - 0.25, stt('e5', 4)
    def buzz(t0): return int(round(6 * math.sin(2 * math.pi * 32 * t))) if (t0 <= t < t0 + 0.3 or t0 + 0.45 <= t < t0 + 0.75) else 0
    dx = buzz(stt('e5', 0)) or buzz(t2 - 0.1)
    im.alpha_composite(PHONE, (dx, 0))
    p1 = eo(clamp((t - t1) / 0.4)); p2 = eo(clamp((t - t2) / 0.4))
    sh1 = p1 * (N_ENT_H + 18); sh2 = p2 * (N_BIA_H + 18)
    comp(im, NO1, (M.NX + dx, M.NY + sh1 + sh2))
    if p1 > 0: comp(im, N_ENT, (M.NX + dx, M.NY + sh2 - (1 - p1) * 60), p1)
    if p2 > 0:
        glo = 1 + 0.03 * math.sin(2 * math.pi * (t - t2) / 1.1) if t > t2 + 0.4 else 1
        nb = sc(N_BIA, glo)
        comp(im, nb, (M.NX + dx - (nb.width - N_BIA.width) / 2, M.NY - (1 - p2) * 60), p2)
    if E.DROPS is not None: im.alpha_composite(E.DROPS)
    if t >= t3 - 0.15:
        q = L_backout(clamp((t - t3 + 0.15) / 0.5))
        dim = Image.new('RGBA', (W, H), (0, 0, 0, int(120 * clamp((t - t3 + 0.15) / 0.4)))); im.alpha_composite(dim)
        comp(im, POSTER, (540 - POSTER.width / 2, lerp(H + 50, 560, q)))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210)); CAP['e5'].draw(im, t)
    return im.convert('RGB')

def L_backout(x): return E.backout(x)

# ------------------------------------------------------------ e6 choice
def setup_e6():
    global E6_BG, E6_RAIN, E6_TITLE, CARD_A, CARD_B, CTA, SUB, FOLLOW
    E6_BG = M.build_s6(); E6_RAIN = M.Rain(26, M.RAIN_OUT)
    E6_TITLE = Caption([(0.1, 99, [(0.15, 'O QUE A LIA FAZ?', WHITE)])], font=('InterDisplay-Black', 92), top=380, maxw=1000, gap=0.11)
    CARD_A = M.card('A', 'Entrar na casa', WARM, (30, 20, 8), WARM, (30, 20, 8))
    CARD_B = M.card('B', 'Responder a Bia', RED, (64, 10, 14), (255, 228, 228), WHITE)
    CTA = rich_line([('Comenta ', WHITE), ('A', WARM), (' ou ', WHITE), ('B', RED)], F('InterDisplay-ExtraBold', 74))
    SUB = rich_line([('O mais votado vira o episódio 4', (204, 204, 216))], F('Inter-Medium', 40), stroke=4)
    FOLLOW = rich_line([('Segue', WARM), (' pra não perder o episódio 4', WHITE)], F('InterDisplay-ExtraBold', 54), stroke=5)

def frame_e6(t):
    im = E6_BG.convert('RGBA'); im.alpha_composite(E6_RAIN.layer(t)); im = M.apply_mult(im, VIG)
    comp(im, KICK, ((W - KICK.width) // 2, 210)); E6_TITLE.draw(im, t)
    for (img, y, t0, side, ph) in [(CARD_A, 560, 0.6, -1, 0.0), (CARD_B, 790, 0.9, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45); x = (W - img.width) / 2 + side * (1 - p) * 140
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.8) / 1.5 + ph) if t > 2.8 else 1.0
        i2 = sc(img, s); comp(im, i2, (x + img.width / 2 - i2.width / 2, y + img.height / 2 - i2.height / 2), p)
    if t >= 1.6: p = eo((t - 1.6) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1065 + (1 - p) * 24), p)
    if t >= 2.0: p = eo((t - 2.0) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1175 + (1 - p) * 18), p)
    if t >= 2.5:
        p = E.backout((t - 2.5) / 0.45); s_ = 0.7 + 0.3 * p + (0.02 * math.sin(2 * math.pi * (t - 3.0) / 1.3) if t > 3.0 else 0)
        fw = sc(FOLLOW, s_); comp(im, fw, ((W - fw.width) / 2, 1275 + (FOLLOW.height - fw.height) / 2), clamp((t - 2.5) * 4))
    return im.convert('RGB')

# ------------------------------------------------------------ captions
def gap_for(k):
    per = [d / len(s[0].split()) for s, d in zip(SENTS[k], T[k]['du'])]
    return float(np.clip(0.8 * min(per), 0.06, 0.3))

def build_caps():
    global CAP
    CAP = {}; s = SENTS
    ts = {k: [LEAD + v for v in T[k]['st']] for k in SENTS}
    def page(k, idxs, end):
        return (ts[k][idxs[0]] - 0.05, end, [(ts[k][i], s[k][i][0], s[k][i][1]) for i in idxs])
    CAP['e1'] = Caption([page('e1', [0, 1], DURS['e1'])], gap=gap_for('e1'))
    CAP['e2'] = Caption([page('e2', [0], ts['e2'][1] - 0.1), page('e2', [1], DURS['e2'])], gap=gap_for('e2'))
    CAP['e3'] = Caption([page('e3', [0], ts['e3'][1] - 0.1), page('e3', [1, 2], DURS['e3'])], gap=gap_for('e3'))
    CAP['e4'] = Caption([page('e4', [0, 1, 2], DURS['e4'])], gap=gap_for('e4'))
    CAP['e5'] = Caption([page('e5', [0, 1], ts['e5'][2] - 0.1), page('e5', [2, 3], ts['e5'][4] - 0.1), page('e5', [4], DURS['e5'])], gap=gap_for('e5'), top=1440)

FRAMES = {'e0': frame_e0, 'e1': frame_e1, 'e2': frame_e2, 'e3': frame_e3, 'e4': frame_e4, 'e5': frame_e5, 'e6': frame_e6}

# ------------------------------------------------------------ sound
def make_audio(path, x, starts, total):
    n = int(total * SR); t = np.arange(n) / SR; rng = np.random.default_rng(13)
    f = np.fft.rfftfreq(n, 1 / SR)
    resp = 1 / (1 + (350 / np.maximum(f, 1)) ** 2) / (1 + (f / 5200) ** 2)
    rain = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * resp, n); rain /= np.abs(rain).max()
    e = starts
    kp = [(0, .36), (e['e1'] - .05, .36), (e['e1'] + .1, .22), (e['e2'], .38), (e['e4'], .30), (e['e5'], .20), (e['e6'], .24), (total, .24)]
    out = rain * np.interp(t, [a for a, _ in kp], [b for _, b in kp])
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 110.4 * t + 1) + 0.45 * np.sin(2 * np.pi * 164.8 * t + 2))
    out += drone * np.interp(t, [0, e['e2'], e['e4'], e['e5'], total], [0.04, 0.05, 0.08, 0.1, 0.09])
    def add(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += sig[:j - i]
    def tt(d): return np.arange(int(d * SR)) / SR
    def bp(sig, lo, hi):
        X = np.fft.rfft(sig); ff = np.fft.rfftfreq(len(sig), 1 / SR); X *= (ff >= lo) & (ff <= hi); return np.fft.irfft(X, len(sig))
    def creak(d=0.9, f0=180, f1=120, g=0.25):
        tq = tt(d); fr = f0 + (f1 - f0) * tq / d + 25 * np.sin(2 * np.pi * 9 * tq)
        saw = 2 * ((np.cumsum(fr) / SR) % 1) - 1
        y = bp(saw * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * tq)), 300, 3000)
        return y / np.abs(y).max() * g * np.minimum(1, tq / 0.05) * np.minimum(1, (d - tq) / 0.1)
    def splash(g=0.12, d=0.18):
        tq = tt(d); y = bp(rng.standard_normal(len(tq)), 200, 2500); return y / np.abs(y).max() * np.exp(-tq / (d / 3.5)) * g
    def scrape(d=0.5, g=0.08):
        tq = tt(d); y = bp(rng.standard_normal(len(tq)), 1200, 6000); y /= np.abs(y).max()
        return y * g * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * tq) ** 2) * np.minimum(1, tq / 0.05) * np.minimum(1, (d - tq) / 0.08)
    def buzz(d):
        tq = tt(d); return np.tanh(2.5 * np.sin(2 * np.pi * 172 * tq)) * np.minimum(1, tq / 0.01) * np.minimum(1, (d - tq) / 0.03) * 0.16
    def hum(d=1.6, g=0.07):
        tq = tt(d); return (np.sin(2 * np.pi * 60 * tq) + 0.5 * np.sin(2 * np.pi * 120 * tq)) * np.minimum(1, tq / 0.02) * np.exp(-tq / 1.4) * g
    def hit(g=0.6):
        tq = tt(2.5); fr = 38 + 52 * np.exp(-tq / 0.25)
        return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tq / 0.9) * 0.6 + np.sin(4 * np.pi * np.cumsum(fr) / SR) * np.exp(-tq / 0.5) * 0.25) * g / 0.6
    def click(g=0.2):
        tq = tt(0.03); return bp(rng.standard_normal(len(tq)), 1500, 8000) * np.exp(-tq / 0.006) * g * 3
    # e0
    add(buzz(0.35) * 2.6, 0.05); add(buzz(0.35) * 2.6, 0.6); add(hit(0.7), 0.0)
    # e1
    add(hit(0.45), e['e1'] + stt('e1', 1) - 0.1)
    # e2
    td = e['e2'] + stt('e2', 1) - 0.1
    for k in range(3): add(scrape(0.45, 0.07), e['e2'] + LEAD + 0.2 + k * 0.6)
    add(hit(0.75), td + 0.38); add(splash(0.3, 0.4), td + 0.38)
    # e3
    t_open = e['e3'] + stt('e3', 0) + 0.15
    add(creak(1.0, 230, 150, 0.22), t_open); add(hum(), t_open + 0.2)
    add(click(0.25), e['e3'] + stt('e3', 1) + 0.2)
    # e5
    add(buzz(0.3), e['e5'] + stt('e5', 0)); add(buzz(0.3), e['e5'] + stt('e5', 0) + 0.45)
    t2 = e['e5'] + stt('e5', 3) - 0.35
    add(buzz(0.3), t2); add(buzz(0.3), t2 + 0.45)
    add(hit(0.7), e['e5'] + stt('e5', 4) - 0.1)
    add(hit(0.6), e['e6'])
    # narration
    nar = np.zeros(n)
    for k in ORDER:
        a, b = max(0.0, T[k]['a'] - 0.04), T[k]['b'] + 0.1
        seg = x[int(a * SR):int(b * SR)]
        i = int((e[k] + LEAD - 0.04) * SR); j = min(n, i + len(seg)); nar[i:j] += seg[:j - i]
    voiced = np.abs(nar) > 0.02 * np.abs(nar).max()
    nar *= 0.15 / np.sqrt((nar[voiced] ** 2).mean())
    env = np.convolve(np.abs(nar), np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
    duck = 1 - 0.5 * np.clip(env / 0.02, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
    mix = out * 0.6 * duck + nar
    mix *= np.clip((total - t) / 0.8, 0, 1)
    mix = np.tanh(mix * 1.3) / 1.3
    mix *= min(1.0, 0.95 / np.abs(mix).max())
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------ main
if __name__ == '__main__':
    mode, narr = sys.argv[1], sys.argv[2]
    bounds = [float(v) for v in os.environ.get('BOUNDS', '2.46,7.41,12.66,15.73,24.2').split(',')]
    X, T = E.analyse(narr, bounds); E.T = T
    DURS = {k: r30(max(MINS[k], LEAD + T[k]['L'] + TAIL[k])) for k in ORDER}
    DURS = {'e0': COLD, **DURS}; E.DURS = DURS
    print('durs', DURS, 'total', round(sum(DURS.values()), 2))
    for k in SENTS: print(k, [round(v, 2) for v in T[k]['st']])
    MULT = M.make_mult(0.55, True); VIG = M.make_mult(0.55, False)
    E.MULT, E.VIG = MULT, VIG
    KICK = E.kicker('QUEM BATE À PORTA  ·  EP. 3'); CHECK = E.build_check()
    E.DROPS = None
    t0 = time.time()
    setup_e0(); setup_e1(); setup_e2(); setup_e3(); setup_e4(); setup_e5(); setup_e6(); build_caps()
    print(f'setup {time.time() - t0:.1f}s', flush=True)
    SEQ = ['e0'] + ORDER
    if mode == 'preview':
        shots = [('e0', 0.6), ('e1', stt('e1', 1) + 0.6), ('e2', stt('e2', 1) - 0.4), ('e2', stt('e2', 1) + 0.9),
                 ('e3', stt('e3', 1) + 1.0), ('e4', stt('e4', 2)), ('e5', stt('e5', 3) + 0.5), ('e5', stt('e5', 4) + 1.0), ('e6', 4.0)]
        th = []
        for k, tt_ in shots: th.append(FRAMES[k](tt_).resize((W // 4, H // 4), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 4 * 5, H // 4 * 2))
        for i, im in enumerate(th): sheet.paste(im, ((i % 5) * (W // 4), (i // 5) * (H // 4)))
        sheet.save(f'{OUT}/sheet.png'); print('sheet ok')
    else:
        only = sys.argv[3:] or SEQ
        for idx, k in enumerate(SEQ):
            if k in only: E.encode(k, FRAMES[k], DURS[k], fade_in=0 if k in ('e0', 'e1') else 4, fade_out=12 if idx == len(SEQ) - 1 else 0)
        starts, acc = {}, 0.0
        for k in SEQ: starts[k] = acc; acc += int(round(DURS[k] * FPS)) / FPS
        make_audio(f'{OUT}/audio.wav', X, starts, acc)
        with open(f'{OUT}/list.txt', 'w') as fl:
            for k in SEQ: fl.write(f"file '{k}.mp4'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video.mp4'], check=True)
        final = f'{OUT}/quem-bate-a-porta-ep3.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final + '.part.mp4'], check=True)
        os.replace(final + '.part.mp4', final); print('done', round(acc, 2))
