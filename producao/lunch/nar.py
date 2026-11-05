#!/usr/bin/env python3
"""Split the narration into scenes by its long pauses and write timing.json for lunch.py / laudio.py."""
import json, subprocess, sys, wave
import numpy as np
SR = 44100; WORK = '/home/claude/lunch'
A, Wt = [255, 196, 104], [244, 244, 248]
PAGES = {
    's1': [('Meio-dia e um!', A), ('O Léo foi pegar a lasanha que a vó dele fez.', Wt)],
    's2': [('Abriu a geladeira e…', Wt), ('a marmita|SUMIU!', A)],
    's3': [('No lugar, só um bilhete:', Wt), ('“tava uma delícia”.', A)],
    's4a': [('Suspeita A: Ju do RH.', Wt), ('Ela tá com um cheirinho de lasanha…', Wt)],
    's4b': [('Suspeito B: Seu Carlos, o chefe.', Wt), ('Tem molho na gravata!', Wt)],
}
MINS = {'s1': 4.2, 's2': 3.8, 's3': 4.0, 's4a': 3.6, 's4b': 3.6}
ORDER = ['s1', 's2', 's3', 's4a', 's4b', 's5']
LEAD = 0.3

src = sys.argv[1]
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR), WORK + '/narration.wav'], check=True)
with wave.open(WORK + '/narration.wav') as w:
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
hop = int(0.01 * SR)
rms = np.sqrt(np.convolve(x * x, np.ones(hop * 3) / (hop * 3), 'same'))[::hop]
db = 20 * np.log10(rms / rms.max() + 1e-9)
loud = db > -38
runs, i = [], 0
while i < len(loud):
    if not loud[i]:
        j = i
        while j < len(loud) and not loud[j]: j += 1
        runs.append((i * 0.01, j * 0.01)); i = j
    else: i += 1
first = next(k for k in range(len(loud)) if loud[k]) * 0.01
last = (len(loud) - next(k for k in range(len(loud)) if loud[::-1][k])) * 0.01
inner = [r for r in runs if r[0] > first and r[1] < last]
bounds = sorted(sorted(inner, key=lambda r: r[1] - r[0], reverse=True)[:5])
print('scene pauses:', [(round(a, 2), round(b - a, 2)) for a, b in bounds])
segs, s0 = [], first
for a, b in bounds: segs.append((s0, a)); s0 = b
segs.append((s0, last))
out = {'durs': {}, 'pages': {}, 'gaps': {}, 'nar': []}
for k, (a, b) in zip(ORDER, segs):
    L = b - a
    out['nar'].append([k, max(0, a - 0.04), b + 0.08, LEAD - 0.04])
    if k == 's5':
        out['durs'][k] = max(7.0, LEAD + L + 1.6); continue
    p1, p2 = PAGES[k]
    frac = len(p1[0]) / (len(p1[0]) + len(p2[0].replace('|', ' ')))
    cands = [r for r in inner if r[0] > a + 0.1 and r[1] < b - 0.1 and r[1] - r[0] >= 0.06]
    split = min(cands, key=lambda r: abs((r[0] - a) / L - frac)) if cands else (a + L * frac, a + L * frac)
    t1, t2 = LEAD, LEAD + (split[1] - a)
    d1, d2 = split[0] - a, b - split[1]
    n1, n2 = len(p1[0].split()), len(p2[0].replace('|', ' ').split())
    out['gaps'][k] = round(min(0.3, max(0.07, 0.8 * min(d1 / n1, d2 / n2))), 3)
    pg2 = [[p2[0], p2[1]]]
    if '|' in p2[0]:
        x1, x2 = p2[0].split('|')
        pg2 = [[x1, Wt], [x2, A]]
        out['s2_sumiu'] = round(t2 + d2 * 0.42, 3)
    out['pages'][k] = [[round(t1, 3), [[p1[0], p1[1]]]], [round(t2 - 0.05, 3), pg2]]
    out['durs'][k] = round(max(MINS[k], LEAD + L + 0.5), 3)
json.dump(out, open(WORK + '/timing.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out['durs']), 'sumiu', out.get('s2_sumiu'))
