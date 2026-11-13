#!/usr/bin/env python3
"""PAUSA O VÍDEO: as criaturas da floresta de Brasa passam rápido (0,1 s cada) e a que parar na pausa é a do espectador.
Gatilhos: auto-referência (cada um ganha a sua), recompensa variável (raridade), replay (quem não gostou tenta de novo).
Saída: out/pausa-<SEED>.mp4  (SEED muda o sorteio da ordem; padrão 1)."""
import os, sys, math, random, subprocess, wave
sys.path.insert(0, "/home/claude/reino")
import numpy as np
from PIL import Image, ImageDraw
import ep1hd as E
import creature as C

FW, FH, FPS = 1080, 1920, 30
SEED = int(os.environ.get('SEED', '1'))
DUR = float(os.environ.get('DUR', '12'))
STEP = 3                                   # quadros por criatura (0,1 s)
OUT = '/home/claude/bestiario/out'
WHITE, GOLD = (255, 255, 255), (255, 196, 70)
RAR_ORDER = ['COMUM', 'INCOMUM', 'RARO', 'ÉPICO', 'LENDÁRIO']
RAR_PCT = dict(C.RARITIES)

# ---------------------------------------------------------------- baralho de criaturas
NSLOT = int(DUR * FPS / STEP)
QUOTA = {'LENDÁRIO': 0.042, 'ÉPICO': 0.09, 'RARO': 0.17, 'INCOMUM': 0.30}
want = {k: max(1, round(NSLOT * v)) for k, v in QUOTA.items()}
want['COMUM'] = NSLOT - sum(want.values())
pool = {k: [] for k in RAR_ORDER}
i = 0
while any(len(pool[k]) < want[k] for k in RAR_ORDER):
    nm = f'pausa{SEED}-{i}'
    tr = C.traits(nm)
    if len(pool[tr['rarity']]) < want[tr['rarity']]:
        pool[tr['rarity']].append(tr)
    i += 1
SLOTS = [t for k in RAR_ORDER for t in pool[k]]
rng = random.Random(SEED)
for _ in range(200):                      # embaralha sem 2 raros-de-verdade (épico/lendário) colados
    rng.shuffle(SLOTS)
    if all(not (SLOTS[j]['lvl'] >= 3 and SLOTS[j + 1]['lvl'] >= 3) for j in range(len(SLOTS) - 1)):
        break
# o primeiro quadro é o gancho: começa num ÉPICO (mostra o que dá pra ganhar logo de cara)
first = next(j for j, t in enumerate(SLOTS) if t['rarity'] == 'ÉPICO')
SLOTS[0], SLOTS[first] = SLOTS[first], SLOTS[0]

# ---------------------------------------------------------------- fundo (floresta de dia, 360x640 x3)
CW, CH = 360, 640


def _bg_day():
    y = np.linspace(0, 1, CH)[:, None, None]
    top, bot = np.array((70, 136, 226)), np.array((176, 220, 252))
    img = np.broadcast_to(top * (1 - y) + bot * y, (CH, CW, 3)).copy()
    r = random.Random(11)
    yy, xx = np.mgrid[0:CH, 0:CW]
    for cx, cy, w in ((60, 70, 46), (250, 40, 60), (320, 150, 38), (130, 200, 30)):
        for k in range(5):
            ex, ey, rr = cx + (k - 2) * w * 0.32, cy + (0 if k % 2 else 4), w * (0.34 if k % 2 else 0.26)
            img[((xx - ex) ** 2 / (rr * 1.6) ** 2 + (yy - ey) ** 2 / rr ** 2) < 1] = (250, 252, 255)
    for col, base, amp in (((110, 160, 200), 470, 70), ((78, 136, 120), 515, 44)):
        h = base
        for x in range(CW):
            if x % 24 == 0:
                tgt = base - r.uniform(0, amp)
            h += (tgt - h) * 0.08
            img[int(h):, x] = col
    for k in range(46):
        x0 = r.randrange(-10, CW)
        hgt = r.randint(30, 62)
        yb = 562 + r.randint(-6, 10)
        col = (34, 92, 58) if k % 3 else (46, 112, 66)
        for j in range(hgt):
            w = int((j / hgt) * 9) + 1
            img[yb - hgt + j:yb - hgt + j + 1, max(0, x0 - w):min(CW, x0 + w)] = col
    img[566:, :] = (92, 170, 74)
    for x in range(0, CW, 2):
        img[566 + (x * 7) % 9, x] = (120, 196, 92)
    return img.astype(np.float32)


BASE = _bg_day()
BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16


def bg_for(rar):
    img = BASE.copy()
    lvl = RAR_ORDER.index(rar)
    strength = (0.45, 0.55, 0.65, 0.8, 0.95)[lvl]
    yy, xx = np.mgrid[0:CH, 0:CW]
    d = np.sqrt((xx - 180) ** 2 + ((yy - 310) * 0.9) ** 2)
    a = (np.clip(1 - d / 165, 0, 1) ** 2 * strength)[..., None]
    a = a * (a[..., 0:1] > BAY[yy % 4, xx % 4][..., None] * 0.35)
    img = img * (1 - a) + np.array(C.RAR_COL[rar]) * a
    big = np.repeat(np.repeat(img, 3, 0), 3, 1).clip(0, 255).astype(np.uint8)
    return Image.fromarray(big).convert('RGBA')


BGS = {k: bg_for(k) for k in RAR_ORDER}


# ---------------------------------------------------------------- texto fixo
def static_overlay():
    ov = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    E.draw_line(d, FW / 2, 150, [('PAUSA O VÍDEO', WHITE)], 128)
    E.draw_line(d, FW / 2, 318, [('A CRIATURA QUE PARAR ', GOLD), ('É A TUA', WHITE)], 62)
    E.draw_line(d, FW / 2, 1568, [('COMENTA QUAL SAIU PRA TI', WHITE)], 60)
    return ov


STATIC = static_overlay()
CX, CY, SPR = 540, 900, 480


def slot_overlay(tr, fr):
    ov = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    a = C.draw(tr['name'], fr)
    sp = Image.fromarray(a).resize((SPR, SPR), Image.NEAREST)
    ov.alpha_composite(sp, (CX - SPR // 2, CY - SPR // 2))
    d = ImageDraw.Draw(ov)
    col = C.RAR_COL[tr['rarity']]
    E.draw_line(d, FW / 2, 1196, [(tr['species'], col)], 96)
    lab = f"{tr['rarity']} · {RAR_PCT[tr['rarity']]}%"
    w = 520
    E.panel(d, (FW / 2 - w / 2, 1322, FW / 2 + w / 2, 1414), fill=(26, 20, 48, 235), b=6)
    d.rectangle((FW / 2 - w / 2 + 14, 1334, FW / 2 - w / 2 + 30, 1402), fill=col + (255,))
    d.text((FW / 2 + 8, 1368), lab, font=E.font(48), fill=col + (255,), anchor='mm')
    d.text((FW / 2, 1460), f"PODER {tr['total']}", font=E.font(44), fill=WHITE + (255,), anchor='mm',
           stroke_width=5, stroke_fill=(24, 18, 40, 255))
    if tr['lvl'] >= 3:                    # brilhos nos épicos/lendários
        r2 = random.Random(tr['seed'] + fr)
        for k in range(10):
            x = CX + r2.uniform(-300, 300); y = CY + r2.uniform(-290, 260)
            s_ = r2.choice((8, 12, 16))
            d.rectangle((x - s_, y - 3, x + s_, y + 3), fill=col + (255,))
            d.rectangle((x - 3, y - s_, x + 3, y + s_), fill=col + (255,))
    return ov


def frame(n):
    k = (n // STEP) % len(SLOTS)
    tr = SLOTS[k]
    base = BGS[tr['rarity']].copy()
    base.alpha_composite(slot_overlay(tr, (n // 6) % 2))
    base.alpha_composite(STATIC)
    return np.array(base.convert('RGB'))


# ---------------------------------------------------------------- áudio
SR = E.SR


def audio(path):
    n = int((DUR + 0.3) * SR)
    s = np.zeros(n)

    def note(t, m, d=0.12, g=0.06, duty=0.25, wave_='sq'):
        nn = int(d * SR)
        osc = E.sq(E.midi(m), nn, duty) if wave_ == 'sq' else E.tri(E.midi(m), nn)
        E.add(s, t, osc * E.adsr(nn, a=0.004, dec=0.05, sus=0.4, r=0.03), g)

    beat = 60 / 140
    prog = [45, 41, 48, 43]
    arp = [0, 3, 7, 12, 7, 3, 7, 12]
    t, k = 0.0, 0
    while t < DUR:
        root = prog[(k // 8) % 4]
        note(t, root + 24 + arp[k % 8], d=beat / 2 * 0.9, g=0.035)
        if k % 2 == 0:
            note(t, root, d=beat * 0.9, g=0.05, wave_='tri')
        t += beat / 2
        k += 1
    for j, tr in enumerate(SLOTS):         # tique a cada criatura, brilho nas raras
        tt = j * STEP / FPS
        if tt >= DUR:
            break
        nn = int(0.012 * SR)
        E.add(s, tt, E.noise(nn, j) * np.exp(-np.arange(nn) / SR * 400), 0.08)
        if tr['lvl'] >= 3:
            note(tt, 88 if tr['lvl'] == 4 else 84, d=0.09, g=0.03)
    s = s / max(1e-9, np.abs(s).max()) * 0.8
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    stills = os.environ.get('STILLS')
    if stills:
        for t in stills.split(','):
            Image.fromarray(frame(int(float(t) * FPS))).save(f'{OUT}/p_{float(t):05.2f}.png')
        print('stills ok')
        raise SystemExit
    wav = f'{OUT}/pausa.wav'
    audio(wav)
    out = f'{OUT}/pausa-{SEED}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}',
                          '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
                          '-af', 'loudnorm=I=-14.5:TP=-2:LRA=11,alimiter=limit=0.7:level=false', '-shortest', out],
                         stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        p.stdin.write(frame(n).tobytes())
    p.stdin.close(); p.wait()
    print(out, len(SLOTS), {k: len(v) for k, v in pool.items()})
