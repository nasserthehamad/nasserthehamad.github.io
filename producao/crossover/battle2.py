#!/usr/bin/env python3
"""Batalha de Séries #2 — Kuririn x Naruto. No narration: text + beat + SFX. Reuses cross.py helpers."""
import os, sys, math, random, subprocess, wave, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/crossover'); sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch')
import cross as C
import make as M
import laudio as LA
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, tracked, rich_line, WHITE, INK

W, H, FPS, S, SR = 1080, 1920, 30, 2, 44100
OUT = '/home/claude/crossover/b2'
os.makedirs(OUT, exist_ok=True)
KUR, NAR = (245, 128, 24), (44, 112, 214)
C.DEX, C.JAN = KUR, NAR
YEL = (255, 214, 77)

C.SENTS = {
    'v1': ['KURIRIN x NARUTO.', 'Quem ganha numa luta de verdade?'],
    'v2': ['Sem Goku pra salvar ninguém.', 'Os dois no auge, numa luta até o fim.'],
    'v3': ['Rodada 1: velocidade.', 'No Dragon Ball, até o Kuririn se move mais rápido do que o olho consegue ver.', 'Ponto pro Kuririn.'],
    'v4': ['Rodada 2: estratégia.', 'O Naruto cria centenas de clones e ataca de todos os lados.', 'O Kuririn nunca enfrentou nada assim.', 'Ponto pro Naruto.'],
    'v5': ['Rodada 3: poder destrutivo.', 'Os fãs de Dragon Ball juram que até o Kuririn explode um planeta.', 'O Naruto destrói montanhas.', 'Dois a um pro Kuririn.'],
    'v6': ['Rodada final: resistência.', 'O Naruto nunca desiste. E se cura de quase tudo.', 'O Kuririn… é famoso por morrer.', 'Dois a dois.'],
    'v7': ['Desempate: a escala.', 'No Dragon Ball, até o mais fraco do time já lutou num torneio dos deuses.', 'Vitória do Kuririn.', 'Discorda? Comenta quem ganha.'],
}
C.HIGHLIGHT = {('v3', 2): KUR, ('v4', 3): NAR, ('v5', 3): KUR, ('v6', 3): WHITE, ('v7', 2): KUR, ('v7', 3): YEL}
LEAD = C.LEAD = 0.35
TAIL = {'v1': 0.5, 'v2': 0.5, 'v3': 0.8, 'v4': 0.8, 'v5': 0.8, 'v6': 0.8, 'v7': 2.4}

def synth_timing():
    T = {}
    for k in C.ORDER:
        st, du, acc = [], [], 0.0
        for s in C.SENTS[k]:
            n = len(s.split())
            d = max(1.5, 0.55 + 0.3 * n)
            st.append(acc); du.append(d - 0.25); acc += d
        T[k] = {'a': 0, 'b': acc, 'L': acc, 'st': st, 'du': du}
    return T

# ------------------------------------------------------------ overrides of cross.py art
def split_bg(cut=0.5):
    w, h = W * S, H * S
    left = vgrad(w, h, (150, 64, 6), (40, 14, 2))
    right = vgrad(w, h, (16, 54, 130), (4, 12, 34))
    m = Image.new('L', (w, h), 0)
    x_top = lerp(-400, W + 400, cut) + 160; x_bot = x_top - 320
    ImageDraw.Draw(m).polygon(P(x_top, -10, W + 500, -10, W + 500, H + 10, x_bot, H + 10), fill=255)
    img = left.copy(); img.paste(right, (0, 0), m)
    ImageDraw.Draw(img).line(P(x_top, -10, x_bot, H + 10), fill=(250, 250, 255), width=14 * S)
    return down(img).convert('RGBA')

def dark_bg():
    img = vgrad(W * S, H * S, (16, 14, 24), (5, 5, 9))
    img = glow(img, lambda d: d.ellipse(P(-500, 300, 400, 1500), fill=110), (110, 46, 4), 140 * S)
    img = glow(img, lambda d: d.ellipse(P(680, 300, 1580, 1500), fill=110), (10, 36, 100), 140 * S)
    return down(img).convert('RGBA')

def build_score_base():
    im = Image.new('RGBA', (W * S, 140 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for (x0, x1, col, name, ax) in ((60, 530, KUR, 'KURIRIN', 116), (550, 1020, NAR, 'NARUTO', 606)):
        d.rounded_rectangle(P(x0, 20, x1, 120), radius=50 * S, fill=col)
        d.text(P(ax, 70), name, font=F('InterDisplay-Black', 50 * S), fill=(255, 255, 255), anchor='lm')
    return down(im)

def kicker():
    txt = tracked('BATALHA DE SÉRIES  ·  #2', F('Inter-SemiBold', 30), (236, 236, 244, 235), 5)
    im = Image.new('RGBA', (txt.width + 34, txt.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); cy = txt.height // 2 + 1
    d.ellipse((4, cy - 8, 12, cy + 8), fill=KUR + (255,)); d.ellipse((12, cy - 8, 20, cy + 8), fill=NAR + (255,))
    im.alpha_composite(txt, (26, 0))
    return im

def build_win():
    a = C.text_img('VITÓRIA', 120, WHITE); b = C.text_img('DO KURIRIN', 132, WHITE, stroke=10)
    im = Image.new('RGBA', (max(a.width, b.width), a.height + b.height - 30), (0, 0, 0, 0))
    im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height - 30))
    return im

C.split_bg, C.dark_bg, C.build_score_base, C.kicker, C.build_win = split_bg, dark_bg, build_score_base, kicker, build_win

def header(im, t, small, big, t0=0.0):
    p = eo((t - t0) / 0.35) if t >= t0 else 0
    if p <= 0: return
    a_ = C.text_img(small, 44, (220, 220, 232), 'InterDisplay-Bold', 5)
    b_ = C.text_img(big, 104, WHITE)
    if b_.width > 1000: b_ = b_.resize((1000, int(b_.height * 1000 / b_.width)), Image.LANCZOS)
    comp(im, a_, ((W - a_.width) / 2, 440 - (1 - p) * 20), p)
    s_ = lerp(1.25, 1.0, p)
    b2 = b_ if s_ == 1 else b_.resize((int(b_.width * s_), int(b_.height * s_)), Image.BILINEAR)
    comp(im, b2, ((W - b2.width) / 2, 500 + (b_.height - b2.height) / 2), p)
C.header = header

def finish(im, t, k, flash_ev=None, flash_col=None):
    if flash_ev is not None: im = C.flash(im, t, [flash_ev], flash_col)
    C.score_frame(im, t)
    im = M.apply_mult(im, C.MULT)
    comp(im, C.KICK, ((W - C.KICK.width) // 2, 196))
    C.CAP[k].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v1: hook (names)
def frame_v1(t):
    im = C.SPLIT.copy()
    p1 = eo(t / 0.4); p2 = eo((t - 0.15) / 0.4)
    comp(im, NAME_K, (40 - (1 - p1) * 500, 560), p1)
    comp(im, NAME_N, (W - NAME_N.width - 40 + (1 - p2) * 500, 1040), p2)
    if t >= 0.35:
        s = max(0.01, C.backout((t - 0.35) / 0.4))
        v = C.VS.resize((max(1, int(C.VS.width * s)), max(1, int(C.VS.height * s))), Image.BILINEAR)
        comp(im, v, (540 - v.width / 2 + M.shake(t, [0.45], 10, freq=18, tau=0.08), 860 - v.height / 2))
    im = M.apply_mult(im, C.MULT)
    comp(im, C.KICK, ((W - C.KICK.width) // 2, 196))
    C.CAP['v1'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v2: neutral arena
def build_arena():
    w, h = W * S, H * S
    img = vgrad(w, h, (40, 22, 60), (230, 120, 70), 0, 1150 * S)
    img = glow(img, lambda d: d.ellipse(P(380, 900, 700, 1220), fill=255), (255, 190, 110), 60 * S)
    d = ImageDraw.Draw(img)
    rng = random.Random(8)
    for (x0, x1, top) in ((-40, 300, 820), (240, 520, 960), (640, 900, 880), (840, 1140, 780)):
        pts = [(x0, 1160)]
        n = 6
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n; y = top + rng.uniform(-40, 60) + (abs(i - n / 2) / (n / 2)) * 120
            pts.append((x, y))
        pts.append((x1, 1160))
        d.polygon([tuple(P(*p)) for p in pts], fill=(50, 26, 40))
    img.paste(vgrad(w, (H - 1150) * S, (90, 50, 46), (20, 10, 12)), (0, 1150 * S)); d = ImageDraw.Draw(img)
    for _ in range(40):
        x = rng.uniform(0, W); y = rng.uniform(1170, H); r = rng.uniform(6, 30)
        d.ellipse(P(x - r, y - r * 0.4, x + r, y + r * 0.4), fill=(70, 38, 36))
    return down(img).convert('RGBA')

def frame_v2(t):
    im = ARENA.copy()
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = random.Random(3)
    for i in range(50):
        x = (rng.uniform(0, W) + t * rng.uniform(30, 90)) % W; y = rng.uniform(900, 1700) - t * rng.uniform(5, 20)
        r = rng.uniform(1.5, 4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 220, 180, 90))
    im.alpha_composite(lay)
    comp(im, ARENA_TAG, ((W - ARENA_TAG.width) / 2, 440), eo(t / 0.4))
    t1 = C.ts('v2', 1) + 0.4
    if t >= t1:
        q = (t - t1) / 0.18; s = lerp(1.8, 1.0, eo(q))
        st = STAMP_FIM.resize((int(STAMP_FIM.width * s), int(STAMP_FIM.height * s)), Image.BILINEAR)
        comp(im, st, (540 - st.width / 2, 860 - st.height / 2), clamp(q * 2))
        sy = M.shake(t, [t1 + 0.18], 12, freq=16, tau=0.07)
        if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = M.apply_mult(im, C.MULT)
    comp(im, C.KICK, ((W - C.KICK.width) // 2, 196))
    C.CAP['v2'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v3: speed gauge
def frame_v3(t):
    im = C.DARK.copy()
    C.header(im, t, 'RODADA 1', 'VELOCIDADE')
    cx, cy, R = 540, 1040, 270
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.arc((cx - R, cy - R, cx + R, cy + R), 180, 360, fill=(70, 70, 86, 255), width=34)
    t1 = C.ts('v3', 1) + 0.3
    v = 0.15 if t < t1 else min(1.05, 0.15 + 0.9 * eo((t - t1) / 1.2)) + (0.02 * math.sin(t * 40) if t > t1 + 1.2 else 0)
    d.arc((cx - R, cy - R, cx + R, cy + R), 180, 180 + 180 * min(v, 1.0), fill=KUR + (255,), width=34)
    for i in range(11):
        a = math.radians(180 + 18 * i)
        d.line((cx + (R - 40) * math.cos(a), cy + (R - 40) * math.sin(a), cx + (R - 70) * math.cos(a), cy + (R - 70) * math.sin(a)), fill=(220, 220, 230, 255), width=6)
    a = math.radians(180 + 180 * min(v, 1.0))
    d.line((cx, cy, cx + (R - 60) * math.cos(a), cy + (R - 60) * math.sin(a)), fill=(255, 255, 255, 255), width=12)
    d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(255, 255, 255, 255))
    if v > 0.9:
        rng = random.Random(int(t * 30))
        for _ in range(14):
            y = rng.uniform(720, 1200); x = rng.uniform(0, W); L = rng.uniform(120, 360)
            d.line((x, y, x + L, y), fill=(255, 220, 160, 120), width=4)
    im.alpha_composite(lay)
    if v > 0.9:
        comp(im, MAX_TAG, ((W - MAX_TAG.width) / 2, 1100), clamp((v - 0.9) * 8))
    return finish(im, t, 'v3', C.ts('v3', 2), KUR)

# ------------------------------------------------------------ v4: clones (pawns multiplying)
def build_pawn(col):
    im = Image.new('RGBA', (120 * S, 200 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse(P(32, 6, 88, 62), fill=col); d.polygon(P(44, 56, 76, 56, 92, 150, 28, 150), fill=col)
    d.rounded_rectangle(P(12, 146, 108, 194), radius=14 * S, fill=col)
    return down(im)

PAWN_POS = []
def frame_v4(t):
    im = C.DARK.copy()
    C.header(im, t, 'RODADA 2', 'ESTRATÉGIA')
    t1 = C.ts('v4', 1) + 0.2
    n = 1 if t < t1 else min(len(PAWN_POS), 1 + int(eio((t - t1) / 1.6) * (len(PAWN_POS) - 1)))
    for i in range(n):
        x, y, s = PAWN_POS[i]
        p = PAWN_N if s == 1.0 else PAWN_N.resize((int(PAWN_N.width * s), int(PAWN_N.height * s)), Image.BILINEAR)
        comp(im, p, (x - p.width / 2, y - p.height))
    t2 = C.ts('v4', 2)
    if t >= t2:
        p = eo((t - t2) / 0.3)
        comp(im, PAWN_K, (540 - PAWN_K.width / 2, 1270 - PAWN_K.height + (1 - p) * 40), p)
        comp(im, Q_TAG, (540 + 60, 1050), p)
    return finish(im, t, 'v4', C.ts('v4', 3), NAR)

# ------------------------------------------------------------ v5: planet vs mountain
def frame_v5(t):
    im = C.DARK.copy()
    C.header(im, t, 'RODADA 3', 'PODER DESTRUTIVO')
    t1 = C.ts('v5', 1) + 1.0
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy, R = 330, 960, 170
    burst = clamp((t - t1) / 0.6) if t >= t1 else 0
    if burst < 1:
        d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(60, 120, 200, 255))
        for (a, b, c_, e) in [(cx - 120, cy - 80, cx - 10, cy + 10), (cx + 20, cy - 30, cx + 130, cy + 90), (cx - 60, cy + 60, cx + 40, cy + 140)]:
            d.ellipse((a, b, c_, e), fill=(70, 160, 90, 255))
        if t >= t1 - 0.5:
            k = clamp((t - t1 + 0.5) / 0.5)
            for ang in range(0, 360, 45):
                a = math.radians(ang + 10)
                d.line((cx, cy, cx + R * k * math.cos(a), cy + R * k * math.sin(a)), fill=(255, 200, 80, 255), width=6)
    if burst > 0:
        rr = R + 170 * eo(burst)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 190, 80, int(220 * (1 - burst))))
        rng = random.Random(4)
        for _ in range(16):
            a = rng.uniform(0, 2 * math.pi); dist = R * 0.4 + 200 * eo(burst) * rng.uniform(0.6, 1.2); r = rng.uniform(10, 28) * (1 - burst * 0.5)
            d.polygon([(cx + dist * math.cos(a) + r * math.cos(a + k2), cy + dist * math.sin(a) + r * math.sin(a + k2)) for k2 in (0, 2.1, 4.2)], fill=(80, 90, 110, int(255 * (1 - burst * 0.6))))
    t2 = C.ts('v5', 2)
    mx, my = 790, 1150
    if t >= t2:
        p = eo((t - t2) / 0.4)
        d.polygon([(mx - 170, my), (mx - 30, my - 300 * p), (mx + 60, my - 200 * p), (mx + 170, my)], fill=(120, 110, 130, 255))
        d.polygon([(mx - 30, my - 300 * p), (mx - 70, my - 230 * p), (mx + 5, my - 240 * p)], fill=(240, 240, 250, 255))
    im.alpha_composite(lay)
    sy = M.shake(t, [t1], 16, freq=15, tau=0.1)
    if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    return finish(im, t, 'v5', C.ts('v5', 3), KUR)

# ------------------------------------------------------------ v6: heart vs skull counter
def frame_v6(t):
    im = C.DARK.copy()
    C.header(im, t, 'RODADA FINAL', 'RESISTÊNCIA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    t1 = C.ts('v6', 1)
    if t >= t1:
        beat = 1 + 0.08 * max(0, math.sin(2 * math.pi * (t - t1) * 1.4)) ** 6
        hx, hy, r = 760, 960, 70 * beat
        d.ellipse((hx - r - r * 0.9, hy - r, hx - r * 0.9 + r, hy + r), fill=NAR + (255,))
        d.ellipse((hx + r * 0.9 - r, hy - r, hx + r * 0.9 + r, hy + r), fill=NAR + (255,))
        d.polygon([(hx - 2 * r, hy + 10), (hx + 2 * r, hy + 10), (hx, hy + 2.3 * r)], fill=NAR + (255,))
    t2 = C.ts('v6', 2)
    if t >= t2:
        sx, sy_ = 320, 960
        d.ellipse((sx - 95, sy_ - 110, sx + 95, sy_ + 60), fill=(236, 236, 242, 255))
        d.rounded_rectangle((sx - 60, sy_ + 30, sx + 60, sy_ + 120), radius=14, fill=(236, 236, 242, 255))
        d.ellipse((sx - 60, sy_ - 50, sx - 14, sy_ + 4), fill=(16, 14, 22, 255)); d.ellipse((sx + 14, sy_ - 50, sx + 60, sy_ + 4), fill=(16, 14, 22, 255))
        d.polygon([(sx, sy_ + 14), (sx - 14, sy_ + 40), (sx + 14, sy_ + 40)], fill=(16, 14, 22, 255))
        for k in (-36, -12, 12, 36): d.line((sx + k, sy_ + 70, sx + k, sy_ + 118), fill=(16, 14, 22, 255), width=6)
    im.alpha_composite(lay)
    if t >= t2:
        q = t - t2
        n = 1 + int(q * 4)
        lab = 'MORTES: ' + str(n) if q < 1.1 else 'MORTES: PERDEMOS A CONTA'
        f = F('InterDisplay-Black', 50)
        ImageDraw.Draw(im).text((540, 1190), lab, font=f, fill=KUR, anchor='mm', stroke_width=6, stroke_fill=INK)
    return finish(im, t, 'v6', C.ts('v6', 3), WHITE)

# ------------------------------------------------------------ v7: verdict (reuse cross.frame_v7 with new art)
def frame_v7(t):
    tw = C.ts('v7', 2)
    if t < tw: im = C.SPLIT.copy()
    elif t - tw < 0.55: im = split_bg(lerp(0.5, 1.3, eio((t - tw) / 0.5)))
    else: im = SPLIT_K.copy()
    C.header(im, t, 'DESEMPATE', 'QUEM VENCE?')
    if t >= tw + 0.3:
        s = C.backout((t - tw - 0.3) / 0.45)
        v = C.WIN.resize((max(1, int(C.WIN.width * s)), max(1, int(C.WIN.height * s))), Image.BILINEAR)
        comp(im, v, (540 - v.width / 2, 860 - v.height / 2))
    im = C.flash(im, t, [tw + 0.3], (255, 255, 255), 0.4, 0.5)
    C.score_frame(im, t)
    t3 = C.ts('v7', 3) + 0.6
    if t >= t3:
        p = C.backout((t - t3) / 0.45)
        comp(im, C.FOLLOW, ((W - C.FOLLOW.width) / 2, 1130 + (1 - p) * 30), clamp((t - t3) * 4))
    im = M.apply_mult(im, C.MULT)
    comp(im, C.KICK, ((W - C.KICK.width) // 2, 196))
    C.CAP['v7'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ sound (beat, no narration)
def make_audio(path, starts, total, events):
    n = int(total * SR); t = np.arange(n) / SR
    out = np.zeros(n + 3 * SR)
    def add(sig, at, g=1.0):
        i = int(at * SR)
        if 0 <= i < n: out[i:i + len(sig)] += sig * g
    K, Cl, Hh = LA.kick(), LA.clap(), LA.hat()
    bpm = 140; beat = 60 / bpm
    notes = [36, 36, 43, 41]
    for b in range(int(total / beat)):
        tb = b * beat; bar = b // 8; pos = b % 8
        if pos in (0, 3, 6): add(K, tb, 0.8)
        if pos in (4,): add(Cl, tb, 0.45)
        for k in range(2): add(Hh, tb + k * beat / 2, 0.12 if k else 0.08)
        if b % 3 == 2: add(Hh, tb + beat * 0.75, 0.07)
        if pos == 0:
            f = LA.mid(notes[bar % 4]); tq = np.arange(int(beat * 7 * SR)) / SR
            add(np.sin(2 * np.pi * np.cumsum(f * (1 + 0.04 * np.exp(-tq / 0.05))) / SR) * np.exp(-tq / 1.6) * 0.5, tb)
    for k in C.ORDER[1:]: add(LA.whoosh(0.4, 0.35), starts[k] - 0.2)
    add(LA.tada(0.35), starts['v1'] + 0.35)
    add(LA.thunk(), starts['v2'] + C.ts('v2', 1) + 0.58, 1.2)
    for (te, sd, v) in events:
        add(LA.ding(1318.5 if sd == 'j' else 987.8, 0.4), te); add(LA.kick(), te, 1.0)
    add(LA.crash(1.8), starts['v5'] + C.ts('v5', 1) + 1.0); add(LA.kick(), starts['v5'] + C.ts('v5', 1) + 1.0, 1.4)
    for i in range(5): add(LA.blip(500 + 80 * i, 900 + 80 * i, 0.08, 0.25), starts['v6'] + C.ts('v6', 2) + i * 0.25)
    add(LA.crash(1.6), starts['v7'] + C.ts('v7', 2) + 0.3); add(LA.tada(0.45), starts['v7'] + C.ts('v7', 2) + 0.3)
    out = out[:n]
    out *= np.clip((total - t) / 0.8, 0, 1) * np.clip(t / 0.05, 0, 1)
    out = np.tanh(out * 1.2) / 1.2
    out *= 0.92 / np.abs(out).max()
    st = np.stack([out, out], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------ main
if __name__ == '__main__':
    mode = sys.argv[1]
    C.T = synth_timing()
    C.DURS = {k: C.r30(LEAD + C.T[k]['L'] + TAIL[k]) for k in C.ORDER}
    print('durs', C.DURS, 'total', round(sum(C.DURS.values()), 1))
    C.setup()
    NAME_K = C.text_img('KURIRIN', 150, WHITE, stroke=10); NAME_N = C.text_img('NARUTO', 170, WHITE, stroke=10)
    SPLIT_K = split_bg(1.3)
    ARENA = build_arena(); ARENA_TAG = C.text_img('ARENA NEUTRA', 52, WHITE, 'InterDisplay-ExtraBold', 6)
    STAMP_FIM = C.build_stamp('LUTA ATÉ O FIM', (255, 214, 77))
    MAX_TAG = C.text_img('VELOCIDADE MÁXIMA', 60, KUR, 'InterDisplay-Black', 7)
    PAWN_N, PAWN_K = build_pawn(NAR), build_pawn(KUR)
    PAWN_K = PAWN_K.resize((int(PAWN_K.width * 1.3), int(PAWN_K.height * 1.3)), Image.BILINEAR)
    Q_TAG = C.text_img('?!', 80, WHITE, 'InterDisplay-Black', 7)
    rng = random.Random(11)
    PAWN_POS = [(540, 1000, 1.0)]
    for i in range(44):
        y = rng.uniform(760, 1260); s = lerp(0.55, 1.05, (y - 760) / 500)
        PAWN_POS.append((rng.uniform(80, 1000), y + 40, s))
    PAWN_POS = [PAWN_POS[0]] + sorted(PAWN_POS[1:], key=lambda p: p[1])
    C.build_caps()
    LOCAL = {'v3': [(C.ts('v3', 2), 'd', 1)], 'v4': [(-1, 'd', 1), (C.ts('v4', 3), 'j', 1)],
             'v5': [(-1, 'd', 1), (-1, 'j', 1), (C.ts('v5', 3), 'd', 2)],
             'v6': [(-1, 'd', 2), (-1, 'j', 1), (C.ts('v6', 3), 'j', 2)],
             'v7': [(-1, 'd', 2), (-1, 'j', 2), (C.ts('v7', 2) + 0.3, 'd', 3)]}
    FR = {'v1': frame_v1, 'v2': frame_v2, 'v3': frame_v3, 'v4': frame_v4, 'v5': frame_v5, 'v6': frame_v6, 'v7': frame_v7}
    def scene_fn(k):
        def fn(t):
            C.SCORE_EVENTS = LOCAL.get(k, [])
            return FR[k](t)
        return fn
    if mode == 'preview':
        shots = [('v1', 1.5), ('v2', C.ts('v2', 1) + 1.0), ('v3', C.ts('v3', 1) + 2.0), ('v4', C.ts('v4', 2) + 0.8),
                 ('v5', C.ts('v5', 1) + 1.3), ('v6', C.ts('v6', 2) + 1.4), ('v7', C.ts('v7', 2) + 1.0), ('v7', C.DURS['v7'] - 0.5)]
        th = []
        for i, (k, tt_) in enumerate(shots):
            im = scene_fn(k)(tt_); th.append(im.resize((W // 4, H // 4), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 4 * 4, H // 4 * 2))
        for i, im in enumerate(th): sheet.paste(im, ((i % 4) * (W // 4), (i // 4) * (H // 4)))
        sheet.save(f'{OUT}/sheet.png'); print('ok')
    else:
        C.OUT = OUT
        for idx, k in enumerate(C.ORDER):
            C.encode(k, scene_fn(k), C.DURS[k], fade_in=0, fade_out=12 if idx == len(C.ORDER) - 1 else 0)
        starts, acc = {}, 0.0
        for k in C.ORDER: starts[k] = acc; acc += int(round(C.DURS[k] * FPS)) / FPS
        ev = [(starts[k] + te, sd, v) for k, evs in LOCAL.items() for (te, sd, v) in evs if te >= 0]
        make_audio(f'{OUT}/audio.wav', starts, acc, ev)
        with open(f'{OUT}/list.txt', 'w') as fl:
            for k in C.ORDER: fl.write(f"file '{k}.mp4'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video.mp4'], check=True)
        final = f'{OUT}/batalha-kuririn-x-naruto.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final + '.part.mp4'], check=True)
        os.replace(final + '.part.mp4', final)
        print('done', acc)
