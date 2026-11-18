#!/usr/bin/env python3
"""Será que enche? #3 — "Será que o porco escapa?": 8 cercas pintadas, uma dentro da outra, girando, cada uma com uma
porteira aberta. Quando um porco passa pela porteira, a cerca estoura e ele vira dois. Cada batida na cerca toca a
próxima nota de "Für Elise" (Beethoven, domínio público). Cronômetro de 22 s: escapa com 0,08 de sobra. Sem narração.
Uso: SEED=79 python3 porco.py   (PLAN=1 · STILLS=1,8,b-1,b+0.5 · CAPA=1)"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REINO = os.environ.get('REINO', '/home/claude/reino')
sys.path.insert(0, REINO)
import ep1hd as E
import folk as F
import world2 as W
from sim_porco import simulate, CX, CY, NR, RADII, RS, ring_angle
from melody import schedule, FUR_ELISE

FW, FH, FPS, S = 1080, 1920, 30, 3
CW, CH = 360, 640
SEED = int(os.environ.get('SEED', '79'))
GP = [41, 34, 32, 37, 51, 50, 53, 31]
LIMIT = 22.0
SPARE = float(os.environ.get('SPARE', '0.34'))   # sobra no cronômetro: varia de episódio pra episódio (0,05–0,50)
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.environ.get('OUT', os.path.join(OUTDIR, 'porco.mp4'))
WHITE, GOLD, TEAL, RED, GREEN = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 84, 64), (120, 236, 120)

SIM = simulate(seed=SEED, gap_px=GP, tmax=40)
FR, BR = SIM['frames'], SIM['breaks']
PHASE = SIM['phase']
ESC_SIM = SIM['esc']
T_ESC = LIMIT - SPARE                     # escapa aqui (tempo do vídeo)
WARP = ESC_SIM / T_ESC                    # tempo da simulação por segundo de vídeo
T_REB = T_ESC + 2.7                       # as cercas voltam
END = T_ESC + 3.5
BREAK_T = [b[0] / WARP for b in BR]       # tempo de vídeo em que cada cerca estoura
CW_RING = [(214, 64, 58), (236, 128, 52), (240, 196, 64), (106, 188, 78), (64, 182, 172), (72, 128, 214),
           (142, 94, 196), (226, 102, 160)]  # tinta de cada cerca (de dentro pra fora)

yy, xx = np.mgrid[0:CH, 0:CW]
BAY = np.tile(W.BAYER, (CH // 4, CW // 4))
ROUT = RADII[-1] + 4


def sim_t(t):
    return min(t * WARP, ESC_SIM)


def sim_frame(t):
    k = min(int(round(sim_t(t) * FPS)), len(FR) - 1)
    return FR[k], k


# ================================================================ chão: grama em volta, lama no chiqueiro
def build_ground():
    g = np.zeros((CH, CW, 3), np.float32)
    gn = W.vnoise(CH, CW, 30, 11, 3)
    lvl = np.clip(np.floor(gn * 3.2 + (BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
    g[:] = W.GREENS[lvl]
    r = np.hypot(xx - CX, yy - CY)
    inside = r < ROUT + 6
    mn = W.vnoise(CH, CW, 14, 31, 3)
    mud = np.array([(92, 62, 40), (112, 78, 50), (132, 96, 62)], np.float32)
    ml = np.clip(np.floor(mn * 3.3 + (BAY - 0.5) * 0.9 - 0.15), 0, 2).astype(int)
    g[inside] = mud[ml[inside]]
    pd = W.vnoise(CH, CW, 22, 77, 2)
    puddle = inside & (pd > 0.68)
    g[puddle] = np.array((70, 52, 42), np.float32)
    shine = puddle & (pd > 0.72) & (((xx * 7 + yy * 13) % 23) == 0)
    g[shine] = np.array((150, 140, 132), np.float32)
    edge = (r >= ROUT + 6) & (r < ROUT + 9)
    g[edge] = g[edge] * 0.78
    rr = random.Random(5)

    def put(x, y, c):
        if 0 <= x < CW and 0 <= y < CH:
            g[y, x] = c
    for _ in range(2200):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < ROUT + 10:
            continue
        c0 = (88, 144, 64) if rr.random() < 0.7 else (78, 132, 58)
        put(x, y, c0); put(x + 1, y - 1, c0); put(x + 2, y, c0)
    for _ in range(900):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < ROUT + 10:
            continue
        put(x, y, (150, 206, 104))
    for _ in range(120):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < ROUT + 14:
            continue
        c0 = rr.choice(W.FLOWER)
        put(x, y, c0); put(x - 1, y, W.shade(c0, 0.85)); put(x + 1, y, W.shade(c0, 0.85)); put(x, y - 1, W.shade(c0, 0.9))
        put(x, y, (255, 240, 170))
    for _ in range(160):                                  # palha na lama
        a = rr.uniform(0, 2 * math.pi); d = math.sqrt(rr.random()) * ROUT
        x, y = int(CX + d * math.cos(a)), int(CY + d * math.sin(a))
        b = rr.uniform(0, math.pi)
        for k in range(rr.randint(2, 4)):
            put(int(round(x + k * math.cos(b))), int(round(y + k * math.sin(b))), (214, 184, 104))
    vg = np.clip((np.hypot((xx - CX) / 230, (yy - 340) / 400) - 0.75) * 0.9, 0, 0.35)
    g *= (1 - vg)[..., None]
    g[:210] *= np.linspace(0.74, 1.0, 210)[:, None, None]
    return g


GROUND = build_ground()


# ================================================================ porco (vista de cima)
SPR = 21
_pig = {}


def pig_sprite(hi, leg, sc):
    k = (hi, leg, sc)
    if k in _pig:
        return _pig[k]
    a = 2 * math.pi * hi / 16
    ca, sa = math.cos(a), math.sin(a)
    c = SPR // 2
    v, u = np.mgrid[0:SPR, 0:SPR].astype(np.float32)
    u = (u - c) / sc; v = (v - c) / sc
    f = u * ca + v * sa
    s = -u * sa + v * ca
    body = (f / 6.6) ** 2 + (s / 5.0) ** 2 <= 1
    snout = ((f - 6.6) / 1.8) ** 2 + (s / 2.4) ** 2 <= 1
    ears = (((f - 3.6) / 1.6) ** 2 + ((s - 3.9) / 1.3) ** 2 <= 1) | (((f - 3.6) / 1.6) ** 2 + ((s + 3.9) / 1.3) ** 2 <= 1)
    tail = (((f + 7.2) ** 2 + (s - 0.6) ** 2) <= 0.9) | (((f + 8.0) ** 2 + (s + 0.4) ** 2) <= 0.7)
    legs = np.zeros_like(body)
    for (lf, ls) in [((3.6, 5.0), (-3.6, -5.0)), ((3.6, -5.0), (-3.6, 5.0))][leg]:
        legs |= (f - lf) ** 2 + (s - ls * 1.08) ** 2 <= 1.1
    legs &= ~body
    mask = body | snout | ears | tail | legs
    out = np.zeros((SPR, SPR, 3), np.float32)
    lit = -(u + v) * 0.17 + (BAY[:SPR, :SPR] - 0.5) * 0.5
    base, hi_c, lo_c = np.array((240, 158, 170)), np.array((252, 198, 206)), np.array((206, 118, 136))
    out[:] = np.where((lit > 0.55)[..., None], hi_c, np.where((lit < -0.7)[..., None], lo_c, base))
    out[snout] = (226, 120, 140)
    out[ears] = (214, 110, 128)
    out[tail] = (226, 128, 146)
    out[legs] = (170, 90, 104)
    for es in (-0.9, 0.9):                                # narinas
        xi = int(round(c + (7.2 * ca - es * sa) * sc)); yi = int(round(c + (7.2 * sa + es * ca) * sc))
        if 0 <= xi < SPR and 0 <= yi < SPR and snout[yi, xi]:
            out[yi, xi] = (120, 48, 66)
    for es in (-2.2, 2.2):                                # olhinhos
        xi = int(round(c + (4.6 * ca - es * sa) * sc)); yi = int(round(c + (4.6 * sa + es * ca) * sc))
        if 0 <= xi < SPR and 0 <= yi < SPR and body[yi, xi]:
            out[yi, xi] = (40, 24, 32)
    m = mask
    dil = m.copy()
    dil[1:] |= m[:-1]; dil[:-1] |= m[1:]; dil[:, 1:] |= m[:, :-1]; dil[:, :-1] |= m[:, 1:]
    ol = dil & ~m
    out[ol] = (84, 36, 50)
    _pig[k] = (out.astype(np.uint8), dil)
    return _pig[k]


SHAD = (((np.mgrid[0:10, 0:16][1] - 7.5) / 7.0) ** 2 + ((np.mgrid[0:10, 0:16][0] - 4.5) / 4.0) ** 2) <= 1


def _blit(img, rgb, m, x0, y0):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0]
    img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - x0:xb - x0][mm]


def _shade(img, m, x0, y0, k):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0]
    reg = img[ya:yb, xa:xb]
    reg[mm] = (reg[mm] * k).astype(img.dtype)


def draw_pig(img, x, y, ang, leg, sc=1.0, z=0.0):
    hi = int(round(ang / (2 * math.pi) * 16)) % 16
    scq = min([0.55, 0.8, 1.0], key=lambda q: abs(q - sc))
    rgb, m = pig_sprite(hi, leg, scq)
    xi, yi = int(round(x)), int(round(y))
    _shade(img, SHAD, xi - 8 + 1, yi - 5 + 3, 0.7)
    _blit(img, rgb, m, xi - SPR // 2, yi - SPR // 2 - int(round(z)))


# ================================================================ cercas
def ring_alive(k, t):
    if t >= T_REB:
        return t >= T_REB + 0.07 * k
    return not (k < len(BREAK_T) and t >= BREAK_T[k])


def ring_ang(k, t):
    st = 0.0 if t >= T_REB else sim_t(t)
    return ring_angle(k, st, PHASE)


def draw_rings(d, t, active):
    for k in range(NR):
        if not ring_alive(k, t):
            continue
        R = RADII[k]
        col = CW_RING[k]
        dark = tuple(int(c * 0.62) for c in col)
        lite = tuple(min(255, int(c * 1.25 + 20)) for c in col)
        g = GP[k] / 2 / R
        gc = ring_ang(k, t)
        pop = 1.0
        if t >= T_REB:
            pop = min(1.0, (t - (T_REB + 0.07 * k)) / 0.1)
        n = max(12, int(2 * math.pi * R / 7))
        pts = []
        for j in range(n + 1):
            a = gc + g + (2 * math.pi - 2 * g) * j / n
            pts.append((CX + R * math.cos(a), CY + R * math.sin(a)))
        lift = 3 * pop
        d.line([(x + 1, y + 2) for x, y in pts], fill=(30, 20, 14, 90), width=3)                # sombra
        d.line([(x, y) for x, y in pts], fill=dark + (255,), width=4)
        d.line([(x, y - lift) for x, y in pts], fill=(40, 26, 24, 255), width=4)
        d.line([(x, y - lift) for x, y in pts], fill=col + (255,), width=2)
        d.line([(x, y - lift - 1) for x, y in pts[::2]], fill=lite + (255,), width=1)
        # postes
        npst = max(6, int(2 * math.pi * R / 16))
        for j in range(npst + 1):
            a = gc + g + (2 * math.pi - 2 * g) * j / npst
            x, y = CX + R * math.cos(a), CY + R * math.sin(a)
            d.rectangle([x - 1, y - 6 * pop, x + 1, y], fill=(48, 30, 22, 255))
            d.point([(x, y - 6 * pop)], fill=lite + (255,))
        # porteira: dois mourões e a folha aberta pra fora
        for sgn in (-1, 1):
            a = gc + sgn * g
            x, y = CX + R * math.cos(a), CY + R * math.sin(a)
            d.rectangle([x - 2, y - 8 * pop, x + 2, y + 1], fill=(40, 26, 20, 255))
            d.rectangle([x - 1, y - 8 * pop, x + 1, y], fill=(150, 110, 70, 255))
        a = gc - g
        x0_, y0_ = CX + R * math.cos(a), CY + R * math.sin(a)
        lf = 9
        x1_, y1_ = x0_ + lf * math.cos(a), y0_ + lf * math.sin(a)
        d.line([(x0_, y0_ - 4), (x1_, y1_ - 4)], fill=(40, 26, 20, 255), width=3)
        d.line([(x0_, y0_ - 4), (x1_, y1_ - 4)], fill=col + (255,), width=1)
        if k == active and t < T_ESC:                    # porteira da vez brilhando
            a = gc
            x, y = CX + R * math.cos(a), CY + R * math.sin(a)
            al = int(90 + 60 * math.sin(t * 9))
            d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(255, 250, 200, al), width=1)


# ================================================================ estouros
_rd = random.Random(SEED * 11)
DEBRIS = []
for k in range(NR):
    R = RADII[k]
    for j in range(18):
        a = _rd.uniform(0, 2 * math.pi)
        sp = _rd.uniform(60, 150) * (1.6 if k == NR - 1 else 1)
        DEBRIS.append(dict(k=k, x=CX + R * math.cos(a), y=CY + R * math.sin(a), vx=math.cos(a) * sp + _rd.uniform(-20, 20),
                           vy=math.sin(a) * sp + _rd.uniform(-20, 20), vz=_rd.uniform(90, 200), a0=_rd.uniform(0, 6.3),
                           w=_rd.uniform(-14, 14), L=_rd.uniform(5, 9)))
GRAV = 620.0


def draw_debris(d, t):
    for db in DEBRIS:
        k = db['k']
        if k >= len(BREAK_T) or t < BREAK_T[k] or t >= T_REB:
            continue
        dt = t - BREAK_T[k]
        if dt > 1.4:
            continue
        tl = 2 * db['vz'] / GRAV
        tt = min(dt, tl)
        x = db['x'] + db['vx'] * tt
        y = db['y'] + db['vy'] * tt
        z = db['vz'] * tt - 0.5 * GRAV * tt * tt
        a = db['a0'] + db['w'] * tt
        hx, hy = math.cos(a) * db['L'] / 2, math.sin(a) * db['L'] / 2 * 0.6
        al = 255 if dt < 1.0 else int(255 * (1.4 - dt) / 0.4)
        col = CW_RING[k]
        d.line([(x - hx, y - z - hy), (x + hx, y - z + hy)], fill=(40, 26, 20, al), width=3)
        d.line([(x - hx, y - z - hy), (x + hx, y - z + hy)], fill=col + (al,), width=1)


def puffs(img, t):
    for k, (tb, rk, px, py) in enumerate(BR):
        tv = tb / WARP
        if not (0 <= t - tv < 0.3):
            continue
        q = (t - tv) / 0.3
        for j in range(10):
            a = j * 2 * math.pi / 10
            for rr_ in (3 + 14 * q,):
                x, y = int(px + rr_ * math.cos(a)), int(py + rr_ * math.sin(a))
                if 0 <= x < CW and 0 <= y < CH:
                    img[y, x] = (255, 250, 220)
        if q < 0.4:
            for j in range(4):
                a = j * math.pi / 2 + math.pi / 4
                for s_ in range(2, int(5 + 10 * q)):
                    x, y = int(px + s_ * math.cos(a)), int(py + s_ * math.sin(a))
                    if 0 <= x < CW and 0 <= y < CH:
                        img[y, x] = (255, 240, 170)


# ================================================================ moradores olhando
FOLK = [('Valdemir', 'vaqueiro', 40, 590), ('Luiza', 'santa', 26, 268), ('pixoto', 'cidadão', 330, 262),
        ('Edilson', 'espadachim', 322, 592)]
FOLK_SPR = {}
for _n, _r, _, _ in FOLK:
    _a = F.folk(_n, _r, 0)
    FOLK_SPR[_n] = (_a[..., :3].astype(np.uint8), _a[..., 3] > 0.5)


def draw_folk(img, t):
    for i, (nm, rl, fx, fy) in enumerate(FOLK):
        rgb, m = FOLK_SPR[nm]
        jump = 0
        if T_ESC <= t < T_ESC + 1.8:
            jump = int(round(abs(math.sin((t - T_ESC) * 9 + i)) * 7))
        _shade(img, np.ones((3, 16), bool), fx - 8, fy - 2, 0.7)
        _blit(img, rgb, m, fx - 15, fy - 42 - jump)
        if T_ESC + 0.05 <= t < T_ESC + 1.8:
            W.qmark(img, fx - 3, fy - 42 - jump - 8, bang=True)


# ================================================================ quadro
ESC_STATE = FR[-1]
_re = random.Random(SEED * 3)
RUN = []
for i, (p, v) in enumerate(zip(ESC_STATE['pos'], ESC_STATE['vel'])):
    rel = p - np.array([CX, CY]); dd = np.hypot(*rel) + 1e-6
    sp = _re.uniform(160, 260)
    RUN.append((p.copy(), rel / dd * sp + v * 0.3, _re.uniform(0, 6.3)))


def heading(k, i):
    k0 = max(0, k - 3)
    if i < FR[k0]['n']:
        dv = FR[k]['pos'][i] - FR[k0]['pos'][i]
        if 0.8 < np.hypot(*dv) < 30:
            return math.atan2(dv[1], dv[0])
    v = FR[k]['vel'][i]
    return math.atan2(v[1], v[0])


def frame_canvas(t):
    img8 = np.clip(GROUND, 0, 255).astype(np.uint8)
    pre = t < T_ESC
    st, k = sim_frame(t) if pre else (ESC_STATE, len(FR) - 1)
    active = st['active']
    pil = Image.fromarray(img8)
    d = ImageDraw.Draw(pil, 'RGBA')
    draw_rings(d, t, active)
    img8 = np.asarray(pil).copy()
    if pre:
        order = np.argsort(st['pos'][:, 1])
        for i in order:
            x, y = st['pos'][i]
            born = st['born'][i] / WARP
            age = t - born
            sc = 1.0 if (i == 0 or age > 0.15) else 0.55 + 0.45 * age / 0.15
            draw_pig(img8, x, y, heading(k, i), int(t * 10 + i) % 2, sc)
        puffs(img8, t)
    elif t < T_REB:
        dt = t - T_ESC
        items = []
        for i, (p, v, ph) in enumerate(RUN):
            x, y = p + v * dt
            if -20 < x < CW + 20 and -20 < y < CH + 20:
                items.append((y, x, i, v, ph))
        for y, x, i, v, ph in sorted(items):
            draw_pig(img8, x, y, math.atan2(v[1], v[0]), int(dt * 16 + i) % 2, 1.0, abs(math.sin(dt * 12 + ph)) * 3)
        puffs(img8, t)
    if t >= END - 0.35:                                     # o primeiro porco volta pro meio
        age = t - (END - 0.35)
        p0 = FR[0]['pos'][0]
        draw_pig(img8, p0[0], p0[1], heading(0, 0), 0, 0.55 + 0.45 * min(1, age / 0.15))
    pil = Image.fromarray(img8)
    d = ImageDraw.Draw(pil, 'RGBA')
    draw_debris(d, t)
    img8 = np.asarray(pil).copy()
    draw_folk(img8, t)
    return img8


# ---------------------------------------------------------------- textos
def timer_val(t):
    if t >= T_ESC and t < END - 0.4:
        return SPARE
    if t >= END - 0.4:
        return LIMIT
    return max(0.0, LIMIT - t)


def fmt(v):
    return f'{v:05.2f}'.replace('.', ',')


def overlay(im, t):
    d = ImageDraw.Draw(im, 'RGBA')
    pre = t < T_ESC or t >= END - 0.4
    if pre:
        E.draw_line(d, FW / 2, 64, [('SERÁ QUE O PORCO', WHITE)], 128)
        E.draw_line(d, FW / 2, 190, [('ESCAPA?', GOLD)], 210, stroke=12)
        hot = T_ESC - 6 <= t < T_ESC
        col = RED if hot else WHITE
        jx = math.sin(t * 61) * 5 if t > T_ESC - 3 and t < T_ESC else 0
        E.draw_line(d, FW / 2 + jx, 410, [(fmt(timer_val(t)), col)], 150, stroke=10)
        st = sim_frame(t)[0] if t < T_ESC else FR[0]
        left = NR - (st['active'] if t < T_ESC else 0)
        if t >= T_ESC:
            left = NR
        E.draw_line(d, FW / 2, 572, [('FALTAM ', WHITE), (f'{left}', GOLD), (' CERCAS' if left != 1 else ' CERCA', WHITE)], 70,
                    stroke=6)
        if t < 4.0 or t >= END - 0.4:
            E.draw_line(d, FW / 2, 1735, [('PASSOU NA PORTEIRA, ', WHITE), ('VIROU DOIS', TEAL)], 60, stroke=6)
    else:
        q = min(1.0, (t - T_ESC) / 0.12)
        E.draw_line(d, FW / 2, 120, [('ESCAPOU!', GOLD)], int(170 + 70 * q), stroke=14)
        E.draw_line(d, FW / 2, 410, [(fmt(SPARE), GREEN)], 150, stroke=10)
        if t > T_ESC + 0.5:
            E.draw_line(d, FW / 2, 572, [('COM ', WHITE), (f'{SPARE:.2f}'.replace('.', ','), GREEN), (' DE SOBRA', WHITE)], 70, stroke=6)


VIG = np.clip((np.hypot((xx - CX) / 200, (yy - 330) / 360) - 0.7) / 0.6, 0, 1).astype(np.float32)


def make_beats():
    bt, tb = [], T_ESC - 6.0
    while tb < T_ESC - 0.15:
        bt.append(tb)
        q = (tb - (T_ESC - 6.0)) / 6.0
        tb += 0.8 - 0.42 * q
    return bt


BEATS = make_beats()


def heart_level(t):
    if not (T_ESC - 6.0 <= t < T_ESC):
        return 0.0
    for tb in BEATS:
        if tb <= t < tb + 0.35:
            return (1 - (t - tb) / 0.35) * (0.3 + 0.4 * (t - (T_ESC - 6)) / 6)
    return 0.0


def frame(t):
    c = frame_canvas(t).astype(np.float32)
    hl = heart_level(t)
    if hl > 0:
        c = c * (1 - VIG[..., None] * hl * 0.8) + np.array([150, 10, 20], np.float32) * VIG[..., None] * hl * 0.8
    for tv in BREAK_T:
        if 0 <= t - tv < 0.08:
            c = c + (255 - c) * 0.25 * (1 - (t - tv) / 0.08)
    if T_ESC <= t < T_ESC + 0.12:
        c = c + (255 - c) * (1 - (t - T_ESC) / 0.12) * 0.75
    f = np.clip(c, 0, 255).astype(np.uint8).repeat(S, 0).repeat(S, 1)
    if T_ESC <= t < T_ESC + 0.5:
        amp = (1 - (t - T_ESC) / 0.5) * 16
        f = np.roll(f, (int(math.sin(t * 90) * amp), int(math.cos(t * 77) * amp)), (0, 1))
    im = Image.fromarray(f)
    overlay(im, t)
    return np.asarray(im)


# ================================================================ áudio
SR = E.SR
FUR_A = [76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72,
         64, 76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 72, 71, 69]
FUR_B = [71, 72, 74, 76, 67, 77, 76, 74, 65, 76, 74, 72, 64, 74, 72, 71]
FUR = FUR_A + FUR_A + FUR_B + FUR_A + FUR_B + FUR_A


def keynote(m, dur=0.55):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    sig = (np.sin(2 * math.pi * f * tt) + 0.42 * np.sin(4 * math.pi * f * tt) * np.exp(-tt * 6)
           + 0.18 * np.sin(6 * math.pi * f * tt) * np.exp(-tt * 9))
    env = np.minimum(1, tt / 0.004) * np.exp(-tt * 4.2)
    return sig * env


def wood(n, fres, dec):
    tt = np.arange(n) / SR
    return np.sin(2 * math.pi * fres * tt) * np.exp(-tt / dec)


def oink(f0, seed):
    n = int(0.22 * SR)
    tt = np.arange(n) / SR
    rr = np.random.default_rng(seed)
    f = f0 * (1 + 0.25 * np.sin(math.pi * tt / 0.22))
    ph = np.cumsum(f) / SR
    buzz = np.sign(np.sin(2 * math.pi * ph)) * 0.6 + rr.normal(0, 0.35, n)
    env = np.sin(math.pi * np.minimum(1, tt / 0.22)) ** 0.6 * (0.6 + 0.4 * np.sin(2 * math.pi * 38 * tt))
    return E.lp(buzz * env, 0.12)


def audio(path):
    total = END + 0.2
    n = int(total * SR)
    s = np.zeros(n)
    rr = random.Random(SEED)
    s += E.lp(E.noise(n, 3), 0.02) * 0.04
    # Für Elise puxada pelas batidas na cerca (cada batida libera uma nota; a nota toca no ritmo da música)
    bts = [tb / WARP for (tb, i, x, y, act) in SIM['bounces'] if tb / WARP < T_ESC]
    for tv in bts:
        E.add(s, tv, wood(int(0.03 * SR), 900, 0.004), 0.04)
    for tv, m, role in schedule(FUR_ELISE, bts, 0.14, T_ESC):
        if role == 'm':
            E.add(s, tv, keynote(m, 0.6), 0.34)
        else:
            E.add(s, tv, keynote(m, 0.7), 0.2)
    # cerca estourando: craque de madeira + baixo + oinc do porco novo
    for k, tv in enumerate(BREAK_T):
        nn = int(0.4 * SR)
        tt = np.arange(nn) / SR
        crack = E.lp(E.noise(nn, 40 + k), 0.3) * np.exp(-tt / 0.07)
        E.add(s, tv, crack, 0.55 if k < NR - 1 else 1.0)
        for q in range(5):
            E.add(s, tv + rr.uniform(0, 0.12), wood(int(0.05 * SR), rr.uniform(500, 1100), 0.01), 0.15)
        if k < NR - 1:
            E.add(s, tv + 0.1, oink(rr.uniform(150, 200), k), 0.22)
    # tique-taque e coração nos últimos 6 s
    tk = T_ESC - 6.0
    while tk < T_ESC:
        E.add(s, tk, wood(int(0.03 * SR), 2400, 0.004), 0.12)
        tk += 0.5
    for tb in BEATS:
        for off, g in ((0.0, 0.5), (0.13, 0.32)):
            nn = int(0.14 * SR)
            tt = np.arange(nn) / SR
            E.add(s, tb + off, np.sin(2 * math.pi * np.cumsum(70 * np.exp(-tt * 9) + 38) / SR) * np.exp(-tt * 22), g)
    # ESCAPOU: estrondo, fanfarra e um coro de oinc
    nn = int(0.9 * SR)
    tt = np.arange(nn) / SR
    E.add(s, T_ESC, np.sin(2 * math.pi * np.cumsum(80 * np.exp(-tt * 5) + 30) / SR) * np.exp(-tt / 0.35), 0.8)
    for k, m in enumerate((69, 73, 76, 81)):
        nb = int(0.12 * SR)
        E.add(s, T_ESC + 0.35 + k * 0.09, E.sq(E.midi(m), nb, 0.5) * E.adsr(nb, a=0.002, dec=0.04, sus=0.6, r=0.02), 0.1)
    nb = int(0.7 * SR)
    for m in (69, 73, 76):
        E.add(s, T_ESC + 0.71, E.sq(E.midi(m + 12), nb, 0.25, vib=0.01) * E.adsr(nb, a=0.004, dec=0.2, sus=0.5, r=0.2), 0.05)
    for k in range(8):
        E.add(s, T_ESC + 0.2 + rr.uniform(0, 1.2), oink(rr.uniform(140, 230), 100 + k), 0.16)
    for k in range(NR):                                   # as cercas voltando
        E.add(s, T_REB + 0.07 * k, wood(int(0.05 * SR), 700 + 60 * k, 0.008), 0.25)
    s = s / (np.abs(s).max() + 1e-9) * 0.85
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


def capa():
    t = T_ESC - 2.0
    f = frame_canvas(t).repeat(S, 0).repeat(S, 1)
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 520, FW, 1320), fill=(16, 12, 30, 125))
    E.draw_line(d, FW / 2, 600, [('SERÁ QUE O', WHITE)], 150)
    E.draw_line(d, FW / 2, 770, [('PORCO', GOLD)], 300, stroke=16)
    E.draw_line(d, FW / 2, 1080, [('ESCAPA?', WHITE)], 180, stroke=12)
    out = os.path.join(OUTDIR, 'capa-porco.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


if __name__ == '__main__':
    if os.environ.get('PLAN'):
        print(f'seed {SEED}: escapa na sim {ESC_SIM:.2f}s → vídeo {T_ESC:.2f}s (warp {WARP:.3f}); fim {END:.2f}s')
        print('cercas estouram (vídeo):', [round(x, 2) for x in BREAK_T], 'notas:', len(SIM['bounces']))
        raise SystemExit
    if os.environ.get('CAPA'):
        capa(); raise SystemExit
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            tv = T_ESC + float(v[1:]) if v.startswith('b') else float(v)
            Image.fromarray(frame(tv)).save(os.path.join(OUTDIR, f'still_{v}.png'))
        print('ok'); raise SystemExit
    wav = os.path.join(OUTDIR, 'porco.wav')
    audio(wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k',
                          '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    for i in range(int(round(END * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(OUT, f'{END:.2f}s')
