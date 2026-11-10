#!/usr/bin/env python3
"""Narração do Brasa Ep. 2 -> timing2.json (cenas, chamada nome a nome, falas internas)."""
import sys, json, subprocess, numpy as np
path, off = sys.argv[1], 0.15
SR = 16000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
x = np.frombuffer(raw, '<i2').astype(np.float64) / 32768
fr = int(0.01 * SR); n = len(x) // fr
db = 20 * np.log10(np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(1) + 1e-12) / 1e-9)
db -= db.max()
sp = db > -38
idx = np.nonzero(sp)[0]; s0, s1 = idx[0], idx[-1]
gaps, i = [], s0
while i <= s1:
    if not sp[i]:
        j = i
        while j <= s1 and not sp[j]:
            j += 1
        gaps.append((i * 0.01, j * 0.01)); i = j
    else:
        i += 1
big = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:6])
ends = [g[1] for g in big]          # início da fala de cada cena
starts = [s0 * 0.01] + ends
fins = [g[0] for g in big] + [s1 * 0.01]
print('cenas:', [(round(a, 2), round(b, 2)) for a, b in zip(starts, fins)], file=sys.stderr)
def inner(k, cnt):
    a, b = starts[k], fins[k]
    g = [gg for gg in gaps if a < gg[0] and gg[1] < b]
    return sorted(sorted(g, key=lambda q: q[1] - q[0], reverse=True)[:cnt])
names = inner(1, 14)
roll = [starts[1]] + [g[1] for g in names]
print('chamada:', [round(r, 2) for r in roll], file=sys.stderr)
lead = 0.08
T = {'S2': starts[1], 'S3': starts[2], 'S4': starts[3], 'S4B': starts[4], 'S5': starts[5], 'S6': starts[6]}
T = {k: round(v - lead + off, 3) for k, v in T.items()}
T['ROLL_T'] = [round(r - lead + off, 3) for r in roll]
T['ROLL_T'][0] = T['S2']
r2 = inner(4, 1); T['R2'] = round((r2[0][1] if r2 else starts[4] + 1.5) - lead + off, 3)
b5 = inner(5, 1); T['BANG'] = round((b5[0][1] if b5 else starts[5] + 1.7) - lead + off, 3)
c6 = inner(6, 1); T['C6'] = round((c6[0][1] if c6 else starts[6] + 1.2) - lead + off, 3)
T['S6B'] = round(fins[6] + off + 0.5, 3)
T['TEND'] = round(T['S6B'] + 2.6, 3)
json.dump(T, open(sys.argv[2], 'w'), indent=1)
print(json.dumps(T), file=sys.stderr)
