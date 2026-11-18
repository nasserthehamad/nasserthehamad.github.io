#!/usr/bin/env python3
"""Copa das bandeiras (versão grande): 48 países numa arena de pedra em forma de estádio com um POÇO DE LAVA no meio.
Etapa 1: duas pás girando. Etapa 2: a lava cresce + 3 rebatedores orbitando. Etapa 3: a lava cresce de novo e as paredes
fecham (o chão em volta vira lava). Quem cai na lava é eliminado. Final Brasil x Argentina (países distribuídos depois
da física). Música: "Na Gruta do Rei da Montanha" acelerando por etapa. Sem narração.
Uso: python3 copa.py   (PLAN=1 · STILLS=0.5,9.5,b-2,b+1 · CAPA=1)"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REINO = os.environ.get('REINO', '/home/claude/reino')
sys.path.insert(0, REINO)
import ep1hd as E
import folk as F
import world2 as W
import flags as FL
import sim_copa as SC
from sim_copa import simulate, CX, CY, HSEG, RC0, RB, SPIN, ARM, ARM_W, BUMP_R, BUMP_ORB

FW, FH, FPS, S = 1080, 1920, 30, 3
CW, CH = 360, 640
SEED = int(os.environ.get('SEED', '150'))
LAVAS = (15.0, 24.0, 31.0)
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.environ.get('OUT', os.path.join(OUTDIR, 'copa.mp4'))
WHITE, GOLD, RED, YEL, LBLUE, ORANGE = (255, 255, 255), (255, 208, 72), (255, 96, 86), (254, 223, 0), (140, 196, 240), (255, 150, 50)

SIM = simulate(n=48, seed=SEED, tmax=45, lavas=LAVAS)
FR = SIM['frames']
T_WIN = SIM['end']
ELIMS = SIM['elims']
TS2, TS3 = SIM['ts2'], SIM['ts3']
T_DUEL = ELIMS[-2][0]
T_BACK = T_WIN + 3.0
END = T_WIN + 3.6
NB = len(FR[0]['pos'])

# ---------------------------------------------------------------- quem é quem (distribuído depois da física)
names = [c[0] for c in FL.COUNTRIES]
order_out = [i for _, i in ELIMS]
WIN, RUNNER = SIM['winner'], order_out[-1]
COUNTRY = {WIN: names.index('BRASIL'), RUNNER: names.index('ARGENTINA')}
TOP = ['FRANÇA', 'PORTUGAL', 'ALEMANHA', 'ESPANHA', 'INGLATERRA', 'HOLANDA']      # 3º ao 8º lugar
for k, nm in enumerate(TOP):
    COUNTRY[order_out[-2 - k]] = names.index(nm)
pool = [k for k in range(len(names)) if k not in COUNTRY.values()]
random.Random(SEED * 101).shuffle(pool)
for i in range(NB):
    if i not in COUNTRY:
        COUNTRY[i] = pool.pop()
BALL = {i: FL.ball(FL.COUNTRIES[COUNTRY[i]][1]()) for i in range(NB)}
OUT_T = {i: t for t, i in ELIMS}

yy, xx = np.mgrid[0:CH, 0:CW]
BAY = np.tile(W.BAYER, (CH // 4, CW // 4))
# distância de cada pixel ao segmento da arena (pra saber dentro/fora/parede)
_sy = np.clip(yy, CY - HSEG, CY + HSEG)
DSEG = np.hypot(xx - CX, yy - _sy).astype(np.float32)
DC = np.hypot(xx - CX, yy - CY).astype(np.float32)
ANG = np.arctan2(yy - CY, xx - CX).astype(np.float32)


def fr_at(t):
    k = min(int(round(min(t, T_WIN) * FPS)), len(FR) - 1)
    return FR[k], k


# ================================================================ chão
def build_ground():
    g = np.zeros((CH, CW, 3), np.float32)
    gn = W.vnoise(CH, CW, 30, 11, 3)
    lvl = np.clip(np.floor(gn * 3.2 + (BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
    g[:] = W.GREENS[lvl]
    rr = random.Random(5)
    for _ in range(2000):
        x, y = rr.randrange(CW), rr.randrange(CH)
        c0 = (88, 144, 64) if rr.random() < 0.7 else (78, 132, 58)
        for dx, dy in ((0, 0), (1, -1), (2, 0)):
            if 0 <= x + dx < CW and 0 <= y + dy < CH:
                g[y + dy, x + dx] = c0
    inside = DSEG < RC0 + 2
    sn = W.vnoise(CH, CW, 10, 41, 3)
    stone = np.array([(52, 46, 50), (64, 58, 62), (78, 70, 72)], np.float32)
    sl = np.clip(np.floor(sn * 3.3 + (BAY - 0.5) * 0.9 - 0.15), 0, 2).astype(int)
    g[inside] = stone[sl[inside]]
    cr = W.vnoise(CH, CW, 7, 93, 2)
    crack = inside & (np.abs(cr - 0.5) < 0.012)
    g[crack] = (30, 24, 28)
    # anel de pedras (parede original) e sombra
    wall = (DSEG >= RC0) & (DSEG < RC0 + 7)
    brick = ((np.floor(ANG * 40 + (DSEG > RC0 + 3.5) * 0.5) % 2) == 0)
    g[wall] = np.where(brick[wall][:, None], np.array((122, 116, 118), np.float32), np.array((104, 98, 102), np.float32))
    g[wall & (DSEG > RC0 + 5.5)] = (60, 54, 58)
    g[wall & (DSEG < RC0 + 1)] = (150, 144, 146)
    sh = (DSEG >= RC0 + 7) & (DSEG < RC0 + 11)
    g[sh] *= 0.72
    vg = np.clip((np.hypot((xx - CX) / 230, (yy - 360) / 420) - 0.78) * 0.9, 0, 0.35)
    g *= (1 - vg)[..., None]
    g[:200] *= np.linspace(0.68, 1.0, 200)[:, None, None]
    return g


GROUND = build_ground()
LN1 = W.vnoise(CH, CW, 9, 7, 3).astype(np.float32)
LN2 = W.vnoise(CH, CW, 5, 19, 2).astype(np.float32)
LAVA_PAL = np.array([(90, 10, 8), (170, 30, 10), (230, 80, 14), (255, 150, 30), (255, 220, 90)], np.float32)


def lava_color(mask, t):
    """cor da lava nos pixels da máscara (fluxo animado)."""
    ys, xs = np.nonzero(mask)
    a = ANG[ys, xs] + t * 0.35
    rr_ = DC[ys, xs]
    u = (np.cos(a) * rr_ * 0.9 + 400).astype(int) % CW
    v = (np.sin(a) * rr_ * 0.9 + 400 + int(t * 8)).astype(int) % CH
    n = LN1[v, u] * 0.7 + LN2[(ys + int(t * 14)) % CH, xs] * 0.3
    lv = np.clip(n * 4.6 - 0.6 + (BAY[ys, xs] - 0.5) * 0.6, 0, 4).astype(int)
    return ys, xs, LAVA_PAL[lv]


def paint_lava(img, t, lr, cap):
    # poço
    m = DC < lr
    ys, xs, col = lava_color(m, t)
    img[ys, xs] = col
    rim = (DC >= lr) & (DC < lr + 3)
    img[rim] = img[rim] * 0.55 + np.array((60, 30, 20)) * 0.45
    glow = np.clip(1 - (DC - lr) / 30, 0, 1) * (DC >= lr + 3) * (DSEG < cap)
    img[:] = img + (np.array((255, 110, 30)) - img) * (glow[..., None] * 0.35)
    # chão derretendo (etapa 3): entre a parede nova e a original vira lava
    if cap < RC0 - 0.5:
        m2 = (DSEG >= cap) & (DSEG < RC0)
        ys, xs, col = lava_color(m2, t)
        img[ys, xs] = col
        edge = (DSEG >= cap - 3) & (DSEG < cap + 2)
        bricks = ((np.floor(ANG * 40) % 2) == 0)
        img[edge] = np.where(bricks[edge][:, None], np.array((112, 104, 106)), np.array((84, 78, 82)))
        g2 = np.clip(1 - (cap - DSEG) / 22, 0, 1) * (DSEG < cap - 3)
        img[:] = img + (np.array((255, 110, 30)) - img) * (g2[..., None] * 0.3)
    # bolhas
    r = random.Random(int(t * 6))
    for _ in range(4):
        a = r.uniform(0, 2 * math.pi); d = r.uniform(0, max(1, lr - 4))
        bx, by = int(CX + d * math.cos(a)), int(CY + d * math.sin(a))
        ph = (t * 6) % 1
        rad = 1 + int(ph * 3)
        for k in range(-rad, rad + 1):
            for q in (-rad, rad):
                for (x_, y_) in ((bx + k, by + q), (bx + q, by + k)):
                    if 0 <= x_ < CW and 0 <= y_ < CH and DC[y_, x_] < lr:
                        img[y_, x_] = (255, 236, 150)


# ================================================================ objetos móveis
def draw_spinners(d, angs):
    for (pv, w), th in zip(SPIN, angs):
        u = (math.cos(th), math.sin(th))
        a0 = (pv[0] - u[0] * ARM, pv[1] - u[1] * ARM)
        a1 = (pv[0] + u[0] * ARM, pv[1] + u[1] * ARM)
        for k, al in ((2, 35), (1, 70)):                  # rastro
            tk = th - w / FPS * k * 0.8
            uk = (math.cos(tk), math.sin(tk))
            d.line([(pv[0] - uk[0] * ARM, pv[1] - uk[1] * ARM), (pv[0] + uk[0] * ARM, pv[1] + uk[1] * ARM)],
                   fill=(210, 210, 220, al), width=5)
        d.line([(a0[0] + 2, a0[1] + 3), (a1[0] + 2, a1[1] + 3)], fill=(0, 0, 0, 90), width=8)
        d.line([a0, a1], fill=(30, 28, 34, 255), width=9)
        d.line([a0, a1], fill=(150, 152, 168, 255), width=6)
        d.line([(a0[0], a0[1] - 1), (a1[0], a1[1] - 1)], fill=(210, 212, 226, 255), width=2)
        for e in (a0, a1):
            d.ellipse([e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4], fill=(200, 50, 40, 255), outline=(30, 20, 20, 255))
        d.ellipse([pv[0] - 7, pv[1] - 7, pv[0] + 7, pv[1] + 7], fill=(30, 28, 34, 255))
        d.ellipse([pv[0] - 5, pv[1] - 5, pv[0] + 5, pv[1] + 5], fill=(236, 190, 60, 255))
        d.ellipse([pv[0] - 2, pv[1] - 2, pv[0] + 2, pv[1] + 2], fill=(120, 90, 30, 255))


BUMP_HITS = {}
for _t, _kind, _i in SIM['hits']:
    if _kind == 'bump':
        BUMP_HITS.setdefault(round(_t * FPS), 1)


def draw_bumpers(d, t, bang):
    if TS2 is None or t < TS2:
        return
    sc = min(1.0, (t - TS2) / 0.35)
    sc = 1.2 * sc if sc < 0.8 else 1.0 + 0.2 * (1 - sc) / 0.2
    flash = any(abs(round(t * FPS) - k) <= 2 for k in BUMP_HITS) and (int(t * 20) % 2 == 0)
    for k in range(3):
        a = bang + k * 2 * math.pi / 3
        bx, by = CX + BUMP_ORB * math.cos(a), CY + BUMP_ORB * math.sin(a)
        r = BUMP_R * sc
        d.ellipse([bx - r + 2, by - r + 3, bx + r + 2, by + r + 3], fill=(0, 0, 0, 90))
        d.ellipse([bx - r - 1, by - r - 1, bx + r + 1, by + r + 1], fill=(30, 20, 24, 255))
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 250, 240, 255) if flash else (226, 52, 60, 255))
        d.ellipse([bx - r * 0.62, by - r * 0.62, bx + r * 0.62, by + r * 0.62], fill=(255, 255, 255, 255))
        d.ellipse([bx - r * 0.35, by - r * 0.35, bx + r * 0.35, by + r * 0.35], fill=(255, 200, 60, 255))


# ================================================================ bolinhas
SHAD = (((np.mgrid[0:10, 0:24][1] - 11.5) / 11.0) ** 2 + ((np.mgrid[0:10, 0:24][0] - 4.5) / 4.0) ** 2) <= 1


def _clip(m, x0, y0):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return None
    return xa, ya, xb, yb, m[ya - y0:yb - y0, xa - x0:xb - x0]


def draw_ball(img, i, x, y, sc=1.0, shadow=True, burn=0.0):
    rgb, m = BALL[i]
    if sc != 1.0:
        n = max(3, int(round(22 * sc)))
        idx = np.clip((np.arange(n) * 22 / n).astype(int), 0, 21)
        rgb, m = rgb[idx][:, idx], m[idx][:, idx]
    if burn > 0:
        rgb = (rgb.astype(np.float32) * (1 - burn) + np.array((255, 90, 20)) * burn * 0.8).astype(np.uint8)
    h = m.shape[0]
    xi, yi = int(round(x)), int(round(y))
    if shadow:
        cl = _clip(SHAD, xi - 12 + 2, yi - 5 + h // 2)
        if cl:
            xa, ya, xb, yb, mm = cl
            reg = img[ya:yb, xa:xb]; reg[mm] = (reg[mm] * 0.72).astype(img.dtype)
    x0, y0 = xi - h // 2, yi - h // 2
    cl = _clip(m, x0, y0)
    if cl:
        xa, ya, xb, yb, mm = cl
        img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - x0:xb - x0][mm]


def sink(img, i, t):
    """bolinha caindo na lava: escorrega pro centro, encolhe, avermelha; fumaça e faíscas."""
    te = OUT_T[i]
    k = min(int(round(te * FPS)), len(FR) - 1)
    p = FR[k]['pos'][i]
    dt = t - te
    q = min(1.0, dt / 0.5)
    x = p[0] + (CX - p[0]) * 0.25 * q
    y = p[1] + (CY - p[1]) * 0.25 * q
    if q < 1:
        draw_ball(img, i, x, y, 1 - 0.75 * q, shadow=False, burn=q)
    r = random.Random(i * 7)
    for s_ in range(10):
        a = r.uniform(0, 2 * math.pi); sp = r.uniform(20, 60)
        sx, sy = x + math.cos(a) * sp * dt, y + math.sin(a) * sp * dt - 40 * dt
        if dt < 0.6 and 0 <= sx < CW and 0 <= sy < CH:
            img[int(sy), int(sx)] = (255, 200, 80) if s_ % 2 else (255, 120, 40)
    if dt < 0.9:
        for s_ in range(5):
            sx = int(x + r.uniform(-5, 5)); sy = int(y - 28 * dt - s_ * 3)
            rad = 2 + int(4 * dt)
            al = max(0.0, 0.6 - dt * 0.6)
            ys_ = slice(max(0, sy - rad), min(CH, sy + rad)); xs_ = slice(max(0, sx - rad), min(CW, sx + rad))
            img[ys_, xs_] = (img[ys_, xs_] * (1 - al) + np.array((70, 66, 70)) * al).astype(img.dtype)


# ================================================================ torcida
FOLK = [('Valdemir', 'vaqueiro', 26, 632), ('Luiza', 'santa', 22, 236), ('pixoto', 'cidadão', 338, 230),
        ('Edilson', 'espadachim', 336, 634)]
FOLK_SPR = {}
for _n, _r, _, _ in FOLK:
    _a = F.folk(_n, _r, 0)
    FOLK_SPR[_n] = (_a[..., :3].astype(np.uint8), _a[..., 3] > 0.5)


def draw_folk(img, t):
    for i, (nm, rl, fx, fy) in enumerate(FOLK):
        rgb, m = FOLK_SPR[nm]
        jump = int(round(abs(math.sin((t - T_WIN) * 9 + i)) * 7)) if T_WIN <= t < T_WIN + 2.2 else 0
        y0 = fy - 42 - jump
        cl = _clip(m, fx - 15, y0)
        if cl:
            xa, ya, xb, yb, mm = cl
            img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - (fx - 15):xb - (fx - 15)][mm]
        if T_WIN + 0.05 <= t < T_WIN + 2.2:
            W.qmark(img, fx - 3, y0 - 8, bang=True)


# ================================================================ quadro
CONF = [(random.Random(k).uniform(0, CW), random.Random(k + 99).uniform(-60, 0), random.Random(k + 7).uniform(40, 120),
         random.Random(k + 3).choice([(0, 156, 59), (254, 223, 0), (0, 39, 118), (255, 255, 255)])) for k in range(200)]


def frame_canvas(t):
    img = GROUND.copy()
    st, k = fr_at(t)
    if t >= T_BACK:
        st = FR[0]
    lr, cap = st['lava'], st['cap']
    paint_lava(img, t, lr, cap)
    img8 = np.clip(img, 0, 255).astype(np.uint8)
    pil = Image.fromarray(img8)
    d = ImageDraw.Draw(pil, 'RGBA')
    draw_spinners(d, st['spin'] if t < T_WIN else [w * T_WIN for _, w in SPIN])
    if t < T_BACK:
        draw_bumpers(d, t, st['bump'])
    img8 = np.asarray(pil).copy()
    if t < T_WIN:
        items = [(st['pos'][i][1], i) for i in range(NB) if st['alive'][i]]
        for _, i in sorted(items):
            draw_ball(img8, i, *st['pos'][i])
        for te, i in ELIMS:
            if 0 <= t - te < 0.9:
                sink(img8, i, t)
    elif t < T_BACK:
        dt = t - T_WIN
        if 0 <= t - OUT_T[RUNNER] < 0.9:
            sink(img8, RUNNER, t)
        p = FR[-1]['pos'][WIN]
        q = 1 - (1 - min(1.0, dt / 0.6)) ** 3
        draw_ball(img8, WIN, p[0] + (CX - p[0]) * q, p[1] + (CY - 60 - p[1]) * q, 1.0 + 2.8 * q)
        for (cx, cy, sp, col) in CONF:
            yc = cy + sp * dt * 1.4
            xc = cx + 6 * math.sin(dt * 5 + cx)
            if 0 <= yc < CH - 1 and 0 <= xc < CW - 1:
                img8[int(yc), int(xc)] = col
                img8[int(yc) + 1, int(xc)] = col
    else:
        q = min(1.0, (t - T_BACK) / 0.35)
        for i in range(NB):
            draw_ball(img8, i, *FR[0]['pos'][i], 0.4 + 0.6 * q)
    draw_folk(img8, t)
    return img8


# ---------------------------------------------------------------- textos
def name(i):
    return FL.COUNTRIES[COUNTRY[i]][0]


BANNERS = [(0.0, 'ETAPA 1', '48 PAÍSES'), (TS2, 'ETAPA 2', 'A LAVA SUBIU'), (TS3, 'ETAPA 3', 'AS PAREDES FECHAM')]


def overlay(im, t):
    d = ImageDraw.Draw(im, 'RGBA')
    st, _ = fr_at(t)
    left = int(st['alive'].sum()) if t < T_WIN else 1
    if t >= T_BACK:
        left = NB
    if t < T_WIN or t >= T_BACK:
        E.draw_line(d, FW / 2, 50, [('QUAL PAÍS', WHITE)], 130)
        E.draw_line(d, FW / 2, 175, [('SOBREVIVE?', GOLD)], 170, stroke=12)
        if left > 2:
            E.draw_line(d, FW / 2, 375, [('RESTAM ', WHITE), (f'{left}', GOLD)], 100, stroke=8)
            last = [(te, i) for te, i in ELIMS if te <= t and t - te < 0.9]
            if last and t < T_BACK:
                E.draw_line(d, FW / 2, 490, [('TCHAU, ', WHITE), (name(last[-1][1]), RED)], 62, stroke=6)
        else:
            hot = math.sin(t * 8) > 0
            E.draw_line(d, FW / 2, 365, [('FINAL', RED if hot else GOLD)], 110, stroke=10)
            E.draw_line(d, FW / 2, 488, [('BRASIL', YEL), (' x ', WHITE), ('ARGENTINA', LBLUE)], 84, stroke=8)
        for tb, a, b in BANNERS:
            if tb is not None and 0 <= t - tb < 1.1 and t < T_WIN:
                q = min(1.0, (t - tb) / 0.15)
                d.rectangle((140, 1040, 940, 1300), fill=(16, 12, 30, 150))
                d.rectangle((140, 1040, 940, 1300), outline=(255, 208, 72, 200), width=5)
                E.draw_line(d, FW / 2, 1065, [(a, GOLD)], int(110 + 30 * q), stroke=10)
                E.draw_line(d, FW / 2, 1200, [(b, WHITE if tb == 0 else ORANGE)], 70, stroke=6)
    else:
        q = min(1.0, (t - T_WIN) / 0.15)
        E.draw_line(d, FW / 2, 80, [('CAMPEÃO!', GOLD)], int(150 + 60 * q), stroke=14)
        if t > T_WIN + 0.35:
            E.draw_line(d, FW / 2, 300, [('BRASIL', YEL)], 190, stroke=14)


VIG = np.clip((np.hypot((xx - CX) / 200, (yy - 360) / 380) - 0.7) / 0.6, 0, 1).astype(np.float32)


def make_beats():
    bt, tb = [], T_DUEL
    while tb < T_WIN - 0.15:
        bt.append(tb)
        tb += 0.75 - 0.35 * (tb - T_DUEL) / max(0.1, T_WIN - T_DUEL)
    return bt


BEATS = make_beats()


def heart_level(t):
    if not (T_DUEL <= t < T_WIN):
        return 0.0
    for tb in BEATS:
        if tb <= t < tb + 0.35:
            return (1 - (t - tb) / 0.35) * 0.55
    return 0.0


def frame(t):
    c = frame_canvas(t).astype(np.float32)
    hl = heart_level(t)
    if hl > 0:
        c = c * (1 - VIG[..., None] * hl * 0.8) + np.array([150, 10, 20], np.float32) * VIG[..., None] * hl * 0.8
    for tb in (TS2, TS3):
        if tb is not None and 0 <= t - tb < 0.15:
            c = c + (np.array((255, 140, 60)) - c) * 0.35 * (1 - (t - tb) / 0.15)
    if T_WIN <= t < T_WIN + 0.12:
        c = c + (255 - c) * (1 - (t - T_WIN) / 0.12) * 0.7
    f = np.clip(c, 0, 255).astype(np.uint8).repeat(S, 0).repeat(S, 1)
    for tb in (TS2, TS3):
        if tb is not None and 0 <= t - tb < 0.5:
            amp = (1 - (t - tb) / 0.5) * 10
            f = np.roll(f, (int(math.sin(t * 90) * amp), int(math.cos(t * 77) * amp)), (0, 1))
    im = Image.fromarray(f)
    overlay(im, t)
    return np.asarray(im)


# ================================================================ áudio
SR = E.SR
_P1 = [59, 61, 62, 64, 66, 62, 66, None, 65, 61, 65, None, 64, 60, 64, None,
       59, 61, 62, 64, 66, 62, 66, 71, 69, 66, 62, 66, 69, None, None, None]
_P2 = [66, 68, 70, 71, 73, 70, 73, None, 74, 70, 74, None, 73, 70, 73, None,
       66, 68, 70, 71, 73, 70, 73, None, 74, 70, 74, None, 73, None, None, None]
MOUNTAIN = (_P1 + _P2) * 10


def pluck(m, dur=0.3):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    sig = np.sin(2 * math.pi * f * tt) + 0.5 * np.sin(4 * math.pi * f * tt) + 0.22 * np.sin(6 * math.pi * f * tt)
    return sig * np.minimum(1, tt / 0.005) * np.exp(-tt * 7)


def bass(m, dur=0.4):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    return (np.sin(2 * math.pi * f * tt) + 0.3 * np.sin(4 * math.pi * f * tt)) * np.exp(-tt * 6)


def tempo(t):
    if t < TS2:
        return 0.21 - 0.03 * t / TS2
    if t < TS3:
        return 0.16 - 0.03 * (t - TS2) / (TS3 - TS2)
    if t < T_DUEL:
        return 0.125 - 0.02 * (t - TS3) / max(0.1, T_DUEL - TS3)
    return 0.095


def audio(path):
    total = END + 0.2
    n = int(total * SR)
    s = np.zeros(n)
    rr = random.Random(SEED)
    tt = np.arange(n) / SR
    rumble = E.lp(E.noise(n, 3), 0.015) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.7 * tt))
    s += rumble * 0.12
    for k in range(int(total * 3)):                        # bolhas da lava
        tb = rr.uniform(0, total)
        nn = int(0.08 * SR); t2 = np.arange(nn) / SR
        E.add(s, tb, np.sin(2 * math.pi * np.cumsum(180 + 400 * t2) / SR) * np.exp(-t2 * 40), 0.05)
    t, j = 0.1, 0
    while t < T_WIN - 0.05:
        m = MOUNTAIN[j % len(MOUNTAIN)]
        if m is not None:
            E.add(s, t, pluck(m + 12), 0.25)
        if j % 4 == 0:
            E.add(s, t, bass(47 if (j // 32) % 2 == 0 else 42), 0.3)
        t += tempo(t)
        j += 1
    last = {}
    for th, kind, i in SIM['hits']:
        if th >= T_WIN:
            continue
        if kind == 'bump':
            nn = int(0.18 * SR); t2 = np.arange(nn) / SR
            E.add(s, th, np.sin(2 * math.pi * np.cumsum(300 + 500 * np.exp(-t2 * 20)) / SR) * np.exp(-t2 * 14), 0.16)
        elif kind == 'spin' and th - last.get('spin', -1) > 0.06:
            last['spin'] = th
            nn = int(0.06 * SR); t2 = np.arange(nn) / SR
            E.add(s, th, np.sin(2 * math.pi * 160 * t2) * np.exp(-t2 * 50), 0.18)
        elif kind == 'wall' and th - last.get('wall', -1) > 0.05 and rr.random() < 0.4:
            last['wall'] = th
            nn = int(0.02 * SR)
            E.add(s, th, np.sin(2 * math.pi * 1100 * np.arange(nn) / SR) * np.exp(-np.arange(nn) / SR * 300), 0.03)
    for k, (te, i) in enumerate(ELIMS):                    # caiu na lava: tsss + plop
        nn = int(0.45 * SR); t2 = np.arange(nn) / SR
        hiss = (E.noise(nn, 50 + k) - E.lp(E.noise(nn, 50 + k), 0.2)) * np.exp(-t2 * 6)
        E.add(s, te, hiss, 0.22)
        nn = int(0.2 * SR); t2 = np.arange(nn) / SR
        E.add(s, te, np.sin(2 * math.pi * np.cumsum(500 * np.exp(-t2 * 8) + 90) / SR) * np.exp(-t2 * 10), 0.25)
        if NB - (k + 1) <= 6:
            nn = int(0.9 * SR); t2 = np.arange(nn) / SR
            E.add(s, te + 0.05, E.lp(E.noise(nn, 300 + k), 0.05) * np.sin(math.pi * t2 / 0.9), 1.1)
    for tb in (TS2, TS3):                                  # etapa nova: gongo grave
        nn = int(1.5 * SR); t2 = np.arange(nn) / SR
        gong = (np.sin(2 * math.pi * 73 * t2) + 0.6 * np.sin(2 * math.pi * 110 * t2) + 0.3 * np.sin(2 * math.pi * 196 * t2))
        E.add(s, tb, gong * np.exp(-t2 * 2.2), 0.5)
    for tb in BEATS:
        for off, g in ((0.0, 0.5), (0.13, 0.32)):
            nn = int(0.14 * SR); t2 = np.arange(nn) / SR
            E.add(s, tb + off, np.sin(2 * math.pi * np.cumsum(70 * np.exp(-t2 * 9) + 38) / SR) * np.exp(-t2 * 22), g)
    nn = int(2.6 * SR); t2 = np.arange(nn) / SR
    E.add(s, T_WIN, E.lp(E.noise(nn, 999), 0.09) * np.minimum(1, t2 / 0.15) * np.exp(-t2 * 0.9), 1.6)
    for k, m in enumerate((71, 75, 78, 83)):
        nb = int(0.12 * SR)
        E.add(s, T_WIN + 0.2 + k * 0.1, E.sq(E.midi(m), nb, 0.5) * E.adsr(nb, a=0.002, dec=0.04, sus=0.6, r=0.02), 0.11)
    nb = int(0.9 * SR)
    for m in (71, 75, 78):
        E.add(s, T_WIN + 0.6, E.sq(E.midi(m + 12), nb, 0.25, vib=0.01) * E.adsr(nb, a=0.004, dec=0.2, sus=0.5, r=0.3), 0.06)
        E.add(s, T_WIN + 0.6, bass(m - 24, 1.2), 0.2)
    s = s / (np.abs(s).max() + 1e-9) * 0.85
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


def capa():
    t = TS3 + 2.5
    f = frame_canvas(t).repeat(S, 0).repeat(S, 1)
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 0, FW, 600), fill=(16, 12, 30, 130))
    E.draw_line(d, FW / 2, 70, [('48 PAÍSES', WHITE)], 150)
    E.draw_line(d, FW / 2, 230, [('1 POÇO DE LAVA', ORANGE)], 120, stroke=10)
    E.draw_line(d, FW / 2, 400, [('QUEM SOBREVIVE?', GOLD)], 120, stroke=10)
    out = os.path.join(OUTDIR, 'capa-copa.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


if __name__ == '__main__':
    if os.environ.get('PLAN'):
        print(f'seed {SEED}: etapa2 {TS2:.1f}s, etapa3 {TS3:.1f}s, final {T_DUEL:.1f}s, campeão {T_WIN:.2f}s, fim {END:.2f}s')
        print('últimos 8:', [name(i) for _, i in ELIMS[-7:]], '+ BRASIL')
        raise SystemExit
    if os.environ.get('CAPA'):
        capa(); raise SystemExit
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            tv = T_WIN + float(v[1:]) if v.startswith('b') else float(v)
            Image.fromarray(frame(tv)).save(os.path.join(OUTDIR, f'copa_{v}.png'))
        print('ok'); raise SystemExit
    wav = os.path.join(OUTDIR, 'copa.wav')
    audio(wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k',
                          '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    for i in range(int(round(END * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(OUT, f'{END:.2f}s')
