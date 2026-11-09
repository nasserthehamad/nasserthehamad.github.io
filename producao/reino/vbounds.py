#!/usr/bin/env python3
"""Acha as pausas da narração e devolve BOUNDS (9 cortes) e TEND."""
import sys, subprocess, numpy as np
path, off = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
SR = 16000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
x = np.frombuffer(raw, '<i2').astype(np.float64) / 32768
fr = int(0.01 * SR)
n = len(x) // fr
rms = np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(1) + 1e-12)
db = 20 * np.log10(rms / rms.max())
sp = db > -38
idx = np.nonzero(sp)[0]
s0, s1 = idx[0], idx[-1]
gaps = []
i = s0
while i <= s1:
    if not sp[i]:
        j = i
        while j <= s1 and not sp[j]:
            j += 1
        gaps.append((j - i, i, j))
        i = j
    else:
        i += 1
gaps = sorted(sorted(gaps, reverse=True)[:9], key=lambda g: g[1])
print('dur', round(n * 0.01, 2), 'speech', s0 * 0.01, s1 * 0.01, file=sys.stderr)
print('gaps', [(round(a * 0.01, 2), round(b * 0.01, 2), round(c * 0.01, 2)) for a, b, c in gaps], file=sys.stderr)
bounds = [round(c * 0.01 - 0.12 + off, 2) for _, b, c in gaps]
print('BOUNDS=' + ','.join(map(str, bounds)) + f' TEND={round(s1 * 0.01 + off + 1.1, 2)}')
