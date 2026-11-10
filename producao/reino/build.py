#!/usr/bin/env python3
"""Construções de Brasa (sprites RGBA em pixel art, escala do canvas 360x640)."""
import math, random
import numpy as np

OUT = (34, 26, 32)


class Spr:
    def __init__(self, w, h):
        self.a = np.zeros((h, w, 4), np.float32)
        self.w, self.h = w, h
        self.emis = []   # (x, y, cor) acesos à noite

    def px(self, x, y, c, emis=False):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x, :3] = c
            self.a[y, x, 3] = 1
            if emis:
                self.emis.append((x, y, c))

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def outline(self):
        m = self.a[..., 3] > 0
        ring = np.zeros_like(m)
        ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
        ring &= ~m
        self.a[ring, :3] = OUT
        self.a[ring, 3] = 1
        return self


def shade(c, f):
    return tuple(int(max(0, min(255, v * f))) for v in c)


def roof(s, x0, x1, ytop, ybase, col, cols, apex=None, rows=3):
    apex = apex if apex is not None else (x0 + x1) / 2
    for y in range(ytop, ybase + 1):
        t = (y - ytop) / max(1, ybase - ytop)
        hw = t * (x1 - x0) / 2 + 1
        for x in range(int(apex - hw), int(apex + hw) + 1):
            c = col if x < apex else cols
            if (y - ytop) % rows == rows - 1:
                c = shade(c, 0.8)
            elif (x + (y // rows) * 2) % 6 == 0:
                c = shade(c, 0.9)
            s.px(x, y, c)


def stones(s, x0, y0, x1, y1, base, seed=1):
    r = random.Random(seed)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            row = (y - y0) // 4
            off = 3 if row % 2 else 0
            mortar = (y - y0) % 4 == 3 or (x - x0 + off) % 7 == 6
            c = shade(base, 0.72) if mortar else shade(base, 0.92 + r.random() * 0.16)
            if x >= x1 - 3:
                c = shade(c, 0.82)
            s.px(x, y, c)


def forja():
    s = Spr(62, 60)
    stones(s, 4, 22, 55, 59, (150, 146, 156), 3)
    roof(s, 0, 59, 4, 23, (78, 84, 108), (60, 64, 86))
    stones(s, 42, 0, 49, 14, (130, 126, 136), 5)
    s.rect(41, 0, 50, 1, (60, 56, 64))
    s.rect(22, 36, 36, 59, (40, 28, 26))
    for x in range(22, 37):
        s.px(x, 35, (70, 60, 64))
    for k, (x, y) in enumerate([(25, 57), (26, 56), (27, 57), (29, 55), (30, 56), (31, 57), (33, 56), (34, 57), (28, 58),
                                (30, 58), (32, 58), (26, 58)]):
        s.px(x, y, (255, 150, 50) if k % 3 else (255, 220, 120), emis=True)
    for y in range(40, 55):
        s.px(22, y, (255, 120, 40), emis=True) if y % 3 == 0 else None
    s.rect(46, 52, 57, 54, (90, 92, 104)); s.rect(48, 55, 55, 59, (70, 72, 84)); s.rect(44, 51, 49, 52, (120, 124, 136))
    s.rect(6, 30, 17, 37, (150, 104, 60)); s.rect(7, 31, 16, 36, (190, 144, 90))
    s.rect(11, 32, 12, 35, (110, 72, 40)); s.rect(9, 32, 14, 33, (90, 92, 104))
    s.px(9, 29, (80, 52, 30)); s.px(14, 29, (80, 52, 30))
    return s.outline()


def padaria():
    s = Spr(64, 62)
    wall, beam = (238, 224, 192), (112, 72, 40)
    s.rect(4, 26, 59, 61, wall)
    for x in range(4, 60):
        if x >= 54:
            for y in range(26, 62):
                s.px(x, y, shade(wall, 0.86))
    for x in (4, 20, 43, 59):
        for y in range(26, 62):
            s.px(x, y, beam); s.px(x + 1, y, shade(beam, 0.8)) if x < 59 else None
    for y in (26, 27, 44, 61):
        for x in range(4, 60):
            s.px(x, y, beam)
    for k in range(10):
        s.px(6 + k, 28 + k, beam); s.px(57 - k, 28 + k, beam)
    roof(s, 0, 63, 6, 27, (192, 72, 54), (156, 54, 42))
    s.rect(46, 0, 52, 14, (160, 70, 50)); s.rect(45, 0, 53, 1, (110, 50, 36))
    for y in range(2, 14, 3):
        for x in range(46, 53):
            s.px(x, y, (130, 56, 40))
    s.rect(26, 42, 37, 61, (128, 82, 46))
    for y in range(42, 62):
        s.px(31, y, (100, 62, 34))
    s.rect(28, 45, 35, 50, (255, 214, 130))
    for x, y in [(28, 45), (35, 45)]:
        s.px(x, y, (128, 82, 46))
    for (x, y) in [(36, 53)]:
        s.px(x, y, (230, 190, 80))
    s.rect(8, 32, 18, 42, (255, 214, 130))
    for x0 in (9, 13):
        s.rect(x0, 38, x0 + 3, 40, (214, 150, 70)); s.px(x0 + 1, 37, (236, 186, 110))
    for y in range(32, 43):
        s.px(13, y, beam) if y < 36 else None
    for x, y in [(8 + i, j) for i in range(11) for j in range(32, 43)]:
        if s.a[y, x, 0] > 250:
            s.emis.append((x, y, (255, 214, 130)))
    for x, y in [(28 + i, j) for i in range(8) for j in range(45, 51)]:
        s.emis.append((x, y, (255, 214, 130)))
    s.rect(40, 30, 50, 37, (150, 104, 60)); s.rect(41, 31, 49, 36, (200, 156, 98))
    s.rect(42, 33, 48, 34, (214, 150, 70)); s.px(43, 32, (236, 186, 110)); s.px(46, 32, (236, 186, 110))
    s.rect(14, 59, 22, 61, (120, 80, 50))
    return s.outline()


def biblioteca():
    s = Spr(48, 76)
    stones(s, 6, 26, 41, 75, (200, 190, 172), 7)
    roof(s, 2, 45, 0, 27, (122, 80, 170), (96, 60, 140), rows=4)
    s.px(23, 0, (255, 210, 90))
    cx, cy = 23, 40
    for y in range(cy - 5, cy + 6):
        for x in range(cx - 5, cx + 6):
            d = math.hypot(x - cx, y - cy)
            if d <= 5.2:
                c = (96, 60, 34) if d > 4.1 else ((150, 200, 240) if x < cx else (120, 170, 220))
                if d <= 4.1 and (x == cx or y == cy):
                    c = (96, 60, 34)
                s.px(x, y, c)
                if d <= 4.1 and not (x == cx or y == cy):
                    s.emis.append((x, y, (255, 214, 130)))
    for y in range(58, 76):
        for x in range(17, 30):
            if y > 61 or abs(x - 23) < 5 - (61 - y):
                s.px(x, y, (110, 70, 40) if x != 23 else (86, 54, 30))
    s.px(26, 67, (230, 190, 80))
    s.rect(8, 48, 15, 55, (150, 104, 60)); s.rect(9, 49, 14, 54, (180, 50, 60)); s.rect(11, 49, 11, 54, (240, 230, 200))
    for y in (30, 31):
        for x in range(6, 42):
            s.px(x, y, (170, 160, 146))
    return s.outline()


def lantern_post():
    s = Spr(8, 26)
    for y in range(6, 26):
        s.px(3, y, (100, 66, 38)); s.px(4, y, (80, 52, 30))
    s.rect(1, 1, 6, 6, (60, 50, 50))
    s.rect(2, 2, 5, 5, (255, 214, 120))
    for x in range(2, 6):
        for y in range(2, 6):
            s.emis.append((x, y, (255, 214, 120)))
    return s.outline()


def draw_pier(img, mask=None, p=1.0):
    """píer de madeira saindo da margem (x 196..214, y 282..300)."""
    rows = int((300 - 282) * p)
    for k in range(rows):
        y = 300 - k
        for x in range(198, 214):
            c = (164, 112, 68) if (y // 2) % 2 == 0 else (146, 98, 58)
            if x in (198, 213):
                c = (104, 66, 38)
            img[y, x] = c
    if p >= 1:
        for x, y0 in ((198, 282), (213, 282), (198, 290), (213, 290)):
            for y in range(y0, y0 + 5):
                img[y, x] = (90, 58, 34)


def draw_horta(img, p=1.0, t=0.0):
    """horta do Victor (x 246..306, y 430..466)."""
    n = int(4 * p + 0.999)
    for r_ in range(n):
        y0 = 434 + r_ * 8
        for y in range(y0, y0 + 5):
            for x in range(248, 304):
                img[y, x] = (118, 80, 48) if y < y0 + 3 else (96, 64, 38)
        for x in range(252, 302, 6):
            img[y0 - 1, x] = (90, 170, 70); img[y0 - 2, x] = (120, 200, 90)
            img[y0 - 1, x + 1] = (70, 140, 60)
            if (x // 6 + r_) % 3 == 0:
                img[y0 - 2, x + 1] = (230, 110, 60)
    if p >= 1:
        for x in range(244, 310, 8):
            for y in range(428, 436):
                img[y, x] = (150, 108, 64)
        for x in range(244, 308):
            img[430, x] = (176, 128, 78)


def blit(img, spr, x0, y0, p=1.0, t=0.0, night=0.0, dust=True):
    """Desenha a construção com progresso p (de baixo para cima)."""
    a = spr.a
    h, w = a.shape[:2]
    if p <= 0:
        return
    cut = int(h * (1 - min(1.0, p)))
    ys, xs = np.nonzero(a[cut:, :, 3] > 0)
    ys = ys + cut
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < img.shape[0]) & (X >= 0) & (X < img.shape[1])
    img[Y[ok], X[ok]] = a[ys[ok], xs[ok], :3]
    if p < 1:
        r = random.Random(int(t * 30))
        for _ in range(10):
            x = x0 + r.randrange(w)
            y = y0 + cut + r.randint(-1, 1)
            if 0 <= y < img.shape[0] and 0 <= x < img.shape[1] and a[min(h - 1, max(0, y - y0)), min(w - 1, x - x0), 3] > 0:
                img[y, x] = (255, 250, 210)
        if dust:
            for _ in range(14):
                x = x0 + r.randint(-6, w + 6)
                y = y0 + h + r.randint(-4, 1)
                if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
                    img[y, x] = img[y, x] * 0.4 + np.array((220, 210, 190)) * 0.6


def emissive(out, spr, x0, y0, strength, t=0.0):
    if strength <= 0:
        return
    for x, y, c in spr.emis:
        X, Y = x + x0, y + y0
        if 0 <= Y < out.shape[0] and 0 <= X < out.shape[1]:
            f = strength * (0.85 + 0.15 * math.sin(t * 9 + x))
            out[Y, X] = out[Y, X] * (1 - f) + np.array(c) * f


def smoke_at(img, t, cx, cy, n=6, seed=0):
    for k in range(n):
        ph = (t * 0.45 + k / n + seed * 0.13) % 1
        y = int(cy - ph * 40)
        x = int(cx + math.sin(ph * 6 + k + seed) * 3 + ph * 10)
        a = 0.5 * (1 - ph)
        for dx, dy in ((0, 0), (1, 0), (0, -1), (1, -1)) if ph > 0.2 else ((0, 0),):
            if 0 <= y + dy < img.shape[0] and 0 <= x + dx < img.shape[1]:
                img[y + dy, x + dx] = img[y + dy, x + dx] * (1 - a) + np.array((206, 206, 216)) * a


FORJA, PADARIA, BIBLIO, LANTERN = forja(), padaria(), biblioteca(), lantern_post()
# posição (canto superior esquerdo) no canvas 360x640
POS = {'forja': (52, 356 - FORJA.h), 'padaria': (236, 396 - PADARIA.h), 'biblio': (58, 478 - BIBLIO.h),
       'lantern': (290, 304 - LANTERN.h)}
