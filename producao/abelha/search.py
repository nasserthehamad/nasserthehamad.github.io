import sys
from sim_abelha import simulate
sp, k, w, sm = float(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
out = []
for seed in range(1, 260):
    r = simulate(seed=seed, speed=sp, k_spawn=k, wander=w, smell=sm, tmax=24)
    if not r['full']:
        continue
    ft = [f[0] for f in r['fills']]
    n = len(ft)
    tail3 = r['full'] - ft[-3]
    tail10 = r['full'] - ft[-10]
    if 21.0 <= r['full'] <= 22.6 and 2.5 <= tail3 and tail10 <= 7.5:
        out.append((seed, round(r['full'], 2), 'meio', round(ft[n // 2], 1), '90%', round(ft[int(n * .9)], 1), 'ult3', round(tail3, 1), 'ult10', round(tail10, 1)))
for o in sorted(out, key=lambda z: -z[8] if not isinstance(z[8], str) else -z[9])[:10]:
    print(o)
print(len(out))
