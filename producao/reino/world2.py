#!/usr/bin/env python3
"""Brasa — mundo em pixel art detalhado (canvas 360x640; ampliado 3x, 4x ou 5x)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw

W, H = 360, 640
yy, xx = np.mgrid[0:H, 0:W]
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
BAY = np.tile(BAYER, (H // 4, W // 4))


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def keyinterp(keys, v):
    if v <= keys[0][0]:
        return np.array(keys[0][1], float)
    for (p0, c0), (p1, c1) in zip(keys, keys[1:]):
        if v <= p1:
            k = (v - p0) / (p1 - p0)
            return np.array([lerp(a, b, k) for a, b in zip(c0, c1)], float)
    return np.array(keys[-1][1], float)


def shade(c, f):
    return tuple(int(clamp(v * f, 0, 255)) for v in c)


def vnoise(h, w, cell, seed, octaves=3):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(2, cell // (2 ** o))
        gh, gw = h // c + 2, w // c + 2
        g = (rng.random((gh, gw)) * 255).astype(np.uint8)
        a = np.asarray(Image.fromarray(g).resize((gw * c, gh * c), Image.BICUBIC), np.float32)[:h, :w] / 255
        out += a * amp
        tot += amp
        amp *= 0.5
    return out / tot


# ================================================================ céu
SKY_TOP = [(0, (74, 142, 222)), (0.5, (96, 140, 214)), (1, (64, 54, 128)), (1.5, (26, 26, 70)), (2, (8, 10, 30))]
SKY_MID = [(0, (118, 184, 236)), (0.5, (200, 180, 176)), (1, (214, 104, 120)), (1.5, (70, 56, 120)), (2, (18, 22, 58))]
SKY_BOT = [(0, (200, 232, 244)), (0.5, (255, 206, 140)), (1, (255, 170, 96)), (1.5, (140, 90, 120)), (2, (40, 42, 92))]
TINT = [(0, (1, 1, 1)), (0.5, (1.04, 0.93, 0.80)), (1, (0.95, 0.68, 0.62)), (1.5, (0.48, 0.43, 0.65)), (2, (0.27, 0.30, 0.56))]
CLOUD_HI = [(0, (255, 255, 255)), (0.5, (255, 240, 222)), (1, (255, 196, 180)), (1.5, (104, 84, 136)), (2, (40, 44, 84))]
CLOUD = [(0, (238, 244, 252)), (0.5, (250, 220, 204)), (1, (240, 160, 160)), (1.5, (84, 66, 116)), (2, (32, 36, 72))]
CLOUD_SH = [(0, (198, 214, 236)), (0.5, (226, 180, 176)), (1, (196, 108, 132)), (1.5, (58, 46, 92)), (2, (24, 28, 58))]
SKYH, NB = 262, 30
SKY_Y = yy[:SKYH]
SKY_X = xx[:SKYH]

_r = random.Random(11)
STARS = [(_r.randrange(W), _r.randrange(4, 210), _r.random() * 6.28, _r.random()) for _ in range(190)]
CLOUDS = []
for cx, cy, n, s in [(40, 82, 7, 1.0), (190, 46, 8, 1.15), (300, 116, 6, 0.9), (120, 148, 5, 0.8)]:
    blobs = [(cx + _r.uniform(-22, 22) * s, cy + _r.uniform(-5, 4) * s, _r.uniform(8, 14) * s) for _ in range(n)]
    CLOUDS.append((blobs, cy + 10 * s))


def sky(td, t):
    top, mid, bot = [keyinterp(K, td) for K in (SKY_TOP, SKY_MID, SKY_BOT)]
    p = np.clip(yy / SKYH, 0, 1) * NB
    band = np.floor(p + (BAY - 0.5) * 0.9)
    q = np.clip(band / NB, 0, 1)[..., None]
    c = np.where(q < 0.5, top + (mid - top) * (q / 0.5), mid + (bot - mid) * ((q - 0.5) / 0.5))
    nf = clamp((td - 1.2) / 0.6)
    if nf > 0:
        for sx, sy, ph, sz in STARS:
            tw = 0.5 + 0.5 * math.sin(t * (1.5 + sz * 2) + ph)
            v = np.array([255, 250, 230]) * nf * (0.45 + 0.55 * tw) * (0.6 + 0.4 * sz)
            c[sy, sx] = np.maximum(c[sy, sx], v)
            if sz > 0.86:
                for d_ in (1, 2):
                    a = 0.6 if d_ == 1 else 0.25
                    for dx, dy in ((d_, 0), (-d_, 0), (0, d_), (0, -d_)):
                        X, Y = (sx + dx) % W, sy + dy
                        c[Y, X] = np.maximum(c[Y, X], v * a)
    if td < 1.3:
        sp = [(0, (276, 66)), (0.55, (264, 140)), (1.0, (252, 200)), (1.3, (244, 246))]
        scx, scy = keyinterp(sp, td)
        scol = keyinterp([(0, (255, 244, 186)), (0.55, (255, 216, 120)), (1, (255, 140, 80)), (1.3, (240, 100, 70))], td)
        r = 15
        d2 = (xx - scx) ** 2 + (yy - scy) ** 2
        for rr, a in ((r + 10, 0.18), (r + 5, 0.32)):
            m = (d2 <= rr * rr) & (BAY > 0.45) & (yy < SKYH)
            c[m] = c[m] * (1 - a) + scol * a
        c[d2 <= r * r] = scol
        c[(d2 <= (r - 4) ** 2) & ((xx - scx) + (yy - scy) < -4)] = np.minimum(scol * 1.06 + 12, 255)
    mf = clamp((td - 1.3) / 0.5)
    if mf > 0:
        mx, my, r = 76, 68, 12
        d1 = (xx - mx) ** 2 + (yy - my) ** 2 <= r * r
        d2 = (xx - mx - 6) ** 2 + (yy - my + 4) ** 2 <= (r - 2) ** 2
        m = d1 & ~d2
        mc = np.array([238, 232, 204])
        c[m] = c[m] * (1 - mf) + mc * mf
        for cx_, cy_ in ((70, 72), (73, 63), (68, 78)):
            if m[cy_, cx_]:
                c[cy_, cx_] = c[cy_, cx_] * (1 - mf) + np.array([206, 198, 172]) * mf
    ch, cm, cs = keyinterp(CLOUD_HI, td), keyinterp(CLOUD, td), keyinterp(CLOUD_SH, td)
    ca = 1.0 if td < 1.5 else lerp(1.0, 0.65, clamp((td - 1.5) / 0.5))
    for k, (blobs, base) in enumerate(CLOUDS):
        off = (t * (2.4 + 0.8 * k)) % (W + 80)
        m = np.zeros((SKYH, W), bool)
        hi = np.zeros((SKYH, W), bool)
        for bx, by, br in blobs:
            x0 = (bx + off + 40) % (W + 80) - 40
            dd = (SKY_X - x0) ** 2 + ((SKY_Y - by) * 1.5) ** 2
            m |= dd <= br * br
            hi |= ((SKY_X - x0 + br * 0.3) ** 2 + ((SKY_Y - by + br * 0.35) * 1.5) ** 2) <= (br * 0.62) ** 2
        m &= SKY_Y <= base
        low = m & (SKY_Y >= base - 4)
        cc = c[:SKYH]
        body = m & ~low
        cc[body] = cc[body] * (1 - ca) + cm * ca
        cc[low] = cc[low] * (1 - ca) + cs * ca
        h2 = hi & body
        cc[h2] = cc[h2] * (1 - ca) + ch * ca
    return c


def birds(c, t):
    for k, (st, by) in enumerate([(0.0, 104), (0.3, 92), (0.55, 116)]):
        x = int(-12 + 32 * (t + 1.5 - st) + k * 14)
        y = int(by + 4 * math.sin(t * 3 + k))
        up = int(t * 8 + k) % 2 == 0
        pts = ([(0, 0), (-1, -1), (1, -1), (-2, -2), (2, -2), (-3, -2), (3, -2)] if up else
               [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (-3, 1), (3, 1)])
        for dx, dy in pts:
            if 0 <= x + dx < W and 0 <= y + dy < H:
                c[y + dy, x + dx] = (40, 48, 70)


# ================================================================ terreno estático
land = np.zeros((H, W, 3), np.float32)
lmask = np.zeros((H, W), bool)


def put(x, y, col):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        land[y, x] = col
        lmask[y, x] = True


def darken_ellipse(cx, cy, rx, ry, f=0.72):
    m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    m &= ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 0.75 + BAY * 0.5
    land[m] *= f


def mpd(n, rough, seed, y0, amp):
    rng = random.Random(seed)
    size = 1 << math.ceil(math.log2(n - 1))
    arr = [0.0] * (size + 1)
    arr[0], arr[size] = rng.uniform(-1, 1) * amp, rng.uniform(-1, 1) * amp
    step, a = size, amp
    while step > 1:
        half = step // 2
        for i in range(half, size, step):
            arr[i] = (arr[i - half] + arr[i + half]) / 2 + rng.uniform(-a, a)
        a *= rough
        step = half
    return np.round(np.array(arr[:n]) + y0).astype(int)


def mountain_layer(top, base_y, lit, mid, dark, snow=None, snowline=0, seed=0):
    nz = vnoise(H, W, 10, seed, 2)
    for x in range(W):
        slope = top[min(x + 3, W - 1)] - top[max(x - 3, 0)]
        for y in range(top[x], base_y):
            depth = y - top[x]
            if slope > 2:
                col = dark
            elif slope < -2:
                col = lit
            else:
                col = mid
            if depth > 26 + nz[y, x] * 20:
                col = mid if BAY[y, x] < 0.5 + (depth - 40) / 60 else col
            if snow and top[x] < snowline and depth < 7 + nz[y, x] * 8 + (snowline - top[x]) * 0.25:
                col = snow[1] if slope > 2 else snow[0]
            put(x, y, col)
        put(x, top[x], shade(lit if slope <= 2 else mid, 1.05))




def peak_range(peaks, base_y, seed, lit, mid, dark, snow=None, snowline=0, specks=None):
    rng = random.Random(seed)
    jit = np.array([rng.choice([0, 0, 0, 1, -1]) for _ in range(W)])
    jit = np.round(np.convolve(jit, [0.3, 0.4, 0.3], mode='same') * 2).astype(int)
    tops = np.full(W, 10 ** 6, float)
    own = np.zeros(W, int)
    for k, (ax, ay, sl, sr) in enumerate(peaks):
        y_ = ay + np.where(xx[0] < ax, (ax - xx[0]) * sl, (xx[0] - ax) * sr)
        better = y_ < tops
        tops[better] = y_[better]
        own[better] = k
    tops = np.round(tops).astype(int) + jit
    nz = vnoise(H, W, 6, seed + 50, 2)
    for x in range(W):
        ax, ay, sl, sr = peaks[own[x]]
        left = x < ax
        for y in range(tops[x], base_y):
            depth = y - tops[x]
            col = lit if left else dark
            # vincos diagonais
            u = (y - ay) - abs(x - ax) * 0.35
            if depth > 30 + nz[y, x] * 18 and BAY[y, x] < (depth - 30) / 40:
                col = mid
            if snow and ay < snowline:
                sd = (snowline - ay) * 0.75 - abs(x - ax) * 0.25 + (nz[y, x] - 0.5) * 8
                if y - ay < sd:
                    col = snow[0] if left else snow[1]
            put(x, y, col)
    if specks:
        for _ in range(specks):
            x = rng.randrange(W)
            y = tops[x] + rng.randint(4, 40)
            if y < base_y - 1:
                put(x, y, shade(mid, 0.82)); put(x, y - 1, shade(mid, 0.9))
    return tops


peak_range([(18, 168, 0.8, 0.9), (72, 146, 0.75, 0.85), (124, 176, 0.9, 0.8), (168, 128, 0.8, 0.95),
            (220, 166, 0.85, 0.8), (266, 140, 0.8, 0.9), (314, 170, 0.9, 0.8), (356, 150, 0.8, 0.8)],
           262, 1, (154, 172, 214), (126, 146, 192), (104, 122, 172),
           snow=((244, 248, 254), (198, 208, 234)), snowline=186)
peak_range([(0, 218, 0.5, 0.5), (58, 204, 0.45, 0.55), (112, 222, 0.5, 0.5), (172, 200, 0.5, 0.45),
            (234, 216, 0.5, 0.55), (292, 198, 0.45, 0.5), (350, 212, 0.5, 0.5)],
           262, 2, (106, 148, 126), (88, 130, 112), (72, 108, 98), specks=420)

for y in range(254, 278):
    for x in range(W):
        put(x, y, (26, 66, 54))


def pine(cx, base, h, pal):
    dark, mid, light, outl = pal
    tiers = 3 if h < 26 else 4
    th = h / tiers
    for r_ in range(h):
        y = base - h + r_
        within = (r_ % th) / th
        hw = int(round((r_ / h) * h * 0.3 * (0.5 + 0.5 * within) + 0.6))
        for dx in range(-hw, hw + 1):
            if dx >= hw - (1 if within > 0.7 else 0):
                col = outl
            elif dx < -hw * 0.35:
                col = light
            elif dx > hw * 0.35:
                col = dark
            else:
                col = mid
            if within > 0.85 and abs(dx) == hw:
                col = outl
            put(cx + dx, y, col)
    for y in range(base, base + 3):
        put(cx, y, (66, 48, 36)); put(cx + 1, y, (52, 38, 30))


_r = random.Random(5)
for x0 in range(-6, W + 8, 7):
    pine(x0 + _r.randint(-2, 2), 262 + _r.randint(0, 4), _r.randint(18, 26),
         ((22, 58, 52), (30, 76, 62), (42, 94, 74), (16, 42, 40)))
for x0 in range(0, W + 8, 10):
    if 252 <= x0 <= 298:   # clareira atrás da ponte
        continue
    pine(x0 + 3 + _r.randint(-2, 2), 277, _r.randint(22, 32), ((28, 74, 56), (38, 96, 68), (58, 124, 82), (20, 52, 44)))
for x in range(254, 298):   # mato baixo na clareira
    put(x, 276, (34, 84, 60)); put(x, 275, (34, 84, 60) if x % 3 else (46, 104, 70))

# rio
_rv = vnoise(H, W, 8, 21, 2)
for y in range(276, 296):
    for x in range(W):
        t_ = (y - 276) / 19
        if y <= 277:
            col = (36, 82, 92)
        else:
            col = (82, 150, 212) if t_ + (_rv[y, x] - 0.5) * 0.3 < 0.35 else (
                (66, 128, 196) if t_ + (BAY[y, x] - 0.5) * 0.25 < 0.7 else (52, 104, 168))
        put(x, y, col)
_r = random.Random(17)
for x in range(W):   # reflexo das árvores
    if _r.random() < 0.55:
        for k in range(_r.randint(1, 4)):
            put(x, 278 + k, (40, 92, 104))
for x in range(0, W, 1):
    if _r.random() < 0.5:
        put(x, 279, (130, 186, 228))
for y, col in ((296, (60, 106, 56)), (297, (72, 122, 62)), (298, (86, 140, 70))):
    for x in range(W):
        put(x, y, col)

# campo
gn = vnoise(H, W, 36, 4, 3)
lvl = np.clip(np.floor(gn * 3.2 + (BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
GREENS = np.array([(104, 164, 74), (116, 176, 84), (130, 190, 94)], np.float32)
mfield = yy >= 299
land[mfield] = GREENS[lvl[mfield]]
lmask[mfield] = True
_r = random.Random(3)
for _ in range(2600):
    x, y = _r.randrange(W), _r.randrange(301, H)
    c0 = (88, 144, 64) if _r.random() < 0.7 else (78, 132, 58)
    put(x, y, c0); put(x + 1, y - 1, c0); put(x + 2, y, c0); put(x + 3, y - 1, c0) if _r.random() < 0.4 else None
for _ in range(1200):
    x, y = _r.randrange(W), _r.randrange(300, H)
    put(x, y, (150, 206, 104))
    if _r.random() < 0.3:
        put(x, y - 1, (166, 218, 116))
FLOWER = [(255, 230, 120), (240, 124, 150), (250, 250, 250), (190, 150, 250), (255, 168, 90)]
for _ in range(170):
    x, y = _r.randrange(W), _r.randrange(304, H)
    c0 = _r.choice(FLOWER)
    put(x, y + 1, (70, 130, 60))
    put(x, y, c0); put(x - 1, y, shade(c0, 0.85)); put(x + 1, y, shade(c0, 0.85)); put(x, y - 1, shade(c0, 0.9))
    put(x, y, (255, 240, 170) if c0 != (255, 230, 120) else (255, 255, 230))

# reeds na margem
for _ in range(90):
    x = _r.randrange(W)
    if 252 <= x <= 300:
        continue
    hgt = _r.randint(3, 7)
    for k in range(hgt):
        put(x, 299 - k, (70, 128, 58) if k < hgt - 1 else (150, 118, 66))

# caminhos
pm = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(pm)
d.polygon([(156, 640), (204, 640), (190, 396), (170, 396)], fill=255)
d.polygon([(-2, 378), (-2, 396), (176, 394), (176, 378)], fill=255)
d.polygon([(172, 382), (190, 392), (284, 298), (266, 298)], fill=255)
d.ellipse((126, 408, 234, 448), fill=255)
d.ellipse((158, 368, 202, 398), fill=255)
pmask = (np.array(pm) > 0) & (yy >= 299)
er = pmask.copy()
for _ in range(2):
    e2 = er.copy()
    e2[1:, :] &= er[:-1, :]; e2[:-1, :] &= er[1:, :]; e2[:, 1:] &= er[:, :-1]; e2[:, :-1] &= er[:, 1:]
    er = e2
dn = vnoise(H, W, 14, 31, 3)
DIRT = np.array([(194, 160, 110), (206, 172, 120), (218, 186, 134)], np.float32)
dl = np.clip(np.floor(dn * 3.3 + (BAY - 0.5) * 0.9 - 0.15), 0, 2).astype(int)
land[pmask] = DIRT[dl[pmask]]
rim = pmask & ~er
land[rim] = (170, 136, 92)
# grama invadindo a borda
for y, x in np.argwhere(rim):
    if _r.random() < 0.28:
        land[y, x] = (104, 164, 74)
        if _r.random() < 0.5 and y - 1 >= 0:
            land[y - 1, x] = (116, 176, 84) if pmask[y - 1, x] else land[y - 1, x]
pts = np.argwhere(er)
for i in _r.sample(range(len(pts)), 420):
    y, x = pts[i]
    land[y, x] = (172, 140, 98)
    if x + 1 < W and er[y, x + 1]:
        land[y, x + 1] = (232, 206, 156)
# terra batida e marcas na praça
pl = ((xx - 180) / 50) ** 2 + ((yy - 428) / 18) ** 2
ring = (pl < 0.55) & (pl > 0.25) & (BAY > 0.55)
land[ring & pmask] = (190, 154, 104)

# ponte
for y in range(270, 300):
    for x in range(264, 288):
        row = (y - 270) // 3
        col = (164, 112, 68) if row % 2 == 0 else (146, 98, 58)
        if (y - 270) % 3 == 2:
            col = (104, 66, 38)
        if x in (264, 287):
            col = (96, 60, 34)
        put(x, y, col)
    if (y - 270) % 3 == 0:
        put(266, y, (196, 150, 98)); put(277, y, (190, 144, 92))
for x in (262, 289):
    for y in range(262, 300):
        put(x, y, (110, 72, 40)); put(x + (1 if x == 262 else -1), y, (86, 56, 32))
    for y in (262, 263):
        put(x, y, (138, 96, 58))
for y in (266, 267):
    for x in range(262, 290):
        if x in (262, 263, 288, 289) or y == 266:
            pass
for x in range(262, 290):
    put(x, 266 + (0 if x < 276 else 0), (126, 84, 48))

# fundo do mapa: cerca à esquerda
for x in range(4, 132, 14):
    for y in range(362, 377):
        put(x, y, (124, 86, 50)); put(x + 1, y, (146, 104, 62)); put(x + 2, y, (100, 68, 40))
    put(x, 361, (170, 128, 80)); put(x + 1, 361, (186, 144, 92)); put(x + 2, 361, (150, 108, 66))
    if x + 14 < 132:
        for k in range(3, 14):
            put(x + k, 365, (156, 112, 66)); put(x + k, 366, (120, 82, 48))
            put(x + k, 371, (156, 112, 66)); put(x + k, 372, (120, 82, 48))

# placas (sem letra)
for y in range(342, 388):
    put(178, y, (150, 104, 60)); put(179, y, (132, 90, 52)); put(180, y, (112, 76, 44)); put(181, y, (92, 62, 36))
put(179, 341, (170, 124, 76)); put(180, 341, (150, 104, 60))


def board(x0, y0, w, h, tip):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            edge = y in (y0, y0 + h - 1) or x in (x0, x0 + w - 1)
            col = (96, 60, 30) if edge else ((210, 162, 98) if (y - y0) < h // 2 else (192, 144, 84))
            put(x, y, col)
    for x in range(x0 + 2, x0 + w - 2):
        if (x * 7) % 5 < 3:
            put(x, y0 + 3, (176, 128, 74))
        if (x * 3) % 7 < 3:
            put(x, y0 + h - 4, (166, 118, 66))
    for y in (y0 + 2, y0 + h - 3):
        put(x0 + 2 if tip > 0 else x0 + w - 3, y, (70, 50, 40))
    tx = x0 - 1 if tip < 0 else x0 + w
    for k in range(h // 2):
        for y in range(y0 + k + 1, y0 + h - k - 1):
            edge = y in (y0 + k + 1, y0 + h - k - 2)
            put(tx + tip * k, y, (96, 60, 30) if edge else (204, 156, 94))


board(150, 346, 28, 13, -1)
board(182, 362, 28, 13, 1)

# fogueira: pedras e lenha
darken_ellipse(180, 426, 16, 6, 0.8)
for y in range(422, 430):
    for x in range(170, 191):
        if ((x - 180) / 9) ** 2 + ((y - 426) / 3.4) ** 2 <= 1:
            put(x, y, (66, 54, 50) if BAY[y, x] > 0.4 else (82, 66, 58))
for k in range(12):
    a = 2 * math.pi * k / 12
    sx, sy = 180 + 12 * math.cos(a), 426 + 4.8 * math.sin(a)
    for dx in range(-2, 2):
        for dy in range(-1, 2):
            col = (150, 148, 160) if dy < 0 and dx < 0 else ((124, 122, 134) if dy <= 0 else (94, 92, 104))
            put(sx + dx, sy + dy, col)
for x, y, c_ in [(172, 425, 1), (188, 425, -1)]:
    for k in range(10):
        X = x + c_ * k
        Y = y - (k // 4)
        put(X, Y, (120, 78, 44)); put(X, Y + 1, (92, 58, 32))
    put(x, y, (214, 172, 112)); put(x, y + 1, (186, 144, 92))

# mastro
for y in range(316, 377):
    put(152, y, (212, 212, 222)); put(153, y, (170, 170, 184))
for dx, dy, c_ in [(0, -2, (255, 220, 110)), (1, -2, (230, 180, 70)), (-1, -1, (230, 180, 70)), (0, -1, (255, 210, 90)),
                   (1, -1, (206, 156, 60)), (2, -1, (206, 156, 60))]:
    put(152 + dx, 316 + dy, c_)


# ---- decoração
def oak(cx, base, R, seed):
    rr = random.Random(seed)
    darken_ellipse(cx + R * 0.2, base + 1, R * 1.15, R * 0.32, 0.7)
    th = int(R * 0.9)
    for y in range(base - th, base + 1):
        for k, col in enumerate([(84, 56, 34), (112, 76, 46), (128, 88, 54), (104, 70, 42), (78, 52, 32)]):
            put(cx - 2 + k, y, col)
        if rr.random() < 0.25:
            put(cx - 1 + rr.randint(0, 2), y, (70, 46, 28))
    for dx in (-4, -3, 3, 4):
        put(cx + dx, base, (90, 60, 36))
    cy = base - th - R * 0.55
    blobs = [(cx, cy, R * 0.75)]
    for k in range(9):
        a = rr.uniform(0, 2 * math.pi)
        dist = rr.uniform(0.3, 0.75) * R
        blobs.append((cx + math.cos(a) * dist, cy + math.sin(a) * dist * 0.75, rr.uniform(0.35, 0.55) * R))
    m = np.zeros((H, W), bool)
    owner = np.full((H, W), -1)
    for bi, (bx, by, br) in enumerate(blobs):
        mm = (xx - bx) ** 2 + (yy - by) ** 2 <= br * br
        owner[mm] = bi
        m |= mm
    rim_ = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    for y, x in np.argwhere(m):
        bx, by, br = blobs[owner[y, x]]
        v = ((x - bx) + (y - by) * 1.2) / br + (cy - by) / R * 0.0
        g = (y - cy) / R
        v = v * 0.7 + g * 0.6 + (BAY[y, x] - 0.5) * 0.35
        if rim_[y, x]:
            col = (30, 66, 46)
        elif v < -0.55:
            col = (132, 198, 96)
        elif v < -0.1:
            col = (96, 168, 78)
        elif v < 0.45:
            col = (66, 136, 66)
        else:
            col = (46, 102, 58)
        put(x, y, col)
    for _ in range(int(R * 3)):
        a = rr.uniform(0, 2 * math.pi)
        dist = rr.uniform(0, 0.8) * R
        x, y = int(cx + math.cos(a) * dist), int(cy + math.sin(a) * dist * 0.75)
        if m[y, x] and not rim_[y, x]:
            put(x, y, (150, 210, 110) if y < cy else (40, 92, 54))


def bush(cx, cy, w, seed):
    rr = random.Random(seed)
    darken_ellipse(cx + 1, cy + 1, w + 2, 3, 0.75)
    for bx, by, br in [(cx - w * 0.45, cy - 3, w * 0.55), (cx + w * 0.4, cy - 3, w * 0.55), (cx, cy - 5, w * 0.6)]:
        for y in range(int(by - br), int(by + br) + 1):
            for x in range(int(bx - br), int(bx + br) + 1):
                if (x - bx) ** 2 + ((y - by) * 1.3) ** 2 <= br * br and y <= cy:
                    v = (x - bx) + (y - by) * 1.3
                    put(x, y, (108, 178, 84) if v < -br * 0.3 else ((78, 146, 68) if v < br * 0.3 else (56, 112, 56)))
    for _ in range(3):
        x, y = cx + rr.randint(-w + 2, w - 2), cy - rr.randint(2, 7)
        put(x, y, rr.choice([(240, 90, 110), (255, 230, 120), (250, 250, 250)]))


def rock(cx, cy, w, h):
    darken_ellipse(cx + 1, cy, w + 2, 2.5, 0.72)
    for y in range(cy - h, cy + 1):
        for x in range(cx - w, cx + w + 1):
            if ((x - cx) / (w + 0.5)) ** 2 + ((y - cy + h * 0.4) / (h * 0.75 + 0.5)) ** 2 <= 1:
                v = (x - cx) / w + (y - (cy - h)) / h
                put(x, y, (186, 184, 196) if v < 0.4 else ((146, 144, 158) if v < 1.1 else (110, 108, 122)))
    for x in range(cx - w + 1, cx):
        put(x, cy - h, (110, 160, 80))


def stump(cx, cy):
    darken_ellipse(cx + 1, cy + 1, 7, 2.5, 0.75)
    for y in range(cy - 4, cy + 1):
        for x in range(cx - 4, cx + 5):
            put(x, y, (128, 86, 52) if x < cx + 2 else (100, 66, 40))
    for x in range(cx - 4, cx + 5):
        put(x, cy - 5, (216, 182, 128)); put(x, cy - 6, (200, 164, 110) if abs(x - cx) < 4 else (128, 86, 52))
    put(cx, cy - 5, (176, 136, 90)); put(cx + 1, cy - 6, (176, 136, 90))


def logs(cx, cy):
    darken_ellipse(cx, cy + 1, 14, 3, 0.75)
    for k, n in enumerate((3, 2, 1)):
        for j in range(n):
            lx = cx - (n - 1) * 3.5 + j * 7
            ly = cy - 3 - k * 6
            for y in range(int(ly) - 4, int(ly) + 5):
                for x in range(int(lx) - 4, int(lx) + 5):
                    d = math.hypot(x - lx, y - ly)
                    if d <= 3.6:
                        col = (88, 56, 32) if d > 2.7 else ((214, 176, 120) if d > 1.6 or d < 0.8 else (180, 140, 92))
                        if d <= 2.7 and x - lx + y - ly > 2:
                            col = shade(col, 0.88)
                        put(x, y, col)


oak(20, 428, 18, 1)
oak(340, 412, 16, 2)
oak(28, 600, 28, 3)
oak(334, 590, 30, 4)
oak(322, 336, 14, 5)
for b in [(72, 432, 10, 1), (300, 460, 12, 2), (248, 526, 10, 3), (116, 500, 8, 4), (60, 482, 8, 5), (226, 324, 8, 6),
          (100, 340, 7, 7)]:
    bush(*b)
rock(264, 428, 6, 6); rock(88, 536, 4, 4); rock(216, 572, 6, 5); rock(40, 320, 4, 3); rock(318, 380, 3, 3)
stump(240, 472); stump(104, 456)
logs(132, 456)

LAND = land.copy()
LMASK = lmask.copy()

# ================================================================ moradores
SKINS = [(246, 208, 172), (184, 128, 90), (226, 174, 132), (132, 90, 62), (100, 66, 48), (214, 160, 120)]
HAIRS = [(46, 34, 30), (212, 160, 76), (98, 60, 36), (162, 66, 44), (28, 28, 40), (232, 232, 232), (70, 46, 34)]
TUNICS = [(204, 72, 72), (70, 122, 206), (232, 182, 62), (92, 164, 92), (164, 92, 174), (232, 132, 62),
          (72, 174, 172), (226, 226, 236)]
PANTS = [(84, 66, 58), (62, 62, 96), (112, 92, 62), (70, 84, 70)]
OUT = (34, 26, 32)


def make_sprite(i, frame):
    SW, SH = 16, 30
    a = np.zeros((SH, SW, 4), np.float32)

    def px(x, y, c):
        if 0 <= x < SW and 0 <= y < SH:
            a[y, x, :3] = c
            a[y, x, 3] = 1

    skin = SKINS[(i * 2 + 1) % len(SKINS)]
    hair = HAIRS[i % len(HAIRS)]
    tun = TUNICS[(i * 3) % len(TUNICS)]
    pants = PANTS[i % len(PANTS)]
    style = i % 5
    apron = i % 4 == 2
    oy = 3
    # cabeça (x 3..12, y oy+1..oy+9)
    for y in range(oy + 1, oy + 10):
        for x in range(3, 13):
            if (y in (oy + 1, oy + 9)) and x in (3, 12):
                continue
            c = skin
            if x >= 11 or y == oy + 9:
                c = shade(skin, 0.84)
            px(x, y, c)
    for ex in (5, 10):
        px(ex, oy + 5, (36, 26, 30)); px(ex, oy + 6, (36, 26, 30))
    px(4, oy + 7, shade(skin, 0.9) if skin[0] < 150 else (236, 150, 140))
    px(11, oy + 7, shade(skin, 0.8) if skin[0] < 150 else (220, 140, 132))
    px(7, oy + 8, shade(skin, 0.72)); px(8, oy + 8, shade(skin, 0.72))
    hh, hs = shade(hair, 1.25), shade(hair, 0.78)
    if style == 3:   # cabelo volumoso
        for y in range(oy - 2, oy + 6):
            for x in range(1, 15):
                if ((x - 7.5) / 7) ** 2 + ((y - oy - 2) / 4.5) ** 2 <= 1 and not (y >= oy + 3 and 4 <= x <= 11):
                    px(x, y, hh if (x + y) % 3 == 0 and x < 8 else (hs if x > 10 else hair))
    else:
        for y in range(oy, oy + 4):
            for x in range(3, 13):
                if y == oy and x in (3, 12):
                    continue
                px(x, y, hh if (x < 7 and y <= oy + 1) else (hs if x >= 11 else hair))
        for x in (3, 4, 11, 12):
            px(x, oy + 4, hair if x < 11 else hs)
        px(5, oy + 4, hair); px(6, oy + 3, hair)
        if style == 1:   # comprido
            for y in range(oy + 4, oy + 14):
                px(2, y, hair); px(3, y, hair if y < oy + 10 else hs)
                px(12, y, hs); px(13, y, hs)
        if style == 2:   # coque
            for y in range(oy - 3, oy):
                for x in range(6, 10):
                    if not (y == oy - 3 and x in (6, 9)):
                        px(x, y, hh if x < 8 else hair)
        if style == 4:   # chapéu de palha
            straw, straw_s = (220, 186, 104), (180, 146, 74)
            for x in range(0, 16):
                px(x, oy + 2, straw if x < 12 else straw_s)
            for y in range(oy - 2, oy + 2):
                for x in range(4, 12):
                    px(x, y, straw if x < 10 else straw_s)
            for x in range(4, 12):
                px(x, oy + 1, (170, 60, 50))
    # corpo
    tsh, thi = shade(tun, 0.74), shade(tun, 1.14)
    for y in range(oy + 10, oy + 19):
        for x in range(4, 12):
            c = tun if x < 10 else tsh
            if x == 4 and y < oy + 16:
                c = thi
            px(x, y, c)
    px(7, oy + 10, skin); px(8, oy + 10, skin); px(7, oy + 11, shade(skin, 0.84))
    if apron:
        for y in range(oy + 13, oy + 20):
            for x in range(5, 11):
                px(x, y, (238, 228, 204) if x < 9 else (206, 196, 172))
        px(5, oy + 12, (238, 228, 204)); px(10, oy + 12, (206, 196, 172))
    else:
        for x in range(4, 12):
            px(x, oy + 16, (96, 64, 40))
        px(7, oy + 16, (230, 190, 80)); px(8, oy + 16, (196, 150, 60))
    # braços
    sw = {0: (0, 0), 1: (-1, 1), 2: (1, -1)}[frame]
    for side, x0, dy in ((0, 2, sw[0]), (1, 12, sw[1])):
        for y in range(oy + 11 + dy, oy + 16 + dy):
            px(x0, y, tun if side == 0 else tsh)
            px(x0 + 1, y, tun if side == 0 else tsh)
        px(x0, oy + 16 + dy, skin); px(x0 + 1, oy + 16 + dy, shade(skin, 0.86))
        px(x0, oy + 17 + dy, shade(skin, 0.9)); px(x0 + 1, oy + 17 + dy, shade(skin, 0.8))
    # pernas e botas
    lift = {0: (0, 0), 1: (1, 0), 2: (0, 1)}[frame]
    boots, bsh = (70, 48, 36), (50, 34, 28)
    for leg, xs in ((0, (5, 6, 7)), (1, (8, 9, 10))):
        up = lift[leg]
        for y in range(oy + 19, oy + 23 - up):
            for x in xs:
                px(x, y, pants if x != xs[-1] else shade(pants, 0.78))
        for y in range(oy + 23 - up, oy + 25 - up):
            for x in (xs[0] - (1 if leg == 0 else 0),) + xs + ((xs[-1] + 1,) if leg == 1 else ()):
                px(x, y, boots if x < xs[-1] else bsh)
    # contorno
    m = a[..., 3] > 0
    ring_ = np.zeros_like(m)
    ring_[1:, :] |= m[:-1, :]; ring_[:-1, :] |= m[1:, :]; ring_[:, 1:] |= m[:, :-1]; ring_[:, :-1] |= m[:, 1:]
    ring_ &= ~m
    a[ring_, :3] = OUT
    a[ring_, 3] = 1
    return a


SPRITES = {}


def sprite(i, frame):
    k = (i, frame)
    if k not in SPRITES:
        SPRITES[k] = make_sprite(i, frame)
    return SPRITES[k]


def blit(img, spr, fx, fy):
    """fx, fy = pés (centro, linha da sola)."""
    h, w = spr.shape[:2]
    rows = np.nonzero(spr[..., 3].any(axis=1))[0]
    bottom = rows.max()
    x0, y0 = int(round(fx)) - w // 2, int(round(fy)) - bottom
    ys, xs = np.nonzero(spr[..., 3] > 0)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
    img[Y[ok], X[ok]] = spr[ys[ok], xs[ok], :3]


def ground_shadow(img, fx, fy):
    m = ((xx - fx) / 7.5) ** 2 + ((yy - fy - 0.5) / 2.2) ** 2 <= 1
    img[m] *= 0.68


def ring_positions(n, cx=180, cy=428):
    pos = []
    inner = min(n, 8)
    for cnt, rx, ry in [(inner, 44, 17), (n - inner, 66, 27)]:
        if cnt <= 0:
            continue
        base = [-90 + 360 * k / cnt for k in range(cnt)]
        best, br = -1, 0
        for rot in range(0, 360, 2):
            angs = [(a_ + rot) % 360 for a_ in base]
            dmin = min(min(abs((a_ - 90 + 180) % 360 - 180) for a_ in angs),
                       min(abs((a_ + 90 + 180) % 360 - 180) for a_ in angs) + 6)
            if dmin > best:
                best, br = dmin, rot
        for a_ in base:
            r = math.radians(a_ + br)
            pos.append((cx + rx * math.cos(r), cy + ry * math.sin(r)))
    return pos


QMARK = [".#####.", "##...##", "##...##", "....##.", "...##..", "...##..", ".......", "...##..", "...##.."]
EMARK = ["..##...", "..##...", "..##...", "..##...", "..##...", ".......", "..##...", "..##..."]


def _glyph(rows):
    g = np.array([[c == '#' for c in r] for r in rows])
    o = np.zeros((g.shape[0] + 2, g.shape[1] + 2), bool)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            o[dy:dy + g.shape[0], dx:dx + g.shape[1]] |= g
    return g, o


GQ, GE = _glyph(QMARK), _glyph(EMARK)


def qmark(img, x, y, bang=False):
    g, o = GE if bang else GQ
    for r_ in range(o.shape[0]):
        for c_ in range(o.shape[1]):
            X, Y = x + c_ - 1, y + r_ - 1
            if o[r_, c_] and 0 <= X < W and 0 <= Y < H:
                inside = 1 <= r_ <= g.shape[0] and 1 <= c_ <= g.shape[1] and g[r_ - 1, c_ - 1]
                img[Y, X] = ((255, 236, 120) if bang else (255, 255, 255)) if inside else (30, 22, 40)


# ================================================================ fogo e luz
FCX, FBASE = 180, 422


def fire(img, t, scale=1.0):
    if scale <= 0:
        return
    r = random.Random(int(t * 12))
    prof = [3, 7, 11, 15, 18, 15, 11, 7, 3]
    for i, dx in enumerate(range(-4, 5)):
        h = int(max(0, (prof[i] + r.randint(-2, 3) + 2.5 * math.sin(t * 9 + i * 1.3))) * scale)
        for k in range(h):
            y = FBASE - k
            rel = k / max(h, 1)
            if rel < 0.35 and abs(dx) <= 2:
                c = (255, 250, 210)
            elif rel < 0.6 and abs(dx) <= 3:
                c = (255, 216, 92)
            elif rel < 0.86:
                c = (255, 150, 50)
            else:
                c = (228, 74, 40)
            img[y, FCX + dx] = c
    for k in range(3):   # línguas soltas
        if r.random() < 0.7 * scale:
            dx = r.randint(-3, 3)
            y = FBASE - int((14 + r.randint(0, 8)) * scale)
            img[y, FCX + dx] = (255, 170, 60)
    for dx in range(-6, 7):   # brasas
        if r.random() < 0.6:
            img[FBASE + 2, FCX + dx] = (255, 120 + r.randint(0, 60), 40)
    if scale > 0.5:
        for k in range(8):
            life = 1.3
            ph = (t + k * 0.17) % life
            sx = FCX + int(math.sin(k * 7 + t * 2.5) * 6 + ph * (k % 3 - 1) * 6)
            sy = FBASE - 10 - int(ph * 46)
            if ph < life * 0.85 and 0 <= sy < H:
                img[sy, sx] = (255, 226, 130) if ph < 0.6 else (255, 150, 70)


def smoke(img, t):
    for k in range(10):
        ph = (t * 0.5 + k / 10) % 1
        y = int(FBASE - 22 - ph * 60)
        x = int(FCX + math.sin(ph * 6 + k) * 4 + ph * 14)
        a = 0.42 * (1 - ph)
        for dx, dy in ((0, 0), (1, 0), (0, -1), (1, -1)) if ph > 0.25 else ((0, 0),):
            img[y + dy, x + dx] = img[y + dy, x + dx] * (1 - a) + np.array((200, 200, 212)) * a


def light_level(t, cx=FCX, cy=FBASE - 6):
    fl = math.sin(t * 13) * 1.6 + math.sin(t * 7.3) * 1.2
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.9) ** 2)
    L = np.clip(1 - d / (94 + fl), 0, 1) ** 0.85
    q = np.floor(L * 6 + BAY * 0.999) / 6
    return np.clip(q, 0, 0.95).astype(np.float32)


MYST = (276, 252)


def _myst():
    d = np.sqrt((xx - MYST[0]) ** 2 + ((yy - MYST[1]) * 1.3) ** 2)
    L = np.clip(1 - d / 20, 0, 1) ** 0.9
    return (np.floor(L * 4 + BAY * 0.999) / 4 * 0.9).astype(np.float32)


MYST_LV = _myst()
