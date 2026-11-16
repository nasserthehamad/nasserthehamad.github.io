#!/usr/bin/env python3
"""Será que enche? — "O cercado do Valdemir": cercado redondo, uma haste girando no centro; cada ovelha que a haste
prensa vira duas, até a cerca estourar. Pixel art 360x640 (ampliado 3x), sem narração.
Uso: SEED=2 OUT=out/cercado.mp4 python3 cercado.py
     PLAN=1 (só a linha do tempo) · STILLS=1,8,15.5,17,19.5 (quadros de conferência) · CAPA=1 (capa)
"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REINO = os.environ.get('REINO', '/home/claude/reino')
sys.path.insert(0, REINO)
import ep1hd as E
import folk as F
import world2 as W
from sim import simulate, CX, CY, R, RS, HW

FW, FH, FPS, S = 1080, 1920, 30, 3
CW, CH = 360, 640
SEED = int(os.environ.get('SEED', '2'))
OMEGA = float(os.environ.get('OMEGA', '2.4'))
NMAX = int(os.environ.get('NMAX', '240'))
SPEED = float(os.environ.get('SPEED', '140'))
COOL = float(os.environ.get('COOL', '0.8'))
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.environ.get('OUT', os.path.join(OUTDIR, 'cercado.mp4'))

WHITE, GOLD, TEAL, RED, ORANGE = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 84, 64), (255, 170, 80)

FR, EV, B = simulate(seed=SEED, omega=OMEGA, nmax=NMAX, speed=SPEED, cooldown=COOL)
NFIN = FR[-1]['n']
P = 2 * math.pi / OMEGA
END = math.ceil((B + 4.4) / P) * P            # a haste volta pro mesmo ângulo: o loop emenda
T_CTA = B + 2.3
T_REB = END - 0.9                               # a cerca se refaz
T_SHEEP0 = END - 0.35                           # a primeira ovelha volta
RF = R + 3.0                                    # raio da cerca (chão)
NP = 40                                         # postes
rng0 = random.Random(SEED * 7 + 1)
POST_H = [rng0.random() for _ in range(NP)]
CRACK = [(rng0.uniform(0.55, 0.97) if rng0.random() < 0.45 else 9.0) for _ in range(NP)]
BLACK = set(i for i in range(1, 400) if random.Random(i * 31).random() < 0.07)

yy, xx = np.mgrid[0:CH, 0:CW]
BAY = np.tile(W.BAYER, (CH // 4, CW // 4))


# ================================================================ chão
def build_ground():
    g = np.zeros((CH, CW, 3), np.float32)
    gn = W.vnoise(CH, CW, 30, 11, 3)
    lvl = np.clip(np.floor(gn * 3.2 + (BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
    g[:] = W.GREENS[lvl]
    r = np.hypot(xx - CX, yy - CY)
    inside = r < RF - 1
    dn = W.vnoise(CH, CW, 16, 23, 3)
    dirt = inside & (dn + (1 - r / R) * 0.35 + (BAY - 0.5) * 0.12 > 0.62)
    dl = np.clip(np.floor(W.vnoise(CH, CW, 10, 5, 2) * 3.3 + (BAY - 0.5) * 0.9 - 0.15), 0, 2).astype(int)
    g[dirt] = W.DIRT[dl[dirt]] * 0.94
    # grama pisada dentro do cercado (mais clara/amarelada)
    worn = inside & ~dirt
    g[worn] = g[worn] * np.array([1.06, 1.0, 0.86], np.float32)
    rr = random.Random(9)

    def put(x, y, c):
        if 0 <= x < CW and 0 <= y < CH:
            g[y, x] = c
    for _ in range(2400):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < RF - 2:
            continue
        c0 = (88, 144, 64) if rr.random() < 0.7 else (78, 132, 58)
        put(x, y, c0); put(x + 1, y - 1, c0); put(x + 2, y, c0)
    for _ in range(1100):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < RF - 2:
            continue
        put(x, y, (150, 206, 104))
        if rr.random() < 0.3:
            put(x, y - 1, (166, 218, 116))
    for _ in range(140):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < RF + 6:
            continue
        c0 = rr.choice(W.FLOWER)
        put(x, y + 1, (70, 130, 60))
        put(x, y, c0); put(x - 1, y, W.shade(c0, 0.85)); put(x + 1, y, W.shade(c0, 0.85)); put(x, y - 1, W.shade(c0, 0.9))
        put(x, y, (255, 240, 170))
    # feno espalhado dentro
    for _ in range(260):
        a = rr.uniform(0, 2 * math.pi); d = math.sqrt(rr.random()) * (R - 6)
        x, y = int(CX + d * math.cos(a)), int(CY + d * math.sin(a))
        b = rr.uniform(0, math.pi)
        col = (230, 204, 118) if rr.random() < 0.6 else (206, 172, 92)
        for k in range(rr.randint(2, 4)):
            put(int(round(x + k * math.cos(b))), int(round(y + k * math.sin(b))), col)
    # sombra da cerca (pro lado de baixo/direita)
    rs = np.hypot(xx - 2 - CX, yy - 3 - CY)
    sh = (rs > RF - 1) & (rs < RF + 2.5) & (r > RF - 1)
    g[sh] *= 0.72
    # moitas nos cantos de baixo
    for (bx, by, bw) in ((330, 600, 22), (18, 612, 18), (344, 420, 12), (14, 330, 10)):
        for y in range(by - bw, by + 4):
            for x in range(bx - bw, bx + bw):
                e = ((x - bx) / bw) ** 2 + ((y - by) / (bw * 0.7)) ** 2
                if e < 1:
                    hi = (x - bx) + (y - by) < -bw * 0.3
                    c0 = (74, 136, 66) if not hi else (104, 168, 82)
                    if (x * 7 + y * 13) % 11 == 0:
                        c0 = (58, 112, 56)
                    put(x, y, c0)
    # vinheta leve
    vg = np.clip((np.hypot((xx - CX) / 230, (yy - 330) / 400) - 0.75) * 0.9, 0, 0.35)
    g *= (1 - vg)[..., None]
    g[:200] *= np.linspace(0.78, 1.0, 200)[:, None, None]
    return g


GROUND = build_ground()


# ================================================================ ovelha (vista de cima)
SPR = 25
_sheep = {}


def sheep_sprite(hi, dark, leg, sc):
    k = (hi, dark, leg, sc)
    if k in _sheep:
        return _sheep[k]
    a = 2 * math.pi * hi / 16
    ca, sa = math.cos(a), math.sin(a)
    c = SPR // 2
    v, u = np.mgrid[0:SPR, 0:SPR].astype(np.float32)
    u = (u - c) / sc; v = (v - c) / sc
    f = u * ca + v * sa
    s = -u * sa + v * ca
    body = (f / 6.4) ** 2 + (s / 5.9) ** 2 <= 1
    for j in range(8):
        b = 2 * math.pi * j / 8 + 0.3
        body |= (f - 5.0 * math.cos(b)) ** 2 + (s - 4.6 * math.sin(b)) ** 2 <= 4.2
    head = ((f - 7.4) / 2.9) ** 2 + (s / 2.4) ** 2 <= 1
    ears = ((f - 6.2) ** 2 + (s - 3.0) ** 2 <= 1.4) | ((f - 6.2) ** 2 + (s + 3.0) ** 2 <= 1.4)
    legs = np.zeros_like(body)
    pairs = [((3.4, 5.6), (-3.4, -5.6)), ((3.4, -5.6), (-3.4, 5.6))][leg]
    for (lf, ls) in pairs:
        legs |= (f - lf) ** 2 + (s - ls * 1.12) ** 2 <= 1.3
    legs &= ~body
    mask = body | head | ears | legs
    out = np.zeros((SPR, SPR, 4), np.float32)
    if dark:
        wb, wh, wl, wc = (70, 64, 74), (98, 92, 104), (50, 46, 56), (60, 54, 64)
        hd, hh = (30, 26, 30), (54, 48, 52)
    else:
        wb, wh, wl, wc = (234, 230, 222), (252, 252, 246), (196, 192, 190), (214, 210, 204)
        hd, hh = (62, 52, 56), (98, 86, 90)
    lit = -(u + v) * 0.16 + (BAY[:SPR, :SPR] - 0.5) * 0.5
    curl = ((np.round(f * 0.9) + 2 * np.round(s * 0.9)) % 4 == 0)
    col = np.where((lit > 0.55)[..., None], wh, np.where((lit < -0.75)[..., None], wl, wb)).astype(np.float32)
    col = np.where((curl & (lit < 0.5) & (lit > -0.75))[..., None], np.array(wc, np.float32), col)
    out[..., :3] = col
    out[head | ears, :3] = hd
    hl = head & ((u - 7.4 * ca) + (v - 7.4 * sa) < -1.3)
    out[hl, :3] = hh
    out[ears & ~head, :3] = (104, 88, 92) if not dark else (60, 52, 58)
    out[legs, :3] = (46, 38, 42)
    # olhinhos
    for es in (-1.5, 1.5):
        ex = c + (8.2 * ca - es * sa) * sc
        ey = c + (8.2 * sa + es * ca) * sc
        xi, yi = int(round(ex)), int(round(ey))
        if 0 <= xi < SPR and 0 <= yi < SPR and head[yi, xi]:
            out[yi, xi, :3] = (236, 236, 236)
    out[..., 3] = mask
    # contorno
    m = mask
    dil = m.copy()
    dil[1:] |= m[:-1]; dil[:-1] |= m[1:]; dil[:, 1:] |= m[:, :-1]; dil[:, :-1] |= m[:, 1:]
    ol = dil & ~m
    out[ol, :3] = (44, 36, 44)
    out[ol, 3] = 1
    _sheep[k] = (out[..., :3].astype(np.uint8), out[..., 3] > 0)
    return _sheep[k]


SHAD = None


def _shadow():
    v, u = np.mgrid[0:12, 0:18]
    return ((u - 8.5) / 8.0) ** 2 + ((v - 5.5) / 5.0) ** 2 <= 1


SHAD = _shadow()


def draw_sheep(img, x, y, ang, dark, leg, sc=1.0, z=0.0):
    hi = int(round(ang / (2 * math.pi) * 16)) % 16
    scq = min([0.55, 0.8, 1.0], key=lambda q: abs(q - sc))
    rgb, m = sheep_sprite(hi, dark, leg, scq)
    xi, yi = int(round(x)), int(round(y))
    # sombra
    x0, y0 = xi - 9 + 1, yi - 6 + 3
    _blend_mask(img, SHAD, x0, y0, 0.72)
    x0, y0 = xi - SPR // 2, yi - SPR // 2 - int(round(z))
    _blit(img, rgb, m, x0, y0)


def _blend_mask(img, m, x0, y0, k):
    h, w = m.shape
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0]
    reg = img[ya:yb, xa:xb]
    reg[mm] = (reg[mm] * k).astype(img.dtype)


def _blit(img, rgb, m, x0, y0):
    h, w = m.shape
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0]
    img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - x0:xb - x0][mm]


# ================================================================ moradores em volta
FOLK = [('Valdemir', 'vaqueiro', 40, 494), ('Luiza', 'santa', 24, 264), ('pixoto', 'cidadão', 60, 248),
        ('Yasmim', 'cantora', 302, 248), ('Gabriel', 'ferreiro', 336, 264)]


def _folk_rgb(name, role):
    a = F.folk(name, role, 0)
    return a[..., :3].astype(np.uint8), a[..., 3] > 0.5


FOLK_SPR = {nm: _folk_rgb(nm, rl) for nm, rl, _, _ in FOLK}


def draw_folk(img, t):
    for i, (nm, rl, fx, fy) in enumerate(FOLK):
        rgb, m = FOLK_SPR[nm]
        jump = 0
        if B <= t < B + 1.6:
            jump = int(round(abs(math.sin((t - B) * 9 + i)) * 7))
        x0, y0 = fx - 15, fy - 42 - jump
        _blend_mask(img, np.ones((3, 16), bool), fx - 8, fy - 2, 0.7)
        _blit(img, rgb, m, x0, y0)
        if B + 0.05 <= t < B + 1.8:
            W.qmark(img, fx - 3, y0 + 4 - 12, bang=True)
        elif nm == 'Valdemir' and B - 4.0 <= t < B:
            if int(t * 3) % 2 == 0:
                W.qmark(img, fx - 3, y0 + 4 - 12, bang=False)


# ================================================================ cerca, haste
WOOD = dict(lit=(196, 146, 90), mid=(160, 112, 66), dark=(112, 74, 42), out=(60, 40, 30), cap=(214, 170, 110))


def strain_at(n):
    return min(1.0, n / NMAX)


def post_geom(i, s, t, rebuilt=1.0):
    phi = 2 * math.pi * i / NP
    sev = max(0.0, (s - 0.3) / 0.7) ** 1.6
    bulge = sev * (2.5 + 3.5 * POST_H[i])
    jit = 0.0
    if s > 0.55:
        jit = (s - 0.55) * 2.6 * math.sin(t * 47 + i * 2.3) * (0.5 + POST_H[i])
    r = RF + bulge + jit
    gx, gy = CX + r * math.cos(phi), CY + r * math.sin(phi)
    tilt = sev * (2.0 + 3.0 * POST_H[i])
    tx, ty = gx + tilt * math.cos(phi), gy + tilt * math.sin(phi)
    h = 12 * rebuilt
    return (gx, gy), (tx, ty - h)


def draw_fence(d, s, t, half, rebuild_t=None):
    """half: 'back' (metade de cima, atrás das ovelhas) ou 'front'."""
    geo = []
    for i in range(NP):
        rb = 1.0
        if rebuild_t is not None:
            ti = T_REB + 0.05 + 0.55 * i / NP
            rb = 0.0 if rebuild_t < ti else min(1.0, (rebuild_t - ti) / 0.08)
        geo.append((post_geom(i, s, t, rb), rb))

    def is_back(phi):
        return math.sin(phi) < 0

    # trilhos
    for i in range(NP):
        j = (i + 1) % NP
        phm = 2 * math.pi * (i + 0.5) / NP
        if is_back(phm) != (half == 'back'):
            continue
        (g1, t1), rb1 = geo[i]
        (g2, t2), rb2 = geo[j]
        if rb1 < 1 or rb2 < 1:
            continue
        cracked = s >= CRACK[i]
        for hh, col, colhi in ((4, WOOD['dark'], WOOD['mid']), (9, WOOD['mid'], WOOD['lit'])):
            fr = hh / 12
            a = (g1[0] + (t1[0] - g1[0]) * fr, g1[1] + (t1[1] + 12 - g1[1]) * fr - hh)
            b = (g2[0] + (t2[0] - g2[0]) * fr, g2[1] + (t2[1] + 12 - g2[1]) * fr - hh)
            if cracked and hh == 9:
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 2.5
                d.line([a, (mx - 1, my)], fill=WOOD['out'], width=3)
                d.line([(mx + 1, my), b], fill=WOOD['out'], width=3)
                d.line([a, (mx - 1, my - 1)], fill=colhi, width=1)
                d.line([(mx + 1, my - 1), b], fill=colhi, width=1)
                d.point([(mx - 1, my - 2), (mx + 1, my + 1)], fill=(236, 210, 160))
            else:
                d.line([a, b], fill=WOOD['out'], width=3)
                d.line([(a[0], a[1] - 0.5), (b[0], b[1] - 0.5)], fill=colhi, width=1)
    # postes
    for i in range(NP):
        phi = 2 * math.pi * i / NP
        if is_back(phi) != (half == 'back'):
            continue
        (g, tp), rb = geo[i]
        if rb <= 0:
            continue
        gx, gy = g
        tx, ty = tp
        d.polygon([(gx - 2.5, gy + 0.5), (gx + 2.5, gy + 0.5), (tx + 2.5, ty), (tx - 2.5, ty)], fill=WOOD['out'])
        d.polygon([(gx - 1.5, gy - 0.5), (gx + 1.5, gy - 0.5), (tx + 1.5, ty + 1), (tx - 1.5, ty + 1)], fill=WOOD['mid'])
        d.line([(gx - 1.5, gy - 0.5), (tx - 1.5, ty + 1)], fill=WOOD['lit'], width=1)
        d.line([(gx + 1.5, gy - 0.5), (tx + 1.5, ty + 1)], fill=WOOD['dark'], width=1)
        d.rectangle([tx - 1.5, ty, tx + 1.5, ty + 1], fill=WOOD['cap'])


def draw_rod(img, theta, alpha_ghost=True):
    pil = Image.fromarray(img)
    sm = Image.new('L', (CW, CH), 0)
    ds = ImageDraw.Draw(sm)
    L0, L1, H0 = 8, R - 1, 5

    def quad(th, w, dx=0, dy=0, l0=L0, l1=L1):
        u = (math.cos(th), math.sin(th)); n = (-u[1], u[0])
        return [(CX + u[0] * l0 + n[0] * w + dx, CY + u[1] * l0 + n[1] * w + dy),
                (CX + u[0] * l1 + n[0] * w + dx, CY + u[1] * l1 + n[1] * w + dy),
                (CX + u[0] * l1 - n[0] * w + dx, CY + u[1] * l1 - n[1] * w + dy),
                (CX + u[0] * l0 - n[0] * w + dx, CY + u[1] * l0 - n[1] * w + dy)]
    ds.polygon(quad(theta, HW + 1, 2, 3), fill=110)
    ds.ellipse([CX - 11 + 2, CY - 9 + 3, CX + 11 + 2, CY + 9 + 3], fill=110)
    a = np.asarray(sm, np.float32) / 255
    base = np.asarray(pil, np.float32) * (1 - a[..., None] * 0.45 / 0.43)
    pil = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(pil, 'RGBA')
    if alpha_ghost:
        for k, al in ((2, 40), (1, 70)):
            d.polygon(quad(theta - OMEGA / FPS * k * 0.9, HW, 0, -H0), fill=(196, 146, 90, al))
    d.polygon(quad(theta, HW + 1, 0, -H0), fill=WOOD['out'])
    d.polygon(quad(theta, HW - 0.2, 0, -H0, L0, L1 - 1), fill=WOOD['mid'])
    q = quad(theta, HW - 0.5, 0, -H0, L0, L1 - 1)
    d.line([q[0], q[1]], fill=WOOD['lit'], width=1)
    d.line([q[2], q[3]], fill=WOOD['dark'], width=1)
    # ponteira de ferro
    d.polygon(quad(theta, HW + 1, 0, -H0, L1 - 5, L1), fill=(70, 72, 84))
    d.polygon(quad(theta, HW - 0.4, 0, -H0, L1 - 4, L1 - 1), fill=(150, 156, 170))
    # poste central (toco)
    cy = CY - 2
    d.ellipse([CX - 11, cy - 9 + 4, CX + 11, cy + 9 + 4], fill=WOOD['out'])
    d.rectangle([CX - 10, cy - 4, CX + 10, cy + 4], fill=WOOD['dark'])
    d.ellipse([CX - 11, cy - 13, CX + 11, cy + 5], fill=WOOD['out'])
    d.ellipse([CX - 10, cy - 12, CX + 10, cy + 4], fill=WOOD['cap'])
    d.ellipse([CX - 7, cy - 9, CX + 7, cy + 1], outline=WOOD['mid'])
    d.ellipse([CX - 4, cy - 6, CX + 4, cy - 2], outline=WOOD['mid'])
    d.rectangle([CX - 1, cy - 5, CX + 1, cy - 3], fill=(80, 80, 96))
    return np.asarray(pil).copy()


# ================================================================ estouro
def burst_state():
    rr = random.Random(SEED * 13)
    last = FR[-1]
    sheep = []
    for i, (p, v) in enumerate(zip(last['pos'], last['vel'])):
        rel = p - np.array([CX, CY])
        d = np.hypot(*rel) + 1e-6
        nr = rel / d
        sp = rr.uniform(150, 320) * (0.6 + 0.4 * d / R)
        vv = nr * sp + v * 0.25 + np.array([rr.uniform(-30, 30), rr.uniform(-30, 30)])
        sheep.append((p.copy(), vv, rr.uniform(0, 6.28), rr.uniform(9, 14)))
    debris = []
    for i in range(NP):
        phi = 2 * math.pi * i / NP
        (g, tp) = post_geom(i, 1.0, B)
        for kind in ('post', 'rail'):
            ph = phi + (math.pi / NP if kind == 'rail' else 0)
            sp = rr.uniform(130, 300)
            debris.append(dict(x=g[0], y=g[1] - (6 if kind == 'post' else 8), vx=math.cos(ph) * sp + rr.uniform(-40, 40),
                               vy=math.sin(ph) * sp + rr.uniform(-40, 40), vz=rr.uniform(110, 260),
                               a0=rr.uniform(0, 6.28), w=rr.uniform(-14, 14), L=12 if kind == 'post' else 15,
                               kind=kind))
    dust = []
    for k in range(70):
        ph = rr.uniform(0, 2 * math.pi)
        dust.append((CX + RF * math.cos(ph), CY + RF * math.sin(ph), math.cos(ph) * rr.uniform(30, 110),
                     math.sin(ph) * rr.uniform(30, 110), rr.uniform(0.5, 1.0)))
    return sheep, debris, dust


BSHEEP, BDEBRIS, BDUST = burst_state()
GRAV = 700.0


def debris_at(dct, dt):
    tl = 2 * dct['vz'] / GRAV                   # tempo até cair no chão
    tt = min(dt, tl)
    x = dct['x'] + dct['vx'] * tt
    y = dct['y'] + dct['vy'] * tt
    z = dct['vz'] * tt - 0.5 * GRAV * tt * tt
    a = dct['a0'] + dct['w'] * tt
    return x, y, z, a, dt >= tl


# ================================================================ quadro
def sim_frame(t):
    k = min(int(round(t * FPS)), len(FR) - 1)
    return FR[k], k


def heading(k, i):
    k0 = max(0, k - 4)
    if i < FR[k0]['n']:
        dv = FR[k]['pos'][i] - FR[k0]['pos'][i]
        if np.hypot(*dv) > 1.0:
            return math.atan2(dv[1], dv[0])
    v = FR[k]['vel'][i]
    return math.atan2(v[1], v[0])


def puffs(img, t, t_lo):
    for ev in EV:
        te = ev[0]
        if te > t or te < t - 0.28 or te < t_lo:
            continue
        p = (t - te) / 0.28
        rad = 3 + 13 * p
        for j in range(7):
            a = j * 2 * math.pi / 7 + te * 5
            x, y = int(ev[2] + rad * math.cos(a)), int(ev[3] + rad * math.sin(a) * 0.8)
            if 0 <= x < CW - 1 and 0 <= y < CH - 1:
                c0 = (255, 255, 255) if p < 0.5 else (236, 232, 220)
                img[y, x] = c0
                if p < 0.6:
                    img[y, x + 1] = c0


def frame_canvas(t):
    img = GROUND.copy()
    theta = OMEGA * t
    reb = t >= T_REB
    pre = t < B
    if pre:
        st, k = sim_frame(t)
        s = strain_at(st['n'])
    else:
        st, k = FR[-1], len(FR) - 1
        s = 1.0
    img8 = np.clip(img, 0, 255).astype(np.uint8)
    # haste (com sombra)
    img8 = draw_rod(img8, theta)
    pil = Image.fromarray(img8)
    d = ImageDraw.Draw(pil)
    if pre:
        draw_fence(d, s, t, 'back')
    elif reb:
        draw_fence(d, 0.0, t, 'back', rebuild_t=t)
    img8 = np.asarray(pil).copy()
    # ovelhas
    if pre:
        order = np.argsort(st['pos'][:, 1])
        born = st['born']
        for i in order:
            x, y = st['pos'][i]
            age = t - born[i] if i > 0 else 9
            sc = 1.0 if age > 0.16 else 0.55 + (0.45 * age / 0.16)
            leg = int(t * 8 + i) % 2
            draw_sheep(img8, x, y, heading(k, i), i in BLACK, leg, sc)
        puffs(img8, t, 0)
    else:
        dt = t - B
        items = []
        for i, (p, v, ph, hop) in enumerate(BSHEEP):
            x, y = p + v * dt
            if -20 < x < CW + 20 and -20 < y < CH + 20:
                items.append((y, x, i, v, ph, hop))
        for y, x, i, v, ph, hop in sorted(items):
            z = abs(math.sin(dt * hop + ph)) * 4
            draw_sheep(img8, x, y, math.atan2(v[1], v[0]), i in BLACK, int(dt * 14 + i) % 2, 1.0, z)
        if t >= T_SHEEP0:
            p0 = FR[0]['pos'][0]
            age = t - T_SHEEP0
            sc = 0.55 + 0.45 * min(1, age / 0.16)
            draw_sheep(img8, p0[0], p0[1], heading(0, 0), False, 0, sc)
            if age < 0.28:
                q = age / 0.28
                for j in range(7):
                    a = j * 2 * math.pi / 7
                    x, y = int(p0[0] + (3 + 13 * q) * math.cos(a)), int(p0[1] + (3 + 13 * q) * math.sin(a) * 0.8)
                    img8[y, x] = (255, 255, 255)
    pil = Image.fromarray(img8)
    d = ImageDraw.Draw(pil, 'RGBA')
    if pre:
        draw_fence(d, s, t, 'front')
        # lascas soltando quando está quase estourando
        if s > 0.7:
            rr = random.Random(int(t * FPS))
            for _ in range(int((s - 0.7) * 20)):
                i = rr.randrange(NP)
                (g, tp) = post_geom(i, s, t)
                d.point([(tp[0] + rr.uniform(-4, 4), tp[1] + rr.uniform(-2, 8))], fill=(236, 210, 160))
    elif reb:
        draw_fence(d, 0.0, t, 'front', rebuild_t=t)
    if not pre and not reb:
        dt = t - B
        # pedaços da cerca voando
        for dc in BDEBRIS:
            x, y, z, a, landed = debris_at(dc, dt)
            if landed and dt > 2.4:
                continue
            L = dc['L']
            hx, hy = math.cos(a) * L / 2, math.sin(a) * L / 2 * 0.6
            sy = y - z
            if z > 1:
                d.line([(x - hx * 0.8, y - hy * 0.3 + 2), (x + hx * 0.8, y + hy * 0.3 + 2)], fill=(0, 0, 0, 50), width=3)
            d.line([(x - hx, sy - hy), (x + hx, sy + hy)], fill=WOOD['out'], width=4 if dc['kind'] == 'post' else 3)
            d.line([(x - hx, sy - hy), (x + hx, sy + hy)], fill=WOOD['mid'], width=2 if dc['kind'] == 'post' else 1)
        # poeira
        if dt < 1.2:
            for (x0, y0, vx, vy, life) in BDUST:
                q = dt / life
                if q >= 1:
                    continue
                x, y = x0 + vx * dt, y0 + vy * dt - 6
                rad = 2 + 7 * q
                al = int(170 * (1 - q))
                d.ellipse([x - rad, y - rad * 0.8, x + rad, y + rad * 0.8], fill=(222, 200, 160, al))
    img8 = np.asarray(pil).copy()
    draw_folk(img8, t)
    return img8, s


# ---------------------------------------------------------------- textos
def tag(d, cx, top, nm, rl):
    f1, f2 = 54, 36
    w = max(E.font(f1).getlength(nm), E.font(f2).getlength(rl)) + 44
    E.panel(d, (cx - w / 2, top, cx + w / 2, top + 104), b=5)
    E.draw_line(d, cx, top + 14, [(nm, GOLD)], f1, stroke=5)
    E.draw_line(d, cx, top + 66, [(rl, WHITE)], f2, stroke=4)


def overlay(im, t, s):
    d = ImageDraw.Draw(im, 'RGBA')
    if t < B or t >= T_REB:
        E.draw_line(d, FW / 2, 70, [('SERÁ QUE A CERCA', WHITE)], 128)
        E.draw_line(d, FW / 2, 196, [('AGUENTA?', GOLD)], 200, stroke=12)
        if t < B:
            n = sim_frame(t)[0]['n']
            show = True
        else:
            n = 1
            show = t >= T_SHEEP0
        if show:
            hot = t < B and t > B - 4.0
            col = WHITE if s < 0.5 else (GOLD if s < 0.8 else RED)
            jx = (math.sin(t * 61) * 6) if hot else 0
            word = 'OVELHA' if n == 1 else 'OVELHAS'
            E.draw_line(d, FW / 2 + jx, 410, [(f'{n} ', col), (word, WHITE)], 118)
        if t < 4.2 or t >= T_SHEEP0:
            E.draw_line(d, FW / 2, 548, [('A HASTE PRENSOU, ', WHITE), ('VIROU DUAS', TEAL)], 56, stroke=5)
        if t < 3.6:
            tag(d, 150, 1500, 'VALDEMIR', 'VAQUEIRO')
    elif t < T_CTA:
        q = min(1.0, (t - B) / 0.12)
        E.draw_line(d, FW / 2, 70, [('A CERCA', WHITE)], 128)
        E.draw_line(d, FW / 2, 196, [('ESTOUROU!', RED)], int(150 + 60 * q), stroke=12)
        if t > B + 0.45:
            E.draw_line(d, FW / 2, 410, [('COM ', WHITE), (f'{NFIN} OVELHAS', GOLD)], 118)
    else:
        E.draw_line(d, FW / 2, 70, [('QUANTAS A CERCA', WHITE)], 128)
        E.draw_line(d, FW / 2, 196, [('NOVA AGUENTA?', GOLD)], 170, stroke=12)
        E.draw_line(d, FW / 2, 410, [('CHUTA AÍ NOS COMENTÁRIOS', WHITE)], 84)


VIG = None


def _vig():
    yv, xv = np.mgrid[0:CH, 0:CW]
    r = np.hypot((xv - CX) / 200, (yv - 330) / 360)
    return np.clip((r - 0.7) / 0.6, 0, 1).astype(np.float32)


VIG = _vig()


def heart_level(t):
    """pulso vermelho nos últimos 4 s antes do estouro (sincronizado com o coração)."""
    if not (B - 4.0 <= t < B):
        return 0.0
    for tb in BEATS:
        if tb <= t < tb + 0.35:
            return (1 - (t - tb) / 0.35) * (0.35 + 0.4 * (t - (B - 4)) / 4)
    return 0.0


def make_beats():
    bt, tb = [], B - 4.0
    while tb < B - 0.15:
        bt.append(tb)
        q = (tb - (B - 4.0)) / 4.0
        tb += 0.78 - 0.38 * q
    return bt


BEATS = make_beats()


def frame(t):
    c, s = frame_canvas(t)
    c = c.astype(np.float32)
    hl = heart_level(t)
    if hl > 0:
        c = c * (1 - VIG[..., None] * hl * 0.8) + np.array([150, 10, 20], np.float32) * VIG[..., None] * hl * 0.8
    if B <= t < B + 0.12:
        c = c + (255 - c) * (1 - (t - B) / 0.12) * 0.75
    c8 = np.clip(c, 0, 255).astype(np.uint8)
    f = c8.repeat(S, 0).repeat(S, 1)
    if B <= t < B + 0.6:
        amp = (1 - (t - B) / 0.6) * 18
        dx, dy = int(math.sin(t * 90) * amp), int(math.cos(t * 77) * amp)
        f = np.roll(f, (dy, dx), (0, 1))
    elif t < B and s > 0.8:
        amp = (s - 0.8) / 0.2 * 4
        f = np.roll(f, (int(math.sin(t * 70) * amp), int(math.cos(t * 83) * amp)), (0, 1))
    im = Image.fromarray(f)
    overlay(im, t, s)
    return np.asarray(im)


# ================================================================ áudio
SR = E.SR
CHORDS = [(62, 66, 69), (57, 61, 64), (59, 62, 66), (55, 59, 62)]   # D A Bm G


def wood_hit(n, fres, dec):
    tt = np.arange(n) / SR
    return np.sin(2 * math.pi * fres * tt) * np.exp(-tt / dec)


def bleat(f0, dur, seed):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    rr = random.Random(seed)
    trem = 24 + rr.uniform(-3, 3)
    f = f0 * (1 + 0.1 * np.exp(-tt * 7)) * (1 + 0.035 * np.sin(2 * math.pi * trem * tt))
    ph = np.cumsum(f) / SR
    sig = 0.55 * (2 * (ph % 1) - 1) + 0.45 * np.sin(2 * math.pi * ph * 2.6)
    env = E.adsr(n, a=0.025, dec=0.2, sus=0.75, r=0.1) * (0.65 + 0.35 * np.sin(2 * math.pi * trem * tt))
    return E.lp(sig * env, 0.22)


def creak(dur, rate0, rate1, fres, seed):
    n = int(dur * SR)
    rr = np.random.default_rng(seed)
    train = np.zeros(n)
    t = 0.0
    while t < dur:
        q = t / dur
        rate = rate0 + (rate1 - rate0) * q
        i = int(t * SR)
        if i < n:
            train[i] = rr.uniform(0.4, 1.0)
        t += 1.0 / rate * rr.uniform(0.85, 1.15)
    ker = wood_hit(int(0.03 * SR), fres, 0.005)
    sig = np.convolve(train, ker)[:n]
    env = np.sin(np.linspace(0, math.pi, n)) ** 0.7
    return sig * env


def audio(path):
    total = END + 0.2
    n = int(total * SR)
    s = np.zeros(n)
    rr = random.Random(SEED)
    # ambiente: vento leve e passarinhos
    s += E.lp(E.noise(n, 3), 0.02) * 0.05
    t = 0.6
    while t < total - 0.5:
        nn = int(0.09 * SR)
        tt = np.arange(nn) / SR
        f0 = rr.uniform(3200, 4200)
        ch = np.sin(2 * math.pi * np.cumsum(f0 + 900 * np.sin(2 * math.pi * 14 * tt)) / SR) * np.hanning(nn)
        for k in range(rr.randint(2, 3)):
            E.add(s, t + k * 0.11, ch, 0.025)
        t += rr.uniform(1.6, 3.2)
    # blip a cada ovelha nova
    last = -1
    for j, ev in enumerate(EV):
        te, nn_ = ev[0], ev[4]
        if te - last < 0.035:
            continue
        last = te
        ch = CHORDS[int(te / 2.0) % 4]
        oc = 12 + 12 * min(2, int(strain_at(nn_) * 2.6))
        f = E.midi(ch[j % 3] + oc)
        nb = int(0.075 * SR)
        sig = E.tri(f, nb) * 0.8 + E.sq(f * 2, nb, 0.25) * 0.12
        E.add(s, te, sig * E.adsr(nb, a=0.002, dec=0.03, sus=0.3, r=0.02), 0.22)
    # balidos: os primeiros e alguns depois
    bleat_ts = [ev[0] for ev in EV if ev[4] in (2, 3, 5, 9, 17)]
    t = 6.0
    while t < B - 0.5:
        bleat_ts.append(t)
        t += rr.uniform(0.7, 1.5)
    for k, tb in enumerate(bleat_ts):
        E.add(s, tb + 0.03, bleat(rr.uniform(330, 470), rr.uniform(0.32, 0.5), k), 0.15 if tb < 6 else 0.07)
    # rangido da cerca, cada vez mais frequente
    t = 0.0
    while t < B:
        st = strain_at(sim_frame(t)[0]['n'])
        if st > 0.38:
            q = (st - 0.38) / 0.62
            dur = rr.uniform(0.25, 0.55)
            E.add(s, t, creak(dur, 25 + 25 * q, 45 + 45 * q, rr.uniform(380, 700), int(t * 100)), 0.18 + 0.4 * q)
            t += rr.uniform(1.4, 2.0) * (1 - 0.75 * q)
        else:
            t += 0.25
    # coração nos últimos 4 s
    for tb in BEATS:
        for off, g in ((0.0, 0.55), (0.13, 0.35)):
            nn = int(0.14 * SR)
            tt = np.arange(nn) / SR
            E.add(s, tb + off, np.sin(2 * math.pi * np.cumsum(70 * np.exp(-tt * 9) + 38) / SR) * np.exp(-tt * 22), g)
    # ESTOURO
    nn = int(1.0 * SR)
    tt = np.arange(nn) / SR
    crash = E.lp(E.noise(nn, 77), 0.25) * np.exp(-tt / 0.22)
    boom = np.sin(2 * math.pi * np.cumsum(80 * np.exp(-tt * 5) + 30) / SR) * np.exp(-tt / 0.35)
    E.add(s, B, crash, 1.1)
    E.add(s, B, boom, 0.9)
    for k in range(26):
        E.add(s, B + rr.uniform(0.0, 0.35), wood_hit(int(0.06 * SR), rr.uniform(500, 1100), 0.012), rr.uniform(0.15, 0.35))
    for dc in BDEBRIS:
        tl = 2 * dc['vz'] / GRAV
        if rr.random() < 0.5:
            E.add(s, B + tl, wood_hit(int(0.05 * SR), rr.uniform(300, 700), 0.01), 0.12)
    for k in range(9):
        E.add(s, B + 0.15 + rr.uniform(0, 1.1), bleat(rr.uniform(320, 520), rr.uniform(0.3, 0.5), 100 + k), 0.09)
    # fanfarra 8-bit
    tf = B + 0.5
    for k, m in enumerate((74, 78, 81, 86)):
        nb = int(0.1 * SR)
        E.add(s, tf + k * 0.09, E.sq(E.midi(m), nb, 0.5) * E.adsr(nb, a=0.002, dec=0.04, sus=0.6, r=0.02), 0.1)
    nb = int(0.6 * SR)
    for m in (74, 78, 81):
        E.add(s, tf + 0.36, E.sq(E.midi(m + 12), nb, 0.25, vib=0.01) * E.adsr(nb, a=0.004, dec=0.2, sus=0.5, r=0.2), 0.05)
    # martelo refazendo a cerca
    for k in range(6):
        E.add(s, T_REB + 0.08 + k * 0.1, wood_hit(int(0.05 * SR), 880 if k % 2 else 760, 0.008), 0.3)
    s = s / (np.abs(s).max() + 1e-9) * 0.85
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


# ================================================================ capa
def capa():
    t = B - 1.2
    c, s = frame_canvas(t)
    f = c.repeat(S, 0).repeat(S, 1)
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 560, FW, 1300), fill=(16, 12, 30, 120))
    E.draw_line(d, FW / 2, 640, [('SERÁ QUE A', WHITE)], 150)
    E.draw_line(d, FW / 2, 810, [('CERCA', GOLD)], 290, stroke=16)
    E.draw_line(d, FW / 2, 1080, [('AGUENTA?', WHITE)], 170, stroke=12)
    out = os.path.join(OUTDIR, 'capa-cercado.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


if __name__ == '__main__':
    if os.environ.get('PLAN'):
        print(f'seed {SEED}: 1ª ovelha nova {EV[0][0]:.2f}s · estoura {B:.2f}s com {NFIN} · fim {END:.2f}s')
        print('n por segundo:', [f['n'] for f in FR[::30]])
        raise SystemExit
    if os.environ.get('CAPA'):
        capa()
        raise SystemExit
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            tv = B + float(v[1:]) if v.startswith('b') else float(v)
            Image.fromarray(frame(tv)).save(os.path.join(OUTDIR, os.environ.get('PFX', 'still') + f'_{v}.png'))
        print('ok')
        raise SystemExit
    wav = os.path.join(OUTDIR, 'cercado.wav')
    audio(wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k',
                          '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    for i in range(int(round(END * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(OUT, f'{END:.2f}s')
