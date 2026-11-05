#!/usr/bin/env python3
"""Quem Bate à Porta — Episódio 1. Vertical 1080x1920, 30 fps, flat-style animation."""
import os, sys, math, random, subprocess, wave, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1080, 1920, 30
S = 2  # supersampling for static art
WORK = '/home/claude/video'
os.makedirs(WORK, exist_ok=True)

FD = '/usr/share/fonts/opentype/inter/'
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + name + '.otf', int(size))
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def P(*v): return [int(round(c * S)) for c in v]

WHITE = (244, 244, 248); WARM = (255, 196, 104); RED = (232, 70, 76); INK = (6, 6, 12)

# ---------------------------------------------------------------- helpers
def vgrad(w, h, top, bot, y0=0, y1=None):
    if y1 is None: y1 = h
    t = np.clip((np.arange(h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None, None]
    a = np.array(top, np.float32)[None, None, :] * (1 - t) + np.array(bot, np.float32)[None, None, :] * t
    a = np.repeat(a, w, axis=1)
    return Image.fromarray(a.astype(np.uint8), 'RGB')

def glow(img, draw_fn, color, blur, gain=1.0):
    m = Image.new('L', img.size, 0)
    draw_fn(ImageDraw.Draw(m))
    if blur: m = m.filter(ImageFilter.GaussianBlur(blur))
    if gain != 1.0:
        m = Image.fromarray(np.clip(np.asarray(m, np.float32) * gain, 0, 255).astype(np.uint8))
    light = Image.composite(Image.new('RGB', img.size, color), Image.new('RGB', img.size, 0), m)
    return ImageChops.screen(img, light)

def fill_mask(img, draw_fn, color, blur=0, alpha=1.0):
    m = Image.new('L', img.size, 0)
    draw_fn(ImageDraw.Draw(m))
    if blur: m = m.filter(ImageFilter.GaussianBlur(blur))
    if alpha != 1.0: m = m.point(lambda v: int(v * alpha))
    img.paste(Image.new('RGB', img.size, color), (0, 0), m)
    return img

def down(img):
    return img.resize((img.width // S, img.height // S), Image.LANCZOS)

def comp(dst, src, xy, a=1.0):
    x, y = int(round(xy[0])), int(round(xy[1]))
    if a <= 0.003: return
    if a < 0.999:
        src = src.copy(); src.putalpha(src.getchannel('A').point(lambda v, a=a: int(v * a)))
    if x + src.width <= 0 or y + src.height <= 0: return
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height)); x += sx; y += sy
    if x >= dst.width or y >= dst.height or src.width <= 0 or src.height <= 0: return
    if x + src.width > dst.width or y + src.height > dst.height:
        src = src.crop((0, 0, min(src.width, dst.width - x), min(src.height, dst.height - y)))
    dst.alpha_composite(src, (x, y))

def make_mult(vig=0.55, scrim=True):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (x - W / 2) / (W / 2); dy = (y - H / 2) / (H / 2)
    r = np.sqrt(dx * dx + 0.75 * dy * dy)
    v = 1 - vig * np.clip((r - 0.5) / 0.85, 0, 1) ** 1.6
    if scrim:
        yy = np.arange(H, dtype=np.float32)
        s = np.exp(-((yy - 1430) / 240) ** 2) * 0.5
        v = v * (1 - s)[:, None]
    return v[..., None].astype(np.float32)

def apply_mult(im, mult):
    a = np.asarray(im.convert('RGB'), np.float32) * mult
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')

def shake(t, knocks, amp, freq=16, tau=0.07):
    v = 0.0
    for k in knocks:
        if t >= k:
            dt = t - k
            v += amp * math.exp(-dt / tau) * math.cos(2 * math.pi * freq * dt)
    return int(round(v))

class Rain:
    def __init__(self, seed, layers, slant=0.16):
        rng = random.Random(seed)
        self.drops = []
        for (n, l0, l1, s0, s1, a0, a1, wd) in layers:
            for _ in range(n):
                self.drops.append((rng.uniform(0, W + 400), rng.uniform(0, H + 300), rng.uniform(s0, s1),
                                   rng.uniform(l0, l1), rng.randint(a0, a1), wd))
        self.slant = slant
    def layer(self, t, color=(178, 196, 232)):
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        for x0, y0, sp, ln, a, wd in self.drops:
            y = (y0 + sp * t) % (H + 300) - 150
            x = (x0 - self.slant * sp * t) % (W + 400) - 200
            d.line([(x, y), (x + self.slant * ln, y - ln)], fill=color + (a,), width=wd)
        return L

RAIN_OUT = [(150, 30, 60, 1300, 1700, 28, 58, 1), (65, 60, 115, 1900, 2500, 50, 95, 2)]
RAIN_GLASS = [(130, 22, 46, 1100, 1500, 22, 48, 1), (30, 40, 70, 1500, 1900, 34, 60, 2)]

class Caption:
    """Word-by-word captions. pages: [(start, end, [(seg_start, text, color), ...]), ...]"""
    def __init__(self, pages, font=('InterDisplay-ExtraBold', 76), top=1300, maxw=920, gap=0.085, cx=540, stroke=6):
        fnt = F(*font)
        asc, desc = fnt.getmetrics()
        lh = int(font[1] * 1.18)
        pad = stroke + 4
        sp = fnt.getlength(' ')
        self.pages = []
        for (pst, pend, segs) in pages:
            lines = []
            for (st, text, color) in segs:
                cur = []
                for i, tok in enumerate(text.split()):
                    item = (tok, color, st + i * gap)
                    if cur and fnt.getlength(' '.join(w for w, _, _ in cur + [item])) > maxw:
                        lines.append(cur); cur = [item]
                    else:
                        cur.append(item)
                if cur: lines.append(cur)
            words = []
            for li, line in enumerate(lines):
                total = fnt.getlength(' '.join(w for w, _, _ in line))
                x = cx - total / 2
                y = top + li * lh
                for (tok, color, ap) in line:
                    wl = fnt.getlength(tok)
                    im = Image.new('RGBA', (int(wl) + 2 * pad + 4, asc + desc + 2 * pad), (0, 0, 0, 0))
                    ImageDraw.Draw(im).text((pad, pad), tok, font=fnt, fill=color, stroke_width=stroke, stroke_fill=INK)
                    words.append((im, int(x) - pad, y - pad, ap))
                    x += wl + sp
            self.pages.append((pst, pend, words))
    def draw(self, frame, t):
        for (pst, pend, words) in self.pages:
            if t < pst or t > pend + 0.3: continue
            pa = 1.0 - eo((t - pend) / 0.25) if t > pend else 1.0
            for (im, x, y, ap) in words:
                if t < ap: continue
                a = eo((t - ap) / 0.2) * pa
                dy = (1 - eo((t - ap) / 0.28)) * 24
                comp(frame, im, (x, y + dy), a)
        return frame

def tracked(text, fnt, color, track=5):
    widths = [fnt.getlength(c) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    asc, desc = fnt.getmetrics()
    im = Image.new('RGBA', (int(total) + 20, asc + desc + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = 10
    for c, w in zip(text, widths):
        d.text((x, 10), c, font=fnt, fill=color); x += w + track
    return im

def build_kicker():
    txt = tracked('QUEM BATE À PORTA  ·  EP. 1', F('Inter-SemiBold', 30), (232, 232, 240, 230), 5)
    im = Image.new('RGBA', (txt.width + 34, txt.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cy = txt.height // 2 + 1
    d.ellipse((4, cy - 8, 20, cy + 8), fill=RED + (255,))
    im.alpha_composite(txt, (26, 0))
    return im

def rich_line(parts, fnt, stroke=6):
    total = sum(fnt.getlength(p) for p, _ in parts)
    asc, desc = fnt.getmetrics()
    im = Image.new('RGBA', (int(total) + 30, asc + desc + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 15
    for p, c in parts:
        d.text((x, 15), p, font=fnt, fill=c, stroke_width=stroke, stroke_fill=INK); x += fnt.getlength(p)
    return im

# ---------------------------------------------------------------- scene 1: the street
def build_s1():
    w, h = W * S, H * S
    img = vgrad(w, h, (4, 7, 20), (34, 42, 78), 0, 1300 * S)
    img = glow(img, lambda d: d.ellipse(P(90, 270, 430, 610), fill=255), (40, 48, 86), 60 * S)
    d = ImageDraw.Draw(img)
    d.ellipse(P(198, 378, 322, 502), fill=(214, 220, 236))
    for (cx, cy, r) in [(240, 420, 12), (282, 460, 9), (260, 472, 6), (292, 410, 5)]:
        d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=(196, 202, 222))
    img = fill_mask(img, lambda d: [d.ellipse(P(*b), fill=255) for b in
                                    [(20, 455, 430, 520), (160, 495, 600, 565), (620, 380, 1120, 450),
                                     (760, 300, 1180, 350), (480, 600, 900, 650), (-80, 640, 260, 690)]],
                    (20, 26, 50), blur=10 * S, alpha=0.92)
    d = ImageDraw.Draw(img)
    rng = random.Random(7); x = -20
    while x < W:
        bw = rng.randint(70, 150); bh = rng.randint(110, 270)
        d.rectangle(P(x, 1300 - bh, x + bw, 1300), fill=(15, 20, 40))
        for _ in range(rng.randint(0, 3)):
            wx = x + rng.randint(10, max(11, bw - 24)); wy = 1300 - bh + rng.randint(15, max(16, bh - 40))
            d.rectangle(P(wx, wy, wx + 10, wy + 14), fill=(46, 50, 74) if rng.random() < 0.75 else (110, 92, 56))
        x += bw + rng.randint(-10, 6)
    img.paste(vgrad(w, (H - 1300) * S, (18, 20, 34), (5, 6, 11)), (0, 1300 * S))
    d = ImageDraw.Draw(img)
    d.rectangle(P(0, 1300, W, 1336), fill=(26, 28, 44))
    d.rectangle(P(0, 1336, W, 1344), fill=(38, 40, 58))
    for x in range(-40, W, 160):
        d.rectangle(P(x, 1600, x + 90, 1610), fill=(36, 38, 52))
    # left house
    d.rectangle(P(-30, 1020, 250, 1300), fill=(11, 14, 28))
    d.polygon(P(-60, 1020, 110, 860, 280, 1020), fill=(9, 11, 24))
    d.rectangle(P(70, 1090, 150, 1180), fill=(17, 21, 37))
    # Lia's house
    d.rectangle(P(885, 815, 925, 880), fill=(10, 12, 26))
    d.polygon(P(505, 980, 775, 770, 1045, 980), fill=(10, 12, 26))
    d.rectangle(P(540, 980, 1010, 1300), fill=(13, 16, 32))
    d.ellipse(P(749, 864, 801, 916), fill=(19, 23, 40))
    d.rectangle(P(860, 1150, 950, 1300), fill=(7, 9, 18))
    img = glow(img, lambda d: d.rectangle(P(560, 1000, 820, 1220), fill=255), (100, 62, 24), 34 * S)
    img.paste(vgrad(180 * S, 140 * S, (255, 206, 120), (226, 146, 66)), tuple(P(600, 1040)))
    d = ImageDraw.Draw(img)
    sil = (66, 40, 22)
    d.ellipse(P(717, 1070, 755, 1110), fill=sil)
    d.ellipse(P(700, 1104, 772, 1240), fill=sil)
    hc = (13, 16, 32)
    d.rectangle(P(592, 1180, 790, 1250), fill=hc)
    d.rectangle(P(592, 1032, 600, 1188), fill=hc); d.rectangle(P(780, 1032, 788, 1188), fill=hc)
    d.rectangle(P(592, 1032, 788, 1040), fill=hc)
    d.rectangle(P(686, 1040, 694, 1180), fill=hc); d.rectangle(P(600, 1106, 780, 1114), fill=hc)
    d.rectangle(P(584, 1180, 796, 1192), fill=(20, 24, 42))
    # fence
    fc = (8, 10, 20)
    for x in range(520, W + 20, 26):
        d.rectangle(P(x, 1252, x + 11, 1300), fill=fc)
        d.polygon(P(x, 1252, x + 5.5, 1242, x + 11, 1252), fill=fc)
    d.rectangle(P(520, 1266, W, 1272), fill=fc)
    # streetlight
    d.rectangle(P(372, 846, 384, 1300), fill=(20, 22, 34))
    d.line(P(378, 852, 398, 832, 450, 828), fill=(20, 22, 34), width=8 * S)
    d.polygon(P(428, 818, 482, 818, 472, 840, 438, 840), fill=(26, 28, 40))
    img = glow(img, lambda d: d.polygon(P(442, 842, 468, 842, 650, 1312, 262, 1312), fill=150), (120, 92, 52), 22 * S)
    img = glow(img, lambda d: d.ellipse(P(280, 1290, 640, 1342), fill=200), (120, 96, 58), 18 * S)
    img = glow(img, lambda d: d.ellipse(P(426, 822, 484, 860), fill=255), (255, 214, 140), 16 * S)
    d = ImageDraw.Draw(img); d.ellipse(P(440, 836, 470, 848), fill=(255, 236, 190))
    img = glow(img, lambda d: d.rectangle(P(430, 1360, 480, 1720), fill=110), (90, 70, 40), 20 * S)
    img = glow(img, lambda d: d.rectangle(P(640, 1360, 740, 1660), fill=110), (100, 66, 28), 24 * S)
    return img

S1_DUR = 5.5
def setup_s1():
    global S1_BG, S1_RAIN, S1_CAP
    S1_BG = build_s1()
    S1_RAIN = Rain(1, RAIN_OUT)
    S1_CAP = Caption([(0.25, S1_DUR, [(0.3, '3h17 da manhã.', WARM),
                                       (1.35, 'Lia mora sozinha na última casa da rua.', WHITE)])])

def frame_s1(t):
    z = 1 + 0.11 * eio(t / S1_DUR)
    fx, fy = 690 * S, 1110 * S
    l, tp = fx * (1 - 1 / z), fy * (1 - 1 / z)
    im = S1_BG.resize((W, H), Image.BILINEAR, box=(l, tp, l + W * S / z, tp + H * S / z)).convert('RGBA')
    im.alpha_composite(S1_RAIN.layer(t))
    im = apply_mult(im, MULT_SCRIM)
    comp(im, KICKER, ((W - KICKER.width) // 2, 210), eo(t / 0.4))
    S1_CAP.draw(im, t)
    return im.convert('RGB')

# ---------------------------------------------------------------- scenes 2 & 5: the phone
PH = (190, 330, 890, 2120)
SCR = (212, 352, 868, 2120)
NX, NY, NW = (W - 630) // 2, 770, 630

def build_phone(time_str):
    w, h = W * S, H * S
    body = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    for b in [(183, 600, 193, 680), (183, 700, 193, 780), (887, 640, 897, 790)]:
        d.rounded_rectangle(P(*b), radius=3 * S, fill=(44, 44, 52))
    d.rounded_rectangle(P(*PH), radius=92 * S, fill=(24, 24, 30), outline=(84, 84, 98), width=3 * S)
    off = body.copy(); do = ImageDraw.Draw(off)
    do.rounded_rectangle(P(*SCR), radius=72 * S, fill=(7, 7, 10))
    refl = Image.new('L', (w, h), 0)
    ImageDraw.Draw(refl).polygon(P(212, 352, 520, 352, 300, 1100, 212, 1300), fill=14)
    smask = Image.new('L', (w, h), 0); ImageDraw.Draw(smask).rounded_rectangle(P(*SCR), radius=72 * S, fill=255)
    off.paste((255, 255, 255, 255), (0, 0), ImageChops.multiply(refl, smask))
    on = body.copy()
    sw, sh = (SCR[2] - SCR[0]) * S, (SCR[3] - SCR[1]) * S
    wall = vgrad(sw, sh, (46, 36, 96), (10, 10, 28), 0, int(sh * 0.7))
    wall = glow(wall, lambda d: d.ellipse((-200 * S, 500 * S, 400 * S, 1200 * S), fill=200), (90, 44, 140), 120 * S)
    wall = glow(wall, lambda d: d.ellipse((300 * S, -100 * S, 900 * S, 500 * S), fill=200), (30, 60, 150), 120 * S)
    wmask = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(wmask).rounded_rectangle((0, 0, sw - 1, sh + 200 * S), radius=72 * S, fill=255)
    on.paste(wall, tuple(P(SCR[0], SCR[1])), wmask)
    dn = ImageDraw.Draw(on)
    dn.text(P(540, 452), 'sexta-feira, 13 de novembro', font=F('Inter-Medium', 34 * S), fill=(226, 226, 238), anchor='mt')
    dn.text(P(540, 486), time_str, font=F('InterDisplay-SemiBold', 200 * S), fill=(240, 240, 248), anchor='mt')
    for im in (off, on):
        ImageDraw.Draw(im).rounded_rectangle(P(466, 372, 614, 414), radius=21 * S, fill=(0, 0, 0))
    return down(off), down(on)

def notif_card(msg, w=NW):
    ft = F('Inter-SemiBold', 33 * S); fm = F('Inter-Regular', 42 * S); fs = F('Inter-Regular', 28 * S)
    maxw = (w - 112 - 26) * S
    lines, cur = [], ''
    for tok in msg.split():
        trial = (cur + ' ' + tok).strip()
        if cur and fm.getlength(trial) > maxw: lines.append(cur); cur = tok
        else: cur = trial
    lines.append(cur)
    hh = 72 + len(lines) * 54 + 26
    im = Image.new('RGBA', (w * S, hh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, hh * S - 1), radius=40 * S, fill=(64, 64, 86, 232))
    d.rounded_rectangle((24 * S, 24 * S, 92 * S, 92 * S), radius=16 * S, fill=(52, 199, 89))
    d.ellipse((36 * S, 38 * S, 80 * S, 72 * S), fill=(255, 255, 255))
    d.polygon([(44 * S, 64 * S), (38 * S, 82 * S), (58 * S, 70 * S)], fill=(255, 255, 255))
    d.text((112 * S, 26 * S), 'Número desconhecido', font=ft, fill=(242, 242, 248))
    d.text(((w - 26) * S, 30 * S), 'agora', font=fs, fill=(176, 178, 196), anchor='ra')
    for i, ln in enumerate(lines):
        d.text((112 * S, (72 + i * 54) * S), ln, font=fm, fill=(238, 238, 246))
    return down(im), hh

S2_DUR, S5_DUR = 6.0, 7.0
S5_KNOCKS = [3.9, 4.25, 4.6]
def setup_phone():
    global PH2_OFF, PH2_ON, PH5_ON, ROOM, ROOM_GLOW, N1, N2, N2H, S2_CAP, S5_CAP
    PH2_OFF, PH2_ON = build_phone('3:17')
    _, PH5_ON = build_phone('3:18')
    ROOM = np.asarray(vgrad(W, H, (14, 13, 24), (4, 4, 8)), np.float32)
    g = glow(Image.new('RGB', (W, H), 0), lambda d: d.rectangle(PH, fill=255), (56, 50, 124), 90)
    ROOM_GLOW = np.asarray(g, np.float32)
    N1, _ = notif_card('não abre a porta.')
    N2, N2H = notif_card('quem tá batendo na sua porta não sou eu.')
    S2_CAP = Caption([(0.15, 2.9, [(0.2, 'O celular vibrou.', WHITE)]),
                      (3.0, S2_DUR, [(3.05, 'Ela nunca tinha visto esse número.', WHITE)])])
    S5_CAP = Caption([(0.15, 3.5, [(0.2, 'Outra mensagem.', WHITE)]),
                      (3.6, S5_DUR, [(3.65, 'E as batidas continuaram.', WHITE)])])

def frame_phone(t, scene):
    if scene == 2:
        on = 0.0 if t < 0.55 else eo((t - 0.55) / 0.18)
        bursts, knocks = [(0.55, 0.9), (1.05, 1.4)], []
        off_img, on_img = PH2_OFF, PH2_ON
    else:
        on = 1.0
        bursts, knocks = [(0.72, 1.02), (1.17, 1.47)], S5_KNOCKS
        off_img, on_img = PH5_ON, PH5_ON
    dx = 0
    for a, b in bursts:
        if a <= t < b: dx = int(round(6 * math.sin(2 * math.pi * 32 * t)))
    base = ROOM + on * ROOM_GLOW
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    ph = on_img if on >= 1 else (off_img if on <= 0 else Image.blend(off_img, on_img, on))
    im.paste(ph, (dx, 0), ph)
    if scene == 2:
        if t >= 0.9:
            p = eo((t - 0.9) / 0.35)
            comp(im, N1, (NX + dx, NY - (1 - p) * 60), p)
    else:
        p = eo((t - 0.75) / 0.4) if t >= 0.75 else 0.0
        comp(im, N1, (NX + dx, NY + p * (N2H + 18)), 1.0)
        if p > 0: comp(im, N2, (NX + dx, NY - (1 - p) * 60), p)
    sy = shake(t, knocks, 9)
    if sy:
        im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = apply_mult(im, MULT_SCRIM)
    (S2_CAP if scene == 2 else S5_CAP).draw(im, t)
    return im.convert('RGB')

def frame_s2(t): return frame_phone(t, 2)
def frame_s5(t): return frame_phone(t, 5)

# ---------------------------------------------------------------- scene 3: the door
def build_s3_bg():
    w, h = W * S, H * S
    img = vgrad(w, h, (34, 29, 40), (17, 15, 22), 0, 1240 * S)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 54):
        d.rectangle(P(x, 0, x + 2, 1220), fill=(38, 33, 45))
    d.rectangle(P(96, 470, 236, 650), fill=(52, 40, 34)); d.rectangle(P(110, 484, 222, 636), fill=(28, 30, 40))
    d.polygon(P(110, 636, 160, 560, 190, 600, 222, 566, 222, 636), fill=(42, 46, 58))
    img.paste(vgrad(w, (H - 1240) * S, (36, 28, 25), (9, 7, 7)), (0, 1240 * S)); d = ImageDraw.Draw(img)
    yy, k = 1240, 0
    while yy < H:
        k += 1; yy += int(16 + k * k * 3)
        d.line(P(0, yy, W, yy), fill=(20, 15, 14), width=2 * S)
    d.rectangle(P(0, 1214, W, 1242), fill=(28, 24, 30)); d.line(P(0, 1215, W, 1215), fill=(52, 46, 56), width=2 * S)
    d.rectangle(P(258, 236, 822, 1242), fill=(48, 35, 29))
    d.rectangle(P(270, 248, 810, 1242), fill=(40, 29, 24))
    d.rectangle(P(296, 276, 784, 1242), fill=(5, 5, 8))
    return img

def door_light(img, feet):
    def line(d):
        d.rectangle(P(300, 1234, 780, 1246), fill=255)
        if feet:
            d.rectangle(P(452, 1228, 512, 1252), fill=0); d.rectangle(P(568, 1228, 628, 1252), fill=0)
    img = glow(img, line, (150, 180, 235), 2 * S)
    def fan(d):
        d.polygon(P(300, 1246, 780, 1246, 900, 1470, 180, 1470), fill=120)
        if feet:
            d.polygon(P(452, 1246, 512, 1246, 545, 1470, 425, 1470), fill=0)
            d.polygon(P(568, 1246, 628, 1246, 655, 1470, 545, 1470), fill=0)
    img = glow(img, fan, (60, 76, 112), 20 * S)
    return down(img)

def build_door():
    im = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle(P(300, 280, 780, 1232), fill=(70, 46, 34, 255))
    rng = random.Random(3)
    for _ in range(70):
        x = rng.uniform(304, 776)
        d.line(P(x, 284, x + rng.uniform(-4, 4), 1228), fill=(63, 41, 30, 255), width=S)
    for (a, b, c, e) in [(342, 330, 522, 700), (558, 330, 738, 700), (342, 760, 522, 1186), (558, 760, 738, 1186)]:
        d.rectangle(P(a, b, c, e), fill=(56, 37, 27, 255))
        d.line(P(a, b, c, b), fill=(38, 24, 18, 255), width=5 * S); d.line(P(a, b, a, e), fill=(38, 24, 18, 255), width=5 * S)
        d.line(P(a, e, c, e), fill=(92, 64, 46, 255), width=4 * S); d.line(P(c, b, c, e), fill=(92, 64, 46, 255), width=4 * S)
        d.rectangle(P(a + 22, b + 22, c - 22, e - 22), fill=(66, 44, 32, 255))
        d.line(P(a + 22, b + 22, c - 22, b + 22), fill=(86, 60, 44, 255), width=3 * S)
        d.line(P(a + 22, b + 22, a + 22, e - 22), fill=(86, 60, 44, 255), width=3 * S)
    d.ellipse(P(714, 906, 762, 954), fill=(70, 52, 30, 255))
    d.ellipse(P(721, 913, 755, 947), fill=(176, 136, 76, 255))
    d.ellipse(P(728, 918, 740, 928), fill=(232, 204, 146, 255))
    d.ellipse(P(726, 838, 750, 862), fill=(150, 116, 66, 255)); d.rectangle(P(736, 844, 740, 856), fill=(60, 44, 26, 255))
    d.ellipse(P(531, 551, 549, 569), fill=(150, 120, 80, 255)); d.ellipse(P(535, 555, 545, 565), fill=(10, 10, 14, 255))
    im = down(im)
    a = np.asarray(im).astype(np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    shade = np.clip(1.0 - 0.28 * np.clip((yy - 0.15) / 0.5, 0, 1), 0, 1)
    xx = np.arange(W)[None, :]
    edge = 1.0 - 0.22 * np.exp(-((xx - 300) / 30) ** 2) - 0.22 * np.exp(-((xx - 780) / 30) ** 2)
    a[..., :3] *= (shade * edge)[..., None]
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

S3_DUR = 5.5
S3_KNOCKS = [1.5, 1.85, 2.2]
TOC_POS = [(155, 560, -9), (905, 470, 8), (170, 930, -6)]
def setup_s3():
    global S3_A, S3_B, S3_DOOR, TOCS, S3_CAP
    bg = build_s3_bg()
    S3_A, S3_B = door_light(bg, False), door_light(bg, True)
    S3_DOOR = build_door()
    f = F('InterDisplay-Black', 104)
    asc, desc = f.getmetrics()
    base = Image.new('RGBA', (int(f.getlength('TOC')) + 40, asc + desc + 40), (0, 0, 0, 0))
    ImageDraw.Draw(base).text((20, 20), 'TOC', font=f, fill=WHITE, stroke_width=7, stroke_fill=INK)
    TOCS = [base.rotate(r, resample=Image.BICUBIC, expand=True) for (_, _, r) in TOC_POS]
    S3_CAP = Caption([(0.2, S3_DUR, [(0.25, 'Três segundos depois…', WHITE),
                                      (1.3, 'alguém bateu na porta.', WHITE)])])

def frame_s3(t):
    feet = eo((t - 3.0) / 0.6) if t > 3.0 else 0.0
    bg = S3_A if feet <= 0 else Image.blend(S3_A, S3_B, feet)
    im = bg.convert('RGBA')
    ddx = shake(t, S3_KNOCKS, 8, freq=20, tau=0.06)
    im.paste(S3_DOOR, (ddx, 0), S3_DOOR)
    sy = shake(t, S3_KNOCKS, 6)
    if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = apply_mult(im, MULT_SCRIM)
    for k, (cx, cy, _), toc in zip(S3_KNOCKS, TOC_POS, TOCS):
        dt = t - k
        if 0 <= dt < 1.0:
            s = lerp(1.35, 1.0, eo(dt / 0.12))
            a = 1.0 if dt < 0.5 else 1.0 - eio((dt - 0.5) / 0.45)
            img = toc.resize((int(toc.width * s), int(toc.height * s)), Image.BILINEAR)
            comp(im, img, (cx - img.width / 2, cy - img.height / 2), a)
    S3_CAP.draw(im, t)
    return im.convert('RGB')

# ---------------------------------------------------------------- scene 4: the window
G = (150, 250, 930, 1170)

def build_exterior(phone_on):
    w, h = W * S, H * S
    img = vgrad(w, h, (5, 8, 22), (30, 36, 66), 250 * S, 930 * S)
    img = glow(img, lambda d: d.ellipse(P(360, 660, 940, 1010), fill=120), (40, 40, 62), 60 * S)
    d = ImageDraw.Draw(img)
    rng = random.Random(11); x = 140
    while x < 940:
        bw = rng.randint(50, 110); bh = rng.randint(60, 190)
        d.rectangle(P(x, 930 - bh, x + bw, 930), fill=(15, 19, 37)); x += bw + rng.randint(-6, 4)
    d.rectangle(P(150, 800, 420, 935), fill=(12, 15, 30)); d.polygon(P(140, 800, 285, 700, 430, 800), fill=(10, 12, 26))
    d.rectangle(P(205, 840, 255, 890), fill=(24, 22, 30))
    d.rectangle(P(830, 820, 960, 935), fill=(12, 15, 30)); d.polygon(P(815, 820, 900, 750, 975, 820), fill=(10, 12, 26))
    img.paste(vgrad(w, (1170 - 955) * S, (15, 16, 26), (9, 10, 16)), (0, 955 * S)); d = ImageDraw.Draw(img)
    d.rectangle(P(0, 932, W, 956), fill=(24, 26, 40)); d.rectangle(P(0, 956, W, 960), fill=(36, 38, 54))
    for x in range(100, 1000, 120): d.rectangle(P(x, 1070, x + 64, 1076), fill=(34, 36, 48))
    d.rectangle(P(696, 570, 704, 948), fill=(18, 20, 30))
    d.line(P(700, 574, 680, 560, 640, 558), fill=(18, 20, 30), width=5 * S)
    d.polygon(P(622, 552, 660, 552, 654, 566, 628, 566), fill=(24, 26, 38))
    img = glow(img, lambda d: d.polygon(P(634, 566, 648, 566, 770, 950, 512, 950), fill=150), (120, 92, 52), 14 * S)
    img = glow(img, lambda d: d.ellipse(P(500, 932, 790, 968), fill=210), (130, 104, 62), 10 * S)
    img = glow(img, lambda d: d.ellipse(P(620, 552, 662, 584), fill=255), (255, 214, 140), 10 * S)
    d = ImageDraw.Draw(img); d.ellipse(P(630, 562, 652, 572), fill=(255, 236, 190))
    img = glow(img, lambda d: d.rectangle(P(615, 965, 670, 1165), fill=100), (90, 70, 40), 14 * S)
    d = ImageDraw.Draw(img); c = (4, 4, 8)
    d.ellipse(P(638, 808, 662, 834), fill=c)
    d.rectangle(P(644, 830, 656, 846), fill=c)
    d.polygon(P(622, 852, 632, 843, 668, 843, 678, 852, 679, 900, 673, 928, 627, 928, 621, 900), fill=c)
    d.rectangle(P(636, 926, 647, 952), fill=c); d.rectangle(P(653, 926, 664, 952), fill=c)
    if phone_on:
        img = glow(img, lambda d: d.ellipse(P(622, 842, 680, 900), fill=255), (80, 110, 180), 10 * S)
        img = glow(img, lambda d: d.ellipse(P(640, 820, 662, 840), fill=110), (70, 90, 140), 3 * S)
        d = ImageDraw.Draw(img); d.rectangle(P(646, 862, 655, 875), fill=(210, 230, 255))
    return img

def curtain_poly(left):
    pts = [(30, 188), (252, 188)]
    for y in range(188, 1331, 30):
        pts.append((238 + 14 * math.sin(y / 90.0), y))
    pts.append((30, 1330))
    if not left: pts = [(W - x, y) for x, y in pts]
    return pts

def build_s4(phone_on):
    w, h = W * S, H * S
    img = vgrad(w, h, (17, 16, 26), (8, 8, 13))
    img = glow(img, lambda d: d.rectangle(P(110, 210, 970, 1230), fill=255), (22, 26, 46), 50 * S)
    ext = build_exterior(phone_on)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rectangle(P(*G), fill=255)
    img.paste(ext, (0, 0), m)
    rng = random.Random(5)
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for _ in range(170):
        x = rng.uniform(155, 925); y = rng.uniform(255, 1165); r = rng.uniform(1.5, 5)
        dl.ellipse(P(x - r, y - r * 1.2, x + r, y + r * 1.2), fill=(150, 165, 200, rng.randint(25, 70)))
        dl.ellipse(P(x - r * 0.4, y - r * 0.7, x + r * 0.1, y - r * 0.2), fill=(220, 230, 255, rng.randint(40, 90)))
    for _ in range(14):
        x = rng.uniform(160, 920); y = rng.uniform(260, 900); L = rng.uniform(60, 220)
        dl.line(P(x, y, x + rng.uniform(-3, 3), y + L), fill=(150, 165, 200, 40), width=2 * S)
    img = Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')
    d = ImageDraw.Draw(img); fr = (33, 30, 40)
    d.rectangle(P(126, 226, 954, 250), fill=fr); d.rectangle(P(126, 1170, 954, 1194), fill=fr)
    d.rectangle(P(126, 226, 150, 1194), fill=fr); d.rectangle(P(930, 226, 954, 1194), fill=fr)
    d.rectangle(P(531, 250, 549, 1170), fill=fr); d.rectangle(P(150, 701, 930, 719), fill=fr)
    d.rectangle(P(100, 1194, 980, 1232), fill=(46, 42, 52)); d.line(P(100, 1195, 980, 1195), fill=(74, 68, 82), width=3 * S)
    for left in (True, False):
        pts = curtain_poly(left)
        d.polygon([tuple(P(x, y)) for x, y in pts], fill=(46, 34, 56))
    folds = [70, 120, 175, 215]
    img = fill_mask(img, lambda d: [d.rectangle(P(x - 5, 200, x + 5, 1320), fill=255) for x in folds + [W - f for f in folds]],
                    (30, 22, 38), blur=6 * S)
    d = ImageDraw.Draw(img)
    d.rectangle(P(20, 176, 1060, 190), fill=(30, 28, 34))
    d.ellipse(P(8, 170, 34, 196), fill=(30, 28, 34)); d.ellipse(P(1046, 170, 1072, 196), fill=(30, 28, 34))
    return img

def build_s4_mask():
    m = Image.new('L', (W * S, H * S), 0); d = ImageDraw.Draw(m)
    d.rectangle(P(*G), fill=255)
    d.rectangle(P(531, 250, 549, 1170), fill=0); d.rectangle(P(150, 701, 930, 719), fill=0)
    for left in (True, False):
        d.polygon([tuple(P(x, y)) for x, y in curtain_poly(left)], fill=0)
    return m

S4_DUR = 7.5
S4_KNOCKS = [5.4, 5.75]
S4_PHONE = 3.45
def setup_s4():
    global S4_OFF, S4_ON, S4_MASK, S4_RAIN, S4_CAP
    S4_OFF, S4_ON = build_s4(False), build_s4(True)
    S4_MASK = build_s4_mask()
    S4_RAIN = Rain(4, RAIN_GLASS)
    S4_CAP = Caption([(0.2, 1.7, [(0.25, 'Ela espiou pela janela.', WHITE)]),
                      (1.85, S4_DUR, [(1.9, 'Tinha alguém parado embaixo do poste.', WHITE),
                                      (3.75, 'Mexendo no celular.', WARM)])])

def frame_s4(t):
    z = 1 + 0.22 * eio(t / S4_DUR)
    fx, fy = 650 * S, 880 * S
    l, tp = fx * (1 - 1 / z), fy * (1 - 1 / z)
    box = (l, tp, l + W * S / z, tp + H * S / z)
    lvl = eo((t - S4_PHONE) / 0.25) if t > S4_PHONE else 0.0
    if lvl <= 0: im = S4_OFF.resize((W, H), Image.BILINEAR, box=box)
    elif lvl >= 1: im = S4_ON.resize((W, H), Image.BILINEAR, box=box)
    else: im = Image.blend(S4_OFF.resize((W, H), Image.BILINEAR, box=box), S4_ON.resize((W, H), Image.BILINEAR, box=box), lvl)
    mask = S4_MASK.resize((W, H), Image.BILINEAR, box=box)
    rain = S4_RAIN.layer(t)
    rain.putalpha(ImageChops.multiply(rain.getchannel('A'), mask))
    im = im.convert('RGBA'); im.alpha_composite(rain)
    sy = shake(t, S4_KNOCKS, 3)
    if sy: im = Image.fromarray(np.roll(np.asarray(im), sy, axis=0))
    im = apply_mult(im, MULT_SCRIM)
    S4_CAP.draw(im, t)
    return im.convert('RGB')

# ---------------------------------------------------------------- scene 6: the choice
def build_s6():
    w, h = W * S, H * S
    img = vgrad(w, h, (5, 6, 16), (28, 10, 22))
    img = glow(img, lambda d: d.ellipse(P(100, 1380, 980, 2150), fill=150), (60, 18, 30), 80 * S)
    d = ImageDraw.Draw(img); hc = (9, 8, 16)
    d.rectangle(P(660, 1440, 700, 1500), fill=hc)
    d.polygon(P(255, 1590, 540, 1400, 825, 1590), fill=(8, 7, 14))
    d.rectangle(P(300, 1590, 780, 1920), fill=hc)
    img = glow(img, lambda d: d.rectangle(P(415, 1635, 585, 1775), fill=255), (110, 64, 24), 30 * S)
    img.paste(vgrad(130 * S, 100 * S, (255, 206, 120), (226, 146, 66)), tuple(P(435, 1655)))
    d = ImageDraw.Draw(img)
    d.rectangle(P(496, 1655, 504, 1755), fill=hc); d.rectangle(P(435, 1701, 565, 1709), fill=hc)
    for x in range(-10, W + 20, 26):
        d.rectangle(P(x, 1838, x + 11, 1920), fill=(6, 5, 11))
        d.polygon(P(x, 1838, x + 5.5, 1828, x + 11, 1838), fill=(6, 5, 11))
    d.rectangle(P(-10, 1856, W, 1862), fill=(6, 5, 11))
    return down(img)

def card(letter, text, fill, circ, letter_col, text_col, w=900, h=180):
    im = Image.new('RGBA', ((w + 60) * S, (h + 60) * S), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle(P(30, 42, 30 + w, 42 + h), radius=40 * S, fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(14 * S))
    im.paste((0, 0, 0, 255), (0, 0), sh)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(P(30, 30, 30 + w, 30 + h), radius=40 * S, fill=fill)
    cx, cy = 30 + 40 + 55, 30 + h / 2
    d.ellipse(P(cx - 55, cy - 55, cx + 55, cy + 55), fill=circ)
    d.text(P(cx, cy + 2), letter, font=F('InterDisplay-Black', 66 * S), fill=letter_col, anchor='mm')
    d.text(P(cx + 55 + 34, cy + 2), text, font=F('InterDisplay-ExtraBold', 60 * S), fill=text_col, anchor='lm')
    return down(im)

S6_DUR = 8.5
def setup_s6():
    global S6_BG, S6_RAIN, S6_TITLE, CARD_A, CARD_B, CTA, SUB
    S6_BG = build_s6()
    S6_RAIN = Rain(6, RAIN_OUT)
    S6_TITLE = Caption([(0.1, S6_DUR + 5, [(0.15, 'O QUE A LIA FAZ?', WHITE)])],
                       font=('InterDisplay-Black', 92), top=380, maxw=1000, gap=0.11)
    CARD_A = card('A', 'Abrir a porta', WARM, (30, 20, 8), WARM, (30, 20, 8))
    CARD_B = card('B', 'Fugir pelos fundos', RED, (64, 10, 14), (255, 228, 228), WHITE)
    CTA = rich_line([('Comenta ', WHITE), ('A', WARM), (' ou ', WHITE), ('B', RED)], F('InterDisplay-ExtraBold', 74))
    SUB = rich_line([('O mais votado vira o episódio 2', (204, 204, 216))], F('Inter-Medium', 40), stroke=4)

def frame_s6(t):
    im = S6_BG.convert('RGBA')
    im.alpha_composite(S6_RAIN.layer(t))
    im = apply_mult(im, MULT_VIG)
    comp(im, KICKER, ((W - KICKER.width) // 2, 210))
    S6_TITLE.draw(im, t)
    for (img, y, t0, side, phase) in [(CARD_A, 560, 0.75, -1, 0.0), (CARD_B, 790, 1.1, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45)
        x = (W - img.width) / 2 + side * (1 - p) * 140
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.8) / 1.5 + phase) if t > 2.8 else 1.0
        im2 = img if abs(s - 1) < 1e-3 else img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
        comp(im, im2, (x + img.width / 2 - im2.width / 2, y + img.height / 2 - im2.height / 2), p)
    if t >= 1.9:
        p = eo((t - 1.9) / 0.4)
        comp(im, CTA, ((W - CTA.width) / 2, 1065 + (1 - p) * 24), p)
    if t >= 2.3:
        p = eo((t - 2.3) / 0.4)
        comp(im, SUB, ((W - SUB.width) / 2, 1175 + (1 - p) * 18), p)
    return im.convert('RGB')

# ---------------------------------------------------------------- assembly
SCENES = [('s1', S1_DUR, frame_s1, True), ('s2', S2_DUR, frame_s2, True), ('s3', S3_DUR, frame_s3, True),
          ('s4', S4_DUR, frame_s4, True), ('s5', S5_DUR, frame_s5, True), ('s6', S6_DUR, frame_s6, False)]

def setup():
    global MULT_SCRIM, MULT_VIG, KICKER
    MULT_SCRIM = make_mult(0.55, True)
    MULT_VIG = make_mult(0.55, False)
    KICKER = build_kicker()
    setup_s1(); setup_phone(); setup_s3(); setup_s4(); setup_s6()

def encode_scene(name, dur, fn, fade_out, fade=5):
    n = int(round(dur * FPS))
    tmp, final = f'{WORK}/{name}.part.mp4', f'{WORK}/{name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
           '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        a = np.asarray(fn(i / FPS), dtype=np.uint8)
        k = 1.0
        if i < fade: k = min(k, (i + 1) / (fade + 1))
        if fade_out and i >= n - fade: k = min(k, (n - i) / (fade + 1))
        if k < 1: a = (a.astype(np.float32) * k).astype(np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, final)
        print(f'{name}: {n} frames in {time.time() - t0:.1f}s', flush=True)
    else:
        sys.exit(f'ffmpeg failed on {name}')

# ---------------------------------------------------------------- audio
def make_audio(path):
    sr = 44100
    starts, acc = {}, 0.0
    for name, dur, _, _ in SCENES:
        starts[name] = acc; acc += int(round(dur * FPS)) / FPS
    total = acc
    n = int(total * sr)
    t = np.arange(n) / sr
    out = np.zeros((n, 2), np.float64)
    f = np.fft.rfftfreq(n, 1 / sr)
    resp = 1 / (1 + (350 / np.maximum(f, 1)) ** 2) / (1 + (f / 5200) ** 2)
    for ch in range(2):
        x = np.random.default_rng(10 + ch).standard_normal(n)
        x = np.fft.irfft(np.fft.rfft(x) * resp, n)
        x /= np.abs(x).max()
        s1, s2, s3, s4, s5, s6 = (starts[k] for k in ('s1', 's2', 's3', 's4', 's5', 's6'))
        kp = [(0, 0), (0.4, .46), (s2 - .1, .46), (s2 + .1, .16), (s4 - .1, .16), (s4 + .1, .28),
              (s5 - .1, .28), (s5 + .1, .16), (s6 - .1, .16), (s6 + .1, .40), (total, .40)]
        out[:, ch] += x * np.interp(t, [a for a, _ in kp], [b for _, b in kp])
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 110.4 * t + 1) +
             0.45 * np.sin(2 * np.pi * 164.8 * t + 2) + 0.25 * np.sin(2 * np.pi * 220.9 * t + .5))
    drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.21 * t)
    dg = np.interp(t, [0, 1.0, starts['s5'], starts['s6'], total], [0, 0.05, 0.085, 0.10, 0.10])
    out += (drone * dg)[:, None]
    rng = np.random.default_rng(3)

    def add(sig, at, pan=0.0):
        i = int(at * sr); j = min(n, i + len(sig))
        if i >= n: return
        out[i:j, 0] += sig[:j - i] * (1 - pan); out[i:j, 1] += sig[:j - i] * (1 + pan)

    def buzz(dur):
        tt = np.arange(int(dur * sr)) / sr
        env = np.minimum(1, tt / 0.01) * np.minimum(1, (dur - tt) / 0.03)
        return np.tanh(2.5 * np.sin(2 * np.pi * 172 * tt)) * env * 0.16

    def knock(g, dark=False):
        L = int(0.4 * sr); tt = np.arange(L) / sr
        k = (np.sin(2 * np.pi * 88 * tt) * np.exp(-tt / 0.11) + 0.7 * np.sin(2 * np.pi * 142 * tt) * np.exp(-tt / 0.07)
             + 0.55 * np.sin(2 * np.pi * 235 * tt) * np.exp(-tt / 0.045))
        click = rng.standard_normal(L) * np.exp(-tt / 0.006) * (0.12 if dark else 0.5)
        return (k + click) * g

    for a, b in [(0.55, 0.9), (1.05, 1.4)]: add(buzz(b - a), starts['s2'] + a)
    for a, b in [(0.72, 1.02), (1.17, 1.47)]: add(buzz(b - a), starts['s5'] + a)
    for k in S3_KNOCKS: add(knock(0.62), starts['s3'] + k)
    for k in S4_KNOCKS: add(knock(0.26, dark=True), starts['s4'] + k)
    for k in S5_KNOCKS: add(knock(0.7), starts['s5'] + k)
    L = int(3.0 * sr); tt = np.arange(L) / sr
    fr = 38 + 52 * np.exp(-tt / 0.25)
    boom = np.sin(2 * np.pi * np.cumsum(fr) / sr) * np.exp(-tt / 0.9) * 0.6
    boom += np.sin(2 * np.pi * 2 * np.cumsum(fr) / sr) * np.exp(-tt / 0.5) * 0.25
    add(boom, starts['s6'])
    fade = np.clip((total - t) / 0.8, 0, 1)
    out *= fade[:, None]
    out *= 0.89 / np.abs(out).max()
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())
    return total

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    t0 = time.time(); setup(); print(f'setup {time.time() - t0:.1f}s', flush=True)
    if mode == 'preview':
        shots = [(frame_s1, 3.2), (frame_s2, 2.5), (frame_s3, 2.0), (frame_s3, 4.6),
                 (frame_s4, 5.0), (frame_s5, 5.0), (frame_s6, 4.0)]
        thumbs = []
        for i, (fn, tt) in enumerate(shots):
            t1 = time.time(); im = fn(tt); dt = time.time() - t1
            im.save(f'{WORK}/prev_{i}.png'); print(f'prev_{i}: {dt * 1000:.0f} ms', flush=True)
            thumbs.append(im.resize((W // 3, H // 3), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 3 * 4, H // 3 * 2), (0, 0, 0))
        for i, th in enumerate(thumbs): sheet.paste(th, ((i % 4) * (W // 3), (i // 4) * (H // 3)))
        sheet.save(f'{WORK}/sheet.png')
    else:
        only = sys.argv[2:] if len(sys.argv) > 2 else None
        for name, dur, fn, fo in SCENES:
            if only and name not in only: continue
            encode_scene(name, dur, fn, fo)
