#!/usr/bin/env python3
"""A Marmita Sumiu — Episódio 3 (venceu B: ver as câmeras).
python3 ep3.py preview | render [scenes...] | audio      (timing3.json from nar3.py, or synthetic)"""
import os, sys, math, json, time, subprocess, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch'); sys.path.insert(0, '/home/claude/marmita2')
import make as M
import lunch as L
import laudio as LA
import ep2 as E2
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, down, Caption, rich_line, WHITE, INK

W, H, S, FPS = 1080, 1920, 2, 30
WORK = '/home/claude/marmita3'
L.WORK = WORK
A_COL, B_COL, YEL = L.A_COL, L.B_COL, L.YEL
BLUE_T = E2.BLUE_T
mix, sc = L.mix, E2.scaled

PAGES = {
    's1': [[('Vocês pediram', WHITE)], [('as câmeras!', B_COL)]],
    's2': [[('O Seu Zé, o porteiro,', WHITE)], [('voltou a gravação do meio-dia.', WHITE)]],
    's3': [[('11h58: alguém de', WHITE), ('moletom amarelo', YEL), ('abre a geladeira…', WHITE)],
           [('e leva a marmita de', WHITE), ('tampa azul!', BLUE_T)]],
    's4': [[('Moletom amarelo…', YEL)], [('igual ao do Pedro!', A_COL)]],
    's5': [[('Mas olha o detalhe:', WHITE)], [('a pessoa é bem mais', WHITE), ('baixinha', A_COL), ('que ele…', WHITE)]],
}
ORDER = ['s1', 's2', 's3', 's4', 's5', 's6']
TIMING = WORK + '/timing3.json'

def synth_timing():
    out = {'durs': {}, 'pages': {}, 'gaps': {}, 'nar': []}
    for k in ORDER[:-1]:
        t, pages = 0.3, []
        for segs in PAGES[k]:
            txt = ' '.join(s for s, _ in segs)
            pages.append([round(t, 3), [[s, list(c)] for s, c in segs]]); t += 0.5 + 0.06 * len(txt)
        out['pages'][k] = pages; out['durs'][k] = round(t + 0.3, 3); out['gaps'][k] = 0.12
    out['durs']['s6'] = 7.5
    return out

TJ = json.load(open(TIMING)) if os.path.exists(TIMING) else synth_timing()
DURS = {k: TJ['durs'][k] for k in ORDER}
def p2_at(k): return TJ['pages'][k][1][0]

# ------------------------------------------------------------------ art
def ze():
    """Seu Zé, porteiro: navy uniform, cap with badge, grey moustache, radio."""
    im = Image.new('RGBA', (L.CW * S, L.CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx, hy, r = 300, 290, 100
    skin, navy, navy_d, ink = (198, 140, 104), (40, 56, 108), (28, 40, 80), (28, 24, 30)
    dark = mix(skin, (60, 30, 20), 0.25); grey = (214, 214, 220)
    d.rounded_rectangle(P(hx - 72, 680, hx - 10, 862), radius=22 * S, fill=navy_d)
    d.rounded_rectangle(P(hx + 10, 680, hx + 72, 862), radius=22 * S, fill=navy_d)
    d.ellipse(P(hx - 96, 838, hx - 4, 888), fill=(30, 30, 36)); d.ellipse(P(hx + 4, 838, hx + 96, 888), fill=(30, 30, 36))
    d.rounded_rectangle(P(hx - 140, 410, hx + 140, 712), radius=70 * S, fill=navy)
    d.polygon(P(hx - 40, 410, hx, 470, hx + 40, 410), fill=(236, 238, 244))                       # shirt collar
    d.line(P(hx, 470, hx, 700), fill=navy_d, width=5 * S)
    for y in (510, 570, 630): d.ellipse(P(hx - 8, y - 8, hx + 8, y + 8), fill=(250, 200, 60))
    d.rounded_rectangle(P(hx + 46, 480, hx + 116, 530), radius=8 * S, fill=(250, 200, 60))         # badge
    d.text(P(hx + 81, 505), 'PORTARIA', font=F('InterDisplay-Black', 11 * S), fill=navy_d, anchor='mm')
    d.rounded_rectangle(P(hx - 112, 470, hx - 62, 560), radius=10 * S, fill=(30, 32, 40))         # radio
    d.rectangle(P(hx - 100, 440, hx - 92, 472), fill=(30, 32, 40))
    d.ellipse(P(hx - 100, 486, hx - 74, 512), fill=(70, 74, 86))
    for sx in (-1, 1):
        xo = hx + sx * 160
        d.rounded_rectangle(P(xo - 28, 430, xo + 28, 640), radius=26 * S, fill=navy)
        d.ellipse(P(xo - 30, 620, xo + 30, 680), fill=skin)
    d.rectangle(P(hx - 26, 370, hx + 26, 420), fill=dark)
    for sx in (-1, 1): d.ellipse(P(hx + sx * r - 22, hy - 10, hx + sx * r + 22, hy + 40), fill=skin)
    d.ellipse(P(hx - r, hy - r, hx + r, hy + r + 6), fill=skin)
    for sx in (-1, 1): d.ellipse(P(hx + sx * (r - 12) - 20, hy - 40, hx + sx * (r - 12) + 20, hy + 6), fill=grey)
    d.rounded_rectangle(P(hx - r - 4, hy - 70, hx + r + 4, hy - 30), radius=10 * S, fill=navy_d)    # cap band
    d.polygon(P(hx - r - 14, hy - 70, hx + r + 14, hy - 70, hx + r - 6, hy - 132, hx - r + 6, hy - 132), fill=navy)
    d.rounded_rectangle(P(hx - r + 10, hy - 40, hx + r + 30, hy - 22), radius=8 * S, fill=(20, 26, 50))  # visor
    d.ellipse(P(hx - 16, hy - 112, hx + 16, hy - 80), fill=(250, 200, 60))
    ey = hy + 14
    for sx in (-1, 1):
        ex = hx + sx * 38
        d.ellipse(P(ex - 19, ey - 22, ex + 19, ey + 22), fill=(255, 255, 255))
        d.ellipse(P(ex - 9, ey - 10, ex + 11, ey + 10), fill=ink)
        d.ellipse(P(ex - 3, ey - 6, ex + 3, ey), fill=(255, 255, 255))
        d.line(P(ex - 24, ey - 36, ex + 24, ey - 30 if sx < 0 else ey - 42), fill=grey, width=8 * S)
    d.ellipse(P(hx - 13, hy + 38, hx + 13, hy + 60), fill=dark)
    d.chord(P(hx - 58, hy + 52, hx + 58, hy + 92), 180, 360, fill=grey)                             # moustache
    d.arc(P(hx - 30, hy + 74, hx + 30, hy + 104), 20, 160, fill=(110, 40, 40), width=6 * S)
    return down(im)

def hooded_back(scale_h=0.66):
    """Hooded figure seen from behind, yellow hoodie, short."""
    im = Image.new('RGBA', (L.CW * S, L.CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx = 300; hood, hood_d, pants = (240, 190, 50), (214, 160, 30), (70, 70, 84)
    d.rounded_rectangle(P(hx - 70, 690, hx - 12, 862), radius=20 * S, fill=pants)
    d.rounded_rectangle(P(hx + 12, 690, hx + 70, 862), radius=20 * S, fill=pants)
    d.ellipse(P(hx - 92, 838, hx - 6, 886), fill=(40, 40, 46)); d.ellipse(P(hx + 6, 838, hx + 92, 886), fill=(40, 40, 46))
    d.rounded_rectangle(P(hx - 128, 420, hx + 128, 712), radius=74 * S, fill=hood)
    d.rounded_rectangle(P(hx - 122, 672, hx + 122, 712), radius=16 * S, fill=hood_d)
    for sx in (-1, 1):
        xo = hx + sx * 146
        d.rounded_rectangle(P(xo - 28, 440, xo + 28, 650), radius=26 * S, fill=hood)
        d.ellipse(P(xo - 22, 630, xo + 22, 672), fill=(190, 140, 110))
    d.ellipse(P(hx - 104, 250, hx + 104, 470), fill=hood)                                            # hood
    d.arc(P(hx - 70, 300, hx + 70, 450), 200, 340, fill=hood_d, width=6 * S)
    d.line(P(hx, 300, hx, 440), fill=hood_d, width=4 * S)
    sp = down(im)
    return sp.resize((sp.width, int(sp.height * scale_h)), Image.LANCZOS) if scale_h != 1 else sp

def outline_of(sp, col=(255, 255, 255), w=7, alpha=200):
    a = sp.getchannel('A'); outer = a.filter(ImageFilter.MaxFilter(w)); inner = a.filter(ImageFilter.MinFilter(3))
    edge = Image.fromarray(np.clip(np.asarray(outer, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8))
    out = Image.new('RGBA', sp.size, col + (0,)); out.putalpha(edge.point(lambda v: int(v * alpha / 255))); return out

def icon_mega(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.polygon([(22 * u, 40 * u), (60 * u, 22 * u), (60 * u, 78 * u), (22 * u, 60 * u)], fill=(226, 60, 60))
    d.rounded_rectangle((12 * u, 38 * u, 26 * u, 62 * u), radius=3 * u, fill=(90, 96, 108))
    d.rounded_rectangle((58 * u, 18 * u, 70 * u, 82 * u), radius=4 * u, fill=(190, 40, 40))
    d.rounded_rectangle((26 * u, 60 * u, 36 * u, 80 * u), radius=3 * u, fill=(90, 96, 108))
    for k, (a, b) in enumerate([(78, 34), (82, 50), (78, 66)]):
        d.line((74 * u, 50 * u + (b - 50) * 0.4 * u, a * u + 8 * u, b * u), fill=(250, 200, 60), width=int(4 * u))
    return im.resize((sz, sz), Image.LANCZOS)

def icon_chili(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    pts = [(30 + 50 * k / 20 + 6 * math.sin(k / 3), 34 + 46 * (k / 20) ** 1.6) for k in range(21)]
    for i, (x, y) in enumerate(pts):
        r = 13 * (1 - i / 24); d.ellipse(((x - r) * u, (y - r) * u, (x + r) * u, (y + r) * u), fill=(220, 40, 36))
    d.ellipse((24 * u, 24 * u, 40 * u, 40 * u), fill=(60, 150, 70)); d.line((32 * u, 26 * u, 40 * u, 10 * u), fill=(60, 150, 70), width=int(5 * u))
    d.ellipse((30 * u, 36 * u, 38 * u, 46 * u), fill=(255, 140, 130))
    return im.resize((sz, sz), Image.LANCZOS)

# ------------------------------------------------------------------ CCTV
_NOISE = None
def cctv(im, t, stamp_t=None, rec=True, label='CAM 02 · COPA'):
    global _NOISE
    a = np.asarray(im.convert('RGB'), np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 0.8
    a = a * np.array([0.95, 1.0, 0.95], np.float32) * 0.86 + 8
    a[::4] *= 0.78
    if _NOISE is None: _NOISE = np.random.default_rng(1).normal(0, 1, (4, H, W, 1)).astype(np.float32)
    a += _NOISE[int(t * 15) % 4] * 9
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    out = L.apply_vig(out, CCTV_VIG)
    d = ImageDraw.Draw(out); fm = F('Inter-Bold', 40)
    d.text((70, 420), label, font=fm, fill=(236, 240, 236), stroke_width=3, stroke_fill=(20, 24, 22))
    if stamp_t is not None:
        secs = int(stamp_t); txt = f'08/11  11:{58 + secs // 60:02d}:{secs % 60:02d}'
        d.text((W - 70, 420), txt, font=fm, fill=(236, 240, 236), anchor='ra', stroke_width=3, stroke_fill=(20, 24, 22))
    if rec and int(t * 2) % 2 == 0:
        d.ellipse((W - 190, 486, W - 160, 516), fill=(236, 40, 40)); d.text((W - 148, 482), 'REC', font=fm, fill=(236, 40, 40), stroke_width=3, stroke_fill=(20, 24, 22))
    for (x0, y0, sx, sy) in [(50, 300, 1, 1), (W - 50, 300, -1, 1), (50, 1290, 1, -1), (W - 50, 1290, -1, -1)]:
        d.line((x0, y0, x0 + 60 * sx, y0), fill=(236, 240, 236), width=5); d.line((x0, y0, x0, y0 + 60 * sy), fill=(236, 240, 236), width=5)
    return out

# ------------------------------------------------------------------ setup
def setup():
    global KICKER, ZE_ST, PED, PED_ST, PED_OUT, BACK, BOX_B, PILL_ESC, PILL_ZE, VIG, K_BG, CCTV_VIG, MON, CARD_A, CARD_B
    global CTA, SUB, FOLLOW, EMPTY, QM, DROP, CHART_FONT, EQ, ARROW
    KICKER = L.build_kicker('A MARMITA SUMIU  ·  EP. 3')
    ZE_ST = L.sticker(ze())
    PED = E2.pedro(); PED_ST = L.sticker(PED); PED_OUT = outline_of(PED, (255, 255, 255), 9, 230)
    BACK = hooded_back(0.70)
    BOX_B = E2.marmita(E2.LID_BLUE, 150)
    PILL_ESC = L.label_pill('VOCÊS ESCOLHERAM', 'B', B_COL)
    PILL_ZE = E2.pill('SEU ZÉ, O PORTEIRO')
    VIG = L.make_vig(0.32, cy=0.45); CCTV_VIG = L.make_vig(0.7, cy=0.5)
    K_BG = L.build_s1()
    MON = Image.new('RGBA', (430, 330), (0, 0, 0, 0)); dm = ImageDraw.Draw(MON)
    dm.rounded_rectangle((0, 0, 429, 290), radius=22, fill=(30, 32, 40)); dm.rounded_rectangle((18, 18, 411, 272), radius=10, fill=(60, 84, 80))
    dm.rectangle((190, 290, 240, 316), fill=(30, 32, 40)); dm.rounded_rectangle((130, 312, 300, 329), radius=8, fill=(30, 32, 40))
    CARD_A = M.card('A', 'Acusar o Pedro', A_COL, (30, 20, 8), A_COL, (30, 20, 8))
    CARD_B = M.card('B', 'Armar armadilha', B_COL, (64, 10, 14), (255, 228, 228), WHITE)
    for c, ic in ((CARD_A, icon_mega()), (CARD_B, icon_chili())):
        c.alpha_composite(E2.badge(ic, 140), (30 + 900 - 22 - 140, 30 + 20))
    CTA = rich_line([('Comenta ', WHITE), ('A', A_COL), (' ou ', WHITE), ('B', B_COL)], F('InterDisplay-ExtraBold', 76))
    SUB = rich_line([('O mais votado vira o episódio 4', (232, 244, 244))], F('Inter-SemiBold', 38), stroke=4)
    FOLLOW = rich_line([('Segue pra não perder o ', WHITE), ('ep. 4', A_COL)], F('InterDisplay-ExtraBold', 46), stroke=5)
    EMPTY = L.build_empty_box()
    f = F('InterDisplay-Black', 120)
    QM = Image.new('RGBA', (110, 160), (0, 0, 0, 0))
    ImageDraw.Draw(QM).text((55, 80), '?', font=f, fill=WHITE, anchor='mm', stroke_width=7, stroke_fill=INK)
    DROP = Image.new('RGBA', (60, 84), (0, 0, 0, 0)); dd = ImageDraw.Draw(DROP)
    dd.ellipse((8, 26, 52, 78), fill=(120, 200, 255), outline=(28, 22, 30), width=4); dd.polygon([(12, 44), (30, 2), (48, 44)], fill=(120, 200, 255))
    dd.line((12, 44, 30, 4), fill=(28, 22, 30), width=4); dd.line((48, 44, 30, 4), fill=(28, 22, 30), width=4)
    CHART_FONT = F('InterDisplay-ExtraBold', 40)
    EQ = rich_line([('=', WHITE)], F('InterDisplay-Black', 150), stroke=8)
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
    CAP['s6'] = Caption([(0.1, DURS['s6'] + 5, [(0.15, 'E AGORA?', WHITE)])], font=('InterDisplay-Black', 104), top=330, maxw=980, gap=0.12)

def finish(im, k, t):
    comp(im, KICKER, ((W - KICKER.width) // 2, 196)); CAP[k].draw(im, t); return im.convert('RGB')

FEET = L.LEO_FEET
def kitchen_with(cx, carrying=False, fridge_open=0.0):
    im = K_BG.copy()
    if fridge_open > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((604, 436, 996, 1296), radius=28, fill=(255, 255, 230, int(150 * fridge_open)))
        im.alpha_composite(lay)
    bk = BACK
    comp(im, bk, (cx - bk.width / 2, FEET - bk.height + 6))
    if carrying:
        comp(im, BOX_B, (cx - 150 - BOX_B.width / 2, FEET - bk.height * 0.33 - BOX_B.height / 2))
    return im

# ------------------------------------------------------------------ scenes
def frame_s1(t):
    bob = -abs(math.sin(2 * math.pi * 1.3 * t)) * 8
    im = cctv(kitchen_with(780, False, 0.0), t, stamp_t=None)
    if t > 0.05:
        s = lerp(0.55, 1.0, L.backout((t - 0.05) / 0.4))
        pi = sc(PILL_ESC, s); comp(im, pi, (540 - pi.width / 2, 600 - pi.height / 2), clamp((t - 0.05) * 6))
    for (qx, qy, ph) in [(790, 760, 0.0)]:
        comp(im, QM, (qx - 55, qy - 80 + 10 * math.sin(2 * math.pi * t / 1.3 + ph)), clamp((t - 0.4) * 3))
    return finish(im, 's1', t)

def frame_s2(t):
    im = L.apply_vig(L.rays(t, (60, 96, 176), (74, 112, 196)), VIG)
    q = t / 0.4; oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    bob = 4 * math.sin(2 * math.pi * t / 1.5)
    zs = sc(ZE_ST, 0.9)
    comp(im, zs, (330 - zs.width / 2, 1330 - zs.height + oy + bob))
    mx, my = 790, 760
    comp(im, MON, (mx - MON.width / 2, my - MON.height / 2), clamp((t - 0.3) * 4))
    if t > 0.3:
        T2 = p2_at('s2')
        sec = 183 - 183 * eio(clamp((t - T2) / 1.4)) if t >= T2 else 183
        mm, ss = divmod(int(sec), 60)
        txt = f'12:{mm:02d}:{ss:02d}' if sec >= 120 else f'11:{58 + mm:02d}:{ss:02d}'
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((mx, my - 20), txt, font=F('InterDisplay-Black', 64), fill=(200, 255, 220), anchor='mm')
        if T2 <= t < T2 + 1.4:
            for k in range(2):
                x0 = mx - 60 + k * 56
                d.polygon([(x0 + 50, my + 40), (x0 + 50, my + 100), (x0, my + 70)], fill=(200, 255, 220))
        im.alpha_composite(lay)
    if t > 0.15:
        s = lerp(0.55, 1.0, L.backout((t - 0.15) / 0.4))
        pi = sc(PILL_ZE, s); comp(im, pi, (540 - pi.width / 2, 340 - pi.height / 2), clamp((t - 0.15) * 6))
    return finish(im, 's2', t)

def frame_s3(t):
    T2 = p2_at('s3'); dur = DURS['s3']
    tw = max(0.8, T2 - 0.9)
    if t < tw:   cx, carry, fo = lerp(150, 690, eio(t / tw)), False, 0.0
    elif t < T2: cx, carry, fo = 690, False, clamp((t - tw) / 0.3)
    else:        cx, carry, fo = lerp(690, -220, eio(clamp((t - T2 - 0.2) / max(0.6, dur - T2 - 0.4)))), True, clamp(1 - (t - T2) / 0.4)
    bob = -abs(math.sin(2 * math.pi * 1.5 * t)) * 10 if (t < tw or t > T2 + 0.2) else 0
    im = kitchen_with(cx, carry, fo)
    if bob: pass
    im = cctv(im, t, stamp_t=t * 1.0)
    if carry and t > T2 + 0.1:
        bx = cx - 150; by = FEET - BACK.height * 0.33
        E2.rings(im, int(bx), int(by), t, (120, 190, 255), 60, 140)
    return finish(im, 's3', t)

def frame_s4(t):
    im = L.apply_vig(L.rays(t, (255, 200, 40), (255, 220, 110)), VIG)
    still = cctv(kitchen_with(560, True, 0.0), 0.3, stamp_t=5, rec=False).crop((240, 520, 840, 1340)).resize((300, 410), Image.LANCZOS)
    fr = Image.new('RGBA', (still.width + 24, still.height + 24), (255, 255, 255, 255)); fr.alpha_composite(still, (12, 12))
    fr = fr.rotate(6, resample=Image.BICUBIC, expand=True)
    k0 = eo(clamp(t / 0.35))
    comp(im, fr, (lerp(-400, 70, k0), 470), k0)
    T2 = p2_at('s4')
    if t >= T2 - 0.1:
        q = (t - T2 + 0.1) / 0.45; oy = (1 - L.backout(q)) * 560 if q < 1 else 0
        ps = sc(PED_ST, 0.86)
        bob = 4 * math.sin(2 * math.pi * t / 1.4)
        comp(im, ps, (700 - ps.width / 2, 1330 - ps.height + oy + bob))
        if t > T2 + 0.4:
            for i, (dx, dy, ph) in enumerate([(-150, 300, 0.0), (140, 260, 0.4)]):
                k = ((t - T2) * 1.6 + ph) % 1.0
                comp(im, DROP, (700 + dx, 1330 - ps.height + dy + k * 80), 1 - k)
        if t > T2 + 0.25:
            k = clamp((t - T2 - 0.25) / 0.25); eq = sc(EQ, lerp(1.6, 1.0, eo(k)))
            comp(im, eq, (430 - eq.width / 2, 700 - eq.height / 2), k)
    return finish(im, 's4', t)

def frame_s5(t):
    base = K_BG.copy()
    bk = BACK
    comp(base, bk, (430 - bk.width / 2, FEET - bk.height + 6))
    im = cctv(base, t, stamp_t=12, rec=True)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, (lab, hpx) in enumerate([('1,20', 270), ('1,40', 450), ('1,60', 630), ('1,80', 810)]):
        y = FEET - hpx
        for x in range(180, 1000, 40): d.line((x, y, x + 22, y), fill=(255, 255, 255, 170), width=4)
        d.text((160, y), lab, font=CHART_FONT, fill=(255, 255, 255, 240), anchor='rm', stroke_width=4, stroke_fill=(20, 24, 22))
    im.alpha_composite(lay)
    T2 = p2_at('s5')
    if t >= T2 - 0.2:
        k = clamp((t - T2 + 0.2) / 0.4)
        po = PED_OUT.copy(); po.putalpha(po.getchannel('A').point(lambda v: int(v * k)))
        comp(im, po, (720 - po.width / 2, FEET - 884 + 6))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        yb, yp = FEET - bk.height * 0.86, FEET - 884 + 40
        d.line((330, yb, 560, yb), fill=(255, 70, 70, int(255 * k)), width=8)
        d.line((620, yp, 840, yp), fill=(255, 255, 255, int(255 * k)), width=6)
        if t > T2 + 0.4:
            q = eo(clamp((t - T2 - 0.4) / 0.5)); ya = lerp(yp, yb, q)
            d.line((600, yp, 600, ya), fill=(255, 70, 70, 255), width=8)
            d.polygon([(584, ya - 20), (616, ya - 20), (600, ya + 4)], fill=(255, 70, 70, 255))
        im.alpha_composite(lay)
    return finish(im, 's5', t)

def frame_s6(t):
    im = E2.S6_BG(t)
    for (img, y, t0, side, phase) in [(CARD_A, 520, 0.5, -1, 0.0), (CARD_B, 750, 0.8, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45); x = (W - img.width) / 2 + side * (1 - p) * 160
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.6) / 1.5 + phase) if t > 2.6 else 1.0
        i2 = sc(img, s); comp(im, i2, (x + img.width / 2 - i2.width / 2, y + img.height / 2 - i2.height / 2), p)
    if t >= 1.4: p = eo((t - 1.4) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1010 + (1 - p) * 24), p)
    if t >= 1.8: p = eo((t - 1.8) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1115 + (1 - p) * 18), p)
    if t >= 2.3:
        p = eo((t - 2.3) / 0.4); pul = 1 + 0.03 * math.sin(2 * math.pi * t / 1.2)
        fo = sc(FOLLOW, pul); comp(im, fo, ((W - fo.width) / 2, 1190 + (1 - p) * 18), p)
    if t >= 0.3:
        p = L.backout((t - 0.3) / 0.5); bob = 6 * math.sin(2 * math.pi * t / 1.7)
        comp(im, EMPTY, (540 - EMPTY.width / 2, 1380 + (1 - p) * 300 + bob), clamp((t - 0.3) * 4))
    return finish(im, 's6', t)

SCENES = [('s1', frame_s1), ('s2', frame_s2), ('s3', frame_s3), ('s4', frame_s4), ('s5', frame_s5), ('s6', frame_s6)]

# ------------------------------------------------------------------ audio
def build_audio(path):
    SR = LA.SR; rng = np.random.default_rng(3)
    st, acc = {}, 0.0
    for k in ORDER: st[k] = acc; acc += round(DURS[k] * FPS) / FPS
    total = acc; n = int(total * SR)
    music = np.zeros(n)
    def put(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if i < n: music[i:j] += sig[:j - i]
    put(LA.groove(st['s3']), 0); put(LA.groove(st['s4'] - st['s3'], full=False), st['s3'])
    put(LA.groove(st['s5'] - st['s4']), st['s4']); put(LA.groove(st['s6'] - st['s5'], full=False), st['s5'])
    put(LA.groove(total - st['s6']), st['s6'])
    fx = np.zeros(n + 3 * SR)
    def add(sig, at, g=1.0):
        i = int(at * SR); fx[i:i + len(sig)] += sig * g
    def static(d=0.35, g=0.25):
        y = LA.bandpass(rng.standard_normal(int(d * SR)), 900, 7000); y /= np.abs(y).max()
        tq = np.arange(len(y)) / SR; return y * g * np.exp(-tq / (d / 2.5))
    add(static(0.4, 0.35), st['s1']); add(LA.blip(1200, 1200, 0.08, 0.25), st['s1'] + 0.3); add(LA.thunk(), st['s1'] + 0.05)
    add(LA.whoosh(0.25, 0.25), st['s2'])
    T2 = p2_at('s2')
    for k in range(12): add(LA.blip(1600 - 70 * k, 1500 - 70 * k, 0.05, 0.12), st['s2'] + T2 + k * 0.11)
    add(static(0.3, 0.3), st['s3'])
    for k in range(int(max(0.8, p2_at('s3') - 0.9) / 0.42)): add(LA.step(0.15), st['s3'] + k * 0.42)
    add(LA.thunk(), st['s3'] + max(0.8, p2_at('s3') - 0.9)); add(LA.ding(1174.7), st['s3'] + p2_at('s3'))
    add(LA.whoosh(), st['s4']); add(LA.slide_whistle(), st['s4'] + p2_at('s4') - 0.15); add(LA.crash(), st['s4'] + p2_at('s4') + 0.25, 0.7)
    add(static(0.3, 0.3), st['s5']); add(LA.blip(500, 900, 0.1, 0.3), st['s5'] + p2_at('s5'))
    add(LA.thunk(), st['s5'] + p2_at('s5') + 0.4)
    add(LA.tada(), st['s6']); add(LA.blip(400, 800, 0.1, 0.3), st['s6'] + 0.5); add(LA.blip(450, 900, 0.1, 0.3), st['s6'] + 0.8)
    add(LA.blip(500, 1000, 0.1, 0.3), st['s6'] + 1.4)
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
    mixm *= np.clip((total - t) / 0.6, 0, 1) * np.clip(t / 0.03, 0, 1)
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
        shots = [('s1', 0.9), ('s2', p2_at('s2') + 0.7), ('s3', p2_at('s3') - 0.5), ('s3', p2_at('s3') + 0.6),
                 ('s4', p2_at('s4') + 0.8), ('s5', p2_at('s5') + 1.2), ('s6', 3.5), ('s2', 0.3)]
        sheet = Image.new('RGB', (W // 3 * 4, H // 3 * 2))
        for i, (k, tt) in enumerate(shots):
            sheet.paste(fns[k](tt).resize((W // 3, H // 3), Image.LANCZOS), ((i % 4) * (W // 3), (i // 4) * (H // 3)))
        sheet.save(WORK + '/sheet.png'); print('sheet', DURS, round(sum(DURS.values()), 2))
    elif mode == 'render':
        only = sys.argv[2:] or ORDER
        for idx, (k, fn) in enumerate(SCENES):
            if k in only: L.encode(k, fn, DURS[k], fade_in=0, fade_out=12 if idx == len(SCENES) - 1 else 0)
        if all(os.path.exists(f'{WORK}/{k}.mp4') for k in ORDER): assemble(WORK + '/a-marmita-sumiu-ep3.mp4')
    elif mode == 'audio':
        assemble(WORK + '/a-marmita-sumiu-ep3.mp4')
