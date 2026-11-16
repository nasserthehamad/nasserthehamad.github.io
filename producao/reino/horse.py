"""Cavalo em pixel art (de lado, virado pra esquerda), 4 quadros de galope, no estilo dos bonecos do folk.py."""
import math
import numpy as np

OUT = (34, 24, 30)
BASE, SHADE, LIGHT = (150, 96, 56), (112, 70, 40), (186, 132, 82)
MANE, HOOF, EYE, MUZZ = (54, 36, 28), (40, 32, 30), (20, 16, 16), (122, 82, 58)
BLANKET, BLANKET2 = (176, 52, 46), (230, 196, 90)

W_, H_ = 36, 26


def _line(m, col, a, x0, y0, x1, y1, w=1.6):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        y = y0 + (y1 - y0) * k / n
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx * dx + dy * dy <= (w / 2) ** 2 * 2:
                    X, Y = int(round(x + dx * 0.5)), int(round(y + dy * 0.5))
                    if 0 <= X < W_ and 0 <= Y < H_:
                        m[Y, X] = True
                        a[Y, X, :3] = col


# pernas: (quadril x, joelho dx, dy; casco dx, dy) por quadro. Dianteiras ~x=12, traseiras ~x=24
LEGS = [
    # 0: esticado (voando)
    [(11, -3, 3, -6, 6), (13, -2, 3, -5, 7), (24, 3, 3, 6, 6), (26, 2, 3, 5, 6)],
    # 1: recolhendo
    [(11, -1, 3, 1, 6), (13, 1, 3, 3, 6), (24, -1, 3, -2, 6), (26, 1, 3, 0, 7)],
    # 2: juntas embaixo
    [(11, 2, 3, 3, 6), (13, 3, 2, 5, 5), (24, -3, 3, -5, 6), (26, -2, 3, -4, 6)],
    # 3: empurrando
    [(11, 0, 3, -2, 7), (13, -1, 3, -4, 6), (24, 1, 3, 3, 7), (26, -1, 3, -1, 7)],
]


def make_horse(frame=0, blanket=True):
    a = np.zeros((H_, W_, 4), np.float32)
    m = np.zeros((H_, W_), bool)
    yy, xx = np.mgrid[0:H_, 0:W_]
    bob = [0, 1, 1, 0][frame % 4]
    by = 12 + bob
    body = ((xx - 18.5) / 9.5) ** 2 + ((yy - by) / 4.6) ** 2 <= 1
    neck = np.zeros_like(body)
    for k in range(0, 9):                         # pescoço subindo pra esquerda
        cx, cy = 10.5 - k * 0.6, by - 2 - k * 0.9
        neck |= ((xx - cx) / 2.6) ** 2 + ((yy - cy) / 2.6) ** 2 <= 1
    hy = by - 9
    head = ((xx - 4.5) / 3.6) ** 2 + ((yy - hy) / 2.3) ** 2 <= 1
    snout = ((xx - 2.0) / 2.2) ** 2 + ((yy - (hy + 1.2)) / 1.8) ** 2 <= 1
    ears = ((xx == 7) & (yy == hy - 3)) | ((xx == 8) & (yy == hy - 3)) | ((xx == 7) & (yy == hy - 2))
    shape = body | neck | head | snout | ears
    a[shape, :3] = BASE
    # sombra embaixo da barriga, luz em cima
    a[shape & (yy >= by + 2), :3] = SHADE
    a[(body | neck) & (yy <= by - 3) & (xx > 12), :3] = LIGHT
    a[snout & (xx <= 1), :3] = MUZZ
    m |= shape
    # crina
    for k in range(0, 9):
        X, Y = int(round(11.5 - k * 0.6)), int(round(by - 4 - k * 0.9))
        for dx in (0, 1):
            if 0 <= X + dx < W_ and 0 <= Y < H_:
                a[Y, X + dx, :3] = MANE; m[Y, X + dx] = True
    # rabo (balança com o galope)
    sw = [2, 0, -1, 1][frame % 4]
    for k in range(8):
        X, Y = 27 + k * 0.8, by - 2 + k * 0.7 + sw * (k / 8) ** 2 * 2
        for dy in (0, 1):
            Xi, Yi = int(round(X)), int(round(Y)) + dy
            if 0 <= Xi < W_ and 0 <= Yi < H_:
                a[Yi, Xi, :3] = MANE; m[Yi, Xi] = True
    # pernas
    for j, (hx, kx, ky, fx, fy) in enumerate(LEGS[frame % 4]):
        col = SHADE if j in (1, 3) else BASE        # as de trás (do outro lado) mais escuras
        y0 = by + 3
        _line(m, col, a, hx, y0, hx + kx, y0 + ky, 1.8)
        _line(m, col, a, hx + kx, y0 + ky, hx + fx, y0 + fy, 1.6)
        X, Y = int(round(hx + fx)), int(round(y0 + fy))
        if 0 <= Y < H_:
            for dx in (0, 1):
                if 0 <= X + dx < W_:
                    a[Y, X + dx, :3] = HOOF; m[Y, X + dx] = True
    # olho e manta
    a[int(hy) - 1, 5, :3] = EYE
    if blanket:
        bl = (xx >= 15) & (xx <= 22) & (yy >= by - 5) & (yy <= by + 1) & body
        a[bl, :3] = BLANKET
        a[bl & ((yy == by + 1) | (xx == 15) | (xx == 22)), :3] = BLANKET2
    a[m, 3] = 1
    # contorno
    ring = np.zeros_like(m)
    ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    a[ring, :3] = OUT
    a[ring, 3] = 1
    return a


_cache = {}


def horse(frame=0):
    if frame not in _cache:
        _cache[frame] = make_horse(frame)
    return _cache[frame]


def rider_on_horse(rider, frame):
    """Monta o cavaleiro (sprite do folk.py, de frente) em cima do cavalo. Devolve sprite RGBA com os pés do cavalo na
    última linha."""
    h = horse(frame)
    rows = np.nonzero(rider[..., 3].any(axis=1))[0]
    top = rows.min()
    cut = top + 23                                # cabeça + tronco até o cinto
    r = rider[top:cut]
    bob = [0, 1, 1, 0][frame % 4]
    Hh, Wh = h.shape[:2]
    Hr, Wr = r.shape[:2]
    oy = Hr - 9                                   # o cinto encosta na manta
    out = np.zeros((Hh + oy, max(Wh, Wr + 6), 4), np.float32)
    out[oy:oy + Hh, :Wh] = h
    x0 = 19 - Wr // 2
    y0 = bob + 1
    reg = out[y0:y0 + Hr, x0:x0 + Wr]
    mk = r[..., 3] > 0.5
    reg[mk] = r[mk]
    return out
