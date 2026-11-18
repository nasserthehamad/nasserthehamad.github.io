from sim_copa import simulate
out = []
for seed in range(1, 260):
    r = simulate(seed=seed, tmax=40, lavas=(15.0, 24.0, 31.0))
    if not r['end']:
        continue
    e = [x[0] for x in r['elims']]
    duel = e[-1] - e[-2]
    semi = e[-2] - e[-3]
    if 27.0 <= r['end'] <= 32.0 and 3.5 <= duel <= 7.0 and 7.0 <= r['ts2'] <= 10.5 and 15.0 <= r['ts3'] <= 21.0 and semi >= 0.8:
        out.append((seed, round(r['end'], 1), round(r['ts2'], 1), round(r['ts3'], 1), round(duel, 1), round(semi, 1)))
for o in out[:12]:
    print(o)
print(len(out))
