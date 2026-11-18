#!/usr/bin/env python3
"""Será que enche? #4 — "Será que as abelhas enchem a colmeia?": um favo grande de alvéolos hexagonais; as abelhas voam
quicando e todo alvéolo que sobrevoam enche de mel; a cada 25 alvéolos cheios nasce mais uma abelha. Cada alvéolo cheio
toca a próxima nota de "O Voo do Besouro" (Rimsky-Korsakov, domínio público). Cronômetro de 22 s; enche com 0,19 de sobra.
Uso: python3 abelha.py   (PLAN=1 · STILLS=1,8,b-1,b+0.8 · CAPA=1)"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REINO = os.environ.get('REINO', '/home/claude/reino')
sys.path.insert(0, REINO)
import ep1hd as E
import folk as F
import world2 as W
from sim_abelha import simulate, CX, CY, RB, CELL, CELLS, RS, NORMALS, APO
sys.path.insert(0, '/home/claude/porco')
from melody import schedule

FW, FH, FPS, S = 1080, 1920, 30, 3
CW, CH = 360, 640
SEED = int(os.environ.get('SEED', '130'))
PARAMS = dict(speed=115.0, k_spawn=25, wander=0.9, smell=1.2)
LIMIT = 22.0
SPARE = float(os.environ.get('SPARE', '0.19'))
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.environ.get('OUT', os.path.join(OUTDIR, 'abelhas.mp4'))
WHITE, GOLD, TEAL, RED, GREEN = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 84, 64), (120, 236, 120)

SIM = simulate(seed=SEED, tmax=40, **PARAMS)
FR = SIM['frames']
FULL_SIM = SIM['full']
T_FULL = LIMIT - SPARE
WARP = FULL_SIM / T_FULL
T_DRAIN = T_FULL + 2.6
END = T_FULL + 3.5
NC = len(CELLS)
FILL_T = np.where(SIM['filled'] >= 0, SIM['filled'] / WARP, 1e9)   # tempo de vídeo em que cada alvéolo encheu
ORDER = np.argsort(FILL_T)
DRAIN_T = np.empty(NC)                                               # esvazia na ordem contrária, rapidinho
DRAIN_T[ORDER[::-1]] = T_DRAIN + np.linspace(0, 0.55, NC)

yy, xx = np.mgrid[0:CH, 0:CW]
BAY = np.tile(W.BAYER, (CH // 4, CW // 4))


def sim_frame(t):
    k = min(int(round(min(t * WARP, FULL_SIM) * FPS)), len(FR) - 1)
    return FR[k], k


# ================================================================ mapa dos alvéolos (pré-calculado)
rel = np.stack([xx - CX, yy - CY], -1).astype(np.float32)
INSIDE = (rel @ NORMALS.T.astype(np.float32)).max(-1) <= APO - 2.0
iy, ix = np.nonzero(INSIDE)
P = np.stack([ix, iy], 1).astype(np.float32) + 0.5
d1 = np.full(len(P), 1e9, np.float32); d2 = np.full(len(P), 1e9, np.float32); lab = np.zeros(len(P), np.int32)
for c, (cx, cy) in enumerate(CELLS):
    d = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
    nb = d < d1
    d2 = np.where(nb, d1, np.minimum(d2, d))
    lab = np.where(nb, c, lab)
    d1 = np.where(nb, d, d1)
RN = d1 / CELL
WALL = ((d2 - d1) < 1.7) | (RN > 0.98)          # o que sobra na beirada vira cera
DXL = P[:, 0] - CELLS[lab, 0]
DYL = P[:, 1] - CELLS[lab, 1]
BAYP = BAY[iy, ix]
EDGE_OUT = (rel @ NORMALS.T.astype(np.float32)).max(-1)
FRAME = (EDGE_OUT > APO - 2.0) & (EDGE_OUT <= APO + 5.0)


# ================================================================ chão: grama com muita flor
def build_ground():
    g = np.zeros((CH, CW, 3), np.float32)
    gn = W.vnoise(CH, CW, 30, 11, 3)
    lvl = np.clip(np.floor(gn * 3.2 + (BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
    g[:] = W.GREENS[lvl]
    rr = random.Random(5)

    def put(x, y, c):
        if 0 <= x < CW and 0 <= y < CH:
            g[y, x] = c
    for _ in range(2200):
        x, y = rr.randrange(CW), rr.randrange(CH)
        c0 = (88, 144, 64) if rr.random() < 0.7 else (78, 132, 58)
        put(x, y, c0); put(x + 1, y - 1, c0); put(x + 2, y, c0)
    for _ in range(900):
        put(rr.randrange(CW), rr.randrange(CH), (150, 206, 104))
    for _ in range(320):                                   # flores (abelha gosta)
        x, y = rr.randrange(CW), rr.randrange(CH)
        c0 = rr.choice(W.FLOWER + [(250, 250, 250), (250, 220, 80)])
        put(x, y + 1, (70, 130, 60))
        put(x, y, (255, 236, 150)); put(x - 1, y, c0); put(x + 1, y, c0); put(x, y - 1, c0); put(x, y + 1, c0)
    sh = (EDGE_OUT > APO + 4) & (EDGE_OUT < APO + 9)
    g[sh] *= 0.72
    vg = np.clip((np.hypot((xx - CX) / 230, (yy - 340) / 400) - 0.75) * 0.9, 0, 0.35)
    g *= (1 - vg)[..., None]
    g[:210] *= np.linspace(0.74, 1.0, 210)[:, None, None]
    return g


GROUND = build_ground()
WAX_WALL = np.array((236, 200, 124), np.float32)
WAX_WALL_D = np.array((196, 156, 84), np.float32)
EMPTY = np.array((112, 72, 32), np.float32)
EMPTY_D = np.array((86, 52, 24), np.float32)
HONEY = np.array((250, 176, 34), np.float32)
HONEY_H = np.array((255, 228, 120), np.float32)
HONEY_D = np.array((212, 128, 22), np.float32)


def paint_comb(img, t):
    if t < T_DRAIN:
        prog = np.clip((t - FILL_T) / 0.18, 0, 1)
    else:
        prog = np.clip(1 - (t - DRAIN_T) / 0.12, 0, 1)
    pl = prog[lab]
    honey = (RN < pl * 1.08) & ~WALL
    col = np.where((RN > 0.62)[:, None], EMPTY, EMPTY_D)
    col = np.where(((DXL + DYL) < -CELL * 0.55)[:, None] & (RN > 0.6)[:, None], EMPTY * 1.15, col)
    hc = np.where(((DXL + DYL) < -CELL * 0.25)[:, None] & (RN < 0.62)[:, None], HONEY_H,
                  np.where((RN > 0.78)[:, None], HONEY_D, HONEY))
    if T_FULL <= t < T_DRAIN:                               # brilho geral quando enche
        k = 0.15 + 0.15 * math.sin((t - T_FULL) * 10)
        hc = hc + (255 - hc) * k
    col = np.where(honey[:, None], hc, col)
    wl = np.where(((DXL + DYL) < 0)[:, None], WAX_WALL, WAX_WALL_D)
    col = np.where(WALL[:, None], wl, col)
    # os últimos alvéolos piscam quando faltam poucos
    st, _ = sim_frame(t)
    left = NC - st['nfill'] if t < T_FULL else 0
    if 0 < left <= 9:
        emp = (FILL_T > t)[lab] & ~WALL & (RN > 0.66) & (RN < 0.9)
        k = 0.35 + 0.35 * math.sin(t * 12)
        col = np.where(emp[:, None], col * (1 - k) + np.array((255, 236, 160)) * k, col)
    img[iy, ix] = col
    fr = FRAME
    img[fr] = np.array((126, 82, 44), np.float32)
    img[fr & (EDGE_OUT > APO + 3.0)] = np.array((70, 44, 26), np.float32)
    img[fr & (EDGE_OUT <= APO - 0.5)] = np.array((168, 116, 64), np.float32)


# ================================================================ abelha (vista de cima)
SPR = 19
_bee = {}


def bee_sprite(hi, wing, sc):
    k = (hi, wing, sc)
    if k in _bee:
        return _bee[k]
    a = 2 * math.pi * hi / 16
    ca, sa = math.cos(a), math.sin(a)
    c = SPR // 2
    v, u = np.mgrid[0:SPR, 0:SPR].astype(np.float32)
    u = (u - c) / sc; v = (v - c) / sc
    f = u * ca + v * sa
    s = -u * sa + v * ca
    body = ((f + 0.6) / 5.4) ** 2 + (s / 3.6) ** 2 <= 1
    head = ((f - 4.6) / 2.2) ** 2 + (s / 2.4) ** 2 <= 1
    sting = (f < -5.6) & (f > -7.4) & (np.abs(s) < 0.8)
    ws = 4.6 if wing == 0 else 3.6
    wings = ((((f + 0.2) / 2.6) ** 2 + ((s - ws) / 2.2) ** 2) <= 1) | ((((f + 0.2) / 2.6) ** 2 + ((s + ws) / 2.2) ** 2) <= 1)
    mask = body | head | sting
    out = np.zeros((SPR, SPR, 3), np.float32)
    stripe = (np.floor((f + 6) / 2.0) % 2 == 0) & (f < 3.2)
    lit = -(u + v) * 0.17 + (BAY[:SPR, :SPR] - 0.5) * 0.4
    out[:] = np.where((lit > 0.5)[..., None], (255, 226, 92), np.where((lit < -0.7)[..., None], (214, 160, 24), (248, 196, 40)))
    out[stripe & body] = (44, 32, 22)
    out[head] = (40, 30, 24)
    out[sting] = (30, 22, 18)
    for es in (-1.2, 1.2):
        xi = int(round(c + (5.4 * ca - es * sa) * sc)); yi = int(round(c + (5.4 * sa + es * ca) * sc))
        if 0 <= xi < SPR and 0 <= yi < SPR:
            out[yi, xi] = (230, 230, 240)
    m = mask
    dil = m.copy()
    dil[1:] |= m[:-1]; dil[:-1] |= m[1:]; dil[:, 1:] |= m[:, :-1]; dil[:, :-1] |= m[:, 1:]
    out[dil & ~m] = (36, 24, 18)
    wm = wings & ~dil
    _bee[k] = (out.astype(np.uint8), dil, wm)
    return _bee[k]


SHAD = (((np.mgrid[0:8, 0:14][1] - 6.5) / 6.0) ** 2 + ((np.mgrid[0:8, 0:14][0] - 3.5) / 3.2) ** 2) <= 1


def _clip(img, m, x0, y0):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return None
    return xa, ya, xb, yb, m[ya - y0:yb - y0, xa - x0:xb - x0]


def draw_bee(img, x, y, ang, wing, sc=1.0, z=3.0):
    hi = int(round(ang / (2 * math.pi) * 16)) % 16
    scq = min([0.55, 0.8, 1.0], key=lambda q: abs(q - sc))
    rgb, m, wm = bee_sprite(hi, wing, scq)
    xi, yi = int(round(x)), int(round(y))
    cl = _clip(img, SHAD, xi - 7 + 2, yi - 4 + 5)
    if cl:
        xa, ya, xb, yb, mm = cl
        reg = img[ya:yb, xa:xb]; reg[mm] = (reg[mm] * 0.72).astype(img.dtype)
    x0, y0 = xi - SPR // 2, yi - SPR // 2 - int(z)
    cl = _clip(img, wm, x0, y0)
    if cl:
        xa, ya, xb, yb, mm = cl
        reg = img[ya:yb, xa:xb]; reg[mm] = (reg[mm] * 0.45 + np.array((236, 244, 255)) * 0.55).astype(img.dtype)
    cl = _clip(img, m, x0, y0)
    if cl:
        xa, ya, xb, yb, mm = cl
        img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - x0:xb - x0][mm]


# ================================================================ moradores olhando
FOLK = [('Valdemir', 'vaqueiro', 40, 596), ('Luiza', 'santa', 26, 262), ('pixoto', 'cidadão', 330, 256),
        ('Edilson', 'espadachim', 322, 598)]
FOLK_SPR = {}
for _n, _r, _, _ in FOLK:
    _a = F.folk(_n, _r, 0)
    FOLK_SPR[_n] = (_a[..., :3].astype(np.uint8), _a[..., 3] > 0.5)


def draw_folk(img, t):
    for i, (nm, rl, fx, fy) in enumerate(FOLK):
        rgb, m = FOLK_SPR[nm]
        jump = int(round(abs(math.sin((t - T_FULL) * 9 + i)) * 7)) if T_FULL <= t < T_FULL + 1.8 else 0
        cl = _clip(img, np.ones((3, 16), bool), fx - 8, fy - 2)
        if cl:
            xa, ya, xb, yb, mm = cl
            reg = img[ya:yb, xa:xb]; reg[mm] = (reg[mm] * 0.7).astype(img.dtype)
        cl = _clip(img, m, fx - 15, fy - 42 - jump)
        if cl:
            xa, ya, xb, yb, mm = cl
            x0, y0 = fx - 15, fy - 42 - jump
            img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - x0:xb - x0][mm]
        if T_FULL + 0.05 <= t < T_FULL + 1.8:
            W.qmark(img, fx - 3, fy - 50 - jump, bang=True)


# ================================================================ quadro
LAST = FR[-1]
_re = random.Random(SEED * 3)
FLY = [(p.copy(), _re.uniform(110, 190), _re.choice((-1, 1)) * _re.uniform(1.5, 3.0), _re.uniform(0, 6.3)) for p in LAST['pos']]


def heading(k, i):
    k0 = max(0, k - 3)
    if i < FR[k0]['n']:
        dv = FR[k]['pos'][i] - FR[k0]['pos'][i]
        if 0.8 < np.hypot(*dv) < 30:
            return math.atan2(dv[1], dv[0])
    v = FR[k]['vel'][i]
    return math.atan2(v[1], v[0])


SPAWNS = []
for _t, _c, _n in SIM['fills']:
    if _n % PARAMS['k_spawn'] == 0:
        SPAWNS.append((_t / WARP, float(CELLS[_c][0]), float(CELLS[_c][1])))


def puffs(img, t):
    for tv, px, py in SPAWNS:
        if not (0 <= t - tv < 0.3):
            continue
        q = (t - tv) / 0.3
        for j in range(10):
            a = j * 2 * math.pi / 10
            x, y = int(px + (3 + 14 * q) * math.cos(a)), int(py + (3 + 14 * q) * math.sin(a))
            if 0 <= x < CW and 0 <= y < CH:
                img[y, x] = (255, 250, 210)


def sparkles(img, t):
    if not (T_FULL <= t < T_FULL + 1.6):
        return
    r = random.Random(int(t * 30))
    for _ in range(40):
        c = r.randrange(NC)
        x, y = int(CELLS[c][0] + r.uniform(-3, 3)), int(CELLS[c][1] + r.uniform(-3, 3))
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < CW and 0 <= y + dy < CH:
                img[y + dy, x + dx] = (255, 252, 220)


def frame_canvas(t):
    img = GROUND.copy()
    paint_comb(img, t)
    img8 = np.clip(img, 0, 255).astype(np.uint8)
    if t < T_FULL:
        st, k = sim_frame(t)
        for i in np.argsort(st['pos'][:, 1]):
            x, y = st['pos'][i]
            age = t - st['born'][i] / WARP
            sc = 1.0 if (i == 0 or age > 0.15) else 0.55 + 0.45 * age / 0.15
            draw_bee(img8, x, y, heading(k, i), int(t * 24 + i) % 2, sc)
        puffs(img8, t)
    elif t < T_DRAIN + 0.6:
        dt = t - T_FULL
        for i, (p, sp, spin, ph) in enumerate(FLY):
            rel_ = p - np.array([CX, CY])
            r0 = np.hypot(*rel_) + 1e-6
            a0 = math.atan2(rel_[1], rel_[0])
            r_ = r0 + sp * dt
            a_ = a0 + spin * dt
            x, y = CX + r_ * math.cos(a_), CY + r_ * math.sin(a_)
            if -20 < x < CW + 20 and -20 < y < CH + 20:
                draw_bee(img8, x, y, a_ + math.pi / 2 * (1 if spin > 0 else -1), int(t * 24 + i) % 2, 1.0, 3 + 4 * min(1, dt))
        sparkles(img8, t)
    if t >= END - 0.35:
        age = t - (END - 0.35)
        draw_bee(img8, CX, CY, heading(0, 0), int(t * 24) % 2, 0.55 + 0.45 * min(1, age / 0.15))
    draw_folk(img8, t)
    return img8


# ---------------------------------------------------------------- textos
def fmt(v):
    return f'{v:05.2f}'.replace('.', ',')


def overlay(im, t):
    d = ImageDraw.Draw(im, 'RGBA')
    pre = t < T_FULL or t >= END - 0.4
    if pre:
        E.draw_line(d, FW / 2, 64, [('SERÁ QUE AS ABELHAS', WHITE)], 112)
        E.draw_line(d, FW / 2, 180, [('ENCHEM A COLMEIA?', GOLD)], 150, stroke=12)
        tv = LIMIT if t >= END - 0.4 else max(0.0, LIMIT - t)
        hot = T_FULL - 6 <= t < T_FULL
        jx = math.sin(t * 61) * 5 if T_FULL - 3 < t < T_FULL else 0
        E.draw_line(d, FW / 2 + jx, 400, [(fmt(tv), RED if hot else WHITE)], 150, stroke=10)
        nf = sim_frame(t)[0]['nfill'] if t < T_FULL else 0
        left = NC - nf
        if t < T_FULL and 0 < left <= 9:
            E.draw_line(d, FW / 2, 572, [('FALTAM ', WHITE), (f'{left}', GOLD), (' FAVOS' if left > 1 else ' FAVO', WHITE)], 72,
                        stroke=6)
        else:
            pct = min(99, int(nf / NC * 100)) if t < T_FULL else 0
            E.draw_line(d, FW / 2, 572, [('MEL: ', WHITE), (f'{pct}%', GOLD)], 72, stroke=6)
        if t < 4.0 or t >= END - 0.4:
            E.draw_line(d, FW / 2, 1700, [('A CADA 25 FAVOS, ', WHITE), ('NASCE UMA ABELHA', TEAL)], 58, stroke=6)
    else:
        q = min(1.0, (t - T_FULL) / 0.12)
        E.draw_line(d, FW / 2, 120, [('ENCHEU!', GOLD)], int(170 + 70 * q), stroke=14)
        E.draw_line(d, FW / 2, 400, [(fmt(SPARE), GREEN)], 150, stroke=10)
        if t > T_FULL + 0.5:
            E.draw_line(d, FW / 2, 572, [('COM ', WHITE), (f'{SPARE:.2f}'.replace('.', ','), GREEN), (' DE SOBRA', WHITE)], 72,
                        stroke=6)


VIG = np.clip((np.hypot((xx - CX) / 200, (yy - 330) / 360) - 0.7) / 0.6, 0, 1).astype(np.float32)


def make_beats():
    bt, tb = [], T_FULL - 6.0
    while tb < T_FULL - 0.15:
        bt.append(tb)
        tb += 0.8 - 0.42 * (tb - (T_FULL - 6.0)) / 6.0
    return bt


BEATS = make_beats()


def heart_level(t):
    if not (T_FULL - 6.0 <= t < T_FULL):
        return 0.0
    for tb in BEATS:
        if tb <= t < tb + 0.35:
            return (1 - (t - tb) / 0.35) * (0.3 + 0.4 * (t - (T_FULL - 6)) / 6)
    return 0.0


def frame(t):
    c = frame_canvas(t).astype(np.float32)
    hl = heart_level(t)
    if hl > 0:
        c = c * (1 - VIG[..., None] * hl * 0.8) + np.array([150, 10, 20], np.float32) * VIG[..., None] * hl * 0.8
    if T_FULL <= t < T_FULL + 0.12:
        c = c + (255 - c) * (1 - (t - T_FULL) / 0.12) * 0.7
    f = np.clip(c, 0, 255).astype(np.uint8).repeat(S, 0).repeat(S, 1)
    if T_FULL <= t < T_FULL + 0.4:
        amp = (1 - (t - T_FULL) / 0.4) * 12
        f = np.roll(f, (int(math.sin(t * 90) * amp), int(math.cos(t * 77) * amp)), (0, 1))
    im = Image.fromarray(f)
    overlay(im, t)
    return np.asarray(im)


# ================================================================ áudio
SR = E.SR
INTRO = [88, 87, 86, 85, 86, 85, 84, 83, 84, 83, 82, 81, 80, 79, 78, 77,
         76, 75, 74, 73, 74, 73, 72, 71, 72, 71, 70, 69, 68, 67, 66, 65]
M1 = [69, 68, 67, 66, 65, 66, 67, 68] * 2
M2 = [69, 70, 69, 68, 69, 70, 69, 68, 69, 70, 71, 72, 73, 74, 75, 76]
M3 = [76, 75, 74, 73, 72, 73, 74, 75] * 2
M4 = [76, 77, 76, 75, 76, 77, 76, 75, 76, 75, 74, 73, 72, 71, 70, 69]
BUMBLE = INTRO + M1 + M2 + M3 + M4 + M1 + M2 + M3 + M4 + INTRO + M1 + M2 + M3 + M4


def pluck(m, dur=0.22):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    vib = 1 + 0.004 * np.sin(2 * math.pi * 6 * tt)
    ph = np.cumsum(f * vib) / SR
    sig = np.sin(2 * math.pi * ph) + 0.5 * np.sin(4 * math.pi * ph) + 0.25 * np.sin(6 * math.pi * ph) + 0.12 * np.sin(8 * math.pi * ph)
    env = np.minimum(1, tt / 0.006) * np.exp(-tt * 9)
    return sig * env


def keynote(m, dur=0.9):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    sig = np.sin(2 * math.pi * f * tt) + 0.42 * np.sin(4 * math.pi * f * tt) * np.exp(-tt * 6)
    return sig * np.minimum(1, tt / 0.004) * np.exp(-tt * 3.5)


def wood(n, fres, dec):
    tt = np.arange(n) / SR
    return np.sin(2 * math.pi * fres * tt) * np.exp(-tt / dec)


def audio(path):
    total = END + 0.2
    n = int(total * SR)
    s = np.zeros(n)
    rr = random.Random(SEED)
    s += E.lp(E.noise(n, 3), 0.02) * 0.04
    # zumbido: cresce com o número de abelhas, some quando elas vão embora
    tt = np.arange(n) / SR
    nb = np.interp(tt, [f['t'] / WARP for f in FR], [f['n'] for f in FR])
    nb = np.where(tt < T_FULL, nb, nb * np.clip(1 - (tt - T_FULL) / 1.2, 0, 1))
    nb = np.where(tt >= END - 0.35, 1, nb)
    f0 = 210 * (1 + 0.03 * np.sin(2 * math.pi * 23 * tt))
    ph = np.cumsum(f0) / SR
    buzz = (2 * (ph % 1) - 1) * 0.6 + (2 * ((ph * 1.007) % 1) - 1) * 0.4
    s += E.lp(buzz, 0.12) * np.sqrt(nb) * 0.045
    # O Voo do Besouro puxado pelos favos (cada favo libera uma nota; a nota toca no ritmo da música)
    fts = [tf / WARP for (tf, c, nf) in SIM['fills'] if tf / WARP < T_FULL]
    for tv, m, role in schedule([[(m, 'm')] for m in BUMBLE], fts, 0.085, T_FULL, lead=8, max_speed=1.5, max_backlog=10):
        E.add(s, tv, pluck(m), 0.24)
    for (tb, i, x, y) in SIM['bounces']:
        tv = tb / WARP
        if tv < T_FULL:
            E.add(s, tv, wood(int(0.03 * SR), 520, 0.006), 0.05)
    for tv, px, py in SPAWNS:                              # abelha nova: bzzt subindo
        nn = int(0.25 * SR)
        t2 = np.arange(nn) / SR
        fz = 260 + 500 * t2
        z = np.sign(np.sin(2 * math.pi * np.cumsum(fz) / SR)) * np.sin(math.pi * t2 / 0.25)
        E.add(s, tv, E.lp(z, 0.2), 0.08)
    tk = T_FULL - 6.0
    while tk < T_FULL:
        E.add(s, tk, wood(int(0.03 * SR), 2400, 0.004), 0.12)
        tk += 0.5
    for tb in BEATS:
        for off, g in ((0.0, 0.5), (0.13, 0.32)):
            nn = int(0.14 * SR)
            t2 = np.arange(nn) / SR
            E.add(s, tb + off, np.sin(2 * math.pi * np.cumsum(70 * np.exp(-t2 * 9) + 38) / SR) * np.exp(-t2 * 22), g)
    # ENCHEU: acorde de Lá maior, fanfarra e brilho
    for m, g in ((57, 0.4), (61, 0.3), (64, 0.3), (69, 0.3)):
        E.add(s, T_FULL, keynote(m, 1.6), g)
    for k, m in enumerate((69, 73, 76, 81)):
        nn = int(0.12 * SR)
        E.add(s, T_FULL + 0.3 + k * 0.09, E.sq(E.midi(m), nn, 0.5) * E.adsr(nn, a=0.002, dec=0.04, sus=0.6, r=0.02), 0.1)
    nn = int(0.7 * SR)
    for m in (69, 73, 76):
        E.add(s, T_FULL + 0.66, E.sq(E.midi(m + 12), nn, 0.25, vib=0.01) * E.adsr(nn, a=0.004, dec=0.2, sus=0.5, r=0.2), 0.05)
    for k in range(10):
        E.add(s, T_FULL + 0.1 + k * 0.08, pluck(93 + (k % 5) * 2, 0.3), 0.06)
    for k in range(8):                                     # mel escorrendo de volta
        E.add(s, T_DRAIN + k * 0.07, wood(int(0.06 * SR), 380 - 20 * k, 0.012), 0.12)
    s = s / (np.abs(s).max() + 1e-9) * 0.85
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


def capa():
    t = T_FULL - 3.0
    f = frame_canvas(t).repeat(S, 0).repeat(S, 1)
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 520, FW, 1330), fill=(16, 12, 30, 125))
    E.draw_line(d, FW / 2, 590, [('SERÁ QUE AS', WHITE)], 150)
    E.draw_line(d, FW / 2, 760, [('ABELHAS', GOLD)], 260, stroke=16)
    E.draw_line(d, FW / 2, 1040, [('ENCHEM A COLMEIA?', WHITE)], 120, stroke=10)
    out = os.path.join(OUTDIR, 'capa-abelhas.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


if __name__ == '__main__':
    if os.environ.get('PLAN'):
        fl = [f[0] / WARP for f in SIM['fills']]
        print(f'seed {SEED}: {NC} alvéolos; enche na sim {FULL_SIM:.2f}s → vídeo {T_FULL:.2f}s (warp {WARP:.3f}); fim {END:.2f}s')
        print('50%:', round(fl[NC // 2], 1), '90%:', round(fl[int(NC * .9)], 1), 'faltam 3 em', round(fl[-3], 1),
              'abelhas no fim:', FR[-1]['n'])
        raise SystemExit
    if os.environ.get('CAPA'):
        capa(); raise SystemExit
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            tv = T_FULL + float(v[1:]) if v.startswith('b') else float(v)
            Image.fromarray(frame(tv)).save(os.path.join(OUTDIR, f'still_{v}.png'))
        print('ok'); raise SystemExit
    wav = os.path.join(OUTDIR, 'abelhas.wav')
    audio(wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k',
                          '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    for i in range(int(round(END * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(OUT, f'{END:.2f}s')
