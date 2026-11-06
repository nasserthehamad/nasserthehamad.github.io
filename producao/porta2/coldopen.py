import sys, math, subprocess, wave, os
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/video'); sys.path.insert(0, '/home/claude/porta2'); sys.path.insert(0, '/home/claude/lunch')
import make as M, ep2 as E, laudio as LA
from make import F, eo, comp, vgrad, WHITE, WARM, INK
W, H, SR, DUR = 1080, 1920, 44100, 1.7
bg = vgrad(W, H, (10, 14, 30), (2, 3, 8)).convert('RGBA')
rain = M.Rain(31, M.RAIN_OUT); mult = M.make_mult(0.45, False); kick = E.kicker()
def big(txt, size, maxw=1000):
    while F('InterDisplay-Black', size).getlength(txt) > maxw - 40: size -= 4
    f = F('InterDisplay-Black', size); w = int(f.getlength(txt)) + 40; asc, desc = f.getmetrics()
    im = Image.new('RGBA', (w, asc + desc + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 20), txt, font=f, fill=WHITE, stroke_width=11, stroke_fill=INK); return im
L1, L2 = big(os.environ.get('HOOK1', 'QUEM TÁ BATENDO'), 150), big(os.environ.get('HOOK2', 'NÃO SOU EU.'), 190)
f_small = F('InterDisplay-ExtraBold', 44)
def frame(t):
    im = bg.copy(); im.alpha_composite(rain.layer(t))
    s = 1 + 0.25 * (1 - eo(t / 0.25))
    for img, y in ((L1, 720), (L2, 900)):
        i2 = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
        comp(im, i2, ((W - i2.width) / 2, y - (i2.height - img.height) / 2))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 640), 'NÚMERO DESCONHECIDO', font=f_small, fill=WARM, anchor='mm', stroke_width=5, stroke_fill=INK)
    dx = int(round(9 * math.sin(2 * math.pi * 30 * t))) if (0.05 <= t < 0.4 or 0.6 <= t < 0.95) else 0
    if dx: im = Image.fromarray(np.roll(np.asarray(im), dx, axis=1))
    im = M.apply_mult(im, mult)
    comp(im, kick, ((W - kick.width) // 2, 210))
    return im.convert('RGB')
E.encode('e0', frame, DUR, fade_in=0)
# audio: buzz x2 + low hit + rain bed, then the existing episode audio
n = int(DUR * SR); t = np.arange(n) / SR
rng = np.random.default_rng(5)
a = np.zeros(n + SR)
def tt(d): return np.arange(int(d * SR)) / SR
def buzz(d):
    q = tt(d); return np.tanh(2.5 * np.sin(2 * np.pi * 172 * q)) * np.minimum(1, q / 0.01) * np.minimum(1, (d - q) / 0.03) * 0.5
for st in (0.05, 0.6):
    b = buzz(0.35); i = int(st * SR); a[i:i + len(b)] += b
h = LA.kick(); a[:len(h)] += h * 1.2
r = LA.bandpass(rng.standard_normal(n), 300, 5000); a[:n] += r / np.abs(r).max() * 0.12
a = a[:n]
with wave.open('audio.wav') as w:
    rest = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64).reshape(-1, 2) / 32768
a = np.tanh(a * 1.2) / 1.2; a *= 0.9 / np.abs(a).max() * np.abs(rest).max()
full = np.concatenate([np.stack([a, a], 1), rest])
with wave.open('audio_v2.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((full * 32767).astype(np.int16).tobytes())
with open('list_v2.txt', 'w') as fl:
    for k in ['e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6']: fl.write(f"file '{k}.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list_v2.txt', '-c', 'copy', 'video_v2.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video_v2.mp4', '-i', 'audio_v2.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'quem-bate-a-porta-ep2.part.mp4'], check=True)
os.replace('quem-bate-a-porta-ep2.part.mp4', 'quem-bate-a-porta-ep2.mp4')
print('ok')
