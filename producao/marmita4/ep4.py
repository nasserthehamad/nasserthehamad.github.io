#!/usr/bin/env python3
"""A Marmita Sumiu — Episódio 4 (Ep. 3 venceu B: armadilha de pimenta). Última votação: dentro × fora do prédio.
python3 ep4.py preview | render [scenes] | audio      (timing.json from nar.py, or synthetic)"""
import os, sys, math, json, time, subprocess, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch'); sys.path.insert(0, '/home/claude/marmita2')
sys.path.insert(0, '/home/claude/marmita3')
import make as M
import lunch as L
import laudio as LA
import ep2 as E2
import ep3 as M3
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, down, Caption, rich_line, WHITE, INK

W, H, S, FPS = 1080, 1920, 2, 30
WORK = '/home/claude/marmita4'
L.WORK = WORK
A_COL, B_COL, YEL = L.A_COL, L.B_COL, L.YEL
BLUE_T, RED_T = E2.BLUE_T, (255, 110, 100)
mix, sc = L.mix, E2.scaled

PAGES = {
    's1': [[('Vocês escolheram a', WHITE), ('armadilha!', B_COL)], [('O Léo fez uma lasanha com', WHITE), ('MUITA pimenta.', RED_T)]],
    's2': [[('No dia seguinte, ao meio-dia…', WHITE)], [('um grito na copa!', RED_T)]],
    's3': [[('Quando o Léo chegou, a pessoa já tinha fugido…', WHITE)], [('e deixou cair o', WHITE), ('moletom amarelo.', YEL)]],
    's4': [[('E na portaria, o Seu Zé achou a', WHITE), ('caneta azul', BLUE_T), ('do Seu Carlos…', WHITE)],
           [('presa no', WHITE), ('livro de visitas!', A_COL)]],
}
ORDER = ['s1', 's2', 's3', 's4', 's5']
TIMING = WORK + '/timing.json'

def synth_timing():
    out = {'durs': {}, 'pages': {}, 'gaps': {}, 'nar': []}
    for k in ORDER[:-1]:
        t, pages = 0.3, []
        for segs in PAGES[k]:
            txt = ' '.join(s for s, _ in segs)
            pages.append([round(t, 3), [[s, list(c)] for s, c in segs]]); t += 0.5 + 0.06 * len(txt)
        out['pages'][k] = pages; out['durs'][k] = round(t + 0.3, 3); out['gaps'][k] = 0.12
    out['durs']['s5'] = 9.0
    return out

TJ = json.load(open(TIMING)) if os.path.exists(TIMING) else synth_timing()
DURS = {k: TJ['durs'][k] for k in ORDER}
def p2_at(k): return TJ['pages'][k][1][0]

# ------------------------------------------------------------------ art
def open_lasagna(w=420):
    h = int(w * 0.6)
    im = Image.new('RGBA', ((w + 40) * S, (h + 40) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle(P(20, 20 + h * 0.15, 20 + w, 20 + h), radius=26 * S, fill=(238, 244, 248), outline=(176, 196, 208), width=6 * S)
    x0, x1 = 44, w - 4
    for i, col in enumerate([(244, 206, 110), (200, 60, 40), (244, 206, 110), (200, 60, 40), (250, 232, 170)]):
        y0 = 20 + h * 0.25 + i * h * 0.12
        d.rounded_rectangle(P(x0, y0, x1, y0 + h * 0.13), radius=10 * S, fill=col)
    rng = random.Random(3)
    for _ in range(14):
        cx, cy = rng.uniform(x0 + 20, x1 - 20), rng.uniform(20 + h * 0.27, 20 + h * 0.36); r = rng.uniform(6, 11)
        d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=(230, 40, 30))
    return down(im)

def flame(w=160, h=220, seed=0):
    im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for col, k in (((250, 90, 30), 1.0), ((255, 180, 40), 0.7), ((255, 240, 150), 0.4)):
        ww, hh = w * k, h * k
        cx, by = w, 2 * h - 10
        d.polygon([(cx - ww * 0.9, by), (cx - ww * 0.6, by - hh * 1.1), (cx - ww * 0.2, by - hh * 0.8), (cx, by - hh * 1.8),
                   (cx + ww * 0.25, by - hh * 0.9), (cx + ww * 0.6, by - hh * 1.3), (cx + ww * 0.9, by)], fill=col)
    return im.resize((w, h), Image.LANCZOS)

def hoodie_flat():
    w, h = 380, 300
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hood, hood_d = (240, 190, 50), (214, 160, 30)
    d.polygon(P(60, 90, 0, 220, 50, 250, 110, 150), fill=hood)
    d.polygon(P(320, 90, 380, 220, 330, 250, 270, 150), fill=hood)
    d.rounded_rectangle(P(90, 70, 290, 290), radius=40 * S, fill=hood)
    d.ellipse(P(130, 20, 250, 120), fill=hood_d); d.ellipse(P(150, 40, 230, 110), fill=(160, 116, 20))
    d.rounded_rectangle(P(130, 200, 250, 260), radius=16 * S, fill=hood_d)
    d.line(P(170, 110, 160, 170), fill=(252, 252, 252), width=5 * S); d.line(P(210, 110, 220, 170), fill=(252, 252, 252), width=5 * S)
    sp = down(im)
    return L.sticker(sp, grow=4).rotate(-12, resample=Image.BICUBIC, expand=True)

def glass_tipped():
    im = Image.new('RGBA', (360 * S, 160 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse(P(60, 90, 360, 150), fill=(150, 200, 240, 170))
    gl = Image.new('RGBA', (120 * S, 160 * S), (0, 0, 0, 0)); dg = ImageDraw.Draw(gl)
    dg.polygon(P(10, 10, 110, 10, 96, 150, 24, 150), fill=(220, 240, 255, 160), outline=(120, 150, 180), width=4 * S)
    gl = gl.rotate(-80, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(gl, (0, 10 * S))
    return down(im)

def visitor_book():
    w, h = 820, 520
    im = Image.new('RGBA', (w + 40, h + 50), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((20, 34, 20 + w, 34 + h), radius=20, fill=150)
    im.paste((30, 10, 30, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=20, fill=(120, 60, 40))
    for x0 in (36, 20 + w / 2 + 6):
        d.rounded_rectangle((x0, 36, x0 + w / 2 - 22, h + 4), radius=10, fill=(252, 248, 236))
    d.line((20 + w / 2, 36, 20 + w / 2, h + 4), fill=(200, 190, 170), width=4)
    d.text((36 + (w / 2 - 22) / 2, 80), 'LIVRO DE VISITAS', font=F('InterDisplay-Black', 34), fill=(120, 60, 40), anchor='mm')
    rng = random.Random(8)
    for side, x0 in enumerate((56, 20 + w / 2 + 26)):
        for i in range(7):
            y = 130 + i * 52 + (0 if side == 0 else -40)
            if y > h - 10 or y < 60: continue
            d.line((x0, y + 22, x0 + w / 2 - 70, y + 22), fill=(220, 214, 200), width=2)
            xx = x0 + 6
            for _ in range(rng.randint(4, 7)):
                seg = rng.uniform(18, 46)
                d.arc((xx, y - 4, xx + seg, y + 20), 200, 340, fill=(70, 70, 110), width=3); xx += seg * 0.8
    return im

def icon_building(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.rectangle((26 * u, 14 * u, 74 * u, 88 * u), fill=(90, 110, 150))
    for r in range(5):
        for c in range(3):
            x = 32 * u + c * 13 * u; y = 20 * u + r * 12 * u
            d.rectangle((x, y, x + 8 * u, y + 7 * u), fill=(250, 220, 120))
    d.rectangle((44 * u, 76 * u, 56 * u, 88 * u), fill=(40, 50, 70))
    return im.resize((sz, sz), Image.LANCZOS)

def icon_exit(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.rectangle((18 * u, 14 * u, 56 * u, 88 * u), outline=(90, 96, 108), width=int(6 * u))
    d.polygon([(22 * u, 18 * u), (46 * u, 26 * u), (46 * u, 92 * u), (22 * u, 84 * u)], fill=(140, 90, 60))
    d.line((52 * u, 52 * u, 86 * u, 52 * u), fill=(214, 40, 50), width=int(8 * u))
    d.polygon([(80 * u, 40 * u), (94 * u, 52 * u), (80 * u, 64 * u)], fill=(214, 40, 50))
    return im.resize((sz, sz), Image.LANCZOS)

# ------------------------------------------------------------------ setup
def setup():
    global KICKER, LEO_ST, ZE_ST, LAS, CHILI, PILL_ESC, PILL_LAST, VIG, K_BG, K_DIM, SCREAM, FLAMES, HOOD, GLASS, BOOK, PEN
    global CARD_A, CARD_B, CTA, SUB, FOLLOW, EMPTY, CLOCK, QM
    KICKER = L.build_kicker('A MARMITA SUMIU  ·  EP. 4')
    LEO_ST = L.sticker(L.person('leo')); ZE_ST = L.sticker(M3.ze())
    LAS = open_lasagna(); CHILI = M3.icon_chili(120)
    PILL_ESC = L.label_pill('VOCÊS ESCOLHERAM', 'B', B_COL)
    PILL_LAST = L.label_pill('ÚLTIMA VOTAÇÃO', '!', B_COL)
    VIG = L.make_vig(0.32, cy=0.45)
    K_BG = L.build_s1()
    a = np.asarray(K_BG.convert('RGB'), np.float32) * 0.82
    K_DIM = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    SCREAM = rich_line([('AAAAAAH!', (255, 226, 80))], F('InterDisplay-Black', 140), stroke=12)
    FLAMES = [flame(170, 230, i) for i in range(3)]
    HOOD = hoodie_flat(); GLASS = glass_tipped()
    BOOK = visitor_book(); PEN = E2.icon_pen(230)
    CARD_A = M.card('A', 'De dentro', A_COL, (30, 20, 8), A_COL, (30, 20, 8))
    CARD_B = M.card('B', 'De fora', B_COL, (64, 10, 14), (255, 228, 228), WHITE)
    for c, ic in ((CARD_A, icon_building()), (CARD_B, icon_exit())):
        c.alpha_composite(E2.badge(ic, 140), (30 + 900 - 22 - 140, 30 + 20))
    CTA = rich_line([('Comenta ', WHITE), ('A', A_COL), (' ou ', WHITE), ('B', B_COL)], F('InterDisplay-ExtraBold', 76))
    SUB = rich_line([('O mais votado decide o ', (232, 244, 244)), ('FINAL', A_COL)], F('Inter-SemiBold', 40), stroke=4)
    FOLLOW = rich_line([('Segue pra ver quem foi', WHITE)], F('InterDisplay-ExtraBold', 46), stroke=5)
    EMPTY = L.build_empty_box()
    CLOCK = E2.pill('12:00')
    f = F('InterDisplay-Black', 120)
    QM = Image.new('RGBA', (110, 160), (0, 0, 0, 0))
    ImageDraw.Draw(QM).text((55, 80), '?', font=f, fill=WHITE, anchor='mm', stroke_width=7, stroke_fill=INK)
    build_caps()

def build_caps():
    global CAP
    CAP = {}
    for k in ORDER[:-1]:
        pages = TJ['pages'][k]; gap = TJ['gaps'].get(k, 0.1); cps = []
        for i, (st, segs) in enumerate(pages):
            end = pages[i + 1][0] - 0.05 if i + 1 < len(pages) else DURS[k] + 1
            ss, acc = [], st
            for text, col in segs:
                ss.append((acc, text, tuple(col))); acc += gap * len(text.split())
            cps.append((st, end, ss))
        CAP[k] = Caption(cps, font=('InterDisplay-ExtraBold', 74), top=1350, maxw=940, gap=gap)
    CAP['s5'] = Caption([(0.1, DURS['s5'] + 5, [(0.15, 'QUEM COMEU?', WHITE)])], font=('InterDisplay-Black', 104), top=330, maxw=980, gap=0.12)

def finish(im, k, t):
    comp(im, KICKER, ((W - KICKER.width) // 2, 196)); CAP[k].draw(im, t); return im.convert('RGB')

def shake_img(im, t, t0, amp=18, d=0.5):
    if not (t0 <= t < t0 + d): return im
    k = 1 - (t - t0) / d
    dx, dy = int(amp * k * math.sin(2 * math.pi * 29 * t)), int(amp * 0.7 * k * math.cos(2 * math.pi * 23 * t))
    return Image.fromarray(np.roll(np.roll(np.asarray(im), dx, axis=1), dy, axis=0))

def smoke(im, t, cx, cy, n=6, seed=1):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rng = random.Random(seed)
    for i in range(n):
        ph = (t * 0.5 + i / n) % 1.0; x = cx + rng.uniform(-90, 90) + 30 * math.sin(t * 2 + i); y = cy - ph * 380; r = 30 + 60 * ph
        d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 235, 240, int(150 * math.sin(math.pi * ph))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))

# ------------------------------------------------------------------ scenes
def frame_s1(t):
    im = L.apply_vig(L.rays(t, (240, 110, 50), (250, 132, 70)), VIG)
    q = t / 0.4; oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    ls = sc(LEO_ST, 0.82); bob = 4 * math.sin(2 * math.pi * t / 1.4)
    comp(im, ls, (60, 1330 - ls.height + oy + bob))
    bx, by = 700, 1080
    comp(im, LAS, (bx - LAS.width / 2, by - LAS.height / 2))
    T2 = p2_at('s1')
    if t >= T2 - 0.3:
        for i in range(10):
            ph = ((t - T2 + 0.3) * 1.4 + i * 0.137) % 1.0
            if (t - T2 + 0.3) * 1.4 < i * 0.137: continue
            x = bx - 150 + (i * 67) % 300; y = lerp(380, by - 40, ph)
            ch = CHILI.rotate((i * 47 + t * 200) % 360, resample=Image.BICUBIC, expand=True)
            comp(im, ch, (x - ch.width / 2, y - ch.height / 2), 1 - ph * 0.2)
        if t > T2 + 0.8:
            for i, fl in enumerate(FLAMES):
                s = 0.6 + 0.08 * math.sin(t * 9 + i)
                f2 = sc(fl, s); comp(im, f2, (bx - 160 + i * 120 - f2.width / 2, by - 80 - f2.height), clamp((t - T2 - 0.8) * 3))
    if t > 0.05:
        s = lerp(0.55, 1.0, L.backout((t - 0.05) / 0.4))
        pi = sc(PILL_ESC, s); comp(im, pi, (540 - pi.width / 2, 340 - pi.height / 2), clamp((t - 0.05) * 6))
    return finish(im, 's1', t)

def frame_s2(t):
    T2 = p2_at('s2')
    im = K_BG.copy()
    if t > 0.1:
        s = lerp(0.55, 1.0, L.backout((t - 0.1) / 0.4))
        ck = sc(CLOCK, s); comp(im, ck, (540 - ck.width / 2, 520 - ck.height / 2), clamp((t - 0.1) * 6))
    if t >= T2 - 0.1:
        k = clamp((t - T2 + 0.1) / 0.2)
        red = Image.new('RGBA', (W, H), (255, 60, 40, int(70 * k))); im.alpha_composite(red)
        smoke(im, t, 800, 1050, 7, 2)
        s = lerp(1.8, 1.0, eo(k)) * (1 + 0.04 * math.sin(t * 30))
        sc_ = sc(SCREAM, s).rotate(-6, resample=Image.BICUBIC, expand=True)
        comp(im, sc_, (540 - sc_.width / 2, 800 - sc_.height / 2), k)
        im = shake_img(im, t, T2 - 0.1, 22, 0.8)
    return finish(im, 's2', t)

def frame_s3(t):
    im = K_DIM.copy()
    smoke(im, t, 820, 1150, 5, 4)
    comp(im, GLASS, (560, 1240))
    T2 = p2_at('s3')
    hx, hy = 330, 1150
    if t >= T2 - 0.2:
        k = L.backout(clamp((t - T2 + 0.2) / 0.45)); hd = sc(HOOD, lerp(0.6, 1.0, k))
        comp(im, hd, (hx - hd.width / 2, hy - hd.height / 2), clamp((t - T2 + 0.2) * 5))
        if t > T2 + 0.4: E2.rings(im, hx, hy, t, (255, 220, 80), 120, 230)
    else:
        for (qx, qy, ph) in [(330, 900, 0.0), (760, 820, 0.9)]:
            comp(im, QM, (qx - 55, qy - 80 + 10 * math.sin(2 * math.pi * t / 1.3 + ph)), clamp((t - 0.4) * 3))
    return finish(im, 's3', t)

def frame_s4(t):
    im = L.apply_vig(L.rays(t, (60, 96, 176), (74, 112, 196)), VIG)
    q = t / 0.4; oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    zs = sc(ZE_ST, 0.62)
    comp(im, zs, (40, 1330 - zs.height + oy + 4 * math.sin(t * 3)))
    k = eo(clamp((t - 0.2) / 0.4)); bk = sc(BOOK, 0.92)
    comp(im, bk, (590 - bk.width / 2 + 60, lerp(1100, 760, k) - bk.height / 2), k)
    tp = max(0.8, p2_at('s4') - 1.2)
    if t >= tp:
        kk = L.backout(clamp((t - tp) / 0.45)); pn = sc(PEN, lerp(0.5, 1.0, kk))
        cx, cy = 820, 700
        comp(im, pn, (cx - pn.width / 2, cy - pn.height / 2), clamp((t - tp) * 5))
        if t > tp + 0.4: E2.rings(im, cx, cy, t, (60, 110, 220), 90, 170)
    return finish(im, 's4', t)

def frame_s5(t):
    im = E2.S6_BG(t)
    if t > 0.05:
        s = lerp(0.55, 1.0, L.backout((t - 0.05) / 0.4))
        pi = sc(PILL_LAST, s); comp(im, pi, (540 - pi.width / 2, 520 - pi.height / 2), clamp((t - 0.05) * 6))
    for (img, y, t0, side, phase) in [(CARD_A, 620, 0.6, -1, 0.0), (CARD_B, 850, 0.9, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45); x = (W - img.width) / 2 + side * (1 - p) * 160
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.6) / 1.5 + phase) if t > 2.6 else 1.0
        i2 = sc(img, s); comp(im, i2, (x + img.width / 2 - i2.width / 2, y + img.height / 2 - i2.height / 2), p)
    if t >= 1.6: p = eo((t - 1.6) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1110 + (1 - p) * 24), p)
    if t >= 2.0: p = eo((t - 2.0) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1215 + (1 - p) * 18), p)
    if t >= 2.4:
        p = eo((t - 2.4) / 0.4); pul = 1 + 0.03 * math.sin(2 * math.pi * t / 1.2)
        fo = sc(FOLLOW, pul); comp(im, fo, ((W - fo.width) / 2, 1290 + (1 - p) * 18), p)
    if t >= 0.3:
        p = L.backout((t - 0.3) / 0.5); bob = 6 * math.sin(2 * math.pi * t / 1.7)
        comp(im, EMPTY, (540 - EMPTY.width / 2, 1440 + (1 - p) * 300 + bob), clamp((t - 0.3) * 4))
    return finish(im, 's5', t)

SCENES = [('s1', frame_s1), ('s2', frame_s2), ('s3', frame_s3), ('s4', frame_s4), ('s5', frame_s5)]

# ------------------------------------------------------------------ audio
def build_audio(path):
    SR = LA.SR; rng = np.random.default_rng(7)
    st, acc = {}, 0.0
    for k in ORDER: st[k] = acc; acc += round(DURS[k] * FPS) / FPS
    total = acc; n = int(total * SR)
    music = np.zeros(n)
    def put(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if i < n: music[i:j] += sig[:j - i]
    put(LA.groove(st['s2'] + p2_at('s2')), 0)
    put(LA.groove(st['s4'] - st['s2'] - p2_at('s2'), full=False), st['s2'] + p2_at('s2'))
    put(LA.groove(total - st['s4']), st['s4'])
    fx = np.zeros(n + 3 * SR)
    def add(sig, at, g=1.0):
        i = int(at * SR); fx[i:i + len(sig)] += sig * g
    def tt(d): return np.arange(int(d * SR)) / SR
    def sizzle(d=1.2, g=0.12):
        y = LA.bandpass(rng.standard_normal(int(d * SR)), 2500, 9000); y /= np.abs(y).max()
        q = tt(d); return y * g * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 13 * q))) * np.minimum(1, q / 0.05) * np.minimum(1, (d - q) / 0.3)
    def scream(d=0.9, g=0.22):
        q = tt(d); f = 520 + 260 * np.sin(np.pi * q / d) + 30 * np.sin(2 * np.pi * 7 * q)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR); y = np.tanh(3 * y) + 0.3 * LA.bandpass(rng.standard_normal(len(q)), 800, 4000)
        return y / np.abs(y).max() * g * np.minimum(1, q / 0.04) * np.minimum(1, (d - q) / 0.2)
    add(LA.whoosh(), st['s1']); add(LA.blip(500, 900, 0.1, 0.3), st['s1'] + 0.1)
    for i in range(6): add(LA.blip(900 + 60 * i, 700 + 60 * i, 0.06, 0.18), st['s1'] + p2_at('s1') - 0.2 + i * 0.12)
    add(sizzle(), st['s1'] + p2_at('s1') + 0.8)
    for k in range(4): add(LA.tick(), st['s2'] + 0.2 + k * 0.4)
    add(scream(), st['s2'] + p2_at('s2') - 0.1); add(LA.crash(), st['s2'] + p2_at('s2') - 0.1, 0.8); add(LA.thunk(), st['s2'] + p2_at('s2') - 0.1, 1.2)
    add(LA.whoosh(0.25, 0.25), st['s3']); add(LA.slide_whistle(), st['s3'] + p2_at('s3') - 0.3); add(LA.ding(1174.7), st['s3'] + p2_at('s3') + 0.2)
    add(LA.whoosh(0.25, 0.25), st['s4']); add(LA.ding(1318.5), st['s4'] + max(0.8, p2_at('s4') - 1.2)); add(LA.thunk(), st['s4'] + p2_at('s4'))
    add(LA.tada(), st['s5']); add(LA.blip(400, 800, 0.1, 0.3), st['s5'] + 0.6); add(LA.blip(450, 900, 0.1, 0.3), st['s5'] + 0.9)
    add(LA.blip(500, 1000, 0.1, 0.3), st['s5'] + 1.6)
    fx = fx[:n]
    nar = np.zeros(n)
    if TJ.get('nar') and os.path.exists(WORK + '/narration.wav'):
        src = LA.load_wav(WORK + '/narration.wav')
        for (k, s0, s1, at) in TJ['nar']:
            seg = src[int(s0 * SR):int(s1 * SR)]
            i = int((st[k] + at) * SR); j = min(n, i + len(seg)); nar[i:j] += seg[:j - i]
    if np.abs(nar).max() > 0:
        rmsv = np.sqrt(np.mean(nar[np.abs(nar) > 0.01] ** 2)); nar *= 0.16 / max(rmsv, 1e-6)
        nar = np.tanh(nar * 1.5) / 1.5
        env = np.convolve(np.abs(nar), np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
        duck = 1 - 0.62 * np.clip(env / 0.02, 0, 1)
        duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
        mixm = music * 0.42 * duck + fx * 0.8 + nar * (0.9 / np.abs(nar).max())
    else:
        mixm = music * 0.6 + fx
    t = np.arange(n) / SR
    mixm *= np.clip((total - t) / 0.6, 0, 1) * np.clip(t / 0.02, 0, 1)
    mixm *= 0.89 / np.abs(mixm).max()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mixm, mixm], 1) * 32767).astype(np.int16).tobytes())
    return total

def assemble(out):
    with open(WORK + '/list.txt', 'w') as fl:
        for k in ORDER: fl.write(f"file '{WORK}/{k}.mp4'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', WORK + '/list.txt', '-c', 'copy', WORK + '/video.mp4'], check=True)
    total = build_audio(WORK + '/audio.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', WORK + '/video.mp4', '-i', WORK + '/audio.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out + '.part.mp4'], check=True)
    os.replace(out + '.part.mp4', out); print('ok', out, round(total, 2))

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    t0 = time.time(); setup(); print(f'setup {time.time() - t0:.1f}s', flush=True)
    fns = dict(SCENES)
    if mode == 'preview':
        shots = [('s1', 0.8), ('s1', p2_at('s1') + 1.2), ('s2', 0.6), ('s2', p2_at('s2') + 0.5),
                 ('s3', p2_at('s3') + 0.8), ('s4', p2_at('s4') + 0.6), ('s5', 3.5), ('s3', 0.6)]
        sheet = Image.new('RGB', (W // 3 * 4, H // 3 * 2))
        for i, (k, tt) in enumerate(shots):
            sheet.paste(fns[k](tt).resize((W // 3, H // 3), Image.LANCZOS), ((i % 4) * (W // 3), (i // 4) * (H // 3)))
        sheet.save(WORK + '/sheet.png'); print('sheet', DURS, round(sum(DURS.values()), 2))
    elif mode == 'render':
        only = sys.argv[2:] or ORDER
        for idx, (k, fn) in enumerate(SCENES):
            if k in only: L.encode(k, fn, DURS[k], fade_in=0, fade_out=12 if idx == len(SCENES) - 1 else 0)
        if all(os.path.exists(f'{WORK}/{k}.mp4') for k in ORDER): assemble(WORK + '/a-marmita-sumiu-ep4.mp4')
    elif mode == 'audio':
        assemble(WORK + '/a-marmita-sumiu-ep4.mp4')
