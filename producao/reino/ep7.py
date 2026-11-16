#!/usr/bin/env python3
"""Brasa — Ep. 7 "O Batedor" (~26 s, sem voz). Feito com a receita de 16/11:
a promessa ("cada seguidor vira morador") na tela no 1º segundo, ação desde o 1º quadro, história que dá pra entender
sem ter visto os outros episódios, e 2 moradores com papel na história (Valdemir e Edilson).
0. O Valdemir vaqueiro vem galopando pela ponte, com tochas nas montanhas atrás dele.
1. Ele chega na vila e todo mundo acorda ("!").
2. Plano aberto nas montanhas: centenas de tochas descendo. "PRA AGUENTAR, PRECISA DE 100 MORADORES. CADA SEGUIDOR É UM."
3. Palco: chegou reforço — o Edilson espadachim (+ os outros novos sem nome).
4. O Valdemir e o Edilson de guarda na ponte; as tochas já chegaram no rio. "FALTAM N MORADORES."
5. Final: QUEM NÃO SEGUE NÃO MORA NA VILA + barra N/100 + COMENTA TEU NOME E TUA FUNÇÃO.
Uso: N=<seguidores> PREV7=<seguidores no ep. 6> python3 ep7.py   (STILLS=1,5,... gera quadros; CAPA=1 gera a capa)"""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '83')
os.environ['PREVN'] = '73'                       # o ep6 importado monta o palco dele (pixoto continua com nome)
import world2 as W
import folk as F
import build as B
import ep1hd as E
import ep2 as P
import ep4 as Q
import ep6 as H
import horse as HS

G = H.G
FW, FH, FPS = 1080, 1920, 30
OUTDIR = G.OUTDIR
WHITE, GOLD, TEAL, RED = (255, 255, 255), (255, 208, 72), (96, 226, 214), (255, 96, 86)
N_FOLLOW = int(os.environ['N'])
PREV7 = int(os.environ.get('PREV7', '80'))
GOAL = 100
PEOPLE, IDX, ROLE, CROWD, NP = G.PEOPLE, G.IDX, G.ROLE, G.CROWD, G.NP
EXPED = G.EXPED
NEW7 = [i for i in range(NP) if PEOPLE[i][0].startswith('anon') and int(PEOPLE[i][0][4:]) >= PREV7 - len(G.NAMED)]
NAMED7 = [('Edilson', 'espadachim')]
for _k, (_n, _r) in enumerate(NAMED7[:len(NEW7)]):
    PEOPLE[NEW7[_k]] = (_n, _r)
    IDX[_n] = NEW7[_k]; ROLE[_n] = _r
NNEW = len(NEW7)
VAL = IDX['Valdemir']
EDI = IDX['Edilson'] if 'Edilson' in IDX else None
TAG7 = {'Edilson': 'ESPADACHIM'}

# ---------------------------------------------------------------- tempo
S1, S2, S3, S4, EN = 4.2, 7.8, 12.3, 16.8, 21.3
TEND = EN + 4.5
XF = 0.4
STAGE_Y, STAGE_CX = G.STAGE_Y, 152
SLOTS = {1: [152], 2: [132, 172], 3: [112, 152, 192], 4: [92, 132, 172, 212]}
put_px = G.put_px
RIDE = [(282, 250), (277, 276), (276, 304), (250, 326), (226, 346), (206, 366)]
RIDE_T = 3.9
STOP = RIDE[-1]
BRIDGE_V = (250, 316)                            # Valdemir de guarda na ponte
BRIDGE_E = (304, 318)                            # Edilson
TRAV_FIRE = H.TRAV_FIRE


def tod(t):
    return 1.9 if t < EN else min(2.0, 1.9 + 0.1 * (t - EN) / 0.6)


def along(path, q):
    seg = [math.dist(path[k], path[k + 1]) for k in range(len(path) - 1)]
    L = q * sum(seg)
    for k, s_ in enumerate(seg):
        if L <= s_ or k == len(seg) - 1:
            u = min(1.0, L / s_)
            return path[k][0] + (path[k + 1][0] - path[k][0]) * u, path[k][1] + (path[k + 1][1] - path[k][1]) * u
        L -= s_


def rider(t):
    """posição do Valdemir a cavalo e o quadro do galope."""
    if t >= S4:
        return BRIDGE_V[0], BRIDGE_V[1], 0, False
    q = W.clamp(t / RIDE_T)
    q = q if q < 0.85 else 0.85 + (1 - (1 - (q - 0.85) / 0.15) ** 2) * 0.15
    x, y = along(RIDE, q)
    moving = t < RIDE_T
    return x, y, (int(t / 0.09) % 4) if moving else 1, moving


def people_now(t):
    res = []
    for i, (n, r) in enumerate(PEOPLE):
        if i == VAL:
            continue
        if n in EXPED:
            x, y = H.EXP_SPOT[n]
            res.append((i, x, y, 0)); continue
        if i in NEW7:
            if t < S3:
                continue
            j = NEW7.index(i)
            if i == EDI and t >= S4:
                res.append((i, BRIDGE_E[0], BRIDGE_E[1], 0)); continue
            if j < 4:
                sx, sy = SLOTS[min(4, NNEW)][j], STAGE_Y
            else:
                sx, sy = SLOTS[min(4, NNEW)][(j - 4) % 4] + 20, STAGE_Y - 14
            res.append((i,) + H.walk((180 + (j - 1) * 8, 652), (sx, sy), S3 + 0.4 + 0.2 * j, 0.9, t))
            continue
        if n == 'Miyuki':
            res.append((i, H.MIY[0], H.MIY[1], 0)); continue
        if n == 'cubo':
            res.append((i, H.GUARD[0], H.GUARD[1], 0)); continue
        x, y = CROWD[i]
        res.append((i, x, y, 0))
    return res


# ---------------------------------------------------------------- alarme: o "!" se espalha pela vila
def alarm_t(i):
    x, y = CROWD[i]
    return S1 + 0.25 + math.dist((x, y), STOP) / 140


# ---------------------------------------------------------------- tochas descendo as montanhas
_rt = random.Random(17)
LINES = []
for k in range(8):                                # filas em zigue-zague, como um exército descendo
    x = 22 + k * 45 + _rt.uniform(-8, 8)
    pts, y = [(x, 150 + _rt.uniform(0, 30))], 150
    while y < 266:
        y = min(268, pts[-1][1] + _rt.uniform(14, 24))
        x = min(345, max(12, pts[-1][0] + _rt.choice((-1, 1)) * _rt.uniform(10, 24)))
        pts.append((x, y))
    LINES.append(pts)
TORCH = []
for li, pts in enumerate(LINES):
    for k in range(22):
        TORCH.append((li, k / 22 * 0.62, _rt.random() * 6.28))
SCATTER = [(_rt.uniform(14, 346), _rt.uniform(170, 256), _rt.random() * 6.28) for _ in range(40)]
BANK = sorted([(_rt.uniform(8, 352), _rt.uniform(270, 274), _rt.random() * 6.28, _rt.uniform(S4 + 1.4, S4 + 3.4))
               for _ in range(64)], key=lambda z: z[3])     # a margem de lá do rio se enchendo de tochas


def torch_pos(li, u0, t):
    """u0 = posição inicial ao longo da fila (0..1); a fila desce devagar e chega no rio no fim do ep."""
    u = u0 + 0.38 * W.clamp(t / EN) ** 0.8
    return along(LINES[li], min(1.0, u)) if u <= 1.0 else None


def torches(out, t):
    pts = []
    for li, u0, ph in TORCH:
        p = torch_pos(li, u0, t)
        if p:
            pts.append((p[0], p[1], ph))
    pts += SCATTER
    pts += [(x, y, ph) for x, y, ph, t0 in BANK if t >= t0]
    for x, y, ph, t0 in BANK:                     # reflexo das tochas na água
        if t >= t0:
            k = 0.35 + 0.15 * math.sin(t * 9 + ph)
            for dy in range(6, 13, 2):
                X, Y = int(x + math.sin(t * 3 + dy + ph)), int(y + dy)
                if 0 <= X < W.W and 0 <= Y < W.H:
                    out[Y, X] = out[Y, X] * (1 - k) + np.array((255, 160, 70)) * k
    for x, y, ph in pts:
        k = 0.75 + 0.25 * math.sin(t * 11 + ph)
        X, Y = int(x + 1.2 * math.sin(t * 0.8 + ph)), int(y)
        for dx, dy, g in ((0, 0, 1.0), (1, 0, 1.0), (0, -1, 0.9), (1, -1, 0.7), (0, -2, 0.5), (-1, 0, 0.4), (2, 0, 0.4),
                          (0, 1, 0.35), (1, 1, 0.35)):
            Xp, Yp = X + dx, Y + dy
            if 0 <= Xp < W.W and 0 <= Yp < W.H:
                out[Yp, Xp] = out[Yp, Xp] * (1 - k * g) + np.array((255, 170, 70)) * k * g


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
    B.smoke_at(img, t, 97, 300, seed=1); B.smoke_at(img, t, 285, 300, seed=2); B.smoke_at(img, t, H.TX + 13, H.TY, seed=3)
    W.smoke(img, t)
    W.ground_shadow(img, H.STX - 12, H.STY); W.ground_shadow(img, H.STX + 12, H.STY)
    ppl = people_now(t)
    rx, ry, rfr, moving = rider(t)
    items = [(H.STY - 0.5, 'statue', None), (H.TB - 0.5, 'tavern', None), (TRAV_FIRE[1], 'trav', None),
             (ry, 'horse', None)] + [(p[2], 'p', p) for p in ppl]
    dog_i = IDX['Ana Sofia']
    for _, kind, p in sorted(items, key=lambda z: z[0]):
        if kind == 'statue':
            h, w = Q.STATUE.shape[:2]
            Q.blit_arr(img, Q.STATUE, H.STX - w // 2, H.STY - h)
            continue
        if kind == 'tavern':
            B.blit(img, H.TAVERN, H.TX, H.TY, p=1.0, t=t)
            continue
        if kind == 'trav':
            W.ground_shadow(img, *TRAV_FIRE)
            W.blit(img, F.folk('Viajante', 'viajante encapuzado', 0), *TRAV_FIRE)
            continue
        if kind == 'horse':
            spr = HS.rider_on_horse(F.folk('Valdemir', ROLE['Valdemir'], 0), rfr)
            for dx in (-6, 0, 6):
                W.ground_shadow(img, rx + dx, ry)
            W.blit(img, spr, rx, ry)
            continue
        i, x, y, fr = p
        n, r = PEOPLE[i]
        rr = r if r else ('moradora' if n == 'Lila' else 'morador')
        if n in TAG7 and S3 + 1.9 <= t < S4:
            Q.sparkles(img, x, y - 20, S3 + 1.9, t, dur=1.2)
        jump = 0
        if S1 <= t < S2 and i < len(CROWD):
            a = t - alarm_t(i)
            if 0 <= a < 0.3:
                jump = 2
        W.ground_shadow(img, x, y)
        W.blit(img, F.folk(n, rr, fr), x, y - jump)
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
    lv = (P.light_at(rx, ry - 14, 26, t) * 0.85)[..., None]          # luz em volta do Valdemir
    tm = tm * (1 - lv) + np.array((1.1, 0.92, 0.72)) * lv
    if t >= S4:
        lv = (P.light_at(BRIDGE_E[0], BRIDGE_E[1] - 14, 22, t) * 0.8)[..., None]
        tm = tm * (1 - lv) + np.array((1.1, 0.92, 0.72)) * lv
    if S3 - 0.1 <= t < S4:
        lv = (P.light_at(STAGE_CX, STAGE_Y - 4, 104, t) * 0.85)[..., None]
        tm = tm * (1 - lv) + np.array((1.0, 0.92, 0.8)) * lv
    out = np.where(W.LMASK[..., None], img * tm, s)
    W.fire(out, t)
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.emissive(out, spr, *B.POS[name], strength=max(nf, 0.35 if name == 'forja' else 0) * 0.95, t=t)
    B.emissive(out, H.TAVERN, H.TX, H.TY, strength=max(nf, 0.5) * 0.95, t=t)
    k = W.clamp((td - 1.5) / 0.4)
    for fx, fy, ph, f in P.FLIES:
        if math.sin(t * f + ph) > 0.2:
            x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
            out[y, x] = out[y, x] * (1 - k) + np.array((226, 255, 140)) * k
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        out[254 + dy, 276 + dx] = (200, 255, 230)
    G.castle5(out, 100 + t)
    torches(out, t)
    if moving:                                    # poeira dos cascos
        r = random.Random(int(t * 30))
        for k_ in range(6):
            a = t - k_ * 0.05
            px, py = along(RIDE, W.clamp(a / RIDE_T)) if a > 0 else RIDE[0]
            px += 10 + r.uniform(-3, 5); py += r.uniform(-2, 1)
            for dx, dy in ((0, 0), (1, 0)):
                put_px(out, px + dx, py + dy, (196, 176, 140))
    # "!" do alarme
    if S1 <= t < S2:
        for p in ppl:
            i, x, y = p[0], p[1], p[2]
            if i >= len(CROWD):
                continue
            a = t - alarm_t(i)
            if 0 <= a < 1.6:
                W.qmark(out, int(x) - 3, int(y) - 41, bang=True)
    if S3 + 2.0 <= t < S4:
        for i in NEW7:
            if PEOPLE[i][0] in TAG7:
                continue
            x, y = [p[1:3] for p in ppl if p[0] == i][0]
            W.qmark(out, int(x) - 3, int(y) - 41)
    return out


# ---------------------------------------------------------------- câmera
def clamp_shot(x0, y0, s):
    return (int(min(max(0, x0), W.W - FW // s)), int(min(max(0, y0), W.H - FH // s)), s)


def shot(t):
    if t < S1:
        rx, ry, _, _ = rider(t)
        return clamp_shot(rx - 90, ry - 200, 6)
    if t < S2:
        return (44, 130, 4)
    if t < S3:
        return (44, 40, 4)
    if t < S4:
        return (STAGE_CX - 108, STAGE_Y - 250, 5)
    if t < EN:
        return clamp_shot(170, 150, 5)
    return (44, 80, 4)


# ---------------------------------------------------------------- textos
FALTAM = max(0, GOAL - N_FOLLOW)
CAPS = [
    (0.0, 1.9, 270, [(0.0, [('NESTE REINO, CADA', WHITE)], 128), (0.0, [('SEGUIDOR VIRA ', WHITE), ('MORADOR.', GOLD)], 128)]),
    (1.9, S1, 270, [(1.9, [('O VAQUEIRO VIU TOCHAS', WHITE)], 116), (1.9, [('NA MONTANHA…', GOLD)], 130),
                    (2.9, [('CENTENAS DELAS.', RED)], 130)]),
    (S1, S1 + 1.8, 270, [(S1, [('ELE CORREU PRA', WHITE)], 140), (S1 + 0.3, [('AVISAR A VILA.', GOLD)], 140)]),
    (S1 + 1.8, S2, 270, [(S1 + 1.8, [('E A VILA INTEIRA', WHITE)], 140), (S1 + 2.1, [('ACORDOU.', GOLD)], 150)]),
    (S2, S2 + 2.2, 270, [(S2, [('PRA AGUENTAR O ATAQUE,', WHITE)], 112), (S2 + 0.3, [('A VILA PRECISA DE', WHITE)], 120),
                         (S2 + 0.3, [('100 MORADORES.', GOLD)], 140)]),
    (S2 + 2.2, S3, 270, [(S2 + 2.2, [('E CADA SEGUIDOR', WHITE)], 136), (S2 + 2.5, [('É UM MORADOR.', GOLD)], 140)]),
    (S2 + 2.9, S3, 1090, [(S2 + 2.9, [('HOJE SÃO ', WHITE), (f'{N_FOLLOW}', GOLD), ('.', WHITE)], 110)]),
    (S3, S3 + 1.9, 270, [(S3, [('MAS HOJE CHEGOU', WHITE)], 136), (S3 + 0.3, [('REFORÇO…', GOLD)], 150)]),
    (S3 + 1.9, S4, 270, [(S3 + 1.9, [('…O ', WHITE), ('EDILSON', GOLD), (',', WHITE)], 140),
                         (S3 + 2.2, [('ESPADACHIM.', WHITE)], 140)]),
    (S4, S4 + 2.3, 270, [(S4, [('ELE E O VALDEMIR', WHITE)], 130), (S4 + 0.3, [('FICARAM DE GUARDA', GOLD)], 120),
                         (S4 + 0.3, [('NA PONTE.', GOLD)], 120)]),
    (S4 + 2.3, EN, 270, [(S4 + 2.3, [('AS TOCHAS JÁ', WHITE)], 140), (S4 + 2.6, [('CHEGARAM NO RIO.', RED)], 130)]),
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
    if S4 + 0.6 <= t < EN:
        st.append(('guards',))
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
            for j, i in enumerate(NEW7[:4]):
                cx = (SLOTS[min(4, NNEW)][j] - x0) * s
                n_ = PEOPLE[i][0]
                if n_ in TAG7:
                    Q.tag(d, cx, (STAGE_Y - y0) * s + 40, F.shown(n_).upper(), TAG7[n_])
                else:
                    Q.tag(d, cx, (STAGE_Y - y0) * s + 40, '???', 'SEM NOME')
        elif k == 'guards':
            x0, y0, s = shot(S4 + 1.0)
            Q.tag(d, (BRIDGE_V[0] - x0) * s, (BRIDGE_V[1] - y0) * s + 30, 'VALDEMIR', 'VAQUEIRO')
            if EDI is not None:
                Q.tag(d, (BRIDGE_E[0] - x0) * s, (BRIDGE_E[1] - y0) * s + 30, 'EDILSON', 'ESPADACHIM')
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
    sh = shot(t)
    f = P.camera(village(t), sh)
    ov = overlay(overlay_state(t))
    if ov:
        (y0, y1, x0, x1), rgb, a = ov
        reg = f[y0:y1, x0:x1].astype(np.float32)
        f[y0:y1, x0:x1] = (reg * (1 - a) + rgb * a).astype(np.uint8)
    if 0.5 <= t < S1:                              # crachá acompanhando o Valdemir no galope
        rx, ry, _, _ = rider(t)
        im = Image.fromarray(f)
        d = ImageDraw.Draw(im)
        x0, y0, s = sh
        Q.tag(d, (rx - x0) * s, (ry - y0) * s + 24, 'VALDEMIR', 'VAQUEIRO')
        f = np.asarray(im).copy()
    return f


# ---------------------------------------------------------------- áudio
SR = E.SR


def sfx(total):
    n = int(total * SR)
    s = np.zeros(n)
    r = random.Random(7)

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
            blip(ta, 988)
    # galope: ta-ta-TUM
    t = 0.0
    while t < RIDE_T:
        for k_, (off, g) in enumerate(((0.0, 0.32), (0.07, 0.26), (0.15, 0.4))):
            nn = int(0.05 * SR)
            hit = E.lp(E.noise(nn, int(t * 100) + k_), 0.18) * np.exp(-np.arange(nn) / SR * 70)
            E.add(s, t + off, hit, g)
            thump(t + off, g=g * 0.5, f0=150, dec=30, ln=0.08)
        t += 0.36
    # relincho no fim da corrida
    nn = int(0.6 * SR)
    tt = np.arange(nn) / SR
    f = 700 + 300 * np.sin(2 * math.pi * 9 * tt) * np.exp(-tt * 2) - 300 * tt
    neigh = np.sign(np.sin(2 * math.pi * np.cumsum(f) / SR)) * np.exp(-tt * 3.5) * (tt < 0.55)
    E.add(s, RIDE_T - 0.15, E.lp(neigh, 0.25), 0.12)
    # corneta de alarme
    nn = int(1.1 * SR)
    tt = np.arange(nn) / SR
    horn = np.zeros(nn)
    for fr_, g in ((196, 1.0), (294, 0.6), (392, 0.3)):
        ph = np.cumsum(fr_ * (1 + 0.012 * np.sin(2 * math.pi * 5.5 * tt))) / SR
        horn += g * (2 * (ph % 1) - 1)
    env = np.minimum(1, tt / 0.08) * np.minimum(1, (1.1 - tt) / 0.3)
    E.add(s, S1 + 0.05, E.lp(horn * env, 0.18), 0.22)
    # burburinho da vila acordando
    nn = int((S2 - S1) * SR)
    tt = np.arange(nn) / SR
    mur = E.lp(E.noise(nn, 55), 0.06) * (0.5 + 0.5 * np.sin(2 * math.pi * 2.3 * tt) ** 2) * np.sin(math.pi * tt / (S2 - S1))
    E.add(s, S1 + 0.2, mur, 0.5)
    # tambores ao longe e zumbido grave nas montanhas
    for k_ in range(8):
        thump(S2 + 0.3 + k_ * 0.55, g=0.3 + 0.04 * k_, f0=70, dec=10)
    nn = int((S3 - S2) * SR)
    tt = np.arange(nn) / SR
    drone = (np.sin(2 * math.pi * 55 * tt) + 0.5 * np.sin(2 * math.pi * 58.3 * tt)) * np.sin(math.pi * tt / (S3 - S2)) ** 0.5
    E.add(s, S2, drone, 0.14)
    # reforço: moradores chegando + espada
    for j in range(NNEW):
        chime(S3 + 0.5 + 0.2 * j, [79 + 2 * j, 83 + 2 * j], g=0.05)
    nn = int(0.5 * SR)
    tt = np.arange(nn) / SR
    shing = (E.noise(nn, 91) * np.exp(-tt * 18) * 0.4 + np.sin(2 * math.pi * 2650 * tt) * np.exp(-tt * 6)
             + 0.5 * np.sin(2 * math.pi * 3980 * tt) * np.exp(-tt * 8))
    E.add(s, S3 + 1.95, shing, 0.12)
    chime(S3 + 2.0, [86, 90, 93, 98], g=0.06, step=0.07, dur=0.16)
    # ponte: tambores mais perto
    for k_ in range(8):
        thump(S4 + 0.4 + k_ * 0.5, g=0.4 + 0.05 * k_, f0=80, dec=10)
    nn = int((EN - S4) * SR)
    tt = np.arange(nn) / SR
    drone = (np.sin(2 * math.pi * 49 * tt) + 0.5 * np.sin(2 * math.pi * 52 * tt)) * np.sin(math.pi * tt / (EN - S4)) ** 0.5
    E.add(s, S4, drone, 0.16)
    for k_, m in enumerate([62, 66, 69, 74, 78, 81]):
        nn = int(0.12 * SR)
        E.add(s, EN + 0.25 + k_ * 0.09, E.sq(E.midi(m + 12), nn, 0.25) * E.adsr(nn), 0.08)
    t = 0.0
    while t < total:                              # fogueira e grilos
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.04 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
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
    for a_, b_ in ((S2, S3), (S4, EN)):
        a, b = int(a_ * SR), int(b_ * SR)
        ramp = int(0.3 * SR)
        g[a:b] = 0.3
        g[a:a + ramp] = np.linspace(1, 0.3, ramp)
        g[b - ramp:b] = np.linspace(0.3, 1, ramp)
    mix = mus * g * 0.85 + sfx(total)
    fo = int(0.3 * SR)
    mix[-fo:] *= np.linspace(1, 0.35, fo)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


# ---------------------------------------------------------------- capa
def capa():
    t = 1.2
    c = village(t)
    x0, y0, s = shot(t)
    f = P.camera(c, (x0, y0, s))
    im = Image.fromarray(f).convert('RGBA')
    d = ImageDraw.Draw(im)
    title = 'EPISÓDIO 7 · O BATEDOR'
    tw = E.font(78).getlength(title)
    E.panel(d, (540 - tw / 2 - 36, 250, 540 + tw / 2 + 36, 372), b=6)
    E.draw_line(d, 540, 278, [(title, WHITE)], 78)
    E.draw_line(d, 540, 450, [('BRASA', GOLD)], 280, stroke=14)
    E.draw_line(d, 540, 700, [('ELES ', WHITE), ('ESTÃO VINDO', RED)], 116)
    out = os.path.join(OUTDIR, 'capa-brasa-ep7.jpg')
    im.convert('RGB').save(out, quality=93)
    print(out)


def main():
    if os.environ.get('CAPA'):
        capa(); return
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep7_{float(v):05.2f}.png'))
        print('ok', NNEW, 'novos', [PEOPLE[i][0] for i in NEW7])
        return
    wav = os.path.join(OUTDIR, 'ep7.wav')
    audio(wav)
    out = os.path.join(OUTDIR, 'brasa-ep7.mp4')
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
