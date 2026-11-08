#!/usr/bin/env python3
"""O Pix Errado — Episódio 1.  python3 ep1.py preview | render [scenes] | audio   (timing.json from nar.py, or synthetic)"""
import os, sys, math, json, time, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch'); sys.path.insert(0, '/home/claude/marmita2')
import make as M
import lunch as L
import laudio as LA
import ep2 as E2
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, rich_line, WHITE, INK

W, H, S, FPS = 1080, 1920, 2, 30
WORK = '/home/claude/pix1'
L.WORK = WORK
A_COL, B_COL = L.A_COL, L.B_COL
GREEN = (90, 226, 140); RED_T = (255, 110, 110)
mix, sc = L.mix, E2.scaled

PAGES = {
    's1': [[('23h59.', WHITE)], [('Caiu um Pix de', WHITE), ('R$ 2.000', GREEN), ('na conta do Caio!', WHITE)]],
    's2': [[('Ele nem conhece', WHITE)], [('quem mandou.', A_COL)]],
    's3': [[('Um minuto depois, uma mensagem:', WHITE)], [('“Pelo amor de Deus, devolve! Foi engano!”', RED_T)]],
    's4': [[('Mas o Caio já ouviu falar', WHITE)], [('de golpe do Pix…', A_COL)]],
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
def caio(phone=True):
    im = Image.new('RGBA', (L.CW * S, L.CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx, hy, r = 300, 240, 105
    skin, pj, pj_d, hair, ink = (196, 134, 96), (92, 132, 222), (66, 102, 190), (24, 20, 22), (28, 24, 30)
    dark = mix(skin, (60, 30, 20), 0.25); tw = 250
    d.rounded_rectangle(P(hx - 76, 660, hx - 10, 856), radius=22 * S, fill=pj)
    d.rounded_rectangle(P(hx + 10, 660, hx + 76, 856), radius=22 * S, fill=pj)
    for x0 in (hx - 78, hx + 8): d.line(P(x0 + 34, 690, x0 + 34, 850), fill=pj_d, width=4 * S)
    d.rounded_rectangle(P(hx - 104, 846, hx - 4, 886), radius=18 * S, fill=(236, 120, 140))
    d.rounded_rectangle(P(hx + 4, 846, hx + 104, 886), radius=18 * S, fill=(236, 120, 140))
    d.rounded_rectangle(P(hx - tw / 2, 360, hx + tw / 2, 700), radius=74 * S, fill=pj)
    d.polygon(P(hx - 46, 362, hx, 430, hx + 46, 362), fill=(255, 255, 255))
    d.polygon(P(hx - 40, 362, hx, 420, hx + 40, 362), fill=skin)
    for y in (460, 530, 600): d.ellipse(P(hx - 9, y - 9, hx + 9, y + 9), fill=(255, 255, 255))
    d.rounded_rectangle(P(hx + 50, 470, hx + 104, 530), radius=8 * S, fill=pj_d)
    for sx in (-1, 1):
        xo = hx + sx * (tw / 2 + 22)
        d.rounded_rectangle(P(xo - 28, 380, xo + 28, 610), radius=26 * S, fill=pj)
    d.ellipse(P(hx - tw / 2 - 52, 590, hx - tw / 2 + 8, 650), fill=skin)
    if phone:
        d.rounded_rectangle(P(hx + 70, 470, hx + 170, 640), radius=16 * S, fill=(30, 30, 38))
        d.rounded_rectangle(P(hx + 78, 482, hx + 162, 628), radius=10 * S, fill=(150, 240, 190))
        d.text(P(hx + 120, 540), 'R$', font=F('InterDisplay-Black', 26 * S), fill=(20, 110, 60), anchor='mm')
        d.text(P(hx + 120, 574), '2.000', font=F('InterDisplay-Black', 22 * S), fill=(20, 110, 60), anchor='mm')
        d.ellipse(P(hx + 120 - 34, 600, hx + 120 + 30, 660), fill=skin)
    else:
        d.ellipse(P(hx + tw / 2 - 8, 590, hx + tw / 2 + 52, 650), fill=skin)
    d.rectangle(P(hx - 24, 318, hx + 24, 372), fill=dark)
    for sx in (-1, 1): d.ellipse(P(hx + sx * r - 22, hy - 10, hx + sx * r + 22, hy + 40), fill=skin)
    d.ellipse(P(hx - r, hy - r, hx + r, hy + r + 6), fill=skin)
    d.pieslice(P(hx - r - 6, hy - r - 14, hx + r + 6, hy + r - 30), 180, 360, fill=hair)
    d.polygon(P(hx - r - 2, hy - 40, hx - 60, hy - 96, hx + 10, hy - 30, hx + 40, hy - 90, hx + 90, hy - 36, hx + r + 4, hy - 40,
                hx + r + 6, hy - 60, hx - r - 6, hy - 60), fill=hair)
    for (x0, y0, x1, y1) in [(-80, -40, -40, 6), (-30, -44, 4, 10), (20, -46, 52, 4), (64, -40, 94, -4)]:
        d.polygon(P(hx + x0, hy + y0, hx + x1, hy + y0, hx + (x0 + x1) / 2 + 6, hy + y1), fill=hair)
    for a0 in (200, 225, 250, 290, 315):
        d.arc(P(hx - r + 10, hy - r - 2, hx + r - 10, hy + r - 40), a0, a0 + 14, fill=(78, 70, 76), width=6 * S)
    for sx in (-1, 1):
        d.rounded_rectangle(P(hx + sx * (r - 6) - 16, hy - 50, hx + sx * (r - 6) + 16, hy + 6), radius=12 * S, fill=hair)
    ey = hy + 16
    for sx in (-1, 1):
        ex = hx + sx * 40
        d.ellipse(P(ex - 25, ey - 30, ex + 25, ey + 30), fill=(255, 255, 255))
        d.ellipse(P(ex - 9, ey - 9, ex + 9, ey + 9), fill=ink)
        d.ellipse(P(ex - 4, ey - 6, ex + 1, ey - 1), fill=(255, 255, 255))
        d.arc(P(ex - 28, ey - 74, ex + 28, ey - 42), 200, 340, fill=hair, width=8 * S)
    d.ellipse(P(hx - 12, hy + 46, hx + 12, hy + 64), fill=dark)
    d.ellipse(P(hx - 20, hy + 74, hx + 20, hy + 112), fill=(110, 32, 44))
    blush = mix(skin, (255, 110, 130), 0.35)
    d.ellipse(P(hx - 88, hy + 50, hx - 54, hy + 70), fill=blush); d.ellipse(P(hx + 54, hy + 50, hx + 88, hy + 70), fill=blush)
    return down(im)

def phone_screen(time_str, date_str):
    w, h = W * S, H * S
    body = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    for b in [(183, 600, 193, 680), (183, 700, 193, 780), (887, 640, 897, 790)]:
        d.rounded_rectangle(P(*b), radius=3 * S, fill=(44, 44, 52))
    d.rounded_rectangle(P(*M.PH), radius=92 * S, fill=(24, 24, 30), outline=(84, 84, 98), width=3 * S)
    sw, sh = (M.SCR[2] - M.SCR[0]) * S, (M.SCR[3] - M.SCR[1]) * S
    wall = vgrad(sw, sh, (20, 70, 80), (6, 14, 24), 0, int(sh * 0.7))
    wall = glow(wall, lambda dd: dd.ellipse((-200 * S, 500 * S, 400 * S, 1200 * S), fill=200), (20, 120, 110), 120 * S)
    wmask = Image.new('L', (sw, sh), 0); ImageDraw.Draw(wmask).rounded_rectangle((0, 0, sw - 1, sh + 200 * S), radius=72 * S, fill=255)
    body.paste(wall, tuple(P(M.SCR[0], M.SCR[1])), wmask)
    dn = ImageDraw.Draw(body)
    dn.text(P(540, 452), date_str, font=F('Inter-Medium', 34 * S), fill=(226, 236, 238), anchor='mt')
    dn.text(P(540, 486), time_str, font=F('InterDisplay-SemiBold', 200 * S), fill=(240, 248, 248), anchor='mt')
    dn.rounded_rectangle(P(466, 372, 614, 414), radius=21 * S, fill=(0, 0, 0))
    return down(body)

def pix_card(w=M.NW):
    hh = 250
    im = Image.new('RGBA', (w * S, hh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, hh * S - 1), radius=40 * S, fill=(64, 64, 86, 236))
    d.rounded_rectangle(P(24, 24, 92, 92), radius=16 * S, fill=(30, 190, 170))
    d.polygon(P(58, 34, 82, 58, 58, 82, 34, 58), outline=(255, 255, 255), width=6 * S)
    d.text(P(112, 26), 'Banco Pila', font=F('Inter-SemiBold', 33 * S), fill=(242, 242, 248))
    d.text(P(w - 26, 30), 'agora', font=F('Inter-Regular', 28 * S), fill=(176, 178, 196), anchor='ra')
    d.text(P(112, 70), 'Pix recebido', font=F('Inter-Regular', 40 * S), fill=(238, 238, 246))
    d.text(P(112, 124), 'R$ 2.000,00', font=F('InterDisplay-Black', 76 * S), fill=GREEN)
    return down(im), hh

def receipt():
    w, h = 640, 600
    im = Image.new('RGBA', (w + 40, h + 50), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((20, 34, 20 + w, 34 + h), radius=36, fill=150)
    im.paste((30, 10, 30, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=36, fill=(255, 255, 255))
    d.rounded_rectangle((20, 20, 20 + w, 130), radius=36, fill=(30, 190, 170)); d.rectangle((20, 90, 20 + w, 130), fill=(30, 190, 170))
    d.text((20 + w / 2, 75), 'COMPROVANTE PIX', font=F('InterDisplay-Black', 46), fill=WHITE, anchor='mm')
    rows = [('Valor', 'R$ 2.000,00'), ('De', 'L***** M** S****'), ('Para', 'Caio R. Lima'), ('Data', '23:59')]
    for i, (a, b) in enumerate(rows):
        y = 190 + i * 100
        d.text((70, y), a, font=F('Inter-Medium', 34), fill=(120, 120, 136), anchor='lm')
        d.text((w - 30, y), b, font=F('InterDisplay-ExtraBold', 44), fill=(30, 30, 40) if i != 1 else (200, 40, 60), anchor='rm')
        if i < 3: d.line((70, y + 50, w - 30, y + 50), fill=(232, 232, 240), width=2)
    return im

def chat_panel(lines_visible, t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1 = M.SCR[0], M.SCR[1], M.SCR[2]
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle(M.SCR, radius=72, fill=255)
    d.rectangle((x0, y0, x1, H), fill=(16, 18, 24, 255))
    d.rectangle((x0, y0, x1, y0 + 200), fill=(30, 32, 40, 255))
    d.ellipse((x0 + 40, y0 + 90, x0 + 130, y0 + 180), fill=(90, 92, 104))
    d.ellipse((x0 + 68, y0 + 104, x0 + 102, y0 + 138), fill=(150, 152, 164)); d.chord((x0 + 52, y0 + 136, x0 + 118, y0 + 196), 180, 360, fill=(150, 152, 164))
    d.text((x0 + 150, y0 + 112), 'Número desconhecido', font=F('Inter-SemiBold', 40), fill=WHITE)
    d.text((x0 + 150, y0 + 158), 'online', font=F('Inter-Regular', 30), fill=GREEN)
    msgs = ['PELO AMOR DE DEUS', 'DEVOLVE', 'FOI ENGANO!!']
    y = y0 + 280
    for i, (txt, tv) in enumerate(zip(msgs, lines_visible)):
        if tv <= 0: continue
        f = F('InterDisplay-ExtraBold', 48); tw = f.getlength(txt)
        s = lerp(0.6, 1.0, L.backout(clamp(tv / 0.3)))
        bw, bh = int((tw + 70) * s), int(110 * s)
        d.rounded_rectangle((x0 + 40, y, x0 + 40 + bw, y + bh), radius=int(34 * s), fill=(52, 54, 66, 255))
        if s > 0.9: d.text((x0 + 75, y + bh / 2), txt, font=f, fill=WHITE, anchor='lm')
        y += 140
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.paste(lay, (0, 0), ImageChops.multiply(lay.getchannel('A'), m))
    return out

def thought(text='GOLPE?'):
    w, h = 560, 360
    im = Image.new('RGBA', (w, h + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for b in [(20, 20, w - 20, h - 40), (60, 0, 300, 160), (260, 10, 520, 170), (30, 160, 220, h), (300, 170, 540, h - 10)]:
        d.ellipse(b, fill=(255, 255, 255), outline=(28, 22, 30), width=6)
    d.ellipse((30, 30, w - 30, h - 50), fill=(255, 255, 255))
    for (cx, cy, r) in [(110, h + 30, 30), (70, h + 90, 18)]:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(28, 22, 30), width=6)
    tx, ty = 150, h / 2 - 10
    d.polygon([(tx - 60, ty + 50), (tx + 60, ty + 50), (tx, ty - 56)], fill=(250, 190, 40), outline=(28, 22, 30))
    d.text((tx, ty + 12), '!', font=F('InterDisplay-Black', 70), fill=(28, 22, 30), anchor='mm')
    d.text((tx + 80, ty), text, font=F('InterDisplay-Black', 68), fill=(214, 40, 50), anchor='lm')
    return im

def icon_return(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.arc((22 * u, 26 * u, 78 * u, 82 * u), 200, 520 - 180 + 160, fill=(30, 170, 120), width=int(10 * u))
    d.polygon([(14 * u, 40 * u), (36 * u, 30 * u), (34 * u, 56 * u)], fill=(30, 170, 120))
    d.text((50 * u, 56 * u), 'R$', font=F('InterDisplay-Black', int(22 * u)), fill=(30, 130, 90), anchor='mm')
    return im.resize((sz, sz), Image.LANCZOS)

def icon_eye(sz=140):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.ellipse((24 * u, 24 * u, 66 * u, 66 * u), outline=(40, 44, 60), width=int(9 * u))
    d.line((60 * u, 60 * u, 84 * u, 84 * u), fill=(40, 44, 60), width=int(11 * u))
    d.text((45 * u, 45 * u), '?', font=F('InterDisplay-Black', int(30 * u)), fill=(214, 40, 50), anchor='mm')
    return im.resize((sz, sz), Image.LANCZOS)

# ------------------------------------------------------------------ setup
def setup():
    global KICKER, CAIO, CAIO_ST, PHONE, PIX, PIX_H, MSG, MSG_H, ROOM, REC, VIG, THINK, CARD_A, CARD_B, CTA, SUB, FOLLOW, HOW, BILL, QM
    KICKER = L.build_kicker('O PIX ERRADO  ·  EP. 1')
    CAIO = caio(True); CAIO_ST = L.sticker(CAIO)
    PHONE = phone_screen('23:59', 'segunda-feira, 9 de novembro')
    PIX, PIX_H = pix_card()
    MSG, MSG_H = M.notif_card('PELO AMOR DE DEUS DEVOLVE')
    ROOM = glow(vgrad(W, H, (16, 18, 34), (4, 5, 10)), lambda d: d.rectangle(M.PH, fill=255), (30, 110, 110), 90).convert('RGBA')
    REC = receipt(); VIG = L.make_vig(0.32, cy=0.45)
    THINK = thought()
    CARD_A = M.card('A', 'TIME DEVOLVE', A_COL, (30, 20, 8), A_COL, (30, 20, 8))
    CARD_B = M.card('B', 'TIME DESCONFIA', B_COL, (64, 10, 14), (255, 228, 228), WHITE)
    for c, ic in ((CARD_A, icon_return()), (CARD_B, icon_eye())):
        c.alpha_composite(E2.badge(ic, 140), (30 + 900 - 22 - 140, 30 + 20))
    HOW = [rich_line([('A', A_COL), (': devolver agora pelo app', WHITE)], F('Inter-SemiBold', 40), stroke=4),
           rich_line([('B', B_COL), (': não mexer até falar com o banco', WHITE)], F('Inter-SemiBold', 40), stroke=4)]
    CTA = rich_line([('Comenta ', WHITE), ('A', A_COL), (' ou ', WHITE), ('B', B_COL)], F('InterDisplay-ExtraBold', 76))
    SUB = rich_line([('O mais votado vira o episódio 2', (232, 244, 244))], F('Inter-SemiBold', 38), stroke=4)
    FOLLOW = rich_line([('Segue pra não perder o ', WHITE), ('ep. 2', A_COL)], F('InterDisplay-ExtraBold', 46), stroke=5)
    BILL = Image.new('RGBA', (300, 150), (0, 0, 0, 0)); db = ImageDraw.Draw(BILL)
    db.rounded_rectangle((4, 4, 296, 146), radius=18, fill=(120, 200, 140), outline=(28, 22, 30), width=6)
    db.ellipse((110, 35, 190, 115), outline=(40, 120, 70), width=6)
    db.text((150, 76), 'R$', font=F('InterDisplay-Black', 40), fill=(40, 120, 70), anchor='mm')
    f = F('InterDisplay-Black', 120)
    QM = Image.new('RGBA', (110, 160), (0, 0, 0, 0))
    ImageDraw.Draw(QM).text((55, 80), '?', font=f, fill=WHITE, anchor='mm', stroke_width=7, stroke_fill=INK)
    build_caps()

def build_caps():
    global CAP
    CAP = {}
    tops = {'s1': 1560, 's2': 1350, 's3': 1560, 's4': 1350}
    for k in ORDER[:-1]:
        pages = TJ['pages'][k]; gap = TJ['gaps'].get(k, 0.1); cps = []
        for i, (st, segs) in enumerate(pages):
            end = pages[i + 1][0] - 0.05 if i + 1 < len(pages) else DURS[k] + 1
            ss, acc = [], st
            for text, col in segs:
                ss.append((acc, text, tuple(col))); acc += gap * len(text.split())
            cps.append((st, end, ss))
        CAP[k] = Caption(cps, font=('InterDisplay-ExtraBold', 74), top=tops[k], maxw=940, gap=gap)
    CAP['s5'] = Caption([(0.1, DURS['s5'] + 5, [(0.15, 'E AGORA?', WHITE)])], font=('InterDisplay-Black', 104), top=330, maxw=980, gap=0.12)

def finish(im, k, t):
    comp(im, KICKER, ((W - KICKER.width) // 2, 196)); CAP[k].draw(im, t); return im.convert('RGB')

def buzz_dx(t, t0): return int(round(7 * math.sin(2 * math.pi * 32 * t))) if (t0 <= t < t0 + 0.3 or t0 + 0.45 <= t < t0 + 0.75) else 0

# ------------------------------------------------------------------ scenes
def frame_s1(t):
    im = ROOM.copy()
    tm = 0.95
    dx = buzz_dx(t, 0.0) or buzz_dx(t, tm)
    im.alpha_composite(PHONE, (dx, 0))
    k1 = clamp(t / 0.25); s = lerp(1.25, 1.0, eo(k1))
    pc = sc(PIX, s)
    yp = M.NY + (MSG_H + 18) * eo(clamp((t - tm) / 0.35))
    comp(im, pc, (M.NX + dx - (pc.width - PIX.width) / 2, yp - (pc.height - PIX.height) / 2), k1)
    if t >= tm:
        p = eo(clamp((t - tm) / 0.35)); comp(im, MSG, (M.NX + dx, M.NY - (1 - p) * 60), p)
    return finish(im, 's1', t)

def frame_s2(t):
    im = L.apply_vig(L.rays(t, (70, 60, 150), (86, 74, 170)), VIG)
    q = t / 0.4; oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    bob = 4 * math.sin(2 * math.pi * t / 1.4)
    comp(im, CAIO_ST, (L.SP_X - 120, L.SP_Y + oy + bob))
    T2 = p2_at('s2')
    if t >= T2 - 0.2:
        k = L.backout(clamp((t - T2 + 0.2) / 0.45)); r = sc(REC, lerp(0.5, 0.72, k))
        r = r.rotate(5, resample=Image.BICUBIC, expand=True)
        comp(im, r, (770 - r.width / 2, 1000 - r.height / 2), clamp((t - T2 + 0.2) * 5))
        if t > T2 + 0.4:
            for (qx, qy, ph) in [(980, 720, 0.0), (640, 700, 0.8)]:
                comp(im, QM, (qx - 55, qy - 80 + 10 * math.sin(2 * math.pi * t / 1.3 + ph)), clamp((t - T2 - 0.4) * 3))
    return finish(im, 's2', t)

def frame_s3(t):
    im = ROOM.copy()
    T2 = p2_at('s3')
    dx = buzz_dx(t, 0.05)
    im.alpha_composite(PHONE, (dx, 0))
    if t < 0.9:
        p = eo(clamp(t / 0.35)); comp(im, MSG, (M.NX + dx, M.NY - (1 - p) * 60), p)
        comp(im, PIX, (M.NX + dx, M.NY + MSG_H + 18))
    else:
        tv = [t - (T2 - 0.1), t - (T2 + 0.55), t - (T2 + 1.2)]
        pan = chat_panel(tv, t); op = clamp((t - 0.9) / 0.25)
        pan.putalpha(pan.getchannel('A').point(lambda v: int(v * op)))
        im.alpha_composite(pan, (dx, 0))
    return finish(im, 's3', t)

def frame_s4(t):
    im = L.apply_vig(L.rays(t, (220, 60, 70), (236, 84, 92)), VIG)
    q = t / 0.4; oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    sh = 5 * math.sin(2 * math.pi * 9 * t) if t > p2_at('s4') else 0
    comp(im, CAIO_ST, (L.SP_X - 60 + sh, L.SP_Y + 80 + oy))
    T2 = p2_at('s4')
    if t >= 0.5:
        k = L.backout(clamp((t - 0.5) / 0.45)); th = sc(THINK, lerp(0.5, 1.0, k))
        comp(im, th, (720 - th.width / 2, 470 - th.height / 2 + 6 * math.sin(t * 2)), clamp((t - 0.5) * 5))
    return finish(im, 's4', t)

def frame_s5(t):
    im = E2.S6_BG(t)
    for (img, y, t0, side, phase) in [(CARD_A, 500, 0.5, -1, 0.0), (CARD_B, 730, 0.8, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45); x = (W - img.width) / 2 + side * (1 - p) * 160
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.6) / 1.5 + phase) if t > 2.6 else 1.0
        i2 = sc(img, s); comp(im, i2, (x + img.width / 2 - i2.width / 2, y + img.height / 2 - i2.height / 2), p)
    for i, hw in enumerate(HOW):
        t0 = 1.2 + 0.3 * i
        if t >= t0: p = eo((t - t0) / 0.4); comp(im, hw, ((W - hw.width) / 2, 990 + i * 62 + (1 - p) * 16), p)
    if t >= 2.0: p = eo((t - 2.0) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1150 + (1 - p) * 24), p)
    if t >= 2.4: p = eo((t - 2.4) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1255 + (1 - p) * 18), p)
    if t >= 2.8:
        p = eo((t - 2.8) / 0.4); pul = 1 + 0.03 * math.sin(2 * math.pi * t / 1.2)
        fo = sc(FOLLOW, pul); comp(im, fo, ((W - fo.width) / 2, 1325 + (1 - p) * 18), p)
    if t >= 0.3:
        p = L.backout((t - 0.3) / 0.5); bob = 6 * math.sin(2 * math.pi * t / 1.7)
        bl = BILL.rotate(8 * math.sin(t * 1.5), resample=Image.BICUBIC, expand=True)
        comp(im, bl, (540 - bl.width / 2, 1480 + (1 - p) * 300 + bob), clamp((t - 0.3) * 4))
    return finish(im, 's5', t)

SCENES = [('s1', frame_s1), ('s2', frame_s2), ('s3', frame_s3), ('s4', frame_s4), ('s5', frame_s5)]

# ------------------------------------------------------------------ audio
def build_audio(path):
    SR = LA.SR; rng = np.random.default_rng(5)
    st, acc = {}, 0.0
    for k in ORDER: st[k] = acc; acc += round(DURS[k] * FPS) / FPS
    total = acc; n = int(total * SR)
    music = np.zeros(n)
    def put(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if i < n: music[i:j] += sig[:j - i]
    put(LA.groove(st['s3']), 0); put(LA.groove(st['s5'] - st['s3'], full=False), st['s3']); put(LA.groove(total - st['s5']), st['s5'])
    fx = np.zeros(n + 3 * SR)
    def add(sig, at, g=1.0):
        i = int(at * SR); fx[i:i + len(sig)] += sig * g
    def tt(d): return np.arange(int(d * SR)) / SR
    def buzz(d=0.3):
        q = tt(d); return np.tanh(2.5 * np.sin(2 * np.pi * 172 * q)) * np.minimum(1, q / 0.01) * np.minimum(1, (d - q) / 0.03) * 0.3
    def coins():
        out = np.zeros(int(0.6 * SR))
        for k in range(6):
            q = tt(0.12); f = 2600 + 400 * rng.random()
            s = np.sin(2 * np.pi * f * q) * np.exp(-q / 0.03) * 0.18; i = int((0.05 + k * 0.07) * SR); out[i:i + len(s)] += s
        return out
    add(LA.ding(1318.5, 0.35), st['s1']); add(LA.ding(1760.0, 0.3), st['s1'] + 0.09); add(coins(), st['s1'] + 0.1)
    add(buzz(), st['s1']); add(buzz(), st['s1'] + 0.45); add(buzz(), st['s1'] + 0.95); add(buzz(), st['s1'] + 1.4)
    add(LA.whoosh(), st['s2']); add(LA.blip(500, 900, 0.1, 0.3), st['s2'] + p2_at('s2') - 0.2)
    add(buzz(), st['s3'] + 0.05); add(buzz(), st['s3'] + 0.5)
    for k, dt in enumerate((-0.1, 0.55, 1.2)): add(LA.blip(800 + 150 * k, 1200 + 150 * k, 0.08, 0.3), st['s3'] + p2_at('s3') + dt)
    add(LA.thunk(), st['s4'] + 0.05); add(LA.crash(), st['s4'] + 0.05, 0.5); add(LA.ding(880, 0.2), st['s4'] + p2_at('s4'))
    add(LA.tada(), st['s5']); add(LA.blip(400, 800, 0.1, 0.3), st['s5'] + 0.5); add(LA.blip(450, 900, 0.1, 0.3), st['s5'] + 0.8)
    add(LA.blip(500, 1000, 0.1, 0.3), st['s5'] + 2.0)
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
        shots = [('s1', 0.3), ('s1', 1.6), ('s2', p2_at('s2') + 0.8), ('s3', p2_at('s3') + 1.8),
                 ('s4', p2_at('s4') + 0.5), ('s5', 3.5), ('s3', 0.4), ('s2', 0.6)]
        sheet = Image.new('RGB', (W // 3 * 4, H // 3 * 2))
        for i, (k, tt) in enumerate(shots):
            sheet.paste(fns[k](tt).resize((W // 3, H // 3), Image.LANCZOS), ((i % 4) * (W // 3), (i // 4) * (H // 3)))
        sheet.save(WORK + '/sheet.png'); print('sheet', DURS, round(sum(DURS.values()), 2))
    elif mode == 'render':
        only = sys.argv[2:] or ORDER
        for idx, (k, fn) in enumerate(SCENES):
            if k in only: L.encode(k, fn, DURS[k], fade_in=0, fade_out=12 if idx == len(SCENES) - 1 else 0)
        if all(os.path.exists(f'{WORK}/{k}.mp4') for k in ORDER): assemble(WORK + '/o-pix-errado-ep1.mp4')
    elif mode == 'audio':
        assemble(WORK + '/o-pix-errado-ep1.mp4')
