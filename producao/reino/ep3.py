#!/usr/bin/env python3
"""Brasa — Ep. 3 "As Pegadas". 44 moradores, meta do castelo, Rafaela volta com ervas, o cão da Ana Sofia fareja pegadas,
20 moradores novos no palco. Sem voz por padrão (TIMING3=json + VOICE=mp3 para narrar)."""
import os, math, random, subprocess, wave, json
import numpy as np
from PIL import Image, ImageDraw
import world2 as W
import folk as F
import build as B
import ep1hd as E
import ep2 as P

FW, FH, FPS = 1080, 1920, 30
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
WHITE, GOLD, GREY, TEAL = (255, 255, 255), (255, 208, 72), (200, 196, 220), (96, 226, 214)
N_FOLLOW = int(os.environ.get('N', '44'))
GOAL = 100
OLD = list(F.FOUNDERS)
NEW = list(F.NEW_EP2)
NAMED = OLD + NEW
ANON = max(0, N_FOLLOW - len(NAMED))
PEOPLE = NAMED + [(f'anon{k}', '') for k in range(ANON)]
NP = len(PEOPLE)
IDX = {n: i for i, (n, _) in enumerate(PEOPLE)}

# ---------------------------------------------------------------- tempo
S2, S3, S3B, S4, S4B, S5, S6, TEND = 3.4, 6.0, 8.4, 10.6, 12.8, 15.0, 21.0, 24.0
BATCH = 4
NB = math.ceil(len(NEW) / BATCH)
_tj = os.environ.get('TIMING3')
if _tj:
    _T = json.load(open(_tj))
    S2, S3, S3B, S4, S4B, S5, S6, TEND = [_T[k] for k in ('S2', 'S3', 'S3B', 'S4', 'S4B', 'S5', 'S6', 'TEND')]
STAGE0 = S5 + 0.8
BDUR = (S6 - STAGE0) / NB
POP0, POP1 = 0.25, 2.6
XF = 0.4


def tod(t):
    if t < S3:
        return 0.0
    if t < S4:
        return 0.95 + 0.3 * (t - S3) / (S4 - S3)
    if t < S5:
        return 1.3 + 0.5 * (t - S4) / (S5 - S4)
    return 2.0


# ---------------------------------------------------------------- multidão
def crowd_positions(n, seed=3):
    r = random.Random(seed)
    pts = []
    tries = 0
    while len(pts) < n and tries < 20000:
        tries += 1
        x, y = r.uniform(100, 262), r.uniform(398, 466)
        if ((x - 180) / 78) ** 2 + ((y - 434) / 38) ** 2 > 1:
            continue
        if ((x - 180) / 16) ** 2 + ((y - 424) / 8) ** 2 < 1:
            continue
        if any((x - a) ** 2 + ((y - b) * 1.6) ** 2 < 11 ** 2 for a, b in pts):
            continue
        pts.append((x, y))
    while len(pts) < n:
        pts.append((r.uniform(110, 250), r.uniform(400, 466)))
    return pts


CROWD = crowd_positions(NP)
POP_T = [POP0 + (POP1 - POP0) * k / max(1, NP - 1) for k in range(NP)]
ORDER_POP = sorted(range(NP), key=lambda i: (CROWD[i][1], CROWD[i][0]))
POP_AT = {i: POP_T[k] for k, i in enumerate(ORDER_POP)}
STAGE_X = [114, 158, 202, 246]
STAGE_Y = 486


def batch_of(t):
    if t < STAGE0 or t >= S6:
        return None
    return min(NB - 1, int((t - STAGE0) / BDUR))


# rastro de pegadas: da ponte até a praça
STEPS = []
_a, _b = (276, 268), (196, 396)
for k in range(26):
    q = k / 25
    x = _a[0] + (_b[0] - _a[0]) * q
    y = _a[1] + (_b[1] - _a[1]) * q
    side = 1 if k % 2 else -1
    STEPS.append((x + side * 2, y))


def steps_visible(t):
    if t < S3B:
        return 0
    if t < S4:
        return int(6 * W.clamp((t - S3B) / 1.2))
    if t < S5:
        return 6 + int(20 * W.clamp((t - S4B) / 1.6)) if t >= S4B else 6
    return len(STEPS)


def rafaela_pos(t):
    q = W.clamp((t - S3) / (S3B - S3 + 0.6))
    return 278 + (262 - 278) * q, 262 + (330 - 262) * q, (1 + int(t / 0.13) % 2) if q < 1 else 0


def dog_pos(t):
    q = W.clamp((t - S4) / (S4B - S4 + 1.6))
    k = int(q * 10)
    x, y = STEPS[min(len(STEPS) - 1, 4 + k)]
    return x + 6, y + 6, int(t * 6) % 2


def people_now(t):
    res = []
    b = batch_of(t)
    stage = set()
    if b is not None:
        for j, (n, r) in enumerate(NEW[b * BATCH:(b + 1) * BATCH]):
            stage.add(n)
    for i, (n, r) in enumerate(PEOPLE):
        if n == 'Rafaela' and S3 <= t < S4:
            x, y, fr = rafaela_pos(t)
            res.append((i, x, y, fr)); continue
        if n == 'Ana Sofia' and S4 <= t < S5:
            res.append((i, 252, 334, 0)); continue
        if n in stage:
            j = [m for m, _ in NEW[b * BATCH:(b + 1) * BATCH]].index(n)
            tin = STAGE0 + b * BDUR
            q = W.clamp((t - tin) / 0.25)
            x0, y0 = CROWD[i]
            x = x0 + (STAGE_X[j] - x0) * W.ease(q)
            y = y0 + (STAGE_Y - y0) * W.ease(q)
            res.append((i, x, y, (1 + int(t / 0.1) % 2) if q < 1 else 0)); continue
        x, y = CROWD[i]
        res.append((i, x, y, 0))
    return res


# ---------------------------------------------------------------- castelo-fantasma (meta)
def _castle():
    im = Image.new('L', (W.W, W.H), 0)
    d = ImageDraw.Draw(im)
    cx, base = 180, 236
    d.rectangle((cx - 40, base - 46, cx + 40, base), outline=255)
    for x in range(cx - 40, cx + 40, 10):
        d.rectangle((x, base - 52, x + 5, base - 46), outline=255)
    for tx in (cx - 54, cx + 40):
        d.rectangle((tx, base - 70, tx + 14, base), outline=255)
        d.polygon([(tx - 2, base - 70), (tx + 7, base - 86), (tx + 16, base - 70)], outline=255)
    d.rectangle((cx - 12, base - 92, cx + 12, base - 46), outline=255)
    d.polygon([(cx - 15, base - 92), (cx, base - 112), (cx + 15, base - 92)], outline=255)
    d.line((cx, base - 112, cx, base - 124), fill=255)
    d.polygon([(cx, base - 124), (cx + 9, base - 121), (cx, base - 118)], outline=255)
    d.rectangle((cx - 8, base - 20, cx + 8, base), outline=255)
    for wx in (cx - 30, cx + 22, cx - 4):
        d.rectangle((wx, base - 36, wx + 6, base - 28), outline=255)
    return np.argwhere(np.array(im) > 0)


CASTLE = _castle()
CASTLE = CASTLE[np.lexsort((CASTLE[:, 1], -CASTLE[:, 0]))]


def castle(out, t):
    if t < S2:
        return
    p = W.clamp((t - S2 - 0.2) / 0.9)
    n = int(len(CASTLE) * p)
    pulse = 0.75 + 0.25 * math.sin(t * 4)
    pts = CASTLE[:n]
    col = np.array((255, 214, 90), float)
    out[pts[:, 0], pts[:, 1]] = out[pts[:, 0], pts[:, 1]] * (1 - pulse) + col * pulse
    if p < 1 and n:
        y, x = pts[-1]
        out[y, x] = (255, 255, 255)


# ---------------------------------------------------------------- cena
def scene(t):
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
    B.smoke_at(img, t, 97, 300, seed=1); B.smoke_at(img, t, 285, 300, seed=2)
    fire_on = t >= S3
    if fire_on:
        W.smoke(img, t)
    ppl = people_now(t)
    dog_i = IDX['Ana Sofia']
    for i, x, y, fr in sorted(ppl, key=lambda p: p[2]):
        n, r = PEOPLE[i]
        W.ground_shadow(img, x, y)
        if r:
            W.blit(img, F.folk(n, r, fr), x, y)
        else:
            W.blit(img, F.folk(n, 'morador', fr), x, y)
        if i == dog_i and not (S4 <= t < S5):
            W.ground_shadow(img, x + 14, y)
            W.blit(img, F.make_dog(int(t * 3) % 2), x + 14, y)
    if S4 <= t < S5:
        dx_, dy_, fr = dog_pos(t)
        W.ground_shadow(img, dx_, dy_)
        W.blit(img, F.make_dog(fr), dx_, dy_)
    if S3 <= t < S4:   # cesta de ervas da Rafaela
        x, y, _ = rafaela_pos(t)
        for (bx, by, c) in [(5, -9, (150, 100, 56)), (6, -9, (150, 100, 56)), (7, -9, (150, 100, 56)), (5, -10, (90, 180, 80)),
                            (6, -11, (120, 210, 100)), (7, -10, (90, 180, 80)), (8, -10, (150, 100, 56)), (6, -8, (120, 80, 44))]:
            img[int(y) + by, int(x) + bx] = c
    s = W.sky(td, t)
    tint = W.keyinterp(W.TINT, td)
    tm = np.broadcast_to(tint, (W.H, W.W, 3)).copy()
    nf = W.clamp((td - 0.6) / 0.9)
    if fire_on:
        lv = (W.light_level(t) * nf)[..., None]
        tm = tm * (1 - lv) + np.array((1.06, 0.84, 0.66)) * lv
    if nf > 0:
        lv = (P.light_at(*P.LANT_C, 30, t) * nf * 0.9)[..., None]
        tm = tm * (1 - lv) + np.array((1.04, 0.86, 0.66)) * lv
        mx, my = 276, 254
        lv = (P.light_at(mx, my, 20, t) * 0.75 * nf)[..., None]
        tm = tm * (1 - lv) + np.array((0.55, 1.0, 0.9)) * lv
    if STAGE0 - 0.1 <= t < S6:
        lv = (P.light_at(180, STAGE_Y - 4, 104, t) * 0.85)[..., None]
        tm = tm * (1 - lv) + np.array((1.0, 0.92, 0.8)) * lv
    out = np.where(W.LMASK[..., None], img * tm, s)
    if fire_on:
        W.fire(out, t, scale=W.ease((t - S3) / 0.3))
    for name, spr in (('forja', B.FORJA), ('padaria', B.PADARIA), ('biblio', B.BIBLIO), ('lantern', B.LANTERN)):
        B.emissive(out, spr, *B.POS[name], strength=max(nf, 0.35 if name == 'forja' else 0) * 0.95, t=t)
    if td > 1.5:
        k = W.clamp((td - 1.5) / 0.4)
        for fx, fy, ph, f in P.FLIES:
            if math.sin(t * f + ph) > 0.2:
                x = int(fx + 4 * math.sin(t * 0.7 + ph)); y = int(fy + 2 * math.sin(t * 1.1 + ph * 2))
                out[y, x] = out[y, x] * (1 - k) + np.array((226, 255, 140)) * k
    if nf > 0.2 and not (S4 + 1.0 <= t < S4 + 1.12):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            out[254 + dy, 276 + dx] = (200, 255, 230)
    nst = steps_visible(t)
    for k in range(nst):
        x, y = STEPS[k]
        glow = 0.6 + 0.4 * math.sin(t * 5 + k)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (0, -1)):
            X, Y = int(x) + dx, int(y) + dy
            out[Y, X] = out[Y, X] * (1 - glow) + np.array((120, 255, 220)) * glow
    castle(out, t) if S2 <= t < S3 or t >= S6 else None
    if t < S2:   # brilho de quem acabou de chegar
        for i in range(NP):
            ts = POP_AT[i]
            if ts <= t < ts + 0.3:
                x, y = CROWD[i]
                yy_ = int(y) - 30
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    out[yy_ + dy, int(x) + dx] = (255, 240, 160)
    if S4 <= t < S5 and t >= S4B:
        x, y = 252, 334
        W.qmark(out, x - 3, y - 40, bang=True)
    return out, td


def shot(t):
    if t < S3:
        return ('wide', None)
    if t < S4:
        x, y, _ = rafaela_pos(t)
        return ('close', (x, y))
    if t < S5:
        return ('close', (262, 330))
    if t < STAGE0:
        return ('med', None)
    if t < S6:
        return ('close', (180, STAGE_Y))
    return ('med', None)


def view(sh):
    kind, c = sh
    if kind == 'wide':
        return 0, 0, 3
    if kind == 'med':
        return 44, 80, 4
    x, y = c
    return int(min(max(x - 108, 0), W.W - 216)), int(min(max(y - 250, 0), W.H - 384)), 5


# ---------------------------------------------------------------- textos
def short_role(r):
    r = r.split('(')[0].split('/')[0].strip()
    return r if len(r) <= 14 else r.split()[0]


CAPS = [
    (S2, S3, 270, [(S2, [(f'COM {GOAL} MORADORES,', WHITE)], 140), (S2 + 0.3, [('A GENTE CONSTRÓI', GOLD)], 150),
                   (S2 + 0.3, [('O CASTELO.', GOLD)], 170)]),
    (S3, S3B, 280, [(S3, [('A RAFAELA VOLTOU', WHITE)], 140), (S3, [('DA FLORESTA COM ERVAS', WHITE)], 120),
                    (S3 + 0.4, [('PRA CHÁS E REMÉDIOS…', GOLD)], 120)]),
    (S3B, S4, 300, [(S3B, [('…MAS ALGUÉM', WHITE)], 150), (S3B + 0.3, [('SEGUIU ELA.', TEAL)], 190)]),
    (S4, S4B, 290, [(S4, [('O CÃO DA ANA SOFIA', WHITE)], 140), (S4 + 0.3, [('FAREJOU AS PEGADAS…', GOLD)], 140)]),
    (S4B, S5, 290, [(S4B, [('…E ELAS VÃO', WHITE)], 150), (S4B + 0.3, [('ATÉ O REINO.', TEAL)], 180)]),
    (S5, S6, 270, [(S5, [(f'CHEGARAM {len(NEW)} MORADORES', WHITE)], 130), (S5 + 0.3, [('NOVOS:', GOLD)], 170)]),
    (S6, TEND + 1, 270, [(S6, [('SEGUE E COMENTA', WHITE)], 150), (S6, [('SEU NOME E SUA FUNÇÃO', GOLD)], 130),
                         (S6 + 0.4, [('PRA VIRAR MORADOR.', WHITE)], 110)]),
]


def overlay_state(t):
    st = []
    if t < S2:
        cnt = sum(1 for i in range(NP) if POP_AT[i] <= t)
        st.append(('count', NP))
    for ci, (a, b, y0, lines) in enumerate(CAPS):
        if a <= t < b:
            st.append(('cap', ci, sum(1 for ta, _, _ in lines if t >= ta)))
    if S2 + 0.6 <= t < S3 or t >= S6 + 0.6:
        st.append(('bar',))
    b = batch_of(t)
    if b is not None and t >= STAGE0 + b * BDUR + 0.2:
        st.append(('stage', b))
    if S4 + 0.6 <= t < S5:
        st.append(('bark', int(t * 2.5) % 2))
    return tuple(st)


_ov = {}


def overlay(state):
    if state in _ov:
        return _ov[state]
    im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for item in state:
        k = item[0]
        if k == 'count':
            E.draw_line(d, FW / 2, 300, [('ESTE REINO TEM', WHITE)], 150)
            E.draw_line(d, FW / 2, 300 + 0.78 * 150 + 10, [(f'{item[1]} MORADORES.', GOLD)], 200)
        elif k == 'cap':
            _, ci, nvis = item
            a, b, y, lines = CAPS[ci]
            for j, (ta, segs, size) in enumerate(lines):
                sz = E.fit(segs, size)
                if j > 0 and any(ch in 'ÁÉÍÓÚÂÊÔÃÕ' for s_, _ in segs for ch in s_):
                    y += 0.17 * sz
                if j < nvis:
                    E.draw_line(d, FW / 2, y, segs, size)
                y += 0.54 * sz + 0.24 * sz + 10
        elif k == 'bar':
            x0, y0, x1, y1 = 170, 720, 910, 830
            E.panel(d, (x0, y0, x1, y1))
            d.text((x0 + 36, y0 + 30), 'MORADORES', font=E.font(54), fill=WHITE + (255,), anchor='lm')
            d.text((x1 - 36, y0 + 30), f'{N_FOLLOW} / {GOAL}', font=E.font(54), fill=GOLD + (255,), anchor='rm')
            bx0, by0, bx1, by1 = x0 + 36, y0 + 62, x1 - 36, y0 + 92
            d.rectangle((bx0, by0, bx1, by1), fill=(60, 50, 80, 255))
            fill = bx0 + (bx1 - bx0) * min(1, N_FOLLOW / GOAL)
            d.rectangle((bx0, by0, fill, by1), fill=(255, 190, 60, 255))
            for xx_ in range(int(bx0), int(fill), 18):
                d.rectangle((xx_, by0, xx_ + 8, by0 + 8), fill=(255, 230, 140, 255))
        elif k == 'stage':
            b = item[1]
            for j, (n, r) in enumerate(NEW[b * BATCH:(b + 1) * BATCH]):
                cx = (STAGE_X[j] - 72) * 5
                fy = (STAGE_Y - (STAGE_Y - 250)) * 5
                nm, rl = n.upper(), short_role(r).upper()
                f1 = 58
                while E.font(f1).getlength(nm) > 200 and f1 > 34:
                    f1 -= 4
                f2 = 38
                while E.font(f2).getlength(rl) > 200 and f2 > 26:
                    f2 -= 2
                w = max(E.font(f1).getlength(nm), E.font(f2).getlength(rl)) + 30
                top = fy + 40
                d.polygon([(cx - 12, top + 2), (cx + 12, top + 2), (cx, top - 16)], fill=(250, 236, 200, 255))
                E.panel(d, (cx - w / 2, top, cx + w / 2, top + 110), b=5)
                d.text((cx, top + 36), nm, font=E.font(f1), fill=GOLD + (255,), anchor='mm')
                d.text((cx, top + 80), rl, font=E.font(f2), fill=(240, 236, 250, 255), anchor='mm')
        elif k == 'bark':
            dx_, dy_ = 252 + 16, 334
            X, Y = (dx_ - 154) * 5, (dy_ - 80 - 40) * 5
            txt = 'AU! AU!' if item[1] == 0 else 'AU!'
            E.draw_line(d, X, Y, [(txt, WHITE)], 96, stroke=6)
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
    f = P.camera(c, view(shot(t)))
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
            blip(ta, 988, g=0.05)
    for k, ts in enumerate(sorted(POP_AT.values())):
        blip(ts, 700 + 900 * k / NP, d=0.03, g=0.05, duty=0.25)
    for k, m in enumerate([62, 66, 69, 74, 78, 81]):   # fanfarra do castelo
        nn = int(0.12 * SR)
        E.add(s, S2 + 0.25 + k * 0.09, E.sq(E.midi(m + 12), nn, 0.25) * E.adsr(nn), 0.08)
    for k in range(int((S3B - S3) / 0.26)):   # passos
        nn = int(0.04 * SR)
        E.add(s, S3 + 0.1 + k * 0.26, E.lp(E.noise(nn, 70 + k), 0.12) * np.exp(-np.arange(nn) / SR * 70), 0.35)
    nn = int(1.6 * SR)
    tt = np.arange(nn) / SR
    hum = (np.sin(2 * math.pi * 98 * tt) + 0.6 * np.sin(2 * math.pi * 147 * tt)) * (0.6 + 0.4 * np.sin(2 * math.pi * 3 * tt))
    E.add(s, S3B, hum * np.sin(math.pi * tt / 1.6), 0.13)
    E.add(s, S4B, hum * np.sin(math.pi * tt / 1.6), 0.13)

    def bark(t0):
        nn = int(0.14 * SR)
        tt = np.arange(nn) / SR
        f = 620 * np.exp(-tt * 6)
        y = np.sign(np.sin(2 * math.pi * np.cumsum(f) / SR)) * 0.5 + E.noise(nn, int(t0 * 77)) * 0.5
        E.add(s, t0, E.lp(y, 0.25) * np.exp(-tt * 18), 0.4)
    t = S4 + 0.6
    while t < S5 - 0.2:
        bark(t); bark(t + 0.18)
        t += 0.8
    for b in range(NB):   # palco: plim por lote
        t0 = STAGE0 + b * BDUR + 0.2
        for j, m in enumerate((79, 83, 86, 91)):
            nn = int(0.09 * SR)
            E.add(s, t0 + j * 0.06, E.sq(E.midi(m), nn, 0.25) * E.adsr(nn, dec=0.05, sus=0.2), 0.08)
    r = random.Random(4)
    t = S3 + 0.1
    while t < TEND:
        nn = int(r.uniform(0.004, 0.012) * SR)
        E.add(s, t, E.noise(nn, int(t * 1000)) * np.exp(-np.arange(nn) / SR * 400), 0.05 * r.uniform(0.4, 1))
        t += r.uniform(0.03, 0.16)
    t = S4
    while t < TEND:
        for k in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.02)
        t += r.uniform(0.55, 0.95)
    return s


def audio(path):
    total = TEND
    E.T4, E.T6, E.T7 = S3, S4, S5
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
            Image.fromarray(frame(float(v))).save(os.path.join(OUTDIR, f'ep3_{float(v):05.2f}.png'))
        return
    wav = os.path.join(OUTDIR, 'ep3.wav')
    audio(wav)
    out = os.path.join(OUTDIR, os.environ.get('NAMEOUT', 'brasa-ep3.mp4'))
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
