#!/usr/bin/env python3
"""Narration file -> timing2.json for ep2.py (6 scenes, split by the 5 longest pauses).
python3 nar2.py narracao.(mp3|m4a|wav)      optional env BOUNDS=t1,t2,t3,t4,t5 (start of each scene pause, seconds)"""
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, '/home/claude/marmita2')
from ep2 import PAGES, ORDER, WORK
SR, LEAD = 44100, 0.3
MINS = {'s1': 3.2, 's2': 3.4, 's3': 4.0, 's4': 3.8, 's5': 2.4}

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', str(SR), WORK + '/narration.wav'], check=True)
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
if os.environ.get('BOUNDS'):
    bounds = []
    for b in map(float, os.environ['BOUNDS'].split(',')):
        r = min(inner, key=lambda r: abs(r[0] - b)); bounds.append(r)
else:
    bounds = sorted(sorted(inner, key=lambda r: r[1] - r[0], reverse=True)[:5])
print('scene pauses:', [(round(a, 2), round(b - a, 2)) for a, b in bounds])
segs, s0 = [], first
for a, b in bounds: segs.append((s0, a)); s0 = b
segs.append((s0, last))
out = {'durs': {}, 'pages': {}, 'gaps': {}, 'nar': []}
for k, (a, b) in zip(ORDER, segs):
    L = b - a
    out['nar'].append([k, max(0.0, a - 0.04), b + 0.08, LEAD - 0.04])
    if k == 's6':
        out['durs'][k] = round(max(6.5, LEAD + L + 1.4), 3); continue
    p1, p2 = [' '.join(s for s, _ in pg) for pg in PAGES[k]]
    frac = len(p1) / (len(p1) + len(p2))
    cands = [r for r in inner if r[0] > a + 0.1 and r[1] < b - 0.1 and r[1] - r[0] >= 0.06]
    split = min(cands, key=lambda r: abs((r[0] - a) / L - frac)) if cands else (a + L * frac, a + L * frac)
    t1, t2 = LEAD, LEAD + (split[1] - a)
    d1, d2 = split[0] - a, b - split[1]
    n1, n2 = len(p1.split()), len(p2.split())
    out['gaps'][k] = round(min(0.3, max(0.07, 0.8 * min(d1 / n1, d2 / n2))), 3)
    out['pages'][k] = [[round(t1, 3), [[s, list(c)] for s, c in PAGES[k][0]]],
                       [round(t2 - 0.05, 3), [[s, list(c)] for s, c in PAGES[k][1]]]]
    out['durs'][k] = round(max(MINS[k], LEAD + L + 0.45), 3)
json.dump(out, open(WORK + '/timing2.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out['durs']), 'total', round(sum(out['durs'].values()), 2))
