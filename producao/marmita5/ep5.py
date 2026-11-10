#!/usr/bin/env python3
"""A Marmita Sumiu — Episódio 5 (FINAL). A última votação deu B: foi alguém de fora (a vó do Léo).
python3 ep5.py preview | render [cenas] | audio      (timing.json vem do nar5.py; sem ele usa tempos sintéticos)"""
import os, sys, math, json, time, subprocess, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/lunch'); sys.path.insert(0, '/home/claude/marmita2')
sys.path.insert(0, '/home/claude/marmita3'); sys.path.insert(0, '/home/claude/marmita4')
import make as M
import lunch as L
import laudio as LA
import ep2 as E2
import ep3 as M3
import ep4 as M4
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, down, Caption, rich_line, WHITE, INK

W, H, S, FPS = 1080, 1920, 2, 30
WORK = '/home/claude/marmita5'
L.WORK = WORK
A_COL, B_COL, YEL = L.A_COL, L.B_COL, L.YEL
BLUE_T, RED_T, PINK = E2.BLUE_T, (255, 110, 100), (255, 150, 190)
mix, sc = L.mix, E2.scaled

PAGES = {
    's1': [[('Quem comeu a lasanha do Léo?', WHITE)], [('Hoje, a', WHITE), ('resposta.', YEL)]],
    's2': [[('Vocês votaram:', WHITE), ('foi alguém de fora.', B_COL)],
           [('Na câmera: alguém baixinho, molhado de chuva, ganha o', WHITE), ('moletom', YEL), ('do Seu Zé.', WHITE)]],
    's3': [[('No livro de visitas, com a', WHITE), ('caneta azul…', BLUE_T)],
           [('assinou: Dona Cida,', WHITE), ('a vó do Léo!', PINK)]],
    's4': [[('Ela veio fazer surpresa, mas não achou o neto…', WHITE)],
           [('provou só um pedacinho.', WHITE), ('Tava uma delícia!', YEL)]],
    's5': [[('No dia seguinte, voltou… e provou a lasanha com', WHITE), ('pimenta!', RED_T)],
           [('E o Seu Zé?', WHITE), ('Sabia de tudo.', BLUE_T)]],
    's6': [[('Hoje, ela deixou uma lasanha nova, sem pimenta:', WHITE)],
           [('“Desculpa, netinho.', PINK), ('Tava uma delícia mesmo.”', YEL)]],
}
ORDER = ['s1', 's2', 's3', 's4', 's5', 's6']
TIMING = WORK + '/timing.json'
END_HOLD = 3.4


def synth_timing():
    out = {'durs': {}, 'pages': {}, 'gaps': {}, 'nar': []}
    for k in ORDER:
        t, pages = 0.3, []
        for segs in PAGES[k]:
            txt = ' '.join(s for s, _ in segs)
            pages.append([round(t, 3), [[s, list(c)] for s, c in segs]]); t += 0.5 + 0.06 * len(txt)
        out['pages'][k] = pages; out['durs'][k] = round(t + 0.3, 3); out['gaps'][k] = 0.12
    out['durs']['s6'] += END_HOLD
    return out


TJ = json.load(open(TIMING)) if os.path.exists(TIMING) else synth_timing()
DURS = {k: TJ['durs'][k] for k in ORDER}
def p2_at(k): return TJ['pages'][k][1][0]
END_T = DURS['s6'] - END_HOLD


# ------------------------------------------------------------------ arte
def vo(mouth='smile'):
    """Dona Cida, a vó do Léo: baixinha, coque grisalho, óculos redondos, vestido florido e casaquinho."""
    im = Image.new('RGBA', (L.CW * S, L.CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx, hy, r = 300, 300, 100
    skin, ink = (146, 96, 66), (28, 24, 30)
    dark = mix(skin, (60, 30, 20), 0.25)
    dress, dress_d = (178, 82, 140), (150, 64, 118)
    card, card_d = (238, 222, 188), (214, 196, 160)
    grey, grey_d = (222, 222, 230), (184, 184, 196)
    for sx in (-1, 1):
        d.rounded_rectangle(P(hx + sx * 40 - 26, 740, hx + sx * 40 + 26, 860), radius=16 * S, fill=(196, 150, 124))
        d.ellipse(P(hx + sx * 40 - 46, 838, hx + sx * 40 + 40, 884), fill=(140, 40, 50))
    d.rounded_rectangle(P(hx - 150, 420, hx + 150, 780), radius=80 * S, fill=dress)
    rng = random.Random(4)
    for _ in range(26):
        x, y = rng.uniform(hx - 120, hx + 120), rng.uniform(460, 760)
        for a in range(5):
            ang = a * 2 * math.pi / 5
            d.ellipse(P(x + 9 * math.cos(ang) - 6, y + 9 * math.sin(ang) - 6, x + 9 * math.cos(ang) + 6, y + 9 * math.sin(ang) + 6),
                      fill=(255, 236, 244))
        d.ellipse(P(x - 4, y - 4, x + 4, y + 4), fill=(255, 210, 90))
    for sx in (-1, 1):
        xa, xb = (hx - 152, hx - 52) if sx < 0 else (hx + 52, hx + 152)
        d.rounded_rectangle(P(xa, 420, xb, 690), radius=40 * S, fill=card)
        d.line(P(hx + sx * 54, 440, hx + sx * 54, 680), fill=card_d, width=6 * S)
        for y in (480, 540, 600):
            d.ellipse(P(hx + sx * 64 - 7, y - 7, hx + sx * 64 + 7, y + 7), fill=card_d) if sx < 0 else None
        xo = hx + sx * 168
        d.rounded_rectangle(P(xo - 30, 430, xo + 30, 640), radius=28 * S, fill=card)
        d.ellipse(P(xo - 28, 622, xo + 28, 676), fill=skin)
    d.rounded_rectangle(P(hx - 214, 560, hx - 150, 640), radius=12 * S, fill=(120, 70, 44))
    d.arc(P(hx - 206, 520, hx - 158, 590), 180, 360, fill=(90, 50, 30), width=6 * S)
    d.rectangle(P(hx - 24, 380, hx + 24, 430), fill=dark)
    for sx in (-1, 1):
        d.ellipse(P(hx + sx * r - 20, hy - 6, hx + sx * r + 20, hy + 38), fill=skin)
        d.ellipse(P(hx + sx * r - 6, hy + 34, hx + sx * r + 6, hy + 46), fill=(250, 200, 60))
    d.ellipse(P(hx - r, hy - r, hx + r, hy + r + 6), fill=skin)
    d.ellipse(P(hx - 58, hy - 212, hx + 58, hy - 100), fill=grey)
    d.arc(P(hx - 40, hy - 196, hx + 40, hy - 120), 200, 340, fill=grey_d, width=6 * S)
    d.chord(P(hx - r - 10, hy - r - 14, hx + r + 10, hy + 60), 180, 360, fill=grey)
    for sx in (-1, 1):
        d.ellipse(P(hx + sx * (r - 6) - 30, hy - 50, hx + sx * (r - 6) + 30, hy + 20), fill=grey)
    d.arc(P(hx - 70, hy - 96, hx + 10, hy - 40), 190, 300, fill=grey_d, width=6 * S)
    ey = hy + 16
    for sx in (-1, 1):
        ex = hx + sx * 40
        d.ellipse(P(ex - 15, ey - 16, ex + 15, ey + 16), fill=(255, 255, 255))
        d.ellipse(P(ex - 7, ey - 8, ex + 9, ey + 8), fill=ink)
        d.ellipse(P(ex - 2, ey - 5, ex + 3, ey), fill=(255, 255, 255))
        d.ellipse(P(ex - 32, ey - 30, ex + 32, ey + 30), outline=(110, 70, 50), width=6 * S)
        d.ellipse(P(ex - 26 + sx * 16, ey + 34, ex + 26 + sx * 16, ey + 54), fill=(236, 140, 140))
    d.line(P(hx - 8, ey - 6, hx + 8, ey - 6), fill=(110, 70, 50), width=6 * S)
    d.ellipse(P(hx - 12, hy + 46, hx + 12, hy + 66), fill=dark)
    if mouth == 'open':
        d.ellipse(P(hx - 34, hy + 70, hx + 34, hy + 124), fill=(90, 20, 30))
        d.ellipse(P(hx - 20, hy + 96, hx + 20, hy + 122), fill=(230, 90, 100))
    else:
        d.arc(P(hx - 34, hy + 64, hx + 34, hy + 104), 20, 160, fill=(110, 40, 40), width=6 * S)
    return down(im)


def fork_img(sz=170):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = sz * 4 / 100
    d.rounded_rectangle((46 * u, 40 * u, 54 * u, 96 * u), radius=4 * u, fill=(200, 206, 220))
    d.rounded_rectangle((34 * u, 30 * u, 66 * u, 44 * u), radius=6 * u, fill=(200, 206, 220))
    for x in (34, 45, 56):
        d.rounded_rectangle((x * u, 4 * u, (x + 10) * u, 36 * u), radius=4 * u, fill=(200, 206, 220))
    d.rounded_rectangle((32 * u, 0, 68 * u, 22 * u), radius=8 * u, fill=(244, 206, 110))
    d.ellipse((40 * u, 4 * u, 52 * u, 14 * u), fill=(200, 60, 40))
    return im.resize((sz, sz), Image.LANCZOS)


def reception_bg():
    im = vgrad(W, H, (226, 214, 196), (196, 180, 160)).convert('RGBA'); d = ImageDraw.Draw(im)
    d.rectangle((0, 1250, W, H), fill=(150, 130, 112))
    for x in range(0, W, 120):
        d.line((x, 1250, x - 60, H), fill=(136, 116, 100), width=3)
    d.rectangle((70, 560, 400, 1250), fill=(90, 110, 130))
    d.rectangle((90, 580, 380, 1240), fill=(160, 196, 220))
    rng = random.Random(2)
    for _ in range(60):
        x, y = rng.uniform(95, 375), rng.uniform(585, 1220)
        d.line((x, y, x - 8, y + 34), fill=(220, 236, 250), width=3)
    d.line((235, 580, 235, 1240), fill=(90, 110, 130), width=10)
    d.text((235, 530), 'ENTRADA', font=F('InterDisplay-Black', 40), fill=(90, 80, 70), anchor='mm')
    d.rectangle((952, 600, 968, 1250), fill=(110, 76, 50))
    d.ellipse((922, 580, 998, 616), fill=(110, 76, 50))
    for x in (912, 1008):
        d.line((960, 640, x, 680), fill=(110, 76, 50), width=10)
    cap = Image.new('RGBA', (150, 90), (0, 0, 0, 0)); dc = ImageDraw.Draw(cap)
    dc.chord((10, 0, 140, 140), 180, 360, fill=(214, 40, 48)); dc.rectangle((60, 60, 150, 76), fill=(170, 30, 36))
    im.alpha_composite(cap, (880, 610))
    d.rounded_rectangle((470, 1000, 1010, 1300), radius=20, fill=(120, 80, 54))
    d.rectangle((470, 990, 1010, 1030), fill=(150, 104, 70))
    d.rounded_rectangle((620, 1080, 860, 1150), radius=14, fill=(250, 200, 60))
    d.text((740, 1115), 'PORTARIA', font=F('InterDisplay-Black', 40), fill=(40, 56, 108), anchor='mm')
    return im


def rack_hoodie():
    return sc(M4.hoodie_flat(), 0.55).rotate(90, resample=Image.BICUBIC, expand=True)


def signature_layer(book):
    lay = Image.new('RGBA', book.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(L.CAVEAT, 64)
    x0 = 20 + (book.width - 40) / 2 + 40
    d.text((x0, 380), 'Dona Cida', font=f, fill=(36, 70, 200))
    d.text((x0 + 20, 446), '(vó do Léo)', font=ImageFont.truetype(L.CAVEAT, 44), fill=(36, 70, 200))
    return lay


def apology_note():
    w, h = 640, 420
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rectangle((24, 30, 24 + w, 30 + h), fill=140)
    im.paste((40, 30, 20, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, 14 + w, 14 + h), fill=(255, 246, 228))
    for y in range(90, h, 62):
        d.line((40, y + 14, w - 10, y + 14), fill=(214, 226, 244), width=3)
    ink = (36, 70, 200)
    f1, f2 = ImageFont.truetype(L.CAVEAT, 76), ImageFont.truetype(L.CAVEAT, 64)
    d.text((54, 40), 'Desculpa, netinho.', font=f1, fill=ink)
    d.text((54, 150), 'Tava uma delícia mesmo.', font=f2, fill=ink)
    d.text((w - 60, 290), '— Vó Cida', font=f2, fill=ink, anchor='ra')
    hx, hy = w - 90, 360
    d.polygon([(hx, hy + 30), (hx - 30, hy), (hx - 18, hy - 16), (hx, hy - 4), (hx + 18, hy - 16), (hx + 30, hy)], fill=(236, 80, 110))
    return im.rotate(3, resample=Image.BICUBIC, expand=True)


def bubble(text, w=420):
    im = Image.new('RGBA', (w, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, w - 10, 160), radius=60, fill=(255, 255, 255), outline=INK, width=6)
    d.polygon([(70, 150), (110, 150), (50, 210)], fill=(255, 255, 255), outline=INK)
    d.line((72, 152, 108, 152), fill=(255, 255, 255), width=8)
    d.text((w / 2, 86), text, font=ImageFont.truetype(L.CAVEAT, 96), fill=INK, anchor='mm')
    return im


# ------------------------------------------------------------------ setup
def setup():
    global KICKER, LEO_ST, ZE_ST, VO_ST, VO_OPEN, VO_SIL, PILL_FIN, PILL_ESC, VIG, K_BG, EMPTY, QM, REC_BG, RACK, HOOD_S
    global BOOK, SIGN, PEN, STAMP, LAS, FORK, NOTE, FLAMES, HOOD, SCREAM, SHH, APOLOGY, FIM, NEXT, BRASA, CCTV_VIG, HEART
    KICKER = L.build_kicker('A MARMITA SUMIU  ·  FINAL')
    LEO_ST = L.sticker(L.person('leo')); ZE_ST = L.sticker(M3.ze())
    raw = vo(); VO_ST = L.sticker(raw); VO_OPEN = L.sticker(vo('open'))
    VO_SIL = E2.silhouette(raw.resize((raw.width, int(raw.height * 0.95))), (40, 44, 60))
    PILL_FIN = L.label_pill('EPISÓDIO FINAL', '5', B_COL)
    PILL_ESC = L.label_pill('VOCÊS ESCOLHERAM', 'B', B_COL)
    VIG = L.make_vig(0.32, cy=0.45)
    K_BG = L.build_s1()
    EMPTY = L.build_empty_box()
    f = F('InterDisplay-Black', 120)
    QM = Image.new('RGBA', (110, 160), (0, 0, 0, 0))
    ImageDraw.Draw(QM).text((55, 80), '?', font=f, fill=WHITE, anchor='mm', stroke_width=7, stroke_fill=INK)
    REC_BG = reception_bg(); RACK = rack_hoodie(); HOOD_S = sc(M4.hoodie_flat(), 0.5)
    CCTV_VIG = L.make_vig(0.45, cy=0.5)
    M3.CCTV_VIG = CCTV_VIG
    BOOK = M4.visitor_book(); SIGN = signature_layer(BOOK); PEN = E2.icon_pen(200)
    STAMP = E2.stamp('VOVÓ?!')
    LAS = M4.open_lasagna(); FORK = fork_img(170)
    nb, t1, t2, sm = L.build_note(); NOTE = nb.copy(); NOTE.alpha_composite(t1); NOTE.alpha_composite(t2); NOTE.alpha_composite(sm)
    NOTE = sc(NOTE, 0.5)
    FLAMES = [M4.flame(150, 200, i) for i in range(3)]
    HOOD = M4.hoodie_flat()
    SCREAM = rich_line([('AAAAAH!', (255, 226, 80))], F('InterDisplay-Black', 130), stroke=12)
    SHH = bubble('shhh…')
    APOLOGY = apology_note()
    FIM = rich_line([('FIM', WHITE)], F('InterDisplay-Black', 200), stroke=14)
    NEXT = rich_line([('Agora no perfil: ', WHITE), ('BRASA', YEL)], F('InterDisplay-Black', 70), stroke=7)
    br = Image.open('/home/claude/reino/out/capa-brasa-ep1-hd.jpg').convert('RGBA')
    br = br.crop((0, 200, 1080, 1500)).resize((360, 433), Image.LANCZOS)
    fr = Image.new('RGBA', (br.width + 20, br.height + 20), (255, 255, 255, 255)); fr.alpha_composite(br, (10, 10))
    BRASA = fr.rotate(-4, resample=Image.BICUBIC, expand=True)
    HEART = Image.new('RGBA', (80, 74), (0, 0, 0, 0))
    ImageDraw.Draw(HEART).polygon([(40, 72), (4, 30), (12, 8), (40, 20), (68, 8), (76, 30)], fill=(236, 80, 110))
    build_caps()


def build_caps():
    global CAP
    CAP = {}
    for k in ORDER:
        pages = TJ['pages'][k]; gap = TJ['gaps'].get(k, 0.1); cps = []
        for i, (st, segs) in enumerate(pages):
            end = pages[i + 1][0] - 0.05 if i + 1 < len(pages) else (END_T + 0.2 if k == 's6' else DURS[k] + 1)
            ss, acc = [], st
            for text, col in segs:
                ss.append((acc, text, tuple(col))); acc += gap * len(text.split())
            cps.append((st, end, ss))
        CAP[k] = Caption(cps, font=('InterDisplay-ExtraBold', 74), top=1350, maxw=940, gap=gap)


def finish(im, k, t):
    comp(im, KICKER, ((W - KICKER.width) // 2, 196)); CAP[k].draw(im, t); return im.convert('RGB')


def pop_in(im, spr, cx, by, t, t0=0.0, s=1.0, bob=4):
    q = (t - t0) / 0.4
    if q < 0: return
    oy = (1 - L.backout(q)) * 420 if q < 1 else 0
    sp = sc(spr, s)
    comp(im, sp, (cx - sp.width / 2, by - sp.height + oy + bob * math.sin(t * 3)))


def cctv(im, t, stamp='08/11  11:52'):
    a = np.asarray(im.convert('RGB'), np.float32)
    g = a.mean(axis=2, keepdims=True); a = g + (a - g) * 0.8
    a = a * np.array([0.95, 1.0, 0.95], np.float32) * 0.86 + 8
    a[::4] *= 0.78
    a += np.random.default_rng(int(t * 15) % 4).normal(0, 1, (H, W, 1)).astype(np.float32) * 9
    out = L.apply_vig(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'), CCTV_VIG)
    d = ImageDraw.Draw(out); fm = F('Inter-Bold', 40)
    d.text((70, 420), 'CAM 01 · PORTARIA', font=fm, fill=(236, 240, 236), stroke_width=3, stroke_fill=(20, 24, 22))
    secs = int(t)
    d.text((W - 70, 420), f'{stamp}:{secs % 60:02d}', font=fm, fill=(236, 240, 236), anchor='ra', stroke_width=3, stroke_fill=(20, 24, 22))
    if int(t * 2) % 2 == 0:
        d.ellipse((W - 190, 486, W - 160, 516), fill=(236, 40, 40))
        d.text((W - 148, 482), 'REC', font=fm, fill=(236, 40, 40), stroke_width=3, stroke_fill=(20, 24, 22))
    for (x0, y0, sx, sy) in [(50, 300, 1, 1), (W - 50, 300, -1, 1), (50, 1290, 1, -1), (W - 50, 1290, -1, -1)]:
        d.line((x0, y0, x0 + 60 * sx, y0), fill=(236, 240, 236), width=5); d.line((x0, y0, x0, y0 + 60 * sy), fill=(236, 240, 236), width=5)
    return out


# ------------------------------------------------------------------ cenas
def frame_s1(t):
    im = K_BG.copy()
    pop_in(im, LEO_ST, 260, 1330, t, 0.0, 0.8)
    comp(im, EMPTY, (650 - EMPTY.width / 2, 980 + 6 * math.sin(t * 2.4)))
    for (qx, qy, ph) in [(560, 760, 0.0), (900, 820, 0.9), (420, 640, 1.7)]:
        comp(im, QM, (qx - 55, qy - 80 + 10 * math.sin(2 * math.pi * t / 1.3 + ph)), clamp((t - 0.3) * 3))
    T2 = p2_at('s1')
    if t >= T2 - 0.15:
        s = lerp(0.55, 1.0, L.backout((t - T2 + 0.15) / 0.4))
        pi = sc(PILL_FIN, s); comp(im, pi, (540 - pi.width / 2, 400 - pi.height / 2), clamp((t - T2 + 0.15) * 6))
    return finish(im, 's1', t)


def frame_s2(t):
    T2 = p2_at('s2')
    im = REC_BG.copy()
    zs = sc(ZE_ST, 0.5)
    comp(im, zs, (660 - zs.width / 2, 1010 - zs.height * 0.62))
    comp(im, sc(Image.new('RGBA', (1, 1)), 1), (0, 0))
    im.alpha_composite(Image.new('RGBA', (540, 300), (120, 80, 54, 255)), (470, 1030))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((620, 1080, 860, 1150), radius=14, fill=(250, 200, 60))
    d.text((740, 1115), 'PORTARIA', font=F('InterDisplay-Black', 40), fill=(40, 56, 108), anchor='mm')
    k = clamp((t - 0.2) / 1.4)
    vx = lerp(240, 400, eio(k))
    vs = sc(VO_SIL, 0.6)
    comp(im, vs, (vx - vs.width / 2, 1290 - vs.height))
    rng = random.Random(int(t * 10))
    for _ in range(6):
        x, y = vx + rng.uniform(-80, 80), 1290 - vs.height * rng.uniform(0.2, 0.9)
        d.ellipse((x - 5, y - 8, x + 5, y + 8), fill=(170, 210, 240, 255))
    if t < T2 + 0.3:
        comp(im, RACK, (960 - RACK.width / 2, 690))
    else:
        q = eio(clamp((t - T2 - 0.3) / 0.8))
        hx, hy = lerp(960, vx + 40, q), lerp(760, 1060, q) - 120 * math.sin(math.pi * q)
        hs = HOOD_S.rotate(lerp(90, -10, q), resample=Image.BICUBIC, expand=True)
        comp(im, hs, (hx - hs.width / 2, hy - hs.height / 2))
    im = cctv(im, t)
    if t > 0.05:
        s = lerp(0.55, 1.0, L.backout((t - 0.05) / 0.4))
        pi = sc(PILL_ESC, s); comp(im, pi, (540 - pi.width / 2, 600 - pi.height / 2), clamp((t - 0.05) * 6) * (1 - clamp((t - T2 + 0.4) * 3)))
    return finish(im, 's2', t)


def frame_s3(t):
    im = L.apply_vig(L.rays(t, (60, 96, 176), (74, 112, 196)), VIG)
    T2 = p2_at('s3')
    k = eo(clamp((t - 0.1) / 0.4))
    up = eio(clamp((t - T2 + 0.3) / 0.4))
    bsc = lerp(0.95, 0.72, up)
    bk = sc(BOOK, bsc)
    bx, by = 540 - bk.width / 2, lerp(1100, 560, k) - 230 * up
    comp(im, bk, (bx, by), k)
    sp = clamp((t - 0.6) / max(0.6, T2 - 0.9))
    sg = L.wipe(sc(SIGN, bsc), sp, x0=int(bk.width * 0.52), x1=bk.width)
    comp(im, sg, (bx, by), k)
    if t < T2 + 0.2:
        pn = sc(PEN, 0.8)
        px_ = bx + bk.width * lerp(0.56, 0.92, sp); py_ = by + 300 + 12 * math.sin(t * 20)
        comp(im, pn, (px_ - 20, py_ - pn.height + 40), clamp((t - 0.5) * 4))
    if t >= T2 - 0.15:
        pop_in(im, VO_ST, 330, 1330, t, T2 - 0.15, 0.62)
        if t >= T2 + 0.35:
            q = L.backout(clamp((t - T2 - 0.35) / 0.35)); st = sc(STAMP, lerp(1.8, 0.9, q))
            comp(im, st, (700 - st.width / 2, 1060 - st.height / 2), clamp((t - T2 - 0.35) * 4))
            E2.rings(im, 330, 960, t, (255, 150, 190), 120, 240)
    return finish(im, 's3', t)


def frame_s4(t):
    im = L.apply_vig(L.rays(t, (240, 170, 60), (250, 190, 90)), VIG)
    T2 = p2_at('s4')
    comp(im, LAS, (640 - LAS.width / 2, 980 - LAS.height / 2))
    pop_in(im, VO_ST, 270, 1330, t, 0.0, 0.72)
    if t > 0.6:
        ph = (t * 1.6) % 1.0
        fy = 900 - 160 * abs(math.sin(math.pi * ph))
        fk = FORK.rotate(-30 + 40 * math.sin(math.pi * ph), resample=Image.BICUBIC, expand=True)
        comp(im, fk, (470 - fk.width / 2, fy - fk.height / 2))
    if t >= T2 - 0.1:
        q = L.backout(clamp((t - T2 + 0.1) / 0.45)); nt = sc(NOTE, lerp(0.4, 1.0, q)).rotate(-6, resample=Image.BICUBIC, expand=True)
        comp(im, nt, (760 - nt.width / 2, 560 - nt.height / 2), clamp((t - T2 + 0.1) * 5))
        for i in range(4):
            ph = ((t - T2) * 0.7 + i * 0.25) % 1.0
            comp(im, sc(HEART, 0.6 + 0.3 * ph), (380 + i * 70, 760 - ph * 260), 1 - ph)
    return finish(im, 's4', t)


def frame_s5(t):
    T2 = p2_at('s5')
    if t < T2 - 0.1:
        im = L.apply_vig(L.rays(t, (232, 76, 60), (244, 104, 80)), VIG)
        tf = max(0.6, T2 - 1.4)
        vs = VO_OPEN if t >= tf else VO_ST
        pop_in(im, vs, 380, 1330, t, 0.0, 0.72)
        if t >= tf:
            for i, fl in enumerate(FLAMES):
                s = 0.55 + 0.08 * math.sin(t * 9 + i)
                f2 = sc(fl, s).rotate(-70, resample=Image.BICUBIC, expand=True)
                comp(im, f2, (500 + i * 70, 880 - f2.height / 2 + 30 * math.sin(t * 7 + i)), clamp((t - tf) * 4))
            q = eo(clamp((t - tf) / 0.3))
            scr = sc(SCREAM, lerp(1.6, 1.0, q) * (1 + 0.04 * math.sin(t * 30))).rotate(-6, resample=Image.BICUBIC, expand=True)
            comp(im, scr, (560 - scr.width / 2, 560 - scr.height / 2), q)
            hq = clamp((t - tf - 0.2) / 1.0)
            hd = HOOD.rotate(hq * 300, resample=Image.BICUBIC, expand=True)
            comp(im, sc(hd, 0.6), (220 - 120 * hq, 900 + 380 * hq * hq), 1 - hq * 0.3)
            im = M4.shake_img(im, t, tf, 18, 0.7)
    else:
        im = L.apply_vig(L.rays(t, (60, 96, 176), (74, 112, 196)), VIG)
        pop_in(im, ZE_ST, 330, 1330, t, T2 - 0.1, 0.62)
        if t >= T2 + 0.35:
            q = L.backout(clamp((t - T2 - 0.35) / 0.4)); b = sc(SHH, lerp(0.5, 1.0, q))
            comp(im, b, (560, 700 - b.height / 2), clamp((t - T2 - 0.35) * 5))
    return finish(im, 's5', t)


def frame_s6(t):
    im = L.apply_vig(L.rays(t, (250, 180, 80), (255, 204, 110), speed=4), VIG)
    pop_in(im, LEO_ST, 230, 1330, t, 0.0, 0.66)
    pop_in(im, VO_ST, 820, 1330, t, 0.15, 0.6)
    comp(im, sc(LAS, 0.8), (540 - LAS.width * 0.4, 1060 - LAS.height * 0.4 + 4 * math.sin(t * 2)))
    for i in range(5):
        ph = (t * 0.5 + i / 5) % 1.0
        x = 470 + i * 40 + 14 * math.sin(t * 2 + i); y = 1000 - ph * 200
        d = ImageDraw.Draw(im); d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 255, 255, int(120 * math.sin(math.pi * ph))))
    T2 = p2_at('s6')
    if t >= T2 - 0.2:
        q = L.backout(clamp((t - T2 + 0.2) / 0.45)); ap = sc(APOLOGY, lerp(0.4, 0.95, q))
        comp(im, ap, (540 - ap.width / 2, 620 - ap.height / 2), clamp((t - T2 + 0.2) * 5))
    if t >= END_T:
        k = clamp((t - END_T) / 0.35)
        im.alpha_composite(Image.new('RGBA', (W, H), (20, 14, 30, int(205 * k))))
        q = L.backout(clamp((t - END_T) / 0.45))
        fm = sc(FIM, lerp(0.5, 1.0, q)); comp(im, fm, (540 - fm.width / 2, 470 - fm.height / 2), k)
        if t >= END_T + 0.5:
            q2 = eo(clamp((t - END_T - 0.5) / 0.4))
            comp(im, NEXT, (540 - NEXT.width / 2, 700 + (1 - q2) * 30), q2)
            comp(im, BRASA, (540 - BRASA.width / 2, 820 + (1 - q2) * 60), q2)
            sub = rich_line([('o reino onde cada seguidor vira morador', (240, 236, 250))], F('InterDisplay-ExtraBold', 44), stroke=5)
            comp(im, sub, (540 - sub.width / 2, 1330), q2)
        return im.convert('RGB') if t >= END_T + 0.2 else finish(im, 's6', t)
    return finish(im, 's6', t)


SCENES = [('s1', frame_s1), ('s2', frame_s2), ('s3', frame_s3), ('s4', frame_s4), ('s5', frame_s5), ('s6', frame_s6)]


# ------------------------------------------------------------------ áudio
def build_audio(path):
    SR = LA.SR; rng = np.random.default_rng(7)
    st, acc = {}, 0.0
    for k in ORDER: st[k] = acc; acc += round(DURS[k] * FPS) / FPS
    total = acc; n = int(total * SR)
    music = np.zeros(n)

    def put(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if i < n: music[i:j] += sig[:j - i]
    put(LA.groove(st['s5']), 0)
    put(LA.groove(st['s6'] - st['s5'], full=False), st['s5'])
    put(LA.groove(total - st['s6']), st['s6'])
    fx = np.zeros(n + 3 * SR)

    def add(sig, at, g=1.0):
        i = int(at * SR); fx[i:i + len(sig)] += sig * g

    def tt(d): return np.arange(int(d * SR)) / SR

    def rain(d, g=0.06):
        y = LA.bandpass(rng.standard_normal(int(d * SR)), 1500, 8000); y /= np.abs(y).max()
        q = tt(d); return y * g * np.minimum(1, q / 0.3) * np.minimum(1, (d - q) / 0.3)

    def scream(d=0.8, g=0.2):
        q = tt(d); f = 700 + 300 * np.sin(np.pi * q / d) + 40 * np.sin(2 * np.pi * 8 * q)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR); y = np.tanh(3 * y) + 0.3 * LA.bandpass(rng.standard_normal(len(q)), 800, 4000)
        return y / np.abs(y).max() * g * np.minimum(1, q / 0.04) * np.minimum(1, (d - q) / 0.2)

    def shh(d=0.7, g=0.12):
        y = LA.bandpass(rng.standard_normal(int(d * SR)), 3000, 9000); y /= np.abs(y).max()
        q = tt(d); return y * g * np.sin(np.pi * q / d)

    add(LA.whoosh(), st['s1']); add(LA.ding(1046.5), st['s1'] + p2_at('s1'))
    add(LA.whoosh(0.25, 0.25), st['s2']); add(rain(DURS['s2']), st['s2'])
    add(LA.slide_whistle(), st['s2'] + p2_at('s2') + 0.3, 0.7)
    add(LA.whoosh(0.25, 0.25), st['s3']); add(LA.scribble(), st['s3'] + 0.7) if hasattr(LA, 'scribble') else None
    add(LA.tada(), st['s3'] + p2_at('s3') + 0.3); add(LA.thunk(), st['s3'] + p2_at('s3') + 0.35, 1.2)
    add(LA.whoosh(0.25, 0.25), st['s4'])
    for i in range(4): add(LA.blip(700, 500, 0.07, 0.15), st['s4'] + 0.7 + i * 0.62)
    add(LA.ding(1318.5), st['s4'] + p2_at('s4'))
    tf = max(0.6, p2_at('s5') - 1.4)
    add(LA.whoosh(0.25, 0.25), st['s5']); add(scream(g=0.12), st['s5'] + tf); add(LA.crash(), st['s5'] + tf, 0.4)
    add(shh(), st['s5'] + p2_at('s5') + 0.35)
    add(LA.whoosh(0.25, 0.25), st['s6']); add(LA.ding(1174.7), st['s6'] + p2_at('s6'))
    add(LA.tada(), st['s6'] + END_T + 0.05)
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
        duck = 1 - 0.75 * np.clip(env / 0.02, 0, 1)
        duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
        mixm = music * 0.3 * duck + fx * 0.6 + nar * (0.9 / np.abs(nar).max())
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
                    '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', out + '.part.mp4'], check=True)
    os.replace(out + '.part.mp4', out); print('ok', out, round(total, 2))


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    t0 = time.time(); setup(); print(f'setup {time.time() - t0:.1f}s', flush=True)
    fns = dict(SCENES)
    if mode == 'preview':
        shots = [('s1', p2_at('s1') + 0.6), ('s2', 0.8), ('s2', p2_at('s2') + 0.8), ('s3', p2_at('s3') - 0.4), ('s3', p2_at('s3') + 0.8),
                 ('s4', p2_at('s4') + 0.6), ('s5', p2_at('s5') * 0.55 + 0.4), ('s5', p2_at('s5') + 0.8), ('s6', p2_at('s6') + 0.6),
                 ('s6', END_T + 1.5)]
        sheet = Image.new('RGB', (W // 3 * 5, H // 3 * 2))
        for i, (k, tt) in enumerate(shots):
            sheet.paste(fns[k](tt).resize((W // 3, H // 3), Image.LANCZOS), ((i % 5) * (W // 3), (i // 5) * (H // 3)))
        sheet.save(WORK + '/sheet.png'); print('sheet', DURS, round(sum(DURS.values()), 2))
    elif mode == 'render':
        only = sys.argv[2:] or ORDER
        for idx, (k, fn) in enumerate(SCENES):
            if k in only: L.encode(k, fn, DURS[k], fade_in=0, fade_out=12 if idx == len(SCENES) - 1 else 0)
        if all(os.path.exists(f'{WORK}/{k}.mp4') for k in ORDER): assemble(WORK + '/a-marmita-sumiu-ep5-final.mp4')
    elif mode == 'audio':
        assemble(WORK + '/a-marmita-sumiu-ep5-final.mp4')
