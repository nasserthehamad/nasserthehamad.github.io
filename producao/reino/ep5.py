#!/usr/bin/env python3
"""Brasa — Ep. 5 "A Taverna" (~27 s, sem voz).
1. O castelo-fantasma se desenha até N% (meta 100) com "ESTE REINO TEM N MORADORES" e "FALTAM X PRO CASTELO".
2. Floresta: a expedição (Rafaela, Andréa, Alexandra) chega a ruínas de outra vila; a laje tem o mesmo símbolo da pedra.
3. Palco: cubo, Delox, Vitória, Meize e Miyuki chegam; a Luiza vira santa e o bruxo "???" ganha nome (Pepze).
4. A Miyuki abre a taverna e no primeiro dia já tem briga (nuvem de poeira, canecas voando).
5. A poeira baixa: pegadas brilhando, iguais às do Ep. 3, entram na taverna.
6. Final: castelo + barra N/100 + "QUEM NÃO SEGUE NÃO MORA NA VILA" + "COMENTA TEU NOME E TUA FUNÇÃO"."""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
import world2 as W
import folk as F
import build as B
import ep1hd as E
import ep2 as P
import ep4 as Q

FW, FH, FPS = 1080, 1920, 30
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
WHITE, GOLD, TEAL = (255, 255, 255), (255, 208, 72), (96, 226, 214)
N_FOLLOW = int(os.environ.get('N', '73'))
GOAL = 100


def _apply_ep5(lst):
    res = []
    for n, r in lst:
        ch = F.EP5_CHANGES.get(n)
        if isinstance(ch, tuple):
            n, r = ch
        elif ch:
            r = ch
        res.append((n, r))
    return res


OLD = list(F.FOUNDERS) + list(F.MISSED_FOUNDERS)
NEW = list(F.NEW_EP5)
NAMED = _apply_ep5(OLD + list(F.NEW_EP2) + list(F.NEW_EP4)) + NEW
ANON = max(0, N_FOLLOW - len(NAMED))
PEOPLE = NAMED + [(f'anon{k}', '') for k in range(ANON)]
NP = len(PEOPLE)
IDX = {n: i for i, (n, _) in enumerate(PEOPLE)}
ROLE = dict(PEOPLE)
EXPED = ['Rafaela', 'Andréa', 'Alexandra']

# ---------------------------------------------------------------- tempo
R0, PA, TV = 2.6, 7.8, 13.8          # ruínas, palco, taverna
RI = R0 + 3.4                        # a runa da laje acende
STAGE0 = PA + 0.6
BT = [STAGE0, STAGE0 + 1.75, STAGE0 + 3.5]
BR = TV + 1.7                        # começa a briga
DS = BR + 3.0                        # a poeira baixa
EN = DS + 3.7                        # final
TEND = EN + 4.6
XF = 0.4
CAST0, CAST1 = 0.15, 1.3             # castelo se desenhando

GROUPS = [[('cubo', ROLE['cubo']), ('Delox', ROLE['Delox']), ('Vitória', ROLE['Vitória'])],
          [('Meize', ROLE['Meize']), ('Miyuki', ROLE['Miyuki'])],
          [('Luiza', ROLE['Luiza']), ('Pepze', ROLE['Pepze'])]]
NB = len(GROUPS)
TAGROLE = {'cubo': 'GUARDA', 'Delox': 'CURANDEIRO', 'Vitória': 'BANQUEIRA', 'Meize': 'ARTISTA',
           'Miyuki': 'TAVERNEIRA', 'Luiza': 'AGORA É SANTA', 'Pepze': 'ERA O ???'}
STAGE_Y = 486
SLOTS = {3: [151, 193, 235], 2: [172, 214]}
STAGE_CX = 193
STX, STY = Q.STX, Q.STY

# taverna
TX, TB = 212, 532                    # canto esquerdo, base
DOOR = (244, 532)
MIY = (220, 540)
GUARD = (292, 546)
LIE = [(204, 556), (222, 569), (240, 582)]
TSHOT = (154, 320, 6)


def tod(t):
    if t < PA:
        return 0.15
    if t < TV:
        return 0.9 + 0.5 * (t - PA) / (TV - PA)
    if t < EN:
        return 1.85
    return min(2.0, 1.85 + 0.15 * (t - EN) / 0.6)


# ---------------------------------------------------------------- multidão
CROWD = Q.crowd_positions(NP)
for _n, _p in (('Alerrandro', (40, 548)), ('Miyuki', (232, 462)), ('cubo', (250, 452))):
    _i = IDX[_n]
    _j = min(range(NP), key=lambda j: (CROWD[j][0] - _p[0]) ** 2 + (CROWD[j][1] - _p[1]) ** 2)
    CROWD[_i], CROWD[_j] = CROWD[_j], CROWD[_i]
CROWD[IDX['Alerrandro']] = (40, 548)
_anons = [IDX[f'anon{k}'] for k in range(ANON)]
FIGHTERS = sorted(_anons, key=lambda i: (CROWD[i][0] - 244) ** 2 + (CROWD[i][1] - 470) ** 2)[:3]
WATCH = sorted([i for i in range(NP) if PEOPLE[i][0] not in EXPED and i not in FIGHTERS
                and PEOPLE[i][0] not in ('Miyuki', 'cubo')],
               key=lambda i: (CROWD[i][0] - 244) ** 2 + (CROWD[i][1] - 470) ** 2)[:4]


def batch_of(t):
    if t < STAGE0 or t >= TV:
        return None
    return max(b for b in range(NB) if BT[b] <= t)


def walk(p0, p1, t0, dur, t):
    q = W.clamp((t - t0) / dur)
    e = W.ease(q)
    return p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e, (1 + int(t / 0.1) % 2) if 0 < q < 1 else 0


def people_now(t):
    res = []
    b = batch_of(t)
    stage = {n: j for j, (n, r) in enumerate(GROUPS[b])} if b is not None else {}
    for i, (n, r) in enumerate(PEOPLE):
        if n in EXPED:
            continue
        if t >= TV:
            if n == 'Miyuki':
                res.append((i,) + walk(CROWD[i], MIY, TV + 0.1, 0.6, t))
                continue
            if i in FIGHTERS:
                k = FIGHTERS.index(i)
                if t < DS:
                    t0 = TV + 0.95 + 0.22 * k
                    if t >= t0 + 0.55:
                        continue                          # entrou na taverna
                    res.append((i,) + walk(CROWD[i], (DOOR[0] + (k - 1) * 3, DOOR[1] + 1), t0, 0.55, t))
                else:
                    res.append((i, LIE[k][0], LIE[k][1], 'lie'))
                continue
            if n == 'cubo' and t >= DS - 0.55:
                res.append((i,) + walk(CROWD[i], GUARD, DS - 0.55, 0.6, t))
                continue
        if n in stage:
            j = stage[n]
            q = W.clamp((t - BT[b]) / 0.25)
            x0, y0 = CROWD[i]
            sx = SLOTS[len(GROUPS[b])][j]
            res.append((i, x0 + (sx - x0) * W.ease(q), y0 + (STAGE_Y - y0) * W.ease(q),
                        (1 + int(t / 0.1) % 2) if q < 1 else 0))
            continue
        x, y = CROWD[i]
        res.append((i, x, y, 0))
    return res


# ---------------------------------------------------------------- taverna
FONT3 = {'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'A': ['.#.', '#.#', '###', '#.#', '#.#'],
         'V': ['#.#', '#.#', '#.#', '#.#', '.#.'], 'E': ['###', '#..', '##.', '#..', '###'],
         'R': ['##.', '#.#', '##.', '#.#', '#.#'], 'N': ['#.#', '###', '###', '###', '#.#']}


def taverna():
    s = B.Spr(72, 62)
    wood, beam = (156, 102, 60), (86, 54, 32)
    for y in range(26, 62):
        for x in range(4, 60):
            c = wood if (y // 3) % 2 == 0 else B.shade(wood, 0.92)
            if y % 3 == 2:
                c = B.shade(wood, 0.76)
            if x >= 54:
                c = B.shade(c, 0.84)
            s.px(x, y, c)
    B.stones(s, 4, 55, 59, 61, (146, 140, 132), 9)
    for x in (4, 5, 58, 59):
        for y in range(26, 56):
            s.px(x, y, beam if x in (4, 59) else B.shade(beam, 1.2))
    for y in (26, 27):
        for x in range(4, 60):
            s.px(x, y, beam)
    B.roof(s, 0, 63, 4, 27, (70, 130, 96), (52, 102, 76))
    B.stones(s, 10, 0, 16, 15, (132, 122, 118), 4)
    s.rect(9, 0, 17, 1, (80, 72, 70))
    # placa TAVERNA
    s.rect(15, 29, 47, 38, (70, 44, 26))
    s.rect(16, 30, 46, 37, (122, 80, 46))
    for x in (19, 43):
        s.px(x, 28, (60, 56, 60))
    x = 18
    for ch in 'TAVERNA':
        for r_, row in enumerate(FONT3[ch]):
            for c_, v in enumerate(row):
                if v == '#':
                    s.px(x + c_, 31 + r_, (255, 222, 140), emis=True)
        x += 4
    # porta aberta com luz
    s.rect(24, 41, 39, 61, beam)
    s.rect(26, 43, 37, 61, (255, 198, 112))
    for y in range(43, 62):
        for x in range(26, 38):
            s.emis.append((x, y, (255, 198, 112)))
    for y in range(46, 61):                              # vulto de gente lá dentro
        for x in range(29, 34):
            if (x - 31.5) ** 2 / 6 + (y - 50) ** 2 / 9 < 1 or (y >= 52 and 29 <= x <= 33):
                s.px(x, y, (196, 126, 70))
    s.rect(22, 43, 24, 61, B.shade(beam, 1.3)); s.rect(39, 43, 41, 61, B.shade(beam, 1.3))
    # janelas
    for x0 in (8, 46):
        s.rect(x0 - 1, 39, x0 + 9, 50, beam)
        s.rect(x0, 40, x0 + 8, 49, (255, 206, 120))
        for y in range(40, 50):
            for x in range(x0, x0 + 9):
                if x == x0 + 4 or y == 44:
                    s.px(x, y, beam)
                else:
                    s.emis.append((x, y, (255, 206, 120)))
    # lampião ao lado da porta
    s.rect(42, 40, 44, 43, (255, 226, 140)); s.px(43, 39, (60, 50, 50))
    for x, y in ((42, 41), (43, 41), (44, 41), (43, 42)):
        s.emis.append((x, y, (255, 226, 140)))
    # barril e caixote
    for y in range(49, 62):
        for x in range(61, 71):
            if abs(x - 65.5) <= 4.5 - (1 if y in (49, 61) else 0):
                c = (136, 86, 48) if x < 67 else (110, 68, 38)
                if y in (52, 58):
                    c = (80, 80, 90)
                s.px(x, y, c)
    s.rect(60, 55, 61, 61, (150, 110, 66))
    return s.outline()


TAVERN = taverna()
TY = TB - TAVERN.h


def tav_p(t):
    return W.clamp((t - TV) / 0.8) if t >= TV else 0.0


# ---------------------------------------------------------------- castelo até N%
def castle5(out, t):
    pts = Q.CASTLE
    p_goal = min(1.0, N_FOLLOW / GOAL)
    p = p_goal * W.ease(W.clamp((t - CAST0) / (CAST1 - CAST0)))
    n = int(len(pts) * p)
    pulse = 0.75 + 0.25 * math.sin(t * 4)
    rest = pts[n:]
    out[rest[:, 0], rest[:, 1]] = out[rest[:, 0], rest[:, 1]] * 0.82 + np.array((255, 214, 90)) * 0.18
    done = pts[:n]
    out[done[:, 0], done[:, 1]] = out[done[:, 0], done[:, 1]] * (1 - pulse) + np.array((255, 214, 90)) * pulse
    if CAST0 < t < CAST1 + 0.15 and n:
        y, x = pts[min(n, len(pts) - 1)]
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
            if 0 <= y + dy < W.H and 0 <= x + dx < W.W:
                out[y + dy, x + dx] = (255, 250, 210)


# ---------------------------------------------------------------- briga
def _mug():
    rows = ["wwww.", "mmmmh", "mmmm.h", "mmmmh", "mmmm."]
    return rows


def put_px(out, x, y, c):
    x, y = int(x), int(y)
    if 0 <= x < W.W and 0 <= y < W.H:
        out[y, x] = c


def draw_mug(out, x, y):
    for r_, row in enumerate(_mug()):
        for c_, ch in enumerate(row):
            col = {'w': (250, 248, 240), 'm': (170, 110, 60), 'h': (112, 70, 38)}.get(ch)
            if col:
                put_px(out, x + c_, y + r_, col)


def draw_plank(out, x, y, ang):
    for k in range(-4, 5):
        put_px(out, x + k * math.cos(ang), y + k * math.sin(ang), (150, 104, 60))
        put_px(out, x + k * math.cos(ang), y + k * math.sin(ang) + 1, (104, 68, 38))


FLY = [(BR + 0.35, -1, 'mug'), (BR + 1.0, 1, 'plank'), (BR + 1.6, 1, 'mug'), (BR + 2.25, -1, 'plank')]
POWS = [(BR + 0.1, 280, 1130, 'PÁ!', GOLD), (BR + 0.75, 800, 1170, 'POF!', WHITE),
        (BR + 1.45, 300, 1230, 'CRÁS!', GOLD), (BR + 2.15, 790, 1100, 'TUM!', WHITE)]
CLOUD_C = (244, 546)


def brawl(out, t):
    if not (BR <= t < DS + 0.5):
        return
    grow = W.ease(W.clamp((t - BR) / 0.25))
    fade = 1 - W.clamp((t - DS) / 0.5)
    cx, cy = CLOUD_C
    R = 23 * grow
    r = random.Random(int(t * 12))
    blobs = [(cx + r.uniform(-14, 14), cy + r.uniform(-10, 5), R * r.uniform(0.38, 0.6)) for _ in range(10)]
    blobs += [(cx, cy - 3, R * 0.62)]
    x0, x1, y0, y1 = cx - 44, cx + 45, cy - 38, cy + 28
    yy, xx = W.yy[y0:y1, x0:x1], W.xx[y0:y1, x0:x1]
    m = np.zeros(yy.shape, bool)
    shade = np.zeros(yy.shape, np.float32)
    for bx, by, br in blobs:
        mm = (xx - bx) ** 2 + ((yy - by) * 1.25) ** 2 <= br * br
        m |= mm
        shade = np.maximum(shade, np.where(mm, ((xx - bx) + (yy - by)) / max(br, 1), -9))
    if fade < 1:
        m &= W.BAY[y0:y1, x0:x1] < fade
    rim = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    reg = out[y0:y1, x0:x1]
    reg[m] = (214, 200, 176)
    reg[m & (shade > 0.2)] = (178, 162, 138)
    reg[m & (shade < -0.45)] = (236, 226, 206)
    sw = m & (np.abs(np.sin((xx - cx) * 0.45 + (yy - cy) * 0.3 + t * 9)) < 0.18) & ~rim   # redemoinhos
    reg[sw] = (150, 134, 112)
    reg[rim] = (60, 48, 50)
    if fade < 0.5:
        return
    for k in range(6):                                   # poeira solta
        a = r.uniform(0, 2 * math.pi)
        d_ = R * r.uniform(1.0, 1.35)
        px_, py_ = cx + math.cos(a) * d_, cy - 3 + math.sin(a) * d_ * 0.8
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            put_px(out, px_ + dx, py_ + dy, (214, 208, 198))
    for k in range(5):                                   # braços e pernas saindo da nuvem
        a = r.uniform(0, 2 * math.pi)
        ex, ey = cx + math.cos(a) * R * 1.05, cy - 2 + math.sin(a) * R * 0.8
        skin = W.SKINS[r.randrange(len(W.SKINS))]
        if k < 3:
            for u in range(5):
                put_px(out, ex + math.cos(a) * u, ey + math.sin(a) * u, skin)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                put_px(out, ex + math.cos(a) * 5 + dx, ey + math.sin(a) * 5 + dy, skin)
        else:
            for u in range(4):
                put_px(out, ex + math.cos(a) * u, ey + math.sin(a) * u, (62, 62, 96))
                put_px(out, ex + math.cos(a) * u + 1, ey + math.sin(a) * u, (62, 62, 96))
            for dx in range(3):
                put_px(out, ex + math.cos(a) * 4 + dx, ey + math.sin(a) * 4, (70, 48, 36))
    for k in range(4):                                   # estrelinhas
        a = t * 5 + k * math.pi / 2
        sx, sy = cx + math.cos(a) * (R + 4), cy - 10 + math.sin(a) * (R * 0.5 + 2)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            put_px(out, sx + dx, sy + dy, (255, 230, 90))
    for t0, side, kind in FLY:                           # coisas voando
        u = (t - t0) / 0.75
        if 0 <= u < 1:
            x = cx + side * (12 + 70 * u)
            y = cy - 8 - 46 * math.sin(math.pi * u * 0.9) + 30 * u * u
            if kind == 'mug':
                draw_mug(out, x, y)
            else:
                draw_plank(out, x, y, t * 14 * side)


# ---------------------------------------------------------------- pegadas
STEPS5 = []
_a, _b = (332, 648), (246, 538)
_L = math.dist(_a, _b)
_ux, _uy = (_b[0] - _a[0]) / _L, (_b[1] - _a[1]) / _L
for k in range(17):
    q = k / 16
    side = 1 if k % 2 else -1
    STEPS5.append((_a[0] + (_b[0] - _a[0]) * q - _uy * side * 2.2, _a[1] + (_b[1] - _a[1]) * q + _ux * side * 2.2))
STEP_T0, STEP_T1 = DS + 0.35, DS + 1.6


def steps_visible(t):
    if t < STEP_T0:
        return 0
    return int(len(STEPS5) * W.clamp((t - STEP_T0) / (STEP_T1 - STEP_T0)))


def footprints(out, t):
    nst = steps_visible(t)
    for k in range(nst):
        x, y = STEPS5[k]
        glow = 0.65 + 0.35 * math.sin(t * 5 + k)
        for dx, dy in ((-1, -1), (2, -1), (-1, 3), (2, 3), (-2, 1), (3, 1)):
            X, Y = int(x) + dx, int(y) + dy
            if 0 <= X < W.W and 0 <= Y < W.H:
                out[Y, X] = out[Y, X] * 0.55 + np.array((60, 190, 170)) * 0.45
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, -1)):
            X, Y = int(x) + dx, int(y) + dy
            if 0 <= X < W.W and 0 <= Y < W.H:
                out[Y, X] = out[Y, X] * (1 - glow) + np.array((140, 255, 226)) * glow


# ---------------------------------------------------------------- vila
def village(t):
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
    tp = tav_p(t)
    if tp >= 1:
        B.smoke_at(img, t, TX + 13, TY, seed=3)
    fire_on = t >= PA
    if fire_on:
        W.smoke(img, t)
    W.ground_shadow(img, STX - 12, STY); W.ground_shadow(img, STX + 12, STY)
    ppl = people_now(t)
    items = [(STY - 0.5, 'statue', None)] + [(p[2], 'p', p) for p in ppl]
    if tp > 0:
        items.append((TB - 0.5, 'tavern', None))
    dog_i = IDX['Ana Sofia']
    for _, kind, p in sorted(items, key=lambda z: z[0]):
        if kind == 'statue':
            h, w = Q.STATUE.shape[:2]
            Q.blit_arr(img, Q.STATUE, STX - w // 2, STY - h)
            continue
        if kind == 'tavern':
            B.blit(img, TAVERN, TX, TY, p=tp, t=t)
            continue
        i, x, y, fr = p
        n, r = PEOPLE[i]
        rr = r if r else ('moradora' if n == 'Lila' else 'morador')
        if fr == 'lie':
            spr = np.rot90(F.folk(n, rr, 0), 1 if FIGHTERS.index(i) % 2 else -1)
            W.ground_shadow(img, x, y)
            W.blit(img, np.ascontiguousarray(spr), x, y)
            continue
        W.ground_shadow(img, x, y)
        W.blit(img, F.folk(n, rr, fr), x, y)
        if i == dog_i:
            W.ground_shadow(img, x + 14, y)
            W.blit(img, F.make_dog(int(t * 3) % 2), x + 14, y)
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
    if tp >= 0.9:                                       # luz da porta da taverna
        lv = (P.light_at(DOOR[0], DOOR[1] + 2, 40, t) * 0.9 * nf)[..., None]
        tm = tm * (1 - lv) + np.array((1.1, 0.9, 0.66)) * lv
    if steps_visible(t):
        lv = (P.light_at(290, 594, 52, t) * 0.55 * W.clamp((t - STEP_T0) / 1.0))[..., None]
        tm = tm * (1 - lv) + np.array((0.62, 1.1, 1.0)) * lv
    if STAGE0 - 0.1 <= t < TV:
        lv = (P.light_at(STAGE_CX, STAGE_Y - 4, 104, t) * 0.85)[..., None]
        tm = tm * (1 - lv) + np.array((1.0, 0.92, 0.8)) * lv
    out = np.where(W.LMASK[..., None], img * tm, s)
    if fire_on:
        W.fire(out, t, scale=W.ease((t - PA) / 0.3))
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.emissive(out, spr, *B.POS[name], strength=max(nf, 0.35 if name == 'forja' else 0) * 0.95, t=t)
    if tp >= 1:
        B.emissive(out, TAVERN, TX, TY, strength=max(nf, 0.5) * 0.95, t=t)
    if td > 1.5:
        k = W.clamp((td - 1.5) / 0.4)
        for fx, fy, ph, f in P.FLIES:
            if math.sin(t * f + ph) > 0.2:
                x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
                out[y, x] = out[y, x] * (1 - k) + np.array((226, 255, 140)) * k
    if nf > 0.2:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            out[254 + dy, 276 + dx] = (200, 255, 230)
    castle5(out, t)
    if TV + 0.2 <= t < TV + 1.4:
        Q.sparkles(out, DOOR[0], TB - 20, TV + 0.3, t, dur=1.0)
    brawl(out, t)
    footprints(out, t)
    if BR + 0.1 <= t < DS:                              # "!" em quem está olhando
        for i in [IDX['Miyuki']] + WATCH:
            x, y = [p[1:3] for p in ppl if p[0] == i][0]
            if (t * 4 + i) % 2 < 1.6:
                W.qmark(out, int(x) - 3, int(y) - 40, bang=True)
    if t >= DS + 0.9:
        for i in (IDX['Miyuki'], IDX['cubo']):
            x, y = [p[1:3] for p in ppl if p[0] == i][0]
            W.qmark(out, int(x) - 3, int(y) - 41)
    if t >= DS:                                         # tontos no chão
        for k, (x, y) in enumerate(LIE):
            for j in range(2):
                a = t * 6 + j * math.pi + k
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    put_px(out, x + 6 * math.cos(a) + dx, y - 12 + 2 * math.sin(a) + dy, (255, 230, 90))
    return out


# ---------------------------------------------------------------- floresta e ruínas
def ruin_wall(w, h, seed):
    s = B.Spr(w, h)
    r = random.Random(seed)
    tops, tp = [], r.randint(2, 8)
    for x in range(w):
        if x % 3 == 0:
            tp = max(0, min(h - 8, tp + r.randint(-4, 4)))
        tops.append(tp)
    for x in range(w):
        for y in range(tops[x], h):
            row = y // 4
            off = 3 if row % 2 else 0
            mortar = y % 4 == 3 or (x + off) % 7 == 6
            base = (132, 134, 146)
            c = B.shade(base, 0.68) if mortar else B.shade(base, 0.86 + r.random() * 0.2)
            if x >= w - 3:
                c = B.shade(c, 0.8)
            s.px(x, y, c)
        for y in range(tops[x], min(h, tops[x] + r.randint(1, 3))):
            s.px(x, y, (84, 136, 74) if r.random() < 0.7 else (110, 162, 88))
        if r.random() < 0.12:                           # hera descendo
            for y in range(tops[x], min(h, tops[x] + r.randint(5, 14))):
                s.px(x, y, (70, 120, 66))
    return s.outline()


RUNE = [(2, 0), (1, 1), (2, 1), (3, 1), (0, 2), (2, 2), (4, 2), (1, 3), (2, 3), (3, 3), (2, 4)]


def slab():
    w, h = 30, 58
    s = B.Spr(w, h)
    for y in range(h):
        for x in range(w):
            if y < 4 and (x < 4 - y or x > w - 5 + y):
                continue
            c = (116, 122, 138) if x < w - 6 else (92, 96, 112)
            if (x * 7 + y * 3) % 11 == 0:
                c = B.shade(c, 0.9)
            s.px(x, y, c)
    for x, y in ((6, 34), (7, 35), (7, 36), (8, 37), (8, 38), (9, 39), (21, 44), (22, 45), (22, 46), (23, 47)):
        s.px(x, y, (64, 66, 80))
    for x in range(0, 12):
        for y in range(0, 3 + (x % 3)):
            if s.a[y, x, 3] > 0:
                s.px(x, y, (84, 136, 74) if (x + y) % 3 else (110, 162, 88))
    for y in range(h - 5, h):
        for x in range(w):
            s.px(x, y, (100, 104, 118) if x < w - 5 else (80, 84, 98))
    rune = []
    for cx, cy in RUNE:
        for u in range(3):
            for v in range(3):
                X, Y = 8 + cx * 3 + u, 10 + cy * 3 + v
                s.px(X, Y, (48, 52, 66))
                rune.append((X, Y))
    return s.outline(), rune


def fallen_column(w):
    s = B.Spr(w, 10)
    for x in range(w):
        for y in range(10):
            c = (150, 150, 160) if y < 3 else ((128, 128, 140) if y < 7 else (100, 100, 112))
            if x % 9 == 0:
                c = B.shade(c, 0.8)
            s.px(x, y, c)
    for y in range(10):
        s.px(w - 1, y, (170, 170, 180) if 2 < y < 8 else (120, 120, 130))
    return s.outline()


SLAB, RUNE_PX = slab()
SLAB_X, SLAB_Y = 165, 456 - SLAB.h
RUNE_C = (SLAB_X + 15, SLAB_Y + 17)
WALL_L, WALL_R = ruin_wall(58, 36, 3), ruin_wall(52, 30, 8)
COLUMN = fallen_column(42)


def _ruins():
    H_, W_ = W.H, W.W
    a = np.zeros((H_, W_, 3), np.float32)
    a[:] = (18, 40, 38)
    r = random.Random(77)
    for _ in range(60):                                 # frestas de céu na copa
        x, y = r.randrange(W_), r.randrange(150, 250)
        a[y:y + 2, x:x + 2] = (70, 120, 110)
    gn = W.vnoise(H_, W_, 22, 34, 3)
    lvl = np.clip(np.floor(gn * 3.2 + (W.BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
    MOSS = np.array([(50, 94, 62), (60, 108, 68), (72, 122, 76)], np.float32)
    g = W.yy >= 300
    a[g] = MOSS[lvl[g]]
    for y in range(486, H_):                             # trilha
        cxp = 180 + math.sin(y / 38) * 6
        hw = 9 + (y - 486) / (H_ - 486) * 10
        for x in range(int(cxp - hw), int(cxp + hw) + 1):
            if 0 <= x < W_:
                a[y, x] = (126, 100, 72) if (x + y) % 5 else (110, 88, 62)
    pv = ((W.xx - 180) / 74) ** 2 + ((W.yy - 468) / 26) ** 2 <= 1   # calçamento antigo
    tile = ((W.xx // 6 + (W.yy // 4) % 2 * 3) % 2 == 0)
    a[pv] = np.where(tile[pv][:, None], np.array((112, 114, 124)), np.array((98, 100, 110)))
    a[pv & ((W.yy % 4 == 3) | (W.xx % 6 == 5))] = (72, 82, 74)
    a[pv & (W.vnoise(H_, W_, 10, 9, 2) > 0.62)] = (66, 112, 66)
    saved = W.land, W.lmask
    W.land, W.lmask = a, np.zeros((H_, W_), bool)
    try:
        for x0 in range(-6, W_ + 8, 9):
            W.pine(x0 + r.randint(-2, 2), 286 + r.randint(0, 6), r.randint(52, 70),
                   ((14, 34, 34), (18, 44, 42), (26, 56, 50), (10, 26, 28)))
        for x0 in range(-4, W_ + 8, 8):
            W.pine(x0 + r.randint(-2, 2), 312 + r.randint(0, 6), r.randint(40, 54),
                   ((18, 46, 44), (24, 60, 52), (34, 76, 62), (12, 34, 34)))
        for x0 in range(0, W_ + 8, 11):
            if 150 <= x0 <= 210:
                continue
            W.pine(x0 + r.randint(-2, 2), 340 + r.randint(0, 6), r.randint(40, 56),
                   ((22, 58, 50), (30, 76, 60), (46, 98, 72), (16, 42, 40)))
        W.oak(52, 578, 30, 11); W.oak(316, 566, 30, 12); W.oak(30, 420, 20, 13); W.oak(334, 404, 20, 14)
        for b_ in [(110, 520, 9, 21), (260, 516, 10, 22), (74, 468, 8, 23), (300, 470, 8, 24)]:
            W.bush(*b_)
        for rk in [(128, 452, 4, 3), (238, 446, 5, 4), (210, 498, 3, 3), (146, 500, 4, 3), (262, 478, 3, 2),
                   (96, 446, 3, 2)]:
            W.rock(*rk)
    finally:
        W.land, W.lmask = saved
    for spr, x0, y0 in ((WALL_L, 86, 438 - WALL_L.h), (WALL_R, 224, 442 - WALL_R.h), (COLUMN, 104, 478),
                        (SLAB, SLAB_X, SLAB_Y)):
        B.blit(a, spr, x0, y0)
    return a


RUINS = _ruins()
RSHAFT = (((W.xx * 0.55 + W.yy) % 120) < 14) & (W.yy < 430)
FOG = W.vnoise(W.H, W.W * 2, 30, 61, 2)
EXP_ARR = R0 + 2.2
EXP_SPOT = {'Rafaela': (180, 482), 'Andréa': (160, 490), 'Alexandra': (200, 490)}


def exped_pos(n, t):
    x1, y1 = EXP_SPOT[n]
    k = EXPED.index(n)
    q = W.clamp((t - R0 - 0.1 * k) / (EXP_ARR - R0))
    e = 1 - (1 - q) ** 2
    return x1, y1 + (620 - y1) * (1 - e), (1 + int(t / 0.13) % 2) if q < 1 else 0


def ruins_scene(t):
    img = RUINS.copy()
    ppl = sorted(((exped_pos(n, t), n) for n in EXPED), key=lambda z: z[0][1])
    for (x, y, fr), n in ppl:
        W.ground_shadow(img, x, y)
        W.blit(img, F.folk(n, ROLE[n], fr), x, y)
    tm = np.broadcast_to(np.array((0.6, 0.72, 0.82), np.float32), (W.H, W.W, 3)).copy()
    sh = RSHAFT & (W.BAY < 0.4 + 0.1 * math.sin(t * 1.5))
    tm[sh] *= 1.18
    rx, ry, _ = exped_pos('Rafaela', t)
    lv = (P.light_at(rx + 7, ry - 22, 30, t) * 0.8)[..., None]
    tm = tm * (1 - lv) + np.array((0.66, 1.1, 1.0)) * lv
    ig = W.clamp((t - RI) / 0.4)
    if ig > 0:
        lv = (P.light_at(RUNE_C[0], RUNE_C[1] + 30, 80, t) * 0.85 * ig)[..., None]
        tm = tm * (1 - lv) + np.array((0.62, 1.12, 1.04)) * lv
    out = img * tm
    fx = int(t * 6) % W.W                               # névoa
    fog = FOG[:, fx:fx + W.W]
    fm = (fog > 0.58) & (W.yy > 330) & (W.yy < 400) & (W.BAY < 0.5)
    out[fm] = out[fm] * 0.7 + np.array((120, 150, 150)) * 0.3
    r = random.Random(3)
    for k in range(26):                                 # esporos subindo
        x0, y0, sp = r.uniform(70, 290), r.uniform(330, 600), r.uniform(6, 14)
        y = (y0 - t * sp) % 300 + 300
        x = x0 + 3 * math.sin(t * 1.3 + k)
        if math.sin(t * 2 + k) > -0.3:
            put_px(out, x, y, (150, 240, 210))
    k_ = 0.6 + 0.4 * math.sin(t * 6)
    for X, Y in RUNE_PX:                                # a runa acende junto com a pedra
        X, Y = X + SLAB_X, Y + SLAB_Y
        if ig > 0:
            g = ig * (0.55 + 0.45 * k_)
            out[Y, X] = out[Y, X] * (1 - g) + np.array((170, 255, 236)) * g
    if ig > 0:
        for X, Y in RUNE_PX[::3]:
            X, Y = X + SLAB_X, Y + SLAB_Y
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                put_px(out, X + dx * 2, Y + dy * 2, out[Y + dy * 2, X + dx * 2] * 0.6 + np.array((90, 230, 200)) * 0.4)
        Q.sparkles(out, RUNE_C[0], RUNE_C[1] + 20, RI, t, dur=1.0, col=(170, 255, 236))
    Q.draw_stone(out, rx + 7, ry - 24, t, glow=1.0 + 0.5 * ig)
    if t >= RI + 0.25:
        for n in EXPED:
            x, y, _ = exped_pos(n, t)
            W.qmark(out, int(x) - 3, int(y) - 41, bang=True)
    return out


def rshot(t):
    q = W.ease(W.clamp((t - R0) / (PA - R0)))
    return (72, int(236 - 40 * q), 5)


# ---------------------------------------------------------------- câmera
def shot(t):
    if t < R0:
        return (44, 80, 4)
    if t < PA:
        return rshot(t)
    if t < STAGE0:
        return (44, 80, 4)
    if t < TV:
        return (STAGE_CX - 108, STAGE_Y - 250, 5)
    if t < EN:
        x0, y0, s = TSHOT
        if BR + 0.05 <= t < DS:
            r = random.Random(int(t * 20))
            x0 += r.choice((-1, 0, 1)); y0 -= r.choice((0, 1))
        return (x0, y0, s)
    return (44, 80, 4)


# ---------------------------------------------------------------- textos
CAPS = [
    (1.5, R0, 760, [(1.5, [('FALTAM ', WHITE), (f'{max(0, GOAL - N_FOLLOW)}', GOLD)], 170),
                    (1.5, [('PRO CASTELO.', WHITE)], 150)]),
    (R0, R0 + 1.9, 270, [(R0, [('NA FLORESTA, A PEDRA', WHITE)], 116), (R0 + 0.3, [('GUIOU A EXPEDIÇÃO…', TEAL)], 116)]),
    (R0 + 1.9, RI, 270, [(R0 + 1.9, [('…ATÉ AS RUÍNAS', WHITE)], 140), (R0 + 2.2, [('DE OUTRA VILA.', GOLD)], 140)]),
    (RI, PA, 270, [(RI, [('COM O MESMO', WHITE)], 140), (RI + 0.2, [('SÍMBOLO DA PEDRA.', TEAL)], 126)]),
    (PA, BT[2], 270, [(PA, [(f'CHEGARAM {len(NEW)}', WHITE)], 140), (PA + 0.3, [('MORADORES NOVOS:', GOLD)], 128)]),
    (BT[2], TV, 270, [(BT[2], [('E 2 NOVIDADES:', GOLD)], 140)]),
    (TV, BR, 270, [(TV, [('A MIYUKI ABRIU', WHITE)], 140), (TV + 0.3, [('UMA TAVERNA…', GOLD)], 150)]),
    (BR, DS, 270, [(BR, [('…E NO PRIMEIRO DIA', WHITE)], 116), (BR + 0.35, [('JÁ TEVE BRIGA.', GOLD)], 150)]),
    (DS, DS + 1.3, 270, [(DS, [('QUANDO A POEIRA', WHITE)], 140), (DS, [('BAIXOU…', WHITE)], 140)]),
    (DS + 1.3, EN, 270, [(DS + 1.3, [('…TINHA PEGADAS', WHITE)], 130), (DS + 1.3, [('IGUAIS ÀS DO EP. 3', TEAL)], 112),
                         (DS + 2.0, [('ENTRANDO NA TAVERNA.', GOLD)], 104)]),
    (EN, TEND + 1, 270, [(EN, [('QUEM NÃO SEGUE', WHITE)], 150), (EN + 0.3, [('NÃO MORA NA VILA.', GOLD)], 136)]),
    (EN + 0.9, TEND + 1, 880, [(EN + 0.9, [('COMENTA TEU NOME', WHITE)], 110), (EN + 0.9, [('E TUA FUNÇÃO', GOLD)], 110)]),
]


def overlay_state(t):
    st = []
    if t < 1.5:
        st.append(('count', NP))
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    b = batch_of(t)
    if b is not None and t >= BT[b] + 0.2:
        st.append(('stage', b))
    for k, (t0, *_r) in enumerate(POWS):
        if t0 <= t < t0 + 0.42:
            st.append(('pow', k))
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
        if k == 'count':
            E.draw_line(d, FW / 2, 760, [('ESTE REINO TEM', WHITE)], 140)
            E.draw_line(d, FW / 2, 760 + 0.78 * 140 + 10, [(f'{item[1]} MORADORES.', GOLD)], 180)
        elif k == 'cap':
            _, ci, nvis = item
            a, b, y, lines = CAPS[ci]
            for j, (ta, segs, size) in enumerate(lines):
                sz = E.fit(segs, size)
                if j > 0 and any(ch in 'ÁÉÍÓÚÂÊÔÃÕÀ' for s_, _ in segs for ch in s_):
                    y += 0.17 * sz
                if j < nvis:
                    E.draw_line(d, FW / 2, y, segs, size)
                y += 0.54 * sz + 0.24 * sz + 10
        elif k == 'stage':
            b = item[1]
            x0, y0, s = shot(BT[b] + 0.3)
            for j, (n, r) in enumerate(GROUPS[b]):
                cx = (SLOTS[len(GROUPS[b])][j] - x0) * s
                top = (STAGE_Y - y0) * s + 40
                Q.tag(d, cx, top, F.shown(n).upper(), TAGROLE.get(n, Q.short_role(r)).upper())
        elif k == 'pow':
            t0, x, y, word, col = POWS[item[1]]
            E.draw_line(d, x, y, [(word, col)], 130, stroke=10)
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
    a = arr[..., 3]
    ys, xs = np.nonzero(a)
    res = None
    if len(ys):
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        res = ((y0, y1, x0, x1), arr[y0:y1, x0:x1, :3].astype(np.float32), (arr[y0:y1, x0:x1, 3:4] / 255.0).astype(np.float32))
    _ov[state] = res
    return res


def frame(t):
    c = ruins_scene(t) if R0 <= t < PA else village(t)
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

    def thump(t0, g=0.5, f0=110):
        nn = int(0.16 * SR)
        tt = np.arange(nn) / SR
        f = f0 * np.exp(-tt * 18) + 40
        E.add(s, t0, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 20), g)
        nn2 = int(0.05 * SR)
        E.add(s, t0, E.noise(nn2, int(t0 * 997)) * np.exp(-np.arange(nn2) / SR * 60), g * 0.5)

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            blip(ta, 988, g=0.05)
    for k in range(12):                                   # castelo se desenhando
        chime(CAST0 + k * (CAST1 - CAST0) / 12, [67 + [0, 2, 4, 7, 9, 12][k % 6] + 12 * (k // 6)], g=0.05, dur=0.1)
    chime(CAST1, [79, 83, 86, 91], g=0.08)
    nn = int((PA - R0) * SR)                              # vento na floresta
    wind = E.lp(E.lp(E.noise(nn, 31), 0.05), 0.05)
    wind *= 0.6 + 0.4 * np.sin(2 * math.pi * 0.4 * np.arange(nn) / SR)
    E.add(s, R0, wind / (np.abs(wind).max() + 1e-9), 0.18)
    for k in range(int((EXP_ARR - R0) / 0.26)):            # passos na mata
        nn = int(0.04 * SR)
        E.add(s, R0 + 0.05 + k * 0.26, E.lp(E.noise(nn, 80 + k), 0.12) * np.exp(-np.arange(nn) / SR * 70), 0.28)
    nn = int(1.8 * SR)                                    # zumbido da runa
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 98 * tt) + 0.6 * np.sin(2 * math.pi * 147 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 3 * tt))
    E.add(s, RI - 0.1, hum * np.sin(math.pi * tt / 1.8), 0.16)
    chime(RI, [88, 84, 91, 96], g=0.07, step=0.1, dur=0.2)
    for b in range(NB):
        chime(BT[b] + 0.2, [79, 83, 86, 91], g=0.08)
    for k in range(4):                                    # martelo erguendo a taverna
        nn = int(0.03 * SR)
        E.add(s, TV + 0.05 + k * 0.2, E.sq(1800, nn, 0.5) * np.exp(-np.arange(nn) / SR * 120), 0.08)
    chime(TV + 0.85, [76, 79, 84, 88], g=0.08)
    r = random.Random(12)                                 # briga
    t = BR + 0.05
    while t < DS - 0.1:
        thump(t, g=r.uniform(0.25, 0.45), f0=r.uniform(90, 140))
        t += r.uniform(0.11, 0.22)
    for t0, *_x in POWS:
        thump(t0, g=0.6, f0=150)
    for t0, side, kind in FLY:                            # caneca quebrando / tábua
        tc = t0 + 0.72
        if kind == 'mug':
            nn = int(0.25 * SR)
            tt = np.arange(nn) / SR
            gl = E.noise(nn, int(tc * 100)) * np.exp(-tt * 18) * 0.5
            gl += (np.sin(2 * math.pi * 2700 * tt) + np.sin(2 * math.pi * 3900 * tt)) * np.exp(-tt * 14) * 0.25
            E.add(s, tc, gl, 0.3)
        else:
            nn = int(0.12 * SR)
            E.add(s, tc, E.lp(E.noise(nn, int(tc * 77)), 0.3) * np.exp(-np.arange(nn) / SR * 30), 0.35)
    nn = int(0.35 * SR)                                   # boing
    tt = np.arange(nn) / SR
    f = 260 + 380 * tt / 0.35 + 40 * np.sin(2 * math.pi * 14 * tt)
    E.add(s, BR + 1.2, np.sign(np.sin(2 * math.pi * np.cumsum(f) / SR)) * np.exp(-tt * 6) * 0.5, 0.12)
    nn = int(0.6 * SR)                                    # poeira baixando
    tt = np.arange(nn) / SR
    E.add(s, DS - 0.05, E.lp(E.noise(nn, 5), 0.15) * np.sin(math.pi * tt / 0.6) ** 2, 0.4)
    for k in range(len(STEPS5)):                          # pegadas acendendo
        tk = STEP_T0 + (k + 1) / len(STEPS5) * (STEP_T1 - STEP_T0)
        nn = int(0.09 * SR)
        E.add(s, tk, E.tri(E.midi([76, 79, 81, 84, 88][k % 5]), nn) * E.adsr(nn, dec=0.04, sus=0.3), 0.06)
    blip(DS + 0.9, 660, d=0.06, g=0.05); blip(DS + 0.98, 520, d=0.08, g=0.05)
    for k, m in enumerate([62, 66, 69, 74, 78, 81]):      # fanfarra do castelo
        nn = int(0.12 * SR)
        E.add(s, EN + 0.25 + k * 0.09, E.sq(E.midi(m + 12), nn, 0.25) * E.adsr(nn), 0.08)
    t = PA + 0.1                                          # fogueira
    while t < TEND:
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.05 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
    t = TV                                                # grilos
    while t < TEND:
        for k in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.02)
        t += r.uniform(0.55, 0.95)
    return s


def audio(path):
    total = TEND
    E.T4, E.T6, E.T7 = R0, PA, PA
    mus = E.music(total + 0.5)[:int(total * SR)]
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
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep5_{float(v):05.2f}.png'))
        return
    wav = os.path.join(OUTDIR, 'ep5.wav')
    audio(wav)
    out = os.path.join(OUTDIR, os.environ.get('NAMEOUT', 'brasa-ep5.mp4'))
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
