#!/usr/bin/env python3
"""A Marmita Sumiu — Episódio 2 (venceu A: Ju do RH). Reuses the episode 1 toolkit in /home/claude/lunch.

python3 ep2.py preview            -> sheet.png
python3 ep2.py render [scenes...] -> s1..s6.mp4 (+ audio + final mp4 when all scenes are rendered)
Timing comes from timing2.json (made by nar2.py from a narration file) or is synthesized from the text.
"""
import os, sys, math, json, time, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch')
import make as M
import lunch as L
import laudio as LA
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, down, Caption, rich_line, WHITE, INK

W, H, S, FPS = 1080, 1920, 2, 30
WORK = '/home/claude/marmita2'
L.WORK = WORK
A_COL, B_COL, YEL = L.A_COL, L.B_COL, L.YEL
BLUE_T = (120, 190, 255)
LID_BLUE = (80, 150, 230)
mix = L.mix

# ------------------------------------------------------------------ script
PAGES = {
    's1': [[('Vocês acusaram a Ju do RH!', A_COL)], [('O Léo foi tirar satisfação.', WHITE)]],
    's2': [[('Ela riu: o cheiro era da lasanha dela…', WHITE)], [('receita da vó dela também!', A_COL)]],
    's3': [[('E um de vocês reparou: o bilhete é de', WHITE), ('caneta azul…', BLUE_T)],
           [('e a Ju só escreve a', WHITE), ('lápis.', A_COL)]],
    's4': [[('Mas ela viu alguém saindo da copa ao meio-dia…', WHITE)],
           [('com uma marmita de', WHITE), ('tampa azul!', BLUE_T)]],
    's5': [[('Era o Pedro,', WHITE)], [('o estagiário!', A_COL)]],
}
ORDER = ['s1', 's2', 's3', 's4', 's5', 's6']
TIMING = WORK + '/timing2.json'

def synth_timing():
    """Reading-speed timing when there is no narration."""
    out = {'durs': {}, 'pages': {}, 'gaps': {}, 'nar': []}
    for k in ORDER[:-1]:
        t, pages = 0.3, []
        for segs in PAGES[k]:
            txt = ' '.join(s for s, _ in segs)
            pages.append([round(t, 3), [[s, list(c)] for s, c in segs]])
            t += 0.55 + 0.062 * len(txt)
        out['pages'][k] = pages; out['durs'][k] = round(t + 0.35, 3); out['gaps'][k] = 0.12
    out['durs']['s6'] = 7.5
    return out

TJ = json.load(open(TIMING)) if os.path.exists(TIMING) else synth_timing()
DURS = {k: TJ['durs'][k] for k in ORDER}
def p2_at(k):  # start of the 2nd caption page of scene k
    return TJ['pages'][k][1][0]

# ------------------------------------------------------------------ art
def pedro():
    im = Image.new('RGBA', (L.CW * S, L.CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx, hy, r = 300, 240, 105
    skin, hood, hood_d = (214, 150, 108), (255, 200, 40), (232, 166, 18)
    pants, shoe, cap, cap_d, hair, ink = (46, 58, 96), (250, 250, 252), (220, 48, 52), (168, 30, 36), (60, 40, 30), (28, 24, 30)
    dark = mix(skin, (60, 30, 20), 0.25); tw = 260
    d.rounded_rectangle(P(hx - 150, 380, hx + 150, 640), radius=50 * S, fill=(40, 110, 200))          # backpack
    d.rounded_rectangle(P(hx - 150, 380, hx + 150, 420), radius=20 * S, fill=(30, 90, 170))
    d.rounded_rectangle(P(hx - 78, 660, hx - 10, 862), radius=22 * S, fill=pants)
    d.rounded_rectangle(P(hx + 10, 660, hx + 78, 862), radius=22 * S, fill=pants)
    d.ellipse(P(hx - 100, 838, hx - 6, 888), fill=shoe); d.ellipse(P(hx + 6, 838, hx + 100, 888), fill=shoe)
    d.rounded_rectangle(P(hx - tw / 2, 360, hx + tw / 2, 704), radius=80 * S, fill=hood)
    d.rounded_rectangle(P(hx - tw / 2 + 6, 664, hx + tw / 2 - 6, 704), radius=16 * S, fill=hood_d)
    d.rounded_rectangle(P(hx - 84, 566, hx + 84, 646), radius=22 * S, fill=hood_d)
    for sx in (-1, 1):
        d.rounded_rectangle(P(hx + sx * 96 - 14, 372, hx + sx * 96 + 14, 560), radius=10 * S, fill=(30, 90, 170))
    d.line(P(hx - 22, 384, hx - 28, 480), fill=(252, 252, 252), width=6 * S)
    d.line(P(hx + 22, 384, hx + 28, 480), fill=(252, 252, 252), width=6 * S)
    for sx in (-1, 1):
        xo = hx + sx * (tw / 2 + 20)
        d.rounded_rectangle(P(xo - 28, 380, xo + 28, 612), radius=26 * S, fill=hood)
        d.ellipse(P(xo - 30, 592, xo + 30, 652), fill=skin)
    d.ellipse(P(hx - 124, 300, hx + 124, 404), fill=hood_d)                                            # hood behind neck
    d.rectangle(P(hx - 26, 318, hx + 26, 372), fill=dark)
    for sx in (-1, 1):
        d.ellipse(P(hx + sx * r - 24, hy - 14, hx + sx * r + 24, hy + 38), fill=skin)
    d.ellipse(P(hx - r, hy - r, hx + r, hy + r + 6), fill=skin)
    for sx in (-1, 1):
        d.ellipse(P(hx + sx * (r - 14) - 24, hy - 62, hx + sx * (r - 14) + 24, hy - 6), fill=hair)
    d.pieslice(P(hx - r - 8, hy - r - 34, hx + r + 8, hy + r - 56), 180, 360, fill=cap)                # cap dome
    d.rounded_rectangle(P(hx - r - 8, hy - 60, hx + r + 78, hy - 34), radius=13 * S, fill=cap_d)       # brim
    d.ellipse(P(hx - 12, hy - r - 42, hx + 12, hy - r - 18), fill=cap_d)
    d.text(P(hx - 6, hy - 92), 'P', font=F('InterDisplay-Black', 54 * S), fill=(255, 255, 255), anchor='mm')
    ey = hy + 14
    for sx in (-1, 1):
        ex = hx + sx * 40
        d.ellipse(P(ex - 22, ey - 27, ex + 22, ey + 27), fill=(255, 255, 255))
        d.ellipse(P(ex - 1, ey - 16, ex + 23, ey + 8), fill=ink)
        d.ellipse(P(ex + 4, ey - 12, ex + 10, ey - 6), fill=(255, 255, 255))
        d.arc(P(ex - 26, ey - 62, ex + 26, ey - 32), 200, 340, fill=hair, width=7 * S)
    d.ellipse(P(hx - 12, hy + 42, hx + 12, hy + 60), fill=dark)
    blush = mix(skin, (255, 110, 130), 0.35)
    d.ellipse(P(hx - 86, hy + 48, hx - 52, hy + 68), fill=blush); d.ellipse(P(hx + 52, hy + 48, hx + 86, hy + 68), fill=blush)
    d.chord(P(hx - 46, hy + 54, hx + 46, hy + 112), 0, 180, fill=(110, 32, 44))
    d.ellipse(P(hx - 20, hy + 86, hx + 20, hy + 104), fill=(232, 106, 118))
    d.ellipse(P(hx + 42, hy + 70, hx + 60, hy + 88), fill=(208, 64, 44))                              # sauce on the cheek
    return down(im)

def marmita(lid, w=230, steam=False):
    h = int(w * 0.62)
    im = Image.new('RGBA', ((w + 24) * S, (h + 24) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle(P(12, 12 + h * 0.3, 12 + w, 12 + h), radius=20 * S, fill=(238, 244, 248), outline=(176, 196, 208), width=5 * S)
    d.rounded_rectangle(P(4, 12, 20 + w, 12 + h * 0.38), radius=16 * S, fill=lid, outline=mix(lid, (0, 0, 0), 0.3), width=4 * S)
    d.rounded_rectangle(P(12 + w * 0.36, 2, 12 + w * 0.64, 20), radius=7 * S, fill=mix(lid, (0, 0, 0), 0.3))
    return down(im)

def silhouette(sp, col=(30, 30, 48)):
    out = Image.new('RGBA', sp.size, col + (0,)); out.putalpha(sp.getchannel('A')); return out

def stamp(text='ACUSADA!'):
    f = F('InterDisplay-Black', 116); red = (226, 36, 48)
    tw = f.getlength(text); w, h = int(tw + 90), 186
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=26, outline=red, width=15)
    d.text((20 + w / 2, 20 + h / 2 + 4), text, font=f, fill=red, anchor='mm')
    a = np.array(im); rng = np.random.default_rng(3)
    m = rng.random(a.shape[:2]) < 0.07; a[..., 3][m] = (a[..., 3][m] * 0.25).astype(np.uint8)
    return Image.fromarray(a).rotate(-9, resample=Image.BICUBIC, expand=True)

def icon_pen(sz=150):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.rounded_rectangle((18 * u, 42 * u, 78 * u, 58 * u), radius=7 * u, fill=(40, 70, 160))
    d.polygon([(78 * u, 43 * u), (92 * u, 50 * u), (78 * u, 57 * u)], fill=(214, 214, 222))
    d.polygon([(88 * u, 48 * u), (95 * u, 50 * u), (88 * u, 52 * u)], fill=(30, 50, 120))
    d.rounded_rectangle((10 * u, 43 * u, 26 * u, 57 * u), radius=6 * u, fill=(30, 52, 130))
    d.rounded_rectangle((20 * u, 36 * u, 46 * u, 41 * u), radius=2 * u, fill=(30, 52, 130))
    return im.rotate(28, resample=Image.BICUBIC).resize((sz, sz), Image.LANCZOS)

def icon_pencil(sz=150):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.rectangle((22 * u, 42 * u, 74 * u, 58 * u), fill=(250, 200, 60))
    d.line((22 * u, 47 * u, 74 * u, 47 * u), fill=(230, 170, 40), width=int(2 * u))
    d.line((22 * u, 53 * u, 74 * u, 53 * u), fill=(230, 170, 40), width=int(2 * u))
    d.polygon([(74 * u, 42 * u), (90 * u, 50 * u), (74 * u, 58 * u)], fill=(238, 206, 160))
    d.polygon([(85 * u, 47.5 * u), (91 * u, 50 * u), (85 * u, 52.5 * u)], fill=(70, 70, 80))
    d.rectangle((16 * u, 42 * u, 22 * u, 58 * u), fill=(190, 190, 200))
    d.rounded_rectangle((6 * u, 42 * u, 18 * u, 58 * u), radius=4 * u, fill=(240, 150, 160))
    return im.rotate(28, resample=Image.BICUBIC).resize((sz, sz), Image.LANCZOS)

def icon_trash(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.polygon([(28 * u, 34 * u), (72 * u, 34 * u), (66 * u, 86 * u), (34 * u, 86 * u)], fill=(120, 128, 140))
    for x in (40, 50, 60): d.line((x * u, 42 * u, x * u, 78 * u), fill=(90, 96, 108), width=int(3 * u))
    d.rounded_rectangle((22 * u, 24 * u, 78 * u, 34 * u), radius=3 * u, fill=(96, 104, 116))
    d.rounded_rectangle((42 * u, 16 * u, 58 * u, 26 * u), radius=3 * u, fill=(96, 104, 116))
    d.ellipse((60 * u, 8 * u, 72 * u, 18 * u), fill=(230, 140, 60))     # banana peel-ish blob
    return im.resize((sz, sz), Image.LANCZOS)

def icon_cam(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.rectangle((14 * u, 16 * u, 30 * u, 22 * u), fill=(90, 96, 108))
    d.line((22 * u, 20 * u, 30 * u, 40 * u), fill=(90, 96, 108), width=int(5 * u))
    body = Image.new('RGBA', im.size, (0, 0, 0, 0)); db = ImageDraw.Draw(body)
    db.rounded_rectangle((24 * u, 34 * u, 80 * u, 58 * u), radius=6 * u, fill=(236, 238, 244), outline=(110, 116, 128), width=int(3 * u))
    db.ellipse((70 * u, 38 * u, 86 * u, 54 * u), fill=(40, 44, 56))
    db.ellipse((75 * u, 43 * u, 81 * u, 49 * u), fill=(120, 190, 255))
    db.ellipse((30 * u, 40 * u, 37 * u, 47 * u), fill=(230, 50, 50))
    body = body.rotate(-14, center=(30 * u, 40 * u), resample=Image.BICUBIC)
    im.alpha_composite(body)
    return im.resize((sz, sz), Image.LANCZOS)

def badge(icon, size=140):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size - 1, size - 1), fill=(255, 255, 255), outline=(28, 22, 30), width=5)
    ic = icon.resize((int(size * 0.86), int(size * 0.86)), Image.LANCZOS)
    im.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2))
    return im

def pill(text, icon=None, fsz=50):
    f = F('InterDisplay-Black', fsz); tw = f.getlength(text); h = 96
    w = int(tw + 60 + (86 if icon else 0))
    im = Image.new('RGBA', (w + 40, h + 46), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((20, 30, 20 + w, 30 + h), radius=h // 2, fill=150)
    im.paste((40, 10, 20, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=h // 2, fill=(255, 255, 255))
    x = 20 + 30
    if icon:
        d.ellipse((20 + 12, 20 + 12, 20 + 12 + 72, 20 + 12 + 72), fill=(26, 22, 30))
        im.alpha_composite(icon.resize((56, 56), Image.LANCZOS), (20 + 20, 20 + 20)); x = 20 + 12 + 72 + 18
    d.text((x, 20 + h / 2 + 2), text, font=f, fill=(26, 22, 30), anchor='lm')
    return im

def icon_lens(sz=56):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.ellipse((14 * u, 14 * u, 62 * u, 62 * u), outline=(255, 255, 255), width=int(11 * u))
    d.line((56 * u, 56 * u, 84 * u, 84 * u), fill=(255, 255, 255), width=int(14 * u))
    return im.resize((sz, sz), Image.LANCZOS)

def scaled(img, s):
    return img if abs(s - 1) < 1e-3 else img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)

def rings(im, cx, cy, t, col=(255, 255, 255), r0=40, r1=110):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for off in (0.0, 0.5):
        k = (t * 1.3 + off) % 1.0; r = r0 + (r1 - r0) * k
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col + (int(255 * (1 - k)),), width=8)
    im.alpha_composite(lay)

# ------------------------------------------------------------------ setup
def setup():
    global KICKER, JU, JU_ST, LEO_ST, PED, PED_ST, PED_SIL, BOX_J, BOX_B, STAMP, PILL_ESC, PILL_EST, PILL_CLUE
    global VIG, NOTE_FULL, PEN, PENCIL, NEQ, K_BG, DARK, CARD_A, CARD_B, CTA, SUB, FOLLOW, EMPTY, QM, HAHA, VO
    KICKER = L.build_kicker('A MARMITA SUMIU  ·  EP. 2')
    JU = L.person('ju'); JU_ST = L.sticker(JU); LEO_ST = L.sticker(L.person('leo'))
    PED = pedro(); PED_ST = L.sticker(PED); PED_SIL = silhouette(PED)
    BOX_J, BOX_B = marmita((150, 96, 214)), marmita(LID_BLUE, 190)
    STAMP = stamp()
    PILL_ESC = L.label_pill('VOCÊS ESCOLHERAM', 'A', A_COL)
    PILL_EST = L.label_pill('O ESTAGIÁRIO', '!', B_COL)
    PILL_CLUE = pill('PISTA DOS COMENTÁRIOS', icon_lens())
    VIG = L.make_vig(0.32, cy=0.45)
    L.setup_s3()
    note = L.NOTE_B.copy(); note.alpha_composite(L.NOTE_T1); note.alpha_composite(L.NOTE_T2); note.alpha_composite(L.NOTE_SM)
    NOTE_FULL = scaled(note.rotate(-4, resample=Image.BICUBIC, expand=True), 0.58)
    PEN, PENCIL = icon_pen(190), icon_pencil(190)
    f = F('InterDisplay-Black', 150)
    NEQ = Image.new('RGBA', (170, 200), (0, 0, 0, 0))
    ImageDraw.Draw(NEQ).text((85, 100), '≠', font=f, fill=(226, 36, 48), anchor='mm', stroke_width=6, stroke_fill=(255, 255, 255))
    K_BG = L.build_s1()
    a = np.asarray(K_BG.convert('RGB'), np.float32) * np.array([0.42, 0.44, 0.62], np.float32)
    DARK = L.apply_vig(Image.fromarray(a.astype(np.uint8)), L.make_vig(0.55, cy=0.5))
    CARD_A = M.card('A', 'Revirar o lixo', A_COL, (30, 20, 8), A_COL, (30, 20, 8))
    CARD_B = M.card('B', 'Ver as câmeras', B_COL, (64, 10, 14), (255, 228, 228), WHITE)
    for c, ic in ((CARD_A, icon_trash()), (CARD_B, icon_cam())):
        c.alpha_composite(badge(ic, 140), (30 + 900 - 22 - 140, 30 + 20))
    CTA = rich_line([('Comenta ', WHITE), ('A', A_COL), (' ou ', WHITE), ('B', B_COL)], F('InterDisplay-ExtraBold', 76))
    SUB = rich_line([('O mais votado vira o episódio 3', (232, 244, 244))], F('Inter-SemiBold', 38), stroke=4)
    FOLLOW = rich_line([('Segue pra não perder o ', WHITE), ('ep. 3', A_COL)], F('InterDisplay-ExtraBold', 46), stroke=5)
    EMPTY = L.build_empty_box()
    f = F('InterDisplay-Black', 120)
    QM = Image.new('RGBA', (110, 160), (0, 0, 0, 0))
    ImageDraw.Draw(QM).text((55, 80), '?', font=f, fill=WHITE, anchor='mm', stroke_width=7, stroke_fill=INK)
    HAHA = rich_line([('HAHA', WHITE)], F('InterDisplay-Black', 70), stroke=7)
    VO = Image.new('RGBA', (430, 150), (0, 0, 0, 0)); dv = ImageDraw.Draw(VO)
    dv.rounded_rectangle((6, 6, 424, 144), radius=22, fill=(255, 250, 236), outline=(200, 170, 120), width=4)
    dv.text((190, 75), 'receita da vó', font=ImageFont.truetype(L.CAVEAT, 64), fill=(200, 60, 90), anchor='mm')
    hx0, hy0 = 372, 70
    dv.ellipse((hx0 - 22, hy0 - 18, hx0 + 2, hy0 + 6), fill=(226, 60, 90)); dv.ellipse((hx0 - 2, hy0 - 18, hx0 + 22, hy0 + 6), fill=(226, 60, 90))
    dv.polygon([(hx0 - 21, hy0 - 2), (hx0 + 21, hy0 - 2), (hx0, hy0 + 26)], fill=(226, 60, 90))
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
    comp(im, KICKER, ((W - KICKER.width) // 2, 196))
    CAP[k].draw(im, t)
    return im.convert('RGB')

def shake(t, t0, amp=16, d=0.3):
    if t0 <= t < t0 + d:
        k = 1 - (t - t0) / d
        return amp * k * math.sin(2 * math.pi * 31 * t), amp * 0.6 * k * math.cos(2 * math.pi * 27 * t)
    return 0, 0

# ------------------------------------------------------------------ scenes
def frame_s1(t):
    im = L.apply_vig(L.rays(t, (255, 196, 92), (255, 212, 128)), VIG)
    T2 = p2_at('s1'); m = eio(clamp((t - T2) / 0.5))
    sx, sy = shake(t, 0.42)
    q = t / 0.45; oy = (1 - L.backout(q)) * 520 if q < 1 else 0
    bob = 4 * math.sin(2 * math.pi * t / 1.6)
    js = lerp(1.0, 0.8, m)
    ju = scaled(JU_ST, js)
    jx = lerp(540, 735, m) - ju.width / 2; jy = 1330 - 920 * js + oy + bob
    comp(im, ju, (jx + sx, jy + sy))
    if t >= 0.42:
        k = clamp((t - 0.42) / 0.14); s = lerp(1.9, 1.0, eo(k)) * js
        st = scaled(STAMP, s)
        cx, cy = jx + ju.width / 2 + 10, jy + 520 * js
        comp(im, st, (cx - st.width / 2 + sx, cy - st.height / 2 + sy), clamp(k * 2))
    if m > 0:
        ls = scaled(LEO_ST, 0.8)
        lx = lerp(-520, 330, eo(clamp((t - T2) / 0.45))) - ls.width / 2
        lb = -abs(math.sin(2 * math.pi * 1.8 * (t - T2))) * 14 if t - T2 < 0.5 else 3 * math.sin(2 * math.pi * t / 1.3)
        comp(im, ls, (lx, 1330 - 920 * 0.8 + lb))
        if t > T2 + 0.5:   # anger marks
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            cx, cy = lx + ls.width / 2 + 110, 1330 - 920 * 0.8 + 40
            pul = 1 + 0.12 * math.sin(2 * math.pi * t * 2.2)
            for a in (0, 90, 180, 270):
                ar = math.radians(a + 45); r1, r2 = 16 * pul, 44 * pul
                d.line((cx + r1 * math.cos(ar), cy + r1 * math.sin(ar), cx + r2 * math.cos(ar), cy + r2 * math.sin(ar)), fill=(226, 36, 48, 255), width=12)
            im.alpha_composite(lay)
    if t > 0.1:
        s = lerp(0.55, 1.0, L.backout((t - 0.1) / 0.4))
        pi = scaled(PILL_ESC, s); comp(im, pi, (540 - pi.width / 2, 340 - pi.height / 2), clamp((t - 0.1) * 6))
    return finish(im, 's1', t)

def frame_s2(t):
    im = L.apply_vig(L.rays(t, (190, 160, 236), (206, 180, 246)), VIG)
    q = t / 0.4; oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    bob = 5 * math.sin(2 * math.pi * t * 1.6)          # laughing bounce
    comp(im, JU_ST, (L.SP_X, L.SP_Y + oy + bob))
    bx, by = 540 - BOX_J.width / 2, L.SP_Y + 545 + oy + bob
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, x0 in enumerate((470, 540, 610)):
        ph = (t * 0.9 + i * 0.33) % 1.0; y0 = by - 10 - ph * 70
        a = int(230 * math.sin(math.pi * ph))
        pts = [(x0 + 14 * math.sin(yy / 24 + t * 5 + i), y0 - yy) for yy in range(0, 150, 6)]
        d.line(pts, fill=(255, 248, 230, a), width=10, joint='curve')
    im.alpha_composite(lay)
    comp(im, BOX_J, (bx, by))
    for i, (hx, hy, ph) in enumerate([(150, 560, 0.0), (790, 500, 0.5), (820, 760, 0.25)]):
        if t < 0.3 + i * 0.25: continue
        s = 1 + 0.08 * math.sin(2 * math.pi * (t * 2.4 + ph))
        hh = scaled(HAHA, s); comp(im, hh, (hx - hh.width / 2 + 60, hy - hh.height / 2), clamp((t - 0.3 - i * 0.25) * 5))
    T2 = p2_at('s2')
    if t >= T2:
        k = L.backout(clamp((t - T2) / 0.4)); v = scaled(VO, lerp(0.5, 1.0, k))
        comp(im, v, (540 - v.width / 2, 372 - v.height / 2), clamp((t - T2) * 5))
    return finish(im, 's2', t)

def frame_s3(t):
    im = L.S3_BG.copy()
    T2 = p2_at('s3')
    if t > 0.05:
        s = lerp(0.55, 1.0, L.backout((t - 0.05) / 0.4))
        pi = scaled(PILL_CLUE, s); comp(im, pi, (540 - pi.width / 2, 330 - pi.height / 2), clamp((t - 0.05) * 6))
    s = lerp(1.25, 1.0, eo(clamp((t - 0.15) / 0.35)))
    nt = scaled(NOTE_FULL, s); ang_y = 2 * math.sin(t * 1.4)
    comp(im, nt, (540 - nt.width / 2, 660 - nt.height / 2 + ang_y), eo(clamp((t - 0.15) / 0.25)))
    # pen (left) pops with the "caneta azul" words
    tp = max(0.9, T2 - 1.0)
    if t >= tp:
        k = L.backout(clamp((t - tp) / 0.4)); pn = scaled(PEN, lerp(0.4, 1.0, k))
        comp(im, pn, (250 - pn.width / 2, 1060 - pn.height / 2), clamp((t - tp) * 5))
        if t > tp + 0.4: rings(im, 250, 1060, t, (60, 110, 220), 70, 130)
        lb = rich_line([('caneta azul', (40, 70, 160))], F('InterDisplay-ExtraBold', 46), stroke=0)
        comp(im, lb, (250 - lb.width / 2, 1160), clamp((t - tp - 0.2) * 5))
    if t >= T2:
        k = L.backout(clamp((t - T2) / 0.4)); pc = scaled(PENCIL, lerp(0.4, 1.0, k))
        comp(im, pc, (830 - pc.width / 2, 1060 - pc.height / 2), clamp((t - T2) * 5))
        lb = rich_line([('lápis da Ju', (150, 100, 20))], F('InterDisplay-ExtraBold', 46), stroke=0)
        comp(im, lb, (830 - lb.width / 2, 1160), clamp((t - T2 - 0.2) * 5))
        if t >= T2 + 0.35:
            k2 = clamp((t - T2 - 0.35) / 0.25); ne = scaled(NEQ, lerp(1.8, 1.0, eo(k2)))
            comp(im, ne, (540 - ne.width / 2, 1060 - ne.height / 2), k2)
    return finish(im, 's3', t)

FEET = L.LEO_FEET
def frame_s4(t):
    im = DARK.copy()
    T2 = p2_at('s4'); dur = DURS['s4']
    p = clamp(t / (dur - 0.3))
    cx = lerp(170, 900, p)
    by = -abs(math.sin(2 * math.pi * 1.4 * t)) * 12
    sil = scaled(PED_SIL, 0.92)
    comp(im, sil, (cx - sil.width / 2, FEET - 884 * 0.92 + by))
    bx, byy = cx + 150, FEET - 884 * 0.92 + 610 * 0.92 + by
    comp(im, BOX_B, (bx - BOX_B.width / 2, byy - BOX_B.height / 2))
    if t >= T2:
        rings(im, int(bx), int(byy - 30), t, (120, 190, 255), 70, 170)
    # tiny "12:00" tag near the clock to anchor "ao meio-dia"
    for (qx, qy, ph) in [(300, 640, 0.0), (760, 560, 1.7)]:
        comp(im, QM, (qx - 55, qy - 80 + 10 * math.sin(2 * math.pi * t / 1.3 + ph)), clamp((t - 0.6) * 2) * 0.85)
    return finish(im, 's4', t)

def frame_s5(t):
    im = L.apply_vig(L.rays(t, (255, 200, 40), (255, 220, 110)), VIG)
    sx, sy = shake(t, 0.05, 20, 0.35)
    q = t / 0.45; oy = (1 - L.backout(q)) * 560 if q < 1 else 0
    bob = 4 * math.sin(2 * math.pi * t / 1.4)
    comp(im, PED_ST, (L.SP_X + sx, L.SP_Y + oy + bob + sy))
    bx, by = 540 + 160, L.SP_Y + 560 + oy + bob
    comp(im, BOX_B, (bx - BOX_B.width / 2 + sx, by - BOX_B.height / 2 + sy))
    if t > 0.5: rings(im, int(bx), int(by - 20), t, (255, 255, 255), 60, 150)
    T2 = p2_at('s5')
    if t >= T2 - 0.1:
        s = lerp(0.55, 1.0, L.backout((t - T2 + 0.1) / 0.4))
        pi = scaled(PILL_EST, s); comp(im, pi, (540 - pi.width / 2, 340 - pi.height / 2), clamp((t - T2 + 0.1) * 6))
    return finish(im, 's5', t)

def frame_s6(t):
    im = S6_BG(t)
    for (img, y, t0, side, phase) in [(CARD_A, 520, 0.5, -1, 0.0), (CARD_B, 750, 0.8, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45)
        x = (W - img.width) / 2 + side * (1 - p) * 160
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.6) / 1.5 + phase) if t > 2.6 else 1.0
        i2 = scaled(img, s)
        comp(im, i2, (x + img.width / 2 - i2.width / 2, y + img.height / 2 - i2.height / 2), p)
    if t >= 1.4:
        p = eo((t - 1.4) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1010 + (1 - p) * 24), p)
    if t >= 1.8:
        p = eo((t - 1.8) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1115 + (1 - p) * 18), p)
    if t >= 2.3:
        p = eo((t - 2.3) / 0.4); pul = 1 + 0.03 * math.sin(2 * math.pi * t / 1.2)
        fo = scaled(FOLLOW, pul); comp(im, fo, ((W - fo.width) / 2, 1190 + (1 - p) * 18), p)
    if t >= 0.3:
        p = L.backout((t - 0.3) / 0.5); bob = 6 * math.sin(2 * math.pi * t / 1.7)
        comp(im, EMPTY, (540 - EMPTY.width / 2, 1380 + (1 - p) * 300 + bob), clamp((t - 0.3) * 4))
    return finish(im, 's6', t)

_VIG6 = None
def S6_BG(t):
    global _VIG6
    if _VIG6 is None: _VIG6 = L.make_vig(0.4, cy=0.5)
    return L.apply_vig(L.rays(t, (22, 118, 122), (30, 134, 138), cy=1000, speed=5), _VIG6)

SCENES = [('s1', frame_s1), ('s2', frame_s2), ('s3', frame_s3), ('s4', frame_s4), ('s5', frame_s5), ('s6', frame_s6)]

# ------------------------------------------------------------------ audio
def build_audio(path):
    SR = LA.SR
    st, acc = {}, 0.0
    for k in ORDER:
        st[k] = acc; acc += round(DURS[k] * FPS) / FPS
    total = acc; n = int(total * SR)
    music = np.zeros(n)
    def put(sig, at, g=1.0, buf=None):
        b = music if buf is None else buf
        i = int(at * SR); j = min(len(b), i + len(sig))
        if i < len(b): b[i:j] += sig[:j - i] * g
    put(LA.groove(st['s4']), 0)
    put(LA.groove(st['s5'] - st['s4'], full=False), st['s4'])
    put(LA.groove(total - st['s5']), st['s5'])
    fx = np.zeros(n + 2 * SR)
    def add(sig, at, g=1.0):
        i = int(at * SR); fx[i:i + len(sig)] += sig * g
    add(LA.whoosh(), st['s1']); add(LA.thunk(), st['s1'] + 0.42, 1.3); add(LA.crash(), st['s1'] + 0.42, 0.6)
    T2 = p2_at('s1')
    for x in (0.0, 0.15, 0.3): add(LA.step(), st['s1'] + T2 + x)
    add(LA.whoosh(0.25, 0.25), st['s2'])
    for i in range(3): add(LA.blip(700 + 120 * i, 1100 + 120 * i, 0.09, 0.22), st['s2'] + 0.3 + i * 0.25)
    add(LA.ding(1567.98, 0.25), st['s2'] + p2_at('s2'))
    add(LA.whoosh(0.25, 0.25), st['s3']); add(LA.scribble(0.8), st['s3'] + 0.2)
    add(LA.ding(1318.5), st['s3'] + max(0.9, p2_at('s3') - 1.0)); add(LA.blip(500, 900, 0.1, 0.3), st['s3'] + p2_at('s3'))
    add(LA.thunk(), st['s3'] + p2_at('s3') + 0.35)
    for k in range(int((DURS['s4'] - 0.3) / 0.5)): add(LA.tick(), st['s4'] + 0.3 + k * 0.5)
    add(LA.ding(1174.7), st['s4'] + p2_at('s4'))
    add(LA.slide_whistle(), st['s5'] - 0.05); add(LA.crash(), st['s5'] + 0.05); add(LA.thunk(), st['s5'] + 0.05, 1.2)
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
    pcm = (np.stack([mixm, mixm], 1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
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
        shots = [('s1', 0.9), ('s1', p2_at('s1') + 0.9), ('s2', p2_at('s2') + 0.6), ('s3', p2_at('s3') + 0.8),
                 ('s4', p2_at('s4') + 0.5), ('s5', p2_at('s5') + 0.5), ('s6', 3.5), ('s6', 0.2)]
        thumbs = []
        for k, tt in shots:
            thumbs.append(fns[k](tt).resize((W // 3, H // 3), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 3 * 4, H // 3 * 2))
        for i, th in enumerate(thumbs): sheet.paste(th, ((i % 4) * (W // 3), (i // 4) * (H // 3)))
        sheet.save(WORK + '/sheet.png'); print('sheet', DURS, round(sum(DURS.values()), 2))
    elif mode == 'render':
        only = sys.argv[2:] or ORDER
        for idx, (k, fn) in enumerate(SCENES):
            if k in only: L.encode(k, fn, DURS[k], fade_in=0, fade_out=12 if idx == len(SCENES) - 1 else 0)
        if all(os.path.exists(f'{WORK}/{k}.mp4') for k in ORDER):
            assemble(WORK + '/a-marmita-sumiu-ep2.mp4')
    elif mode == 'audio':
        assemble(WORK + '/a-marmita-sumiu-ep2.mp4')
