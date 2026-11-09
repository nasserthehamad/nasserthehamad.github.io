#!/usr/bin/env python3
"""Brasa — Ep. 1 "A Fundação" (versão detalhada, canvas 360x640). Pixel art + texto + chiptune, sem narração.
Uso: N=7 python3 ep1.py            (vídeo completo)
     STILLS=0.5,4,7 python3 ep1.py (só quadros de conferência)
"""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from world2 import *

HERE = os.path.dirname(os.path.abspath(__file__))
FW, FH, FPS = 1080, 1920, 30
N = int(os.environ.get('N', '7'))
NAME = os.environ.get('NAME', 'BRASA')
OUTDIR = os.environ.get('OUTDIR', os.path.join(HERE, 'out'))
os.makedirs(OUTDIR, exist_ok=True)
JERSEY = os.path.join(HERE, 'fonts', 'JerseyFix.ttf')

T2, T3, T4, T5, T6, T7, TEND = 2.7, 6.1, 8.9, 12.4, 15.4, 19.6, 23.6
XF = 0.5

WHITE, GOLD, TEAL, ORANGE, GREY = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 170, 80), (190, 186, 210)


def tod(t):
    if t < T3:
        return 0.0
    if t < T4:
        return 0.55 * (t - T3) / (T4 - T3)
    if t < T5:
        return 0.9 + 0.35 * (t - T4) / (T5 - T4)
    if t < T6:
        return 1.25 + 0.75 * (t - T5) / (T6 - T5)
    return 2.0


# ---------------------------------------------------------------- moradores no tempo
POS = ring_positions(N)
TAG = max(range(N), key=lambda i: (POS[i][1], -abs(POS[i][0] - 180)))
STEP = min(0.42, 2.3 / max(N - 1, 1))
START = [T2 + 0.3 + STEP * i for i in range(N)]
WALK = 1.0
ARRIVE = [s + WALK for s in START]
ENTRY = [(180 + (i % 3 - 1) * 6, 672) if i % 2 == 0 else (-16, 386) for i in range(N)]
QTIMES = [T4 + 1.95 + 0.14 * k for k in range(N)]
TAG_T = T5 + 0.65
MYST_T = T6 + 0.9
BANG_T = [MYST_T + 0.45 + 0.09 * k for k in range(N)]


def vstate(i, t):
    tx, ty = POS[i]
    s = START[i]
    if t < s:
        return None
    p = (t - s) / WALK
    if p < 1:
        ex, ey = ENTRY[i]
        return ex + (tx - ex) * p, ey + (ty - ey) * p, 1 + int((t - s) / 0.12) % 2
    if i == TAG and T5 + 0.2 <= t < T6:
        q = clamp((t - T5 - 0.2) / 0.5)
        return tx, ty + 30 * q, (1 + int(t / 0.12) % 2) if q < 1 else 0
    if i == TAG and t >= T6:
        return tx, ty + 22, 0
    return tx, ty, 0


# ---------------------------------------------------------------- cena (canvas)
FLAG = {}
for _r_, _cols in {2: (10,), 3: (9, 10), 4: (9, 10, 11), 5: (8, 9, 10, 11), 6: (8, 9, 10, 11, 12), 7: (7, 8, 9, 10, 11, 12),
                   8: (7, 8, 9, 10, 11, 12), 9: (8, 9, 10, 11)}.items():
    for _c in _cols:
        FLAG[(_c, _r_)] = (255, 236, 140) if (_r_ >= 6 and 9 <= _c <= 10) else (255, 160, 50)
_r = random.Random(21)
SHIM = [(_r.randrange(W), _r.randrange(280, 295), _r.uniform(10, 22), _r.randint(3, 6)) for _ in range(34)]
FLIES = [(_r.uniform(20, 340), _r.uniform(304, 480), _r.random() * 6.28, _r.uniform(1.5, 3)) for _ in range(22)]


def myst_on(t):
    if t < MYST_T:
        return 0.0
    for a, b in [(17.55, 17.68), (20.95, 21.15), (22.4, 22.5)]:
        if a <= t < b:
            return 0.0
    return clamp((t - MYST_T) / 0.25)


def scene(t):
    td = tod(t)
    img = LAND.copy()
    # brilho do rio
    for x0, y, sp, ln in SHIM:
        x = int(x0 + t * sp) % W
        for k in range(ln):
            xk = (x + k) % W
            if not (260 <= xk <= 290):
                img[y, xk] = (170, 214, 246) if k else (210, 236, 252)
    # bandeira subindo
    if t >= T3 + 0.2:
        top = int(round(lerp(364, 318, ease((t - T3 - 0.2) / 1.2))))
        for c_ in range(20):
            dy = int(round(math.sin(t * 7 - c_ * 0.45) * 1.4 * min(1, c_ / 6)))
            for r_ in range(12):
                col = FLAG.get((c_, r_), (178, 46, 42))
                wave = math.sin(t * 7 - c_ * 0.45 + 1.2)
                if wave > 0.55:
                    col = shade(col, 1.12)
                elif wave < -0.55:
                    col = shade(col, 0.82)
                if r_ in (0, 11):
                    col = shade(col, 0.78)
                img[top + r_ + dy, 154 + c_] = col
    # fumaça
    fire_on = t >= T4
    if fire_on:
        smoke(img, t)
    # moradores (ordem de profundidade)
    vs = []
    for i in range(N):
        st = vstate(i, t)
        if st:
            vs.append((st[1], i, st))
    for _, i, (x, y, fr) in sorted(vs):
        bob = 1 if (fr == 0 and math.sin(t * 2.2 + i * 1.7) > 0.93) else 0
        ground_shadow(img, x, y)
        blit(img, sprite(i, fr), x, y - bob)
    # céu
    s = sky(td, t)
    if t < T4:
        birds(s, t)
    # luz
    tint = keyinterp(TINT, td)
    tm = np.broadcast_to(tint, (H, W, 3)).copy()
    if fire_on:
        nfl = clamp((td - 0.6) / 0.9)
        lv = (light_level(t) * nfl)[..., None]
        tm = tm * (1 - lv) + np.array((1.06, 0.84, 0.66)) * lv
    mo = myst_on(t)
    if mo > 0:
        lv2 = (MYST_LV * mo)[..., None]
        tm = tm * (1 - lv2) + np.array((0.55, 1.0, 0.9)) * lv2
    out = np.where(LMASK[..., None], img * tm, s)
    # emissivos
    if fire_on:
        fire(out, t, scale=ease((t - T4) / 0.3))
    if td > 1.5:
        nf = clamp((td - 1.5) / 0.4)
        for fx, fy, ph, f in FLIES:
            if math.sin(t * f + ph) > 0.2:
                x = int(fx + 4 * math.sin(t * 0.7 + ph))
                y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
                out[y, x] = out[y, x] * (1 - nf) + np.array((226, 255, 140)) * nf
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    out[y + dy, x + dx] = out[y + dy, x + dx] * (1 - 0.35 * nf) + np.array((180, 230, 100)) * 0.35 * nf
    if mo > 0:
        mx, my = MYST
        core = np.array((200, 255, 230))
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            out[my + dy, mx + dx] = out[my + dy, mx + dx] * (1 - mo) + core * mo
        for dx, dy in ((-1, 0), (2, 0), (-1, 1), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)):
            out[my + dy, mx + dx] = out[my + dy, mx + dx] * (1 - 0.6 * mo) + np.array((110, 220, 190)) * 0.6 * mo
    # plantas-fantasma
    if T6 <= t < T7:
        for k in range(N):
            if BANG_T[k] <= t < BANG_T[k] + 1.6:
                x, y, _ = vstate(k, t)
                qmark(out, int(round(x)) - 3, int(round(y)) - 40, bang=True)
    # ? sobre as cabeças
    if T4 <= t < T6:
        for k in range(N):
            if t >= QTIMES[k] and not (k == TAG and t >= TAG_T):
                st = vstate(k, t)
                x, y = int(round(st[0])), int(round(st[1]))
                qmark(out, x - 3, y - 40)
    return out, td


def shot(t):
    if T3 <= t < T4:
        return 'wide'
    if T4 <= t < T6:
        return 'close'
    return 'medium'


SHOTS = {'wide': (0, 0, 3), 'medium': (44, 80, 4), 'close': (72, 208, 5)}   # x0, y0, escala


def camera(c, sh):
    c8 = np.clip(c, 0, 255).astype(np.uint8)
    x0, y0, s = SHOTS[sh]
    return c8[y0:y0 + FH // s, x0:x0 + FW // s].repeat(s, 0).repeat(s, 1)


def to_full(cx, cy, sh):
    x0, y0, s = SHOTS[sh]
    return (cx - x0) * s, (cy - y0) * s


# ---------------------------------------------------------------- textos (alta resolução)
_fc = {}


def font(size):
    size = int(size)
    if size not in _fc:
        _fc[size] = ImageFont.truetype(JERSEY, size)
    return _fc[size]


def fit(segs, size, maxw=990):
    while sum(font(size).getlength(s) for s, _ in segs) > maxw and size > 40:
        size -= 4
    return size


def draw_line(d, cx, ycap, segs, size, stroke=None):
    """ycap = topo das maiúsculas."""
    size = fit(segs, size)
    ft = font(size)
    stroke = stroke or max(5, size // 17)
    sh = stroke + max(4, size // 30)
    total = sum(ft.getlength(s) for s, _ in segs)
    y = ycap - 0.267 * size
    for pass_ in (0, 1):
        x = cx - total / 2
        for s, c in segs:
            if pass_ == 0:
                d.text((x, y + sh), s, font=ft, fill=(16, 12, 30, 255), stroke_width=stroke, stroke_fill=(16, 12, 30, 255))
            else:
                d.text((x, y), s, font=ft, fill=c + (255,), stroke_width=stroke, stroke_fill=(24, 18, 44, 255))
            x += ft.getlength(s)
    return size


def panel(d, box, fill=(26, 20, 48, 230), border=(250, 236, 200, 255), b=6):
    x0, y0, x1, y1 = [int(v) for v in box]
    d.rectangle((x0 + b, y0, x1 - b, y1), fill=border)
    d.rectangle((x0, y0 + b, x1, y1 - b), fill=border)
    d.rectangle((x0 + b, y0 + b, x1 - b, y1 - b), fill=fill)


CAPS = [
    (0, T2, 300, [(0.0, [('ESTE PERFIL TEM', WHITE)], 150), (0.25, [(f'{N} SEGUIDORES.', GOLD)], 200)]),
    (T2, T3, 300, [(T2, [('AQUI, CADA SEGUIDOR', WHITE)], 150),
                   (T2 + 0.45, [('VIRA ', WHITE), ('MORADOR.', GOLD)], 180)]),
    (T3, T4, 270, [(T3, [('BEM-VINDOS A', WHITE)], 130), (T3 + 0.4, [(NAME, GOLD)], 300),
                   (T3 + 1.1, [('UM REINO QUE CRESCE A CADA SEGUIDOR', WHITE)], 74)]),
    (T4, T4 + 1.8, 300, [(T4, [('POR ENQUANTO,', WHITE)], 150), (T4 + 0.45, [('É SÓ UMA FOGUEIRA…', WHITE)], 150)]),
    (T4 + 1.8, T5, 300, [(T4 + 1.8, [(f'…E {N} MORADORES', WHITE)], 150), (T4 + 2.2, [('SEM NOME.', GOLD)], 200)]),
    (T5, T6, 300, [(T5, [('SÓ GANHA NOME', WHITE)], 150), (T5 + 0.45, [('QUEM SE APRESENTA.', GOLD)], 170)]),
    (T6, T7, 270, [(T6, [('E ALÉM DA PONTE…', WHITE)], 140), (MYST_T, [('ALGUÉM ACENDEU', GOLD)], 170),
                   (MYST_T, [('UMA LUZ.', GOLD)], 170)]),
    (T7, T7 + 2.1, 270, [(T7, [('COMENTA SEU NOME', WHITE)], 150),
                         (T7 + 0.4, [('E SUA FUNÇÃO.', GOLD)], 170)]),
    (T7 + 2.1, TEND + 1, 270, [(T7 + 2.1, [('OS PRIMEIROS VIRAM', WHITE)], 150),
                               (T7 + 2.5, [('FUNDADORES.', GOLD)], 210)]),
]
COUNT_T = (T2 + 0.6, T3)
EX_T = T7 + 0.8


def overlay_state(t):
    st = []
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    if COUNT_T[0] <= t < COUNT_T[1]:
        st.append(('count', sum(1 for x in ARRIVE if t >= x)))
    if TAG_T <= t < T6:
        x, y, _ = vstate(TAG, t)
        st.append(('tag', round(x, 1), round(y, 1), int((t - TAG_T) / 0.35) % 2))
    if t >= EX_T:
        st.append(('ex',))
    return tuple(st)


_ov = {}


def overlay(state):
    if state in _ov:
        return _ov[state]
    im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for item in state:
        kind = item[0]
        if kind == 'cap':
            _, ci, nvis = item
            a, b, y, lines = CAPS[ci]
            for k, (ta, segs, size) in enumerate(lines):
                sz = fit(segs, size)
                if k > 0 and any(ch in 'ÁÉÍÓÚÂÊÔÃÕ' for s_, _ in segs for ch in s_):
                    y += 0.17 * sz
                if k < nvis:
                    draw_line(d, FW / 2, y, segs, size)
                y += 0.54 * sz + 0.24 * sz + 10
        elif kind == 'count':
            n = item[1]
            txt = [('MORADORES: ', WHITE), (str(n), GOLD)]
            ft = font(86)
            w = sum(ft.getlength(s) for s, _ in txt)
            panel(d, (FW / 2 - w / 2 - 36, 690, FW / 2 + w / 2 + 36, 800))
            draw_line(d, FW / 2, 722, txt, 86, stroke=3)
        elif kind == 'tag':
            _, vx, vy, blink = item
            X, Y = to_full(vx, vy - 25, 'close')
            l1 = [('SEU NOME', GOLD), ('_' if blink == 0 else ' ', WHITE)]
            ft1, ft2 = font(84), font(58)
            w = max(ft1.getlength('SEU NOME_'), ft2.getlength('SUA FUNÇÃO')) + 70
            bx0, by1 = X - 40, Y - 40
            by0 = by1 - 180
            panel(d, (bx0, by0, bx0 + w, by1))
            d.polygon([(X - 6, by1 - 2), (X + 42, by1 - 2), (X, by1 + 34)], fill=(250, 236, 200, 255))
            d.polygon([(X + 2, by1 - 6), (X + 30, by1 - 6), (X + 2, by1 + 18)], fill=(26, 20, 48, 230))
            x = bx0 + 35
            for s, c in l1:
                d.text((x, by0 + 32 - 0.267 * 84), s, font=ft1, fill=c + (255,))
                x += ft1.getlength(s)
            d.text((bx0 + 35, by0 + 114 - 0.267 * 58), 'SUA FUNÇÃO', font=ft2, fill=(210, 206, 230, 255))
        elif kind in ('labA', 'labB'):
            key = 'A' if kind == 'labA' else 'B'
            name, col, (cx, cy) = (('TAVERNA', TEAL, (235, 830)) if key == 'A' else ('MURALHA', ORANGE, (740, 990)))
            ft = font(84)
            w = 92 + 22 + ft.getlength(name) + 40
            x0 = cx - w / 2
            panel(d, (x0, cy - 58, x0 + w, cy + 58))
            d.rectangle((x0 + 18, cy - 40, x0 + 18 + 82, cy + 40), fill=col + (255,))
            d.text((x0 + 18 + 41 - ft.getlength(key) / 2, cy - 23 - 0.267 * 84), key, font=ft, fill=(26, 20, 48, 255))
            d.text((x0 + 18 + 82 + 22, cy - 23 - 0.267 * 84), name, font=ft, fill=(255, 255, 255, 255))
        elif kind == 'ex':
            ft1, ft2 = font(56), font(92)
            segs = [('Lia', WHITE), (', ', GREY), ('ferreira', GOLD)]
            w = max(sum(ft2.getlength(s) for s, _ in segs), ft1.getlength('EXEMPLO DE COMENTÁRIO:')) + 80
            x0, y0 = FW / 2 - w / 2, 580
            panel(d, (x0, y0, x0 + w, y0 + 190), fill=(26, 20, 48, 235))
            d.text((x0 + 40, y0 + 30 - 0.267 * 56), 'EXEMPLO DE COMENTÁRIO:', font=ft1, fill=GREY + (255,))
            x = x0 + 40
            for s, c in segs:
                d.text((x, y0 + 100 - 0.267 * 92), s, font=ft2, fill=c + (255,))
                x += ft2.getlength(s)
    arr = np.array(im)
    a = arr[..., 3]
    ys, xs = np.nonzero(a)
    if len(ys):
        bb = (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)
        y0, y1, x0, x1 = bb
        res = (bb, arr[y0:y1, x0:x1, :3].astype(np.float32), (arr[y0:y1, x0:x1, 3:4] / 255.0).astype(np.float32))
    else:
        res = None
    _ov[state] = res
    return res


def frame(t):
    c, td = scene(t)
    sh = shot(t)
    f = camera(c, sh)
    ov = overlay(overlay_state(t))
    if ov:
        (y0, y1, x0, x1), rgb, a = ov
        reg = f[y0:y1, x0:x1].astype(np.float32)
        f[y0:y1, x0:x1] = (reg * (1 - a) + rgb * a).astype(np.uint8)
    return f


# ---------------------------------------------------------------- áudio
SR = 44100


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def adsr(n, a=0.004, dec=0.09, sus=0.65, r=0.03):
    tt = np.arange(n) / SR
    e = np.minimum(1, tt / a) * (sus + (1 - sus) * np.exp(-tt / dec))
    return e * np.clip((n / SR - tt) / r, 0, 1)


def sq(f, n, duty=0.5, vib=0.0):
    tt = np.arange(n) / SR
    ph = np.cumsum(np.full(n, f) * (1 + vib * np.sin(2 * math.pi * 5.5 * tt) * np.clip((tt - 0.12) / 0.1, 0, 1))) / SR
    return np.where(ph % 1 < duty, 1.0, -1.0)


def tri(f, n, vib=0.0):
    tt = np.arange(n) / SR
    ph = np.cumsum(np.full(n, f) * (1 + vib * np.sin(2 * math.pi * 5 * tt) * np.clip((tt - 0.12) / 0.1, 0, 1))) / SR
    return 4 * np.abs(ph % 1 - 0.5) - 1


def noise(n, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, n)


def add(buf, t, sig, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * g


def lp(x, a=0.35):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def smooth(x, k=4):
    return np.convolve(x, np.ones(k) / k, mode='same')


BPM = 120
E8 = 60 / BPM / 2
PROG = [(62, 65, 69), (60, 64, 67), (58, 62, 65), (60, 64, 67)]
ROOT = [50, 48, 46, 48]
M1 = [[69, '-', 74, '-', 72, 69, 67, 69], [67, '-', 64, '-', 67, 69, 67, 64],
      [65, '-', 62, '-', 65, 67, 69, 65], [64, '-', 67, '-', 72, '-', 70, 69]]
M2 = [[74, '-', 72, 74, 77, '-', 76, 74], [72, '-', 67, '-', 72, 74, 76, 72],
      [70, '-', 69, 67, 65, '-', 67, 69], [67, '-', 64, '-', 67, '-', None, None]]
M3 = [[62, 65, 69, 74, '-', '-', 72, 69], [67, '-', 64, 67, 72, '-', 70, 67],
      [65, '-', 70, '-', 69, 67, 65, 64], [64, '-', 67, '-', 69, '-', 67, 64]]
MEL = M1 + M2 + M3


def gain_env(n, keys):
    tt = np.arange(n) / SR
    return np.interp(tt, [k[0] for k in keys], [k[1] for k in keys])


def music(total):
    n = int(total * SR)
    lead_sq, lead_tr, bass, arp, drums = (np.zeros(n) for _ in range(5))
    bars = int(total / (8 * E8)) + 1
    for b in range(bars):
        t0 = b * 8 * E8
        mel = MEL[b % len(MEL)]
        k = 0
        while k < 8:
            m = mel[k]
            if m is None or m == '-':
                k += 1
                continue
            L = 1
            while k + L < 8 and mel[k + L] == '-':
                L += 1
            dur = L * E8 * 0.95
            nn = int(dur * SR)
            add(lead_sq, t0 + k * E8, sq(midi(m), nn, 0.25, vib=0.006) * adsr(nn))
            add(lead_tr, t0 + k * E8, tri(midi(m + 12), nn, vib=0.01) * adsr(nn, a=0.02, sus=0.8))
            k += L
        root = ROOT[b % 4]
        for beat, (off, dd) in enumerate([(0, 0.42), (12, 0.2), (0, 0.42), (7, 0.2)]):
            nn = int(dd * SR)
            add(bass, t0 + beat * 2 * E8, tri(midi(root + off), nn) * adsr(nn, sus=0.9))
        ch = PROG[b % 4]
        pat = [0, 1, 2, 1, 0, 1, 2, 1] * 2
        for s16 in range(16):
            m = ch[pat[s16]] + 12 + (12 if s16 % 8 >= 4 and pat[s16] == 2 else 0)
            nn = int(0.09 * SR)
            add(arp, t0 + s16 * E8 / 2, sq(midi(m), nn, 0.125) * adsr(nn, dec=0.03, sus=0.2))
        for beat in range(4):
            tb = t0 + beat * 2 * E8
            if beat in (0, 2):
                nn = int(0.14 * SR)
                tt = np.arange(nn) / SR
                f = 150 * np.exp(-tt * 25) + 45
                add(drums, tb, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 22), 0.9)
            else:
                nn = int(0.12 * SR)
                tt = np.arange(nn) / SR
                add(drums, tb, (noise(nn, b * 4 + beat) * 0.7 + np.sin(2 * math.pi * 190 * tt) * 0.3) * np.exp(-tt * 30), 0.45)
            for h in (0, 1):
                nn = int(0.035 * SR)
                hh = np.diff(noise(nn + 1, 999 + b * 8 + beat * 2 + h))
                add(drums, tb + h * E8, hh * np.exp(-np.arange(nn) / SR * 90), 0.10)
    # virada antes da decisão
    for k in range(4):
        nn = int(0.06 * SR)
        add(drums, T7 - 0.25 + k * 0.0625, noise(nn, 500 + k) * np.exp(-np.arange(nn) / SR * 50), 0.32 + 0.06 * k)
    dg = gain_env(n, [(0, 1), (T4 - 0.3, 1), (T4, 0), (T7 - 0.3, 0), (T7 - 0.26, 1), (total, 1)])
    sg = gain_env(n, [(0, 1), (T4 - 0.1, 1), (T4 + 0.2, 0), (T7 - 0.1, 0), (T7 + 0.1, 1), (total, 1)])
    tg = 1 - sg
    mix = (smooth(lead_sq, 3) * 0.16 * sg + lead_tr * 0.20 * tg + bass * 0.30 + smooth(arp, 3) * 0.05
           + drums * 0.55 * dg)
    return mix


def sfx(total):
    n = int(total * SR)
    s = np.zeros(n)

    def blip(t, f, d=0.035, g=0.10, duty=0.5):
        nn = int(d * SR)
        add(s, t, sq(f, nn, duty) * adsr(nn, a=0.002, dec=0.02, sus=0.3, r=0.01), g)

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            if ta < TEND - 0.2:
                blip(ta, 988, g=0.07)
    # gancho
    for k, m in enumerate([84, 91]):
        nn = int(0.22 * SR)
        add(s, 0.25 + k * 0.06, sq(midi(m), nn, 0.25) * adsr(nn, dec=0.08, sus=0.2), 0.11)
    # pássaros
    for tb in (0.6, 0.72, 1.9, 3.3, 3.42):
        nn = int(0.06 * SR)
        tt = np.arange(nn) / SR
        f = 2600 + 1200 * tt / 0.06
        add(s, tb, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.sin(math.pi * tt / 0.06), 0.035)
    # chegada dos moradores
    scale = [74, 77, 79, 81, 84, 86, 89, 91, 93, 96, 98, 101]
    for i, ta in enumerate(ARRIVE):
        m = scale[i % len(scale)]
        for k, mm in enumerate((m, m + 12)):
            nn = int(0.08 * SR)
            add(s, ta + k * 0.05, sq(midi(mm), nn, 0.25) * adsr(nn, dec=0.04, sus=0.2), 0.10)
    # fanfarra do nome
    for k, m in enumerate([62, 65, 69, 74]):
        nn = int(0.09 * SR)
        add(s, T3 + 0.4 + k * 0.07, sq(midi(m + 12), nn, 0.25) * adsr(nn), 0.11)
    nn = int(0.6 * SR)
    add(s, T3 + 0.68, sq(midi(86), nn, 0.25, vib=0.01) * adsr(nn, dec=0.3, sus=0.5, r=0.2), 0.10)
    nn = int(0.8 * SR)
    add(s, T3 + 0.4, np.diff(noise(nn + 1, 77)) * np.exp(-np.arange(nn) / SR * 5), 0.05)
    # fogo acendendo + estalos
    nn = int(0.45 * SR)
    tt = np.arange(nn) / SR
    add(s, T4 - 0.05, lp(noise(nn, 3), 0.08) * np.sin(math.pi * tt / 0.45) ** 2, 0.9)
    r = random.Random(4)
    t = T4 + 0.1
    while t < TEND:
        nn = int(r.uniform(0.004, 0.012) * SR)
        g = 0.09 if t < T6 else 0.045
        add(s, t, noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), g * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
    # ? pops
    for tq in QTIMES:
        nn = int(0.07 * SR)
        tt = np.arange(nn) / SR
        f = 520 + 700 * tt / 0.07
        add(s, tq, np.sin(2 * math.pi * np.cumsum(f) / SR) * adsr(nn, dec=0.03, sus=0.4), 0.13)
    # passos e brilho do crachá
    for tp in (T5 + 0.25, T5 + 0.45):
        nn = int(0.05 * SR)
        add(s, tp, lp(noise(nn, int(tp * 99)), 0.15) * np.exp(-np.arange(nn) / SR * 60), 0.5)
    for k, m in enumerate([88, 93, 96, 100]):
        nn = int(0.09 * SR)
        add(s, TAG_T + k * 0.05, tri(midi(m), nn) * adsr(nn, dec=0.05, sus=0.3), 0.12)
    # luz misteriosa
    nn = int(1.8 * SR)
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 98 * tt) + 0.6 * np.sin(2 * math.pi * 147 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 3 * tt))
    add(s, MYST_T, hum * np.sin(math.pi * tt / 1.8), 0.12)
    add(s, MYST_T, np.sin(2 * math.pi * 2637 * tt) * (0.5 + 0.5 * np.sin(2 * math.pi * 7 * tt)) * np.sin(math.pi * tt / 1.8), 0.03)
    for k, m in enumerate((81, 80)):
        nn = int(0.5 * SR)
        add(s, MYST_T + k * 0.25, tri(midi(m), nn, vib=0.02) * adsr(nn, a=0.03, dec=0.3, sus=0.4, r=0.2), 0.10)
    # moradores reagem (!)
    for k, tb in enumerate(BANG_T):
        blip(tb, 1180 + 60 * k, d=0.04, g=0.08, duty=0.25)
    # grilos
    t = T5 + 1.0
    while t < TEND:
        for k in range(3):
            nn = int(0.018 * SR)
            add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.022)
        t += r.uniform(0.55, 0.95)
    # exemplo + fundadores
    blip(EX_T, 1318, d=0.05, g=0.08)
    for k, m in enumerate((79, 86)):
        nn = int(0.25 * SR)
        add(s, T7 + 2.5 + k * 0.08, sq(midi(m), nn, 0.25) * adsr(nn, dec=0.1, sus=0.3), 0.11)
    return s


def audio(path):
    total = TEND
    mix = music(total + 0.5)[:int(total * SR)] * 0.9 + sfx(total)
    fo = int(0.25 * SR)
    mix[-fo:] *= np.linspace(1, 0.35, fo)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    pcm = (mix * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- saída
def main():
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            t = float(v)
            Image.fromarray(frame(t)).save(os.path.join(OUTDIR, f'still_{t:05.2f}.png'))
        return
    wav = os.path.join(OUTDIR, 'ep1.wav')
    audio(wav)
    out = os.path.join(OUTDIR, os.environ.get('NAMEOUT', 'brasa-ep1-hd.mp4'))
    nfr = int(round(TEND * FPS))
    f0 = frame(0.0).astype(np.float32)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    for i in range(nfr):
        t = i / FPS
        f = frame(t)
        if t > TEND - XF:
            k = (t - (TEND - XF)) / XF
            f = (f.astype(np.float32) * (1 - k) + f0 * k).astype(np.uint8)
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print(out)


if __name__ == '__main__':
    main()
