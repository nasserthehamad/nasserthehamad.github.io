#!/usr/bin/env python3
"""Batalha de Séries #1 — Patrick Jane x Dexter Morgan. Typographic versus format (no character art).
Usage: cross.py preview|render narr.mp3   (env BOUNDS = 6 scene-pause start times)"""
import os, sys, math, random, subprocess, wave, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch')
import make as M
import laudio as LA
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, tracked, rich_line, WHITE, WARM, INK

W, H, FPS, S = 1080, 1920, 30, 2
OUT = '/home/claude/crossover'
SR = 44100
LEAD = 0.3
DEX, DEX_D = (214, 38, 48), (70, 8, 14)
JAN, JAN_D = (44, 134, 214), (8, 32, 80)
YEL = (255, 204, 77)

def backout(x, c1=1.70158):
    x = clamp(x); c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

ORDER = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7']
SENTS = {
    'v1': ['Patrick Jane contra Dexter Morgan.', 'Quem descobriria o outro primeiro?'],
    'v2': ['Imagina: o Jane é chamado pra ajudar a polícia de Miami num caso de desaparecimentos.', 'E o perito do caso… é o Dexter.'],
    'v3': ['Rodada um: ler pessoas.', 'O Dexter passou a vida inteira ensaiando ser normal.',
           'Mas o Jane percebe o que ninguém percebe: o sorriso dele chega meio segundo atrasado.', 'Ponto pro Jane.'],
    'v4': ['Rodada dois: as provas.', 'Só que quem analisa o sangue… é o próprio Dexter.', 'Ele decide o que a prova diz.', 'Ponto pro Dexter.'],
    'v5': ['Rodada três: a armadilha.', 'O Jane é mestre em fazer culpado se entregar.', 'O problema? O Dexter não sente culpa.', 'Dois a um pro Dexter.'],
    'v6': ['Rodada final: o jogo mental.', 'O Jane não precisa provar nada.', 'Ele só precisa que o Dexter ache que foi descoberto.',
           'E aí… o Dexter erra.', 'Dois a dois.'],
    'v7': ['Desempate: o Dexter ainda tem muito a perder.', 'O Jane… já perdeu tudo.', 'Vitória do Jane.', 'Discorda? Comenta quem ganha.'],
}
HIGHLIGHT = {('v3', 3): JAN, ('v4', 3): DEX, ('v5', 3): DEX, ('v6', 4): WHITE, ('v7', 2): JAN, ('v7', 3): YEL}
MINS = {'v1': 4.0, 'v2': 5.0, 'v3': 6.0, 'v4': 5.0, 'v5': 5.0, 'v6': 6.0, 'v7': 7.0}
TAIL = {'v1': 0.7, 'v2': 0.9, 'v3': 1.0, 'v4': 1.0, 'v5': 1.0, 'v6': 1.0, 'v7': 2.2}

# ------------------------------------------------------------ narration analysis
def analyse(path, bounds_at):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    hop = int(0.01 * SR)
    rms = np.sqrt(np.convolve(x * x, np.ones(hop * 3) / (hop * 3), 'same'))[::hop]
    loud = 20 * np.log10(rms / rms.max() + 1e-9) > -38
    runs, i = [], 0
    while i < len(loud):
        if not loud[i]:
            j = i
            while j < len(loud) and not loud[j]: j += 1
            runs.append((i * 0.01, j * 0.01)); i = j
        else:
            i += 1
    first = next(k for k in range(len(loud)) if loud[k]) * 0.01
    last = (len(loud) - next(k for k in range(len(loud)) if loud[::-1][k])) * 0.01
    inner = [r for r in runs if r[0] > first and r[1] < last]
    if bounds_at:
        bounds = [min(inner, key=lambda r: abs(r[0] - t)) for t in bounds_at]
    else:
        bounds = sorted(sorted(inner, key=lambda r: r[1] - r[0], reverse=True)[:len(ORDER) - 1])
    segs, s0 = [], first
    for a, b in bounds: segs.append((s0, a)); s0 = b
    segs.append((s0, last))
    T = {}
    for k, (a, b) in zip(ORDER, segs):
        sents = SENTS[k]; L = b - a
        tot = sum(len(s) for s in sents)
        cands = [r for r in inner if r[0] > a + 0.1 and r[1] < b - 0.05 and r[1] - r[0] >= 0.05]
        st, ch, acc, prev = [0.0], [], 0, a
        for s in sents[:-1]:
            acc += len(s); f = acc / tot
            pool = [r for r in cands if r[0] > prev + 0.15]
            r = min(pool, key=lambda r: abs((r[0] - a) / L - f)) if pool else (a + L * f, a + L * f)
            ch.append(r); st.append(r[1] - a); prev = r[1]
        ends = [c[0] - a for c in ch] + [L]
        T[k] = {'a': a, 'b': b, 'L': L, 'st': st, 'du': [e - s for s, e in zip(st, ends)]}
    return x, T

def r30(v): return round(v * 30) / 30
def ts(k, i): return LEAD + T[k]['st'][i]

# ------------------------------------------------------------ shared art
def text_img(txt, size, fill=WHITE, font='InterDisplay-Black', stroke=8):
    f = F(font, size); asc, desc = f.getmetrics(); w = int(f.getlength(txt))
    im = Image.new('RGBA', (w + 2 * stroke + 20, asc + desc + 2 * stroke + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((stroke + 10, stroke + 10), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=INK)
    return im

def kicker():
    txt = tracked('BATALHA DE SÉRIES  ·  #1', F('Inter-SemiBold', 30), (236, 236, 244, 235), 5)
    im = Image.new('RGBA', (txt.width + 34, txt.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); cy = txt.height // 2 + 1
    d.ellipse((4, cy - 8, 12, cy + 8), fill=DEX + (255,)); d.ellipse((12, cy - 8, 20, cy + 8), fill=JAN + (255,))
    im.alpha_composite(txt, (26, 0))
    return im

def split_bg(cut=0.5):
    """Diagonal red/blue split; cut moves the boundary (0..1+)."""
    w, h = W * S, H * S
    red = vgrad(w, h, (120, 14, 24), (30, 4, 8))
    blue = vgrad(w, h, (16, 60, 130), (4, 12, 34))
    m = Image.new('L', (w, h), 0)
    x_top = lerp(-400, W + 400, cut) + 160; x_bot = x_top - 320
    ImageDraw.Draw(m).polygon(P(x_top, -10, W + 500, -10, W + 500, H + 10, x_bot, H + 10), fill=255)
    img = red.copy(); img.paste(blue, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.line(P(x_top, -10, x_bot, H + 10), fill=(250, 250, 255), width=14 * S)
    return down(img).convert('RGBA')

def dark_bg():
    img = vgrad(W * S, H * S, (16, 14, 24), (5, 5, 9))
    img = glow(img, lambda d: d.ellipse(P(-500, 300, 400, 1500), fill=110), (90, 10, 18), 140 * S)
    img = glow(img, lambda d: d.ellipse(P(680, 300, 1580, 1500), fill=110), (10, 40, 100), 140 * S)
    return down(img).convert('RGBA')

def build_score_base():
    im = Image.new('RGBA', (W * S, 140 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for (x0, x1, col, name, anchor_x) in ((60, 530, DEX, 'DEXTER', 120), (550, 1020, JAN, 'JANE', 610)):
        d.rounded_rectangle(P(x0, 20, x1, 120), radius=50 * S, fill=col)
        d.text(P(anchor_x, 70), name, font=F('InterDisplay-Black', 52 * S), fill=(255, 255, 255), anchor='lm')
    return down(im)

def score_frame(im, t, y=286):
    comp(im, SCORE_BASE, (0, y))
    d = ImageDraw.Draw(im)
    for side, cx, col in (('d', 470, DEX), ('j', 960, JAN)):
        val, tchg = 0, -9
        for (te, sd, v) in SCORE_EVENTS:
            if sd == side and t >= te: val, tchg = v, te
        q = t - tchg
        s = 1.0 + (0.6 * (1 - eo(q / 0.35)) if 0 <= q < 0.35 else 0)
        r = 40 * s
        d.ellipse((cx - r, y + 70 - r, cx + r, y + 70 + r), fill=(255, 255, 255))
        d.text((cx, y + 72), str(val), font=F('InterDisplay-Black', int(56 * s)), fill=col, anchor='mm')

def flash(im, t, events, color, dur=0.35, amt=0.35):
    for te in events:
        if te <= t < te + dur:
            k = (1 - (t - te) / dur) ** 2 * amt
            a = np.asarray(im).astype(np.float32)
            a[..., :3] = a[..., :3] * (1 - k) + np.array(color, np.float32) * k
            return Image.fromarray(a.astype(np.uint8), 'RGBA')
    return im

def header(im, t, small, big, t0=0.0):
    p = eo((t - t0) / 0.35) if t >= t0 else 0
    if p <= 0: return
    a = text_img(small, 44, (220, 220, 232), 'InterDisplay-Bold', 5)
    b = text_img(big, 104, WHITE)
    comp(im, a, ((W - a.width) / 2, 440 - (1 - p) * 20), p)
    s = lerp(1.25, 1.0, p)
    b2 = b if s == 1 else b.resize((int(b.width * s), int(b.height * s)), Image.BILINEAR)
    comp(im, b2, ((W - b2.width) / 2, 500 + (b.height - b2.height) / 2), p)

# ------------------------------------------------------------ v1: hook
def frame_v1(t):
    im = SPLIT.copy()
    p1 = eo(t / 0.4); p2 = eo((t - 0.15) / 0.4)
    comp(im, NAME_D, (60 - (1 - p1) * 500, 560), p1)
    comp(im, NAME_J, (W - NAME_J.width - 60 + (1 - p2) * 500, 1040), p2)
    if t >= 0.35:
        s = backout((t - 0.35) / 0.4); s = max(0.01, s)
        v = VS.resize((max(1, int(VS.width * s)), max(1, int(VS.height * s))), Image.BILINEAR)
        jx = M.shake(t, [0.45], 10, freq=18, tau=0.08)
        comp(im, v, (540 - v.width / 2 + jx, 860 - v.height / 2))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v1'].draw(im, t)
    return im.convert('RGB')

def build_vs():
    im = Image.new('RGBA', (300 * S, 300 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse(P(10, 10, 290, 290), fill=(255, 255, 255)); d.ellipse(P(24, 24, 276, 276), fill=(14, 12, 18))
    d.text(P(150, 152), 'VS', font=F('InterDisplay-Black', 130 * S), fill=YEL, anchor='mm')
    return down(im)

# ------------------------------------------------------------ v2: Miami case file
def build_v2():
    w, h = W * S, H * S
    img = vgrad(w, h, (10, 8, 28), (96, 26, 70), 0, 1150 * S)
    img = glow(img, lambda d: d.ellipse(P(200, 950, 900, 1350), fill=160), (140, 50, 70), 80 * S)
    d = ImageDraw.Draw(img)
    rng = random.Random(4); x = -10
    while x < W:
        bw = rng.randint(50, 120); bh = rng.randint(140, 420)
        d.rectangle(P(x, 1150 - bh, x + bw, 1150), fill=(16, 10, 30))
        for _ in range(rng.randint(2, 7)):
            wx = x + rng.randint(6, max(7, bw - 14)); wy = 1150 - bh + rng.randint(10, max(11, bh - 20))
            d.rectangle(P(wx, wy, wx + 8, wy + 10), fill=(240, 180, 120) if rng.random() < 0.5 else (90, 120, 200))
        x += bw + rng.randint(-8, 6)
    img.paste(vgrad(w, (H - 1150) * S, (34, 14, 50), (6, 4, 12)), (0, 1150 * S)); d = ImageDraw.Draw(img)
    for k in range(14):
        y = 1170 + k * k * 4
        d.line(P(200 - k * 8, y, 880 + k * 8, y), fill=(120, 60, 110), width=2 * S)
    return down(img).convert('RGBA')

def build_folder():
    im = Image.new('RGBA', (760 * S, 520 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle(P(20, 40, 740, 510), radius=18 * S, fill=(196, 160, 104))
    d.rounded_rectangle(P(20, 10, 300, 80), radius=14 * S, fill=(196, 160, 104))
    d.rounded_rectangle(P(40, 70, 720, 490), radius=12 * S, fill=(222, 190, 132))
    d.text(P(80, 130), 'CASO 0417', font=F('InterDisplay-Black', 64 * S), fill=(60, 40, 24), anchor='lm')
    d.text(P(80, 210), 'DESAPARECIMENTOS', font=F('InterDisplay-ExtraBold', 50 * S), fill=(60, 40, 24), anchor='lm')
    d.text(P(80, 280), 'POLÍCIA DE MIAMI', font=F('Inter-SemiBold', 36 * S), fill=(110, 84, 54), anchor='lm')
    for y in (350, 395, 440): d.line(P(80, y, 680, y), fill=(170, 136, 90), width=4 * S)
    return down(im)

def build_stamp(txt, col):
    f = F('InterDisplay-Black', 60 * S); w = int(f.getlength(txt)) + 80 * S
    im = Image.new('RGBA', (w, 130 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6 * S, 6 * S, w - 6 * S, 124 * S), radius=14 * S, outline=col + (255,), width=10 * S)
    d.text((w // 2, 66 * S), txt, font=f, fill=col + (255,), anchor='mm')
    return down(im).rotate(-8, resample=Image.BICUBIC, expand=True)

def frame_v2(t):
    im = V2_BG.copy()
    comp(im, TAG, ((W - TAG.width) / 2, 440), eo(t / 0.4))
    t0 = ts('v2', 0) + 1.0
    if t >= t0:
        p = backout((t - t0) / 0.5)
        comp(im, FOLDER, ((W - FOLDER.width) / 2, 720 + (1 - p) * 700), clamp((t - t0) * 5))
    t1 = ts('v2', 1) + 1.0
    if t >= t1:
        q = (t - t1) / 0.18
        s = lerp(1.8, 1.0, eo(q))
        st = STAMP_D.resize((int(STAMP_D.width * s), int(STAMP_D.height * s)), Image.BILINEAR)
        comp(im, st, (540 - st.width / 2, 1070 - st.height / 2), clamp(q * 2))
        sy = M.shake(t, [t1 + 0.18], 12, freq=16, tau=0.07)
        if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v2'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v3: reading people
def build_eye():
    im = Image.new('RGBA', (520 * S, 300 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse(P(10, 30, 510, 270), fill=(250, 250, 252))
    return down(im)

def frame_v3(t):
    im = DARK.copy()
    header(im, t, 'RODADA 1', 'LER PESSOAS')
    ex, ey = 540, 900
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    open_ = 1.0
    blink = (t * 1.0) % 3.2
    if 1.4 < blink < 1.55: open_ = 0.1
    d.ellipse((ex - 250, ey - 120 * open_, ex + 250, ey + 120 * open_), fill=(250, 250, 252, 255))
    if open_ > 0.5:
        px = ex + 90 * math.sin(t * 1.6)
        d.ellipse((px - 92, ey - 92, px + 92, ey + 92), fill=JAN + (255,))
        d.ellipse((px - 46, ey - 46, px + 46, ey + 46), fill=(10, 10, 14, 255))
        d.ellipse((px - 34, ey - 50, px - 10, ey - 26), fill=(255, 255, 255, 230))
    d.arc((ex - 290, ey - 190, ex + 290, ey + 190), 200, 340, fill=(250, 250, 252, 255), width=10)
    im.alpha_composite(lay)
    t2 = ts('v3', 2) + 1.6
    if t >= t2:
        p = eo((t - t2) / 0.4)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.arc((380, 1040, 700, 1200), 20, 160, fill=(255, 255, 255, int(255 * p)), width=12)
        im.alpha_composite(lay)
        comp(im, TAG_HALF, (720, 1060 - (1 - p) * 20), p)
    im = flash(im, t, [ts('v3', 3)], JAN)
    score_frame(im, t)
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v3'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v4: the evidence
def build_scope():
    im = Image.new('RGBA', (420 * S, 520 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g, g2 = (214, 218, 228), (150, 156, 170)
    d.rounded_rectangle(P(60, 460, 360, 510), radius=14 * S, fill=g)
    d.rounded_rectangle(P(230, 120, 280, 470), radius=20 * S, fill=g2)
    d.rounded_rectangle(P(90, 300, 300, 330), radius=8 * S, fill=g)
    d.polygon(P(150, 60, 205, 40, 300, 250, 245, 270), fill=g)
    d.rounded_rectangle(P(130, 10, 200, 70), radius=10 * S, fill=g2)
    d.rounded_rectangle(P(170, 250, 210, 300), radius=8 * S, fill=g2)
    return down(im)

def build_slide():
    im = Image.new('RGBA', (360 * S, 120 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle(P(10, 20, 350, 100), radius=8 * S, fill=(200, 230, 245, 200))
    d.ellipse(P(150, 40, 210, 80), fill=DEX)
    return down(im)

def frame_v4(t):
    im = DARK.copy()
    header(im, t, 'RODADA 2', 'AS PROVAS')
    comp(im, SCOPE, (150, 760))
    t1 = ts('v4', 1) + 0.6
    p = eo((t - t1) / 0.5) if t >= t1 else 0
    comp(im, SLIDE, (lerp(1100, 560, p), 1000), p)
    t2 = ts('v4', 2) + 0.5
    if t >= t2:
        q = (t - t2) / 0.18; s = lerp(1.8, 1.0, eo(q))
        st = STAMP_ALT.resize((int(STAMP_ALT.width * s), int(STAMP_ALT.height * s)), Image.BILINEAR)
        comp(im, st, (600 - st.width / 2, 1190 - st.height / 2), clamp(q * 2))
    im = flash(im, t, [ts('v4', 3)], DEX)
    score_frame(im, t)
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v4'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v5: the trap
def draw_trap(d, cx, cy, openness):
    st = (196, 200, 212, 255)
    d.rounded_rectangle((cx - 230, cy + 60, cx + 230, cy + 90), radius=12, fill=(120, 124, 136, 255))
    ang = lerp(8, 80, openness)
    for side in (-1, 1):
        a = math.radians(ang)
        pts = []
        for k in range(0, 181, 12):
            th = math.radians(k)
            x = cx + side * 200 * math.cos(th) * math.cos(a) * (1 if side == 1 else 1)
            y = cy + 60 - 200 * math.sin(th) * math.sin(a) * 0.9 - side * 0
            pts.append((cx + 200 * math.cos(th), cy + 60 - side * 200 * math.sin(th) * math.sin(a)))
        d.line(pts, fill=st, width=16, joint='curve')
        for k in range(15, 170, 22):
            th = math.radians(k)
            x0, y0 = cx + 200 * math.cos(th), cy + 60 - side * 200 * math.sin(th) * math.sin(a)
            d.polygon([(x0 - 12, y0), (x0 + 12, y0), (x0, y0 + side * 30 * math.sin(a))], fill=st)

def frame_v5(t):
    im = DARK.copy()
    header(im, t, 'RODADA 3', 'A ARMADILHA')
    tsnap = ts('v5', 2) + 0.9
    openness = 1.0 if t < tsnap else 1 - eo((t - tsnap) / 0.12)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    draw_trap(d, 540, 880, openness)
    im.alpha_composite(lay)
    if t >= tsnap:
        p = eo((t - tsnap) / 0.3)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((240, 1080, 840, 1140), radius=30, outline=(255, 255, 255), width=5)
        d.text((540, 1196), 'CULPA: 0%', font=F('InterDisplay-Black', 64), fill=(255, 255, 255), anchor='mm', stroke_width=6, stroke_fill=INK)
        sy = M.shake(t, [tsnap + 0.1], 14, freq=17, tau=0.07)
        if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = flash(im, t, [ts('v5', 3)], DEX)
    score_frame(im, t)
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v5'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v6: chess
def build_board():
    w, h = W * S, H * S
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y_top, y_bot, half_top, half_bot = 960, 1290, 300, 520
    for r in range(8):
        for c in range(8):
            def pt(u, v):
                y = lerp(y_top, y_bot, v); half = lerp(half_top, half_bot, v)
                return (540 + lerp(-half, half, u), y)
            u0, u1, v0, v1 = c / 8, (c + 1) / 8, r / 8, (r + 1) / 8
            col = (230, 230, 236) if (r + c) % 2 == 0 else (40, 40, 52)
            d.polygon([tuple(P(*pt(u0, v0))), tuple(P(*pt(u1, v0))), tuple(P(*pt(u1, v1))), tuple(P(*pt(u0, v1)))], fill=col)
    return down(im)

def build_king():
    im = Image.new('RGBA', (200 * S, 380 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = (226, 30, 42)
    d.rectangle(P(92, 10, 108, 70), fill=c); d.rectangle(P(70, 28, 130, 44), fill=c)
    d.ellipse(P(60, 60, 140, 130), fill=c)
    d.polygon(P(70, 120, 130, 120, 150, 300, 50, 300), fill=c)
    d.rounded_rectangle(P(30, 300, 170, 370), radius=16 * S, fill=c)
    return down(im)

def frame_v6(t):
    im = DARK.copy()
    header(im, t, 'RODADA FINAL', 'JOGO MENTAL')
    im.alpha_composite(BOARD)
    tf = ts('v6', 3) + 0.8
    ang = 0 if t < tf else -82 * eio((t - tf) / 0.45)
    k = KING.rotate(ang, resample=Image.BICUBIC, expand=True, center=(100, 370))
    k = k.resize((int(k.width * 1.35), int(k.height * 1.35)), Image.BILINEAR)
    comp(im, k, (540 - k.width / 2 + (60 if ang else 0) * (abs(ang) / 82), 1180 - k.height + (0 if not ang else 40 * abs(ang) / 82)))
    if t >= tf + 0.45:
        sy = M.shake(t, [tf + 0.45], 10, freq=15, tau=0.08)
        if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = flash(im, t, [ts('v6', 4)], JAN)
    score_frame(im, t)
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v6'].draw(im, t)
    return im.convert('RGB')

# ------------------------------------------------------------ v7: verdict
def frame_v7(t):
    tw = ts('v7', 2)
    cut = 0.5 if t < tw else lerp(0.5, -0.25, eio((t - tw) / 0.5))
    im = SPLIT if t < tw else split_bg(cut) if (t - tw) < 0.55 else SPLIT_J
    im = im.copy()
    header(im, t, 'DESEMPATE', 'QUEM VENCE?')
    if t >= tw + 0.3:
        s = backout((t - tw - 0.3) / 0.45)
        v = WIN.resize((max(1, int(WIN.width * s)), max(1, int(WIN.height * s))), Image.BILINEAR)
        comp(im, v, (540 - v.width / 2, 860 - v.height / 2))
    im = flash(im, t, [tw + 0.3], (255, 255, 255), 0.4, 0.5)
    score_frame(im, t)
    t3 = ts('v7', 3) + 0.6
    if t >= t3:
        p = backout((t - t3) / 0.45)
        comp(im, FOLLOW, ((W - FOLLOW.width) / 2, 1130 + (1 - p) * 30), clamp((t - t3) * 4))
    im = M.apply_mult(im, MULT)
    comp(im, KICK, ((W - KICK.width) // 2, 196))
    CAP['v7'].draw(im, t)
    return im.convert('RGB')

def build_win():
    a = text_img('VITÓRIA', 120, WHITE); b = text_img('DO JANE', 150, WHITE, stroke=10)
    im = Image.new('RGBA', (max(a.width, b.width), a.height + b.height - 30), (0, 0, 0, 0))
    im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height - 30))
    return im

# ------------------------------------------------------------ captions, setup
def build_caps():
    global CAP
    CAP = {}
    for k in ORDER:
        pages = []
        t_ = [ts(k, i) for i in range(len(SENTS[k]))]
        for i, s in enumerate(SENTS[k]):
            end = t_[i + 1] - 0.3 if i + 1 < len(SENTS[k]) else DURS[k] + 1
            col = HIGHLIGHT.get((k, i), WHITE)
            pages.append((t_[i] - 0.05, end, [(t_[i], s, col)]))
        per = [d / len(s.split()) for s, d in zip(SENTS[k], T[k]['du'])]
        gap = float(np.clip(0.8 * min(per), 0.05, 0.3))
        CAP[k] = Caption(pages, font=('InterDisplay-ExtraBold', 66), top=1330, maxw=930, gap=gap)

FRAMES = {'v1': frame_v1, 'v2': frame_v2, 'v3': frame_v3, 'v4': frame_v4, 'v5': frame_v5, 'v6': frame_v6, 'v7': frame_v7}

def setup():
    global SPLIT, SPLIT_J, NAME_D, NAME_J, VS, KICK, MULT, V2_BG, FOLDER, STAMP_D, TAG, DARK, SCORE_BASE, TAG_HALF
    global SCOPE, SLIDE, STAMP_ALT, BOARD, KING, WIN, FOLLOW
    SPLIT, SPLIT_J = split_bg(0.5), split_bg(-0.25)
    NAME_D = text_img('DEXTER', 168, WHITE, stroke=10); NAME_J = text_img('JANE', 200, WHITE, stroke=10)
    VS = build_vs(); KICK = kicker(); MULT = M.make_mult(0.5, True)
    V2_BG = build_v2(); FOLDER = build_folder(); STAMP_D = build_stamp('PERITO: DEXTER MORGAN', (226, 30, 42))
    TAG = text_img('MIAMI  ·  23:47', 52, WHITE, 'InterDisplay-ExtraBold', 6)
    DARK = dark_bg(); SCORE_BASE = build_score_base()
    TAG_HALF = text_img('+0,5s', 70, YEL, 'InterDisplay-Black', 7)
    SCOPE = build_scope(); SLIDE = build_slide(); STAMP_ALT = build_stamp('LAUDO: INCONCLUSIVO', (226, 30, 42))
    BOARD = build_board(); KING = build_king(); WIN = build_win()
    FOLLOW = rich_line([('Segue', YEL), (' pra próxima batalha', WHITE)], F('InterDisplay-ExtraBold', 58), stroke=6)

def encode(name, fn, dur, fade_in=0, fade_out=0):
    n = int(round(dur * FPS))
    tmp, final = f'{OUT}/{name}.part.mp4', f'{OUT}/{name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); t0 = time.time()
    for i in range(n):
        a = np.asarray(fn(i / FPS), dtype=np.uint8)
        k = 1.0
        if fade_in and i < fade_in: k = (i + 1) / (fade_in + 1)
        if fade_out and i >= n - fade_out: k = min(k, (n - i) / (fade_out + 1))
        if k < 1: a = (a.astype(np.float32) * k).astype(np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit('ffmpeg failed ' + name)
    os.replace(tmp, final); print(f'{name}: {n} frames {time.time() - t0:.1f}s', flush=True)

# ------------------------------------------------------------ sound
def make_audio(path, x, starts, total):
    n = int(total * SR); t = np.arange(n) / SR
    out = np.zeros(n + 3 * SR)
    def add(sig, at, g=1.0):
        i = int(at * SR)
        if 0 <= i < n: out[i:i + len(sig)] += sig * g
    K, Hh = LA.kick(), LA.hat()
    beat = 0.5
    for b in range(int(total / beat)):
        tb = b * beat
        add(K, tb, 0.55 if b % 2 == 0 else 0.3)
        add(Hh, tb + 0.25, 0.08)
    drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 1) + 0.4 * np.sin(2 * np.pi * 110 * t + 2)) * 0.05
    out[:n] += drone * np.clip(t / 2, 0, 1)
    for k in ORDER[1:]: add(LA.whoosh(0.4, 0.3), starts[k] - 0.2)
    add(LA.tada(0.3), starts['v1'] + 0.35)
    add(LA.thunk(), starts['v2'] + ts('v2', 1) + 1.18, 1.2)
    for (te, sd, v) in SCORE_EVENTS:
        add(LA.ding(1318.5 if sd == 'j' else 987.8, 0.35), te)
        add(LA.kick(), te, 0.9)
    add(LA.thunk(), starts['v4'] + ts('v4', 2) + 0.68, 1.0)
    tsn = starts['v5'] + ts('v5', 2) + 0.9
    clank = LA.bandpass(np.random.default_rng(3).standard_normal(int(0.3 * SR)), 1500, 9000)
    clank = clank / np.abs(clank).max() * np.exp(-np.arange(len(clank)) / SR / 0.05) * 0.5
    add(clank, tsn); add(LA.thunk(), tsn, 0.8)
    add(LA.thunk(), starts['v6'] + ts('v6', 3) + 1.25, 1.1)
    add(LA.crash(1.6), starts['v7'] + ts('v7', 2) + 0.3); add(LA.tada(0.4), starts['v7'] + ts('v7', 2) + 0.3)
    out = out[:n]
    nar = np.zeros(n)
    for k in ORDER:
        a, b = max(0.0, T[k]['a'] - 0.04), T[k]['b'] + 0.1
        seg = x[int(a * SR):int(b * SR)]
        i = int((starts[k] + LEAD - 0.04) * SR); j = min(n, i + len(seg)); nar[i:j] += seg[:j - i]
    voiced = np.abs(nar) > 0.02 * np.abs(nar).max()
    nar *= 0.15 / np.sqrt((nar[voiced] ** 2).mean())
    env = np.convolve(np.abs(nar), np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
    duck = 1 - 0.55 * np.clip(env / 0.02, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
    mix = out * 0.55 * duck + nar
    mix *= np.clip((total - t) / 0.8, 0, 1)
    mix = np.tanh(mix * 1.3) / 1.3
    mix *= min(1.0, 0.95 / np.abs(mix).max())
    st = np.stack([mix, mix], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------ main
if __name__ == '__main__':
    mode, narr = sys.argv[1], sys.argv[2]
    bs = os.environ.get('BOUNDS')
    X, T = analyse(narr, [float(v) for v in bs.split(',')] if bs else None)
    DURS = {k: r30(max(MINS[k], LEAD + T[k]['L'] + TAIL[k])) for k in ORDER}
    print('durs', DURS, 'total', round(sum(DURS.values()), 1))
    SCORE_EVENTS = [(ts('v3', 3), 'j', 1), (ts('v4', 3), 'd', 1), (ts('v5', 3), 'd', 2), (ts('v6', 4), 'j', 2), (ts('v7', 2) + 0.3, 'j', 3)]
    # score events are scene-local; convert each scene's frame to use local times
    LOCAL = {'v3': [(ts('v3', 3), 'j', 1)], 'v4': [(-1, 'j', 1), (ts('v4', 3), 'd', 1)],
             'v5': [(-1, 'j', 1), (-1, 'd', 1), (ts('v5', 3), 'd', 2)],
             'v6': [(-1, 'j', 1), (-1, 'd', 2), (ts('v6', 4), 'j', 2)],
             'v7': [(-1, 'd', 2), (-1, 'j', 2), (ts('v7', 2) + 0.3, 'j', 3)]}
    setup(); build_caps()
    def scene_fn(k):
        def fn(t):
            global SCORE_EVENTS
            SCORE_EVENTS = LOCAL.get(k, [])
            return FRAMES[k](t)
        return fn
    if mode == 'preview':
        shots = [('v1', 1.5), ('v2', ts('v2', 1) + 1.5), ('v3', ts('v3', 3) + 0.2), ('v4', ts('v4', 2) + 0.9),
                 ('v5', ts('v5', 3) + 0.1), ('v6', ts('v6', 4) + 0.2), ('v7', ts('v7', 2) + 1.0), ('v7', DURS['v7'] - 0.5)]
        th = []
        for i, (k, tt_) in enumerate(shots):
            t1 = time.time(); im = scene_fn(k)(tt_); im.save(f'{OUT}/prev_{i}.png')
            print(f'prev_{i} {k}@{tt_:.2f} {1000 * (time.time() - t1):.0f}ms', flush=True)
            th.append(im.resize((W // 4, H // 4), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 4 * 4, H // 4 * 2))
        for i, im in enumerate(th): sheet.paste(im, ((i % 4) * (W // 4), (i // 4) * (H // 4)))
        sheet.save(f'{OUT}/sheet.png')
    else:
        only = sys.argv[3:] or ORDER
        for idx, k in enumerate(ORDER):
            if k in only: encode(k, scene_fn(k), DURS[k], fade_in=0, fade_out=12 if idx == len(ORDER) - 1 else 0)
        starts, acc = {}, 0.0
        for k in ORDER: starts[k] = acc; acc += int(round(DURS[k] * FPS)) / FPS
        SCORE_EVENTS = [(starts[k] + te, sd, v) for k, evs in LOCAL.items() for (te, sd, v) in evs if te >= 0]
        make_audio(f'{OUT}/audio.wav', X, starts, acc)
        with open(f'{OUT}/list.txt', 'w') as fl:
            for k in ORDER: fl.write(f"file '{k}.mp4'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video.mp4'], check=True)
        final = f'{OUT}/batalha-dexter-x-jane.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final + '.part.mp4'], check=True)
        os.replace(final + '.part.mp4', final)
        print('done', acc)
