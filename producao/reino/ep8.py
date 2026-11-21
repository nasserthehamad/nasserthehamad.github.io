#!/usr/bin/env python3
"""Brasa — Ep. 8 "A Margem" (~27 s, sem voz).
0. (1º quadro) A flecha de fogo do Cauã já está no ar; ela acende uma fogueira na outra margem e revela uma multidão
   de encapuzados com tochas. "NESTE REINO, CADA SEGUIDOR VIRA MORADOR."
1. A câmera passa pela vila inteira na beira do rio: os ferreiros (Gabriel e João) afiam as espadas e as bruxas e os
   magos (Oliveti, Cathe e Pepze) acendem luzes sobre a água. "ESTE REINO TEM N MORADORES."
2. Estreia da Gabi, vigia, na torre da ponte: "UM DELES ESTÁ ATRAVESSANDO SOZINHO."
3. A Raviela e a Alexandra vão até ele no meio da ponte: "NÃO VIEMOS ATACAR." / "VIEMOS FUGIDOS."
4. O céu atrás das montanhas fica vermelho: "ELE ESTÁ VINDO ATRÁS DE NÓS." (sem monstro na tela)
5. "CADA SEGUIDOR NOVO DEIXA UM DELES ATRAVESSAR A PONTE." (+1 atravessando) e o final de sempre.
Uso: N=<seguidores> PREV8=<seguidores no ep. 7> python3 ep8.py   (STILLS=1,5,... · CAPA=1)"""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '86')
os.environ.setdefault('PREV7', '80')
import ep7 as X

W, F, B, E, P, Q, H, G, HS = X.W, X.F, X.B, X.E, X.P, X.Q, X.H, X.G, X.HS
FW, FH, FPS = 1080, 1920, 30
OUTDIR = G.OUTDIR
WHITE, GOLD, TEAL, RED = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 96, 86)
N_FOLLOW = int(os.environ['N'])
PREV8 = int(os.environ.get('PREV8', '83'))
GOAL = 100
PEOPLE, IDX, ROLE, NP = X.PEOPLE, X.IDX, X.ROLE, X.NP
NEW8 = [i for i in range(NP) if PEOPLE[i][0].startswith('anon') and int(PEOPLE[i][0][4:]) >= PREV8 - len(G.NAMED)]
NAMED8 = [('Gabi', 'vigia')]
for _k, (_n, _r) in enumerate(NAMED8[:len(NEW8)]):
    PEOPLE[NEW8[_k]] = (_n, _r)
    IDX[_n] = NEW8[_k]; ROLE[_n] = _r
GABI = IDX.get('Gabi')

# ---------------------------------------------------------------- tempo
S1, S2, S3, S4, S5 = 3.8, 9.0, 12.6, 17.4, 20.4
EN = 22.4
TEND = EN + 4.4
XF = 0.4
T_SHOT, FLIGHT = -0.25, 1.0                      # a flecha já está no ar no 1º quadro
T_IGN = T_SHOT + FLIGHT                          # acerta a outra margem
C3, C4 = S1 + 1.6, S1 + 3.4                      # ferreiros, magia
T_STR0, T_STR1 = S2 + 1.7, S2 + 3.4              # o estranho atravessa até o meio da ponte
B1, B2 = S3 + 1.8, S3 + 3.3                      # balões de fala
T_CROSS0, T_CROSS1 = S5 + 0.3, S5 + 1.6          # +1 atravessando


def tod(t):
    return 1.82


def ease(q):
    return W.ease(q)


def walk(p0, p1, t0, dur, t):
    q = W.clamp((t - t0) / dur)
    e = q * q * (3 - 2 * q)
    return p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e, (1 + int(t / 0.12) % 2) if 0 < q < 1 else 0


# ---------------------------------------------------------------- lugares
PIER = (206, 294)                               # Cauã na ponta do píer
FIRE_FAR = (236, 268)
HAND = (213, 274)
TOWER_X, TOWER_BASE, TOWER_TOP = 330, 302, 262  # torre da vigia
HORSE = (250, 316)
SPECIAL = {
    'Cauã': PIER,
    'Gabriel': (112, 318), 'João': (158, 316),
    'Oliveti': (192, 330), 'Cathe': (236, 336), 'Pepze': (282, 338),
    'Raviela': (226, 316), 'Alexandra': (306, 334),
    'Edilson': (304, 318),
}
if GABI is not None:
    SPECIAL['Gabi'] = (TOWER_X, TOWER_TOP)
RAV_TO, ALX_TO = (258, 305), (296, 307)
STR_FROM, STR_MID = (276, 265), (276, 286)
STR_END = (268, 309)                            # no fim ele já passou pro lado de cá
CROSS_FROM, CROSS_TO = (278, 265), (286, 306)


def _excluded(x, y):
    if 48 <= x <= 118 and y < 360:               # forja
        return True
    if 186 <= x <= 226 and y < 326:              # Cauã no píer
        return True
    if 306 <= x <= 340 and y < 342:              # árvore + torre
        return True
    if 254 <= x <= 300 and y < 314:              # pé da ponte
        return True
    if 232 <= x <= 270 and 300 <= y < 326:       # cavalo do Valdemir
        return True
    if 296 <= x <= 314 and y < 328:              # Edilson
        return True
    return False


def crowd8():
    r = random.Random(8)
    cand = []
    for row in range(9):
        y = 306 + row * 6.5
        off = 5.5 if row % 2 else 0
        x = 6 + off
        while x < 356:
            px_, py_ = x + r.uniform(-2, 2), y + r.uniform(-1.2, 1.2)
            if not _excluded(px_, py_) and all(math.dist((px_, py_), p) > 9 for p in SPECIAL.values()):
                cand.append((px_, py_))
            x += 11
    cand.sort(key=lambda p: (p[1], p[0]))
    pos = {}
    rest = [i for i in range(NP) if PEOPLE[i][0] not in SPECIAL and i != X.VAL]
    # espalha: pega os lugares da frente pra trás, intercalando a largura toda
    for i, p in zip(rest, cand):
        pos[i] = p
    for n, p in SPECIAL.items():
        if n in IDX:
            pos[IDX[n]] = p
    return pos


POS = crowd8()
BRAZ = [(22, 302), (124, 302), (180, 300), (350, 304)]


# ---------------------------------------------------------------- os encapuzados da outra margem
TINTS = [(1.0, 1.0, 1.0), (0.86, 0.86, 0.96), (0.98, 0.9, 0.8), (0.8, 0.8, 0.82), (1.05, 0.95, 0.9), (0.9, 0.82, 0.78)]
HOODS = []
for _k in range(12):
    _a = F.folk(f'Fugitivo{_k}', 'refugiado', 0).copy()
    _a[..., :3] = np.clip(_a[..., :3] * np.array(TINTS[_k % len(TINTS)]), 0, 255)
    HOODS.append(_a)
_rf = random.Random(31)
FAR = []
for row, (y, step, x0) in enumerate(((270.5, 15.0, 6), (276.0, 15.0, 13))):
    x = x0
    while x < 358:
        xx_ = x + _rf.uniform(-2.5, 2.5)
        if not (252 <= xx_ <= 300 or 312 <= xx_ <= 350):  # entrada da ponte livre e fundo da torre limpo
            FAR.append((xx_, y + _rf.uniform(-0.6, 0.6), _rf.randrange(len(HOODS)), _rf.random() * 6.28))
        x += step
FAR.sort(key=lambda z: z[1])


def far_jit(ph, t):
    return int(round(math.sin(t * 40 + ph) * 0.7)) if S4 <= t < S5 else 0


def far_people(img, t):
    for x, y, v, ph in FAR:
        W.blit(img, HOODS[v], x + far_jit(ph, t), y)


def far_torches(out, t):
    for x, y, v, ph in FAR:
        fx = x + far_jit(ph, t) + 6
        small_flame(out, fx, y - 19, t, ph=ph)
        for dy in range(4, 18, 3):                          # reflexo na água
            Yr = int(y + dy)
            Xr = int(fx + math.sin(t * 3 + dy + ph))
            if 277 <= Yr < 296 and 0 <= Xr < W.W:
                kk = 0.3 + 0.12 * math.sin(t * 9 + ph)
                out[Yr, Xr] = out[Yr, Xr] * (1 - kk) + np.array((255, 160, 70)) * kk


def mountain_torches(out, t):
    pts = []
    for li, u0, ph in X.TORCH:
        u = u0 + 0.38 + 0.05 * t / TEND
        if u <= 1.0:
            p = X.along(X.LINES[li], u)
            pts.append((p[0], p[1], ph))
    pts += X.SCATTER
    for x, y, ph in pts:
        k = 0.75 + 0.25 * math.sin(t * 11 + ph)
        X_, Y_ = int(x + 1.2 * math.sin(t * 0.8 + ph)), int(y)
        for dx, dy, g in ((0, 0, 1.0), (1, 0, 1.0), (0, -1, 0.9), (1, -1, 0.7), (0, -2, 0.5)):
            Xp, Yp = X_ + dx, Y_ + dy
            if 0 <= Xp < W.W and 0 <= Yp < W.H:
                out[Yp, Xp] = out[Yp, Xp] * (1 - k * g) + np.array((255, 170, 70)) * k * g


# ---------------------------------------------------------------- fogo genérico (fogueira da outra margem, braseiros)
def flame(img, cx, base, t, scale=1.0, seed=0):
    if scale <= 0:
        return
    r = random.Random(int(t * 12) + seed * 1000)
    prof = [3, 7, 11, 15, 18, 15, 11, 7, 3]
    for i, dx in enumerate(range(-4, 5)):
        h = int(max(0, (prof[i] + r.randint(-2, 3) + 2.5 * math.sin(t * 9 + i * 1.3 + seed))) * scale)
        for k in range(h):
            y = base - k
            rel = k / max(h, 1)
            if rel < 0.35 and abs(dx) <= 2:
                c = (255, 250, 210)
            elif rel < 0.6 and abs(dx) <= 3:
                c = (255, 216, 92)
            elif rel < 0.86:
                c = (255, 150, 50)
            else:
                c = (228, 74, 40)
            X_ = int(cx + dx * max(0.5, scale))
            if 0 <= y < W.H and 0 <= X_ < W.W:
                img[y, X_] = c
    if scale > 0.5:
        for k in range(6):
            life = 1.2
            ph = (t + k * 0.21 + seed) % life
            sx = int(cx + math.sin(k * 7 + t * 2.5) * 5 * scale)
            sy = int(base - 10 * scale - ph * 40 * scale)
            if ph < life * 0.85 and 0 <= sy < W.H:
                img[sy, sx] = (255, 226, 130) if ph < 0.6 else (255, 150, 70)


def small_flame(out, x, y, t, ph=0.0):
    k = 0.85 + 0.15 * math.sin(t * 13 + ph)
    pts = ((0, 0, (255, 240, 170)), (0, -1, (255, 210, 90)), (1, 0, (255, 170, 60)), (-1, 0, (255, 150, 50)),
           (0, -2, (255, 150, 50)), (0, -3 if math.sin(t * 17 + ph) > 0 else -2, (230, 90, 40)), (1, -1, (255, 150, 50)))
    for dx, dy, c in pts:
        Xp, Yp = int(x + dx), int(y + dy)
        if 0 <= Xp < W.W and 0 <= Yp < W.H:
            out[Yp, Xp] = out[Yp, Xp] * (1 - k) + np.array(c) * k


def brazier(img, x, y):
    for dx in range(-3, 4):
        img[y - 1, x + dx] = (70, 62, 66)
        img[y - 2, x + dx] = (96, 88, 92)
    for yy_ in range(y, y + 4):
        img[yy_, x] = (60, 52, 56)
    img[y + 3, x - 2:x + 3] = (60, 52, 56)


# ---------------------------------------------------------------- torre da vigia
def tower(img):
    wood, dk, lt = np.array((122, 84, 50)), np.array((84, 56, 34)), np.array((156, 112, 70))
    x0, x1 = TOWER_X - 10, TOWER_X + 10
    for x in (x0, x1):
        img[TOWER_TOP:TOWER_BASE, x] = dk
        img[TOWER_TOP:TOWER_BASE, x + 1] = wood
    for k in range(0, TOWER_BASE - TOWER_TOP - 4, 1):     # x de travamento
        y = TOWER_TOP + 4 + k
        if y >= TOWER_BASE:
            break
        u = k / max(1, TOWER_BASE - TOWER_TOP - 5)
        img[y, int(x0 + 1 + u * (x1 - x0 - 1))] = dk
        img[y, int(x1 - u * (x1 - x0 - 1))] = dk
    img[TOWER_TOP - 1:TOWER_TOP + 2, x0 - 3:x1 + 5] = wood
    img[TOWER_TOP - 1, x0 - 3:x1 + 5] = lt
    img[TOWER_TOP + 2, x0 - 3:x1 + 5] = dk
    for x in range(x0 - 3, x1 + 5, 4):                     # parapeito
        img[TOWER_TOP - 8:TOWER_TOP - 1, x] = dk
    img[TOWER_TOP - 8, x0 - 3:x1 + 5] = wood
    for y in range(TOWER_TOP + 3, TOWER_BASE, 3):          # escada
        img[y, x1 + 3:x1 + 7] = lt
    img[TOWER_TOP + 2:TOWER_BASE, x1 + 3] = dk
    img[TOWER_TOP + 2:TOWER_BASE, x1 + 7] = dk


def tower_front(img):
    """parapeito da frente (por cima dos pés da Gabi)."""
    wood, dk = np.array((122, 84, 50)), np.array((84, 56, 34))
    x0, x1 = TOWER_X - 10, TOWER_X + 10
    img[TOWER_TOP - 4:TOWER_TOP - 2, x0 - 3:x1 + 5] = wood
    img[TOWER_TOP - 2, x0 - 3:x1 + 5] = dk


# ---------------------------------------------------------------- quem está onde
def stranger_pos(t):
    if t < T_STR0:
        return None
    if t < S5:
        return walk(STR_FROM, STR_MID, T_STR0, T_STR1 - T_STR0, t)
    return STR_END[0], STR_END[1], 0


def crosser_pos(t):
    if t < T_CROSS0:
        return None
    return walk(CROSS_FROM, CROSS_TO, T_CROSS0, T_CROSS1 - T_CROSS0, t)


def person_pos(i, t):
    n = PEOPLE[i][0]
    x, y = POS[i]
    if n == 'Raviela' and t >= S3:
        if t >= S5:
            return 250, 309, 0
        return walk((x, y), RAV_TO, S3, 0.9, t)
    if n == 'Alexandra' and t >= S3:
        if t >= S5:
            return 300, 312, 0
        return walk((x, y), ALX_TO, S3 + 0.15, 0.9, t)
    return x, y, 0


def alarm_t(i):
    x, y = POS.get(i, (180, 320))
    return S4 + 0.3 + abs(x - 180) / 260


# ---------------------------------------------------------------- luzes
def orbs(t):
    """luzes mágicas: nascem nos bruxos (C4) e ficam boiando em cima do rio."""
    res = []
    if t < C4:
        return res
    src = [SPECIAL['Oliveti'], SPECIAL['Cathe'], SPECIAL['Pepze']]
    r = random.Random(77)
    for k in range(15):
        sx, sy = src[k % 3]
        tx, ty = 16 + k * 23 + r.uniform(-6, 6), 283 + r.uniform(-3, 5)
        t0 = C4 + 0.1 * k
        q = W.clamp((t - t0) / 0.9)
        if q <= 0:
            continue
        e = 1 - (1 - q) ** 2
        x = sx + (tx - sx) * e
        y = (sy - 24) + (ty - (sy - 24)) * e - 18 * math.sin(math.pi * q)
        y += 1.5 * math.sin(t * 2.2 + k)
        col = [(140, 255, 230), (200, 150, 255), (255, 230, 140)][k % 3]
        res.append((x, y, col, q))
    return res


def light_sum(t, srcs):
    """luz de várias fontes de uma vez (mesmo desenho do P.light_at, em degraus)."""
    if not srcs:
        return None
    L = np.zeros((W.H, W.W), np.float32)
    for cx, cy, R, g in srcs:
        x0, x1 = int(max(0, cx - R - 2)), int(min(W.W, cx + R + 3))
        y0, y1 = int(max(0, cy - R / 1.9 - 2)), int(min(W.H, cy + R / 1.9 + 3))
        if x0 >= x1 or y0 >= y1:
            continue
        d = np.sqrt((W.xx[y0:y1, x0:x1] - cx) ** 2 + ((W.yy[y0:y1, x0:x1] - cy) * 1.9) ** 2)
        l = np.clip(1 - d / R, 0, 1) ** 0.85 * g
        L[y0:y1, x0:x1] = np.maximum(L[y0:y1, x0:x1], l)
    return (np.floor(L * 6 + W.BAY * 0.999) / 6).astype(np.float32)


# céu vermelho
SKY_GLOW = np.clip(1 - np.hypot((W.xx - 180) / 260, (W.yy - 160) / 120), 0, 1).astype(np.float32) ** 1.4
_lm = W.LMASK
RIM = np.zeros_like(_lm)
for _d in range(1, 5):
    RIM[_d:] |= _lm[_d:] & ~_lm[:-_d]


def red_level(t):
    if t < S4 or t >= S5 + 0.3:
        return 0.0
    a = t - S4
    base = W.clamp(a / 0.5) * (1 - W.clamp((t - S5) / 0.3))
    return base * (0.75 + 0.25 * math.sin(a * 5.5))


# ---------------------------------------------------------------- cena
def village(t):
    td = tod(t)
    img = W.LAND.copy()
    for x0, y, sp, ln in P.SHIM:
        x = int(x0 + t * sp) % W.W
        for k in range(ln):
            xk = (x + k) % W.W
            if not (260 <= xk <= 290 or 196 <= xk <= 215):
                img[y, xk] = (170, 214, 246) if k else (210, 236, 252)
    for c_ in range(20):                          # bandeira
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
    B.smoke_at(img, t, 97, 300, seed=1); B.smoke_at(img, t, 285, 300, seed=2); B.smoke_at(img, t, H.TX + 13, H.TY, seed=3)
    W.smoke(img, t)
    far_people(img, t)
    tower(img)
    for bx, by in BRAZ:
        brazier(img, bx, by)
    items = [(H.STY - 0.5, 'statue', None), (H.TB - 0.5, 'tavern', None), (HORSE[1], 'horse', None),
             (TOWER_TOP + 0.5, 'tfront', None)]
    for i in range(NP):
        if i == X.VAL:
            continue
        x, y, fr = person_pos(i, t)
        items.append((y, 'p', (i, x, y, fr)))
    sp = stranger_pos(t)
    if sp:
        items.append((sp[1], 'str', sp))
    cp = crosser_pos(t)
    if cp:
        items.append((cp[1], 'cross', cp))
    dog_i = IDX['Ana Sofia']
    for _, kind, p in sorted(items, key=lambda z: z[0]):
        if kind == 'statue':
            h, w = Q.STATUE.shape[:2]
            Q.blit_arr(img, Q.STATUE, H.STX - w // 2, H.STY - h)
        elif kind == 'tavern':
            B.blit(img, H.TAVERN, H.TX, H.TY, p=1.0, t=t)
        elif kind == 'tfront':
            tower_front(img)
        elif kind == 'horse':
            spr = HS.rider_on_horse(F.folk('Valdemir', ROLE['Valdemir'], 0), 1)
            for dx in (-6, 0, 6):
                W.ground_shadow(img, HORSE[0] + dx, HORSE[1])
            jump = 2 if 0 <= t - alarm_t(X.VAL) < 0.3 else 0
            W.blit(img, spr, HORSE[0], HORSE[1] - jump)
        elif kind in ('str', 'cross'):
            x, y, fr = p
            W.ground_shadow(img, x, y)
            W.blit(img, F.folk('Estranho' if kind == 'str' else 'Fugitivo', 'refugiado', fr), x, y)
        else:
            i, x, y, fr = p
            n, r = PEOPLE[i]
            rr = r if r else ('moradora' if n == 'Lila' else 'morador')
            jump = 0
            if S4 <= t < S5:
                a = t - alarm_t(i)
                if 0 <= a < 0.3:
                    jump = 2
            if n != 'Gabi':
                W.ground_shadow(img, x, y)
            W.blit(img, F.folk(n, rr, fr), x, y - jump)
            if i == dog_i:
                W.ground_shadow(img, x + 14, y)
                W.blit(img, F.make_dog(int(t * 3) % 2), x + 14, y)
    # ---- luz
    s = W.sky(td, t)
    tm = np.broadcast_to(W.keyinterp(W.TINT, td), (W.H, W.W, 3)).copy()
    tm = tm * 1.12
    nf = 1.0
    lv = (W.light_level(t) * nf)[..., None]
    tm = tm * (1 - lv) + np.array((1.06, 0.84, 0.66)) * lv
    warm = [(P.LANT_C[0], P.LANT_C[1], 32, 0.9), (HORSE[0], HORSE[1] - 14, 26, 0.8),
            (SPECIAL['Edilson'][0], SPECIAL['Edilson'][1] - 14, 22, 0.75)]
    warm += [(bx, by - 4, 44, 0.85) for bx, by in BRAZ]
    if t >= T_IGN:
        g = W.clamp((t - T_IGN) / 0.35)
        warm.append((FIRE_FAR[0], FIRE_FAR[1] - 4, 96 * g, 0.95))
    sp = stranger_pos(t)
    if sp:
        warm.append((sp[0] + 6, sp[1] - 18, 26, 0.9))
    cp = crosser_pos(t)
    if cp:
        warm.append((cp[0] + 6, cp[1] - 18, 22, 0.85))
    if GABI is not None:
        warm.append((TOWER_X, TOWER_TOP - 16, 28, 0.95))
    lv = light_sum(t, warm)
    if lv is not None:
        tm = tm * (1 - lv[..., None]) + np.array((1.1, 0.9, 0.7)) * lv[..., None]
    ob = orbs(t)
    if ob:
        lv = light_sum(t, [(x, y, 30 * q, 0.8) for x, y, c, q in ob])
        tm = tm * (1 - lv[..., None]) + np.array((0.8, 1.05, 1.1)) * lv[..., None]
    rl = red_level(t)
    if rl > 0:
        s = s + (np.array((210, 40, 30)) - s) * (SKY_GLOW[..., None] * rl * 0.95)
        tm = tm * (1 - 0.25 * rl) + np.array((0.5, 0.1, 0.1)) * 0.25 * rl
    out = np.where(W.LMASK[..., None], img * tm, s)
    if rl > 0:
        out[RIM] = out[RIM] * (1 - 0.6 * rl) + np.array((255, 70, 40)) * 0.6 * rl
    W.fire(out, t)
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.emissive(out, spr, *B.POS[name], strength=0.95, t=t)
    B.emissive(out, H.TAVERN, H.TX, H.TY, strength=0.95, t=t)
    for fx, fy, ph, f in P.FLIES:
        if math.sin(t * f + ph) > 0.2:
            x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
            out[y, x] = out[y, x] * 0.0 + np.array((226, 255, 140))
    G.castle5(out, 100 + t)
    mountain_torches(out, t)
    far_torches(out, t)
    for k, (bx, by) in enumerate(BRAZ):
        flame(out, bx, by - 3, t, 0.42, seed=k + 1)
    if t >= T_IGN:                                 # fogueira da outra margem
        g = W.clamp((t - T_IGN) / 0.35)
        flame(out, FIRE_FAR[0], FIRE_FAR[1], t, 0.5 + 0.9 * g, seed=9)
        if t - T_IGN < 0.5:                        # estouro
            r = random.Random(5)
            a = t - T_IGN
            for _ in range(40):
                ang, sp_ = r.uniform(math.pi, 2 * math.pi), r.uniform(40, 120)
                X_, Y_ = FIRE_FAR[0] + math.cos(ang) * sp_ * a, FIRE_FAR[1] - 6 + math.sin(ang) * sp_ * a + 60 * a * a
                if 0 <= X_ < W.W and 0 <= Y_ < W.H:
                    out[int(Y_), int(X_)] = (255, 210, 110)
    arrow(out, t)
    for sp_ in (stranger_pos(t), crosser_pos(t)):     # tochas na mão
        if sp_:
            small_flame(out, sp_[0] + 6, sp_[1] - 19, t, ph=sp_[0])
    for x, y, c, q in ob:                          # luzes mágicas
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            Xp, Yp = int(x + dx), int(y + dy)
            if 0 <= Xp < W.W and 0 <= Yp < W.H:
                out[Yp, Xp] = (255, 255, 255) if (dx, dy) == (0, 0) else c
        for dy in range(6, 13, 3):                 # reflexo
            Yr = int(y + dy)
            if 277 <= Yr < 296 and q >= 1:
                out[Yr, int(x)] = out[Yr, int(x)] * 0.6 + np.array(c) * 0.4
    if C3 <= t < S2 + 0.5:                         # faíscas dos ferreiros
        for n in ('Gabriel', 'João'):
            if n in IDX:
                hx, hy = SPECIAL[n][0] + 6, SPECIAL[n][1] - 24
                r = random.Random(int(t * 8) + len(n))
                ph = (t * 8) % 1
                for k in range(10):
                    ang = r.uniform(-2.6, -0.5)
                    sp_ = r.uniform(20, 46)
                    X_, Y_ = hx + math.cos(ang) * sp_ * ph * 0.5, hy + math.sin(ang) * sp_ * ph * 0.5 + 30 * ph * ph * 0.25
                    if 0 <= X_ < W.W and 0 <= Y_ < W.H:
                        out[int(Y_), int(X_)] = (255, 236, 150) if k % 2 else (255, 170, 60)
    if GABI is not None and S2 + 0.3 <= t < S2 + 1.6:
        Q.sparkles(out, TOWER_X, TOWER_TOP - 20, S2 + 0.3, t, dur=1.2)
    if GABI is not None and S2 + 1.6 <= t < S3:
        W.qmark(out, TOWER_X - 3, TOWER_TOP - 50, bang=True)
    if T_STR0 + 0.6 <= t < S3:                     # o Valdemir e o Edilson reagem
        W.qmark(out, HORSE[0] + 2, HORSE[1] - 56, bang=True)
        W.qmark(out, SPECIAL['Edilson'][0] - 3, SPECIAL['Edilson'][1] - 46, bang=True)
    if S4 <= t < S5:                               # "!" em todo mundo
        for i in range(NP):
            a = t - alarm_t(i)
            if 0 <= a < 1.8 and i != X.VAL:
                x, y, _ = person_pos(i, t)
                if (i * 7) % 3 == 0:
                    W.qmark(out, int(x) - 3, int(y) - 46, bang=True)
    return out


def arrow(out, t):
    q = (t - T_SHOT) / FLIGHT
    if not (0 <= q < 1):
        return
    (x0, y0), (x1, y1) = HAND, (FIRE_FAR[0], FIRE_FAR[1] - 3)
    hgt = 40

    def at(q_):
        return x0 + (x1 - x0) * q_, y0 + (y1 - y0) * q_ - 4 * hgt * q_ * (1 - q_)
    x, y = at(q)
    xb, yb = at(max(0, q - 0.03))
    dx, dy = x - xb, y - yb
    L = math.hypot(dx, dy) + 1e-6
    ux, uy = dx / L, dy / L
    for k in range(1, 40):                          # rastro de fogo
        qq = q - k * 0.006
        if qq < 0:
            break
        X_, Y_ = at(qq)
        a = max(0.0, 1 - k / 40)
        col = np.array((255, 220, 120)) if k < 8 else np.array((255, 130, 50))
        for dx, dy in ((0, 0), (0, 1)) if k < 20 else ((0, 0),):
            Xp, Yp = int(X_ + dx), int(Y_ + dy)
            if 0 <= Xp < W.W and 0 <= Yp < W.H:
                out[Yp, Xp] = out[Yp, Xp] * (1 - a) + col * a
    for k in range(8):                              # haste
        X_, Y_ = int(round(x - ux * k)), int(round(y - uy * k))
        if 0 <= X_ < W.W and 0 <= Y_ < W.H:
            out[Y_, X_] = (170, 120, 70) if k < 6 else (240, 240, 240)
    for dx in range(-2, 3):                         # bola de fogo na ponta
        for dy in range(-2, 3):
            d2 = dx * dx + dy * dy
            if d2 <= 5:
                Xp, Yp = int(x + dx), int(y + dy)
                if 0 <= Xp < W.W and 0 <= Yp < W.H:
                    c = (255, 250, 210) if d2 <= 1 else ((255, 200, 90) if d2 <= 2 else (255, 120, 40))
                    out[Yp, Xp] = c


# ---------------------------------------------------------------- câmera
def clamp_shot(x0, y0, s):
    return (int(min(max(0, x0), W.W - FW // s)), int(min(max(0, y0), W.H - FH // s)), s)


def pan_x(t):
    q = W.clamp((t - S1) / (S2 - S1))
    e = q * q * (3 - 2 * q)
    return 180 * e


def shot(t):
    if t < S1:
        return clamp_shot(122, 136, 6)
    if t < S2:
        return clamp_shot(pan_x(t), 140, 6)
    if t < S4:
        return clamp_shot(180, 130, 6)
    if t < S5:
        return (44, 40, 4)
    return clamp_shot(90, 80, 4)


# ---------------------------------------------------------------- textos
FALTAM = max(0, GOAL - N_FOLLOW)
CAPS = [
    (0.0, 1.9, 270, [(0.0, [('NESTE REINO, CADA', WHITE)], 128), (0.0, [('SEGUIDOR VIRA ', WHITE), ('MORADOR.', GOLD)], 128)]),
    (1.9, S1, 270, [(1.9, [('O CAUÃ ATIROU FOGO', WHITE)], 128), (1.9, [('NA OUTRA MARGEM…', GOLD)], 128),
                    (2.7, [('…E ELES ESTAVAM LÁ.', RED)], 120)]),
    (S1, C3, 270, [(S1, [('A VILA INTEIRA FOI', WHITE)], 130), (S1 + 0.3, [('PRA BEIRA DO RIO.', GOLD)], 130)]),
    (S1 + 0.5, S2, 1520, [(S1 + 0.5, [('ESTE REINO TEM ', WHITE), (f'{N_FOLLOW}', GOLD), (' MORADORES.', WHITE)], 96)]),
    (C3, C4, 270, [(C3, [('OS FERREIROS', WHITE)], 140), (C3 + 0.3, [('AFIARAM AS ESPADAS.', GOLD)], 124)]),
    (C4, S2, 270, [(C4, [('AS BRUXAS E OS MAGOS', WHITE)], 124), (C4 + 0.3, [('ACENDERAM O RIO.', GOLD)], 130)]),
    (S2, T_STR0, 270, [(S2, [('ESTREIA HOJE:', WHITE)], 140), (S2 + 0.3, [('GABI', GOLD), (', VIGIA.', WHITE)], 140)]),
    (T_STR0, S3, 270, [(T_STR0, [('UM DELES ESTÁ', WHITE)], 140), (T_STR0 + 0.3, [('ATRAVESSANDO SOZINHO.', RED)], 124)]),
    (S3, B1, 270, [(S3, [('A RAVIELA E A', WHITE)], 136), (S3 + 0.3, [('ALEXANDRA', GOLD), (' FORAM', WHITE)], 136),
                   (S3 + 0.3, [('ATÉ ELE.', WHITE)], 136)]),
    (S4 + 0.5, S5, 270, [(S4 + 0.5, [('"ELE ESTÁ VINDO', RED)], 140), (S4 + 0.8, [('ATRÁS DE NÓS."', RED)], 140)]),
    (S5, EN, 270, [(S5, [('CADA SEGUIDOR NOVO', WHITE)], 126), (S5 + 0.3, [('DEIXA UM DELES', GOLD)], 132),
                   (S5 + 0.3, [('ATRAVESSAR A PONTE.', GOLD)], 124)]),
    (EN, TEND + 1, 270, [(EN, [('QUEM NÃO SEGUE', WHITE)], 150), (EN + 0.3, [('NÃO MORA NA VILA.', GOLD)], 136)]),
    (EN + 0.9, TEND + 1, 880, [(EN + 0.9, [('COMENTA TEU NOME', WHITE)], 110), (EN + 0.9, [('E TUA FUNÇÃO', GOLD)], 110)]),
]
BUBBLES = [(B1, B2, 'NÃO VIEMOS ATACAR.'), (B2, S4, 'VIEMOS FUGIDOS.')]
CHAR_T = 0.045


def bubble_text(t):
    for a, b, txt in BUBBLES:
        if a <= t < b:
            return txt[:min(len(txt), int((t - a) / CHAR_T) + 1)], txt
    return None


def overlay_state(t):
    st = []
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    bt = bubble_text(t)
    if bt:
        st.append(('bubble', bt[0], bt[1]))
    if t >= EN + 0.5:
        st.append(('bar',))
    return tuple(st)


_ov = {}


def overlay(state):
    if state in _ov:
        return _ov[state]
    im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for item in state:
        k = item[0]
        if k == 'cap':
            _, ci, nvis = item
            a, b, y, lines = CAPS[ci]
            for j, (ta, segs, size) in enumerate(lines):
                sz = E.fit(segs, size)
                if j > 0 and any(ch in 'ÁÉÍÓÚÂÊÔÃÕÀ' for s_, _ in segs for ch in s_):
                    y += 0.17 * sz
                if j < nvis:
                    E.draw_line(d, FW / 2, y, segs, size)
                y += 0.54 * sz + 0.24 * sz + 10
        elif k == 'bubble':
            _, shown_, full = item
            x0, y0, s = shot(S3 + 1.0)
            hx, hy = (STR_MID[0] - x0) * s, (STR_MID[1] - 44 - y0) * s
            fnt = E.font(82)
            w = fnt.getlength(full) + 70
            bx0, bx1 = max(30, hx - w / 2), min(FW - 30, hx + w / 2)
            by1 = hy - 40
            by0 = by1 - 130
            d.rounded_rectangle((bx0 - 6, by0 - 6, bx1 + 6, by1 + 6), 24, fill=(30, 22, 40, 255))
            d.rounded_rectangle((bx0, by0, bx1, by1), 20, fill=(252, 248, 236, 255))
            d.polygon([(hx - 26, by1 - 2), (hx + 26, by1 - 2), (hx, hy - 4)], fill=(30, 22, 40, 255))
            d.polygon([(hx - 18, by1 - 4), (hx + 18, by1 - 4), (hx, hy - 14)], fill=(252, 248, 236, 255))
            d.text((bx0 + 35, (by0 + by1) / 2), shown_, font=fnt, fill=(40, 28, 50, 255), anchor='lm')
        elif k == 'bar':
            x0, y0, x1, y1 = 170, 650, 910, 760
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
    ys, xs = np.nonzero(arr[..., 3])
    res = None
    if len(ys):
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        res = ((y0, y1, x0, x1), arr[y0:y1, x0:x1, :3].astype(np.float32), (arr[y0:y1, x0:x1, 3:4] / 255.0).astype(np.float32))
    _ov[state] = res
    return res


def tags_now(t):
    """crachás (seguem a câmera)."""
    res = []
    if 0.4 <= t < S1:
        res.append(('Cauã', 'CAUÃ', 'ARQUEIRO', PIER))
    if C3 + 0.3 <= t < C4:
        res += [('Gabriel', 'GABRIEL', 'FERREIRO', SPECIAL['Gabriel']), ('João', 'JOÃO', 'FERREIRO', SPECIAL['João'])]
    if C4 + 0.3 <= t < S2:
        res += [('Oliveti', 'OLIVETI', 'BRUXA', SPECIAL['Oliveti']), ('Cathe', 'CATHE', 'MAGO', SPECIAL['Cathe']),
                ('Pepze', 'PEPZE', 'BRUXO', SPECIAL['Pepze'])]
    if GABI is not None and S2 + 0.3 <= t < S3:
        res.append(('Gabi', 'GABI', 'VIGIA', (TOWER_X, TOWER_TOP + 2)))
    if S3 + 0.9 <= t < S4:
        res += [('Raviela', 'RAVIELA', 'CAVALEIRA', RAV_TO), ('Alexandra', 'ALEXANDRA', 'DIPLOMATA', ALX_TO)]
    return res


def frame(t):
    sh = shot(t)
    c = village(t)
    f = P.camera(c, sh)
    if S4 <= t < S4 + 0.6:                          # tremor
        amp = (1 - (t - S4) / 0.6) * 14
        f = np.roll(f, (int(math.sin(t * 90) * amp), int(math.cos(t * 77) * amp)), (0, 1))
    tg = tags_now(t)
    pl = None
    if S5 <= t < EN + 0.6 and t >= T_CROSS1:
        pl = t - T_CROSS1
    if tg or pl is not None:
        im = Image.fromarray(f)
        d = ImageDraw.Draw(im)
        x0, y0, s = sh
        for _, nm, rl, (wx, wy) in tg:
            Q.tag(d, (wx - x0) * s, (wy - y0) * s + 26, nm, rl)
        if pl is not None and pl < 0.9:
            q = min(1.0, pl / 0.2)
            yy_ = (CROSS_TO[1] - 46 - y0) * s - 30 * pl
            E.draw_line(d, (CROSS_TO[0] - x0) * s, yy_, [('+1 MORADOR', GOLD)], int(70 + 20 * q), stroke=8)
        f = np.asarray(im).copy()
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
    r = random.Random(8)

    def blip(t, f, d=0.035, g=0.05, duty=0.5):
        nn = int(d * SR)
        E.add(s, t, E.sq(f, nn, duty) * E.adsr(nn, a=0.002, dec=0.02, sus=0.3, r=0.01), g)

    def chime(t0, notes, g=0.08, step=0.06, dur=0.12):
        for j, m in enumerate(notes):
            nn = int(dur * SR)
            E.add(s, t0 + j * step, E.sq(E.midi(m), nn, 0.25) * E.adsr(nn, dec=0.05, sus=0.2), g)

    def thump(t0, g=0.5, f0=110, dec=18, ln=0.25):
        nn = int(ln * SR)
        tt = np.arange(nn) / SR
        f = f0 * np.exp(-tt * dec) + 38
        E.add(s, t0, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 12), g)

    def noise_burst(t0, ln, g, cut=0.2, dec=8.0, seed=0):
        nn = int(ln * SR)
        tt = np.arange(nn) / SR
        E.add(s, t0, E.lp(E.noise(nn, seed), cut) * np.exp(-tt * dec), g)

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            blip(max(0, ta), 988)
    # flecha: assobio + chiado de fogo em voo, depois o "vuuush" da fogueira acendendo
    nn = int((T_IGN + 0.02) * SR)
    tt = np.arange(nn) / SR
    E.add(s, 0.0, np.sin(2 * math.pi * np.cumsum(900 - 500 * tt / max(0.1, T_IGN)) / SR) * 0.4 *
          np.minimum(1, (T_IGN - tt) / 0.1), 0.05)
    E.add(s, 0.0, (E.noise(nn, 3) - E.lp(E.noise(nn, 3), 0.3)) * 0.5, 0.06)
    thump(T_IGN, g=0.45, f0=150, dec=25, ln=0.18)
    nn = int(1.2 * SR)
    tt = np.arange(nn) / SR
    E.add(s, T_IGN, E.lp(E.noise(nn, 4), 0.12) * np.minimum(1, tt / 0.08) * np.exp(-tt * 2.2), 0.9)
    # burburinho da vila na beira do rio
    nn = int((S2 - S1) * SR)
    tt = np.arange(nn) / SR
    mur = E.lp(E.noise(nn, 55), 0.06) * (0.5 + 0.5 * np.sin(2 * math.pi * 2.1 * tt) ** 2) * np.sin(math.pi * tt / (S2 - S1))
    E.add(s, S1, mur, 0.45)
    # ferreiros: tim-tim de martelo + raspar da lâmina
    t = C3 + 0.2
    while t < C4:
        nn = int(0.12 * SR)
        tt = np.arange(nn) / SR
        clang = (np.sin(2 * math.pi * 1870 * tt) + 0.6 * np.sin(2 * math.pi * 2930 * tt)) * np.exp(-tt * 30)
        E.add(s, t, clang, 0.06)
        nn = int(0.1 * SR)
        E.add(s, t + 0.12, (E.noise(nn, int(t * 99)) - E.lp(E.noise(nn, int(t * 99)), 0.4)) * np.hanning(nn), 0.05)
        t += 0.26
    # magia: arpejo de sininhos subindo, um por luz
    for k in range(15):
        nn = int(0.4 * SR)
        tt = np.arange(nn) / SR
        m = [76, 79, 83, 88, 91][k % 5] + (12 if k >= 10 else 0)
        E.add(s, C4 + 0.1 * k, np.sin(2 * math.pi * E.midi(m) * tt) * np.exp(-tt * 6), 0.035)
    # Gabi estreia
    chime(S2 + 0.3, [84, 88, 91, 96], g=0.06, step=0.07, dur=0.16)
    # alerta + passos na madeira (o estranho atravessando)
    blip(T_STR0 + 0.6, 1320, d=0.07, g=0.07); blip(T_STR0 + 0.7, 1760, d=0.09, g=0.07)
    t = T_STR0
    while t < T_STR1:
        thump(t, g=0.22, f0=180, dec=40, ln=0.07)
        t += 0.34
    nn = int((S4 - T_STR0) * SR)
    tt = np.arange(nn) / SR
    drone = (np.sin(2 * math.pi * 55 * tt) + 0.5 * np.sin(2 * math.pi * 58.3 * tt)) * np.sin(math.pi * tt / (S4 - T_STR0)) ** 0.5
    E.add(s, T_STR0, drone, 0.12)
    # Raviela e Alexandra: armadura tilintando
    for k in range(5):
        blip(S3 + 0.1 + k * 0.18, 2400 + 300 * (k % 2), d=0.03, g=0.025, duty=0.25)
    # fala estilo RPG: um blip por letra
    for a, b, txt in BUBBLES:
        for j, ch in enumerate(txt):
            if ch != ' ':
                blip(a + j * CHAR_T, 330 if j % 2 else 294, d=0.03, g=0.06, duty=0.25)
    # "ele": estrondo grave + ronco
    noise_burst(S4, 2.8, 1.5, cut=0.03, dec=1.2, seed=21)
    thump(S4, g=1.0, f0=60, dec=4, ln=1.4)
    nn = int((S5 - S4) * SR)
    tt = np.arange(nn) / SR
    rum = (np.sin(2 * math.pi * 41 * tt) + 0.6 * np.sin(2 * math.pi * 43.5 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.9 * tt))
    E.add(s, S4, rum * np.minimum(1, (S5 - S4 - tt) / 0.5), 0.3)
    for k in range(4):
        thump(S4 + 0.9 + k * 0.62, g=0.55, f0=70, dec=9)
    # +1 atravessando
    t = T_CROSS0
    while t < T_CROSS1:
        thump(t, g=0.18, f0=190, dec=40, ln=0.07)
        t += 0.32
    chime(T_CROSS1, [79, 83, 86, 91], g=0.07, step=0.06)
    for k_, m in enumerate([62, 66, 69, 74, 78, 81]):
        nn = int(0.12 * SR)
        E.add(s, EN + 0.25 + k_ * 0.09, E.sq(E.midi(m + 12), nn, 0.25) * E.adsr(nn), 0.08)
    t = 0.0
    while t < total:                              # fogo crepitando e grilos
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.05 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.14)
    t = 0.0
    while t < total:
        for k_ in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k_ * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.02)
        t += r.uniform(0.55, 0.95)
    return s


def audio(path):
    total = TEND
    E.T4, E.T6, E.T7 = S1, S2, S2
    mus = E.music(total + 0.5)[:int(total * SR)]
    g = np.ones(len(mus))
    for a_, b_, lvl in ((T_STR0, S4, 0.3), (S4, S5, 0.0)):
        a, b = int(a_ * SR), int(b_ * SR)
        ramp = int(0.3 * SR)
        g[a:b] = lvl
        g[a:a + ramp] = np.linspace(g[a - 1] if a > 0 else 1, lvl, ramp)
        g[b - ramp:b] = np.linspace(lvl, 1 if b_ == S5 else lvl, ramp)
    mix = mus * g * 0.85 + sfx(total)
    fo = int(0.3 * SR)
    mix[-fo:] *= np.linspace(1, 0.35, fo)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


# ---------------------------------------------------------------- capa
def capa():
    t = T_STR1 + 0.3
    f = P.camera(village(t), shot(t))
    im = Image.fromarray(f).convert('RGBA')
    d = ImageDraw.Draw(im)
    title = 'EPISÓDIO 8 · A MARGEM'
    tw = E.font(78).getlength(title)
    E.panel(d, (540 - tw / 2 - 36, 250, 540 + tw / 2 + 36, 372), b=6)
    E.draw_line(d, 540, 278, [(title, WHITE)], 78)
    E.draw_line(d, 540, 450, [('BRASA', GOLD)], 280, stroke=14)
    E.draw_line(d, 540, 700, [('UM DELES ', WHITE), ('ATRAVESSOU', RED)], 104)
    out = os.path.join(OUTDIR, 'capa-brasa-ep8.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


def main():
    if os.environ.get('CAPA'):
        capa(); return
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep8_{float(v):05.2f}.png'))
        print('ok', 'novos:', [PEOPLE[i][0] for i in NEW8], 'Gabi' in IDX)
        return
    wav = os.path.join(OUTDIR, 'ep8.wav')
    audio(wav)
    out = os.path.join(OUTDIR, 'brasa-ep8.mp4')
    f0 = frame(0.0).astype(np.float32)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(round(TEND * FPS))):
        t = i / FPS
        f = frame(t)
        if t > TEND - XF:
            k = (t - (TEND - XF)) / XF
            f = (f.astype(np.float32) * (1 - k) + f0 * k).astype(np.uint8)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    print(out)


if __name__ == '__main__':
    main()
