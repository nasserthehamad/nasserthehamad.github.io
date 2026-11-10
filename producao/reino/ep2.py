#!/usr/bin/env python3
"""Brasa — Ep. 2 "Os Fundadores". Sem narração por padrão (VOICE=arquivo.mp3 + BOUNDS para sincronizar)."""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
import world2 as W
import folk as F
import build as B
import ep1hd as E

HERE = os.path.dirname(os.path.abspath(__file__))
FW, FH, FPS = 1080, 1920, 30
OUTDIR = os.path.join(HERE, 'out')
WHITE, GOLD, GREY, TEAL = (255, 255, 255), (255, 208, 72), (200, 196, 220), (96, 226, 214)
FOUND = F.FOUNDERS
NF = len(FOUND)

# ---------------------------------------------------------------- tempo
S2, S3, S4, S4B, S5, S6, S6B, TEND = 3.0, 9.6, 14.4, 16.8, 19.8, 24.0, 26.0, 28.4
ROLL = 0.6
_b = os.environ.get('BOUNDS')
if _b:
    S2, S3, S4, S4B, S5, S6, S6B = [float(v) for v in _b.split(',')][:7]
    TEND = float(os.environ['TEND'])
    ROLL = (S3 - S2) / NF
XF = 0.4


def tod(t):
    if t < S3:
        return 0.0
    if t < S4:
        return 0.5 * (t - S3) / (S4 - S3)
    if t < S5:
        return 0.95 + 0.6 * (t - S4) / (S5 - S4)
    return 2.0


# ---------------------------------------------------------------- lugares
RING = W.ring_positions(NF)
WORK = {'Gabriel': (118, 358), 'Naty': (250, 404), 'Ana Sofia': (34, 412), 'Raviela': (196, 446), 'Rafael': (206, 292),
        'Emanuel': (110, 482), 'Victor': (296, 470), 'Antônio': (268, 406), 'Izabelly': (150, 322), 'Francini': (284, 404),
        'Cristal': (282, 310)}
BUILDS = [('forja', S3 + 0.35), ('padaria', S3 + 1.05), ('biblio', S3 + 1.75), ('pier', S3 + 2.45), ('horta', S3 + 2.85),
          ('lantern', S3 + 3.25)]
BDUR = 0.6
LABELS = [('forja', 'FORJA DO GABRIEL', None, (250, 888)),
          ('padaria', 'PADARIA', 'Antônio · Francini · Naty', (780, 1000)),
          ('biblio', 'BIBLIOTECA DO EMANUEL', None, (270, 1190)),
          ('pier', 'PÍER DO RAFAEL', None, (640, 800)),
          ('horta', 'HORTA DO VICTOR', None, (800, 1290))]
SPARK_T = [1.25 + 0.12 * k for k in range(NF)]
RAVI = [n for n, _ in FOUND].index('Raviela')
CRIS = [n for n, _ in FOUND].index('Cristal')
BANG_T = S5 + 1.7


def bprog(name, t):
    for n, t0 in BUILDS:
        if n == name:
            return 0.0 if t < t0 else min(1.0, (t - t0) / (BDUR if n not in ('pier', 'horta', 'lantern') else 0.35))
    return 0.0


def people(t):
    """[(i, x, y, frame)] para o instante t."""
    res = []
    for i, (n, r) in enumerate(FOUND):
        if S3 <= t < S4 or (n == 'Cristal' and S5 <= t < S6):
            x, y = WORK[n]
        else:
            x, y = RING[i]
        sh_ = shot(t)
        if sh_[0] == 'close' and sh_[1] == i and t < S3:
            ph_ = (t - S2) - i * ROLL
            if 0 <= ph_ < 0.18:
                y -= 4 * math.sin(math.pi * ph_ / 0.18)
        fr = 0
        if i == RAVI and S4 <= t < S5:
            q = W.clamp((t - S4 - 0.3) / 0.5)
            y += 14 * q
            fr = (1 + int(t / 0.12) % 2) if 0 < q < 1 else 0
        res.append((i, x, y, fr))
    return res


# ---------------------------------------------------------------- cena
_r = random.Random(21)
SHIM = [(_r.randrange(W.W), _r.randrange(280, 295), _r.uniform(10, 22), _r.randint(3, 6)) for _ in range(34)]
FLIES = [(_r.uniform(20, 340), _r.uniform(304, 480), _r.random() * 6.28, _r.uniform(1.5, 3)) for _ in range(22)]
FLAGC = {}
for _r_, _cols in {2: (10,), 3: (9, 10), 4: (9, 10, 11), 5: (8, 9, 10, 11), 6: (8, 9, 10, 11, 12), 7: (7, 8, 9, 10, 11, 12),
                   8: (7, 8, 9, 10, 11, 12), 9: (8, 9, 10, 11)}.items():
    for _c in _cols:
        FLAGC[(_c, _r_)] = (255, 236, 140) if (_r_ >= 6 and 9 <= _c <= 10) else (255, 160, 50)
LANT_C = (B.POS['lantern'][0] + 4, B.POS['lantern'][1] + 4)


def myst_pos(t):
    return (276 + int(round(2 * math.sin(t * 1.3))), 262)


def light_at(cx, cy, R, t):
    fl = math.sin(t * 13) * 1.2
    d = np.sqrt((W.xx - cx) ** 2 + ((W.yy - cy) * 1.9) ** 2)
    L = np.clip(1 - d / (R + fl), 0, 1) ** 0.85
    return (np.floor(L * 6 + W.BAY * 0.999) / 6).astype(np.float32)


def scene(t):
    td = tod(t)
    img = W.LAND.copy()
    for x0, y, sp, ln in SHIM:
        x = int(x0 + t * sp) % W.W
        for k in range(ln):
            xk = (x + k) % W.W
            if not (260 <= xk <= 290 or 196 <= xk <= 215):
                img[y, xk] = (170, 214, 246) if k else (210, 236, 252)
    # bandeira no alto
    for c_ in range(20):
        dy = int(round(math.sin(t * 7 - c_ * 0.45) * 1.4 * min(1, c_ / 6)))
        for r_ in range(12):
            col = FLAGC.get((c_, r_), (178, 46, 42))
            wv = math.sin(t * 7 - c_ * 0.45 + 1.2)
            col = W.shade(col, 1.12) if wv > 0.55 else (W.shade(col, 0.82) if wv < -0.55 else col)
            if r_ in (0, 11):
                col = W.shade(col, 0.78)
            img[318 + r_ + dy, 154 + c_] = col
    # construções (a partir do S3; depois ficam prontas)
    after = t >= S3
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        p = bprog(name, t) if after else 0
        if p > 0:
            B.blit(img, spr, *B.POS[name], p=p, t=t)
    if after:
        pp = bprog('pier', t)
        if pp > 0:
            B.draw_pier(img, p=pp)
        ph = bprog('horta', t)
        if ph > 0:
            B.draw_horta(img, p=ph)
    if bprog('forja', t) >= 1:
        B.smoke_at(img, t, 97, 300, seed=1)
    if bprog('padaria', t) >= 1:
        B.smoke_at(img, t, 285, 300, seed=2)
    fire_on = t >= S4
    if fire_on:
        W.smoke(img, t)
    elif t < S3:
        B.smoke_at(img, t, 180, 418, n=4, seed=3)
    # moradores
    for i, x, y, fr in sorted(people(t), key=lambda p: p[2]):
        n, r = FOUND[i]
        W.ground_shadow(img, x, y)
        W.blit(img, F.folk(n, r, fr), x, y)
        if 'adestr' in F.norm(r):
            dx = 14
            W.ground_shadow(img, x + dx, y)
            W.blit(img, F.make_dog(int(t * 3) % 2), x + dx, y)
    s = W.sky(td, t)
    if t < S4:
        W.birds(s, t % 6)
    tint = W.keyinterp(W.TINT, td)
    tm = np.broadcast_to(tint, (W.H, W.W, 3)).copy()
    nf = W.clamp((td - 0.6) / 0.9)
    if fire_on:
        lv = (W.light_level(t) * nf)[..., None]
        tm = tm * (1 - lv) + np.array((1.06, 0.84, 0.66)) * lv
    if bprog('lantern', t) >= 1 and nf > 0:
        lv = (light_at(*LANT_C, 30, t) * nf * 0.9)[..., None]
        tm = tm * (1 - lv) + np.array((1.04, 0.86, 0.66)) * lv
    if t >= S5:
        mx, my = myst_pos(t)
        lv = (light_at(mx, my, 22, t) * 0.8)[..., None]
        tm = tm * (1 - lv) + np.array((0.55, 1.0, 0.9)) * lv
    out = np.where(W.LMASK[..., None], img * tm, s)
    if fire_on:
        W.fire(out, t, scale=W.ease((t - S4) / 0.3))
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        if bprog(name, t) >= 1:
            B.emissive(out, spr, *B.POS[name], strength=max(nf, 0.35 if name == 'forja' else 0) * 0.95, t=t)
    if td > 1.5:
        k = W.clamp((td - 1.5) / 0.4)
        for fx, fy, ph, f in FLIES:
            if math.sin(t * f + ph) > 0.2:
                x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
                out[y, x] = out[y, x] * (1 - k) + np.array((226, 255, 140)) * k
    if t >= S5:
        mx, my = myst_pos(t)
        on = not (S5 + 2.6 <= t < S5 + 2.75)
        if on:
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                out[my + dy, mx + dx] = (200, 255, 230)
            for dx, dy in ((-1, 0), (2, 0), (-1, 1), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)):
                out[my + dy, mx + dx] = out[my + dy, mx + dx] * 0.4 + np.array((110, 220, 190)) * 0.6
    # brilhinhos (S1) e "!" da Cristal
    if t < S2:
        for k, ts in enumerate(SPARK_T):
            if ts <= t < ts + 0.5:
                x, y = RING[k]
                yy_ = int(y) - 34 - int((t - ts) * 8)
                for dx, dy, c in ((0, 0, (255, 255, 220)), (1, 0, (255, 220, 120)), (-1, 0, (255, 220, 120)),
                                  (0, 1, (255, 220, 120)), (0, -1, (255, 220, 120)), (2, 0, (255, 200, 80)),
                                  (-2, 0, (255, 200, 80)), (0, 2, (255, 200, 80)), (0, -2, (255, 200, 80))):
                    out[yy_ + dy, int(x) + dx] = c
    if S5 <= t < S6 and t >= BANG_T:
        x, y = WORK['Cristal']
        W.qmark(out, int(x) - 3, int(y) - 40, bang=True)
    sh_ = shot(t)
    hi = sh_[1] if (sh_[0] == 'close' and (t < S3 or t < S4B)) else None
    if hi is not None:
        x, y = [p for p in people(t) if p[0] == hi][0][1:3]
        arrow(out, int(round(x)), int(round(y)) - 38 - int(2 * abs(math.sin(t * 7))))
    return out, td


ARROW = ["#######", ".#####.", "..###..", "...#..."]


def arrow(img, cx, ty):
    g = np.array([[c == '#' for c in r] for r in ARROW])
    o = np.zeros((g.shape[0] + 2, g.shape[1] + 2), bool)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            o[dy:dy + g.shape[0], dx:dx + g.shape[1]] |= g
    for r_ in range(o.shape[0]):
        for c_ in range(o.shape[1]):
            X, Y = cx - 4 + c_, ty - 1 + r_
            if o[r_, c_] and 0 <= X < W.W and 0 <= Y < W.H:
                inside = 1 <= r_ <= g.shape[0] and 1 <= c_ <= g.shape[1] and g[r_ - 1, c_ - 1]
                img[Y, X] = ((255, 214, 80) if r_ > 1 else (255, 244, 170)) if inside else (40, 26, 20)


def shot(t):
    if t < S2:
        return ('med', None)
    if t < S3:
        return ('close', min(NF - 1, int((t - S2) / ROLL)))
    if t < S4:
        return ('wide', None)
    if t < S5:
        return ('close', RAVI)
    if t < S6:
        return ('bridge', None)
    return ('med', None)


def view(sh, t):
    kind, i = sh
    if kind == 'wide':
        return 0, 0, 3
    if kind == 'med':
        return 44, 80, 4
    if kind == 'bridge':
        return 90, 80, 4
    x, y = [p for p in people(t) if p[0] == i][0][1:3]
    x0 = int(min(max(x - 108, 0), W.W - 216))
    y0 = int(min(max(y - 250, 0), W.H - 384))
    return x0, y0, 5


def camera(c, v):
    x0, y0, s = v
    c8 = np.clip(c, 0, 255).astype(np.uint8)
    return c8[y0:y0 + FH // s, x0:x0 + FW // s].repeat(s, 0).repeat(s, 1)


# ---------------------------------------------------------------- textos
def art(role):
    g = F.gender(role)
    return {'f': 'A ', 'm': 'O '}.get(g, '')


def fund(role):
    g = F.gender(role)
    return {'f': 'FUNDADORA', 'm': 'FUNDADOR'}.get(g, 'FUNDADOR(A)')


CAPS = [
    (0, S2, 300, [(0.0, [('VOCÊS COMENTARAM', WHITE)], 140), (0.0, [('O NOME…', WHITE)], 140),
                  (0.7, [('…E VIRARAM ', WHITE), ('MORADORES.', GOLD)], 150)]),
    (S3, S4, 290, [(S3, [('E O REINO COMEÇOU', WHITE)], 140), (S3, [('A CRESCER.', GOLD)], 170)]),
    (S4, S4B, 290, [(S4, [('A RAVIELA, A CAVALEIRA,', WHITE)], 130), (S4 + 0.4, [('FEZ UM JURAMENTO:', GOLD)], 150)]),
    (S4B, S5, 270, [(S4B, [('“VOU DERROTAR O INIMIGO', GOLD)], 130), (S4B, [('QUE QUER DESTRUIR', GOLD)], 130),
                    (S4B, [('O REINO…', GOLD)], 130), (S4B + 1.1, [('…E UM DIA SEREI RAINHA.”', WHITE)], 120)]),
    (S5, S6, 280, [(S5, [('NAQUELA NOITE, A CRISTAL', WHITE)], 130), (S5, [('VIGIAVA A PONTE…', WHITE)], 130),
                   (BANG_T, [('E A LUZ ESTAVA', GOLD)], 160), (BANG_T, [('MAIS PERTO.', GOLD)], 160)]),
    (S6, S6B, 290, [(S6, [('COMENTA SEU NOME', WHITE)], 150), (S6, [('E SUA FUNÇÃO.', GOLD)], 170),
                    (S6 + 0.6, [('OS PRÓXIMOS MORAM AQUI.', WHITE)], 110)]),
]


def overlay_state(t):
    st = []
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    sh = shot(t)
    if sh[0] == 'close' and t < S3:
        st.append(('name', sh[1]))
    if S3 <= t < S4:
        for nm, t0 in BUILDS:
            if nm != 'lantern' and t >= t0 + BDUR * 0.9:
                st.append(('lab', nm))
    if t >= S6B:
        st.append(('book',))
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
                if j > 0 and any(ch in 'ÁÉÍÓÚÂÊÔÃÕ' for s_, _ in segs for ch in s_):
                    y += 0.17 * sz
                if j < nvis:
                    E.draw_line(d, FW / 2, y, segs, size)
                y += 0.54 * sz + 0.24 * sz + 10
        elif k == 'name':
            i = item[1]
            n, r = FOUND[i]
            E.draw_line(d, FW / 2, 300, [(n.upper(), GOLD)], 230)
            role = r.upper() if len(r) < 14 else r.upper()
            E.draw_line(d, FW / 2, 300 + 0.54 * 230 + 60, [(f'{art(r)}{role}', WHITE)], 120)
            txt = f'MORADOR {i + 1:03d} · {fund(r)}'
            ft = E.font(58)
            w = ft.getlength(txt) + 60
            E.panel(d, (FW / 2 - w / 2, 610, FW / 2 + w / 2, 700))
            d.text((FW / 2, 655), txt, font=ft, fill=GOLD + (255,), anchor='mm')
        elif k == 'lab':
            nm = item[1]
            title, sub, (cx, cy) = [(l[1], l[2], l[3]) for l in LABELS if l[0] == nm][0]
            ft, ft2 = E.font(56), E.font(40)
            w = max(ft.getlength(title), ft2.getlength(sub) if sub else 0) + 50
            hgt = 76 if not sub else 116
            E.panel(d, (cx - w / 2, cy - hgt / 2, cx + w / 2, cy + hgt / 2))
            d.text((cx, cy - (18 if sub else 0)), title, font=ft, fill=GOLD + (255,), anchor='mm')
            if sub:
                d.text((cx, cy + 28), sub, font=ft2, fill=(240, 236, 250, 255), anchor='mm')
        elif k == 'book':
            x0, y0, x1, y1 = 90, 250, 990, 1500
            E.panel(d, (x0, y0, x1, y1), fill=(240, 222, 182, 248), border=(92, 58, 34, 255), b=12)
            d.rectangle((x0 + 12, y0 + 12, x1 - 12, y0 + 190), fill=(178, 46, 42, 255))
            d.text((FW / 2, y0 + 70), 'LIVRO DO REINO', font=E.font(100), fill=(255, 220, 120, 255), anchor='mm')
            d.text((FW / 2, y0 + 150), 'OS FUNDADORES DE BRASA', font=E.font(56), fill=(255, 240, 220, 255), anchor='mm')
            yy_ = y0 + 250
            for j, (n, r) in enumerate(FOUND):
                rr = r if len(r) <= 15 else r.split()[0]
                d.text((x0 + 70, yy_), f'{j + 1:03d}', font=E.font(64), fill=(140, 100, 64, 255), anchor='lm')
                d.text((x0 + 200, yy_), n.upper(), font=E.font(70), fill=(40, 26, 20, 255), anchor='lm')
                d.text((x1 - 60, yy_), rr, font=E.font(54), fill=(178, 46, 42, 255), anchor='rm')
                yy_ += 92
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
    c, td = scene(t)
    f = camera(c, view(shot(t), t))
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

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            blip(ta, 988, g=0.06)
    scale = [74, 77, 79, 81, 84, 86, 89, 91, 93, 96, 98, 101]
    for k, ts in enumerate(SPARK_T):
        m = scale[k % len(scale)]
        for j, mm in enumerate((m, m + 12)):
            nn = int(0.07 * SR)
            E.add(s, ts + j * 0.04, E.sq(E.midi(mm), nn, 0.25) * E.adsr(nn, dec=0.04, sus=0.2), 0.09)
    for k in range(NF):   # chamada: um "plim" por morador
        t0 = S2 + k * ROLL
        nn = int(0.12 * SR)
        tt = np.arange(nn) / SR
        E.add(s, t0, E.lp(E.noise(nn, 40 + k), 0.2) * np.exp(-tt * 30), 0.25)
        m = scale[k % len(scale)]
        nn = int(0.18 * SR)
        E.add(s, t0 + 0.05, E.tri(E.midi(m), nn) * E.adsr(nn, dec=0.08, sus=0.3), 0.14)
    for nm, t0 in BUILDS:   # construção: marteladas + plim
        dur = BDUR if nm not in ('pier', 'horta', 'lantern') else 0.35
        k = 0
        while k * 0.09 < dur:
            nn = int(0.03 * SR)
            E.add(s, t0 + k * 0.09, E.noise(nn, int(t0 * 100) + k) * np.exp(-np.arange(nn) / SR * 120), 0.18)
            blip(t0 + k * 0.09, 300 + 60 * k, d=0.02, g=0.04, duty=0.25)
            k += 1
        for mm in (79, 86):
            nn = int(0.35 * SR)
            E.add(s, t0 + dur, E.sq(E.midi(mm), nn, 0.25) * E.adsr(nn, dec=0.15, sus=0.3, r=0.1), 0.06)
    nn = int(0.45 * SR)   # fogueira
    tt = np.arange(nn) / SR
    E.add(s, S4 - 0.05, E.lp(E.noise(nn, 3), 0.08) * np.sin(math.pi * tt / 0.45) ** 2, 0.8)
    r = random.Random(4)
    t = S4 + 0.1
    while t < TEND:
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.06 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
    nn = int(0.5 * SR)   # espada
    tt = np.arange(nn) / SR
    E.add(s, S4B, (np.sin(2 * math.pi * 2400 * tt) + 0.5 * np.sin(2 * math.pi * 3700 * tt)) * np.exp(-tt * 7), 0.06)
    nn = int(1.8 * SR)   # luz misteriosa
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 98 * tt) + 0.6 * np.sin(2 * math.pi * 147 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 3 * tt))
    E.add(s, BANG_T - 0.2, hum * np.sin(math.pi * tt / 1.8), 0.12)
    for k, m in enumerate((81, 80)):
        nn = int(0.5 * SR)
        E.add(s, BANG_T + k * 0.25, E.tri(E.midi(m), nn, vib=0.02) * E.adsr(nn, a=0.03, dec=0.3, sus=0.4, r=0.2), 0.09)
    blip(BANG_T, 1250, d=0.05, g=0.09, duty=0.25)
    t = S5
    while t < TEND:   # grilos
        for k in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.02)
        t += r.uniform(0.55, 0.95)
    nn = int(0.4 * SR)   # livro abrindo
    tt = np.arange(nn) / SR
    E.add(s, S6B, E.lp(E.noise(nn, 9), 0.3) * np.sin(math.pi * tt / 0.4), 0.25)
    for k, m in enumerate((74, 78, 81, 86)):
        nn = int(0.16 * SR)
        E.add(s, S6B + 0.1 + k * 0.08, E.sq(E.midi(m), nn, 0.25) * E.adsr(nn, dec=0.08, sus=0.3), 0.09)
    return s


def audio(path):
    total = TEND
    E.T4, E.T6, E.T7 = S4, S5, S6
    mus = E.music(total + 0.5)[:int(total * SR)]
    voice = os.environ.get('VOICE')
    if voice:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', voice, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                             capture_output=True).stdout
        v = np.frombuffer(raw, '<i2').astype(np.float64) / 32768
        v = v / (np.abs(v).max() + 1e-9)
        vt = np.zeros(len(mus))
        E.add(vt, float(os.environ.get('VOICE_OFF', '0.15')), v, 1.0)
        env = np.convolve(np.abs(vt), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode='same')
        talk = np.convolve((env > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
        duck = 0.09 * (1 - talk) + 0.035 * talk
        mix = mus * duck + sfx(total) * 0.3 + vt * 0.95
    else:
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
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep2_{float(v):05.2f}.png'))
        return
    wav = os.path.join(OUTDIR, 'ep2.wav')
    audio(wav)
    out = os.path.join(OUTDIR, os.environ.get('NAMEOUT', 'brasa-ep2.mp4'))
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
