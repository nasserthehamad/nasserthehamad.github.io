import sys
from sim_porco import simulate
GP = [41, 34, 32, 37, 51, 50, 53, 31]
out = []
for seed in range(1, 500):
    r = simulate(seed=seed, gap_px=GP, tmax=26)
    if not r['esc']:
        continue
    bt = [b[0] for b in r['breaks']]
    d = [bt[0]] + [bt[k] - bt[k - 1] for k in range(1, len(bt))]
    nl = sum(1 for x in r['nears'] if x[1] == 7)
    if 20.6 <= r['esc'] <= 23.2 and 0.5 <= bt[0] <= 1.8 and d[-1] >= 4.0 and max(d[:-1]) < 4.2:
        out.append((seed, round(r['esc'], 2), [round(x, 1) for x in bt], round(d[-1], 1), nl))
for o in sorted(out, key=lambda z: -z[4])[:12]:
    print(o)
print(len(out))
