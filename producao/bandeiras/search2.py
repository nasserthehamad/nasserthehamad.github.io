import sys
from sim_flags import simulate
sp, gd = float(sys.argv[1]), float(sys.argv[2])
out = []
for seed in range(1, 400):
    r = simulate(seed=seed, speed=sp, gap_deg=gd, tmax=30)
    if not r['end']:
        continue
    e = r['elims']
    duel = e[-1][0] - e[-2][0]
    semi = e[-2][0] - e[-3][0]
    if 20.0 <= r['end'] <= 24.0 and 3.5 <= duel <= 7.0 and e[0][0] >= 0.6 and semi >= 1.0:
        out.append((seed, round(r['end'], 2), round(duel, 1), round(e[0][0], 1), [round(e[k][0], 1) for k in (0, 7, 15, 23, 27, 29)]))
for o in out[:12]:
    print(o)
print(len(out))
