"""Bandeiras em pixel art, desenhadas num quadrado 22x22 pensado pra virar bolinha (recorte redondo)."""
import math
import numpy as np

N = 22
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) + 0.5


def blank(c):
    a = np.zeros((N, N, 3), np.float32)
    a[:] = c
    return a


def hstripes(cols, w=None):
    w = w or [1] * len(cols)
    a = blank(cols[0]); tot = sum(w); y0 = 0
    for c, k in zip(cols, w):
        y1 = y0 + N * k / tot
        a[(yy >= y0) & (yy < y1)] = c
        y0 = y1
    return a


def vstripes(cols, w=None):
    w = w or [1] * len(cols)
    a = blank(cols[0]); tot = sum(w); x0 = 0
    for c, k in zip(cols, w):
        x1 = x0 + N * k / tot
        a[(xx >= x0) & (xx < x1)] = c
        x0 = x1
    return a


def disc(a, cx, cy, r, c):
    a[(xx - cx) ** 2 + (yy - cy) ** 2 <= r * r] = c
    return a


def rect(a, x0, y0, x1, y1, c):
    a[(xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)] = c
    return a


def star(a, cx, cy, r, c):
    """estrela de 5 pontas pequena (polígono)."""
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    inside = np.zeros((N, N), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        cond = ((y1 > yy) != (y2 > yy)) & (xx < (x2 - x1) * (yy - y1) / (y2 - y1 + 1e-9) + x1)
        inside ^= cond
    a[inside] = c
    return a


R_, W_, B_, G_, Y_, K_ = (206, 32, 44), (250, 250, 250), (16, 52, 140), (0, 140, 70), (252, 206, 0), (24, 24, 24)


def brasil():
    a = blank((0, 156, 59))
    a[np.abs(xx - 11) / 10.2 + np.abs(yy - 11) / 8.0 <= 1] = (254, 223, 0)
    disc(a, 11, 11, 4.6, (0, 39, 118))
    a[(np.abs(np.hypot(xx - 13, yy - 16) - 7.2) < 0.6) & ((xx - 11) ** 2 + (yy - 11) ** 2 <= 4.6 ** 2)] = W_
    return a


def argentina():
    a = hstripes([(116, 172, 223), W_, (116, 172, 223)])
    disc(a, 11, 11, 2.4, (246, 180, 14))
    return a


def eua():
    a = blank(W_)
    for k in range(7):
        if k % 2 == 0:
            a[(yy >= k * N / 7) & (yy < (k + 1) * N / 7)] = (178, 34, 52)
    rect(a, 0, 0, 11, 11.0, (60, 59, 110))
    for i in range(3):
        for j in range(3):
            a[int(2 + i * 3.3), int(2 + j * 3.3)] = W_
    return a


def uruguai():
    a = blank(W_)
    for k in range(9):
        if k % 2 == 1:
            a[(yy >= k * N / 9) & (yy < (k + 1) * N / 9)] = (0, 56, 168)
    rect(a, 0, 0, 10, 10, W_)
    disc(a, 5, 5, 2.8, (252, 209, 22))
    return a


def chile():
    a = hstripes([W_, (213, 43, 30)])
    rect(a, 0, 0, 9, 11, (0, 57, 166))
    star(a, 4.5, 5.5, 3.0, W_)
    return a


def japao():
    return disc(blank(W_), 11, 11, 6.2, (188, 0, 45))


def coreia():
    a = blank(W_)
    m = (xx - 11) ** 2 + (yy - 11) ** 2 <= 5.2 ** 2
    a[m & (yy < 11 + 1.5 * np.sin((xx - 11) / 5.2 * math.pi))] = (205, 46, 58)
    a[m & (yy >= 11 + 1.5 * np.sin((xx - 11) / 5.2 * math.pi))] = (0, 71, 160)
    for (cx, cy) in ((3.5, 3.5), (18.5, 3.5), (3.5, 18.5), (18.5, 18.5)):
        for k in range(3):
            rect(a, cx - 2, cy - 1.6 + k * 1.3, cx + 2, cy - 1.0 + k * 1.3, K_)
    return a


def china():
    a = blank((222, 41, 16))
    star(a, 6, 6, 4.2, (255, 222, 0))
    for (cx, cy) in ((11, 2.5), (13, 5), (13, 8.5), (11, 11)):
        star(a, cx, cy, 1.4, (255, 222, 0))
    return a


def india():
    a = hstripes([(255, 153, 51), W_, (19, 136, 8)])
    a[np.abs(np.hypot(xx - 11, yy - 11) - 2.6) < 0.7] = (0, 0, 136)
    return a


def suecia():
    a = blank((0, 106, 167))
    rect(a, 6, 0, 10, N, (254, 204, 0)); rect(a, 0, 9, N, 13, (254, 204, 0))
    return a


def suica():
    a = blank((218, 41, 28))
    rect(a, 9, 4, 13, 18, W_); rect(a, 4, 9, 18, 13, W_)
    return a


def inglaterra():
    a = blank(W_)
    rect(a, 9, 0, 13, N, (206, 17, 36)); rect(a, 0, 9, N, 13, (206, 17, 36))
    return a


def turquia():
    a = blank((227, 10, 23))
    disc(a, 9, 11, 5.6, W_); disc(a, 10.6, 11, 4.5, (227, 10, 23))
    star(a, 15, 11, 2.6, W_)
    return a


def marrocos():
    a = blank((193, 39, 45))
    s = np.zeros((N, N, 3), np.float32); star(s, 11, 11.5, 6.0, (1, 1, 1))
    inner = np.zeros((N, N, 3), np.float32); star(inner, 11, 11.5, 4.2, (1, 1, 1))
    a[(s[..., 0] > 0) & (inner[..., 0] == 0)] = (0, 98, 51)
    return a


def canada():
    a = vstripes([(216, 6, 33), W_, (216, 6, 33)], [1, 2, 1])
    a[(np.abs(xx - 11) / 3.6 + np.abs(yy - 10.5) / 4.2 <= 1)] = (216, 6, 33)
    a[(np.abs(xx - 11) / 5.0 + np.abs(yy - 9.5) / 2.0 <= 1)] = (216, 6, 33)
    rect(a, 10.5, 14, 11.5, 17, (216, 6, 33))
    return a


def espanha():
    a = hstripes([(170, 21, 27), (241, 191, 0), (170, 21, 27)], [1, 2, 1])
    rect(a, 5, 8, 8, 13, (170, 21, 27))
    return a


def portugal():
    a = vstripes([(0, 102, 0), (255, 0, 0)], [2, 3])
    disc(a, 8.8, 11, 4.2, (255, 225, 0)); disc(a, 8.8, 11, 2.6, (255, 0, 0)); disc(a, 8.8, 11, 1.6, W_)
    return a


def croacia():
    a = hstripes([(255, 0, 0), W_, (23, 23, 150)])
    for i in range(4):
        for j in range(3):
            rect(a, 8 + i * 1.5, 7.5 + j * 1.8, 9.5 + i * 1.5, 9.3 + j * 1.8, (255, 0, 0) if (i + j) % 2 == 0 else W_)
    return a


def mexico():
    a = vstripes([(0, 104, 71), W_, (206, 17, 38)])
    disc(a, 11, 11, 2.6, (140, 90, 40))
    return a


def senegal():
    a = vstripes([(0, 133, 63), (253, 239, 66), (227, 27, 35)])
    star(a, 11, 11.5, 3.6, (0, 133, 63))
    return a


def paraguai():
    a = hstripes([(213, 43, 30), W_, (0, 56, 168)])
    a[np.abs(np.hypot(xx - 11, yy - 11) - 2.4) < 0.7] = (0, 120, 60)
    return a


def gana():
    a = hstripes([(206, 17, 38), (252, 209, 22), (0, 107, 63)])
    star(a, 11, 11.3, 3.6, K_)
    return a


COUNTRIES = [
    ('BRASIL', brasil), ('ARGENTINA', argentina), ('FRANÇA', lambda: vstripes([(0, 85, 164), W_, (239, 65, 53)])),
    ('ALEMANHA', lambda: hstripes([K_, (221, 0, 0), (255, 206, 0)])), ('ESPANHA', espanha), ('PORTUGAL', portugal),
    ('ITÁLIA', lambda: vstripes([(0, 146, 70), W_, (206, 43, 55)])), ('INGLATERRA', inglaterra),
    ('HOLANDA', lambda: hstripes([(174, 28, 40), W_, (33, 70, 139)])),
    ('BÉLGICA', lambda: vstripes([K_, (253, 218, 36), (239, 51, 64)])), ('CROÁCIA', croacia), ('URUGUAI', uruguai),
    ('COLÔMBIA', lambda: hstripes([(252, 209, 22), (0, 56, 147), (206, 17, 38)], [2, 1, 1])), ('CHILE', chile),
    ('PARAGUAI', paraguai), ('PERU', lambda: vstripes([(217, 16, 35), W_, (217, 16, 35)])), ('MÉXICO', mexico),
    ('EUA', eua), ('CANADÁ', canada), ('JAPÃO', japao), ('COREIA DO SUL', coreia), ('CHINA', china),
    ('ÍNDIA', india), ('RÚSSIA', lambda: hstripes([W_, (0, 57, 166), (213, 43, 30)])),
    ('UCRÂNIA', lambda: hstripes([(0, 87, 183), (255, 215, 0)])), ('POLÔNIA', lambda: hstripes([W_, (220, 20, 60)])),
    ('SUÉCIA', suecia), ('SUÍÇA', suica), ('TURQUIA', turquia), ('MARROCOS', marrocos),
    ('NIGÉRIA', lambda: vstripes([(0, 135, 81), W_, (0, 135, 81)])), ('SENEGAL', senegal),
]


def ball(flag, shade=True):
    """recorta a bandeira em bolinha, com contorno e brilho. Devolve (rgb uint8, máscara)."""
    a = flag.copy()
    r = np.hypot(xx - 11, yy - 11)
    m = r <= 10.6
    if shade:
        lit = -((xx - 11) + (yy - 11)) / 15
        a = a * (0.86 + 0.18 * np.clip(lit, -1, 1))[..., None]
        a[(np.hypot(xx - 7.5, yy - 7) < 1.6)] = (255, 255, 255)
        a[(np.hypot(xx - 9.5, yy - 5.8) < 0.8)] = (255, 255, 255)
    ring = (r > 10.6) & (r <= 11.6)
    out = np.zeros((N, N, 3), np.float32)
    out[m] = a[m]
    out[ring] = (30, 22, 26)
    return np.clip(out, 0, 255).astype(np.uint8), (m | ring)
