#!/usr/bin/env python3
"""Quem Bate à Porta — Episódio 4 (FINAL; Ep. 3 sem votos -> B: responder a Bia).
Usage: ep4.py preview|render narr.mp3 [scenes]   (env BOUNDS=5 pause-start times, else auto)"""
import os, sys, math, random, subprocess, wave, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/porta2'); sys.path.insert(0, '/home/claude/porta3')
import make as M
import ep2 as E
import ep3 as P3
from make import P, F, eo, eio, lerp, clamp, comp, vgrad, glow, down, Caption, rich_line, WHITE, WARM, RED, INK

W, H, FPS, S = 1080, 1920, 30, 2
OUT = '/home/claude/porta4'
E.OUT = OUT
SR, LEAD = 44100, 0.35
E.LEAD = LEAD
SIL = E.SIL
sc, rimmed = P3.sc, P3.rimmed
COLD, FIM = 1.7, 4.2

SENTS = {
    'e1': [('Lia respondeu:', WHITE), ('“cadê você?”', WARM)],
    'e2': [('“No poste.', WARM), ('Ele tem a chave da sua casa.', WARM), ('Foi ele que me levou.”', RED)],
    'e3': [('Lia correu até o poste…', WHITE), ('e lá estava a Bia.', WARM)],
    'e4': [('Atrás delas, a lanterna do Seu Antônio…', WHITE), ('mas a Bia já tinha chamado a polícia.', RED)],
    'e5': [('Depois de um ano,', WHITE), ('as irmãs estavam juntas de novo.', WARM)],
    'e6': [('Até que, às 3h17, o celular vibrou:', WHITE), ('“vocês acharam que ele trabalhava sozinho?”', RED)],
}
ORDER = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6']
MINS = {'e1': 2.8, 'e2': 5.0, 'e3': 3.8, 'e4': 5.2, 'e5': 3.6, 'e6': 5.0}
TAIL = {'e1': 0.6, 'e2': 0.8, 'e3': 0.8, 'e4': 0.9, 'e5': 0.9, 'e6': 1.3}
E.SENTS, E.ORDER = SENTS, ORDER

def r30(v): return round(v * 30) / 30
def stt(k, i): return LEAD + T[k]['st'][i]

def auto_bounds(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    hop = int(0.01 * SR); rms = np.sqrt(np.convolve(x * x, np.ones(hop * 3) / (hop * 3), 'same'))[::hop]
    loud = 20 * np.log10(rms / rms.max() + 1e-9) > -38
    runs, i = [], 0
    while i < len(loud):
        if not loud[i]:
            j = i
            while j < len(loud) and not loud[j]: j += 1
            runs.append((i * 0.01, (j - i) * 0.01)); i = j
        else: i += 1
    first = next(k for k in range(len(loud)) if loud[k]) * 0.01
    inner = [r for r in runs if r[0] > first and r[0] + r[1] < len(loud) * 0.01 - 0.05]
    print('pauses', [(round(a, 2), round(b, 2)) for a, b in inner if b >= 0.25])
    return sorted(a for a, _ in sorted(inner, key=lambda r: r[1], reverse=True)[:5])

# ------------------------------------------------------------ characters
def bia_hooded():
    lia = E.build_lia()
    im = Image.new('RGBA', (300 * S, 720 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = SIL + (255,)
    d.ellipse(P(80, 36, 220, 190), fill=c); d.polygon(P(70, 150, 230, 150, 242, 250, 58, 250), fill=c)
    hood = down(im)
    base = Image.new('RGBA', lia.size, (0, 0, 0, 0)); base.alpha_composite(lia); base.alpha_composite(hood)
    a = base.getchannel('A'); sil = Image.new('RGBA', base.size, SIL + (0,)); sil.putalpha(a)
    return rimmed(sil, (110, 140, 200), 0.55, 5)

# ------------------------------------------------------------ street
FEET = 1330
LX, LY = 640, 400            # lamp head
def build_street():
    w, h = W * S, H * S
    img = vgrad(w, h, (8, 11, 26), (26, 30, 56), 0, 1150 * S); d = ImageDraw.Draw(img)
    rng = random.Random(9); x = -20
    while x < W:
        bw = rng.randint(120, 220); bh = rng.randint(140, 260)
        d.rectangle(P(x, 1150 - bh, x + bw, 1150), fill=(13, 16, 32)); d.polygon(P(x - 10, 1150 - bh, x + bw / 2, 1150 - bh - 70, x + bw + 10, 1150 - bh), fill=(11, 13, 28))
        if rng.random() < 0.5:
            wx = x + bw / 2 - 25; wy = 1150 - bh + 50
            img = glow(img, lambda dd, wx=wx, wy=wy: dd.rectangle(P(wx, wy, wx + 50, wy + 50), fill=255), (255, 190, 110), 8 * S)
            d = ImageDraw.Draw(img); d.rectangle(P(wx, wy, wx + 50, wy + 50), fill=(255, 206, 130))
        x += bw + rng.randint(10, 40)
    img.paste(vgrad(w, (H - 1150) * S, (22, 22, 30), (5, 5, 8)), (0, 1150 * S)); d = ImageDraw.Draw(img)
    d.rectangle(P(0, 1150, W, 1170), fill=(34, 34, 44))
    for xx in range(60, W, 200): d.rectangle(P(xx, 1600, xx + 110, 1612), fill=(40, 40, 50))
    d.rectangle(P(752, 380, 770, FEET - 10), fill=(16, 18, 26))
    d.line(P(760, 392, 720, 372, 660, 372), fill=(16, 18, 26), width=7 * S)
    d.polygon(P(620, 372, 668, 372, 660, 392, 628, 392), fill=(22, 24, 34))
    img = glow(img, lambda dd: dd.polygon(P(632, 392, 656, 392, 900, FEET, 380, FEET), fill=120), (140, 108, 60), 18 * S)
    img = glow(img, lambda dd: dd.ellipse(P(380, FEET - 40, 900, FEET + 40), fill=200), (150, 118, 70), 14 * S)
    img = glow(img, lambda dd: dd.ellipse(P(620, 380, 668, 404), fill=255), (255, 214, 140), 12 * S)
    d = ImageDraw.Draw(img); d.ellipse(P(628, 386, 660, 398), fill=(255, 240, 200))
    img = glow(img, lambda dd: dd.rectangle(P(600, FEET + 60, 680, 1900), fill=80), (120, 92, 52), 16 * S)
    return down(img).convert('RGBA')

def police_wash(t, k):
    if k <= 0: return None
    ph = (t * 3.0) % 1.0; red = ph < 0.5
    col = (240, 40, 50) if red else (50, 100, 255)
    a = 0.55 * k * (0.6 + 0.4 * math.sin(math.pi * ((ph * 2) % 1.0)))
    m = WASH_L if red else WASH_R
    lay = Image.new('RGBA', (W, H), col + (0,)); lay.putalpha(m.point(lambda v: int(v * a))); return lay

# ------------------------------------------------------------ setup
def setup():
    global E0_BG, E0_RAIN, H1, H2, H0, PHONE, NO_ENT, NO_BIA, NB_H, NE_H, BUB, N_POSTE, N_CHAVE, N_LEVOU, NP_H, NC_H, NL_H
    global STREET, ST_RAIN, LIA, BIA_H, BIA, ANT, ANT_HAND, WASH_L, WASH_R, PH6, N_SOZ, END_RAIN, FIM_T, FIM_Q, FIM_SUB, FIM_F, E6_BG
    E0_BG = vgrad(W, H, (10, 14, 30), (2, 3, 8)).convert('RGBA'); E0_RAIN = M.Rain(41, M.RAIN_OUT)
    def big(txt, size):
        while F('InterDisplay-Black', size).getlength(txt) > 960: size -= 4
        f = F('InterDisplay-Black', size); asc, desc = f.getmetrics(); w = int(f.getlength(txt)) + 40
        im = Image.new('RGBA', (w, asc + desc + 40), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 20), txt, font=f, fill=WHITE, stroke_width=11, stroke_fill=INK); return im
    H1, H2 = big('SOU EU, LIA.', 170), big('A BIA.', 210)
    H0 = rich_line([('NÚMERO DESCONHECIDO', WARM)], F('InterDisplay-ExtraBold', 44), stroke=5)
    _, PHONE = M.build_phone('3:26')
    NO_ENT, NE_H = M.notif_card('não entra.'); NO_BIA, NB_H = M.notif_card('sou eu, lia. a bia.')
    N_POSTE, NP_H = M.notif_card('no poste.'); N_CHAVE, NC_H = M.notif_card('ele tem a chave da sua casa.')
    N_LEVOU, NL_H = M.notif_card('foi ele que me levou.')
    f = F('Inter-SemiBold', 48); tw = f.getlength('cadê você?')
    BUB = Image.new('RGBA', (int(tw + 80), 120), (0, 0, 0, 0)); db = ImageDraw.Draw(BUB)
    db.rounded_rectangle((0, 0, BUB.width - 1, 100), radius=46, fill=(40, 130, 250))
    db.polygon([(BUB.width - 40, 80), (BUB.width - 4, 112), (BUB.width - 70, 96)], fill=(40, 130, 250))
    db.text((40, 50), 'cadê você?', font=f, fill=WHITE, anchor='lm')
    STREET = build_street(); ST_RAIN = M.Rain(42, M.RAIN_OUT)
    LIA = sc(E.build_lia(), 0.82); BIA_H = sc(bia_hooded(), 0.82); BIA = LIA
    a, hand = P3.build_antonio(52, torch=True)
    ANT_HAND = (a.width - hand[0], hand[1]); ANT = sc(ImageOps.mirror(a), 0.55)
    yy, xx = np.mgrid[0:H, 0:W]
    WASH_L = Image.fromarray((255 * np.clip(1 - np.hypot((xx + 100) / 900, (yy - 1200) / 1300), 0, 1)).astype(np.uint8))
    WASH_R = Image.fromarray((255 * np.clip(1 - np.hypot((xx - 1180) / 900, (yy - 1200) / 1300), 0, 1)).astype(np.uint8))
    _, PH6 = M.build_phone('3:17')
    N_SOZ, _ = M.notif_card('vocês acharam que ele trabalhava sozinho?')
    E6_BG = vgrad(W, H, (10, 14, 30), (4, 5, 10)).convert('RGBA')
    END_RAIN = M.Rain(43, M.RAIN_OUT)
    FIM_T = rich_line([('FIM', WHITE), ('?', RED)], F('InterDisplay-Black', 300), stroke=14)
    FIM_Q = rich_line([('Qual história vem agora?', WHITE)], F('InterDisplay-ExtraBold', 66), stroke=6)
    FIM_SUB = rich_line([('Comenta ', WHITE), ('👇', WHITE)], F('InterDisplay-ExtraBold', 60), stroke=6) if False else \
        rich_line([('Comenta aqui embaixo', WARM)], F('InterDisplay-ExtraBold', 58), stroke=6)
    FIM_F = rich_line([('Segue', WARM), (' pra ver a próxima série', WHITE)], F('InterDisplay-ExtraBold', 52), stroke=5)

# ------------------------------------------------------------ frames
def head(im, k, t):
    im = M.apply_mult(im, MULT); comp(im, KICK, ((W - KICK.width) // 2, 210))
    if k in CAP: CAP[k].draw(im, t)
    return im.convert('RGB')

def frame_e0(t):
    im = E0_BG.copy(); im.alpha_composite(E0_RAIN.layer(t))
    s = 1 + 0.25 * (1 - eo(t / 0.25))
    for img, y in ((H1, 700), (H2, 910)):
        i2 = sc(img, s); comp(im, i2, ((W - i2.width) / 2, y - (i2.height - img.height) / 2))
    comp(im, H0, ((W - H0.width) / 2, 610))
    dx = int(round(9 * math.sin(2 * math.pi * 30 * t))) if (0.05 <= t < 0.4 or 0.6 <= t < 0.95) else 0
    if dx: im = Image.fromarray(np.roll(np.asarray(im), dx, axis=1))
    return head(im, 'e0', t)

def phone_base(t, phone=None):
    im = E6_BG.copy(); im.alpha_composite(ST_RAIN.layer(t)); im.alpha_composite(phone or PHONE); return im

def frame_e1(t):
    im = phone_base(t)
    comp(im, NO_BIA, (M.NX, M.NY)); comp(im, NO_ENT, (M.NX, M.NY + NB_H + 18))
    tb = stt('e1', 1) - 0.15
    if t >= tb:
        q = E.backout(clamp((t - tb) / 0.4)); b = sc(BUB, lerp(0.6, 1.0, q))
        comp(im, b, (M.NX + 600 - b.width, 1500 - b.height / 2 + (1 - q) * 60), clamp((t - tb) * 5))
        if t > tb + 0.6:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.text((M.NX + 600, 1580), 'Entregue', font=F('Inter-Medium', 30), fill=(200, 200, 214, 255), anchor='rm')
            im.alpha_composite(lay)
    return head(im, 'e1', t)

def frame_e2(t):
    im = phone_base(t)
    ts = [stt('e2', i) - 0.2 for i in range(3)]
    def buzz(t0): return int(round(6 * math.sin(2 * math.pi * 32 * t))) if (t0 <= t < t0 + 0.3) else 0
    dx = buzz(ts[0]) or buzz(ts[1]) or buzz(ts[2])
    cards = [(N_POSTE, NP_H), (N_CHAVE, NC_H), (N_LEVOU, NL_H)]
    shown = [(c, h, eo(clamp((t - t0) / 0.35))) for (c, h), t0 in zip(cards, ts) if t >= t0]
    y = M.NY
    for c, h, p in reversed(shown):
        comp(im, c, (M.NX + dx, y - (1 - p) * 60), p); y += (h + 18) * p
    comp(im, NO_BIA, (M.NX + dx, y)); y += NB_H + 18
    if t >= ts[2] + 0.2:
        k = clamp((t - ts[2] - 0.2) / 0.4)
        lay = Image.new('RGBA', (W, H), (200, 20, 30, int(60 * k * (0.7 + 0.3 * math.sin(t * 6))))); im.alpha_composite(lay)
    return head(im, 'e2', t)

def street_frame(t, lia_x, bia_x, bia_hood, beam=0.0, police=0.0, ant_x=None, zoom=1.0, hug=0.0):
    im = STREET.copy()
    if ant_x is not None:
        comp(im, ANT, (ant_x - ANT.width / 2, 1260 - ANT.height))
        if beam > 0:
            hx = ant_x - ANT.width / 2 + ANT_HAND[0] * 0.55 - 16; hy = 1260 - ANT.height + ANT_HAND[1] * 0.55 + 10
            fl = 0.85 + 0.15 * math.sin(t * 37) * math.sin(t * 13)
            bm = Image.new('L', (W, H), 0)
            ImageDraw.Draw(bm).polygon([(hx, hy - 6), (hx, hy + 6), (bia_x + 120, FEET + 40), (lia_x - 160, FEET - 380)], fill=int(185 * beam * fl))
            bm = bm.filter(ImageFilter.GaussianBlur(22))
            lb = Image.new('RGBA', (W, H), (255, 236, 190, 0)); lb.putalpha(bm); im.alpha_composite(lb)
    b = BIA_H if bia_hood else BIA
    comp(im, b, (bia_x - b.width / 2, FEET - b.height))
    if lia_x is not None: comp(im, LIA, (lia_x - LIA.width / 2 - hug * 30, FEET - LIA.height))
    im.alpha_composite(ST_RAIN.layer(t))
    pw = police_wash(t, police)
    if pw is not None: im.alpha_composite(pw)
    if zoom > 1.0001:
        l, tp = 640 * (1 - 1 / zoom), 1000 * (1 - 1 / zoom)
        im = im.resize((W, H), Image.BILINEAR, box=(l, tp, l + W / zoom, tp + H / zoom))
    return im

def frame_e3(t):
    t2 = stt('e3', 1)
    p = eio(clamp((t - 0.1) / max(0.6, t2 - 0.1)))
    lia_x = lerp(-200, 520, p)
    bob = -abs(math.sin(2 * math.pi * 2.2 * t)) * 14 if p < 1 else 0
    im = street_frame(t, lia_x, 700, bia_hood=t < t2 + 0.15)
    if bob: im = Image.fromarray(np.roll(np.asarray(im), int(bob), axis=0))
    return head(im, 'e3', t)

def frame_e4(t):
    t2 = stt('e4', 1)
    ax = lerp(1160, 960, eo(clamp((t - 0.2) / 1.2)))
    beam = clamp((t - 0.6) / 0.4) * (1 - clamp((t - t2 - 0.6) / 0.3))
    pol = clamp((t - t2 + 0.1) / 0.5)
    im = street_frame(t, 560, 700, False, beam=beam, police=pol, ant_x=ax)
    return head(im, 'e4', t)

def frame_e5(t):
    z = 1 + 0.12 * eio(t / DURS['e5'])
    im = street_frame(t, 600, 680, False, police=0.35, zoom=z, hug=1.0)
    lay = Image.new('RGBA', (W, H), (255, 190, 110, int(30 + 20 * math.sin(t * 2)))); im.alpha_composite(lay)
    return head(im, 'e5', t)

def frame_e6(t):
    im = E6_BG.copy(); im.alpha_composite(END_RAIN.layer(t))
    t2 = stt('e6', 1) - 0.2
    dx = int(round(6 * math.sin(2 * math.pi * 32 * t))) if (t2 <= t < t2 + 0.3 or t2 + 0.45 <= t < t2 + 0.75) else 0
    im.alpha_composite(PH6, (dx, 0))
    if t >= t2:
        p = eo(clamp((t - t2) / 0.4)); comp(im, N_SOZ, (M.NX + dx, M.NY - (1 - p) * 60), p)
    return head(im, 'e6', t)

def frame_fim(t):
    im = E0_BG.copy(); im.alpha_composite(END_RAIN.layer(t))
    k = eo(clamp(t / 0.5)); s = lerp(1.3, 1.0, k)
    ft = sc(FIM_T, s); comp(im, ft, ((W - ft.width) / 2, 620 - (ft.height - FIM_T.height) / 2), k)
    if t > 0.7: p = eo((t - 0.7) / 0.4); comp(im, FIM_Q, ((W - FIM_Q.width) / 2, 1020 + (1 - p) * 20), p)
    if t > 1.1: p = eo((t - 1.1) / 0.4); comp(im, FIM_SUB, ((W - FIM_SUB.width) / 2, 1120 + (1 - p) * 20), p)
    if t > 1.6:
        p = E.backout((t - 1.6) / 0.45); s2 = 0.7 + 0.3 * p + (0.02 * math.sin(2 * math.pi * (t - 2.1) / 1.3) if t > 2.1 else 0)
        fw = sc(FIM_F, s2); comp(im, fw, ((W - fw.width) / 2, 1260 + (FIM_F.height - fw.height) / 2), clamp((t - 1.6) * 4))
    return head(im, 'fim', t)

FRAMES = {'e0': frame_e0, 'e1': frame_e1, 'e2': frame_e2, 'e3': frame_e3, 'e4': frame_e4, 'e5': frame_e5, 'e6': frame_e6, 'fim': frame_fim}

def gap_for(k):
    per = [d / len(s[0].split()) for s, d in zip(SENTS[k], T[k]['du'])]
    return float(np.clip(0.8 * min(per), 0.06, 0.3))

def build_caps():
    global CAP
    CAP = {}; s = SENTS
    ts = {k: [LEAD + v for v in T[k]['st']] for k in SENTS}
    def page(k, idxs, end): return (ts[k][idxs[0]] - 0.05, end, [(ts[k][i], s[k][i][0], s[k][i][1]) for i in idxs])
    CAP['e1'] = Caption([page('e1', [0, 1], DURS['e1'])], gap=gap_for('e1'), top=1660)
    CAP['e2'] = Caption([page('e2', [0, 1], ts['e2'][2] - 0.1), page('e2', [2], DURS['e2'])], gap=gap_for('e2'), top=1660)
    CAP['e3'] = Caption([page('e3', [0], ts['e3'][1] - 0.1), page('e3', [1], DURS['e3'])], gap=gap_for('e3'), top=1440)
    CAP['e4'] = Caption([page('e4', [0], ts['e4'][1] - 0.1), page('e4', [1], DURS['e4'])], gap=gap_for('e4'), top=1440)
    CAP['e5'] = Caption([page('e5', [0, 1], DURS['e5'])], gap=gap_for('e5'), top=1440)
    CAP['e6'] = Caption([page('e6', [0], ts['e6'][1] - 0.1), page('e6', [1], DURS['e6'])], gap=gap_for('e6'), top=1500)

# ------------------------------------------------------------ sound
def make_audio(path, x, st, total):
    n = int(total * SR); t = np.arange(n) / SR; rng = np.random.default_rng(17)
    f = np.fft.rfftfreq(n, 1 / SR)
    resp = 1 / (1 + (350 / np.maximum(f, 1)) ** 2) / (1 + (f / 5200) ** 2)
    rain = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * resp, n); rain /= np.abs(rain).max()
    kp = [(0, .30), (st['e1'], .16), (st['e3'], .38), (st['e5'], .24), (st['e6'], .16), (st['fim'], .3), (total, .3)]
    out = rain * np.interp(t, [a for a, _ in kp], [b for _, b in kp])
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 110.4 * t + 1) + 0.45 * np.sin(2 * np.pi * 164.8 * t + 2))
    out += drone * np.interp(t, [0, st['e3'], st['e4'], st['e5'], st['e6'], total], [0.04, 0.05, 0.09, 0.02, 0.1, 0.08])
    def add(sig, at):
        i = int(at * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += sig[:j - i]
    def tt(d): return np.arange(int(d * SR)) / SR
    def bp(sig, lo, hi):
        X = np.fft.rfft(sig); ff = np.fft.rfftfreq(len(sig), 1 / SR); X *= (ff >= lo) & (ff <= hi); return np.fft.irfft(X, len(sig))
    def buzz(d=0.3):
        tq = tt(d); return np.tanh(2.5 * np.sin(2 * np.pi * 172 * tq)) * np.minimum(1, tq / 0.01) * np.minimum(1, (d - tq) / 0.03) * 0.16
    def hit(g=0.6):
        tq = tt(2.5); fr = 38 + 52 * np.exp(-tq / 0.25)
        return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tq / 0.9) * 0.6 + np.sin(4 * np.pi * np.cumsum(fr) / SR) * np.exp(-tq / 0.5) * 0.25) * g / 0.6
    def swoosh(g=0.12):
        tq = tt(0.35); y = bp(rng.standard_normal(len(tq)), 1500, 6000); y /= np.abs(y).max()
        return y * g * np.sin(np.pi * tq / 0.35) ** 2
    def splash(g=0.12, d=0.16):
        tq = tt(d); y = bp(rng.standard_normal(len(tq)), 200, 2500); return y / np.abs(y).max() * np.exp(-tq / (d / 3.5)) * g
    def click(g=0.25):
        tq = tt(0.03); return bp(rng.standard_normal(len(tq)), 1500, 8000) * np.exp(-tq / 0.006) * g * 3
    def siren(d, g=0.07):
        tq = tt(d); fr = np.where((tq * 1.6) % 1 < 0.5, 660, 880); ph = 2 * np.pi * np.cumsum(fr) / SR
        y = np.sin(ph) + 0.3 * np.sin(2 * ph); return y * g * np.minimum(1, tq / 0.8) * np.minimum(1, (d - tq) / 0.8)
    def pad(d, g=0.06):
        tq = tt(d); y = sum(np.sin(2 * np.pi * fq * tq) for fq in (220, 277.2, 329.6, 440))
        return y * g * np.minimum(1, tq / 1.2) * np.minimum(1, (d - tq) / 1.0)
    add(buzz() * 2.6, 0.05); add(buzz() * 2.6, 0.6); add(hit(0.6), 0.0)
    add(swoosh(), st['e1'] + stt('e1', 1) - 0.15)
    for i in range(3): add(buzz(), st['e2'] + stt('e2', i) - 0.2)
    add(hit(0.55), st['e2'] + stt('e2', 2))
    for k in range(7): add(splash(0.18), st['e3'] + 0.15 + k * 0.23)
    add(hit(0.5), st['e3'] + stt('e3', 1))
    add(click(), st['e4'] + 0.6)
    add(siren(st['e5'] + DURS['e5'] - (st['e4'] + stt('e4', 1) - 0.1)), st['e4'] + stt('e4', 1) - 0.1)
    add(pad(DURS['e5'] + 0.5), st['e5'])
    add(buzz(), st['e6'] + stt('e6', 1) - 0.2); add(buzz(), st['e6'] + stt('e6', 1) + 0.25)
    add(hit(0.75), st['e6'] + stt('e6', 1) + 0.4)
    add(hit(0.6), st['fim'])
    nar = np.zeros(n)
    for k in ORDER:
        a, b = max(0.0, T[k]['a'] - 0.04), T[k]['b'] + 0.1
        seg = x[int(a * SR):int(b * SR)]
        i = int((st[k] + LEAD - 0.04) * SR); j = min(n, i + len(seg)); nar[i:j] += seg[:j - i]
    voiced = np.abs(nar) > 0.02 * np.abs(nar).max()
    nar *= 0.15 / np.sqrt((nar[voiced] ** 2).mean())
    env = np.convolve(np.abs(nar), np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
    duck = 1 - 0.5 * np.clip(env / 0.02, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
    mix = out * 0.6 * duck + nar
    mix *= np.clip((total - t) / 1.0, 0, 1)
    mix = np.tanh(mix * 1.3) / 1.3; mix *= min(1.0, 0.95 / np.abs(mix).max())
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------ main
class _FakeT(dict): pass
def fake_T():
    out = {}
    for k in ORDER:
        st, acc, du = [], 0.0, []
        for s, _ in SENTS[k]:
            d = 0.4 + 0.065 * len(s); st.append(acc); du.append(d); acc += d + 0.25
        out[k] = {'a': 0, 'b': 0, 'L': acc, 'st': st, 'du': du}
    return out

if __name__ == '__main__':
    mode, narr = sys.argv[1], sys.argv[2]
    if narr == 'none':
        X, T = np.zeros(SR), fake_T()
    else:
        bounds = [float(v) for v in os.environ['BOUNDS'].split(',')] if os.environ.get('BOUNDS') else auto_bounds(narr)
        print('bounds', bounds)
        X, T = E.analyse(narr, bounds)
    E.T = T
    DURS = {k: r30(max(MINS[k], LEAD + T[k]['L'] + TAIL[k])) for k in ORDER}
    DURS = {'e0': COLD, **DURS, 'fim': FIM}; E.DURS = DURS
    print('durs', DURS, 'total', round(sum(DURS.values()), 2))
    for k in SENTS: print(k, [round(v, 2) for v in T[k]['st']])
    MULT = M.make_mult(0.55, True); E.MULT = MULT; E.VIG = M.make_mult(0.55, False)
    KICK = E.kicker('QUEM BATE À PORTA  ·  EP. 4 · FINAL')
    t0 = time.time(); setup(); build_caps(); print(f'setup {time.time() - t0:.1f}s', flush=True)
    SEQ = ['e0'] + ORDER + ['fim']
    if mode == 'preview':
        shots = [('e0', 0.6), ('e1', stt('e1', 1) + 0.8), ('e2', stt('e2', 2) + 0.6), ('e3', stt('e3', 0) + 0.6), ('e3', stt('e3', 1) + 0.6),
                 ('e4', 1.4), ('e4', stt('e4', 1) + 0.6), ('e5', 1.5), ('e6', stt('e6', 1) + 0.6), ('fim', 3.0)]
        th = [FRAMES[k](tt_).resize((W // 4, H // 4), Image.LANCZOS) for k, tt_ in shots]
        sheet = Image.new('RGB', (W // 4 * 5, H // 4 * 2))
        for i, im in enumerate(th): sheet.paste(im, ((i % 5) * (W // 4), (i // 5) * (H // 4)))
        sheet.save(f'{OUT}/sheet.png'); print('sheet ok')
    else:
        only = sys.argv[3:] or SEQ
        for idx, k in enumerate(SEQ):
            if k in only: E.encode(k, FRAMES[k], DURS[k], fade_in=0 if k in ('e0', 'e1') else 4, fade_out=15 if k == 'fim' else 0)
        st, acc = {}, 0.0
        for k in SEQ: st[k] = acc; acc += int(round(DURS[k] * FPS)) / FPS
        make_audio(f'{OUT}/audio.wav', X, st, acc)
        with open(f'{OUT}/list.txt', 'w') as fl:
            for k in SEQ: fl.write(f"file '{k}.mp4'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video.mp4'], check=True)
        final = f'{OUT}/quem-bate-a-porta-ep4-final.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final + '.part.mp4'], check=True)
        os.replace(final + '.part.mp4', final); print('done', round(acc, 2))
