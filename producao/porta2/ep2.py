#!/usr/bin/env python3
"""Quem Bate à Porta — Episódio 2 (caminho B: fugir pelos fundos). Usage: ep2.py preview|render narr.mp3"""
import os, sys, math, random, subprocess, wave, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/video')
import make as M
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, tracked, rich_line, WHITE, WARM, RED, INK

W, H, FPS, S = 1080, 1920, 30, 2
OUT = '/home/claude/porta2'
SR = 44100
LEAD = 0.35
NIGHT_TOP, NIGHT_BOT = (6, 9, 22), (30, 36, 66)
SIL = (8, 10, 18)

def backout(x, c1=1.70158):
    x = clamp(x); c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def kicker(text='QUEM BATE À PORTA  ·  EP. 2'):
    txt = tracked(text, F('Inter-SemiBold', 30), (232, 232, 240, 230), 5)
    im = Image.new('RGBA', (txt.width + 34, txt.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); cy = txt.height // 2 + 1
    d.ellipse((4, cy - 8, 20, cy + 8), fill=RED + (255,))
    im.alpha_composite(txt, (26, 0))
    return im

# ------------------------------------------------------------ narration timing
SENTS = {
    'e1': [('Vocês escolheram…', WHITE), ('fugir pelos fundos.', RED)],
    'e2': [('Lia saiu pela porta da cozinha, descalça, debaixo da chuva.', WHITE)],
    'e3': [('O portão do quintal…', WHITE), ('estava aberto.', WHITE)],
    'e4': [('Tinha pegadas de barro no chão.', WHITE), ('Elas iam direto pro galpão.', WHITE), ('E a luz lá dentro estava acesa.', WARM)],
    'e5': [('O celular vibrou de novo.', WHITE), ('“Não vai pro galpão.”', WARM)],
}
ORDER = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6']
MINS = {'e1': 4.2, 'e2': 5.5, 'e3': 4.6, 'e4': 7.0, 'e5': 5.0, 'e6': 8.0}
TAIL = {'e1': 1.0, 'e2': 1.4, 'e3': 1.3, 'e4': 1.2, 'e5': 1.3, 'e6': 1.6}

def analyse(path, bounds_at):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    hop = int(0.01 * SR)
    rms = np.sqrt(np.convolve(x * x, np.ones(hop * 3) / (hop * 3), 'same'))[::hop]
    loud = 20 * np.log10(rms / rms.max() + 1e-9) > -38
    runs, i = [], 0
    while i < len(loud):
        if not loud[i]:
            j = i
            while j < len(loud) and not loud[j]: j += 1
            runs.append((i * 0.01, j * 0.01)); i = j
        else:
            i += 1
    first = next(k for k in range(len(loud)) if loud[k]) * 0.01
    last = (len(loud) - next(k for k in range(len(loud)) if loud[::-1][k])) * 0.01
    inner = [r for r in runs if r[0] > first and r[1] < last]
    bounds = [min(inner, key=lambda r: abs(r[0] - t)) for t in bounds_at]
    segs, s0 = [], first
    for a, b in bounds: segs.append((s0, a)); s0 = b
    segs.append((s0, last))
    T = {}
    for k, (a, b) in zip(ORDER, segs):
        T[k] = {'a': a, 'b': b, 'L': b - a}
        if k in SENTS:
            sents = SENTS[k]; L = b - a
            tot = sum(len(s[0]) for s in sents)
            cands = [r for r in inner if r[0] > a + 0.1 and r[1] < b - 0.1 and r[1] - r[0] >= 0.06]
            st, ch, acc, prev = [0.0], [], 0, a
            for s in sents[:-1]:
                acc += len(s[0]); f = acc / tot
                pool = [r for r in cands if r[0] > prev + 0.15]
                r = min(pool, key=lambda r: abs((r[0] - a) / L - f)) if pool else (a + L * f, a + L * f)
                ch.append(r); st.append(r[1] - a); prev = r[1]
            ends = [c[0] - a for c in ch] + [L]
            T[k]['st'] = st; T[k]['du'] = [e - s for s, e in zip(st, ends)]
    return x, T

def r30(v): return round(v * 30) / 30

# ------------------------------------------------------------ e1: recap of the vote
def setup_e1():
    global E1_BG, E1_RAIN, CARD_A1, CARD_B1
    E1_BG = M.build_s6()
    E1_RAIN = M.Rain(21, M.RAIN_OUT)
    CARD_A1 = M.card('A', 'Abrir a porta', WARM, (30, 20, 8), WARM, (30, 20, 8))
    CARD_B1 = M.card('B', 'Fugir pelos fundos', RED, (64, 10, 14), (255, 228, 228), WHITE)

def frame_e1(t):
    im = E1_BG.convert('RGBA'); im.alpha_composite(E1_RAIN.layer(t))
    im = M.apply_mult(im, MULT)
    sel = T['e1']['st'][1] + LEAD - 0.1
    for img, y, t0, side, isB in ((CARD_A1, 640, 0.1, -1, False), (CARD_B1, 870, 0.25, 1, True)):
        if t < t0: continue
        p = eo((t - t0) / 0.4)
        a = p
        s = 1.0
        if t > sel:
            q = eo((t - sel) / 0.3)
            if isB: s = 1 + 0.08 * q + (0.012 * math.sin(2 * math.pi * (t - sel) / 1.2) if t > sel + 0.3 else 0)
            else: a = p * (1 - 0.7 * q)
        im2 = img if abs(s - 1) < 1e-3 else img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
        x = (W - img.width) / 2 + side * (1 - p) * 160
        comp(im, im2, (x + img.width / 2 - im2.width / 2, y + img.height / 2 - im2.height / 2), a)
    if t > sel:
        q = eo((t - sel) / 0.25)
        ck = CHECK.resize((max(1, int(CHECK.width * (0.5 + 0.5 * q))), max(1, int(CHECK.height * (0.5 + 0.5 * q)))), Image.BILINEAR)
        comp(im, ck, (975 - ck.width / 2, 878 - ck.height / 2), q)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    CAP['e1'].draw(im, t)
    return im.convert('RGB')

def build_check():
    im = Image.new('RGBA', (150 * S, 150 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse(P(5, 5, 145, 145), fill=(255, 255, 255)); d.ellipse(P(15, 15, 135, 135), fill=(40, 170, 90))
    d.line(P(45, 78, 66, 100, 108, 52), fill=(255, 255, 255), width=14 * S, joint='curve')
    return down(im)

# ------------------------------------------------------------ e2: the back door
OX0, OY0, OX1, OY1 = 330, 470, 750, 1400
def build_e2():
    w, h = W * S, H * S
    img = vgrad(w, h, (22, 22, 34), (12, 12, 20), 0, 1400 * S)
    img = glow(img, lambda d: d.ellipse(P(-300, 300, 300, 1300), fill=160), (40, 30, 18), 80 * S)
    d = ImageDraw.Draw(img)
    img.paste(vgrad(w, (H - 1400) * S, (26, 22, 24), (6, 5, 6)), (0, 1400 * S)); d = ImageDraw.Draw(img)
    yy, k = 1400, 0
    while yy < H:
        k += 1; yy += 18 + k * k * 4
        d.line(P(0, yy, W, yy), fill=(18, 15, 16), width=2 * S)
    for x in range(-600, W + 600, 160):
        d.line(P(540 + (x - 540) * 0.4, 1400, x, H), fill=(18, 15, 16), width=2 * S)
    d.rectangle(P(0, 1060, 250, 1400), fill=(14, 13, 20)); d.rectangle(P(0, 1040, 262, 1066), fill=(30, 28, 38))
    d.rectangle(P(860, 1100, W, 1400), fill=(14, 13, 20)); d.rectangle(P(848, 1080, W, 1106), fill=(30, 28, 38))
    d.rectangle(P(306, 446, 774, 1400), fill=(36, 30, 34))
    ext = build_e2_ext()
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rectangle(P(OX0, OY0, OX1, OY1), fill=255)
    img.paste(ext, (0, 0), m)
    return down(img), down(m)

def build_e2_ext():
    w, h = W * S, H * S
    img = vgrad(w, h, (8, 12, 28), (40, 48, 80), 470 * S, 1000 * S)
    img = glow(img, lambda d: d.ellipse(P(600, 560, 760, 700), fill=200), (90, 80, 50), 30 * S)
    d = ImageDraw.Draw(img)
    d.rectangle(P(0, 960, W, 1160), fill=(14, 16, 26))
    for x in range(OX0 - 20, OX1 + 20, 34):
        d.rectangle(P(x, 940, x + 26, 1160), fill=(16, 18, 28))
        d.polygon(P(x, 940, x + 13, 924, x + 26, 940), fill=(16, 18, 28))
    img.paste(vgrad(w, (1400 - 1160) * S, (16, 22, 24), (8, 10, 12)), (0, 1160 * S)); d = ImageDraw.Draw(img)
    for (a, b, c, e) in [(380, 1250, 520, 1275), (580, 1320, 720, 1350), (430, 1360, 600, 1385)]:
        d.ellipse(P(a, b, c, e), fill=(46, 56, 88))
    return img

def build_backdoor():
    dw, dh = OX1 - OX0, OY1 - OY0
    im = Image.new('RGBA', (dw * S, dh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, dw * S - 1, dh * S - 1), fill=(46, 34, 30))
    d.rectangle(P(60, 50, dw - 60, 360), fill=(34, 44, 72))
    for k in range(9):
        x = 80 + k * 32
        d.line(P(x, 60, x - 14, 350), fill=(70, 84, 120), width=2 * S)
    d.rectangle(P(60, 50, dw - 60, 360), outline=(30, 22, 20), width=12 * S)
    d.line(P(dw / 2, 50, dw / 2, 360), fill=(30, 22, 20), width=8 * S)
    d.rectangle(P(50, 420, dw - 50, 880), outline=(36, 26, 22), width=6 * S)
    d.ellipse(P(dw - 70, 560, dw - 34, 596), fill=(150, 116, 66))
    inner = Image.new('RGBA', (dw * S, dh * S), (0, 0, 0, 0)); di = ImageDraw.Draw(inner)
    di.rectangle((0, 0, dw * S - 1, dh * S - 1), fill=(36, 28, 26))
    di.rectangle(P(50, 420, dw - 50, 880), outline=(28, 20, 18), width=6 * S)
    return down(im), down(inner)

def build_lia():
    im = Image.new('RGBA', (300 * S, 720 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = SIL + (255,)
    d.ellipse(P(92, 52, 208, 176), fill=c)
    d.rounded_rectangle(P(88, 110, 212, 320), radius=52 * S, fill=c)
    d.polygon(P(66, 236, 234, 236, 204, 392, 96, 392), fill=c)
    d.polygon(P(96, 388, 204, 388, 216, 476, 84, 476), fill=c)
    d.rounded_rectangle(P(58, 222, 242, 276), radius=28 * S, fill=c)
    d.rounded_rectangle(P(42, 236, 72, 462), radius=15 * S, fill=c)
    d.rounded_rectangle(P(228, 236, 258, 462), radius=15 * S, fill=c)
    d.rounded_rectangle(P(104, 466, 140, 712), radius=17 * S, fill=c)
    d.rounded_rectangle(P(160, 466, 196, 712), radius=17 * S, fill=c)
    sp = down(im)
    a = sp.getchannel('A')
    rim = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))
    out = Image.new('RGBA', sp.size, (110, 140, 200, 0)); out.putalpha(rim.point(lambda v: int(v * 0.55)))
    out.alpha_composite(sp)
    return out

def setup_e2():
    global E2_BG, E2_MASK, DOOR_F, DOOR_I, LIA, E2_RAIN
    E2_BG, E2_MASK = build_e2()
    DOOR_F, DOOR_I = build_backdoor()
    LIA = build_lia()
    E2_RAIN = M.Rain(22, M.RAIN_OUT)

def frame_e2(t):
    im = E2_BG.convert('RGBA')
    rain = E2_RAIN.layer(t)
    rain.putalpha(ImageChops.multiply(rain.getchannel('A'), E2_MASK))
    im.alpha_composite(rain)
    t_open = LEAD + 0.2
    th = 0.0 if t < t_open else eio((t - t_open) / 0.8) * math.radians(100)
    open_amt = math.sin(min(th, math.pi / 2))
    if open_amt > 0:
        spill = Image.new('L', (W, H), 0)
        ImageDraw.Draw(spill).polygon([(OX0, OY1), (OX1, OY1), (980, H), (100, H)], fill=int(120 * open_amt))
        spill = spill.filter(ImageFilter.GaussianBlur(30))
        light = Image.new('RGBA', (W, H), (90, 110, 160, 0)); light.putalpha(spill)
        im.alpha_composite(light)
    dw, dh = OX1 - OX0, OY1 - OY0
    c = math.cos(th)
    hh = int(dh * (1 + 0.1 * math.sin(th))); yy = OY0 - (hh - dh) // 2
    if th == 0:
        im.alpha_composite(DOOR_F, (OX0, OY0))
    elif c > 0.003:
        im.alpha_composite(M_shade(DOOR_F.resize((max(1, int(dw * c)), hh), Image.BILINEAR), 1 - 0.4 * math.sin(th)), (OX0, yy))
    elif c < -0.003:
        wi = int(dw * -c); comp(im, M_shade(DOOR_I.resize((wi, hh), Image.BILINEAR), 0.6), (OX0 - wi, yy))
    w0, w1 = t_open + 0.6, DURS['e2'] - 0.5
    if w0 < t < w1 + 0.4:
        p = clamp((t - w0) / (w1 - w0))
        pe = eio(p)
        feet = lerp(2080, 1300, pe)
        s = lerp(1.55, 0.36, pe)
        bob = -abs(math.sin(2 * math.pi * 1.4 * (t - w0))) * 14 * s
        sp = LIA.resize((max(1, int(LIA.width * s)), max(1, int(LIA.height * s))), Image.BILINEAR)
        a = 1.0 - clamp((t - w1) / 0.4)
        comp(im, sp, (540 - sp.width / 2, feet - sp.height + bob), a)
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    CAP['e2'].draw(im, t)
    return im.convert('RGB')

def M_shade(im, f):
    r, g, b, a = im.split(); lut = [int(v * f) for v in range(256)]
    return Image.merge('RGBA', (r.point(lut), g.point(lut), b.point(lut), a))

# ------------------------------------------------------------ e3: the open gate
GX0, GX1, GY0, GY1 = 400, 680, 760, 1240
def build_e3():
    w, h = W * S, H * S
    img = vgrad(w, h, NIGHT_TOP, NIGHT_BOT, 0, 900 * S)
    img = glow(img, lambda d: d.ellipse(P(700, 420, 1000, 720), fill=180), (70, 60, 40), 60 * S)
    d = ImageDraw.Draw(img)
    rng = random.Random(31); x = -20
    while x < W:
        bw = rng.randint(80, 160); bh = rng.randint(120, 300)
        d.rectangle(P(x, 900 - bh, x + bw, 900), fill=(14, 18, 34))
        if rng.random() < 0.3: d.rectangle(P(x + 20, 900 - bh + 30, x + 34, 900 - bh + 48), fill=(96, 80, 50))
        x += bw + rng.randint(-10, 8)
    d.rectangle(P(0, 880, W, 1240), fill=(16, 20, 30))
    d.rectangle(P(836, 560, 846, 1100), fill=(18, 20, 30))
    img = glow(img, lambda d: d.ellipse(P(800, 540, 880, 600), fill=255), (255, 214, 140), 14 * S)
    img = glow(img, lambda d: d.polygon(P(820, 590, 862, 590, 980, 1240, 700, 1240), fill=110), (110, 90, 56), 22 * S)
    d = ImageDraw.Draw(img)
    fc, fl = (30, 25, 24), (22, 18, 18)
    for x0, x1 in ((-20, GX0), (GX1, W + 20)):
        d.rectangle(P(x0, GY0, x1, GY1), fill=fc)
        for x in range(x0, x1, 46): d.line(P(x, GY0, x, GY1), fill=fl, width=4 * S)
        for x in range(x0, x1, 46): d.polygon(P(x, GY0, x + 23, GY0 - 26, x + 46, GY0), fill=fc)
        d.rectangle(P(x0, GY0 + 70, x1, GY0 + 92), fill=fl); d.rectangle(P(x0, GY1 - 110, x1, GY1 - 88), fill=fl)
    d.rectangle(P(GX0 - 16, GY0 - 40, GX0, GY1), fill=(20, 16, 16)); d.rectangle(P(GX1, GY0 - 40, GX1 + 16, GY1), fill=(20, 16, 16))
    img.paste(vgrad(w, (H - GY1) * S, (16, 22, 20), (5, 7, 7)), (0, GY1 * S)); d = ImageDraw.Draw(img)
    d.polygon(P(GX0, GY1, GX1, GY1, 760, H, 320, H), fill=(26, 22, 20))
    for (a, b, c, e) in [(140, 1400, 360, 1440), (700, 1500, 960, 1550), (420, 1650, 660, 1700), (60, 1760, 300, 1810)]:
        d.ellipse(P(a, b, c, e), fill=(38, 46, 72))
    return down(img).convert('RGBA')

def setup_e3():
    global E3_BG, E3_RAIN, RIPPLES
    E3_BG = build_e3()
    E3_RAIN = M.Rain(23, M.RAIN_OUT)
    rng = random.Random(5)
    RIPPLES = [(rng.uniform(120, 960), rng.uniform(1380, 1820), rng.uniform(0, 1)) for _ in range(26)]

def frame_e3(t):
    im = E3_BG.copy()
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ang = math.radians(64 + 5 * math.sin(2 * math.pi * t / 2.6))
    gw = GX1 - GX0
    fx = GX1 - gw * math.cos(ang)
    sh = 0.12 * math.sin(ang)
    top = GY0 + (GY1 - GY0) * sh * 0.5; bot = GY1 - (GY1 - GY0) * sh * 0.5
    d.polygon([(GX1, GY0), (fx, top), (fx, bot), (GX1, GY1)], fill=(40, 33, 30, 255))
    for k in range(1, 6):
        xk = GX1 - (GX1 - fx) * k / 6
        d.line([(xk, GY0 + (top - GY0) * k / 6), (xk, GY1 + (bot - GY1) * k / 6)], fill=(28, 22, 20, 255), width=3)
    for k in range(len(RIPPLES)):
        x, y, ph = RIPPLES[k]
        q = (t * 0.9 + ph) % 1.0
        r = 6 + 34 * q
        d.ellipse((x - r, y - r * 0.3, x + r, y + r * 0.3), outline=(130, 150, 200, int(120 * (1 - q))), width=2)
    im.alpha_composite(lay)
    im.alpha_composite(E3_RAIN.layer(t))
    tl = LEAD + T['e3']['st'][1] - 0.15
    if tl <= t < tl + 0.5:
        q = (t - tl) / 0.5
        f = (1 - q) ** 2 * (1.0 if (t - tl) > 0.06 or (t - tl) < 0.03 else 0.4)
        bolt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); db = ImageDraw.Draw(bolt)
        pts = [(260, 0), (300, 160), (250, 260), (320, 420), (290, 520), (350, 700)]
        db.line(pts, fill=(230, 236, 255, int(255 * f)), width=6, joint='curve')
        im.alpha_composite(bolt)
        a = np.asarray(im).astype(np.float32)
        a[..., :3] = a[..., :3] + (255 - a[..., :3]) * 0.45 * f
        im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    CAP['e3'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ e4: footprints to the shed
def build_e4(light):
    w, h = W * S, H * S
    img = vgrad(w, h, NIGHT_TOP, NIGHT_BOT, 0, 1000 * S)
    d = ImageDraw.Draw(img)
    rng = random.Random(41)
    for _ in range(9):
        cx = rng.uniform(-60, W + 60); r = rng.uniform(90, 170)
        d.ellipse(P(cx - r, 1010 - r * 1.1, cx + r, 1010 + r * 0.4), fill=(10, 14, 20))
    img.paste(vgrad(w, (H - 1000) * S, (12, 18, 16), (4, 6, 6)), (0, 1000 * S)); d = ImageDraw.Draw(img)
    d.polygon(P(520, 1066, 600, 1066, 790, H, 290, H), fill=(40, 30, 24))
    for (a, b, c, e) in [(470, 1300, 560, 1320), (600, 1500, 720, 1530), (380, 1700, 520, 1735)]:
        d.ellipse(P(a, b, c, e), fill=(54, 50, 62))
    if light:
        img = glow(img, lambda d: d.polygon(P(430, 1070, 650, 1070, 760, 1300, 330, 1300), fill=130), (130, 90, 40), 30 * S)
        img = glow(img, lambda d: d.ellipse(P(400, 790, 560, 940), fill=200), (200, 140, 60), 40 * S)
        d = ImageDraw.Draw(img)
    d.polygon(P(372, 790, 540, 690, 708, 790), fill=(22, 18, 18))
    d.rectangle(P(400, 786, 680, 1068), fill=(36, 29, 26))
    for x in range(400, 680, 28): d.line(P(x, 790, x, 1068), fill=(28, 22, 20), width=3 * S)
    d.rectangle(P(440, 830, 520, 904), fill=(255, 206, 120) if light else (16, 18, 26))
    d.line(P(480, 830, 480, 904), fill=(36, 29, 26), width=5 * S); d.line(P(440, 867, 520, 867), fill=(36, 29, 26), width=5 * S)
    d.rectangle(P(564, 880, 650, 1068), fill=(26, 20, 18))
    if light:
        d.rectangle(P(560, 880, 566, 1068), fill=(255, 210, 130))
    return down(img).convert('RGBA')

FOOT = []
def setup_e4():
    global E4_OFF, E4_ON, E4_RAIN
    E4_OFF, E4_ON = build_e4(False), build_e4(True)
    E4_RAIN = M.Rain(24, M.RAIN_OUT)
    n = 12
    for i in range(n):
        p = i / (n - 1)
        y = lerp(1840, 1090, 1 - (1 - p) ** 1.6)
        s = lerp(1.0, 0.16, 1 - (1 - p) ** 1.3)
        side = -1 if i % 2 == 0 else 1
        FOOT.append((540 + side * 46 * s, y, s))

def draw_print(d, x, y, s, a):
    col = (16, 10, 8, int(235 * a))
    d.ellipse((x - 24 * s, y - 14 * s, x + 24 * s, y + 14 * s), fill=col)
    for k in range(5):
        tx = x - 20 * s + k * 10 * s; ty = y - 22 * s - (2 - abs(k - 2)) * 2 * s
        d.ellipse((tx - 4.5 * s, ty - 4 * s, tx + 4.5 * s, ty + 4 * s), fill=col)

def frame_e4(t):
    st = [LEAD + v for v in T['e4']['st']]
    lt = st[2] + 0.4
    if t < lt: base = E4_OFF
    else:
        q = t - lt
        flick = 1.0 if q > 0.5 else (1.0 if int(q * 14) % 3 else 0.0)
        base = E4_ON if flick > 0.5 else E4_OFF
        if q > 0.5: base = Image.blend(E4_ON, E4_OFF, 0.08 * (1 + math.sin(t * 23)) / 2)
    im = base.copy()
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f0, f1 = st[0] + 0.2, st[1] + 0.8
    for i, (x, y, s) in enumerate(FOOT):
        ti = f0 + (f1 - f0) * i / len(FOOT)
        if t >= ti: draw_print(d, x, y, s, eo((t - ti) / 0.3))
    im.alpha_composite(lay)
    im.alpha_composite(E4_RAIN.layer(t))
    z = 1 + 0.14 * eio(t / DURS['e4'])
    fx, fy = 540, 930
    l, tp = fx * (1 - 1 / z), fy * (1 - 1 / z)
    im = im.resize((W, H), Image.BILINEAR, box=(l, tp, l + W / z, tp + H / z))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    CAP['e4'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ e5: third message
def setup_e5():
    global E5_BG, PHONE, N1, N2, N3, N3H, N2H, E5_RAIN, DROPS
    E5_BG = vgrad(W, H, (10, 14, 30), (4, 5, 10)).convert('RGBA')
    E5_BG = glow(E5_BG.convert('RGB'), lambda d: d.rectangle(M.PH, fill=255), (40, 50, 110), 90).convert('RGBA')
    _, PHONE = M.build_phone('3:21')
    N1, _ = M.notif_card('não abre a porta.')
    N2, N2H = M.notif_card('quem tá batendo na sua porta não sou eu.')
    N3, N3H = M.notif_card('não vai pro galpão.')
    E5_RAIN = M.Rain(25, M.RAIN_OUT)
    DROPS = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(DROPS)
    rng = random.Random(9)
    for _ in range(60):
        x = rng.uniform(230, 850); y = rng.uniform(380, 1900); r = rng.uniform(4, 13)
        dd.ellipse((x - r, y - r * 1.2, x + r, y + r * 1.2), fill=(170, 190, 230, 70))
        dd.ellipse((x - r * 0.45, y - r * 0.8, x - r * 0.05, y - r * 0.3), fill=(235, 242, 255, 140))

def frame_e5(t):
    im = E5_BG.copy()
    im.alpha_composite(E5_RAIN.layer(t))
    tb = LEAD + 0.25
    dx = int(round(6 * math.sin(2 * math.pi * 32 * t))) if tb <= t < tb + 0.35 or tb + 0.5 <= t < tb + 0.85 else 0
    im.alpha_composite(PHONE, (dx, 0))
    p = eo((t - (tb + 0.15)) / 0.4) if t >= tb + 0.15 else 0.0
    shift = p * (N3H + 18)
    comp(im, N2, (M.NX + dx, M.NY + shift), 1.0)
    comp(im, N1, (M.NX + dx, M.NY + N2H + 18 + shift), 1.0)
    if p > 0: comp(im, N3, (M.NX + dx, M.NY - (1 - p) * 60), p)
    im.alpha_composite(DROPS)
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    CAP['e5'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ e6: the choice
def setup_e6():
    global E6_BG, E6_RAIN, E6_TITLE, CARD_A, CARD_B, CTA, SUB
    E6_BG = M.build_s6()
    E6_RAIN = M.Rain(26, M.RAIN_OUT)
    E6_TITLE = Caption([(0.1, 99, [(0.15, 'O QUE A LIA FAZ?', WHITE)])], font=('InterDisplay-Black', 92), top=380, maxw=1000, gap=0.11)
    CARD_A = M.card('A', 'Entrar no galpão', WARM, (30, 20, 8), WARM, (30, 20, 8))
    CARD_B = M.card('B', 'Pular o muro', RED, (64, 10, 14), (255, 228, 228), WHITE)
    CTA = rich_line([('Comenta ', WHITE), ('A', WARM), (' ou ', WHITE), ('B', RED)], F('InterDisplay-ExtraBold', 74))
    SUB = rich_line([('O mais votado vira o episódio 3', (204, 204, 216))], F('Inter-Medium', 40), stroke=4)
    global FOLLOW
    FOLLOW = rich_line([('Segue', WARM), (' pra não perder o episódio 3', WHITE)], F('InterDisplay-ExtraBold', 54), stroke=5)

def frame_e6(t):
    im = E6_BG.convert('RGBA'); im.alpha_composite(E6_RAIN.layer(t))
    im = M.apply_mult(im, VIG)
    comp(im, KICK, ((W - KICK.width) // 2, 210))
    E6_TITLE.draw(im, t)
    for (img, y, t0, side, phase) in [(CARD_A, 560, 0.75, -1, 0.0), (CARD_B, 790, 1.1, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45)
        x = (W - img.width) / 2 + side * (1 - p) * 140
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.8) / 1.5 + phase) if t > 2.8 else 1.0
        im2 = img if abs(s - 1) < 1e-3 else img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
        comp(im, im2, (x + img.width / 2 - im2.width / 2, y + img.height / 2 - im2.height / 2), p)
    if t >= 1.9:
        p = eo((t - 1.9) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1065 + (1 - p) * 24), p)
    if t >= 2.3:
        p = eo((t - 2.3) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1175 + (1 - p) * 18), p)
    if t >= 2.9:
        p = backout((t - 2.9) / 0.45); s_ = 0.7 + 0.3 * p + (0.02 * math.sin(2 * math.pi * (t - 3.4) / 1.3) if t > 3.4 else 0)
        fw = FOLLOW.resize((max(1, int(FOLLOW.width * s_)), max(1, int(FOLLOW.height * s_))), Image.BILINEAR)
        comp(im, fw, ((W - fw.width) / 2, 1275 + (FOLLOW.height - fw.height) / 2), clamp((t - 2.9) * 4))
    return im.convert('RGB')

# ------------------------------------------------------------ captions & assembly
def gap_for(k):
    per = [d / len(s[0].split()) for s, d in zip(SENTS[k], T[k]['du'])]
    return float(np.clip(0.8 * min(per), 0.06, 0.3))

def build_caps():
    global CAP
    CAP = {}
    ts = {k: [LEAD + v for v in T[k]['st']] for k in SENTS}
    s = SENTS
    CAP['e1'] = Caption([(LEAD - 0.05, DURS['e1'], [(ts['e1'][0], s['e1'][0][0], WHITE), (ts['e1'][1], s['e1'][1][0], RED)])], gap=gap_for('e1'))
    CAP['e2'] = Caption([(LEAD - 0.05, DURS['e2'], [(ts['e2'][0], s['e2'][0][0], WHITE)])], gap=gap_for('e2'))
    CAP['e3'] = Caption([(LEAD - 0.05, DURS['e3'], [(ts['e3'][0], s['e3'][0][0], WHITE), (ts['e3'][1], s['e3'][1][0], WHITE)])], gap=gap_for('e3'))
    CAP['e4'] = Caption([(LEAD - 0.05, ts['e4'][1] - 0.1, [(ts['e4'][0], s['e4'][0][0], WHITE)]),
                         (ts['e4'][1] - 0.05, DURS['e4'], [(ts['e4'][1], s['e4'][1][0], WHITE), (ts['e4'][2], s['e4'][2][0], WARM)])], gap=gap_for('e4'))
    CAP['e5'] = Caption([(LEAD - 0.05, ts['e5'][1] - 0.1, [(ts['e5'][0], s['e5'][0][0], WHITE)]),
                         (ts['e5'][1] - 0.05, DURS['e5'], [(ts['e5'][1], s['e5'][1][0], WARM)])], gap=gap_for('e5'))

FRAMES = {'e1': frame_e1, 'e2': frame_e2, 'e3': frame_e3, 'e4': frame_e4, 'e5': frame_e5, 'e6': frame_e6}

def encode(name, fn, dur, fade_in=5, fade_out=0):
    n = int(round(dur * FPS))
    tmp, final = f'{OUT}/{name}.part.mp4', f'{OUT}/{name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); t0 = time.time()
    for i in range(n):
        a = np.asarray(fn(i / FPS), dtype=np.uint8)
        k = 1.0
        if fade_in and i < fade_in: k = (i + 1) / (fade_in + 1)
        if fade_out and i >= n - fade_out: k = min(k, (n - i) / (fade_out + 1))
        if k < 1: a = (a.astype(np.float32) * k).astype(np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit('ffmpeg failed ' + name)
    os.replace(tmp, final); print(f'{name}: {n} frames {time.time() - t0:.1f}s', flush=True)

# ------------------------------------------------------------ sound
def make_audio(path, x, starts, total):
    n = int(total * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(12)
    f = np.fft.rfftfreq(n, 1 / SR)
    resp = 1 / (1 + (350 / np.maximum(f, 1)) ** 2) / (1 + (f / 5200) ** 2)
    rain = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * resp, n); rain /= np.abs(rain).max()
    e = starts
    t_open = e['e2'] + LEAD + 0.2
    kp = [(0, 0), (0.4, .28), (e['e2'] - .1, .28), (e['e2'] + .1, .10), (t_open, .10), (t_open + .8, .42), (e['e5'] - .1, .42),
          (e['e5'] + .1, .30), (e['e6'] - .1, .30), (e['e6'] + .1, .26), (total, .26)]
    out = rain * np.interp(t, [a for a, _ in kp], [b for _, b in kp])
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 110.4 * t + 1) + 0.45 * np.sin(2 * np.pi * 164.8 * t + 2))
    out += drone * np.interp(t, [0, 2, e['e4'], e['e6'], total], [0.03, 0.05, 0.07, 0.09, 0.09])
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
    def splash(g=0.12):
        tq = tt(0.18); y = bp(rng.standard_normal(len(tq)), 200, 2500); return y / np.abs(y).max() * np.exp(-tq / 0.05) * g
    def thunder(d=3.0, g=0.6):
        tq = tt(d); y = bp(rng.standard_normal(len(tq)), 25, 260); y /= np.abs(y).max()
        env = np.minimum(1, tq / 0.04) * np.exp(-tq / 0.9) * (1 + 0.5 * np.sin(2 * np.pi * 1.3 * tq))
        crack = bp(rng.standard_normal(len(tq)), 800, 7000) * np.exp(-tq / 0.06); crack /= np.abs(crack).max()
        return (y * env + 0.35 * crack) * g
    def buzz(d):
        tq = tt(d); return np.tanh(2.5 * np.sin(2 * np.pi * 172 * tq)) * np.minimum(1, tq / 0.01) * np.minimum(1, (d - tq) / 0.03) * 0.16
    def hum(d=1.5, g=0.08):
        tq = tt(d); return (np.sin(2 * np.pi * 60 * tq) + 0.5 * np.sin(2 * np.pi * 120 * tq)) * np.minimum(1, tq / 0.02) * np.exp(-tq / 1.2) * g
    def hit(g=0.6):
        tq = tt(2.5); fr = 38 + 52 * np.exp(-tq / 0.25)
        return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tq / 0.9) * 0.6 + np.sin(4 * np.pi * np.cumsum(fr) / SR) * np.exp(-tq / 0.5) * 0.25) * g / 0.6
    sel = e['e1'] + LEAD + T['e1']['st'][1] - 0.1
    add(hit(0.45), sel)
    add(creak(1.1, 220, 140, 0.22), t_open)
    w0 = t_open + 0.6
    for k in range(int((e['e3'] - w0) / 0.42)): add(splash(0.08 + 0.04 * (k > 2)), w0 + k * 0.42)
    for k in range(int(MINS['e3'] / 1.3) + 1): add(creak(0.7, 160, 120, 0.12), e['e3'] + 0.2 + k * 1.3)
    add(thunder(), e['e3'] + LEAD + T['e3']['st'][1] - 0.1)
    st4 = [e['e4'] + LEAD + v for v in T['e4']['st']]
    for i in range(12): add(splash(0.07), st4[0] + 0.2 + (st4[1] + 0.8 - st4[0] - 0.2) * i / 12)
    add(hum(), st4[2] + 0.4)
    tb = e['e5'] + LEAD + 0.25
    add(buzz(0.35), tb); add(buzz(0.35), tb + 0.5)
    add(hit(0.6), e['e6'])
    # narration with ducking
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
    st = np.stack([mix, mix], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------ main
if __name__ == '__main__':
    mode, narr = sys.argv[1], sys.argv[2]
    bounds = [float(v) for v in os.environ.get('BOUNDS', '2.88,7.7,10.89,17.09,20.81').split(',')]
    X, T = analyse(narr, bounds)
    DURS = {k: r30(max(MINS[k], LEAD + T[k]['L'] + TAIL[k])) for k in ORDER}
    print('durs', DURS)
    MULT = M.make_mult(0.55, True); VIG = M.make_mult(0.55, False)
    KICK = kicker(); CHECK = build_check()
    t0 = time.time()
    setup_e1(); setup_e2(); setup_e3(); setup_e4(); setup_e5(); setup_e6(); build_caps()
    print(f'setup {time.time() - t0:.1f}s', flush=True)
    if mode == 'preview':
        st = lambda k, i: LEAD + T[k]['st'][i]
        shots = [('e1', st('e1', 1) + 0.8), ('e2', 1.6), ('e2', DURS['e2'] - 1.2), ('e3', st('e3', 1) + 0.6),
                 ('e4', st('e4', 1) + 0.3), ('e4', st('e4', 2) + 1.2), ('e5', st('e5', 1) + 0.6), ('e6', 4.0)]
        th = []
        for i, (k, tt_) in enumerate(shots):
            t1 = time.time(); im = FRAMES[k](tt_); im.save(f'{OUT}/prev_{i}.png')
            print(f'prev_{i} {k}@{tt_:.2f} {1000 * (time.time() - t1):.0f}ms', flush=True)
            th.append(im.resize((W // 4, H // 4), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 4 * 4, H // 4 * 2))
        for i, im in enumerate(th): sheet.paste(im, ((i % 4) * (W // 4), (i // 4) * (H // 4)))
        sheet.save(f'{OUT}/sheet.png')
    else:
        only = sys.argv[3:] or ORDER
        for idx, k in enumerate(ORDER):
            if k not in only: continue
            encode(k, FRAMES[k], DURS[k], fade_in=5, fade_out=12 if idx == len(ORDER) - 1 else 0)
        starts, acc = {}, 0.0
        for k in ORDER: starts[k] = acc; acc += int(round(DURS[k] * FPS)) / FPS
        make_audio(f'{OUT}/audio.wav', X, starts, acc)
        with open(f'{OUT}/list.txt', 'w') as fl:
            for k in ORDER: fl.write(f"file '{k}.mp4'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video.mp4'], check=True)
        final = f'{OUT}/quem-bate-a-porta-ep2.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final + '.part.mp4'], check=True)
        os.replace(final + '.part.mp4', final)
        print('done', acc)
