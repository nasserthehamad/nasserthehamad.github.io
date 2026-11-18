import sys
from sim_porco import simulate
import json
GP = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [41, 26, 23.5, 26, 33, 32, 33.5, 22]
out = []
for seed in range(1, 700):
    r = simulate(seed=seed, gap_px=GP, tmax=26)
    if not r['esc']:
        continue
    bt = [b[0] for b in r['breaks']]
    d = [bt[0]] + [bt[k] - bt[k - 1] for k in range(1, len(bt))]
    nl = sum(1 for x in r['nears'] if x[1] == 7)
    if 20.6 <= r['esc'] <= 23.2 and 0.4 <= bt[0] <= 2.0 and 4.0 <= d[-1] <= 8.0 and max(d[:-1]) <= 5.5:
        out.append((seed, round(r['esc'], 2), [round(x, 1) for x in bt], round(d[-1], 1), nl))
import statistics
for o in sorted(out, key=lambda z: statistics.pstdev([z[2][0]] + [z[2][k] - z[2][k - 1] for k in range(1, len(z[2]) - 1)]))[:12]:
    print(o)
print(len(out))
