#!/usr/bin/env python3
"""Bestiário — "a roleta decide a criatura do seu nome". Um nome por vídeo (~20 s), sem voz.
6 roletas com a porcentagem de cada fatia (elemento, raridade, forma, força, velocidade, magia),
depois o ovo choca e aparece a criatura com o PODER TOTAL. NAME=<nome> python3 roleta.py"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/claude/reino')
import ep1hd as E
import creature as C
import cartas as K
import json

FW, FH, FPS = 1080, 1920, 30
NAME = os.environ.get('NAME', 'Letícia')
TR = C.traits(NAME)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
WHITE, GOLD, DARK = (255, 255, 255), (255, 208, 72), (16, 12, 30)
RC = C.RAR_COL[TR['rarity']]

# ---------------------------------------------------------------- roteiro (s)
# baralho: cada carta é o print de um comentário; NAME é o sorteado (sortear.py)
_dj = os.environ.get('DECK_JSON')
DECK = [tuple(x) for x in json.load(open(_dj))] if _dj else list(K.DEFAULT_DECK)
USE_CARDS = os.environ.get('CARDS', '1') != '0'
if USE_CARDS and NAME not in [n for n, _ in DECK]:
    DECK.insert(len(DECK) // 2, (NAME, NAME))
DRAWN = [n for n, _ in DECK].index(NAME) if USE_CARDS else -1
INTRO = 4.6 if USE_CARDS else 0.0
# fases da intro (s)
I_IN, I_FLIP, I_GATHER, I_SHUF, I_PULL, I_SHOW, I_OUT = 0.0, 1.95, 2.25, 2.65, 3.05, 3.45, 4.25

SPINS = [  # (roleta, rótulo exibido, salt, início, duração da giro, pausa depois)
    ('ELEMENTO', 'ELEMENTO', 'el', INTRO, 2.5, 0.5),
    ('RARIDADE', 'RARIDADE', 'rar', None, 2.7, 0.55),
    ('FORMA', 'FORMA', 'fo', None, 2.0, 0.4),
    ('ATRIB', 'FORÇA', 'f', None, 1.45, 0.3),
    ('ATRIB', 'VELOCIDADE', 'v', None, 1.45, 0.3),
    ('ATRIB', 'MAGIA', 'm', None, 1.45, 0.4),
]
_t = 0.0
SP = []
for w, lab, salt, t0, dur, hold in SPINS:
    t0 = _t if t0 is None else t0
    SP.append(dict(w=w, lab=lab, salt=salt, t0=t0, t1=t0 + dur, t2=t0 + dur + hold))
    _t = t0 + dur + hold
R0 = _t                      # revelação
EGG_IN, EGG_CRACK = R0 + 0.3, R0 + 0.95
COUNT0, COUNT1 = R0 + 1.4, R0 + 2.5
CTA = R0 + 3.9
TEND = CTA + 2.8
XF = 0.4


def spin_res(s):
    return C.spin(NAME, s['w'], s['salt'])


# ---------------------------------------------------------------- fundo pixel (canvas 360x640, 3x)
CW, CH = 360, 640
rnd = random.Random(3)
STARS = [(rnd.randrange(CW), rnd.randrange(0, 470), rnd.uniform(0, 6.28), rnd.uniform(1.5, 4)) for _ in range(90)]


def _bg():
    y = np.linspace(0, 1, CH)[:, None]
    top, bot = np.array((18, 14, 40)), np.array((58, 34, 86))
    img = (top * (1 - y[..., None]) + bot * y[..., None]) * np.ones((CH, CW, 1))
    img = img[:, :, 0, :] if img.ndim == 4 else img
    img = np.broadcast_to(img, (CH, CW, 3)).copy()
    r = random.Random(11)
    # montanhas
    for layer, (col, base, amp) in enumerate((((44, 30, 70), 470, 60), ((32, 22, 54), 520, 40))):
        hts = []
        h = base
        for x in range(CW):
            if x % 24 == 0:
                tgt = base - r.uniform(0, amp)
            h += (tgt - h) * 0.08
            hts.append(int(h))
        for x in range(CW):
            img[hts[x]:, x] = col
    # floresta
    for k in range(40):
        x0 = r.randrange(-10, CW)
        hgt = r.randint(30, 60)
        yb = 560 + r.randint(-6, 10)
        for j in range(hgt):
            w = int((j / hgt) * 9) + 1
            yy = yb - hgt + j
            img[yy:yy + 1, max(0, x0 - w):min(CW, x0 + w)] = (20, 16, 36)
    img[566:, :] = (24, 18, 40)
    for x in range(0, CW, 2):
        img[566 + (x * 7) % 5, x] = (36, 28, 58)
    return img.astype(np.float32)


BG = _bg()


def background(t, glow=0.0):
    img = BG.copy()
    for x, y, ph, f in STARS:
        k = 0.5 + 0.5 * math.sin(t * f + ph)
        img[y, x] = img[y, x] * (1 - k) + np.array((255, 248, 220)) * k
    if glow > 0:
        yy, xx = np.mgrid[0:CH, 0:CW]
        d = np.sqrt((xx - 180) ** 2 + ((yy - 287) * 0.9) ** 2)
        a = (np.clip(1 - d / 150, 0, 1) ** 2 * glow * 0.75)[..., None]
        # bayer pra parecer pixel
        bay = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16
        a = a * (a[..., 0:1] > bay[yy % 4, xx % 4][..., None] * 0.35)
        img = img * (1 - a) + np.array(RC) * a
    if math.sin(t * 2.3) > -0.3:                 # a luz turquesa da floresta de Brasa
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            img[548 + dy, 286 + dx] = (170, 255, 230)
    big = np.repeat(np.repeat(img, 3, 0), 3, 1)
    return big.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- roletas
WR = 322                       # raio na tela
WCX, WCY = 540, 892


def wheel_colors(w):
    items = C.WHEELS[w]
    if w == 'ELEMENTO':
        return [C.TYPES[l][0] for l, _ in items]
    if w == 'RARIDADE':
        return [C.RAR_COL[l] for l, _ in items]
    if w == 'FORMA':
        return [(244, 132, 120), (110, 190, 140), (120, 160, 240), (230, 170, 80), (170, 130, 220)]
    return [tuple(int(a + (b - a) * k / 9) for a, b in zip((70, 60, 110), (255, 200, 70))) for k in range(10)]


def wheel_geom(w):
    items = C.WHEELS[w]
    tot = sum(p for _, p in items)
    out, a = [], 0.0
    for lab, p in items:
        span = 360 * p / tot
        out.append((a, a + span))
        a += span
    return out


def render_wheel(w):
    SS = 2
    R = WR * SS
    pad = 40 * SS
    size = 2 * R + 2 * pad
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size // 2
    d.ellipse((c - R - 18 * SS, c - R - 18 * SS, c + R + 18 * SS, c + R + 18 * SS), fill=(40, 28, 64, 255))
    d.ellipse((c - R - 12 * SS, c - R - 12 * SS, c + R + 12 * SS, c + R + 12 * SS), fill=(250, 236, 200, 255))
    cols = wheel_colors(w)
    geo = wheel_geom(w)
    for (a0, a1), col in zip(geo, cols):
        d.pieslice((c - R, c - R, c + R, c + R), a0, a1, fill=col + (255,), outline=(24, 18, 40, 255), width=3 * SS)
    for k in range(24):                                   # lâmpadas
        ang = math.radians(k * 15)
        x, y = c + (R + 6 * SS) * math.cos(ang), c + (R + 6 * SS) * math.sin(ang)
        d.ellipse((x - 4 * SS, y - 4 * SS, x + 4 * SS, y + 4 * SS), fill=(255, 236, 150, 255))
    im = im.resize((size // SS, size // SS), Image.LANCZOS)
    # rótulos radiais (texto lido do centro pra borda)
    c = im.size[0] // 2
    for (a0, a1), (lab, p) in zip(geo, C.WHEELS[w]):
        mid = (a0 + a1) / 2
        span = a1 - a0
        txt = f'{lab}  {p}%'
        fs = 40 if w != 'ATRIB' else 44
        ft = E.font(fs)
        while ft.getlength(txt) > WR * 0.66 and fs > 22:
            fs -= 2; ft = E.font(fs)
        arc = math.radians(span) * WR * 0.6
        if arc < fs * 0.95:
            fs = max(18, int(arc / 0.95)); ft = E.font(fs)
        tw = int(ft.getlength(txt)) + 16
        th = fs + 18
        lab_im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lab_im)
        ld.text((tw / 2, th / 2), txt, font=ft, fill=(255, 255, 255, 255), anchor='mm', stroke_width=max(3, fs // 10),
                stroke_fill=(24, 18, 40, 255))
        rot = lab_im.rotate(-mid, resample=Image.BICUBIC, expand=True)   # sempre lendo do centro pra borda
        rr = WR * 0.6
        x = c + rr * math.cos(math.radians(mid)) - rot.size[0] / 2
        y = c + rr * math.sin(math.radians(mid)) - rot.size[1] / 2
        im.alpha_composite(rot, (int(x), int(y)))
    return im


WHEEL_IM = {}


def wheel_im(w):
    if w not in WHEEL_IM:
        WHEEL_IM[w] = render_wheel(w)
    return WHEEL_IM[w]


def final_angle(s):
    """Rotação (graus, horário) que põe o meio do resultado (com desvio) embaixo do ponteiro, no topo (270°)."""
    i, lab, p = spin_res(s)
    a0, a1 = wheel_geom(s['w'])[i]
    r = random.Random(C.h32(NAME, 'off' + s['salt']))
    off = (r.random() - 0.5) * 0.6 * (a1 - a0)
    turns = 4 if s['t1'] - s['t0'] > 2 else 3
    start = r.uniform(0, 360)
    return start, 270 - ((a0 + a1) / 2 + off) + 360 * turns + (start // 360 + 1) * 360


def angle_at(s, t):
    start, fin = final_angle(s)
    q = W_clamp((t - s['t0']) / (s['t1'] - s['t0']))
    e = 1 - (1 - q) ** 4
    return start + (fin - start) * e


def W_clamp(x):
    return max(0.0, min(1.0, x))


def current_spin(t):
    for k, s in enumerate(SP):
        if s['t0'] <= t < s['t2']:
            return k, s
    return None, None


# ---------------------------------------------------------------- ovo
def egg_sprite(crack=0):
    base, light, dark, acc, belly, _ = C.TYPES[TR['type']]
    w, h = 22, 28
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((1, 1, w - 2, h - 2), fill=(246, 238, 220, 255))
    r = random.Random(5)
    for k in range(6):
        x, y = r.randint(4, w - 7), r.randint(5, h - 9)
        d.ellipse((x, y, x + 3, y + 2), fill=base + (255,))
    if crack:
        pts = [(3, 12), (7, 9), (10, 13), (13, 9), (16, 13), (19, 10)]
        d.line(pts, fill=(60, 40, 40, 255), width=1)
    a = np.array(im).astype(np.int16)
    op = a[..., 3] > 0
    edge = ~op & (np.roll(op, 1, 0) | np.roll(op, -1, 0) | np.roll(op, 1, 1) | np.roll(op, -1, 1))
    a[edge] = (24, 18, 30, 255)
    sh = op & ~np.roll(op, -1, 1)
    a[sh, :3] = (a[sh, :3] * 0.8)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


EGG = egg_sprite(0)
EGG_C = egg_sprite(1)


# ---------------------------------------------------------------- textos
def chip(d, box, cat, val, pct, col):
    x0, y0, x1, y1 = box
    E.panel(d, box, fill=(26, 20, 48, 235), b=5)
    d.rectangle((x0 + 12, y0 + 14, x0 + 26, y1 - 14), fill=col + (255,))
    d.text((x0 + 42, y0 + 26), cat, font=E.font(32), fill=(200, 196, 220, 255), anchor='lm')
    d.text((x0 + 42, y0 + 62), val, font=E.font(46), fill=WHITE + (255,), anchor='lm')
    d.text((x1 - 18, y0 + 62), f'{pct}%', font=E.font(40), fill=GOLD + (255,), anchor='rm')


CHIP_BOX = []
for k in range(6):
    col, row = k % 2, k // 2
    x0 = 92 + col * 452
    y0 = 1236 + row * 100
    CHIP_BOX.append((x0, y0, x0 + 436, y0 + 88))


def chip_info(k):
    s = SP[k]
    i, lab, p = spin_res(s)
    col = wheel_colors(s['w'])[i]
    return s['lab'], lab if s['w'] != 'ATRIB' else f'{lab} / 10', p, col


def layer(t):
    im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if t < I_SHOW + 0.35 and USE_CARDS:
        E.draw_line(d, FW / 2, 214, [('QUEM VAI PRA ROLETA?', WHITE)], 96)
        E.draw_line(d, FW / 2, 330, [('CADA COMENTÁRIO VIROU UMA CARTA', GOLD)], 54)
    elif t < CTA:
        E.draw_line(d, FW / 2, 222, [('QUAL CRIATURA É O SEU NOME?', (220, 214, 240))], 60)
        E.draw_line(d, FW / 2, 300, [(NAME.upper(), GOLD)], 170)
    else:
        E.draw_line(d, FW / 2, 196, [('COMENTA SEU NOME', WHITE)], 104)
        E.draw_line(d, FW / 2, 306, [('PRA ENTRAR NO BARALHO', GOLD)], 72)
        E.draw_line(d, FW / 2, 390, [('SUA CRIATURA PODE IR PRO ', (96, 226, 214)), ('BRASA', (255, 150, 40))], 50)
    k, s = current_spin(t)
    if s is not None:
        E.draw_line(d, FW / 2, 446, [(f"{s['lab']}", WHITE)], 74)
        d.text((FW - 110, 470), f'{k + 1}/6', font=E.font(40), fill=(200, 196, 220, 255), anchor='rm')
        if s['w'] == 'RARIDADE' and t >= s['t1'] and TR['lvl'] >= 3 and t < s['t2']:   # pico do vídeo
            q = W_clamp((t - s['t1']) / 0.12)
            sz = int(150 + 40 * (1 - q))
            E.draw_line(d, FW / 2, WCY - sz * 0.27, [(TR['rarity'] + '!', RC)], sz, stroke=12)
    # fichas
    for j in range(6):
        if t >= SP[j]['t1'] + 0.25 and t < (CTA if True else 99):
            cat, val, p, col = chip_info(j)
            q = W_clamp((t - SP[j]['t1'] - 0.25) / 0.15)
            if q < 1:
                continue
            chip(d, CHIP_BOX[j], cat, val, p, col)
    if t >= CTA:
        for j in range(6):
            cat, val, p, col = chip_info(j)
            chip(d, CHIP_BOX[j], cat, val, p, col)
    # revelação
    if t >= EGG_CRACK + 0.15:
        E.draw_line(d, FW / 2, 470, [(TR['species'], RC)], 96)
        E.draw_line(d, FW / 2, 572, [('VIVE NA FLORESTA DE BRASA', (96, 226, 214))], 44)
    if t >= COUNT0:
        q = W_clamp((t - COUNT0) / (COUNT1 - COUNT0))
        val = int(round(TR['total'] * (1 - (1 - q) ** 2)))
        E.panel(d, (250, 1112, 830, 1214), fill=(26, 20, 48, 235), b=6)
        d.text((290, 1163), 'PODER TOTAL', font=E.font(52), fill=WHITE + (255,), anchor='lm')
        d.text((790, 1163), f'{val}', font=E.font(86), fill=(RC if q >= 1 else GOLD) + (255,), anchor='rm')
    return im


# ---------------------------------------------------------------- intro: cartas
CWD, CHT = 410, 118
GRID = [(285 + (i % 2) * 490, 600 + (i // 2) * 136) for i in range(12)]
STACK = (540, 930)
_FACES = {}


def face(i, scale=1.0):
    key = (i, round(scale, 2))
    if key not in _FACES:
        n, c = DECK[i]
        _FACES[key] = K.card_face(n, c, int(CWD * scale), int(CHT * scale))
    return _FACES[key]


def ease(q):
    q = W_clamp(q)
    return 1 - (1 - q) ** 3


def put(base, im, cx, cy, sx=1.0, rot=0.0, alpha=1.0):
    if sx < 0.999:
        im = im.resize((max(2, int(im.size[0] * sx)), im.size[1]), Image.BILINEAR)
    if abs(rot) > 0.3:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy(); a = im.getchannel('A').point(lambda v: int(v * alpha)); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)))


def intro(base, t):
    n = len(DECK)
    r = random.Random(21)
    jit = [(r.uniform(-14, 14), r.uniform(-10, 10), r.uniform(-6, 6)) for _ in range(n)]
    order = sorted(range(n), key=lambda i: (i == DRAWN, i))          # o sorteado por cima no fim
    for i in order:
        gx, gy = GRID[i % len(GRID)]
        x, y, rot, sx, show_face, alpha = gx, gy, 0.0, 1.0, True, 1.0
        if t < I_FLIP:                                                   # entram voando
            q = ease((t - I_IN - 0.035 * i) / 0.45)
            y = gy + (1 - q) * 900
            rot = (1 - q) * jit[i][2] * 3
        elif t < I_GATHER:                                               # viram
            q = W_clamp((t - I_FLIP - 0.012 * i) / 0.17)                # viram em cascata
            sx = abs(1 - 2 * q); show_face = q < 0.5
        else:
            show_face = False
            sxx, syy = STACK[0] + jit[i][0], STACK[1] + jit[i][1]
            if t < I_SHUF:                                               # juntam no monte
                q = ease((t - I_GATHER) / (I_SHUF - I_GATHER))
                x, y = gx + (sxx - gx) * q, gy + (syy - gy) * q
                rot = jit[i][2] * q
            elif t < I_PULL:                                             # embaralham
                q = (t - I_SHUF) / (I_PULL - I_SHUF)
                side = 1 if i % 2 else -1
                off = math.sin(q * math.pi * 2) * 230 * side * (1 if (i // 2) % 2 else 0.6)
                x, y, rot = sxx + off, syy, jit[i][2]
            else:
                x, y, rot = sxx, syy, jit[i][2]
                if i == DRAWN:
                    continue
                if t >= I_OUT:
                    alpha = 1 - W_clamp((t - I_OUT) / 0.3)
        put(base, face(i) if show_face else K.card_back(), x, y, sx, rot, alpha)
    if t >= I_PULL:                                                      # a sorteada sobe e vira
        sxx, syy = STACK[0] + jit[DRAWN][0], STACK[1] + jit[DRAWN][1]
        q = ease((t - I_PULL) / (I_SHOW - I_PULL))
        sc = 1 + 0.55 * q
        x, y = sxx + (540 - sxx) * q, syy + (820 - syy) * q
        alpha = 1 - W_clamp((t - I_OUT) / 0.3)
        if t < I_SHOW:
            put(base, K.card_back().resize((int(CWD * sc), int(CHT * sc)), Image.BILINEAR), x, y, 1, jit[DRAWN][2] * (1 - q), alpha)
        else:
            qf = W_clamp((t - I_SHOW) / 0.3)
            sx = abs(1 - 2 * qf)
            im = K.card_back().resize((int(CWD * 1.55), int(CHT * 1.55)), Image.BILINEAR) if qf < 0.5 else face(DRAWN, 1.55)
            if qf >= 1:
                d = ImageDraw.Draw(base)
                rr = random.Random(int(t * 14))
                for k in range(12):
                    px_, py_ = 540 + rr.uniform(-380, 380), 820 + rr.uniform(-170, 170)
                    s_ = rr.choice((6, 9, 12))
                    d.rectangle((px_ - s_, py_ - 2, px_ + s_, py_ + 2), fill=(255, 214, 72, int(255 * alpha)))
                    d.rectangle((px_ - 2, py_ - s_, px_ + 2, py_ + s_), fill=(255, 214, 72, int(255 * alpha)))
            put(base, im, x, y, sx, 0, alpha)


# ---------------------------------------------------------------- quadro
def creature_im(t):
    fr = int(t / 0.4) % 2
    a = C.draw(NAME, fr)
    return Image.fromarray(a).resize((440, 440), Image.NEAREST)


def frame(t):
    glow = 0.0
    if t >= EGG_CRACK:
        glow = min(1, (t - EGG_CRACK) / 0.3)
    base = Image.fromarray(background(t, glow)).convert('RGBA')
    if USE_CARDS and t < INTRO:
        intro(base, t)
    k, s = current_spin(t)
    if s is not None:
        wi = wheel_im(s['w'])
        sc = 1.0
        if t < s['t0'] + 0.14 and k > 0:
            sc = 0.6 + 0.4 * (t - s['t0']) / 0.14
        ang = angle_at(s, t)
        rot = wi.rotate(-ang, resample=Image.BICUBIC)
        if sc != 1:
            sz = int(rot.size[0] * sc)
            rot = rot.resize((sz, sz), Image.BILINEAR)
        base.alpha_composite(rot, (int(WCX - rot.size[0] / 2), int(WCY - rot.size[1] / 2)))
        d = ImageDraw.Draw(base)
        # cubo central
        d.ellipse((WCX - 70, WCY - 70, WCX + 70, WCY + 70), fill=(250, 236, 200, 255))
        d.ellipse((WCX - 62, WCY - 62, WCX + 62, WCY + 62), fill=(40, 28, 64, 255))
        if t >= s['t1']:
            i, lab, p = spin_res(s)
            q = W_clamp((t - s['t1']) / 0.12)
            ft = E.font(int(52 if len(lab) > 6 else 64))
            d.text((WCX, WCY - 12), lab, font=ft, fill=WHITE + (255,), anchor='mm', stroke_width=4, stroke_fill=(24, 18, 40, 255))
            d.text((WCX, WCY + 32), f'{p}%', font=E.font(40), fill=GOLD + (255,), anchor='mm')
            if q < 1 or (t - s['t1']) % 0.24 < 0.12:
                ang_m = math.radians(270)
                d.ellipse((WCX - WR - 22, WCY - WR - 22, WCX + WR + 22, WCY + WR + 22), outline=(255, 255, 255, 255), width=6)
        else:
            d.text((WCX, WCY), '?', font=E.font(90), fill=GOLD + (255,), anchor='mm')
        # ponteiro
        px, py = WCX, WCY - WR - 30
        d.polygon([(px - 34, py - 26), (px + 34, py - 26), (px, py + 34)], fill=(24, 18, 40, 255))
        d.polygon([(px - 24, py - 18), (px + 24, py - 18), (px, py + 22)], fill=(255, 90, 80, 255))
    if t >= R0:
        d = ImageDraw.Draw(base)
        if t < EGG_CRACK:
            q = W_clamp((t - R0) / 0.3)
            y = -200 + (880 - -200) * (1 - (1 - q) ** 3)
            shake = math.sin(t * 60) * 10 * W_clamp((t - EGG_IN) / 0.3) if t >= EGG_IN else 0
            eg = (EGG_C if t > EGG_CRACK - 0.25 else EGG).resize((264, 336), Image.NEAREST).rotate(shake, Image.NEAREST, expand=True)
            base.alpha_composite(eg, (int(WCX - eg.size[0] / 2), int(y - eg.size[1] / 2)))
        else:
            q = W_clamp((t - EGG_CRACK) / 0.16)
            cr = creature_im(t)
            sz = int(440 * (0.4 + 0.6 * q)) if q < 1 else 440
            if sz != 440:
                cr = cr.resize((sz, sz), Image.NEAREST)
            base.alpha_composite(cr, (int(WCX - sz / 2), int(WCY - sz / 2 - 10)))
            r = random.Random(4)
            for k in range(14):                          # cascas
                a = t - EGG_CRACK
                if a < 0.7:
                    ang = r.uniform(0, 6.28); sp = r.uniform(400, 900)
                    x = WCX + math.cos(ang) * sp * a
                    y = WCY + math.sin(ang) * sp * a + 900 * a * a
                    d.rectangle((x - 9, y - 9, x + 9, y + 9), fill=(246, 238, 220, 255), outline=(24, 18, 30, 255), width=3)
            if t - EGG_CRACK < 0.12:
                fl = Image.new('RGBA', (FW, FH), (255, 255, 255, int(255 * (1 - (t - EGG_CRACK) / 0.12))))
                base.alpha_composite(fl)
            if TR['lvl'] >= 3:                           # brilho de épico/lendário
                r2 = random.Random(int(t * 12))
                for k in range(10):
                    x = WCX + r2.uniform(-260, 260); y = WCY + r2.uniform(-260, 220)
                    s_ = r2.choice((6, 9, 12))
                    d.rectangle((x - s_, y - 2, x + s_, y + 2), fill=RC + (255,))
                    d.rectangle((x - 2, y - s_, x + 2, y + s_), fill=RC + (255,))
    base.alpha_composite(layer(t))
    return np.array(base.convert('RGB'))


# ---------------------------------------------------------------- áudio
SR = E.SR


def audio(path):
    n = int((TEND + 0.5) * SR)
    s = np.zeros(n)

    def note(t, m, d=0.12, g=0.06, duty=0.25, wave_='sq'):
        nn = int(d * SR)
        osc = E.sq(E.midi(m), nn, duty) if wave_ == 'sq' else E.tri(E.midi(m), nn)
        E.add(s, t, osc * E.adsr(nn, a=0.004, dec=0.05, sus=0.4, r=0.03), g)

    # trilha: lá menor, 128 bpm
    beat = 60 / 128
    prog = [45, 41, 48, 43]
    arp = [0, 3, 7, 12, 7, 3]
    t = 0.0
    k = 0
    while t < TEND + 0.4:
        root = prog[(k // 8) % 4]
        if k % 2 == 0:
            note(t, root, d=beat * 0.9, g=0.07, wave_='tri')
        note(t, root + 24 + arp[k % 6] + (0 if (k // 8) % 4 != 2 else 0), d=beat * 0.4, g=0.022, duty=0.125)
        nn = int(0.02 * SR)
        E.add(s, t + beat / 2, E.noise(nn, k) * np.exp(-np.arange(nn) / SR * 200), 0.02)
        t += beat / 2
        k += 1
    if USE_CARDS:                                       # cartas
        for i in range(len(DECK)):
            nn = int(0.03 * SR)
            E.add(s, I_IN + 0.035 * i + 0.3, E.lp(E.noise(nn, 300 + i), 0.35) * np.exp(-np.arange(nn) / SR * 90), 0.12)
        for tt in (I_FLIP, I_SHOW):
            nn = int(0.12 * SR)
            E.add(s, tt, E.lp(E.noise(nn, int(tt * 100)), 0.3) * np.exp(-np.arange(nn) / SR * 30), 0.3)
        nn = int(0.35 * SR)
        E.add(s, I_GATHER, E.lp(E.noise(nn, 9), 0.12) * np.sin(np.pi * np.arange(nn) / nn), 0.35)
        for j in range(22):
            nn = int(0.015 * SR)
            E.add(s, I_SHUF + j * (I_PULL - I_SHUF) / 22, E.noise(nn, 400 + j) * np.exp(-np.arange(nn) / SR * 250), 0.16)
        for j, m in enumerate([72, 76, 79, 84, 88]):
            note(I_SHOW + 0.15 + j * 0.06, m, d=0.18, g=0.08)
    # tiques das fatias
    for sp in SP:
        geo = wheel_geom(sp['w'])
        bounds = [a0 for a0, _ in geo]
        prev = None
        tt = sp['t0']
        while tt < sp['t1']:
            a = angle_at(sp, tt)
            idx = sum(1 for b in bounds if ((270 - a) % 360) >= b)
            if prev is not None and idx != prev:
                nn = int(0.012 * SR)
                E.add(s, tt, E.sq(2200, nn, 0.5) * np.exp(-np.arange(nn) / SR * 300), 0.05)
            prev = idx
            tt += 1 / 600
        i, lab, p = spin_res(sp)
        rare = p <= 9
        for j, m in enumerate([79, 84] if not rare else [79, 83, 86, 91, 95]):
            note(sp['t1'] + j * 0.06, m, d=0.14, g=0.07 if not rare else 0.08)
        if sp['w'] == 'RARIDADE' and TR['lvl'] >= 3:
            for j, m in enumerate([72, 76, 79, 84, 88, 91, 96]):
                note(sp['t1'] + 0.3 + j * 0.07, m, d=0.2, g=0.07)
    # ovo
    for j in range(8):
        nn = int(0.03 * SR)
        E.add(s, EGG_IN + j * 0.075, E.lp(E.noise(nn, 50 + j), 0.2) * np.exp(-np.arange(nn) / SR * 60), 0.25)
    nn = int(0.25 * SR)
    E.add(s, EGG_CRACK, E.noise(nn, 77) * np.exp(-np.arange(nn) / SR * 18), 0.35)
    for j, m in enumerate([67, 71, 74, 79, 83, 86, 91]):
        note(EGG_CRACK + 0.05 + j * 0.06, m, d=0.22, g=0.08)
    # contagem do poder
    steps = 14
    for j in range(steps):
        note(COUNT0 + j * (COUNT1 - COUNT0) / steps, 72 + j, d=0.04, g=0.04, duty=0.5)
    for j, m in enumerate([84, 88, 91, 96]):
        note(COUNT1 + j * 0.05, m, d=0.25, g=0.08)
    note(CTA, 88, d=0.08, g=0.05); note(CTA + 0.12, 91, d=0.12, g=0.05)
    mix = s[:int(TEND * SR)]
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


def main():
    slug = C.norm(NAME).replace(' ', '-')
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            Image.fromarray(frame(float(v))).save(os.path.join(OUT, f'r_{slug}_{float(v):05.2f}.png'))
        return
    wav = os.path.join(OUT, f'r_{slug}.wav')
    audio(wav)
    out = os.path.join(OUT, f'bestiario-{slug}.mp4')
    nfr = int(round(TEND * FPS))
    f0 = frame(0.0).astype(np.float32)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
                          '-af', 'loudnorm=I=-14.5:TP=-2:LRA=11,alimiter=limit=0.7:level=false',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(nfr):
        t = i / FPS
        f = frame(t)
        if t > TEND - XF:
            k = (t - (TEND - XF)) / XF
            f = (f.astype(np.float32) * (1 - k) + f0 * k).astype(np.uint8)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    print(out, round(TEND, 2))


if __name__ == '__main__':
    main()
