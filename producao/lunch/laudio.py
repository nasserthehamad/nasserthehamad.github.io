#!/usr/bin/env python3
"""Soundtrack for A Marmita Sumiu: synthesized upbeat groove + comic SFX + optional narration."""
import json, os, sys, wave
import numpy as np

SR = 44100
WORK = '/home/claude/lunch'
ORDER = ['s1', 's2', 's3', 's4a', 's4b', 's5']
DEF_DURS = {'s1': 5.5, 's2': 4.5, 's3': 4.5, 's4a': 4.5, 's4b': 4.5, 's5': 8.0}
rng = np.random.default_rng(7)

def mid(n): return 440.0 * 2 ** ((n - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR

def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (f >= lo) & (f <= hi)
    return np.fft.irfft(X, len(x))

def pluck(f, d=0.6, decay=3.0, harm=6):
    t = tt(d); y = np.zeros_like(t)
    for k in range(1, harm + 1):
        y += (0.7 ** (k - 1)) / k * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (decay + 2.4 * k))
    return y * np.minimum(1, t / 0.003)

def marimba(f, d=0.6):
    t = tt(d)
    y = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 22)
         + 0.12 * np.sin(2 * np.pi * 9.9 * f * t) * np.exp(-t * 45))
    return y * np.minimum(1, t / 0.002)

def kick():
    t = tt(0.3); fr = 48 + 100 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.11)

def clap():
    t = tt(0.25); n = bandpass(rng.standard_normal(len(t)), 900, 5000)
    env = np.exp(-t / 0.06) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return n / np.abs(n).max() * env

def hat():
    t = tt(0.06); n = bandpass(rng.standard_normal(len(t)), 6000, 16000)
    return n / np.abs(n).max() * np.exp(-t / 0.014)

CHORDS = [(60, 64, 67), (59, 62, 67), (57, 60, 64), (57, 60, 65)]
BASS = [48, 43, 45, 41]
MEL = [[72, None, 76, 79, None, 76, 74, None], [74, None, 71, 74, None, 79, 76, None],
       [72, None, 76, 81, None, 79, 76, None], [77, 76, 74, None, 72, None, 69, None]]

def groove(total, full=True):
    """Return a mono music bed of `total` seconds. full=False -> sneaky (drums+bass only)."""
    n = int(total * SR); out = np.zeros(n + SR)
    def add(sig, at, g):
        i = int(at * SR)
        if i >= n: return
        j = min(len(out), i + len(sig)); out[i:j] += sig[:j - i] * g
    bar = 2.0
    K, C, Hh = kick(), clap(), hat()
    for b in range(int(total / bar) + 1):
        t0 = b * bar; ci = b % 4
        for x in (0.0, 1.0): add(K, t0 + x, 0.9)
        if full:
            for x in (0.5, 1.5): add(C, t0 + x, 0.35)
        for k in range(8): add(Hh, t0 + k * 0.25, 0.10 if k % 2 == 0 else 0.18)
        for x, o in ((0.0, 0), (0.75, 0), (1.0, 12), (1.5, 0)):
            add(pluck(mid(BASS[ci] + o), 0.45, decay=5), t0 + x, 0.55 if full else 0.7)
        if full:
            for x in (0.0, 0.5, 0.75, 1.25, 1.5, 1.75):
                for j, nn in enumerate(CHORDS[ci]):
                    add(pluck(mid(nn), 0.5, decay=6, harm=5), t0 + x + j * 0.012, 0.13)
            for k, nn in enumerate(MEL[ci]):
                if nn: add(marimba(mid(nn), 0.5), t0 + k * 0.25, 0.26)
        else:
            for k, nn in enumerate([72, None, None, 75, None, 74, None, None]):
                if nn: add(pluck(mid(nn - 12), 0.25, decay=14, harm=4), t0 + k * 0.25, 0.32)
    return out[:n]

def slide_whistle(d=0.7):
    t = tt(d); f = 1300 * (300 / 1300) ** (t / d) * (1 + 0.02 * np.sin(2 * np.pi * 7 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08) * 0.5

def crash(d=1.2):
    t = tt(d); n = bandpass(rng.standard_normal(len(t)), 3000, 15000)
    return n / np.abs(n).max() * np.exp(-t / 0.35) * 0.35

def thunk():
    t = tt(0.35); n = bandpass(rng.standard_normal(len(t)), 80, 900)
    return (np.sin(2 * np.pi * 90 * t) * np.exp(-t / 0.09) + 0.6 * n / np.abs(n).max() * np.exp(-t / 0.04)) * 0.7

def blip(f0=600, f1=1300, d=0.12, g=0.35):
    t = tt(d); f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (d / 2.5)) * g

def ding(f=1318.5, g=0.3):
    t = tt(0.9)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 6)) * np.exp(-t * 4) * g

def whoosh(d=0.35, g=0.35):
    t = tt(d); n = rng.standard_normal(len(t)); y = np.zeros_like(n)
    for i, (lo, hi) in enumerate([(300, 1200), (900, 3000), (2000, 6000)]):
        seg = bandpass(n, lo, hi); w = np.exp(-((t / d - (0.25 + 0.3 * i)) / 0.18) ** 2); y += seg * w
    return y / np.abs(y).max() * g

def scribble(d=1.3, g=0.16):
    t = tt(d); n = bandpass(rng.standard_normal(len(t)), 2500, 9000)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 11 * t) * np.sin(2 * np.pi * 2.3 * t + 1)
    return n / np.abs(n).max() * np.abs(am) * g * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1)

def tick(g=0.18):
    t = tt(0.05); n = bandpass(rng.standard_normal(len(t)), 2000, 8000)
    return n / np.abs(n).max() * np.exp(-t / 0.006) * g

def step(g=0.22):
    t = tt(0.12); n = bandpass(rng.standard_normal(len(t)), 100, 700)
    return n / np.abs(n).max() * np.exp(-t / 0.03) * g

def tada(g=0.35):
    y = np.zeros(int(1.2 * SR))
    for i, nn in enumerate([72, 76, 79, 84]):
        s = marimba(mid(nn), 0.9); i0 = int(i * 0.07 * SR); y[i0:i0 + len(s)] += s[:len(y) - i0]
    return y * g

def load_wav(path):
    with wave.open(path) as w:
        ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    if ch == 2: a = a.reshape(-1, 2).mean(1)
    assert sr == SR
    return a

def build(path, timing=None):
    durs = dict(DEF_DURS)
    if timing: durs.update(timing.get('durs', {}))
    st, acc = {}, 0.0
    for k in ORDER:
        st[k] = acc; acc += round(durs[k] * 30) / 30
    total = acc; n = int(total * SR)
    sumiu = st['s2'] + (timing.get('s2_sumiu', 2.0) if timing else 2.0)
    music = np.zeros(n)
    g1 = groove(sumiu - 0.02); music[:len(g1)] += g1
    sneaky = groove(st['s5'] - st['s4a'], full=False)
    i = int(st['s4a'] * SR); music[i:i + len(sneaky)] += sneaky
    g3 = groove(total - st['s5']); i = int(st['s5'] * SR); music[i:i + len(g3)] += g3[:n - i]
    fx = np.zeros(n + 2 * SR)
    def add(sig, at):
        i = int(at * SR); fx[i:i + len(sig)] += sig
    for x in (0.1, 0.45, 0.8, 1.15): add(step(), st['s1'] + x)
    add(blip(), st['s1'] + 1.55)
    add(thunk(), st['s2'] + 0.45)
    add(slide_whistle(), sumiu); add(crash(), sumiu)
    add(whoosh(0.25, 0.25), st['s3']); add(scribble(), st['s3'] + 0.5); add(blip(500, 900, 0.1, 0.3), st['s3'] + 1.95)
    for k in range(int((st['s4a'] - sumiu - 0.8) / 0.5)): add(tick(), sumiu + 0.8 + k * 0.5)
    for k in ('s4a', 's4b'):
        add(whoosh(), st[k]); add(ding(1318.5 if k == 's4a' else 1174.7), st[k] + 0.18)
    add(tada(), st['s5']); add(blip(400, 800, 0.1, 0.3), st['s5'] + 0.7); add(blip(450, 900, 0.1, 0.3), st['s5'] + 1.0)
    add(blip(500, 1000, 0.1, 0.3), st['s5'] + 1.7)
    fx = fx[:n]
    nar = np.zeros(n)
    if timing and timing.get('nar'):
        src = load_wav(WORK + '/narration.wav')
        for (k, s0, s1, at) in timing['nar']:
            seg = src[int(s0 * SR):int(s1 * SR)]
            i = int((st[k] + at) * SR); j = min(n, i + len(seg)); nar[i:j] += seg[:j - i]
    # duck music under narration
    env = np.abs(nar)
    if env.max() > 0:
        win = int(0.15 * SR); env = np.convolve(env, np.ones(win) / win, 'same')
        duck = 1 - 0.62 * np.clip(env / (0.02 + 1e-9), 0, 1)
        win2 = int(0.12 * SR); duck = np.convolve(duck, np.ones(win2) / win2, 'same')
        mgain, nargain = 0.42, 1.0
    else:
        duck = np.ones(n); mgain, nargain = 0.6, 0.0
    music *= mgain * duck
    mixm = music + fx * (0.8 if nargain else 1.0) + nar * nargain * (0.9 / max(1e-6, np.abs(nar).max()) if nargain else 0)
    t = np.arange(n) / SR
    mixm *= np.clip((total - t) / 0.6, 0, 1) * np.clip(t / 0.05, 0, 1)
    mixm *= 0.89 / np.abs(mixm).max()
    stereo = np.stack([mixm, mixm], 1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return total

if __name__ == '__main__':
    tj = json.load(open(WORK + '/timing.json')) if os.path.exists(WORK + '/timing.json') else None
    print(build(WORK + '/audio.wav', tj))
