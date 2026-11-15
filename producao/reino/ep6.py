#!/usr/bin/env python3
"""Brasa — Ep. 6 "O Viajante" (~26 s, sem voz).
0. A porta da taverna estoura e sai um viajante encapuzado: "AS PEGADAS ERAM DELE." (ação no 1º segundo)
1. Close: no pescoço, um colar com o mesmo símbolo da pedra. Ele veio da vila em ruínas.
2. Na mesma noite a expedição volta, e a pedra brilha junto com o colar.
3. Palco: 4 moradores novos que seguiram mas não disseram o nome ("???").
4. Tochas aparecem nas montanhas: "CONSTRUAM O CASTELO. ELES ESTÃO VINDO." + "FALTAM N MORADORES."
5. Final: QUEM NÃO SEGUE NÃO MORA NA VILA + barra N/100 + COMENTA TEU NOME E TUA FUNÇÃO.
Uso: N=<seguidores> PREVN=<seguidores no ep. 5> python3 ep6.py   (STILLS=1,5,... gera quadros)"""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '77')
import world2 as W
import folk as F
import build as B
import ep1hd as E
import ep2 as P
import ep4 as Q
import ep5 as G

FW, FH, FPS = 1080, 1920, 30
OUTDIR = G.OUTDIR
WHITE, GOLD, TEAL, RED = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 96, 86)
N_FOLLOW = int(os.environ['N'])
PREVN = int(os.environ.get('PREVN', '73'))
GOAL = 100
PEOPLE, IDX, ROLE, CROWD, NP = G.PEOPLE, G.IDX, G.ROLE, G.CROWD, G.NP
EXPED = G.EXPED
NEWBIES = [i for i in range(NP) if PEOPLE[i][0].startswith('anon') and int(PEOPLE[i][0][4:]) >= PREVN - len(G.NAMED)]
NNEW = len(NEWBIES)
# quem pediu nome entre o Ep. 5 e o Ep. 6 assume o lugar de um dos novos sem nome
NAMED6 = [('pixoto', 'cidadão')] if os.environ.get('SEMNOME') is None else []
for _k, (_n, _r) in enumerate(NAMED6[:NNEW]):
    PEOPLE[NEWBIES[_k]] = (_n, _r)
    IDX[_n] = NEWBIES[_k]; ROLE[_n] = _r
TAG6 = {'pixoto': 'CIDADÃO'}

# ---------------------------------------------------------------- tempo
S1, S2, S3, S4, EN = 4.0, 8.5, 13.0, 17.0, 21.5
TEND = EN + 4.5
XF = 0.4
STAGE_Y, STAGE_CX = G.STAGE_Y, 152
SLOTS = {1: [152], 2: [132, 172], 3: [112, 152, 192], 4: [92, 132, 172, 212]}
DOOR, MIY, GUARD, TSHOT = G.DOOR, G.MIY, G.GUARD, G.TSHOT
TX, TY, TB, TAVERN = G.TX, G.TY, G.TB, G.TAVERN
STX, STY = Q.STX, Q.STY
put_px = G.put_px
TRAV_OUT = (246, 551)
TRAV_FIRE = (292, 506)
EXP_SPOT = {'Rafaela': (224, 470), 'Andréa': (206, 476), 'Alexandra': (242, 478)}
EXP_PATH = [(276, 262), (270, 284), (236, 336), (214, 404), (224, 470)]


def tod(t):
    return 1.9 if t < EN else min(2.0, 1.9 + 0.1 * (t - EN) / 0.6)


def walk(p0, p1, t0, dur, t):
    q = W.clamp((t - t0) / dur)
    e = W.ease(q)
    return p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e, (1 + int(t / 0.1) % 2) if 0 < q < 1 else 0


def along(path, q):
    seg = [math.dist(path[k], path[k + 1]) for k in range(len(path) - 1)]
    L = q * sum(seg)
    for k, s_ in enumerate(seg):
        if L <= s_ or k == len(seg) - 1:
            u = min(1.0, L / s_)
            return path[k][0] + (path[k + 1][0] - path[k][0]) * u, path[k][1] + (path[k + 1][1] - path[k][1]) * u
        L -= s_


def exped_pos(n, t):
    k = EXPED.index(n)
    q = W.clamp((t - S2 - 0.15 * k) / 2.4)
    if q <= 0:
        return None
    x, y = along(EXP_PATH, q)
    if q >= 1:
        x, y = EXP_SPOT[n]
    else:
        x += (k - 1) * 7
    return x, y, (1 + int(t / 0.12) % 2) if q < 1 else 0


def traveler(t):
    if t < 0.25:
        return None
    if t < S2:
        x, y, fr = walk((DOOR[0], DOOR[1] + 1), TRAV_OUT, 0.25, 0.9, t)
        return x, y, fr
    return walk(TRAV_OUT, TRAV_FIRE, S2 + 0.2, 2.0, t)


def people_now(t):
    res = []
    for i, (n, r) in enumerate(PEOPLE):
        if n in EXPED:
            p = exped_pos(n, t)
            if p:
                res.append((i,) + p)
            continue
        if i in NEWBIES:
            if t < S3:
                continue
            j = NEWBIES.index(i)
            if j < 4:                                     # fila da frente, com crachá
                sx, sy = SLOTS[min(4, NNEW)][j], STAGE_Y
            else:                                         # quem sobrar fica atrás, entre os da frente
                sx, sy = SLOTS[min(4, NNEW)][(j - 4) % 4] + 20, STAGE_Y - 14
            res.append((i,) + walk((180 + (j - 1.5) * 8, 652), (sx, sy), S3 + 0.4 + 0.2 * j, 0.9, t))
            continue
        if n == 'Miyuki':
            res.append((i, MIY[0], MIY[1], 0)); continue
        if n == 'cubo':
            res.append((i, GUARD[0], GUARD[1], 0)); continue
        x, y = CROWD[i]
        res.append((i, x, y, 0))
    return res


# ---------------------------------------------------------------- tochas nas montanhas
_rt = random.Random(9)
TORCHES = sorted([(_rt.uniform(30, 330), _rt.uniform(236, 256), _rt.random() * 6.28, _rt.uniform(S4 + 0.6, S4 + 3.6))
                  for _ in range(70)], key=lambda z: z[3])


def torches(out, t):
    if t < S4 + 0.5:
        return
    for x, y, ph, t0 in TORCHES:
        if t < t0:
            continue
        k = W.clamp((t - t0) / 0.3) * (0.75 + 0.25 * math.sin(t * 11 + ph))
        X, Y = int(x + 2 * math.sin(t * 0.6 + ph)), int(y)
        for dx, dy, g in ((0, 0, 1.0), (1, 0, 1.0), (0, -1, 0.9), (1, -1, 0.7), (0, -2, 0.5), (-1, 0, 0.4), (2, 0, 0.4),
                          (0, 1, 0.35), (1, 1, 0.35)):
            put_px(out, X + dx, Y + dy, out[Y + dy, X + dx] * (1 - k * g) + np.array((255, 170, 70)) * k * g)


# ---------------------------------------------------------------- colar com o símbolo
def pendant(out, x, y, t, big=1.0):
    g = 0.6 + 0.4 * math.sin(t * 6)
    cx, cy = int(x), int(y) - 16
    put_px(out, cx - 2, cy - 2, (120, 110, 90)); put_px(out, cx + 2, cy - 2, (120, 110, 90))
    for cxr, cyr in G.RUNE:
        X, Y = cx - 2 + cxr, cy - 1 + cyr
        if 0 <= X < W.W and 0 <= Y < W.H:
            out[Y, X] = out[Y, X] * (1 - g) + np.array((170, 255, 236)) * g


# ---------------------------------------------------------------- vila
def village(t):
    td = tod(t)
    img = W.LAND.copy()
    for x0, y, sp, ln in P.SHIM:
        x = int(x0 + t * sp) % W.W
        for k in range(ln):
            xk = (x + k) % W.W
            if not (260 <= xk <= 290 or 196 <= xk <= 215):
                img[y, xk] = (170, 214, 246) if k else (210, 236, 252)
    for c_ in range(20):
        dy = int(round(math.sin(t * 7 - c_ * 0.45) * 1.4 * min(1, c_ / 6)))
        for r_ in range(12):
            col = P.FLAGC.get((c_, r_), (178, 46, 42))
            wv = math.sin(t * 7 - c_ * 0.45 + 1.2)
            col = W.shade(col, 1.12) if wv > 0.55 else (W.shade(col, 0.82) if wv < -0.55 else col)
            if r_ in (0, 11):
                col = W.shade(col, 0.78)
            img[318 + r_ + dy, 154 + c_] = col
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.blit(img, spr, *B.POS[name])
    B.draw_pier(img); B.draw_horta(img)
    B.smoke_at(img, t, 97, 300, seed=1); B.smoke_at(img, t, 285, 300, seed=2); B.smoke_at(img, t, TX + 13, TY, seed=3)
    W.smoke(img, t)
    W.ground_shadow(img, STX - 12, STY); W.ground_shadow(img, STX + 12, STY)
    ppl = people_now(t)
    trav = traveler(t)
    items = [(STY - 0.5, 'statue', None), (TB - 0.5, 'tavern', None)] + [(p[2], 'p', p) for p in ppl]
    if trav:
        items.append((trav[1], 'trav', trav))
    dog_i = IDX['Ana Sofia']
    for _, kind, p in sorted(items, key=lambda z: z[0]):
        if kind == 'statue':
            h, w = Q.STATUE.shape[:2]
            Q.blit_arr(img, Q.STATUE, STX - w // 2, STY - h)
            continue
        if kind == 'tavern':
            B.blit(img, TAVERN, TX, TY, p=1.0, t=t)
            continue
        if kind == 'trav':
            x, y, fr = p
            W.ground_shadow(img, x, y)
            W.blit(img, F.folk('Viajante', 'viajante encapuzado', fr), x, y)
            continue
        i, x, y, fr = p
        n, r = PEOPLE[i]
        rr = r if r else ('moradora' if n == 'Lila' else 'morador')
        if n in TAG6 and S3 + 1.9 <= t < S4:              # brilho em quem disse o nome
            Q.sparkles(img, x, y - 20, S3 + 1.9, t, dur=1.2)
        W.ground_shadow(img, x, y)
        W.blit(img, F.folk(n, rr, fr), x, y)
        if i == dog_i:
            W.ground_shadow(img, x + 14, y)
            W.blit(img, F.make_dog(int(t * 3) % 2), x + 14, y)
    s = W.sky(td, t)
    tm = np.broadcast_to(W.keyinterp(W.TINT, td), (W.H, W.W, 3)).copy()
    nf = W.clamp((td - 0.6) / 0.9)
    lv = (W.light_level(t) * nf)[..., None]
    tm = tm * (1 - lv) + np.array((1.06, 0.84, 0.66)) * lv
    lv = (P.light_at(*P.LANT_C, 30, t) * nf * 0.9)[..., None]
    tm = tm * (1 - lv) + np.array((1.04, 0.86, 0.66)) * lv
    lv = (P.light_at(276, 254, 20, t) * 0.75 * nf)[..., None]
    tm = tm * (1 - lv) + np.array((0.55, 1.0, 0.9)) * lv
    burst = max(0.0, 1 - t / 0.7)                          # porta estourando
    lv = (P.light_at(DOOR[0], DOOR[1] + 2, 40 + 50 * burst, t) * min(1.0, 0.9 * nf + burst))[..., None]
    tm = tm * (1 - lv) + np.array((1.1 + 0.5 * burst, 0.9 + 0.4 * burst, 0.66 + 0.3 * burst)) * lv
    if t < S2:                                            # pegadas ainda acesas
        lv = (P.light_at(290, 594, 52, t) * 0.5)[..., None]
        tm = tm * (1 - lv) + np.array((0.62, 1.1, 1.0)) * lv
    if trav and t < S3:                                   # luz do colar
        k = 0.6 if t < S1 else (0.9 if t < S2 else 0.7)
        lv = (P.light_at(trav[0], trav[1] - 16, 18, t) * k)[..., None]
        tm = tm * (1 - lv) + np.array((0.6, 1.15, 1.05)) * lv
    if S3 - 0.1 <= t < S4:
        lv = (P.light_at(STAGE_CX, STAGE_Y - 4, 104, t) * 0.85)[..., None]
        tm = tm * (1 - lv) + np.array((1.0, 0.92, 0.8)) * lv
    out = np.where(W.LMASK[..., None], img * tm, s)
    W.fire(out, t)
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.emissive(out, spr, *B.POS[name], strength=max(nf, 0.35 if name == 'forja' else 0) * 0.95, t=t)
    B.emissive(out, TAVERN, TX, TY, strength=max(nf, 0.5) * 0.95, t=t)
    k = W.clamp((td - 1.5) / 0.4)
    for fx, fy, ph, f in P.FLIES:
        if math.sin(t * f + ph) > 0.2:
            x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
            out[y, x] = out[y, x] * (1 - k) + np.array((226, 255, 140)) * k
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        out[254 + dy, 276 + dx] = (200, 255, 230)
    G.castle5(out, 100 + t)
    torches(out, t)
    if t < S2:
        G.footprints(out, G.STEP_T1 + 1 + t)
    if t < 0.9:                                           # poeira da porta
        r = random.Random(int(t * 20))
        for _ in range(int(14 * (1 - t / 0.9))):
            a = r.uniform(-math.pi, 0)
            d_ = 6 + 22 * t / 0.9 * r.uniform(0.6, 1.2)
            x, y = DOOR[0] + math.cos(a) * d_, DOOR[1] + 2 + math.sin(a) * d_ * 0.4
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                put_px(out, x + dx, y + dy, (214, 200, 176))
    if trav:
        pendant(out, trav[0], trav[1], t)
    if 0.2 <= t < S1:
        for i in (IDX['Miyuki'], IDX['cubo']):
            x, y = [p[1:3] for p in ppl if p[0] == i][0]
            W.qmark(out, int(x) - 3, int(y) - 40, bang=True)
    rafa = exped_pos('Rafaela', t)
    if rafa:
        Q.draw_stone(out, rafa[0] + 7, rafa[1] - 24, t, glow=1.4)
        if t >= S2 + 2.4:
            for n in EXPED:
                x, y, _ = exped_pos(n, t)
                W.qmark(out, int(x) - 3, int(y) - 41, bang=True)
    if S3 + 2.0 <= t < S4:
        for i in NEWBIES:
            if PEOPLE[i][0] in TAG6:
                continue
            x, y = [p[1:3] for p in ppl if p[0] == i][0]
            W.qmark(out, int(x) - 3, int(y) - 41)
    return out


# ---------------------------------------------------------------- câmera
def shot(t):
    if t < S1:
        return TSHOT
    if t < S2:
        tr = traveler(t)
        return (int(tr[0]) - 54, min(W.H - 192, int(tr[1]) - 122), 10)
    if t < S3:
        return (150, 250, 6)
    if t < S4:
        return (STAGE_CX - 108, STAGE_Y - 250, 5)
    if t < EN:
        return (44, 40, 4)
    return (44, 80, 4)


# ---------------------------------------------------------------- textos
FALTAM = max(0, GOAL - N_FOLLOW)
CAPS = [
    (0.0, 1.8, 290, [(0.0, [('AS PEGADAS', WHITE)], 150), (0.0, [('ERAM ', WHITE), ('DELE.', GOLD)], 170)]),
    (1.8, S1, 290, [(1.8, [('UM VIAJANTE', WHITE)], 150), (2.1, [('ENCAPUZADO…', GOLD)], 150)]),
    (S1, S1 + 2.3, 270, [(S1, [('NO PESCOÇO,', WHITE)], 130), (S1 + 0.3, [('O MESMO SÍMBOLO', TEAL)], 120),
                         (S1 + 0.3, [('DA PEDRA.', TEAL)], 120)]),
    (S1 + 2.3, S2, 270, [(S1 + 2.3, [('ELE VEIO DA', WHITE)], 140), (S1 + 2.6, [('VILA EM RUÍNAS.', GOLD)], 140)]),
    (S2, S2 + 2.3, 270, [(S2, [('NA MESMA NOITE,', WHITE)], 128), (S2 + 0.3, [('A EXPEDIÇÃO VOLTOU…', GOLD)], 112)]),
    (S2 + 2.3, S3, 270, [(S2 + 2.3, [('…E A PEDRA BRILHOU', WHITE)], 116), (S2 + 2.6, [('JUNTO COM O COLAR.', TEAL)], 116)]),
    (S3, S3 + 1.9, 270, [(S3, [(f'CHEGARAM {NNEW}', WHITE)], 140), (S3 + 0.3, [('MORADORES NOVOS…', GOLD)], 128)]),
    ((S3 + 1.9, S4, 270, [(S3 + 1.9, [('…E SÓ O ', WHITE), (NAMED6[0][0].upper(), GOLD)], 130),
                          (S3 + 2.2, [('DISSE O NOME.', WHITE)], 130)]) if NAMED6 else
     (S3 + 1.9, S4, 270, [(S3 + 1.9, [('…MAS NINGUÉM SABE', WHITE)], 120), (S3 + 2.2, [('O NOME DELES.', GOLD)], 140)])),
    (S4, EN, 270, [(S4, [('O VIAJANTE AVISOU:', WHITE)], 116), (S4 + 0.8, [('"CONSTRUAM O CASTELO.', GOLD)], 106),
                   (S4 + 2.0, [('ELES ESTÃO VINDO."', RED)], 120)]),
    (S4 + 3.0, EN, 1090, [(S4 + 3.0, [('FALTAM ', WHITE), (f'{FALTAM}', GOLD), (' MORADORES.', WHITE)], 100)]),
    (EN, TEND + 1, 270, [(EN, [('QUEM NÃO SEGUE', WHITE)], 150), (EN + 0.3, [('NÃO MORA NA VILA.', GOLD)], 136)]),
    (EN + 0.9, TEND + 1, 880, [(EN + 0.9, [('COMENTA TEU NOME', WHITE)], 110), (EN + 0.9, [('E TUA FUNÇÃO', GOLD)], 110)]),
]


def overlay_state(t):
    st = []
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    if S3 + 1.5 <= t < S4:
        st.append(('stage',))
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
        elif k == 'stage':
            x0, y0, s = shot(S3 + 1.0)
            for j, i in enumerate(NEWBIES[:4]):
                cx = (SLOTS[min(4, NNEW)][j] - x0) * s
                n_ = PEOPLE[i][0]
                if n_ in TAG6:
                    Q.tag(d, cx, (STAGE_Y - y0) * s + 40, F.shown(n_).upper(), TAG6[n_])
                else:
                    Q.tag(d, cx, (STAGE_Y - y0) * s + 40, '???', 'SEM NOME')
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


def frame(t):
    f = P.camera(village(t), shot(t))
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
    r = random.Random(6)

    def blip(t, f, d=0.035, g=0.05, duty=0.5):
        nn = int(d * SR)
        E.add(s, t, E.sq(f, nn, duty) * E.adsr(nn, a=0.002, dec=0.02, sus=0.3, r=0.01), g)

    def chime(t0, notes, g=0.08, step=0.06, dur=0.12):
        for j, m in enumerate(notes):
            nn = int(dur * SR)
            E.add(s, t0 + j * step, E.sq(E.midi(m), nn, 0.25) * E.adsr(nn, dec=0.05, sus=0.2), g)

    def thump(t0, g=0.5, f0=110, dec=18):
        nn = int(0.25 * SR)
        tt = np.arange(nn) / SR
        f = f0 * np.exp(-tt * dec) + 38
        E.add(s, t0, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 12), g)

    for a, b, y, lines in CAPS:
        for ta, segs, size in lines:
            blip(ta, 988)
    thump(0.02, g=0.8, f0=160)                           # porta estourando
    nn = int(0.35 * SR)
    E.add(s, 0.02, E.lp(E.noise(nn, 3), 0.4) * np.exp(-np.arange(nn) / SR * 14), 0.45)
    blip(0.25, 660, d=0.06); blip(0.33, 880, d=0.06)
    for k in range(4):                                    # passos dele
        nn = int(0.05 * SR)
        E.add(s, 0.35 + k * 0.24, E.lp(E.noise(nn, 40 + k), 0.12) * np.exp(-np.arange(nn) / SR * 60), 0.3)
    nn = int((S2 - S1 + 0.5) * SR)                         # zumbido do colar
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 98 * tt) + 0.6 * np.sin(2 * math.pi * 147 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 3 * tt))
    E.add(s, S1 - 0.1, hum * np.sin(math.pi * tt / (S2 - S1 + 0.5)), 0.16)
    chime(S1 + 0.3, [88, 84, 91, 96], g=0.06, step=0.1, dur=0.2)
    chime(S2 + 2.4, [84, 88, 91, 96, 100], g=0.07, step=0.08, dur=0.18)
    for j in range(NNEW):
        chime(S3 + 0.5 + 0.25 * j, [79 + 2 * j, 83 + 2 * j], g=0.05)
    blip(S3 + 2.0, 520, d=0.08); blip(S3 + 2.1, 440, d=0.1)
    for k in range(7):                                    # tambores ao longe
        thump(S4 + 0.6 + k * 0.55, g=0.35 + 0.05 * k, f0=70, dec=10)
    nn = int((EN - S4) * SR)
    tt = np.arange(nn) / SR
    drone = (np.sin(2 * math.pi * 55 * tt) + 0.5 * np.sin(2 * math.pi * 58.3 * tt)) * np.sin(math.pi * tt / (EN - S4)) ** 0.5
    E.add(s, S4, drone, 0.14)
    for k, m in enumerate([62, 66, 69, 74, 78, 81]):
        nn = int(0.12 * SR)
        E.add(s, EN + 0.25 + k * 0.09, E.sq(E.midi(m + 12), nn, 0.25) * E.adsr(nn), 0.08)
    t = 0.0
    while t < total:                                      # fogueira e grilos
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.04 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
    t = 0.0
    while t < total:
        for k in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.02)
        t += r.uniform(0.55, 0.95)
    return s


def audio(path):
    total = TEND
    E.T4, E.T6, E.T7 = S1, S2, S2
    mus = E.music(total + 0.5)[:int(total * SR)]
    g = np.ones(len(mus))
    a, b = int(S4 * SR), int(EN * SR)
    ramp = int(0.3 * SR)
    g[a:b] = 0.3
    g[a:a + ramp] = np.linspace(1, 0.3, ramp)
    g[b - ramp:b] = np.linspace(0.3, 1, ramp)
    mix = mus * g * 0.9 + sfx(total)
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
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep6_{float(v):05.2f}.png'))
        return
    wav = os.path.join(OUTDIR, 'ep6.wav')
    audio(wav)
    out = os.path.join(OUTDIR, 'brasa-ep6.mp4')
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
