#!/usr/bin/env python3
"""O reino nos memes #1 — "go go go": o guarda cubo indo apartar a briga da taverna bem devagar.
9 s, sem música (o áudio em alta entra no app do TikTok). Saída: out/meme-gogogo.mp4"""
import os, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '73')
import ep5 as G
import ep1hd as E
import ep2 as P
import ep4 as Q
import world2 as W

FW, FH, FPS = 1080, 1920, 30
DUR = 9.0
M_END = 7.2                          # a poeira baixa quando ele chega
CUBO = G.IDX['cubo']
C0 = G.CROWD[CUBO]
C1 = (286, 538)
G.STEP_T0 = G.STEP_T1 = 1e9          # sem pegadas neste vídeo


def tmap(m):
    if m < M_END:
        return G.BR + 0.3 + (m % 2.6)
    return G.DS + 0.5 + (m - M_END)


def cubo_pos(m):
    q = min(1.0, m / (M_END + 0.1))
    pts = [C0, (306, 480), C1]                     # contorna a taverna pela direita
    seg = [math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])]
    L = q * sum(seg)
    k = 0 if L <= seg[0] else 1
    u = (L if k == 0 else L - seg[0]) / seg[k]
    x = pts[k][0] + (pts[k + 1][0] - pts[k][0]) * u
    y = pts[k][1] + (pts[k + 1][1] - pts[k][1]) * u
    fr = (1 + int(m / 0.38) % 2) if q < 1 else 0
    return x, y, fr


_orig_people = G.people_now
_M = {'m': 0.0}


def people_patched(t):
    res = []
    for p in _orig_people(t):
        if p[0] == CUBO:
            res.append((CUBO,) + cubo_pos(_M['m']))
        else:
            res.append(p)
    return res


G.people_now = people_patched
ARROW = ["..###..", "..#r#..", "..#r#..", "###r###", "#rrrrr#", ".#rrr#.", "..#r#..", "...#..."]


def arrow(out, x, y):
    for r_, row in enumerate(ARROW):
        for c_, ch in enumerate(row):
            col = (40, 16, 20) if ch == '#' else ((236, 56, 56) if ch == 'r' else None)
            if col:
                for u in range(2):
                    for v in range(2):
                        G.put_px(out, x - 7 + c_ * 2 + u, y + r_ * 2 + v, col)


def frame(m):
    _M['m'] = m
    t = tmap(m)
    c = G.village(t)
    x, y, _ = cubo_pos(m)
    if m < M_END + 0.3:
        arrow(c, int(x), int(y) - 60 + int(round(math.sin(m * 6) * 1.5)))
    sh = G.shot(t) if m < M_END else G.TSHOT
    f = P.camera(c, sh)
    im = Image.fromarray(f)
    d = ImageDraw.Draw(im, 'RGBA')
    E.draw_line(d, FW / 2, 290, [('eu vendo o guarda da vila', (255, 255, 255))], 96)
    E.draw_line(d, FW / 2, 410, [('indo apartar a briga', (255, 255, 255))], 96)
    for t0, px_, py_, word, col in G.POWS:
        if t0 <= t < t0 + 0.42 and m < M_END:
            E.draw_line(d, px_, py_, [(word, col)], 130, stroke=10)
    if m >= M_END + 0.5:
        x0, y0, s = G.TSHOT
        Q.tag(d, (x - x0) * s, (y - y0) * s + 30, 'CUBO', 'GUARDA DA VILA')
    return np.array(im)


SR = E.SR


def audio(path):
    n = int((DUR + 0.2) * SR)
    s = np.zeros(n)
    r = random.Random(5)

    def thump(t0, g=0.4, f0=110):
        nn = int(0.16 * SR)
        tt = np.arange(nn) / SR
        f = f0 * np.exp(-tt * 18) + 40
        E.add(s, t0, np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 20), g)
        nn2 = int(0.05 * SR)
        E.add(s, t0, E.noise(nn2, int(t0 * 997)) * np.exp(-np.arange(nn2) / SR * 60), g * 0.5)

    t = 0.05
    while t < M_END - 0.1:
        thump(t, g=r.uniform(0.2, 0.4), f0=r.uniform(90, 140))
        t += r.uniform(0.12, 0.24)
    t = 0.0
    while t < DUR:
        for k in range(3):
            nn = int(0.018 * SR)
            E.add(s, t + k * 0.045, np.sin(2 * math.pi * 4600 * np.arange(nn) / SR) * np.hanning(nn), 0.03)
        t += r.uniform(0.55, 0.95)
    for tt_, f_ in ((M_END + 0.45, 660), (M_END + 0.53, 520)):
        nn = int(0.07 * SR)
        E.add(s, tt_, E.sq(f_, nn, 0.5) * E.adsr(nn, a=0.002, dec=0.02, sus=0.3, r=0.01), 0.08)
    s = s / (np.abs(s).max() + 1e-9) * 0.8
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype('<i2').tobytes())


if __name__ == '__main__':
    stills = os.environ.get('STILLS')
    if stills:
        for v in stills.split(','):
            Image.fromarray(frame(float(v))).save(os.path.join(G.OUTDIR, f'meme1_{float(v):04.1f}.png'))
        raise SystemExit
    wav = os.path.join(G.OUTDIR, 'meme1.wav')
    audio(wav)
    out = os.path.join(G.OUTDIR, 'meme-gogogo.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(out)
