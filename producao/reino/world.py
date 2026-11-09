#!/usr/bin/env python3
"""Bifúrcia — mundo em pixel art (canvas 180x320, ampliado 6x ou 10x)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw

W, H = 180, 320
yy, xx = np.mgrid[0:H, 0:W]


def lerp(a, b, t):
    return a + (b - a) * t


def keyinterp(keys, v):
    if v <= keys[0][0]:
        return np.array(keys[0][1], float)
    for (p0, c0), (p1, c1) in zip(keys, keys[1:]):
        if v <= p1:
            k = (v - p0) / (p1 - p0)
            return np.array([lerp(a, b, k) for a, b in zip(c0, c1)], float)
    return np.array(keys[-1][1], float)


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


# ---------------------------------------------------------------- céu
SKY_TOP = [(0, (78, 148, 224)), (0.5, (96, 140, 214)), (1, (64, 54, 128)), (1.5, (26, 26, 70)), (2, (8, 10, 30))]
SKY_MID = [(0, (120, 186, 236)), (0.5, (200, 180, 176)), (1, (214, 104, 120)), (1.5, (70, 56, 120)), (2, (18, 22, 58))]
SKY_BOT = [(0, (196, 230, 242)), (0.5, (255, 206, 140)), (1, (255, 170, 96)), (1.5, (140, 90, 120)), (2, (40, 42, 92))]
TINT = [(0, (1, 1, 1)), (0.5, (1.04, 0.93, 0.80)), (1, (0.95, 0.68, 0.62)), (1.5, (0.48, 0.43, 0.65)), (2, (0.27, 0.30, 0.56))]
CLOUD = [(0, (250, 250, 255)), (0.5, (255, 232, 214)), (1, (255, 180, 170)), (1.5, (90, 70, 120)), (2, (34, 38, 74))]
CLOUD_SH = [(0, (212, 226, 242)), (0.5, (236, 190, 180)), (1, (214, 120, 140)), (1.5, (60, 48, 96)), (2, (24, 28, 60))]
SKYH, NB = 130, 16

_r = random.Random(11)
STARS = [(_r.randrange(W), _r.randrange(2, 104), _r.random() * 6.28, _r.random() < 0.15) for _ in range(80)]
CLOUDS = []
for cx, cy, n in [(20, 40, 5), (95, 22, 6), (150, 58, 4), (60, 74, 4)]:
    blobs = [(cx + _r.randint(-9, 9), cy + _r.randint(-2, 2), _r.randint(4, 7)) for _ in range(n)]
    CLOUDS.append(blobs)


def sky(td, t):
    top, mid, bot = [keyinterp(K, td) for K in (SKY_TOP, SKY_MID, SKY_BOT)]
    p = np.clip(yy / SKYH, 0, 1) * NB
    band = np.floor(p)
    frac = p - band
    band = band + ((frac > 0.6) & ((xx + yy) % 2 == 0))
    q = np.clip(band / NB, 0, 1)[..., None]
    c = np.where(q < 0.5, top + (mid - top) * (q / 0.5), mid + (bot - mid) * ((q - 0.5) / 0.5))
    nf = clamp((td - 1.2) / 0.6)
    # estrelas
    if nf > 0:
        for sx, sy, ph, big in STARS:
            tw = 0.55 + 0.45 * math.sin(t * 2.3 + ph)
            v = np.array([255, 250, 230]) * nf * tw
            c[sy, sx] = np.maximum(c[sy, sx], v)
            if big:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c[sy + dy, (sx + dx) % W] = np.maximum(c[sy + dy, (sx + dx) % W], v * 0.55)
    # sol
    if td < 1.3:
        sp = [(0, (138, 34)), (0.55, (132, 70)), (1.0, (126, 100)), (1.3, (122, 122))]
        scx, scy = keyinterp(sp, td)
        scol = keyinterp([(0, (255, 242, 176)), (0.55, (255, 216, 120)), (1, (255, 140, 80)), (1.3, (240, 100, 70))], td)
        r = 8
        d2 = (xx - scx) ** 2 + (yy - scy) ** 2
        halo = (d2 <= (r + 3) ** 2) & ((xx + yy) % 2 == 0) & (yy < SKYH)
        c[halo] = c[halo] * 0.6 + scol * 0.4
        c[d2 <= r * r] = scol
    # lua
    mf = clamp((td - 1.3) / 0.5)
    if mf > 0:
        mx, my, r = 38, 34, 6
        d1 = (xx - mx) ** 2 + (yy - my) ** 2 <= r * r
        d2 = (xx - mx - 3) ** 2 + (yy - my + 2) ** 2 <= (r - 1) ** 2
        m = d1 & ~d2
        c[m] = c[m] * (1 - mf) + np.array([238, 232, 204]) * mf
    # nuvens
    cc, cs = keyinterp(CLOUD, td), keyinterp(CLOUD_SH, td)
    ca = 1.0 if td < 1.5 else lerp(1.0, 0.6, clamp((td - 1.5) / 0.5))
    for k, blobs in enumerate(CLOUDS):
        off = (t * (1.2 + 0.4 * k)) % (W + 40)
        mask = np.zeros((H, W), bool)
        for bx, by, br in blobs:
            x0 = (bx + off + 20) % (W + 40) - 20
            mask |= ((xx - x0) ** 2 + ((yy - by) * 1.6) ** 2) <= br * br
        low = mask & ~np.roll(mask, -2, axis=0)
        body = mask & ~low
        c[body] = c[body] * (1 - ca) + cc * ca
        c[low] = c[low] * (1 - ca) + cs * ca
    return c


def birds(c, t):
    for k, (st, by) in enumerate([(0.0, 52), (0.3, 46), (0.55, 58)]):
        x = int(-6 + 16 * (t + 1.5 - st) + k * 7)
        y = int(by + 2 * math.sin(t * 3 + k))
        up = int(t * 8 + k) % 2 == 0
        pts = [(0, 0), (-1, -1), (1, -1), (-2, -1), (2, -1)] if up else [(0, 0), (-1, 0), (1, 0), (-2, 1), (2, 1)]
        for dx, dy in pts:
            if 0 <= x + dx < W and 0 <= y + dy < H:
                c[y + dy, x + dx] = (40, 48, 70)


# ---------------------------------------------------------------- terreno estático
land = np.zeros((H, W, 3), np.float32)
lmask = np.zeros((H, W), bool)


def put(x, y, col):
    if 0 <= x < W and 0 <= y < H:
        land[y, x] = col
        lmask[y, x] = True


def ridge(pts, seed):
    r = random.Random(seed)
    xs = np.arange(W)
    top = np.interp(xs, [p[0] for p in pts], [p[1] for p in pts])
    top = top + np.array([r.choice([0, 0, 0, 1, -1]) for _ in xs])
    return np.round(top).astype(int)


far = ridge([(0, 104), (16, 94), (30, 101), (48, 86), (66, 99), (84, 92), (100, 80), (118, 95), (136, 88),
             (154, 100), (170, 92), (180, 97)], 1)
for x in range(W):
    shade = far[min(x + 1, W - 1)] > far[x]
    for y in range(far[x], 141):
        col = (104, 122, 172) if shade else (126, 146, 192)
        if y - far[x] < 3 and far[x] < 97:
            col = (206, 214, 234) if shade else (236, 242, 250)
        put(x, y, col)
near = ridge([(0, 118), (22, 111), (46, 116), (70, 108), (96, 114), (120, 106), (150, 113), (180, 109)], 2)
for x in range(W):
    shade = near[min(x + 1, W - 1)] > near[x]
    for y in range(near[x], 141):
        put(x, y, (70, 110, 96) if shade else (84, 128, 108))

for y in range(128, 139):
    for x in range(W):
        put(x, y, (28, 70, 58))


def pine(x0, base, h, cm, cl, cd):
    for r_ in range(h):
        y = base - h + r_
        hw = round(r_ * 0.42) - (1 if r_ % 4 == 0 and r_ > 3 else 0)
        for dx in range(-hw, hw + 1):
            col = cl if dx < -hw // 2 else (cd if dx == hw else cm)
            put(x0 + dx, y, col)
    put(x0, base, (66, 48, 36))


_r = random.Random(5)
for x0 in range(-3, W + 4, 5):
    pine(x0 + _r.randint(-1, 1), 131 + _r.randint(0, 2), _r.randint(9, 14), (28, 74, 60), (40, 92, 70), (20, 52, 46))
for x0 in range(0, W + 4, 6):
    if 127 <= x0 <= 148:   # clareira atrás da ponte
        continue
    pine(x0 + 2 + _r.randint(-1, 1), 138, _r.randint(10, 16), (36, 92, 66), (56, 118, 80), (24, 60, 50))

# rio
for y, col in [(138, (124, 184, 228)), (139, (78, 146, 208)), (140, (78, 146, 208)), (141, (72, 138, 202)),
               (142, (64, 126, 194)), (143, (64, 126, 194)), (144, (60, 118, 186)), (145, (56, 110, 178)),
               (146, (52, 104, 170)), (147, (48, 96, 160))]:
    for x in range(W):
        put(x, y, col)
for x in range(W):
    put(x, 148, (72, 122, 62))

# campo
for y in range(149, H):
    for x in range(W):
        put(x, y, (116, 176, 84))
_r = random.Random(3)
for _ in range(950):
    x, y = _r.randrange(W), _r.randrange(150, H)
    put(x, y, (98, 154, 70)); put(x + 2, y, (98, 154, 70)); put(x + 1, y - 1, (98, 154, 70))
for _ in range(420):
    put(_r.randrange(W), _r.randrange(150, H), (148, 204, 100))
for _ in range(60):
    x, y = _r.randrange(W), _r.randrange(152, H)
    put(x, y, _r.choice([(255, 230, 120), (240, 124, 150), (250, 250, 250), (190, 150, 250)]))

# caminhos (bifurcação)
pm = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(pm)
d.polygon([(78, 320), (102, 320), (95, 198), (85, 198)], fill=255)
d.polygon([(-1, 189), (-1, 198), (88, 197), (88, 189)], fill=255)
d.polygon([(86, 191), (95, 196), (142, 149), (133, 149)], fill=255)
d.ellipse((63, 204, 117, 224), fill=255)
d.ellipse((79, 184, 101, 199), fill=255)
pmask = (np.array(pm) > 0) & (yy >= 149)
er = pmask.copy()
er[1:, :] &= pmask[:-1, :]; er[:-1, :] &= pmask[1:, :]; er[:, 1:] &= pmask[:, :-1]; er[:, :-1] &= pmask[:, 1:]
land[pmask] = (206, 172, 120)
land[pmask & ~er] = (170, 136, 92)
pts = np.argwhere(er)
for i in _r.sample(range(len(pts)), 150):
    y, x = pts[i]
    land[y, x] = _r.choice([(184, 150, 104), (226, 196, 146)])

# ponte
for y in range(136, 150):
    for x in range(132, 144):
        put(x, y, (156, 106, 64) if y % 2 == 0 else (132, 88, 52))
for y in range(133, 150):
    put(131, y, (104, 68, 38)); put(144, y, (104, 68, 38))
for x in (131, 144):
    put(x, 132, (80, 52, 30))

# placa A / B
GLYPH = {'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.']}
for y in range(172, 194):
    put(89, y, (140, 96, 56)); put(90, y, (110, 74, 42))
for x0, y0, tip in [(74, 173, -1), (91, 181, 1)]:
    for y in range(y0, y0 + 7):
        for x in range(x0, x0 + 15):
            edge = y in (y0, y0 + 6) or x in (x0, x0 + 14)
            put(x, y, (96, 60, 30) if edge else (204, 156, 94))
    # ponta da seta
    tx = x0 - 1 if tip < 0 else x0 + 15
    for k, (a, b) in enumerate([(1, 5), (2, 4), (3, 3)]):
        for y in range(y0 + a, y0 + b + 1):
            put(tx + tip * k, y, (96, 60, 30) if y in (y0 + a, y0 + b) else (204, 156, 94))
for y0 in (175, 183):   # tábuas sem letra (veios)
    for x0, x1 in ((77, 86), (93, 102)):
        if (y0 == 175) == (x0 == 77):
            for x in range(x0, x1):
                if x % 3:
                    put(x, y0 + 1, (176, 128, 74)); put(x + 1, y0 + 3, (176, 128, 74))

# fogueira (pedras e lenha)
for dx, dy in [(-5, 0), (-4, 1), (-2, 2), (0, 2), (2, 2), (4, 1), (5, 0), (-4, -1), (4, -1), (-2, -2), (2, -2), (0, -2)]:
    put(90 + dx, 213 + dy, (140, 138, 148)); put(90 + dx + 1, 213 + dy, (104, 102, 114))
for x, y in [(87, 213), (88, 212), (89, 212), (90, 212), (91, 212), (92, 212), (93, 213), (88, 213), (92, 213)]:
    put(x, y, (112, 72, 42))

# mastro
for y in range(158, 189):
    put(76, y, (200, 200, 210))
put(76, 157, (255, 210, 90)); put(75, 157, (230, 180, 70)); put(77, 157, (230, 180, 70))


# ---- decoração do campo


def oak(cx, base, r, seed):
    rr = random.Random(seed)
    for y in range(base - r - 3, base + 1):
        put(cx - 1, y, (104, 70, 42)); put(cx, y, (124, 84, 50)); put(cx + 1, y, (88, 58, 36))
    put(cx - 2, base, (88, 58, 36)); put(cx + 2, base, (88, 58, 36))
    cy = base - r - 4
    blobs = [(cx, cy, r), (cx - r * 0.6, cy + r * 0.35, r * 0.7), (cx + r * 0.6, cy + r * 0.3, r * 0.72),
             (cx, cy - r * 0.45, r * 0.7)]
    m = np.zeros((H, W), bool)
    for bx, by, br in blobs:
        m |= (xx - bx) ** 2 + (yy - by) ** 2 <= br * br
    rim = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    for y, x in np.argwhere(m):
        dx, dy = x - cx, y - cy
        if (x, y) and rim[y, x]:
            col = (30, 66, 46)
        elif dx + dy < -r * 0.5:
            col = (96, 168, 78)
        elif dx + dy > r * 0.6:
            col = (44, 98, 58)
        else:
            col = (64, 132, 66)
        if not rim[y, x] and rr.random() < 0.12:
            col = (110, 184, 88) if dx + dy < 0 else (40, 88, 54)
        put(x, y, col)


def bush(cx, cy, w):
    for y in range(cy - 3, cy + 1):
        for x in range(cx - w, cx + w + 1):
            if (x - cx) ** 2 / (w * w) + (y - cy + 0.5) ** 2 / 9 <= 1:
                top = y <= cy - 2
                put(x, y, (82, 150, 70) if top else (58, 116, 56))
    put(cx - w, cy, (36, 76, 44)); put(cx + w, cy, (36, 76, 44))
    put(cx - 1, cy - 2, (240, 120, 140)); put(cx + 2, cy - 1, (255, 230, 120))


def rock(cx, cy, w):
    for x in range(cx - w, cx + w + 1):
        put(x, cy, (110, 108, 120)); put(x, cy - 1, (150, 148, 160))
    for x in range(cx - w + 1, cx + w):
        put(x, cy - 2, (176, 174, 186))


def stump(cx, cy):
    for x in range(cx - 2, cx + 3):
        put(x, cy, (98, 64, 38)); put(x, cy - 1, (120, 80, 48)); put(x, cy - 2, (206, 170, 118))
    put(cx, cy - 2, (170, 130, 86))


def logs(cx, cy):
    for k, y in enumerate((cy, cy - 2, cy - 4)):
        n = 3 - k
        for j in range(n):
            x0 = cx - n * 2 + j * 4 + 1
            put(x0, y, (90, 58, 34)); put(x0 + 1, y, (120, 80, 48)); put(x0 + 2, y, (90, 58, 34))
            put(x0 + 1, y - 1, (210, 170, 110))


for x in range(2, 66, 7):
    for y in range(183, 188):
        put(x, y, (130, 92, 56))
    put(x, 182, (160, 118, 72))
    if x + 7 < 66:
        for k in range(1, 7):
            put(x + k, 184, (150, 108, 64))
oak(10, 214, 9, 1)
oak(170, 206, 8, 2)
oak(14, 296, 14, 3)
oak(166, 292, 15, 4)
oak(160, 168, 7, 5)
bush(36, 216, 5); bush(150, 230, 6); bush(124, 262, 5); bush(58, 250, 4); bush(30, 240, 4); bush(112, 162, 4)
rock(132, 214, 3); rock(44, 268, 2); rock(108, 286, 3); rock(20, 160, 2)
stump(120, 236); stump(52, 228)
logs(66, 228)

LAND = land.copy()
LMASK = lmask.copy()

# ---------------------------------------------------------------- moradores
SKINS = [(244, 204, 166), (176, 120, 84), (222, 168, 126), (126, 84, 58), (98, 64, 46)]
HAIRS = [(46, 34, 30), (206, 156, 72), (96, 58, 34), (156, 64, 42), (30, 30, 42), (226, 226, 226)]
TUNICS = [(204, 72, 72), (70, 122, 206), (232, 182, 62), (92, 164, 92), (164, 92, 174), (232, 132, 62),
          (72, 174, 172), (220, 220, 230)]
PANTS = [(84, 66, 58), (62, 62, 96), (112, 92, 62)]
BODY = ["..HHH..", ".HHHHH.", "..SSS..", "..ESE..", "..SSS..", ".TTTTT.", "STTTTTS", "STTTTTS", ".TDDDT."]
LEGS = {0: [".LL.LL.", ".LL.LL.", ".BB.BB."], 1: [".LL.L..", ".LL..L.", ".BB..BB"], 2: ["..L.LL.", ".L..LL.", "BB..BB."]}


def make_sprite(i, frame):
    style = i % 3
    rows = list(BODY) + LEGS[frame]
    rows = [list(r) for r in rows]
    if style == 1:   # cabelo comprido
        for r_ in (2, 3, 4):
            rows[r_][1] = 'H'; rows[r_][5] = 'H'
    pal = {'H': HAIRS[i % len(HAIRS)], 'S': SKINS[(i * 2) % len(SKINS)], 'E': (36, 26, 26),
           'T': TUNICS[(i * 3) % len(TUNICS)], 'L': PANTS[i % len(PANTS)], 'B': (50, 36, 30)}
    pal['D'] = tuple(int(v * 0.72) for v in pal['T'])
    h, w = len(rows) + (1 if style == 2 else 0), 7
    spr = np.zeros((h + 2, w + 2, 4), np.float32)
    off = 1 + (1 if style == 2 else 0)
    if style == 2:   # coque
        spr[1, 4, :3] = pal['H']; spr[1, 4, 3] = 1
    for r_, row in enumerate(rows):
        for c_, v in enumerate(row):
            if v != '.':
                spr[r_ + off, c_ + 1, :3] = pal[v]
                spr[r_ + off, c_ + 1, 3] = 1
    a = spr[..., 3] > 0
    ring = np.zeros_like(a)
    ring[1:, :] |= a[:-1, :]; ring[:-1, :] |= a[1:, :]; ring[:, 1:] |= a[:, :-1]; ring[:, :-1] |= a[:, 1:]
    ring &= ~a
    spr[ring, :3] = (34, 26, 32)
    spr[ring, 3] = 1
    return spr


SPRITES = {}


def sprite(i, frame):
    k = (i, frame)
    if k not in SPRITES:
        SPRITES[k] = make_sprite(i, frame)
    return SPRITES[k]


def blit(img, mask, spr, fx, fy):
    """fx, fy = pés (centro, última linha)."""
    h, w = spr.shape[:2]
    x0, y0 = int(round(fx)) - w // 2, int(round(fy)) - h + 2
    for r_ in range(h):
        y = y0 + r_
        if not (0 <= y < H):
            continue
        for c_ in range(w):
            x = x0 + c_
            if 0 <= x < W and spr[r_, c_, 3] > 0:
                img[y, x] = spr[r_, c_, :3]
                if mask is not None:
                    mask[y, x] = True
    return x0, y0


def ring_positions(n, cx=90, cy=214):
    pos = []
    inner = min(n, 8)
    for ring, (cnt, rx, ry) in enumerate([(inner, 21, 8), (n - inner, 32, 13)]):
        if cnt <= 0:
            continue
        base = [-90 + 360 * k / cnt for k in range(cnt)]
        best, br = -1, 0
        for rot in range(0, 360, 2):
            angs = [(a + rot) % 360 for a in base]
            dmin = min(min(abs((a - 90 + 180) % 360 - 180) for a in angs),
                       min(abs((a + 90 + 180) % 360 - 180) for a in angs) + 6)
            if dmin > best:
                best, br = dmin, rot
        for a in base:
            r = math.radians(a + br)
            pos.append((cx + rx * math.cos(r), cy + ry * math.sin(r)))
    return pos


QMARK = ['.###.', '#...#', '...#.', '..#..', '.....', '..#..']
EMARK = ['..#..', '..#..', '..#..', '..#..', '.....', '..#..']


_QMk = np.array([[c == '#' for c in row] for row in QMARK])
_QOk = np.zeros((8, 7), bool)
for _dy in (-1, 0, 1):
    for _dx in (-1, 0, 1):
        _QOk[1 + _dy:7 + _dy, 1 + _dx:6 + _dx] |= _QMk


_EM = np.array([[c == '#' for c in row] for row in EMARK])
_EO = np.zeros((8, 7), bool)
for _dy in (-1, 0, 1):
    for _dx in (-1, 0, 1):
        _EO[1 + _dy:7 + _dy, 1 + _dx:6 + _dx] |= _EM


def qmark(img, x, y, bang=False):
    """? (ou !) branco com contorno, topo em (x, y)."""
    _QM, _QO = (globals()['_EM'], globals()['_EO']) if bang else (globals()['_QMk'], globals()['_QOk'])
    for r_ in range(8):
        for c_ in range(7):
            X, Y = x + c_ - 1, y + r_ - 1
            if 0 <= X < W and 0 <= Y < H and _QO[r_, c_]:
                inside = 1 <= r_ <= 6 and 1 <= c_ <= 5 and _QM[r_ - 1, c_ - 1]
                img[Y, X] = (255, 255, 255) if inside else (30, 22, 40)


# ---------------------------------------------------------------- fogo e luz
def fire(img, t, scale=1.0, seed=0):
    r = random.Random(int(t * 10) + seed)
    base = [3, 6, 8, 6, 3]
    for i, dx in enumerate(range(-2, 3)):
        h = max(0, int((base[i] + r.randint(-1, 2)) * scale))
        for k in range(h):
            y = 211 - k
            rel = k / max(h, 1)
            if rel < 0.4 and abs(dx) <= 1:
                col = (255, 242, 176)
            elif rel < 0.75:
                col = (255, 178, 58)
            else:
                col = (238, 88, 40)
            img[y, 90 + dx] = col
    if scale > 0.5:
        for k in range(4):
            life = 1.1
            ph = (t + k * 0.29) % life
            sx = 90 + int(math.sin(k * 7 + t * 3) * 3)
            sy = 204 - int(ph * 18)
            if ph < life * 0.8 and 0 <= sy < H:
                img[sy, sx] = (255, 220, 120)


def light_level(t, cx=90, cy=209):
    fl = math.sin(t * 13) * 0.8 + math.sin(t * 7.3) * 0.6
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.9) ** 2)
    lv = np.zeros((H, W), np.float32)
    lv[d < 36 + fl] = 0.33
    lv[d < 24 + fl] = 0.62
    lv[d < 12 + fl] = 0.92
    return lv


MYST = (138, 127)


def myst_level():
    d = np.sqrt((xx - MYST[0]) ** 2 + ((yy - MYST[1]) * 1.4) ** 2)
    lv = np.zeros((H, W), np.float32)
    lv[d < 10] = 0.3
    lv[d < 6] = 0.6
    lv[d < 3] = 0.85
    return lv


MYST_LV = myst_level()

# ---------------------------------------------------------------- planta-fantasma (taverna A, muralha B)


def _pix(draw_fn):
    im = Image.new('L', (W, H), 0)
    draw_fn(ImageDraw.Draw(im))
    return np.array(im) > 0


TX = 6


def _tav_out(d):
    d.rectangle((18 + TX, 165, 50 + TX, 177), outline=255)
    d.line((15 + TX, 165, 34 + TX, 153), fill=255); d.line((34 + TX, 153, 53 + TX, 165), fill=255)
    d.line((15 + TX, 165, 53 + TX, 165), fill=255)
    d.rectangle((31 + TX, 170, 36 + TX, 177), outline=255)
    d.rectangle((22 + TX, 168, 26 + TX, 171), outline=255); d.rectangle((41 + TX, 168, 45 + TX, 171), outline=255)
    d.rectangle((44 + TX, 154, 46 + TX, 160), outline=255)
    d.line((51 + TX, 167, 56 + TX, 167), fill=255)
    d.rectangle((54 + TX, 168, 58 + TX, 172), outline=255)


def _tav_fill(d):
    d.rectangle((18 + TX, 165, 50 + TX, 177), fill=255)
    d.polygon([(15 + TX, 165), (34 + TX, 153), (53 + TX, 165)], fill=255)


def _wall_out(d):
    d.rectangle((105, 188, 141, 199), outline=255)
    for x in range(105, 132, 6):
        d.rectangle((x, 184, x + 3, 188), outline=255)
    d.rectangle((131, 176, 145, 199), outline=255)
    for x in (131, 136, 141):
        d.rectangle((x, 172, x + 3, 176), outline=255)
    d.rectangle((136, 190, 140, 199), outline=255)
    for y in (192, 196):
        for x in range(107, 130, 4):
            d.point((x, y), fill=255)


def _wall_fill(d):
    d.rectangle((105, 188, 141, 199), fill=255)
    d.rectangle((131, 176, 145, 199), fill=255)


def _order(mask):
    p = np.argwhere(mask)
    idx = np.lexsort((p[:, 1], -p[:, 0]))
    return p[idx]


GHOSTS = {
    'A': dict(out=_order(_pix(_tav_out)), fill=_pix(_tav_fill), col=np.array((110, 236, 226), float)),
    'B': dict(out=_order(_pix(_wall_out)), fill=_pix(_wall_fill), col=np.array((255, 178, 90), float)),
}


def ghost(img, key, p, t):
    g = GHOSTS[key]
    if p <= 0:
        return
    pulse = 0.82 + 0.18 * math.sin(t * 4 + (0 if key == 'A' else 1.7))
    fa = 0.2 * clamp((p - 0.85) / 0.15) * pulse
    if fa > 0:
        m = g['fill']
        img[m] = img[m] * (1 - fa) + g['col'] * fa
    n = int(len(g['out']) * clamp(p))
    pts = g['out'][:n]
    img[pts[:, 0], pts[:, 1]] = img[pts[:, 0], pts[:, 1]] * (1 - pulse) + g['col'] * pulse
    if p < 1 and n > 0:
        y, x = pts[-1]
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < W and 0 <= y + dy < H:
                img[y + dy, x + dx] = (255, 255, 255)
