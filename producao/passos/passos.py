#!/usr/bin/env python3
"""10.000 PASSOS — POV de um herói com espada numa trilha de pedra na floresta, em pixel art de baixa resolução.
Cada seguidor = 1 passo. Cada vídeo anda de PREV até N passos (N = seguidores hoje). Objetivo: 10.000.
Uso: N=73 PREV=0 DIA=1 python3 passos.py   (STILLS=0.5,6,14 só gera quadros)"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/reino')
import ep1hd as E

N = int(os.environ.get('N', '73'))
PREV = int(os.environ.get('PREV', '0'))
DIA = int(os.environ.get('DIA', '1'))
GOAL = 10000
OUT = '/home/claude/passos/out'
FW, FH, FPS = 1080, 1920, 30
CW, CH, S = 90, 160, 12                  # tela de 90x160 px, ampliada 12x
HOR0 = 80                                # linha do horizonte
FOC, CAMH = 70.0, 1.0
STEP_LEN = 0.75
T_WALK0, T_WALK1 = 1.0, 12.0
TEND = 17.0
WHITE, GOLD, TEAL = (255, 255, 255), (255, 208, 72), (110, 236, 214)
CX = CW / 2


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def steps_at(t):
    """passo (contínuo) em que o herói está no instante t."""
    if t <= T_WALK0:
        return float(PREV)
    q = clamp((t - T_WALK0) / (T_WALK1 - T_WALK0))
    e = 0.35 * q + 0.65 * (q - math.sin(2 * math.pi * q) / (2 * math.pi))
    return PREV + (N - PREV) * e


def curve(z):
    return 0.9 * math.sin(z * 0.045) + 0.4 * math.sin(z * 0.11 + 1.3)


def curve_v(z):
    return 0.9 * np.sin(z * 0.045) + 0.4 * np.sin(z * 0.11 + 1.3)


def h2(a, b):
    """hash inteiro -> [0,1) (vetorizado)."""
    v = (a * 374761393 + b * 668265263) & 0xFFFFFFFF
    v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
    return (v & 0xFFFF) / 65536.0


BAY = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
BAYF = np.tile(BAY, (CH // 4, CW // 4 + 1))[:, :CW]
YY, XX = np.mgrid[0:CH, 0:CW]
SKY_TOP, SKY_HOR = np.array((96, 158, 206)), np.array((206, 224, 210))
FOG = np.array((196, 216, 204))


# ---------------------------------------------------------------- floresta ao fundo (estática)
def _ridge(seed, base, amp, step):
    r = random.Random(seed)
    hs = []
    for x in range(CW + 40):
        if x % step == 0:
            peak = r.uniform(0.3, 1.0) * amp
        k = x % step
        hs.append(base - peak * (1 - abs(k - step / 2) / (step / 2)) - r.uniform(0, 1.2))
    return hs


RIDGE_FAR = _ridge(3, 0, 13, 7)
RIDGE_NEAR = _ridge(8, 0, 20, 9)


# ---------------------------------------------------------------- objetos ao lado da trilha
OBJS = []
_r = random.Random(21)
for k in range(1400):
    z = k * 0.62 + _r.uniform(0, 0.5)
    side = -1 if k % 2 else 1
    kind = _r.choices(['pine', 'pine', 'pine', 'oak', 'bush', 'rock'], k=1)[0]
    if kind in ('bush', 'rock'):
        x = side * _r.uniform(1.25, 2.2)
    else:
        x = side * _r.uniform(1.7, 4.6)
    OBJS.append((z, x, kind, _r.uniform(3.2, 5.8) if kind == 'pine' else _r.uniform(2.6, 3.6), _r.randrange(1 << 20)))
OBJS = [o for o in OBJS if not (3.5 < o[0] < 8 and o[1] > 0)]
SIGN_Z = 5.6
OBJS.append((SIGN_Z, 1.3, 'sign', 1.2, 0))
OBJS.sort()
OBJ_Z = np.array([o[0] for o in OBJS])


def fog_amt(z):
    return clamp((z - 6) / 34) ** 0.8


def mix(c, f):
    return tuple(int(c[i] * (1 - f) + FOG[i] * f) for i in range(3))


def draw_pine(img, sx, base, hpx, z, seed):
    hpx = int(hpx)
    if hpx < 3:
        return
    f = fog_amt(z)
    dark, mid, lit, out = mix((22, 64, 50), f), mix((34, 90, 62), f), mix((60, 124, 78), f), mix((14, 40, 34), f)
    trunk_h = max(1, hpx // 9)
    for y in range(base - trunk_h, base + 1):
        if 0 <= y < CH:
            w = max(0, hpx // 22)
            for x in range(int(sx - w), int(sx + w) + 1):
                if 0 <= x < CW:
                    img[y, x] = mix((76, 52, 36), f)
    tiers = 3 if hpx < 40 else 4
    top = base - trunk_h - hpx
    th = hpx / tiers
    for r_ in range(hpx):
        y = top + r_
        if y < 0 or y >= CH:
            continue
        within = (r_ % th) / th
        tier = int(r_ / th)
        hw = (0.18 + 0.22 * (tier + within) / tiers) * hpx * (0.55 + 0.45 * within)
        x0, x1 = int(round(sx - hw)), int(round(sx + hw))
        for x in range(max(0, x0), min(CW, x1 + 1)):
            if x in (x0, x1) or (within > 0.88):
                c = out
            elif x < sx - hw * 0.3:
                c = lit
            elif x > sx + hw * 0.35:
                c = dark
            else:
                c = mid
            img[y, x] = c


def draw_oak(img, sx, base, hpx, z, seed):
    hpx = int(hpx)
    if hpx < 3:
        return
    f = fog_amt(z)
    r = random.Random(seed)
    th = int(hpx * 0.4)
    tw = max(1, hpx // 12)
    for y in range(base - th, base + 1):
        if 0 <= y < CH:
            for x in range(int(sx - tw), int(sx + tw) + 1):
                if 0 <= x < CW:
                    img[y, x] = mix((96, 66, 42) if x < sx else (72, 48, 30), f)
    cy, R = base - th - hpx * 0.32, hpx * 0.42
    blobs = [(sx, cy, R)] + [(sx + r.uniform(-0.6, 0.6) * R, cy + r.uniform(-0.4, 0.3) * R, R * r.uniform(0.45, 0.7)) for _ in range(5)]
    y0, y1 = int(cy - R * 1.5), int(cy + R * 1.2)
    x0, x1 = int(sx - R * 1.6), int(sx + R * 1.6)
    y0c, y1c, x0c, x1c = max(0, y0), min(CH, y1), max(0, x0), min(CW, x1)
    if y0c >= y1c or x0c >= x1c:
        return
    yy, xx = YY[y0c:y1c, x0c:x1c], XX[y0c:y1c, x0c:x1c]
    m = np.zeros(yy.shape, bool)
    for bx, by, br in blobs:
        m |= (xx - bx) ** 2 + (yy - by) ** 2 <= br * br
    v = ((xx - sx) + (yy - cy)) / max(R, 1)
    reg = img[y0c:y1c, x0c:x1c]
    rim = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    for cond, col in ((v < -0.5, (110, 176, 92)), ((v >= -0.5) & (v < 0.3), (74, 140, 70)), (v >= 0.3, (48, 102, 56))):
        reg[m & cond] = mix(col, f)
    reg[rim] = mix((26, 60, 40), f)


def draw_bush(img, sx, base, wpx, z, seed):
    f = fog_amt(z)
    R = max(1.0, wpx / 2)
    y0c, y1c = max(0, int(base - R * 1.4)), min(CH, int(base) + 1)
    x0c, x1c = max(0, int(sx - R * 1.5)), min(CW, int(sx + R * 1.5) + 1)
    if y0c >= y1c or x0c >= x1c:
        return
    yy, xx = YY[y0c:y1c, x0c:x1c], XX[y0c:y1c, x0c:x1c]
    m = ((xx - sx) / (R * 1.4)) ** 2 + ((yy - base) / (R * 1.2)) ** 2 <= 1
    reg = img[y0c:y1c, x0c:x1c]
    v = (xx - sx) / (R * 1.4) + (yy - base + R) / R
    reg[m] = mix((70, 132, 66), f)
    reg[m & (v < 0.2)] = mix((104, 168, 84), f)
    reg[m & (v > 1.1)] = mix((44, 92, 50), f)
    r = random.Random(seed)
    if wpx > 6:
        for _ in range(3):
            x, y = int(sx + r.uniform(-R, R)), int(base - r.uniform(0.3, 1.0) * R)
            if 0 <= x < CW and 0 <= y < CH and m[min(m.shape[0] - 1, y - y0c), min(m.shape[1] - 1, x - x0c)]:
                img[y, x] = mix(r.choice([(250, 230, 120), (240, 120, 150), (250, 250, 250)]), f)


def draw_rock(img, sx, base, wpx, z, seed):
    f = fog_amt(z)
    R = max(1.0, wpx / 2)
    y0c, y1c = max(0, int(base - R * 1.3)), min(CH, int(base) + 1)
    x0c, x1c = max(0, int(sx - R * 1.3)), min(CW, int(sx + R * 1.3) + 1)
    if y0c >= y1c or x0c >= x1c:
        return
    yy, xx = YY[y0c:y1c, x0c:x1c], XX[y0c:y1c, x0c:x1c]
    m = ((xx - sx) / (R * 1.2)) ** 2 + ((yy - base + R * 0.3) / R) ** 2 <= 1
    m &= yy <= base
    v = (xx - sx) / R + (yy - base + R) / R
    reg = img[y0c:y1c, x0c:x1c]
    reg[m] = mix((150, 150, 158), f)
    reg[m & (v < 0.4)] = mix((190, 190, 196), f)
    reg[m & (v > 1.2)] = mix((104, 104, 116), f)


F3 = {'V': ['#.#', '#.#', '#.#', '#.#', '.#.'], 'O': ['###', '#.#', '#.#', '#.#', '###'],
      'L': ['#..', '#..', '#..', '#..', '###'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
      'E': ['###', '#..', '##.', '#..', '###']}


def _sign_sprite():
    w, h = 25, 24
    a = np.zeros((h, w, 4), np.uint8)
    a2 = None
    for x in (5, 19):                                  # postes
        a[10:h, x:x + 2] = (92, 62, 38, 255)
        a[10:h, x + 1] = (70, 46, 28, 255)
    a[1:12, 0:w] = (40, 26, 18, 255)                   # borda
    a[2:11, 1:w - 1] = (150, 104, 62, 255)             # tábua
    a[6, 1:w - 1] = (122, 82, 48, 255)
    a[2:4, 17:21] = (112, 74, 42, 255)                 # lasca
    x = 3
    for ch in 'VOLTE':
        for r_, row in enumerate(F3[ch]):
            for c_, v in enumerate(row):
                if v == '#':
                    a[4 + r_, x + c_] = (206, 34, 30, 255)
        x += 4
    big = np.repeat(np.repeat(a, 2, 0), 2, 1)
    big[8:20, 4:46][np.all(big[8:20, 4:46, :3] == (206, 34, 30), -1)] = (206, 34, 30, 255)
    return Image.fromarray(big, 'RGBA')


SIGN = _sign_sprite()


def draw_sign(img, sx, base, wpx, z, seed):
    w = max(2, int(round(wpx)))
    h = max(2, int(round(wpx * SIGN.height / SIGN.width)))
    sp = np.asarray(SIGN.resize((w, h), Image.NEAREST), np.float32)
    f = fog_amt(z)
    x0, y0 = int(round(sx - w / 2)), int(round(base - h))
    for yy in range(h):
        Y = y0 + yy
        if not 0 <= Y < CH:
            continue
        for xx in range(w):
            X = x0 + xx
            if 0 <= X < CW and sp[yy, xx, 3] > 0:
                img[Y, X] = sp[yy, xx, :3] * (1 - f) + FOG * f


DRAW = {'pine': draw_pine, 'oak': draw_oak, 'bush': draw_bush, 'rock': draw_rock, 'sign': draw_sign}


# ---------------------------------------------------------------- espada (POV)
def draw_sword(img, ox, oy):
    hx, hy = 70 + ox, 152 + oy                         # mão
    tx, ty = 53 + ox, 84 + oy                          # ponta
    ax, ay = tx - hx, ty - hy
    L = math.hypot(ax, ay)
    ux, uy = ax / L, ay / L                            # ao longo da lâmina
    px_, py_ = -uy, ux                                 # atravessado
    dx, dy = XX - hx, YY - hy
    u = dx * ux + dy * uy                              # 0 na mão, L na ponta
    v = dx * px_ + dy * py_
    blade0 = 15
    half = np.where(u > L - 7, 2.6 * (L - u) / 7, 2.6)
    m = (u >= blade0) & (u <= L) & (np.abs(v) <= half)
    rim = (u >= blade0 - 0.5) & (u <= L + 0.8) & (np.abs(v) <= half + 1.0) & ~m
    img[rim] = (28, 30, 42)
    img[m & (v < -0.9)] = (236, 242, 250)
    img[m & (v >= -0.9) & (v < 0.6)] = (184, 194, 212)
    img[m & (v >= 0.6)] = (118, 126, 150)
    img[m & (np.abs(v) < 0.5) & (u > blade0 + 4) & (u < L - 10)] = (150, 160, 182)   # canaleta
    g = (u >= blade0 - 3) & (u < blade0) & (np.abs(v) <= 8)                         # guarda
    img[(u >= blade0 - 4) & (u < blade0 + 1) & (np.abs(v) <= 9) & ~g] = (40, 30, 24)
    img[g] = (214, 172, 72)
    img[g & (u < blade0 - 1.5)] = (150, 108, 44)
    gr = (u >= 2) & (u < blade0 - 3) & (np.abs(v) <= 1.8)                            # cabo
    img[gr] = (96, 60, 36)
    img[gr & ((np.floor(u) % 3) == 0)] = (64, 40, 26)
    # mão (luva) e manga
    hand = ((dx * ux + dy * uy - 6) ** 2 / 30 + (dx * px_ + dy * py_ - 1) ** 2 / 26) <= 1
    img[hand] = (132, 88, 54)
    img[hand & (v < -1.5)] = (168, 118, 74)
    for k in range(3):
        kn = ((u - (3 + k * 3)) ** 2 + (v + 3.5) ** 2) <= 1.4
        img[kn & hand] = (186, 136, 88)
    sleeve = (u < 2) & (u > -40) & (np.abs(v + 1) <= 6 - u * 0.12)
    img[sleeve & ~hand] = (52, 62, 112)
    img[sleeve & ~hand & (v < -3)] = (72, 84, 140)
    cuff = (u >= -1) & (u < 1.5) & (np.abs(v + 1) <= 6.5) & ~hand
    img[cuff] = (214, 172, 72)


# ---------------------------------------------------------------- cena
def scene(t):
    s = steps_at(t)
    travel = s * STEP_LEN
    ph = s - math.floor(s)
    moving = T_WALK0 < t < T_WALK1
    bob = int(round(abs(math.sin(ph * math.pi)) * 1.6)) if moving else 0
    hor = HOR0 + bob
    img = np.zeros((CH, CW, 3), np.float32)
    # céu
    q = np.clip(YY / max(1, hor), 0, 1)[..., None]
    sky = SKY_TOP * (1 - q) + SKY_HOR * q
    img[:] = sky
    # raio de sol
    sun_x, sun_y = 64, 22
    d = np.sqrt((XX - sun_x) ** 2 + (YY - sun_y) ** 2)
    glow = np.clip(1 - d / 26, 0, 1) ** 2
    img += (glow[..., None] * np.array((60, 50, 20))) * (BAYF[..., None] < 0.8)
    img[d < 4.5] = (255, 246, 200)
    # cordilheiras de árvores ao fundo (deslocam com a curva)
    shift = int(round(curve(travel + 30) * 6))
    for ridge, col, off in ((RIDGE_FAR, (150, 182, 168), 0), (RIDGE_NEAR, (104, 142, 118), 0)):
        for x in range(CW):
            hh = ridge[(x + shift + 20) % len(ridge)]
            y0 = int(hor + hh - 1)
            img[max(0, y0):hor, x] = col
    # objetivo no fim da trilha: torre com luz pulsando, no meio da névoa
    gx = int(CX + (curve(travel + 60) - curve(travel)) * 5)
    pulse = 0.6 + 0.4 * math.sin(t * 3)
    for y in range(hor - 17, hor):
        w = 1 if y < hor - 11 else (2 if y < hor - 5 else 3)
        for x in range(gx - w, gx + w + 1):
            img[y, x] = img[y, x] * 0.3 + np.array((70, 86, 100)) * 0.7
    img[hor - 19:hor - 17, gx] = (70, 86, 100)
    gl = np.clip(1 - np.sqrt((XX - gx) ** 2 + ((YY - (hor - 15)) * 1.1) ** 2) / 13, 0, 1) ** 2 * pulse
    img = img * (1 - gl[..., None] * 0.8) + np.array((150, 255, 230)) * gl[..., None] * 0.8
    img[hor - 16:hor - 13, gx] = (230, 255, 248)
    img[hor - 15, gx - 1:gx + 2] = (230, 255, 248)
    # chão (trilha + grama)
    rows = np.arange(hor + 1, CH)
    dz = CAMH * FOC / (rows - hor)                    # distância de cada linha
    zw = dz + travel
    xr = (XX[hor + 1:CH] - CX) * dz[:, None] / FOC     # x no mundo em relação à câmera
    rel = xr - (curve_v(zw) - curve(travel))[:, None]  # em relação ao centro da trilha
    ZW = np.broadcast_to(zw[:, None], rel.shape)
    path = np.abs(rel) < 0.9
    edge = (np.abs(rel) >= 0.9) & (np.abs(rel) < 1.08)
    vrow = ZW / 0.42
    rowi = np.floor(vrow).astype(np.int64)
    ucol = rel / 0.42 + 0.5 * (rowi % 2)
    coli = np.floor(ucol).astype(np.int64)
    fu, fv = ucol - coli, vrow - rowi
    hsh = h2(coli + 5000, rowi + 5000)
    stone = np.stack([128 + 30 * hsh, 124 + 28 * hsh, 118 + 26 * hsh], -1)
    moss = hsh > 0.86
    stone[moss] = (96, 128, 80)
    mortar = (fu < 0.12) | (fv < 0.14)
    stone[mortar] = (78, 76, 72)
    gstripe = (np.floor(ZW / 1.4) % 2) == 0
    grass = np.where(gstripe[..., None], np.array((92, 158, 70)), np.array((80, 142, 62))).astype(np.float32)
    fl = h2(np.floor(rel * 4).astype(np.int64) + 9000, np.floor(ZW * 4).astype(np.int64) + 9000)
    grass[fl > 0.985] = (240, 226, 120)
    grass[(fl > 0.97) & (fl <= 0.985)] = (122, 186, 92)
    ground = np.where(path[..., None], stone, grass)
    ground[edge] = (70, 96, 60)
    fz = np.clip((dz - 6) / 34, 0, 1) ** 0.8
    ground = ground * (1 - fz[:, None, None]) + FOG * fz[:, None, None]
    img[hor + 1:CH] = ground
    # objetos (de longe pra perto)
    i0, i1 = np.searchsorted(OBJ_Z, travel + 0.7), np.searchsorted(OBJ_Z, travel + 46)
    for k in range(i1 - 1, i0 - 1, -1):
        z, x, kind, size, seed = OBJS[k]
        dzo = z - travel
        sx = CX + (x + curve(z) - curve(travel)) * FOC / dzo
        base = hor + CAMH * FOC / dzo
        if kind in ('pine', 'oak'):
            hpx = size * FOC / dzo
            if sx + hpx * 0.6 < -2 or sx - hpx * 0.6 > CW + 2:
                continue
            DRAW[kind](img, sx, int(base), hpx, dzo, seed)
        else:
            wpx = {'bush': 0.55, 'rock': 0.4, 'sign': 1.2}[kind] * FOC / dzo
            DRAW[kind](img, sx, base, wpx, dzo, seed)
    # luz entre as árvores (feixes)
    # espada
    sw = math.sin(ph * 2 * math.pi) if moving else 0
    draw_sword(img, int(round(sw * 1.5)), int(round(abs(sw) * 2)) if moving else int(round(math.sin(t * 2) * 0.6)))
    return np.clip(img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- textos
def fmt(n):
    return f'{n:,}'.replace(',', '.')


def overlay_frame(t, im):
    d = ImageDraw.Draw(im)
    s = steps_at(t)
    cnt = int(math.floor(s + 1e-6)) if N >= PREV else int(math.ceil(s - 1e-6))
    done = t >= T_WALK1 + 0.25
    if t < 2.4:
        E.draw_line(d, FW / 2, 240, [('DISSERAM PRA ELE ', WHITE), ('NÃO IR LÁ…', (255, 96, 86))], 84)
    elif t < 5.0:
        E.draw_line(d, FW / 2, 240, [('…MAS ELE ', WHITE), ('CONTINUA ANDANDO.', GOLD)], 84)
    elif not done:
        E.draw_line(d, FW / 2, 240, [('CADA SEGUIDOR = ', WHITE), ('1 PASSO', GOLD)], 84)
    else:
        E.draw_line(d, FW / 2, 240, [('FALTAM ', WHITE), (fmt(max(0, GOAL - N)), GOLD), (' PASSOS', WHITE)], 84)
    E.draw_line(d, FW / 2, 352, [(f'DIA {DIA}', TEAL)], 56)
    pop = 1.0
    if done:
        pop = 1 + 0.25 * max(0.0, 1 - (t - T_WALK1 - 0.25) / 0.25)
    E.draw_line(d, FW / 2, 430, [(fmt(cnt), GOLD)], int(230 * pop), stroke=12)
    # barra até 10.000
    x0, x1, y0 = 190, 890, 640
    E.panel(d, (x0 - 16, y0 - 14, x1 + 16, y0 + 40), b=5)
    d.rectangle((x0, y0, x1, y0 + 26), fill=(60, 50, 80, 255))
    fill = x0 + (x1 - x0) * min(1, cnt / GOAL)
    d.rectangle((x0, y0, max(x0 + 6, fill), y0 + 26), fill=(255, 190, 60, 255))
    d.text((x1, y0 + 70), f'{fmt(cnt)} / {fmt(GOAL)}', font=E.font(40), fill=(240, 236, 250, 255), anchor='rm',
           stroke_width=4, stroke_fill=(24, 18, 44, 255))
    if t >= T_WALK1 + 1.0:
        E.draw_line(d, FW / 2, 1010, [('O QUE TEM NO FIM', WHITE)], 96)
        E.draw_line(d, FW / 2, 1110, [('DA TRILHA?', TEAL)], 110)
    if t >= T_WALK1 + 2.0:
        E.draw_line(d, FW / 2, 1270, [('SEGUE PRA ELE ANDAR.', GOLD)], 88)
    return im


def frame(t):
    c = scene(t)
    big = Image.fromarray(c).resize((FW, FH), Image.NEAREST)
    return np.array(overlay_frame(t, big))


# ---------------------------------------------------------------- áudio
SR = E.SR


def audio(path):
    n = int((TEND + 0.3) * SR)
    s = np.zeros(n)
    r = random.Random(7)
    wind = E.lp(E.lp(E.noise(n, 3), 0.03), 0.03)
    wind = wind / (np.abs(wind).max() + 1e-9) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.2 * np.arange(n) / SR))
    s += wind * 0.18
    t = 0.3
    while t < TEND:                                   # passarinhos
        nn = int(0.09 * SR)
        tt = np.arange(nn) / SR
        f0 = r.uniform(2600, 3800)
        chirp = np.sin(2 * math.pi * np.cumsum(f0 + 900 * np.sin(2 * math.pi * 22 * tt)) / SR) * np.hanning(nn)
        for k in range(r.randint(1, 3)):
            E.add(s, t + k * 0.11, chirp, 0.04)
        t += r.uniform(0.8, 2.2)
    last = PREV
    for i in range(int(T_WALK0 * FPS), int(T_WALK1 * FPS) + 2):   # um passo cada vez que o contador muda
        tt_ = i / FPS
        c = int(math.floor(steps_at(tt_) + 1e-6))
        if c != last:
            for j in range(abs(c - last)):
                ts = tt_ + j * 0.01
                nn = int(0.07 * SR)
                env = np.exp(-np.arange(nn) / SR * 55)
                thump = np.sin(2 * math.pi * (95 if (c + j) % 2 else 80) * np.arange(nn) / SR) * env
                grit = E.lp(E.noise(nn, int(ts * 1000)), 0.35) * np.exp(-np.arange(nn) / SR * 90)
                E.add(s, ts, thump * 0.5 + grit * 0.6, 0.35)
                nb = int(0.02 * SR)
                E.add(s, ts, E.sq(1760 + 40 * ((c + j) % 5), nb, 0.25) * np.exp(-np.arange(nb) / SR * 120), 0.03)
            last = c
    nn = int(2.2 * SR)                                # tom grave do aviso
    tt = np.arange(nn) / SR
    E.add(s, 0.0, (np.sin(2 * math.pi * 55 * tt) + 0.5 * np.sin(2 * math.pi * 82.4 * tt)) * np.exp(-tt * 1.2), 0.18)
    for k, m in enumerate([72, 76, 79, 84]):           # parou: acorde
        nn = int(0.4 * SR)
        E.add(s, T_WALK1 + 0.25 + k * 0.07, E.tri(E.midi(m), nn) * E.adsr(nn, dec=0.2, sus=0.4), 0.09)
    nn = int(3.5 * SR)                                # zumbido do que tem no fim
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 110 * tt) + 0.5 * np.sin(2 * math.pi * 165 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 2 * tt))
    E.add(s, T_WALK1 + 0.9, hum * np.sin(math.pi * tt / 3.5), 0.1)
    s = s / (np.abs(s).max() + 1e-9) * 0.85
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    st = os.environ.get('STILLS')
    if st:
        for v in st.split(','):
            Image.fromarray(frame(float(v))).save(f'{OUT}/p_{float(v):05.2f}.png')
        raise SystemExit
    wav = f'{OUT}/passos.wav'
    audio(wav)
    out = f'{OUT}/passos-dia{DIA}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(TEND * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(out)
