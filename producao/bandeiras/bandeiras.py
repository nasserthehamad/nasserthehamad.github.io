#!/usr/bin/env python3
"""Eliminatória das bandeiras: 32 países em bolinhas quicando num cercado redondo com uma porteira larga girando.
Quem sai pela porteira é eliminado. A física não sabe de país nenhum: os países são distribuídos depois — a bolinha que
sobra vira o Brasil e a vice vira a Argentina (final Brasil x Argentina, pedido do Nasser). Música: "Na Gruta do Rei da
Montanha" (Grieg, domínio público) acelerando até a final. Sem narração.
Uso: python3 bandeiras.py   (PLAN=1 · STILLS=0.5,8,b-2,b+0.6 · CAPA=1)"""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REINO = os.environ.get('REINO', '/home/claude/reino')
sys.path.insert(0, REINO)
import ep1hd as E
import folk as F
import world2 as W
import flags as FL
from sim_flags import simulate, CX, CY, R, RB

FW, FH, FPS, S = 1080, 1920, 30, 3
CW, CH = 360, 640
SEED = int(os.environ.get('SEED', '119'))
PARAMS = dict(speed=185.0, gap_deg=52.0)
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.environ.get('OUT', os.path.join(OUTDIR, 'bandeiras.mp4'))
WHITE, GOLD, TEAL, RED, GREEN, YEL = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 96, 86), (90, 220, 110), (254, 223, 0)

SIM = simulate(n=32, seed=SEED, tmax=40, **PARAMS)
FR = SIM['frames']
T_WIN = SIM['end']
ELIMS = SIM['elims']
END = T_WIN + 3.6
T_BACK = END - 0.6

# ---------------------------------------------------------------- quem é quem (distribuído depois da física)
names = [c[0] for c in FL.COUNTRIES]
NB = len(FR[0]['pos'])
order_out = [i for _, i in ELIMS]                 # ordem de eliminação (índice da bolinha)
WIN = SIM['winner']
RUNNER = order_out[-1]
rr0 = random.Random(SEED * 101)
pool = [k for k in range(len(names)) if names[k] not in ('BRASIL', 'ARGENTINA')]
rr0.shuffle(pool)
COUNTRY = {WIN: names.index('BRASIL'), RUNNER: names.index('ARGENTINA')}
# semifinal com gente grande: 3º e 4º lugar França e Portugal
for idx, nm in ((order_out[-2], 'FRANÇA'), (order_out[-3], 'PORTUGAL')):
    COUNTRY[idx] = names.index(nm)
    pool.remove(names.index(nm))
for i in range(NB):
    if i not in COUNTRY:
        COUNTRY[i] = pool.pop()
BALL = {i: FL.ball(FL.COUNTRIES[COUNTRY[i]][1]()) for i in range(NB)}
OUT_T = {i: t for t, i in ELIMS}

yy, xx = np.mgrid[0:CH, 0:CW]
BAY = np.tile(W.BAYER, (CH // 4, CW // 4))


def sim_frame(t):
    k = min(int(round(min(t, T_WIN) * FPS)), len(FR) - 1)
    return FR[k], k


# ================================================================ chão: gramado com a areia da arena
def build_ground():
    g = np.zeros((CH, CW, 3), np.float32)
    gn = W.vnoise(CH, CW, 30, 11, 3)
    lvl = np.clip(np.floor(gn * 3.2 + (BAY - 0.5) * 0.8 - 0.1), 0, 2).astype(int)
    g[:] = W.GREENS[lvl]
    r = np.hypot(xx - CX, yy - CY)
    inside = r < R + 3
    dl = np.clip(np.floor(W.vnoise(CH, CW, 12, 5, 2) * 3.3 + (BAY - 0.5) * 0.9 - 0.15), 0, 2).astype(int)
    sand = np.array([(196, 160, 104), (214, 180, 122), (228, 198, 142)], np.float32)
    g[inside] = sand[dl[inside]]
    lines = inside & (np.abs(r - 60) < 0.8)
    g[lines] = g[lines] * 1.12
    g[inside & (np.abs(xx - CX) < 0.6)] *= 1.08
    rr = random.Random(5)

    def put(x, y, c):
        if 0 <= x < CW and 0 <= y < CH:
            g[y, x] = c
    for _ in range(2200):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < R + 8:
            continue
        c0 = (88, 144, 64) if rr.random() < 0.7 else (78, 132, 58)
        put(x, y, c0); put(x + 1, y - 1, c0); put(x + 2, y, c0)
    for _ in range(140):
        x, y = rr.randrange(CW), rr.randrange(CH)
        if math.hypot(x - CX, y - CY) < R + 12:
            continue
        c0 = rr.choice(W.FLOWER)
        put(x, y, c0); put(x - 1, y, W.shade(c0, 0.85)); put(x + 1, y, W.shade(c0, 0.85)); put(x, y, (255, 240, 170))
    sh = (r > R + 2) & (r < R + 7)
    g[sh] *= 0.74
    vg = np.clip((np.hypot((xx - CX) / 230, (yy - 340) / 400) - 0.75) * 0.9, 0, 0.35)
    g *= (1 - vg)[..., None]
    g[:210] *= np.linspace(0.72, 1.0, 210)[:, None, None]
    return g


GROUND = build_ground()


def draw_ring(d, gc):
    g = SIM['g']
    n = 120
    pts = [(CX + R * math.cos(gc + g + (2 * math.pi - 2 * g) * j / n), CY + R * math.sin(gc + g + (2 * math.pi - 2 * g) * j / n))
           for j in range(n + 1)]
    d.line([(x + 1, y + 2) for x, y in pts], fill=(30, 20, 14, 90), width=4)
    d.line(pts, fill=(70, 44, 26, 255), width=6)
    d.line([(x, y - 3) for x, y in pts], fill=(40, 26, 20, 255), width=5)
    d.line([(x, y - 3) for x, y in pts], fill=(176, 122, 70, 255), width=3)
    d.line([(x, y - 4) for x, y in pts[::2]], fill=(214, 168, 108, 255), width=1)
    for j in range(0, n + 1, 6):
        x, y = pts[j]
        d.rectangle([x - 1.5, y - 8, x + 1.5, y + 1], fill=(48, 30, 22, 255))
        d.point([(x, y - 8)], fill=(214, 168, 108, 255))
    for sgn in (-1, 1):                                   # mourões da porteira, vermelhos
        a = gc + sgn * g
        x, y = CX + R * math.cos(a), CY + R * math.sin(a)
        d.rectangle([x - 3, y - 12, x + 3, y + 2], fill=(40, 20, 20, 255))
        d.rectangle([x - 2, y - 12, x + 2, y + 1], fill=(214, 60, 52, 255))
        d.rectangle([x - 2, y - 12, x + 2, y - 10], fill=(255, 220, 120, 255))


# ================================================================ bolinhas
SHAD = (((np.mgrid[0:10, 0:24][1] - 11.5) / 11.0) ** 2 + ((np.mgrid[0:10, 0:24][0] - 4.5) / 4.0) ** 2) <= 1


def _clip(m, x0, y0):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(CW, x0 + w), min(CH, y0 + h)
    if xa >= xb or ya >= yb:
        return None
    return xa, ya, xb, yb, m[ya - y0:yb - y0, xa - x0:xb - x0]


def draw_ball(img, i, x, y, sc=1.0, shadow=True):
    rgb, m = BALL[i]
    if sc != 1.0:
        n = max(3, int(round(22 * sc)))
        idx = np.clip((np.arange(n) * 22 / n).astype(int), 0, 21)
        rgb, m = rgb[idx][:, idx], m[idx][:, idx]
    h = m.shape[0]
    xi, yi = int(round(x)), int(round(y))
    if shadow:
        cl = _clip(SHAD, xi - 12 + 2, yi - 5 + h // 2)
        if cl:
            xa, ya, xb, yb, mm = cl
            reg = img[ya:yb, xa:xb]; reg[mm] = (reg[mm] * 0.72).astype(img.dtype)
    x0, y0 = xi - h // 2, yi - h // 2
    cl = _clip(m, x0, y0)
    if cl:
        xa, ya, xb, yb, mm = cl
        img[ya:yb, xa:xb][mm] = rgb[ya - y0:yb - y0, xa - x0:xb - x0][mm]


# ================================================================ moradores na torcida
FOLK = [('Valdemir', 'vaqueiro', 40, 600), ('Luiza', 'santa', 26, 248), ('pixoto', 'cidadão', 330, 242),
        ('Edilson', 'espadachim', 322, 602)]
FOLK_SPR = {}
for _n, _r, _, _ in FOLK:
    _a = F.folk(_n, _r, 0)
    FOLK_SPR[_n] = (_a[..., :3].astype(np.uint8), _a[..., 3] > 0.5)


def draw_folk(img, t):
    for i, (nm, rl, fx, fy) in enumerate(FOLK):
        rgb, m = FOLK_SPR[nm]
        jump = int(round(abs(math.sin((t - T_WIN) * 9 + i)) * 7)) if T_WIN <= t < T_WIN + 2.0 else 0
        cl = _clip(m, fx - 15, fy - 42 - jump)
        if cl:
            xa, ya, xb, yb, mm = cl
            img[ya:yb, xa:xb][mm] = rgb[ya - (fy - 42 - jump):yb - (fy - 42 - jump), xa - (fx - 15):xb - (fx - 15)][mm]
        if T_WIN + 0.05 <= t < T_WIN + 2.0:
            W.qmark(img, fx - 3, fy - 50 - jump, bang=True)


# ================================================================ quadro
def out_pos(i, t):
    """bolinha eliminada: continua rolando pra fora e cai (encolhe)."""
    te = OUT_T[i]
    k = min(int(round(te * FPS)), len(FR) - 1)
    p, v = FR[k]['pos'][i], FR[k]['vel'][i]
    dt = t - te
    return p + v * dt * 0.8, max(0.0, 1 - dt / 0.7)


CONF = [(random.Random(k).uniform(0, CW), random.Random(k + 99).uniform(-40, 0), random.Random(k + 7).uniform(40, 120),
         random.Random(k + 3).choice([(0, 156, 59), (254, 223, 0), (0, 39, 118), (255, 255, 255)])) for k in range(160)]


def frame_canvas(t):
    img8 = np.clip(GROUND, 0, 255).astype(np.uint8)
    st, k = sim_frame(t)
    gc = st['gap'] if t < T_WIN else FR[-1]['gap']
    if t >= T_BACK:
        gc = FR[0]['gap']
    pil = Image.fromarray(img8)
    draw_ring(ImageDraw.Draw(pil, 'RGBA'), gc)
    img8 = np.asarray(pil).copy()
    if t < T_WIN:
        items = []
        for i in range(NB):
            if st['alive'][i]:
                x, y = st['pos'][i]
                items.append((y, i, x, y, 1.0))
            elif i in OUT_T and t - OUT_T[i] < 0.7:
                p, sc = out_pos(i, t)
                items.append((p[1], i, p[0], p[1], sc))
        for _, i, x, y, sc in sorted(items):
            draw_ball(img8, i, x, y, sc, shadow=sc > 0.9)
    elif t < T_BACK:
        dt = t - T_WIN
        if RUNNER in OUT_T and t - OUT_T[RUNNER] < 0.7:
            p, sc = out_pos(RUNNER, t)
            draw_ball(img8, RUNNER, p[0], p[1], sc, shadow=False)
        p = FR[-1]['pos'][WIN]
        q = min(1.0, dt / 0.6)
        q = 1 - (1 - q) ** 3
        x = p[0] + (CX - p[0]) * q
        y = p[1] + (CY - p[1]) * q
        draw_ball(img8, WIN, x, y, 1.0 + 2.6 * q)
        for (cx, cy, sp, col) in CONF:                     # confete verde e amarelo
            yc = cy + sp * dt * 1.4
            xc = cx + 6 * math.sin(dt * 5 + cx)
            if 0 <= yc < CH - 1 and 0 <= xc < CW - 1:
                img8[int(yc), int(xc)] = col
                img8[int(yc) + 1, int(xc)] = col
    else:                                                 # todo mundo volta pro começo
        q = min(1.0, (t - T_BACK) / 0.35)
        for i in range(NB):
            x, y = FR[0]['pos'][i]
            draw_ball(img8, i, x, y, 0.4 + 0.6 * q)
    draw_folk(img8, t)
    return img8


# ---------------------------------------------------------------- textos
def name(i):
    return FL.COUNTRIES[COUNTRY[i]][0]


def overlay(im, t):
    d = ImageDraw.Draw(im, 'RGBA')
    st, _ = sim_frame(t)
    left = int(st['alive'].sum()) if t < T_WIN else 1
    if t >= T_BACK:
        left = NB
    if t < T_WIN or t >= T_BACK:
        E.draw_line(d, FW / 2, 64, [('QUAL PAÍS', WHITE)], 140)
        E.draw_line(d, FW / 2, 200, [('SOBREVIVE?', GOLD)], 190, stroke=12)
        if left > 2:
            E.draw_line(d, FW / 2, 420, [('RESTAM ', WHITE), (f'{left}', GOLD)], 110, stroke=8)
            last = [(te, i) for te, i in ELIMS if te <= t and t - te < 0.9]
            if last and t < T_BACK:
                te, i = last[-1]
                E.draw_line(d, FW / 2, 548, [('TCHAU, ', WHITE), (name(i), RED)], 66, stroke=6)
        else:
            hot = math.sin(t * 8) > 0
            E.draw_line(d, FW / 2, 400, [('FINAL', RED if hot else GOLD)], 120, stroke=10)
            E.draw_line(d, FW / 2, 535, [('BRASIL', YEL), (' x ', WHITE), ('ARGENTINA', (140, 196, 240))], 92, stroke=8)
    else:
        q = min(1.0, (t - T_WIN) / 0.15)
        E.draw_line(d, FW / 2, 90, [('CAMPEÃO!', GOLD)], int(150 + 60 * q), stroke=14)
        if t > T_WIN + 0.35:
            E.draw_line(d, FW / 2, 330, [('BRASIL', YEL)], 200, stroke=14)


VIG = np.clip((np.hypot((xx - CX) / 200, (yy - 330) / 360) - 0.7) / 0.6, 0, 1).astype(np.float32)
T_DUEL = ELIMS[-2][0]


def make_beats():
    bt, tb = [], T_DUEL
    while tb < T_WIN - 0.15:
        bt.append(tb)
        tb += 0.75 - 0.35 * (tb - T_DUEL) / max(0.1, T_WIN - T_DUEL)
    return bt


BEATS = make_beats()


def heart_level(t):
    if not (T_DUEL <= t < T_WIN):
        return 0.0
    for tb in BEATS:
        if tb <= t < tb + 0.35:
            return (1 - (t - tb) / 0.35) * 0.55
    return 0.0


def frame(t):
    c = frame_canvas(t).astype(np.float32)
    hl = heart_level(t)
    if hl > 0:
        c = c * (1 - VIG[..., None] * hl * 0.8) + np.array([150, 10, 20], np.float32) * VIG[..., None] * hl * 0.8
    if T_WIN <= t < T_WIN + 0.12:
        c = c + (255 - c) * (1 - (t - T_WIN) / 0.12) * 0.7
    f = np.clip(c, 0, 255).astype(np.uint8).repeat(S, 0).repeat(S, 1)
    im = Image.fromarray(f)
    overlay(im, t)
    return np.asarray(im)


# ================================================================ áudio
SR = E.SR
_P1 = [59, 61, 62, 64, 66, 62, 66, None, 65, 61, 65, None, 64, 60, 64, None,
       59, 61, 62, 64, 66, 62, 66, 71, 69, 66, 62, 66, 69, None, None, None]
_P2 = [66, 68, 70, 71, 73, 70, 73, None, 74, 70, 74, None, 73, 70, 73, None,
       66, 68, 70, 71, 73, 70, 73, None, 74, 70, 74, None, 73, None, None, None]
MOUNTAIN = (_P1 + _P2) * 6


def pluck(m, dur=0.3):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    sig = np.sin(2 * math.pi * f * tt) + 0.5 * np.sin(4 * math.pi * f * tt) + 0.22 * np.sin(6 * math.pi * f * tt)
    return sig * np.minimum(1, tt / 0.005) * np.exp(-tt * 7)


def bass(m, dur=0.4):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 440 * 2 ** ((m - 69) / 12)
    return (np.sin(2 * math.pi * f * tt) + 0.3 * np.sin(4 * math.pi * f * tt)) * np.exp(-tt * 6)


def audio(path):
    total = END + 0.2
    n = int(total * SR)
    s = np.zeros(n)
    rr = random.Random(SEED)
    # "Na Gruta do Rei da Montanha" acelerando até a final
    t, j = 0.15, 0
    while t < T_WIN - 0.05:
        q = 0.2 - (0.2 - 0.088) * min(1.0, t / T_DUEL) ** 1.2
        m = MOUNTAIN[j % len(MOUNTAIN)]
        if m is not None:
            E.add(s, t, pluck(m + 12), 0.26)
        if j % 4 == 0:
            E.add(s, t, bass(47 if (j // 32) % 2 == 0 else 42), 0.3)
        t += q
        j += 1
    for tb, i in SIM['bounces']:
        if tb < T_WIN and rr.random() < 0.35:
            nn = int(0.02 * SR)
            E.add(s, tb, np.sin(2 * math.pi * 1300 * np.arange(nn) / SR) * np.exp(-np.arange(nn) / SR * 300), 0.03)
    # eliminado: "plop" descendo + torcida
    for k, (te, i) in enumerate(ELIMS):
        nn = int(0.22 * SR)
        tt = np.arange(nn) / SR
        f = 700 * np.exp(-tt * 6) + 120
        E.add(s, te, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 9), 0.3)
        left = 32 - (k + 1)
        if left <= 4:
            nn = int(0.9 * SR)
            tt = np.arange(nn) / SR
            ooh = E.lp(E.noise(nn, 300 + k), 0.05) * np.sin(math.pi * tt / 0.9)
            E.add(s, te + 0.05, ooh, 1.2)
    for tb in BEATS:
        for off, g in ((0.0, 0.5), (0.13, 0.32)):
            nn = int(0.14 * SR)
            tt = np.arange(nn) / SR
            E.add(s, tb + off, np.sin(2 * math.pi * np.cumsum(70 * np.exp(-tt * 9) + 38) / SR) * np.exp(-tt * 22), g)
    # CAMPEÃO: torcida, fanfarra em Si maior
    nn = int(2.4 * SR)
    tt = np.arange(nn) / SR
    cheer = E.lp(E.noise(nn, 999), 0.09) * np.minimum(1, tt / 0.15) * np.exp(-tt * 0.9)
    E.add(s, T_WIN, cheer, 1.6)
    for k, m in enumerate((71, 75, 78, 83)):
        nb = int(0.12 * SR)
        E.add(s, T_WIN + 0.2 + k * 0.1, E.sq(E.midi(m), nb, 0.5) * E.adsr(nb, a=0.002, dec=0.04, sus=0.6, r=0.02), 0.11)
    nb = int(0.9 * SR)
    for m in (71, 75, 78):
        E.add(s, T_WIN + 0.6, E.sq(E.midi(m + 12), nb, 0.25, vib=0.01) * E.adsr(nb, a=0.004, dec=0.2, sus=0.5, r=0.3), 0.06)
        E.add(s, T_WIN + 0.6, bass(m - 24, 1.2), 0.2)
    for k in range(NB):
        E.add(s, T_BACK + k * 0.01, pluck(83 + (k % 5) * 2, 0.08), 0.02)
    s = s / (np.abs(s).max() + 1e-9) * 0.85
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


def capa():
    t = T_DUEL + 1.5
    f = frame_canvas(t).repeat(S, 0).repeat(S, 1)
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 0, FW, 700), fill=(16, 12, 30, 120))
    E.draw_line(d, FW / 2, 90, [('QUAL PAÍS', WHITE)], 170)
    E.draw_line(d, FW / 2, 270, [('SOBREVIVE?', GOLD)], 220, stroke=14)
    E.draw_line(d, FW / 2, 540, [('BRASIL', YEL), (' x ', WHITE), ('ARGENTINA', (140, 196, 240))], 96, stroke=8)
    out = os.path.join(OUTDIR, 'capa-bandeiras.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


if __name__ == '__main__':
    if os.environ.get('PLAN'):
        print(f'seed {SEED}: campeão aos {T_WIN:.2f}s; final começa {T_DUEL:.2f}s; fim {END:.2f}s')
        print('ordem de saída:', [name(i) for _, i in ELIMS])
        raise SystemExit
    if os.environ.get('CAPA'):
        capa(); raise SystemExit
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            tv = T_WIN + float(v[1:]) if v.startswith('b') else float(v)
            Image.fromarray(frame(tv)).save(os.path.join(OUTDIR, f'still_{v}.png'))
        print('ok'); raise SystemExit
    wav = os.path.join(OUTDIR, 'bandeiras.wav')
    audio(wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k',
                          '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    for i in range(int(round(END * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(OUT, f'{END:.2f}s')
