#!/usr/bin/env python3
"""A Marmita Sumiu — Episódio 1. Vertical 1080x1920, 30 fps, flat comedy."""
import os, sys, math, random, time, subprocess, wave, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/video')
import make as M
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, tracked, rich_line, WHITE, INK

W, H, FPS, S = 1080, 1920, 30, 2
WORK = '/home/claude/lunch'
CAVEAT = WORK + '/fontpkg/package/files/caveat-latin-700-normal.woff'
YEL = (255, 204, 77)
A_COL, B_COL = M.WARM, M.RED

def backout(x, c1=1.70158):
    x = clamp(x); c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def mix(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

def make_vig(strength=0.35, cx=0.5, cy=0.45):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (x / W - cx) * 2; dy = (y / H - cy) * 2 * 0.75
    r = np.sqrt(dx * dx + dy * dy)
    v = 1 - strength * np.clip((r - 0.55) / 0.8, 0, 1) ** 1.5
    return v[..., None].astype(np.float32)

def apply_vig(im, v):
    a = np.asarray(im.convert('RGB'), np.float32) * v
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')

# ---------------------------------------------------------------- shared pieces
def build_kicker(text='A MARMITA SUMIU  ·  EP. 1'):
    txt = tracked(text, F('Inter-Bold', 30), (250, 250, 252, 255), 5)
    h = 64; w = txt.width + 66
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=h * S // 2, fill=(22, 24, 34, 225))
    d.ellipse(P(24, 24, 40, 40), fill=YEL)
    im = down(im)
    im.alpha_composite(txt, (46, 4))
    return im

CW, CH = 600, 920
def person(kind):
    im = Image.new('RGBA', (CW * S, CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx, hy, r = 300, 240, 105
    if kind == 'leo':
        skin, shirt, pants, shoe, hair, tw = (158, 104, 70), (70, 182, 122), (54, 80, 150), (246, 246, 248), (32, 24, 22), 250
    elif kind == 'ju':
        skin, shirt, pants, shoe, hair, tw = (242, 200, 166), (132, 92, 206), (30, 96, 112), (214, 64, 76), (112, 60, 40), 230
    else:
        skin, shirt, pants, shoe, hair, tw = (222, 164, 124), (246, 246, 250), (80, 86, 104), (92, 58, 38), (178, 178, 186), 290
    dark = mix(skin, (60, 30, 20), 0.25)
    line = (196, 200, 212)
    ink = (28, 24, 30)
    # legs
    if kind == 'ju':
        for x0 in (hx - 62, hx + 22):
            d.rounded_rectangle(P(x0, 700, x0 + 40, 862), radius=18 * S, fill=skin)
    else:
        top = 700 if kind == 'carlos' else 650
        d.rounded_rectangle(P(hx - 78, top, hx - 10, 862), radius=22 * S, fill=pants)
        d.rounded_rectangle(P(hx + 10, top, hx + 78, 862), radius=22 * S, fill=pants)
    d.ellipse(P(hx - 100, 838, hx - 6, 888), fill=shoe); d.ellipse(P(hx + 6, 838, hx + 100, 888), fill=shoe)
    # torso
    if kind == 'carlos':
        for grow, col in ((4, line), (0, shirt)):
            d.rounded_rectangle(P(hx - tw / 2 - grow, 360 - grow, hx + tw / 2 + grow, 712 + grow), radius=80 * S, fill=col)
            d.ellipse(P(hx - 168 - grow, 440 - grow, hx + 168 + grow, 718 + grow), fill=col)
        d.rectangle(P(hx - 92, 692, hx + 92, 714), fill=(70, 44, 30))
        d.rounded_rectangle(P(hx - 20, 688, hx + 20, 716), radius=4 * S, fill=(214, 180, 90))
    else:
        bot = 640 if kind == 'ju' else 690
        d.rounded_rectangle(P(hx - tw / 2, 360, hx + tw / 2, bot), radius=80 * S, fill=shirt)
    if kind == 'ju':
        d.polygon(P(hx - 118, 600, hx + 118, 600, hx + 142, 762, hx - 142, 762), fill=pants)
    # arms
    for sx in (-1, 1):
        xo = hx + sx * (tw / 2 + (40 if kind == 'carlos' else 20))
        if kind == 'leo':
            d.rounded_rectangle(P(xo - 26, 400, xo + 26, 612), radius=26 * S, fill=skin)
            d.rounded_rectangle(P(xo - 30, 372, xo + 30, 470), radius=28 * S, fill=shirt)
        elif kind == 'carlos':
            d.rounded_rectangle(P(xo - 28, 380, xo + 28, 612), radius=26 * S, fill=shirt, outline=line, width=4 * S)
        else:
            d.rounded_rectangle(P(xo - 26, 380, xo + 26, 612), radius=26 * S, fill=shirt)
        d.ellipse(P(xo - 30, 592, xo + 30, 652), fill=skin)
    d.rectangle(P(hx - 26, 318, hx + 26, 372), fill=dark)
    if kind == 'carlos':
        d.polygon(P(hx - 42, 352, hx, 390, hx - 8, 412, hx - 56, 380), fill=(252, 252, 254), outline=line, width=3 * S)
        d.polygon(P(hx + 42, 352, hx, 390, hx + 8, 412, hx + 56, 380), fill=(252, 252, 254), outline=line, width=3 * S)
        d.polygon(P(hx - 17, 382, hx + 17, 382, hx + 12, 410, hx - 12, 410), fill=(40, 70, 160))
        d.polygon(P(hx - 12, 408, hx + 12, 408, hx + 30, 612, hx, 652, hx - 30, 612), fill=(48, 82, 176))
        sc = (206, 44, 40)
        for (cx, cy, rr) in [(hx + 4, 520, 17), (hx - 8, 530, 11), (hx + 14, 536, 9)]:
            d.ellipse(P(cx - rr, cy - rr, cx + rr, cy + rr), fill=sc)
        d.ellipse(P(hx + 1, 538, hx + 11, 570), fill=sc)
        d.rectangle(P(hx + 56, 420, hx + 104, 474), outline=line, width=3 * S)
        d.rounded_rectangle(P(hx + 66, 402, hx + 74, 442), radius=3 * S, fill=(40, 70, 160))
    if kind == 'ju':
        d.line(P(hx - 34, 366, hx - 14, 500), fill=(60, 160, 230), width=6 * S)
        d.line(P(hx + 34, 366, hx + 14, 500), fill=(60, 160, 230), width=6 * S)
        d.rounded_rectangle(P(hx - 42, 494, hx + 42, 566), radius=8 * S, fill=(252, 252, 254))
        d.text(P(hx, 531), 'RH', font=F('InterDisplay-Black', 34 * S), fill=(132, 92, 206), anchor='mm')
    # head
    if kind == 'ju':
        d.rounded_rectangle(P(hx - r - 16, hy - 40, hx - r + 44, hy + 150), radius=26 * S, fill=hair)
        d.rounded_rectangle(P(hx + r - 44, hy - 40, hx + r + 16, hy + 150), radius=26 * S, fill=hair)
    else:
        for sx in (-1, 1):
            d.ellipse(P(hx + sx * r - 24, hy - 14, hx + sx * r + 24, hy + 38), fill=skin)
    d.ellipse(P(hx - r, hy - r, hx + r, hy + r + 6), fill=skin)
    if kind == 'leo':
        for a in range(195, 350, 22):
            ar = math.radians(a); cx = hx + (r - 6) * math.cos(ar); cy = hy - 12 + (r - 6) * math.sin(ar)
            d.ellipse(P(cx - 40, cy - 40, cx + 40, cy + 40), fill=hair)
        for (cx, cy, rr) in [(hx - 50, hy - r + 6, 46), (hx, hy - r - 6, 50), (hx + 50, hy - r + 6, 46)]:
            d.ellipse(P(cx - rr, cy - rr, cx + rr, cy + rr), fill=hair)
    elif kind == 'ju':
        d.line(P(hx + 22, hy - r - 112, hx + 74, hy - r - 36), fill=(250, 200, 60), width=12 * S)
        d.line(P(hx + 66, hy - r - 48, hx + 74, hy - r - 36), fill=(240, 150, 160), width=12 * S)
        d.ellipse(P(hx - 58, hy - r - 92, hx + 58, hy - r + 16), fill=hair)
        d.pieslice(P(hx - r - 10, hy - r - 14, hx + r + 10, hy + r - 44), 180, 360, fill=hair)
    else:
        for sx in (-1, 1):
            d.ellipse(P(hx + sx * (r - 12) - 24, hy - 46, hx + sx * (r - 12) + 24, hy + 16), fill=hair)
        d.ellipse(P(hx - 56, hy - r + 16, hx - 12, hy - r + 40), fill=mix(skin, (255, 255, 255), 0.4))
    # eyes
    ey = hy + 4
    pdx, pdy = {'leo': (0, -2), 'ju': (-10, 0), 'carlos': (9, 3)}[kind]
    for sx in (-1, 1):
        ex = hx + sx * 40
        d.ellipse(P(ex - 22, ey - 27, ex + 22, ey + 27), fill=(255, 255, 255))
        d.ellipse(P(ex - 12 + pdx, ey - 12 + pdy, ex + 12 + pdx, ey + 12 + pdy), fill=ink)
        d.ellipse(P(ex - 7 + pdx, ey - 8 + pdy, ex - 1 + pdx, ey - 2 + pdy), fill=(255, 255, 255))
    if kind == 'ju':
        for sx in (-1, 1):
            ex = hx + sx * 40
            d.ellipse(P(ex - 34, ey - 34, ex + 34, ey + 34), outline=(54, 36, 72), width=7 * S)
        d.line(P(hx - 7, ey - 6, hx + 7, ey - 6), fill=(54, 36, 72), width=6 * S)
        d.arc(P(hx - 70, ey - 70, hx - 14, ey - 40), 200, 340, fill=(90, 48, 32), width=7 * S)
        d.arc(P(hx + 14, ey - 80, hx + 70, ey - 46), 200, 340, fill=(90, 48, 32), width=7 * S)
    if kind == 'carlos':
        d.line(P(hx - 66, ey - 34, hx - 18, ey - 46), fill=(150, 150, 158), width=11 * S)
        d.line(P(hx + 18, ey - 46, hx + 66, ey - 34), fill=(150, 150, 158), width=11 * S)
    d.ellipse(P(hx - 12, hy + 30, hx + 12, hy + 50), fill=dark)
    blush = mix(skin, (255, 110, 130), 0.35)
    if kind != 'carlos':
        d.ellipse(P(hx - 84, hy + 42, hx - 50, hy + 62), fill=blush)
        d.ellipse(P(hx + 50, hy + 42, hx + 84, hy + 62), fill=blush)
    # mouths
    if kind == 'leo':
        d.pieslice(P(hx - 40, hy + 48, hx + 40, hy + 100), 0, 180, fill=(110, 32, 44))
        d.ellipse(P(hx - 18, hy + 82, hx + 18, hy + 98), fill=(232, 106, 118))
    elif kind == 'ju':
        d.ellipse(P(hx + 12, hy + 66, hx + 36, hy + 92), fill=(120, 36, 50))
        d.ellipse(P(hx - 66, hy + 66, hx - 50, hy + 80), fill=(232, 140, 60))
        d.ellipse(P(hx - 46, hy + 80, hx - 38, hy + 88), fill=(214, 70, 50))
    else:
        d.rounded_rectangle(P(hx - 40, hy + 74, hx + 40, hy + 102), radius=8 * S, fill=(255, 255, 255), outline=(110, 32, 44), width=3 * S)
        d.line(P(hx - 38, hy + 88, hx + 38, hy + 88), fill=(190, 190, 198), width=2 * S)
        for x in (hx - 20, hx, hx + 20):
            d.line(P(x, hy + 76, x, hy + 100), fill=(190, 190, 198), width=2 * S)
        d.ellipse(P(hx - 50, hy + 50, hx + 2, hy + 78), fill=(120, 112, 108))
        d.ellipse(P(hx - 2, hy + 50, hx + 50, hy + 78), fill=(120, 112, 108))
    if kind in ('ju', 'carlos'):
        x, y = hx + r - 4, hy - 46
        d.polygon(P(x, y - 30, x - 15, y + 2, x + 15, y + 2), fill=(150, 210, 255))
        d.ellipse(P(x - 15, y - 12, x + 15, y + 18), fill=(150, 210, 255))
        d.ellipse(P(x - 7, y - 4, x - 1, y + 6), fill=(240, 250, 255))
    return down(im)

def sticker(sp, color=(255, 255, 255), grow=6):
    a = sp.getchannel('A')
    for _ in range(grow): a = a.filter(ImageFilter.MaxFilter(3))
    a = a.filter(ImageFilter.GaussianBlur(0.8))
    out = Image.new('RGBA', sp.size, (0, 0, 0, 0))
    sh = a.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.4))
    shl = Image.new('RGBA', sp.size, (30, 10, 20, 0)); shl.putalpha(sh)
    out.alpha_composite(shl, (0, 0), (0, 0, sp.width, sp.height - 14))
    out = Image.new('RGBA', sp.size, (0, 0, 0, 0)); out.paste(shl, (0, 14), shl)
    ol = Image.new('RGBA', sp.size, color + (0,)); ol.putalpha(a)
    out.alpha_composite(ol); out.alpha_composite(sp)
    return out

def head_portrait(sp, size=140):
    hx, hy = 300, 240
    crop = sp.crop((hx - 150, hy - 160, hx + 150, hy + 140)).resize((size * 4, size * 4), Image.LANCZOS)
    bg = Image.new('RGBA', crop.size, (255, 255, 255, 255)); bg.alpha_composite(crop)
    m = Image.new('L', crop.size, 0); ImageDraw.Draw(m).ellipse((0, 0, crop.width - 1, crop.height - 1), fill=255)
    bg.putalpha(m)
    ring = Image.new('RGBA', crop.size, (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, crop.width - 1, crop.height - 1), outline=(28, 22, 30, 255), width=16)
    bg.alpha_composite(ring)
    return bg.resize((size, size), Image.LANCZOS)

# ---------------------------------------------------------------- scene 1: kitchen
def build_s1():
    w, h = W * S, H * S
    img = vgrad(w, h, (255, 240, 210), (250, 224, 188), 0, 1300 * S)
    d = ImageDraw.Draw(img)
    for x in range(20, W, 92):
        d.rectangle(P(x, 0, x + 34, 1300), fill=(255, 246, 224))
    d.rectangle(P(0, 840, 560, 992), fill=(190, 230, 224))
    for x in range(0, 560, 52): d.line(P(x, 840, x, 992), fill=(168, 212, 206), width=2 * S)
    for y in range(840, 992, 38): d.line(P(0, y, 560, y), fill=(168, 212, 206), width=2 * S)
    d.rectangle(P(0, 990, 570, 1026), fill=(72, 72, 88))
    d.rectangle(P(0, 1026, 550, 1300), fill=(92, 172, 172))
    for x0 in (14, 284):
        d.rounded_rectangle(P(x0, 1046, x0 + 250, 1284), radius=10 * S, fill=(104, 186, 186))
        d.rounded_rectangle(P(x0 + 112, 1070, x0 + 138, 1082), radius=5 * S, fill=(60, 120, 120))
    d.rounded_rectangle(P(36, 856, 296, 990), radius=12 * S, fill=(222, 224, 232))
    d.rounded_rectangle(P(54, 874, 212, 972), radius=8 * S, fill=(44, 48, 66))
    d.rectangle(P(226, 880, 282, 910), fill=(20, 22, 28))
    d.text(P(254, 896), '12:01', font=F('Inter-Bold', 20 * S), fill=(110, 255, 150), anchor='mm')
    for y in (928, 952): d.ellipse(P(244, y - 8, 262, y + 10), fill=(170, 172, 184))
    d.polygon(P(368, 930, 452, 930, 442, 990, 378, 990), fill=(212, 112, 72))
    for (cx, cy, rx, ry) in [(392, 900, 22, 40), (428, 896, 22, 42), (410, 880, 18, 44), (380, 918, 24, 18), (440, 916, 24, 18)]:
        d.ellipse(P(cx - rx, cy - ry, cx + rx, cy + ry), fill=(80, 170, 90))
    # fridge
    d.rounded_rectangle(P(590, 432, 1010, 1302), radius=34 * S, fill=(150, 196, 190))
    d.rounded_rectangle(P(600, 430, 1000, 1300), radius=30 * S, fill=(205, 238, 232))
    d.rectangle(P(960, 460, 1000, 1270), fill=(188, 224, 218))
    d.line(P(600, 700, 1000, 700), fill=(170, 210, 204), width=4 * S)
    d.rounded_rectangle(P(624, 560, 646, 670), radius=8 * S, fill=(150, 165, 172))
    d.rounded_rectangle(P(624, 730, 646, 880), radius=8 * S, fill=(150, 165, 172))
    d.rectangle(P(800, 770, 930, 880), fill=(255, 255, 255))
    d.ellipse(P(852, 760, 878, 786), fill=(232, 70, 76))
    for (cx, cy) in [(846, 816), (884, 816)]: d.ellipse(P(cx - 18, cy - 18, cx + 18, cy + 18), fill=(236, 90, 110))
    d.polygon(P(830, 822, 900, 822, 865, 858), fill=(236, 90, 110))
    d.ellipse(P(730, 500, 766, 536), fill=(255, 196, 70)); d.ellipse(P(890, 600, 920, 630), fill=(70, 150, 230))
    # clock
    d.ellipse(P(742, 262, 858, 378), fill=(60, 60, 72)); d.ellipse(P(750, 270, 850, 370), fill=(255, 255, 255))
    for k in range(12):
        a = math.radians(k * 30); x = 800 + 40 * math.sin(a); y = 320 - 40 * math.cos(a)
        d.ellipse(P(x - 3, y - 3, x + 3, y + 3), fill=(80, 80, 90))
    d.line(P(800, 320, 800, 290), fill=(40, 40, 50), width=8 * S)
    d.line(P(800, 320, 804, 276), fill=(232, 70, 76), width=4 * S)
    d.ellipse(P(794, 314, 806, 326), fill=(40, 40, 50))
    # floor
    img.paste(vgrad(w, (H - 1300) * S, (52, 160, 160), (22, 92, 98)), (0, 1300 * S)); d = ImageDraw.Draw(img)
    yy, k = 1300, 0
    while yy < H:
        k += 1; yy += 20 + k * k * 4
        d.line(P(0, yy, W, yy), fill=(40, 132, 134), width=3 * S)
    for x in range(-400, W + 400, 140):
        d.line(P(540 + (x - 540) * 0.45, 1300, x, H), fill=(40, 132, 134), width=3 * S)
    d.rectangle(P(0, 1294, W, 1306), fill=(214, 190, 150))
    img = fill_soft(img, lambda d: d.ellipse(P(600, 1290, 1010, 1330), fill=255), (20, 70, 74), 10 * S, 0.6)
    return down(img).convert('RGBA')

def fill_soft(img, fn, color, blur, alpha):
    return M.fill_mask(img, fn, color, blur=blur, alpha=alpha)

def build_bubble():
    bw, bh = 520, 360
    im = Image.new('RGBA', (bw * S, bh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new('L', im.size, 0); ds = ImageDraw.Draw(sh)
    for b in [(24, 34, 454, 262), (196, 290, 232, 326), (168, 328, 190, 350)]: ds.ellipse(P(*b), fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(8 * S))
    im.paste((90, 60, 40, 255), (0, 0), sh)
    for b in [(20, 20, 450, 250), (192, 280, 228, 316), (166, 320, 188, 342)]: d.ellipse(P(*b), fill=(255, 255, 255))
    for (cx, cy, rr) in [(80, 70, 50), (380, 60, 46), (430, 160, 40), (60, 190, 40), (230, 30, 40)]:
        d.ellipse(P(cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 255, 255))
    d.rounded_rectangle(P(126, 92, 324, 208), radius=18 * S, fill=(236, 243, 247), outline=(186, 204, 214), width=4 * S)
    for i, y in enumerate(range(110, 198, 11)):
        d.rectangle(P(140, y, 310, y + 11), fill=(244, 196, 96) if i % 2 == 0 else (208, 64, 44))
    d.rectangle(P(140, 104, 310, 112), fill=(255, 226, 130))
    d.rounded_rectangle(P(116, 72, 334, 100), radius=10 * S, fill=(80, 150, 230))
    for x in (190, 230, 270):
        d.arc(P(x - 10, 30, x + 10, 50), 90, 270, fill=(200, 200, 210), width=4 * S)
        d.arc(P(x - 10, 48, x + 10, 68), 270, 450, fill=(200, 200, 210), width=4 * S)
    for (cx, cy) in [(358, 92), (386, 92)]: d.ellipse(P(cx - 16, cy - 16, cx + 16, cy + 16), fill=(236, 70, 90))
    d.polygon(P(343, 98, 401, 98, 372, 132), fill=(236, 70, 90))
    return down(im)

S1_DUR = 5.5
LEO_FEET = 1338
def setup_s1():
    global S1_BG, LEO, BUBBLE, FOOTSH
    S1_BG = build_s1()
    LEO = person('leo')
    BUBBLE = build_bubble()
    FOOTSH = Image.new('RGBA', (280, 60), (0, 0, 0, 0))
    m = Image.new('L', (280, 60), 0); ImageDraw.Draw(m).ellipse((20, 14, 260, 46), fill=120)
    FOOTSH.putalpha(m.filter(ImageFilter.GaussianBlur(8)))
    global HOOK
    f = F('InterDisplay-Black', 132)
    HOOK = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); dh = ImageDraw.Draw(HOOK)
    for y, line in ((110, 'QUEM COMEU'), (270, 'A MARMITA?')):
        dh.text((W // 2, y), line, font=f, fill=WHITE, anchor='mm', stroke_width=10, stroke_fill=INK)

def frame_s1(t):
    im = S1_BG.copy()
    p = eo(t / 1.5)
    cx = lerp(-260, 330, p)
    walking = t < 1.5
    by = -abs(math.sin(2 * math.pi * 1.6 * t)) * 16 * (1 - p) if walking else 3 * math.sin(2 * math.pi * (t - 1.5) / 1.4)
    comp(im, FOOTSH, (cx - 140, LEO_FEET - 34))
    comp(im, LEO, (cx - 300, LEO_FEET - 884 + by))
    if t >= 1.55:
        q = (t - 1.55) / 0.35
        s = lerp(0.5, 1.0, backout(q)) if q < 1 else 1.0
        b = BUBBLE if s == 1.0 else BUBBLE.resize((max(1, int(BUBBLE.width * s)), max(1, int(BUBBLE.height * s))), Image.BILINEAR)
        bob = 4 * math.sin(2 * math.pi * t / 1.8)
        ax, ay = 40 + 190, 262 + 330
        comp(im, b, (ax - 190 * s, ay - 330 * s + bob), clamp(q * 3))
    if t < 1.5:
        ha = 1.0 if t < 1.15 else 1 - (t - 1.15) / 0.35
        hs = 1.0 + 0.04 * (1 - eo(t / 0.4))
        hk = HOOK if hs == 1.0 else HOOK.resize((int(W * hs), int(400 * hs)), Image.BILINEAR)
        comp(im, hk, ((W - hk.width) / 2, 280 - (hk.height - 400) / 2), ha)
    comp(im, KICKER, ((W - KICKER.width) // 2, 196))
    CAP['s1'].draw(im, t)
    return im.convert('RGB')

# ---------------------------------------------------------------- scene 2: fridge opens
BX0, BY0, BX1, BY1 = 90, 120, 990, 1290
def build_s2_bg():
    w, h = W * S, H * S
    img = vgrad(w, h, (255, 240, 210), (250, 224, 188), 0, 1300 * S)
    d = ImageDraw.Draw(img)
    for x in range(20, W, 92): d.rectangle(P(x, 0, x + 34, 1300), fill=(255, 246, 224))
    img.paste(vgrad(w, (H - 1300) * S, (52, 160, 160), (22, 92, 98)), (0, 1300 * S)); d = ImageDraw.Draw(img)
    yy, k = 1300, 0
    while yy < H:
        k += 1; yy += 20 + k * k * 4
        d.line(P(0, yy, W, yy), fill=(40, 132, 134), width=3 * S)
    d.rectangle(P(0, 1294, W, 1306), fill=(214, 190, 150))
    img = fill_soft(img, lambda d: d.ellipse(P(60, 1280, 1020, 1340), fill=255), (20, 70, 74), 12 * S, 0.6)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(P(BX0, BY0, BX1, BY1), radius=36 * S, fill=(196, 230, 224))
    d.rounded_rectangle(P(130, 160, 950, 1250), radius=18 * S, fill=(230, 243, 248))
    cav = vgrad((950 - 130) * S, (1250 - 160) * S, (248, 252, 254), (212, 232, 240))
    m = Image.new('L', cav.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cav.width - 1, cav.height - 1), radius=18 * S, fill=255)
    img.paste(cav, tuple(P(130, 160)), m)
    img = glow(img, lambda d: d.ellipse(P(330, 120, 750, 380), fill=200), (40, 36, 20), 40 * S)
    d = ImageDraw.Draw(img)
    # top shelf items
    d.rectangle(P(180, 252, 300, 470), fill=(250, 250, 252))
    d.polygon(P(180, 252, 240, 214, 300, 252), fill=(226, 228, 236))
    d.rectangle(P(180, 330, 300, 384), fill=(80, 150, 230))
    d.text(P(240, 357), 'LEITE', font=F('InterDisplay-Black', 26 * S), fill=(255, 255, 255), anchor='mm')
    for x0 in (330, 418):
        d.polygon(P(x0, 400, x0 + 76, 400, x0 + 68, 470, x0 + 8, 470), fill=(250, 160, 190))
        d.ellipse(P(x0 - 4, 390, x0 + 80, 410), fill=(255, 255, 255))
    d.rounded_rectangle(P(540, 334, 660, 470), radius=16 * S, fill=(206, 232, 212))
    for (cx, cy) in [(570, 380), (600, 420), (630, 380), (575, 440), (628, 440), (600, 360)]:
        d.ellipse(P(cx - 14, cy - 22, cx + 14, cy + 22), fill=(96, 164, 74))
    d.rounded_rectangle(P(530, 312, 670, 338), radius=6 * S, fill=(232, 120, 60))
    d.rounded_rectangle(P(722, 280, 802, 470), radius=14 * S, fill=(250, 162, 52))
    d.rectangle(P(744, 246, 780, 284), fill=(250, 162, 52)); d.rectangle(P(740, 228, 784, 250), fill=(240, 240, 244))
    d.rounded_rectangle(P(836, 424, 926, 470), radius=8 * S, fill=(255, 226, 120))
    # bottom shelf items
    for x0 in (180, 262):
        d.rounded_rectangle(P(x0, 898, x0 + 70, 1040), radius=10 * S, fill=(220, 50, 60))
        d.ellipse(P(x0, 890, x0 + 70, 908), fill=(200, 204, 212))
        d.rectangle(P(x0 + 10, 950, x0 + 60, 980), fill=(255, 255, 255))
    d.rounded_rectangle(P(400, 880, 470, 1040), radius=18 * S, fill=(214, 40, 40))
    d.rectangle(P(420, 850, 450, 884), fill=(240, 240, 244))
    d.rectangle(P(408, 940, 462, 990), fill=(255, 250, 240))
    d.ellipse(P(546, 972, 616, 1040), fill=(230, 70, 60))
    d.polygon(P(570, 974, 582, 960, 596, 976), fill=(70, 160, 70))
    d.rounded_rectangle(P(670, 1000, 910, 1040), radius=8 * S, fill=(226, 218, 204))
    for x in range(690, 900, 46): d.ellipse(P(x, 974, x + 38, 1012), fill=(255, 250, 240))
    # shelves
    for y in (470, 800, 1040):
        d.rectangle(P(130, y, 950, y + 14), fill=(190, 220, 232))
        d.line(P(130, y + 1, 950, y + 1), fill=(244, 252, 255), width=3 * S)
    # empty spot
    x0, y0, x1, y1 = 330, 662, 750, 792
    per = []
    for sx in range(x0 + 16, x1 - 16, 26): per.append(((sx, y0), (sx + 13, y0))); per.append(((sx, y1), (sx + 13, y1)))
    for sy in range(y0 + 16, y1 - 16, 26): per.append(((x0, sy), (x0, sy + 13))); per.append(((x1, sy), (x1, sy + 13)))
    for (a, b) in per: d.line(P(a[0], a[1], b[0], b[1]), fill=(176, 200, 214), width=4 * S)
    for (cx, cy, rr, col) in [(380, 782, 6, (232, 140, 60)), (412, 788, 4, (208, 64, 44)), (540, 786, 5, (232, 140, 60)),
                              (690, 780, 6, (208, 64, 44)), (720, 788, 4, (232, 140, 60))]:
        d.ellipse(P(cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    # small sticky note on the back wall
    note = Image.new('RGBA', (180 * S, 180 * S), (0, 0, 0, 0)); dn = ImageDraw.Draw(note)
    dn.rectangle(P(20, 20, 160, 160), fill=(255, 226, 102))
    dn.rectangle(P(60, 8, 120, 30), fill=(255, 255, 255, 150))
    for y in (60, 92): dn.line(P(40, y, 140, y + 4), fill=(38, 52, 120), width=5 * S)
    dn.arc(P(70, 104, 110, 144), 20, 160, fill=(38, 52, 120), width=5 * S)
    note = note.rotate(-7, resample=Image.BICUBIC, expand=True)
    img.paste(note, tuple(P(450, 504)), note)
    # crisper drawers
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for (cx, cy, rr) in [(260, 1170, 70), (360, 1190, 60), (680, 1180, 70), (790, 1170, 60), (860, 1200, 50)]:
        d.ellipse(P(cx - rr, cy - rr, cx + rr, cy + rr), fill=(110, 186, 90))
    for (a, b) in [(140, 535), (545, 940)]:
        dl.rounded_rectangle(P(a, 1062, b, 1244), radius=14 * S, fill=(226, 242, 246, 170), outline=(244, 252, 255, 255), width=3 * S)
        dl.rounded_rectangle(P((a + b) / 2 - 50, 1082, (a + b) / 2 + 50, 1100), radius=8 * S, fill=(190, 214, 224, 255))
    img = Image.alpha_composite(img.convert('RGBA'), lay)
    return down(img)

def build_door():
    dw, dh = BX1 - BX0, BY1 - BY0
    front = Image.new('RGBA', (dw * S, dh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(front)
    d.rounded_rectangle((0, 0, dw * S - 1, dh * S - 1), radius=36 * S, fill=(205, 238, 232))
    d.rectangle(P(dw - 50, 30, dw, dh - 30), fill=(188, 224, 218))
    d.rounded_rectangle(P(dw - 96, 380, dw - 70, 760), radius=10 * S, fill=(150, 165, 172))
    d.rectangle(P(180, 250, 380, 430), fill=(255, 255, 255))
    d.ellipse(P(264, 236, 298, 270), fill=(232, 70, 76))
    for (cx, cy) in [(254, 320), (306, 320)]: d.ellipse(P(cx - 28, cy - 28, cx + 28, cy + 28), fill=(236, 90, 110))
    d.polygon(P(228, 330, 332, 330, 280, 386), fill=(236, 90, 110))
    d.ellipse(P(560, 200, 610, 250), fill=(255, 196, 70)); d.ellipse(P(620, 560, 664, 604), fill=(70, 150, 230))
    inner = Image.new('RGBA', (dw * S, dh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(inner)
    d.rounded_rectangle((0, 0, dw * S - 1, dh * S - 1), radius=36 * S, fill=(222, 240, 238))
    for y in (220, 520, 820):
        for (x, c) in [(140, (230, 80, 60)), (260, (250, 200, 60)), (380, (120, 180, 90)), (500, (240, 240, 244)), (620, (200, 60, 80))]:
            d.rounded_rectangle(P(x, y - 90, x + 70, y + 60), radius=12 * S, fill=c)
        d.rounded_rectangle(P(80, y, dw - 80, y + 110), radius=12 * S, fill=(200, 226, 232))
    return down(front), down(inner)

S2_DUR = 4.5
S2_OPEN, S2_SUMIU = 0.45, 2.0
def setup_s2():
    global S2_BG, DOOR_F, DOOR_I, RING
    S2_BG = build_s2_bg()
    DOOR_F, DOOR_I = build_door()

def shade(im, f):
    r, g, b, a = im.split()
    lut = [int(v * f) for v in range(256)]
    return Image.merge('RGBA', (r.point(lut), g.point(lut), b.point(lut), a))

def frame_s2(t):
    im = S2_BG.copy()
    th = 0.0 if t < S2_OPEN else eio((t - S2_OPEN) / 0.55) * math.radians(112)
    dw, dh = BX1 - BX0, BY1 - BY0
    c = math.cos(th)
    hh = int(dh * (1 + 0.06 * math.sin(th))); yy = BY0 - (hh - dh) // 2
    if th == 0:
        im.alpha_composite(DOOR_F, (BX0, BY0))
    elif c > 0.003:
        dimg = shade(DOOR_F.resize((max(1, int(dw * c)), hh), Image.BILINEAR), 1 - 0.3 * math.sin(th))
        im.alpha_composite(dimg, (BX0, yy))
    elif c < -0.003:
        wi = int(dw * -c)
        dimg = shade(DOOR_I.resize((wi, hh), Image.BILINEAR), 0.85 + 0.15 * (-c))
        comp(im, dimg, (BX0 - wi, yy))
    if t >= S2_SUMIU:
        k = ((t - S2_SUMIU) * 1.6) % 1.0
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle((330 - 10 * k, 662 - 10 * k, 750 + 10 * k, 792 + 10 * k), radius=18,
                                               outline=(232, 70, 76, int(255 * (1 - k))), width=8)
        im.alpha_composite(lay)
    if t >= S2_SUMIU:
        z = 1 + 0.22 * eo((t - S2_SUMIU) / 0.22)
        fx, fy = 540, 760
        l, tp = fx * (1 - 1 / z), fy * (1 - 1 / z)
        im = im.resize((W, H), Image.BILINEAR, box=(l, tp, l + W / z, tp + H / z))
        sy = M.shake(t, [S2_SUMIU], 14, freq=18, tau=0.08)
        sx = M.shake(t, [S2_SUMIU + 0.03], 10, freq=15, tau=0.08)
        if sy or sx: im = Image.fromarray(np.roll(np.roll(np.asarray(im), sy, axis=0), sx, axis=1))
    comp(im, KICKER, ((W - KICKER.width) // 2, 196))
    CAP['s2'].draw(im, t)
    return im.convert('RGB')

# ---------------------------------------------------------------- scene 3: the note
NS = 780
def build_note():
    base = Image.new('RGBA', (NS * S, NS * S), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    sh = Image.new('L', base.size, 0); ImageDraw.Draw(sh).rectangle(P(56, 70, 740, 754), fill=140)
    sh = sh.filter(ImageFilter.GaussianBlur(16 * S))
    base.paste((50, 40, 30, 255), (0, 0), sh)
    paper = vgrad(700 * S, 700 * S, (255, 236, 124), (255, 220, 92))
    base.paste(paper, tuple(P(40, 40)))
    d = ImageDraw.Draw(base)
    d.polygon(P(740, 660, 740, 740, 660, 740), fill=(236, 196, 70))
    d.polygon(P(660, 740, 740, 660, 700, 700), fill=(255, 240, 160))
    tape = Image.new('RGBA', (240 * S, 90 * S), (0, 0, 0, 0))
    ImageDraw.Draw(tape).rectangle((0, 0, 240 * S, 90 * S), fill=(255, 255, 255, 130))
    tape = tape.rotate(4, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(tape, tuple(P(270, 0)))
    ink = (38, 52, 120)
    t1 = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(t1).text(P(390, 250), 'tava uma', font=ImageFont.truetype(CAVEAT, 150 * S), fill=ink, anchor='mm')
    t2 = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(t2).text(P(390, 430), 'delícia', font=ImageFont.truetype(CAVEAT, 178 * S), fill=ink, anchor='mm')
    sm = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sm)
    d.ellipse(P(326, 550, 454, 678), outline=ink, width=9 * S)
    d.arc(P(356, 580, 380, 604), 200, 340, fill=ink, width=7 * S)
    d.arc(P(400, 580, 424, 604), 200, 340, fill=ink, width=7 * S)
    d.ellipse(P(394, 630, 426, 668), fill=(236, 110, 130), outline=ink, width=5 * S)
    d.arc(P(348, 586, 432, 652), 20, 160, fill=ink, width=9 * S)
    return down(base), down(t1), down(t2), down(sm)

def wipe(layer, p, x0=40, x1=740):
    xe = int(lerp(x0, x1, p))
    m = Image.new('L', layer.size, 0); ImageDraw.Draw(m).rectangle((0, 0, xe, layer.height), fill=255)
    out = layer.copy(); out.putalpha(ImageChops.multiply(layer.getchannel('A'), m))
    return out

S3_DUR = 4.5
def setup_s3():
    global S3_BG, NOTE_B, NOTE_T1, NOTE_T2, NOTE_SM
    bg = vgrad(W, H, (244, 250, 253), (206, 226, 236))
    bg = M.fill_mask(bg, lambda d: d.rectangle((0, 1236, W, 1270), fill=255), (186, 216, 228), blur=6)
    bg = M.fill_mask(bg, lambda d: d.rectangle((0, 1238, W, 1242), fill=255), (250, 254, 255), blur=1)
    S3_BG = apply_vig(bg, make_vig(0.3))
    NOTE_B, NOTE_T1, NOTE_T2, NOTE_SM = build_note()

def frame_s3(t):
    im = S3_BG.copy()
    note = NOTE_B.copy()
    p1 = clamp((t - 0.5) / 0.6); p2 = clamp((t - 1.15) / 0.7)
    if p1 > 0: note.alpha_composite(wipe(NOTE_T1, p1))
    if p2 > 0: note.alpha_composite(wipe(NOTE_T2, p2))
    if t > 1.95:
        comp(note, NOTE_SM, (0, 0), eo((t - 1.95) / 0.25))
    ang = -5 + 1.2 * math.sin(t * 1.4)
    rot = note.rotate(ang, resample=Image.BICUBIC, expand=True)
    s = lerp(1.3, 1.0, eo(t / 0.35))
    if abs(s - 1) > 1e-3: rot = rot.resize((int(rot.width * s), int(rot.height * s)), Image.BILINEAR)
    comp(im, rot, (540 - rot.width / 2, 735 - rot.height / 2), eo(t / 0.25))
    comp(im, KICKER, ((W - KICKER.width) // 2, 196))
    CAP['s3'].draw(im, t)
    return im.convert('RGB')

# ---------------------------------------------------------------- scenes 4a/4b: suspects
def rays(t, c1, c2, n=16, cx=540, cy=860, speed=7):
    im = Image.new('RGB', (W, H), c1); d = ImageDraw.Draw(im)
    R = 2600; off = math.radians(t * speed)
    for i in range(0, 2 * n, 2):
        a0 = off + i * math.pi / n; a1 = off + (i + 1) * math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c2)
    return im

def label_pill(word, letter, lcol):
    f = F('InterDisplay-Black', 62)
    tw = f.getlength(word); h = 112; w = int(28 + 84 + 24 + tw + 44)
    im = Image.new('RGBA', ((w + 40) * S, (h + 50) * S), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle(P(20, 32, 20 + w, 32 + h), radius=h * S // 2, fill=150)
    im.paste((40, 10, 20, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(10 * S)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(P(20, 20, 20 + w, 20 + h), radius=h * S // 2, fill=(255, 255, 255))
    d.ellipse(P(20 + 14, 20 + 14, 20 + 14 + 84, 20 + 14 + 84), fill=(26, 22, 30))
    d.text(P(20 + 14 + 42, 20 + h / 2 + 2), letter, font=F('InterDisplay-Black', 58 * S), fill=lcol, anchor='mm')
    d.text(P(20 + 28 + 84 + 24 - 14, 20 + h / 2 + 3), word, font=F('InterDisplay-Black', 62 * S), fill=(26, 22, 30), anchor='lm')
    return down(im)

S4_DUR = 4.5
SP_X, SP_Y = 240, 410
def setup_s4():
    global JU, CARLOS, JU_ST, CARLOS_ST, PILL_A, PILL_B, VIG
    JU, CARLOS = person('ju'), person('carlos')
    JU_ST, CARLOS_ST = sticker(JU), sticker(CARLOS)
    PILL_A = label_pill('SUSPEITA', 'A', A_COL)
    PILL_B = label_pill('SUSPEITO', 'B', B_COL)
    VIG = make_vig(0.32, cy=0.45)

def suspect_frame(t, sprite, pill, c1, c2, extra, cap):
    im = apply_vig(rays(t, c1, c2), VIG)
    q = t / 0.5
    oy = (1 - backout(q)) * 520 if q < 1 else 0
    bob = 4 * math.sin(2 * math.pi * t / 1.6)
    comp(im, sprite, (SP_X, SP_Y + oy + bob))
    extra(im, t, oy + bob)
    if t > 0.12:
        s = lerp(0.55, 1.0, backout((t - 0.12) / 0.4))
        pi = pill if abs(s - 1) < 1e-3 else pill.resize((int(pill.width * s), int(pill.height * s)), Image.BILINEAR)
        comp(im, pi, (540 - pi.width / 2, 340 - pi.height / 2), clamp((t - 0.12) * 6))
    comp(im, KICKER, ((W - KICKER.width) // 2, 196))
    CAP[cap].draw(im, t)
    return im.convert('RGB')

def ju_extra(im, t, dy):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, (x0, yb) in enumerate([(540 - 196, 830), (540 + 190, 800), (540 + 226, 900)]):
        ph = (t * 0.9 + i * 0.33) % 1.0
        y0 = yb - ph * 60 + dy
        a = int(230 * math.sin(math.pi * ph))
        pts = [(x0 + 16 * math.sin(yy / 26 + t * 5 + i), y0 - yy) for yy in range(0, 170, 6)]
        d.line(pts, fill=(255, 248, 230, a), width=10, joint='curve')
    im.alpha_composite(lay)

def carlos_extra(im, t, dy):
    if t < 1.9: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy = SP_X + 304, SP_Y + 528 + dy
    for off in (0.0, 0.5):
        k = ((t - 1.9) * 1.3 + off) % 1.0
        r = 34 + 46 * k
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, int(255 * (1 - k))), width=8)
    im.alpha_composite(lay)

def frame_s4a(t): return suspect_frame(t, JU_ST, PILL_A, (255, 196, 92), (255, 212, 128), ju_extra, 's4a')
def frame_s4b(t): return suspect_frame(t, CARLOS_ST, PILL_B, (232, 76, 82), (244, 104, 106), carlos_extra, 's4b')

# ---------------------------------------------------------------- scene 5: the choice
def build_empty_box():
    im = Image.new('RGBA', (520 * S, 300 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lid = Image.new('RGBA', (300 * S, 60 * S), (0, 0, 0, 0))
    ImageDraw.Draw(lid).rounded_rectangle((0, 0, 300 * S - 1, 50 * S), radius=14 * S, fill=(80, 150, 230))
    lid = lid.rotate(18, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(lid, tuple(P(250, 10)))
    d.rounded_rectangle(P(60, 90, 400, 270), radius=24 * S, fill=(236, 243, 247), outline=(186, 204, 214), width=6 * S)
    d.rectangle(P(78, 104, 382, 128), fill=(214, 228, 236))
    for (cx, cy, rr, col) in [(130, 240, 9, (232, 140, 60)), (170, 252, 6, (208, 64, 44)), (300, 246, 8, (232, 140, 60)),
                              (340, 254, 5, (208, 64, 44)), (230, 250, 6, (232, 140, 60))]:
        d.ellipse(P(cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    fork = Image.new('RGBA', (60 * S, 260 * S), (0, 0, 0, 0)); df = ImageDraw.Draw(fork)
    df.rounded_rectangle(P(22, 90, 38, 250), radius=8 * S, fill=(196, 200, 210))
    df.rounded_rectangle(P(10, 40, 50, 100), radius=10 * S, fill=(196, 200, 210))
    for x in (12, 24, 36, 46):
        df.rounded_rectangle(P(x - 2, 0, x + 4, 60), radius=3 * S, fill=(196, 200, 210))
    fork = fork.rotate(-28, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(fork, tuple(P(380, 30)))
    return down(im)

S5_DUR = 8.0
def setup_s5():
    global CARD_A, CARD_B, CTA, SUB, BOX, VIG5, QM
    CARD_A = M.card('A', 'Ju do RH', A_COL, (30, 20, 8), A_COL, (30, 20, 8))
    CARD_B = M.card('B', 'Seu Carlos', B_COL, (64, 10, 14), (255, 228, 228), WHITE)
    for c, sp in ((CARD_A, JU), (CARD_B, CARLOS)):
        pt = head_portrait(sp, 140)
        c.alpha_composite(pt, (30 + 900 - 22 - 140, 30 + 20))
    CTA = rich_line([('Comenta ', WHITE), ('A', A_COL), (' ou ', WHITE), ('B', B_COL)], F('InterDisplay-ExtraBold', 76))
    SUB = rich_line([('O mais votado vai ser confrontado no ep. 2', (232, 244, 244))], F('Inter-SemiBold', 38), stroke=4)
    BOX = build_empty_box()
    VIG5 = make_vig(0.4, cy=0.5)
    f = F('InterDisplay-Black', 120)
    QM = Image.new('RGBA', (110, 160), (0, 0, 0, 0))
    ImageDraw.Draw(QM).text((55, 80), '?', font=f, fill=WHITE, anchor='mm', stroke_width=7, stroke_fill=INK)

def frame_s5(t):
    im = apply_vig(rays(t, (22, 118, 122), (30, 134, 138), cy=1000, speed=5), VIG5)
    comp(im, KICKER, ((W - KICKER.width) // 2, 196))
    CAP['s5'].draw(im, t)
    for (img, y, t0, side, phase) in [(CARD_A, 560, 0.7, -1, 0.0), (CARD_B, 790, 1.0, 1, math.pi)]:
        if t < t0: continue
        p = eo((t - t0) / 0.45)
        x = (W - img.width) / 2 + side * (1 - p) * 160
        s = 1 + 0.016 * math.sin(2 * math.pi * (t - 2.6) / 1.5 + phase) if t > 2.6 else 1.0
        im2 = img if abs(s - 1) < 1e-3 else img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
        comp(im, im2, (x + img.width / 2 - im2.width / 2, y + img.height / 2 - im2.height / 2), p)
    if t >= 1.7:
        p = eo((t - 1.7) / 0.4); comp(im, CTA, ((W - CTA.width) / 2, 1050 + (1 - p) * 24), p)
    if t >= 2.1:
        p = eo((t - 2.1) / 0.4); comp(im, SUB, ((W - SUB.width) / 2, 1160 + (1 - p) * 18), p)
    if t >= 0.3:
        p = backout((t - 0.3) / 0.5)
        bob = 6 * math.sin(2 * math.pi * t / 1.7)
        comp(im, BOX, (540 - BOX.width / 2, 1330 + (1 - p) * 300 + bob), clamp((t - 0.3) * 4))
        for (qx, qy, ph) in [(290, 1420, 0.0), (800, 1400, 1.7)]:
            comp(im, QM, (qx - 55, qy - 80 + 10 * math.sin(2 * math.pi * t / 1.3 + ph)), clamp((t - 0.6) * 3))
    return im.convert('RGB')

# ---------------------------------------------------------------- captions (narration-ready)
TIMING_FILE = WORK + '/timing.json'
DEFAULT = {
    's1': [(0.3, [('Meio-dia e um!', A_COL)]), (2.3, [('O Léo foi pegar a lasanha que a vó dele fez.', WHITE)])],
    's2': [(0.15, [('Abriu a geladeira e…', WHITE)]), (S2_SUMIU, [('a marmita', WHITE), ('SUMIU!', A_COL)])],
    's3': [(0.2, [('No lugar, só um bilhete:', WHITE)]), (2.3, [('“tava uma delícia”.', A_COL)])],
    's4a': [(0.3, [('Suspeita A: Ju do RH.', WHITE)]), (1.9, [('Ela tá com um cheirinho de lasanha…', WHITE)])],
    's4b': [(0.3, [('Suspeito B: Seu Carlos, o chefe.', WHITE)]), (2.0, [('Tem molho na gravata!', WHITE)])],
    's5': [(0.1, [('QUEM COMEU A MARMITA?', WHITE)])],
}
DURS = {'s1': S1_DUR, 's2': S2_DUR, 's3': S3_DUR, 's4a': S4_DUR, 's4b': S4_DUR, 's5': S5_DUR}
WORD_TIMES = {}

def build_caps():
    global CAP
    CAP = {}
    for k, pages in DEFAULT.items():
        if k == 's5':
            CAP[k] = Caption([(0.1, DURS[k] + 5, [(0.15, 'QUEM COMEU A MARMITA?', WHITE)])],
                             font=('InterDisplay-Black', 88), top=330, maxw=980, gap=0.1)
            continue
        cps = []
        gap = WORD_TIMES.get(k, 0.085)
        for i, (st, segs) in enumerate(pages):
            end = pages[i + 1][0] - 0.05 if i + 1 < len(pages) else DURS[k] + 1
            ss, acc = [], st
            for text, col in segs:
                ss.append((acc, text, col)); acc += gap * len(text.split()) + 0.1
            cps.append((st, end, ss))
        CAP[k] = Caption(cps, font=('InterDisplay-ExtraBold', 74), top=1350, maxw=940, gap=gap)

SCENES = [('s1', frame_s1), ('s2', frame_s2), ('s3', frame_s3), ('s4a', frame_s4a), ('s4b', frame_s4b), ('s5', frame_s5)]

def setup():
    global KICKER
    KICKER = build_kicker()
    setup_s1(); setup_s2(); setup_s3(); setup_s4(); setup_s5()
    build_caps()

def encode(name, fn, dur, fade_in=0, fade_out=0):
    n = int(round(dur * FPS))
    tmp, final = f'{WORK}/{name}.part.mp4', f'{WORK}/{name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE); t0 = time.time()
    for i in range(n):
        a = np.asarray(fn(i / FPS), dtype=np.uint8)
        k = 1.0
        if fade_in and i < fade_in: k = (i + 1) / (fade_in + 1)
        if fade_out and i >= n - fade_out: k = min(k, (n - i) / (fade_out + 1))
        if k < 1: a = (a.astype(np.float32) * k).astype(np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, final); print(f'{name}: {n} frames {time.time() - t0:.1f}s', flush=True)
    else:
        sys.exit('ffmpeg failed ' + name)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    if os.path.exists(TIMING_FILE):
        tj = json.load(open(TIMING_FILE))
        DURS.update(tj.get('durs', {}))
        for k, v in tj.get('pages', {}).items():
            DEFAULT[k] = [(st, [(sg[0], tuple(sg[1])) for sg in segs]) for st, segs in v]
        WORD_TIMES.update(tj.get('gaps', {}))
        S2_SUMIU = tj.get('s2_sumiu', S2_SUMIU)
    t0 = time.time(); setup(); print(f'setup {time.time() - t0:.1f}s', flush=True)
    fns = dict(SCENES)
    if mode == 'preview':
        shots = [('s1', 3.0), ('s2', 1.2), ('s2', 2.8), ('s3', 3.0), ('s4a', 3.0), ('s4b', 3.0), ('s5', 4.0)]
        thumbs = []
        for i, (k, tt) in enumerate(shots):
            t1 = time.time(); im = fns[k](tt); dt = time.time() - t1
            im.save(f'{WORK}/prev_{i}.png'); print(f'prev_{i} {k}@{tt}: {dt * 1000:.0f} ms', flush=True)
            thumbs.append(im.resize((W // 3, H // 3), Image.LANCZOS))
        sheet = Image.new('RGB', (W // 3 * 4, H // 3 * 2))
        for i, th in enumerate(thumbs): sheet.paste(th, ((i % 4) * (W // 3), (i // 4) * (H // 3)))
        sheet.save(f'{WORK}/sheet.png')
    else:
        only = sys.argv[2:] or [k for k, _ in SCENES]
        for idx, (k, fn) in enumerate(SCENES):
            if k in only:
                encode(k, fn, DURS[k], fade_in=0, fade_out=12 if idx == len(SCENES) - 1 else 0)
