#!/usr/bin/env python3
"""Brasa — Ep. 9 "A Capitã" (~20 s, sem voz). Mesma noite e mesmo cenário do Ep. 8 (a vila na beira do rio).
0. (1º quadro) A capa vermelha cai nos ombros da Raviela, com brilho dourado: ela ganhou a Copa de Brasa e virou capitã.
1. "ELA CHAMOU QUEM FOI MAIS LONGE NA COPA:" os 5 que chegaram mais longe saem da multidão, um por um, e ficam do lado
   dela com a medalha da colocação (Izabelle 2º, Lorena 3º, Pixoto 4º, Cubo 5º, Miyuki 6º).
2. O encapuzado na ponte conta quem é "ele": "ELE APAGA REINOS." / "SÓ NÃO ENTRA ONDE TEM 100."
3. O céu fica vermelho de novo: "FALTAM N MORADORES."
4. Final de sempre.
Uso: N=<seguidores> python3 ep9.py   (STILLS=1,5,... · CAPA=1)"""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '89')
import ep8 as X8

W, F, B, E, P, Q, H, G = X8.W, X8.F, X8.B, X8.E, X8.P, X8.Q, X8.H, X8.G
FW, FH, FPS = 1080, 1920, 30
OUTDIR = X8.OUTDIR
WHITE, GOLD, RED = (255, 255, 255), (255, 208, 72), (255, 96, 86)
N_FOLLOW = int(os.environ['N'])
GOAL = 100
FALTAM = max(0, GOAL - N_FOLLOW)
PEOPLE, IDX, NP = X8.PEOPLE, X8.IDX, X8.NP
RAV_I = IDX['Raviela']

# ---------------------------------------------------------------- tempo
T_CAPE = 0.5
S1, S2, S3, EN = 4.0, 9.6, 14.4, 16.4
TEND = EN + 4.4
XF = 0.4
FINAL = [('Izabelle', 2), ('Lorena', 3), ('pixoto', 4), ('cubo', 5), ('Miyuki', 6)]
STEP_T = [S1 + 0.5 + 0.9 * k for k in range(5)]
B1, B2 = S2 + 1.0, S2 + 2.6

# ---------------------------------------------------------------- lugares (ajusta o cenário do Ep. 8)
RAV = (272, 306)
SLOTS = [(250, 309), (229, 311), (208, 313), (187, 315), (166, 317)]
STR = (288, 290)
X8.HORSE = (138, 322)
X8.SPECIAL = {'Cauã': X8.PIER, 'Edilson': (300, 318), 'Raviela': RAV}
if X8.GABI is not None:
    X8.SPECIAL['Gabi'] = (X8.TOWER_X, X8.TOWER_TOP)


def _excluded9(x, y):
    if 48 <= x <= 118 and y < 360:               # forja
        return True
    if 186 <= x <= 226 and y < 300:              # Cauã no píer
        return True
    if 306 <= x <= 340 and y < 342:              # árvore + torre
        return True
    if 156 <= x <= 300 and y < 326:              # fila da cerimônia e pé da ponte
        return True
    if 116 <= x <= 162 and 300 <= y < 334:       # cavalo do Valdemir
        return True
    if 290 <= x <= 312 and y < 330:              # Edilson
        return True
    return False


X8._excluded = _excluded9
X8.POS = X8.crowd8()
POS = X8.POS
# o resto do Ep. 8 fica parado no estado final: fogueira acesa, luzes mágicas no rio, sem flecha, sem travessia
X8.T_SHOT, X8.T_IGN = -999.0, -10.0
X8.C3, X8.C4 = 999.0, -10.0
X8.S2, X8.S3 = 999.0, 999.0
X8.T_STR0, X8.T_CROSS0 = 999.0, 999.0
X8.S4, X8.S5 = S3, EN                             # céu vermelho e "!" na vila
X8.stranger_pos = lambda t: (STR[0], STR[1], 0)


def orbs9(t):
    """as luzes mágicas do Ep. 8, já paradas em cima do rio."""
    r = random.Random(77)
    res = []
    for k in range(15):
        tx, ty = 16 + k * 23 + r.uniform(-6, 6), 283 + r.uniform(-3, 5)
        col = [(140, 255, 230), (200, 150, 255), (255, 230, 140)][k % 3]
        res.append((tx, ty + 1.5 * math.sin(t * 2.2 + k), col, 1.0))
    return res


X8.orbs = orbs9
FIDX = [IDX[n] for n, _ in FINAL]


def person_pos(i, t):
    if i in FIDX:
        k = FIDX.index(i)
        return X8.walk(POS[i], SLOTS[k], STEP_T[k] - 0.6, 0.6, t)
    x, y = POS[i]
    return x, y, 0


X8.person_pos = person_pos


# ---------------------------------------------------------------- câmera
def clamp_shot(x0, y0, s):
    return (int(min(max(0, x0), W.W - FW // s)), int(min(max(0, y0), W.H - FH // s)), s)


def shot(t):
    if t < S1:
        return clamp_shot(RAV[0] - 90, 100, 6)
    if t < S2:
        return clamp_shot(120, 150, 5)
    if t < S3:
        return clamp_shot(180, 130, 6)
    if t < EN:
        return (44, 40, 4)
    return clamp_shot(90, 80, 4)


# ---------------------------------------------------------------- textos
CAPS = [
    (0.0, 1.9, 270, [(0.0, [('NESTE REINO, CADA', WHITE)], 128), (0.0, [('SEGUIDOR VIRA ', WHITE), ('MORADOR.', GOLD)], 128)]),
    (1.9, S1, 270, [(1.9, [('A RAVIELA GANHOU', WHITE)], 136), (1.9, [('A COPA DE BRASA…', GOLD)], 132),
                    (2.6, [('…E VIROU CAPITÃ.', GOLD)], 132)]),
    (S1, S2, 270, [(S1, [('ELA CHAMOU QUEM FOI', WHITE)], 128), (S1 + 0.2, [('MAIS LONGE NA COPA:', GOLD)], 128)]),
    (S1 + 0.3, S2, 1560, [(S1 + 0.3, [('ESTE REINO TEM ', WHITE), (f'{N_FOLLOW}', GOLD), (' MORADORES.', WHITE)], 92)]),
    (S2, B1, 270, [(S2, [('E O ENCAPUZADO', WHITE)], 140), (S2, [('CONTOU QUEM É ELE:', RED)], 128)]),
    (S3 + 0.4, EN, 270, [(S3 + 0.4, [('FALTAM ', WHITE), (f'{FALTAM}', RED)], 170), (S3 + 0.7, [('MORADORES.', WHITE)], 150)]),
    (EN, TEND + 1, 270, [(EN, [('QUEM NÃO SEGUE', WHITE)], 150), (EN + 0.3, [('NÃO MORA NA VILA.', GOLD)], 136)]),
    (EN + 0.9, TEND + 1, 880, [(EN + 0.9, [('COMENTA TEU NOME', WHITE)], 110), (EN + 0.9, [('E TUA FUNÇÃO', GOLD)], 110)]),
]
BUBBLES = [(B1, B2, 'ELE APAGA REINOS.'), (B2, S3, 'SÓ NÃO ENTRA ONDE TEM 100.')]
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
            x0, y0, s = shot(S2 + 1.0)
            hx, hy = (STR[0] - x0) * s, (STR[1] - 44 - y0) * s
            fnt = E.font(78 if len(full) < 20 else 66)
            w = fnt.getlength(full) + 70
            bx0 = max(30, min(FW - 30 - w, hx - w / 2))
            bx1 = bx0 + w
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


def medal(d, cx, cy, txt, s=1.0):
    r = 34 * s
    d.ellipse((cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5), fill=(60, 30, 20, 255))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 196, 60, 255))
    d.ellipse((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), fill=(255, 220, 110, 255))
    d.text((cx, cy + 2), txt, font=E.font(int(44 * s)), fill=(110, 50, 20, 255), anchor='mm')


# ---------------------------------------------------------------- quadro
def falling_cape(c, t):
    q = W.clamp(t / T_CAPE)
    if q >= 1:
        return
    x, y = RAV[0], RAV[1] - 34 - (1 - q) ** 1.6 * 70
    wob = math.sin(t * 22) * 2 * (1 - q)
    for dy in range(14):
        half = 3 + dy * 0.35
        for dx in range(-int(half), int(half) + 1):
            X_, Y_ = int(x + dx + wob * (dy / 14)), int(y + dy)
            if 0 <= X_ < W.W and 0 <= Y_ < W.H:
                shade = 0.7 if dx < -half + 2 else (1.0 if dx < half - 1 else 0.82)
                c[Y_, X_] = np.array((184, 36, 40)) * shade * 0.75


def frame(t):
    PEOPLE[RAV_I] = ('Raviela', 'capitã' if t >= T_CAPE else 'cavaleira')
    sh = shot(t)
    c = X8.village(t)
    falling_cape(c, t)
    if T_CAPE <= t < T_CAPE + 1.3:
        Q.sparkles(c, RAV[0], RAV[1] - 22, T_CAPE, t, dur=1.3)
    for k, (n, place) in enumerate(FINAL):
        if STEP_T[k] <= t < STEP_T[k] + 0.9:
            Q.sparkles(c, SLOTS[k][0], SLOTS[k][1] - 22, STEP_T[k], t, dur=0.9)
    f = P.camera(c, sh)
    if T_CAPE <= t < T_CAPE + 0.35:                 # clarão dourado
        a = 1 - (t - T_CAPE) / 0.35
        f = (f.astype(np.float32) * (1 - 0.55 * a) + np.array((255, 230, 160)) * 0.55 * a).astype(np.uint8)
    if S3 <= t < S3 + 0.6:                          # tremor
        amp = (1 - (t - S3) / 0.6) * 14
        f = np.roll(f, (int(math.sin(t * 90) * amp), int(math.cos(t * 77) * amp)), (0, 1))
    x0, y0, s = sh
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im)
    drew = False
    if 0.7 <= t < S1:
        Q.tag(d, (RAV[0] - x0) * s, (RAV[1] - y0) * s + 26, 'RAVIELA', 'CAPITÃ DA GUARDA')
        drew = True
    if S1 <= t < S2:
        for k, (n, place) in enumerate(FINAL):
            if t >= STEP_T[k]:
                sx, sy = SLOTS[k]
                cx, cy = (sx - x0) * s, (sy - 46 - y0) * s
                if 0 < cx < FW:
                    pop = min(1.0, (t - STEP_T[k]) / 0.15)
                    medal(d, cx, cy, f'{place}', 0.7 + 0.3 * pop)
                    drew = True
                if STEP_T[k] <= t < STEP_T[k] + 0.9 and t < S2:
                    Q.tag(d, cx, (sy - y0) * s + 26, F.shown(n).upper(), f'TOP {place} DA COPA')
        if t < S2:
            cx, cy = (RAV[0] - x0) * s, (RAV[1] - 46 - y0) * s
            medal(d, cx, cy, '1', 1.0)
    if drew or S1 <= t < S2:
        f = np.asarray(im).copy()
    ov = overlay(overlay_state(t))
    if ov:
        (oy0, oy1, ox0, ox1), rgb, a = ov
        reg = f[oy0:oy1, ox0:ox1].astype(np.float32)
        f[oy0:oy1, ox0:ox1] = (reg * (1 - a) + rgb * a).astype(np.uint8)
    return f


# ---------------------------------------------------------------- áudio
SR = E.SR


def sfx(total):
    n = int(total * SR)
    s = np.zeros(n)
    r = random.Random(9)

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

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            blip(max(0, ta), 988)
    # capa caindo: "fuuush" + fanfarra
    nn = int(T_CAPE * SR)
    tt = np.arange(nn) / SR
    E.add(s, 0.0, E.lp(E.noise(nn, 11), 0.25) * np.sin(np.pi * tt / T_CAPE), 0.5)
    for j, m in enumerate([67, 72, 76, 79]):
        nn = int(0.16 * SR)
        E.add(s, T_CAPE + j * 0.08, E.sq(E.midi(m), nn, 0.5) * E.adsr(nn, dec=0.06, sus=0.4), 0.09)
    nn = int(0.9 * SR)
    E.add(s, T_CAPE + 0.32, E.sq(E.midi(84), nn, 0.5) * E.adsr(nn, dec=0.2, sus=0.5, r=0.3), 0.08)
    nn = int(1.4 * SR)
    tt = np.arange(nn) / SR
    E.add(s, T_CAPE, E.lp(E.noise(nn, 12), 0.08) * np.minimum(1, tt / 0.1) * np.exp(-tt * 1.6), 0.6)   # vila comemorando
    # cada finalista: passos + sininho que sobe de tom (6º → 2º) e aplauso curto
    for k, t0 in enumerate(STEP_T):
        for j in range(2):
            thump(t0 - 0.55 + j * 0.25, g=0.16, f0=170, dec=40, ln=0.06)
        chime(t0, [72 + 2 * k, 76 + 2 * k, 79 + 2 * k], g=0.07, step=0.05)
        nn = int(0.6 * SR)
        tt = np.arange(nn) / SR
        E.add(s, t0, (E.noise(nn, 40 + k) - E.lp(E.noise(nn, 40 + k), 0.2)) * (0.6 + 0.4 * np.sin(tt * 90) ** 2) * np.exp(-tt * 4), 0.08)
    # fala estilo RPG + suspense
    for a, b, txt in BUBBLES:
        for j, ch in enumerate(txt):
            if ch != ' ':
                blip(a + j * CHAR_T, 330 if j % 2 else 294, d=0.03, g=0.06, duty=0.25)
    nn = int((S3 - S2) * SR)
    tt = np.arange(nn) / SR
    E.add(s, S2, (np.sin(2 * math.pi * 55 * tt) + 0.5 * np.sin(2 * math.pi * 58.3 * tt)) * np.minimum(1, tt / 0.5), 0.12)
    # "ele"
    nn = int(2.4 * SR)
    tt = np.arange(nn) / SR
    E.add(s, S3, E.lp(E.noise(nn, 21), 0.03) * np.exp(-tt * 1.2), 1.5)
    thump(S3, g=1.0, f0=60, dec=4, ln=1.4)
    for k in range(3):
        thump(S3 + 0.8 + k * 0.6, g=0.5, f0=70, dec=9)
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
    for a_, b_, lvl in ((S2, S3, 0.3), (S3, EN, 0.0)):
        a, b = int(a_ * SR), int(b_ * SR)
        ramp = int(0.3 * SR)
        g[a:b] = lvl
        g[a:a + ramp] = np.linspace(g[a - 1] if a > 0 else 1, lvl, ramp)
        g[b - ramp:b] = np.linspace(lvl, 1 if b_ == EN else lvl, ramp)
    mix = mus * g * 0.85 + sfx(total)
    fo = int(0.3 * SR)
    mix[-fo:] *= np.linspace(1, 0.35, fo)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


# ---------------------------------------------------------------- capa
def capa():
    t = 1.4
    PEOPLE[RAV_I] = ('Raviela', 'capitã')
    sh = shot(t)
    c = X8.village(t)
    f = P.camera(c, sh)
    im = Image.fromarray(f).convert('RGBA')
    d = ImageDraw.Draw(im)
    x0, y0, s = sh
    medal(d, (RAV[0] - x0) * s, (RAV[1] - 48 - y0) * s, '1', 1.3)
    Q.tag(d, (RAV[0] - x0) * s, (RAV[1] - y0) * s + 26, 'RAVIELA', 'CAPITÃ DA GUARDA')
    title = 'EPISÓDIO 9 · A CAPITÃ'
    tw = E.font(78).getlength(title)
    E.panel(d, (540 - tw / 2 - 36, 250, 540 + tw / 2 + 36, 372), b=6)
    E.draw_line(d, 540, 278, [(title, WHITE)], 78)
    E.draw_line(d, 540, 450, [('BRASA', GOLD)], 280, stroke=14)
    E.draw_line(d, 540, 1560, [('ELA GANHOU A COPA', WHITE)], 100)
    E.draw_line(d, 540, 1680, [('E VIROU CAPITÃ', GOLD)], 112)
    out = os.path.join(OUTDIR, 'capa-brasa-ep9.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


def main():
    if os.environ.get('CAPA'):
        capa(); return
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep9_{float(v):05.2f}.png'))
        print('ok', [(n, IDX.get(n)) for n, _ in FINAL])
        return
    wav = os.path.join(OUTDIR, 'ep9.wav')
    audio(wav)
    out = os.path.join(OUTDIR, 'brasa-ep9.mp4')
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
