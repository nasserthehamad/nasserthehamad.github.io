#!/usr/bin/env python3
"""Brasa — Ep. 4 "A Estátua". Formato curto (~26 s): o pano voa da estátua dos fundadores no 1º segundo,
Julielen e Robson entram como fundadores, a Julielen acha uma pedra que brilha na base, 17 moradores novos no palco,
e a Rafaela leva a pedra pra floresta com a Andréa e a Alexandra. Sem voz por padrão (TIMING4=json + VOICE=mp3)."""
import os, math, random, subprocess, wave, json
import numpy as np
from PIL import Image, ImageDraw
import world2 as W
import folk as F
import build as B
import ep1hd as E
import ep2 as P

FW, FH, FPS = 1080, 1920, 30
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
WHITE, GOLD, TEAL = (255, 255, 255), (255, 208, 72), (96, 226, 214)
N_FOLLOW = int(os.environ.get('N', '67'))
GOAL = 100
OLD = list(F.FOUNDERS) + list(F.MISSED_FOUNDERS)
EP2 = list(F.NEW_EP2)
NEW = list(F.NEW_EP4)
NAMED = OLD + EP2 + NEW
ANON = max(0, N_FOLLOW - len(NAMED))
PEOPLE = NAMED + [(f'anon{k}', '') for k in range(ANON)]
NP = len(PEOPLE)
IDX = {n: i for i, (n, _) in enumerate(PEOPLE)}
TAGROLE = {'Lila': '???'}
EXPED = ['Rafaela', 'Andréa', 'Alexandra']

# ---------------------------------------------------------------- tempo
T = dict(S2=2.8, S2B=5.6, S3=8.6, S3B=10.1, S5=11.6, S4=18.6, S4B=20.0, S6=21.6, TEND=25.6,
         D2=0.35, D2B=0.6, D4=0.35, D6=0.4)
_tj = os.environ.get('TIMING4')
if _tj:
    T.update(json.load(open(_tj)))
S2, S2B, S3, S3B, S5, S4, S4B, S6, TEND = [T[k] for k in ('S2', 'S2B', 'S3', 'S3B', 'S5', 'S4', 'S4B', 'S6', 'TEND')]
D2, D2B, D4, D6 = T['D2'], T['D2B'], T['D4'], T['D6']
SIZES = [4, 4, 3, 3, 3]
NB = len(SIZES)
GROUPS, _k = [], 0
for s_ in SIZES:
    GROUPS.append(NEW[_k:_k + s_]); _k += s_
STAGE0 = S5 + 0.7
BT = T.get('BT') or [STAGE0 + b * (S4 - STAGE0) / NB for b in range(NB)]
STAGE0 = BT[0]
XF = 0.4
CLOTH0, CLOTH1 = 0.35, 1.05      # pano voando

STX, STY = 84, 540               # estátua (centro, base)
STAGE_Y = 486
SLOTS = {4: [130, 172, 214, 256], 3: [151, 193, 235]}
STAGE_CX = 193


def tod(t):
    if t < S3:
        return 0.0
    if t < S5:
        return 0.6 + 0.5 * (t - S3) / (S5 - S3)
    if t < S4:
        return 1.1 + 0.6 * (t - S5) / (S4 - S5)
    return min(2.0, 1.7 + 0.3 * (t - S4) / 0.6)


# ---------------------------------------------------------------- multidão
def crowd_positions(n, seed=5):
    r = random.Random(seed)
    pts, tries = [], 0
    while len(pts) < n and tries < 40000:
        tries += 1
        x, y = r.uniform(96, 266), r.uniform(396, 468)
        if ((x - 181) / 84) ** 2 + ((y - 433) / 40) ** 2 > 1:
            continue
        if ((x - 180) / 16) ** 2 + ((y - 424) / 8) ** 2 < 1:
            continue
        if any((x - a) ** 2 + ((y - b) * 1.6) ** 2 < 10.4 ** 2 for a, b in pts):
            continue
        pts.append((x, y))
    while len(pts) < n:
        pts.append((r.uniform(110, 250), r.uniform(400, 466)))
    return pts


CROWD = crowd_positions(NP)
# quem tem papel na história fica na borda da frente da multidão (fácil de achar)
for _n, _p in (('Alerrandro', (40, 548)), ('Julielen', (226, 462)), ('Robson', (240, 458)),
               ('Rafaela', (204, 404)), ('Andréa', (214, 400)), ('Alexandra', (196, 398))):
    _i = IDX[_n]
    _j = min(range(NP), key=lambda j: (CROWD[j][0] - _p[0]) ** 2 + (CROWD[j][1] - _p[1]) ** 2)
    CROWD[_i], CROWD[_j] = CROWD[_j], CROWD[_i]
CROWD[IDX['Alerrandro']] = (40, 548)

JUL_SPOT, ROB_SPOT = (130, 548), (172, 550)
DIG_SPOT = (122, 552)
STONE = (106, 556)


def batch_of(t):
    if t < STAGE0 or t >= S4:
        return None
    return max(b for b in range(NB) if BT[b] <= t)


PATH = [(200, 404), (236, 336), (270, 284), (276, 262), (276, 230)]


def along(q):
    q = W.clamp(q)
    seg = [math.dist(PATH[k], PATH[k + 1]) for k in range(len(PATH) - 1)]
    L = sum(seg) * q
    for k, s in enumerate(seg):
        if L <= s or k == len(seg) - 1:
            u = min(1, L / s)
            return PATH[k][0] + (PATH[k + 1][0] - PATH[k][0]) * u, PATH[k][1] + (PATH[k + 1][1] - PATH[k][1]) * u
        L -= s


def exped_pos(n, t):
    k = EXPED.index(n)
    q = (t - S4) / (S6 - S4 - 0.15) - 0.07 * k
    if q < 0:
        x0, y0 = CROWD[IDX[n]]
        u = W.ease(W.clamp((t - S4) / 0.35 + 1 - k * 0.25))
        x1, y1 = along(0)
        return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    return along(q)


def walk_to(i, spot, t0, dur=0.45, t=0):
    x0, y0 = CROWD[i]
    q = W.clamp((t - t0) / dur)
    return x0 + (spot[0] - x0) * W.ease(q), y0 + (spot[1] - y0) * W.ease(q), (1 + int(t / 0.1) % 2) if 0 < q < 1 else 0


def people_now(t):
    res = []
    b = batch_of(t)
    stage = {}
    if b is not None:
        for j, (n, r) in enumerate(GROUPS[b]):
            stage[n] = j
    for i, (n, r) in enumerate(PEOPLE):
        if n in EXPED and t >= S4:
            x, y = exped_pos(n, t)
            if y > 236:
                res.append((i, x, y, 1 + int(t / 0.12) % 2))
            continue
        if n == 'Julielen' and S2B <= t < S5:
            if t < S3:
                res.append((i,) + walk_to(i, JUL_SPOT, S2B + 0.1, t=t))
            else:
                q = W.clamp((t - S3) / 0.35)
                x = JUL_SPOT[0] + (DIG_SPOT[0] - JUL_SPOT[0]) * q
                y = JUL_SPOT[1] + (DIG_SPOT[1] - JUL_SPOT[1]) * q
                fr = (1 + int(t / 0.09) % 2) if (q >= 1 and t < S3B) else 0
                res.append((i, x, y, fr))
            continue
        if n == 'Robson' and S2B <= t < S5:
            res.append((i,) + walk_to(i, ROB_SPOT, S2B + 0.2, t=t))
            continue
        if n in stage:
            j = stage[n]
            q = W.clamp((t - BT[b]) / 0.25)
            x0, y0 = CROWD[i]
            sx = SLOTS[len(GROUPS[b])][j]
            res.append((i, x0 + (sx - x0) * W.ease(q), y0 + (STAGE_Y - y0) * W.ease(q), (1 + int(t / 0.1) % 2) if q < 1 else 0))
            continue
        x, y = CROWD[i]
        res.append((i, x, y, 0))
    return res


# ---------------------------------------------------------------- estátua, pano, pedra
def _stone_of(spr):
    a = spr.copy()
    m = a[..., 3] > 0
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
    base = np.array((176, 170, 160), np.float32)
    col = base[None, None, :] * (0.45 + 0.75 * lum[..., None])
    outline = (a[..., 0] == F.OUT[0]) & (a[..., 1] == F.OUT[1]) & (a[..., 2] == F.OUT[2])
    col[outline] = (70, 66, 64)
    a[..., :3] = np.where(m[..., None], col, 0)
    return a


def _statue():
    Wd, Hd = 66, 62
    a = np.zeros((Hd, Wd, 4), np.float32)
    figs = [('Gabriel', 'ferreiro', 15, 0), ('Raviela', 'cavaleira', 33, -4), ('Lívia', 'construtora de casas', 51, 0)]
    top = Hd - 13
    for nm, rl, cx, dy in figs:
        s = _stone_of(F.make_folk(nm, rl, 0))
        rows = np.nonzero(s[..., 3].any(axis=1))[0]
        h, w = s.shape[:2]
        y0 = top + dy - rows.max()
        x0 = cx - w // 2
        ys, xs = np.nonzero(s[..., 3] > 0)
        Y, X = ys + y0, xs + x0
        ok = (Y >= 0) & (Y < Hd) & (X >= 0) & (X < Wd)
        a[Y[ok], X[ok]] = s[ys[ok], xs[ok]]
    for y in range(top + 1, Hd):           # pedestal
        for x in range(2, Wd - 2):
            if y == top + 1 and x in (2, Wd - 3):
                continue
            c = (150, 144, 136) if y < top + 3 else (128, 122, 116)
            if (x + (y // 3) * 4) % 12 == 0 or y in (top + 3, top + 8):
                c = (104, 98, 94)
            if x >= Wd - 6:
                c = W.shade(c, 0.82)
            a[y, x, :3] = c; a[y, x, 3] = 1
    for x in range(1, Wd - 1):              # contorno do pedestal
        a[Hd - 1, x, :3] = (60, 56, 54); a[Hd - 1, x, 3] = 1
    for y in range(top + 4, top + 11):      # placa
        for x in range(Wd // 2 - 13, Wd // 2 + 13):
            a[y, x, :3] = (74, 70, 72); a[y, x, 3] = 1
    for y in (top + 6, top + 8):
        for x in range(Wd // 2 - 10, Wd // 2 + 10, 2):
            a[y, x, :3] = (190, 184, 176)
    return a


STATUE = _statue()
PLAQUE = [(STX - 11 + k, STY - 13 + 9) for k in range(0, 22, 2)]   # linha extra que brilha (nomes novos)


def _cloth():
    w, h = 70, 56
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(4, h - 1), (8, 22), (20, 6), (35, 1), (50, 6), (62, 22), (66, h - 1)], fill=(178, 46, 42, 255), outline=(60, 18, 20, 255))
    for x in (18, 30, 42, 54):
        d.line((x, 12, x - 3, h - 2), fill=(140, 30, 30, 255))
    d.line((22, 8, 34, 3), fill=(220, 90, 80, 255))
    cx, cy = 35, 28                                       # chama dourada
    d.polygon([(cx, cy - 9), (cx + 5, cy), (cx + 3, cy + 6), (cx - 3, cy + 6), (cx - 5, cy)], fill=(255, 196, 60, 255))
    d.polygon([(cx, cy - 3), (cx + 2, cy + 2), (cx, cy + 5), (cx - 2, cy + 2)], fill=(255, 240, 160, 255))
    return im


CLOTH = _cloth()


def draw_rgba(img, im, cx, cy):
    a = np.asarray(im, np.float32)
    h, w = a.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    ys, xs = np.nonzero(a[..., 3] > 128)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < W.H) & (X >= 0) & (X < W.W)
    img[Y[ok], X[ok]] = a[ys[ok], xs[ok], :3]


def blit_arr(img, a, x0, y0):
    ys, xs = np.nonzero(a[..., 3] > 0)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < W.H) & (X >= 0) & (X < W.W)
    img[Y[ok], X[ok]] = a[ys[ok], xs[ok], :3]


def draw_statue(img, t):
    h, w = STATUE.shape[:2]
    blit_arr(img, STATUE, STX - w // 2, STY - h)
    if t < CLOTH1:
        q = W.clamp((t - CLOTH0) / (CLOTH1 - CLOTH0))
        if q <= 0:
            wob = math.sin(t * 9) * 0.6
            draw_rgba(img, CLOTH, STX + wob, STY - h + 22)
        else:
            e = q * q
            sc = 1 - 0.55 * e
            im = CLOTH.resize((max(2, int(70 * sc)), max(2, int(56 * sc))), Image.NEAREST).rotate(-40 * e, Image.NEAREST, expand=True)
            draw_rgba(img, im, STX + 70 * e, STY - h + 22 - 120 * e)


def stone_y(t):
    if t < S3B - 0.25:
        return None
    q = W.clamp((t - (S3B - 0.25)) / 0.45)
    return STONE[1] - 26 * W.ease(q) + (math.sin(t * 3.2) * 1.2 if q >= 1 else 0)


_STONE_ROWS = ["...ooooo...",
               "..oSSSSSo..",
               ".oSSRSSsSo.",
               "oSSRRRSSssO",
               "oSRSRSRSssO",
               "oSSRRRSSssO",
               ".oSSRSSssO.",
               "..oSssssO..",
               "...ooOOO..."]


def draw_stone(out, x, y, t, glow=1.0, sc=1):
    k = 0.6 + 0.4 * math.sin(t * 6)
    x0, y0 = int(x) - 5 * sc, int(y) - 4 * sc
    R = 9 * sc
    yy_, xx_ = np.mgrid[-R:R + 1, -R:R + 1]                    # halo
    d = np.sqrt(xx_ ** 2 + (yy_ * 1.1) ** 2)
    a = np.clip(1 - d / (R + 0.5), 0, 1) ** 1.5 * 0.55 * glow * (0.7 + 0.3 * k)
    Y, X = yy_ + int(y), xx_ + int(x)
    ok = (Y >= 0) & (Y < W.H) & (X >= 0) & (X < W.W)
    out[Y[ok], X[ok]] = out[Y[ok], X[ok]] * (1 - a[ok][:, None]) + np.array((120, 255, 225)) * a[ok][:, None]
    cols = {'o': (40, 44, 58), 'O': (28, 30, 40), 'S': (92, 104, 122), 's': (66, 76, 94)}
    for r, row in enumerate(_STONE_ROWS):
        for c, ch in enumerate(row):
            if ch == '.':
                continue
            col = (np.array((90, 120, 120)) * (1 - k * glow) + np.array((170, 255, 236)) * k * glow) if ch == 'R' else cols[ch]
            for u in range(sc):
                for v in range(sc):
                    X, Y = x0 + c * sc + u, y0 + r * sc + v
                    if 0 <= X < W.W and 0 <= Y < W.H:
                        out[Y, X] = col


# ---------------------------------------------------------------- castelo-fantasma (meta)
def _castle():
    im = Image.new('L', (W.W, W.H), 0)
    d = ImageDraw.Draw(im)
    cx, base = 180, 236
    d.rectangle((cx - 40, base - 46, cx + 40, base), outline=255)
    for x in range(cx - 40, cx + 40, 10):
        d.rectangle((x, base - 52, x + 5, base - 46), outline=255)
    for tx in (cx - 54, cx + 40):
        d.rectangle((tx, base - 70, tx + 14, base), outline=255)
        d.polygon([(tx - 2, base - 70), (tx + 7, base - 86), (tx + 16, base - 70)], outline=255)
    d.rectangle((cx - 12, base - 92, cx + 12, base - 46), outline=255)
    d.polygon([(cx - 15, base - 92), (cx, base - 112), (cx + 15, base - 92)], outline=255)
    d.line((cx, base - 112, cx, base - 124), fill=255)
    d.polygon([(cx, base - 124), (cx + 9, base - 121), (cx, base - 118)], outline=255)
    d.rectangle((cx - 8, base - 20, cx + 8, base), outline=255)
    for wx in (cx - 30, cx + 22, cx - 4):
        d.rectangle((wx, base - 36, wx + 6, base - 28), outline=255)
    a = np.argwhere(np.array(im) > 0)
    return a[np.lexsort((a[:, 1], -a[:, 0]))]


CASTLE = _castle()


def castle(out, t):
    p = W.clamp((t - S6 - 0.2) / 0.9)
    n = int(len(CASTLE) * p)
    pulse = 0.75 + 0.25 * math.sin(t * 4)
    pts = CASTLE[:n]
    col = np.array((255, 214, 90), float)
    out[pts[:, 0], pts[:, 1]] = out[pts[:, 0], pts[:, 1]] * (1 - pulse) + col * pulse


SPARK = [(random.Random(9).uniform(-30, 30), random.Random(19 + k).uniform(-58, -4), k * 0.05) for k in range(14)]


def sparkles(out, cx, cy, t0, t, dur=0.9, col=(255, 240, 170)):
    r = random.Random(int(t0 * 100))
    for k in range(14):
        dx, dy, dl = r.uniform(-32, 32), r.uniform(-60, -4), r.uniform(0, 0.4)
        a = t - t0 - dl
        if 0 <= a < dur:
            s = 1 if a < dur * 0.6 else 0
            X, Y = int(cx + dx), int(cy + dy - a * 8)
            for ddx, ddy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))[: 5 if s else 1]:
                if 0 <= X + ddx < W.W and 0 <= Y + ddy < W.H:
                    out[Y + ddy, X + ddx] = col


# ---------------------------------------------------------------- cena
def scene(t):
    td = tod(t)
    img = W.LAND.copy()
    for x0, y, sp, ln in P.SHIM:
        x = int(x0 + t * sp) % W.W
        for k in range(ln):
            xk = (x + k) % W.W
            if not (260 <= xk <= 290 or 196 <= xk <= 215):
                img[y, xk] = (170, 214, 246) if k else (210, 236, 252)
    for c_ in range(20):
        dy = int(round(math.sin(t * 7 - c_ * 0.45) * 1.4 * min(1, c_ / 6)))
        for r_ in range(12):
            col = P.FLAGC.get((c_, r_), (178, 46, 42))
            wv = math.sin(t * 7 - c_ * 0.45 + 1.2)
            col = W.shade(col, 1.12) if wv > 0.55 else (W.shade(col, 0.82) if wv < -0.55 else col)
            if r_ in (0, 11):
                col = W.shade(col, 0.78)
            img[318 + r_ + dy, 154 + c_] = col
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.blit(img, spr, *B.POS[name])
    B.draw_pier(img); B.draw_horta(img)
    B.smoke_at(img, t, 97, 300, seed=1); B.smoke_at(img, t, 285, 300, seed=2)
    fire_on = t >= S5
    if fire_on:
        W.smoke(img, t)
    W.ground_shadow(img, STX - 12, STY); W.ground_shadow(img, STX + 12, STY)
    ppl = people_now(t)
    items = [(STY - 0.5, 'statue', None)] + [(p[2], 'p', p) for p in ppl]
    dog_i = IDX['Ana Sofia']
    for _, kind, p in sorted(items, key=lambda z: z[0]):
        if kind == 'statue':
            draw_statue(img, t)
            continue
        i, x, y, fr = p
        n, r = PEOPLE[i]
        W.ground_shadow(img, x, y)
        W.blit(img, F.folk(n, r if r else ('moradora' if n == 'Lila' else 'morador'), fr), x, y)
        if i == dog_i:
            W.ground_shadow(img, x + 14, y)
            W.blit(img, F.make_dog(int(t * 3) % 2), x + 14, y)
    if S3 <= t < S3B + 0.2:                       # terra voando enquanto ela cava
        r = random.Random(int(t * 30))
        for k in range(5):
            a = (t * 30 + k * 7) % 10 / 10
            X = int(DIG_SPOT[0] - 10 + r.uniform(-4, 4) - a * 6)
            Y = int(DIG_SPOT[1] - a * 10 + a * a * 12)
            if 0 <= X < W.W and 0 <= Y < W.H:
                img[Y, X] = (120, 84, 50)
        for dx in range(-3, 4):
            img[STONE[1] + 1, STONE[0] + dx] = (96, 66, 40)
    s = W.sky(td, t)
    tint = W.keyinterp(W.TINT, td)
    tm = np.broadcast_to(tint, (W.H, W.W, 3)).copy()
    nf = W.clamp((td - 0.6) / 0.9)
    if fire_on:
        lv = (W.light_level(t) * nf)[..., None]
        tm = tm * (1 - lv) + np.array((1.06, 0.84, 0.66)) * lv
    if nf > 0:
        lv = (P.light_at(*P.LANT_C, 30, t) * nf * 0.9)[..., None]
        tm = tm * (1 - lv) + np.array((1.04, 0.86, 0.66)) * lv
        lv = (P.light_at(276, 254, 20, t) * 0.75 * nf)[..., None]
        tm = tm * (1 - lv) + np.array((0.55, 1.0, 0.9)) * lv
    sy = stone_y(t)
    if sy is not None and t < S4:                 # luz da pedra
        lv = (P.light_at(STONE[0], sy + 8, 34, t) * 0.9)[..., None]
        tm = tm * (1 - lv) + np.array((0.62, 1.1, 1.0)) * lv
    if t >= S4:                                   # a pedra vai com a Rafaela
        rx, ry = exped_pos('Rafaela', t)
        if ry > 236:
            lv = (P.light_at(rx + 5, ry - 18, 30, t) * 0.85)[..., None]
            tm = tm * (1 - lv) + np.array((0.62, 1.1, 1.0)) * lv
    if STAGE0 - 0.1 <= t < S4:
        lv = (P.light_at(STAGE_CX, STAGE_Y - 4, 104, t) * 0.85)[..., None]
        tm = tm * (1 - lv) + np.array((1.0, 0.92, 0.8)) * lv
    out = np.where(W.LMASK[..., None], img * tm, s)
    if fire_on:
        W.fire(out, t, scale=W.ease((t - S5) / 0.3))
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.emissive(out, spr, *B.POS[name], strength=max(nf, 0.35 if name == 'forja' else 0) * 0.95, t=t)
    if td > 1.5:
        k = W.clamp((td - 1.5) / 0.4)
        for fx, fy, ph, f in P.FLIES:
            if math.sin(t * f + ph) > 0.2:
                x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
                out[y, x] = out[y, x] * (1 - k) + np.array((226, 255, 140)) * k
    if nf > 0.2:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            out[254 + dy, 276 + dx] = (200, 255, 230)
    if CLOTH0 <= t < CLOTH0 + 1.5:
        sparkles(out, STX, STY, CLOTH0, t, dur=1.0)
    if S2B + 0.3 <= t < S3:                       # nomes novos brilhando na placa
        k = 0.6 + 0.4 * math.sin(t * 8)
        for X, Y in PLAQUE:
            out[Y, X] = out[Y, X] * (1 - k) + np.array((255, 214, 90)) * k
        sparkles(out, (JUL_SPOT[0] + ROB_SPOT[0]) / 2, JUL_SPOT[1], S2B + 0.5, t, dur=0.9)
    if sy is not None and t < S4:
        draw_stone(out, STONE[0], sy, t, sc=2)
        if t < S3B + 0.8:
            sparkles(out, STONE[0], STONE[1] + 20, S3B - 0.2, t, dur=0.8, col=(170, 255, 236))
    if t >= S4:
        rx, ry = exped_pos('Rafaela', t)
        if ry > 236:
            draw_stone(out, rx + 7, ry - 24, t)
    if S3B <= t < S5:
        for (x, y) in [DIG_SPOT, ROB_SPOT] + [CROWD[IDX[n]] for n in ('Ana Sofia', 'Gabriel', 'Raviela')]:
            W.qmark(out, int(x) - 3, int(y) - 40, bang=True)
    if t >= S6:
        castle(out, t)
    return out, td


def shot(t):
    if t < S5:
        return (6, 256, 5)                                # estátua
    if t < STAGE0:
        return (44, 80, 4)
    if t < S4:
        return (STAGE_CX - 108, STAGE_Y - 250, 5)
    if t < S6:
        x, y = exped_pos('Rafaela', t)
        x, y = (x, y) if y > 236 else along(1)
        return int(min(max(x - 108, 0), W.W - 216)), int(min(max(y - 250, 0), W.H - 384)), 5
    return (44, 80, 4)


# ---------------------------------------------------------------- textos
def short_role(r):
    r = r.split('(')[0].split('/')[0].strip()
    r = r.split(' e ')[0] if len(r) > 14 else r
    return r if len(r) <= 14 else r.split()[0]


CAPS = [
    (S2, S2B, 280, [(S2, [('O ALERRANDRO', WHITE)], 150), (S2, [('ESCULPIU', WHITE)], 150),
                    (S2 + D2, [('OS FUNDADORES.', GOLD)], 150)]),
    (S2B, S3, 270, [(S2B, [('E GRAVOU 2 NOMES', WHITE)], 140), (S2B, [('QUE FALTAVAM:', WHITE)], 140),
                    (S2B + D2B, [('JULIELEN E ROBSON.', GOLD)], 130)]),
    (S3, S3B, 280, [(S3, [('A JULIELEN CAVOU', WHITE)], 140), (S3, [('A BASE DA ESTÁTUA…', WHITE)], 120)]),
    (S3B, S5, 300, [(S3B, [('…E ACHOU', WHITE)], 160), (S3B + 0.25, [('ISSO.', TEAL)], 200)]),
    (S5, S4, 270, [(S5, [(f'CHEGARAM {len(NEW)} MORADORES', WHITE)], 130), (S5 + 0.3, [('NOVOS:', GOLD)], 170)]),
    (S4, S4B, 270, [(S4, [('A RAFAELA, A ANDRÉA', WHITE)], 130), (S4, [('E A ALEXANDRA', WHITE)], 130),
                    (S4 + D4, [('LEVARAM A PEDRA…', GOLD)], 130)]),
    (S4B, S6, 290, [(S4B, [('…PRA PROCURAR', WHITE)], 150), (S4B + 0.3, [('OUTRAS VILAS.', TEAL)], 170)]),
    (S6, TEND + 1, 270, [(S6, [('SEGUE E COMENTA', WHITE)], 150), (S6, [('SEU NOME E SUA FUNÇÃO', GOLD)], 130),
                         (S6 + D6, [('PRA VIRAR MORADOR.', WHITE)], 110)]),
]


def overlay_state(t):
    st = []
    if t < S2:
        st.append(('count', NP))
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    if S2B + 0.55 <= t < S3:
        st.append(('fund',))
    b = batch_of(t)
    if b is not None and t >= BT[b] + 0.2:
        st.append(('stage', b))
    if t >= S6 + 0.6:
        st.append(('bar',))
    return tuple(st)


def tag(d, cx, top, nm, rl, f1=58, f2=38, h=110, extra=None):
    while E.font(f1).getlength(nm) > 190 and f1 > 34:
        f1 -= 4
    while E.font(f2).getlength(rl) > 190 and f2 > 24:
        f2 -= 2
    w = max(E.font(f1).getlength(nm), E.font(f2).getlength(rl)) + 30
    d.polygon([(cx - 12, top + 2), (cx + 12, top + 2), (cx, top - 16)], fill=(250, 236, 200, 255))
    E.panel(d, (cx - w / 2, top, cx + w / 2, top + h), b=5)
    d.text((cx, top + 36), nm, font=E.font(f1), fill=GOLD + (255,), anchor='mm')
    d.text((cx, top + 80), rl, font=E.font(f2), fill=(240, 236, 250, 255), anchor='mm')


def flame_px(d, cx, cy, s=6):
    pts = [(0, -3), (-1, -2), (0, -2), (1, -2), (-2, -1), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0),
           (-1, 1), (0, 1), (1, 1)]
    for x, y in pts:
        c = (255, 236, 150) if (x, y) in ((0, 0), (0, -1), (0, 1)) else (255, 150, 50)
        d.rectangle((cx + x * s, cy + y * s, cx + x * s + s - 1, cy + y * s + s - 1), fill=c + (255,))


_ov = {}


def overlay(state):
    if state in _ov:
        return _ov[state]
    im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for item in state:
        k = item[0]
        if k == 'count':
            E.draw_line(d, FW / 2, 300, [('ESTE REINO TEM', WHITE)], 150)
            E.draw_line(d, FW / 2, 300 + 0.78 * 150 + 10, [(f'{item[1]} MORADORES.', GOLD)], 200)
        elif k == 'cap':
            _, ci, nvis = item
            a, b, y, lines = CAPS[ci]
            for j, (ta, segs, size) in enumerate(lines):
                sz = E.fit(segs, size)
                if j > 0 and any(ch in 'ÁÉÍÓÚÂÊÔÃÕ' for s_, _ in segs for ch in s_):
                    y += 0.17 * sz
                if j < nvis:
                    E.draw_line(d, FW / 2, y, segs, size)
                y += 0.54 * sz + 0.24 * sz + 10
        elif k == 'fund':
            x0, y0, s = shot(S2B + 1)
            cx = min(((JUL_SPOT[0] + ROB_SPOT[0]) / 2 - x0) * s, 690)
            top = (JUL_SPOT[1] - 44 - y0) * s - 150
            w = 500
            E.panel(d, (cx - w / 2, top, cx + w / 2, top + 140), b=6)
            d.text((cx, top + 46), 'JULIELEN  ·  ROBSON', font=E.font(64), fill=GOLD + (255,), anchor='mm')
            d.text((cx + 22, top + 102), 'FUNDADORES', font=E.font(44), fill=(240, 236, 250, 255), anchor='mm')
            flame_px(d, cx - E.font(44).getlength('FUNDADORES') / 2 - 6, top + 102, 5)
            d.polygon([(cx - 14, top + 140), (cx + 14, top + 140), (cx, top + 158)], fill=(250, 236, 200, 255))
        elif k == 'stage':
            b = item[1]
            x0, y0, s = shot(BT[b] + 0.3)
            for j, (n, r) in enumerate(GROUPS[b]):
                cx = (SLOTS[len(GROUPS[b])][j] - x0) * s
                top = (STAGE_Y - y0) * s + 40
                tag(d, cx, top, F.shown(n).upper(), TAGROLE.get(n, short_role(r)).upper())
        elif k == 'bar':
            x0, y0, x1, y1 = 170, 720, 910, 830
            E.panel(d, (x0, y0, x1, y1))
            d.text((x0 + 36, y0 + 30), 'MORADORES', font=E.font(54), fill=WHITE + (255,), anchor='lm')
            d.text((x1 - 36, y0 + 30), f'{N_FOLLOW} / {GOAL}', font=E.font(54), fill=GOLD + (255,), anchor='rm')
            bx0, by0, bx1, by1 = x0 + 36, y0 + 62, x1 - 36, y0 + 92
            d.rectangle((bx0, by0, bx1, by1), fill=(60, 50, 80, 255))
            fill = bx0 + (bx1 - bx0) * min(1, N_FOLLOW / GOAL)
            d.rectangle((bx0, by0, fill, by1), fill=(255, 190, 60, 255))
            for xx_ in range(int(bx0), int(fill), 18):
                d.rectangle((xx_, by0, xx_ + 8, by0 + 8), fill=(255, 230, 140, 255))
    arr = np.array(im)
    a = arr[..., 3]
    ys, xs = np.nonzero(a)
    res = None
    if len(ys):
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        res = ((y0, y1, x0, x1), arr[y0:y1, x0:x1, :3].astype(np.float32), (arr[y0:y1, x0:x1, 3:4] / 255.0).astype(np.float32))
    _ov[state] = res
    return res


def frame(t):
    c, td = scene(t)
    f = P.camera(c, shot(t))
    ov = overlay(overlay_state(t))
    if ov:
        (y0, y1, x0, x1), rgb, a = ov
        reg = f[y0:y1, x0:x1].astype(np.float32)
        f[y0:y1, x0:x1] = (reg * (1 - a) + rgb * a).astype(np.uint8)
    return f


# ---------------------------------------------------------------- áudio
SR = E.SR


def sfx(total):
    n = int(total * SR)
    s = np.zeros(n)

    def blip(t, f, d=0.035, g=0.08, duty=0.5):
        nn = int(d * SR)
        E.add(s, t, E.sq(f, nn, duty) * E.adsr(nn, a=0.002, dec=0.02, sus=0.3, r=0.01), g)

    def chime(t0, notes, g=0.08, step=0.06, dur=0.12):
        for j, m in enumerate(notes):
            nn = int(dur * SR)
            E.add(s, t0 + j * step, E.sq(E.midi(m), nn, 0.25) * E.adsr(nn, dec=0.05, sus=0.2), g)

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            blip(ta, 988, g=0.05)
    nn = int(0.55 * SR)                                   # whoosh do pano
    tt = np.arange(nn) / SR
    wh = E.noise(nn, 3) * np.sin(math.pi * tt / 0.55) ** 2
    E.add(s, CLOTH0 - 0.05, E.lp(wh, 0.18), 0.5)
    chime(CLOTH0 + 0.25, [72, 76, 79, 84, 88], g=0.09, step=0.07, dur=0.16)
    for k in range(4):                                    # cinzel
        nn = int(0.03 * SR)
        E.add(s, S2 + 0.2 + k * 0.32, E.sq(2400, nn, 0.5) * np.exp(-np.arange(nn) / SR * 120), 0.06)
    chime(S2B + D2B, [79, 83, 86, 91], g=0.09)
    for k in range(int((S3B - S3 - 0.4) / 0.18)):         # cavando
        nn = int(0.06 * SR)
        E.add(s, S3 + 0.4 + k * 0.18, E.lp(E.noise(nn, 40 + k), 0.2) * np.exp(-np.arange(nn) / SR * 40), 0.3)
    nn = int(1.4 * SR)                                    # zumbido da pedra
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 98 * tt) + 0.6 * np.sin(2 * math.pi * 147 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 3 * tt))
    E.add(s, S3B - 0.2, hum * np.sin(math.pi * tt / 1.4), 0.15)
    chime(S3B, [88, 84, 91], g=0.06, step=0.1, dur=0.2)
    for b in range(NB):
        chime(BT[b] + 0.2, [79, 83, 86, 91], g=0.08)
    for k in range(int((S6 - S4) / 0.24)):                # passos
        nn = int(0.04 * SR)
        E.add(s, S4 + 0.1 + k * 0.24, E.lp(E.noise(nn, 70 + k), 0.12) * np.exp(-np.arange(nn) / SR * 70), 0.3)
    for k, m in enumerate([62, 66, 69, 74, 78, 81]):      # fanfarra do castelo
        nn = int(0.12 * SR)
        E.add(s, S6 + 0.25 + k * 0.09, E.sq(E.midi(m + 12), nn, 0.25) * E.adsr(nn), 0.08)
    r = random.Random(4)
    t = S5 + 0.1
    while t < TEND:
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.05 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
    t = S4
    while t < TEND:
        for k in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.02)
        t += r.uniform(0.55, 0.95)
    return s


def audio(path):
    total = TEND
    E.T4, E.T6, E.T7 = S2B, S3, S5
    mus = E.music(total + 0.5)[:int(total * SR)]
    voice = os.environ.get('VOICE')
    if voice:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', voice, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                             capture_output=True).stdout
        v = np.frombuffer(raw, '<i2').astype(np.float64) / 32768
        v = v / (np.abs(v).max() + 1e-9)
        vt = np.zeros(len(mus))
        E.add(vt, float(os.environ.get('VOICE_OFF', '0.15')), v, 1.0)
        env = np.convolve(np.abs(vt), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode='same')
        talk = np.convolve((env > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
        duck = 0.09 * (1 - talk) + 0.035 * talk
        mix = mus * duck + sfx(total) * 0.3 + vt * 0.95
    else:
        mix = mus * 0.9 + sfx(total)
    fo = int(0.3 * SR)
    mix[-fo:] *= np.linspace(1, 0.35, fo)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


def main():
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep4_{float(v):05.2f}.png'))
        return
    wav = os.path.join(OUTDIR, 'ep4.wav')
    audio(wav)
    out = os.path.join(OUTDIR, os.environ.get('NAMEOUT', 'brasa-ep4.mp4'))
    nfr = int(round(TEND * FPS))
    f0 = frame(0.0).astype(np.float32)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
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
