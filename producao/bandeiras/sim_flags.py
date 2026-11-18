"""Eliminatória das bandeiras: N bolinhas (países) quicando com velocidade constante dentro de um anel com uma abertura
que gira. Quem passa pela abertura é eliminado (sai rolando pra fora). A última que sobra é a campeã."""
import math
import numpy as np

CX, CY, R = 180.0, 404.0, 150.0
RB = 11.0
FPS, SUB = 30, 4


def gap_angle(t, phase, omega):
    return phase + omega * t


def simulate(n=32, seed=1, speed=200.0, gap_deg=62.0, omega=1.2, tmax=60.0):
    rng = np.random.default_rng(seed)
    phase = rng.uniform(0, 2 * math.pi)
    C = np.array([CX, CY])
    # posições iniciais em anéis concêntricos, sem encostar
    pos = []
    rings = [(0, 1), (26, 7), (52, 12), (78, 12)]
    for rr, k in rings:
        a0 = rng.uniform(0, 2 * math.pi)
        for j in range(k):
            a = a0 + 2 * math.pi * j / k
            pos.append((CX + rr * math.cos(a), CY + rr * math.sin(a)))
    pos = np.array(pos[:n], float)
    order = rng.permutation(n)                     # qual país fica em cada lugar
    pos = pos[np.argsort(order)]
    ang = rng.uniform(0, 2 * math.pi, n)
    vel = np.stack([np.cos(ang), np.sin(ang)], 1) * speed
    alive = np.ones(n, bool)
    out_t = np.full(n, -1.0)
    g = math.radians(gap_deg) / 2
    dt = 1.0 / (FPS * SUB)
    t = 0.0
    frames, bounces, elims = [], [], []
    end_t = None
    while t < tmax:
        for _ in range(SUB):
            pos = pos + vel * dt
            idx = np.nonzero(alive)[0]
            m = len(idx)
            if m > 1:
                P = pos[idx]
                d = P[:, None, :] - P[None, :, :]
                dist = np.hypot(d[..., 0], d[..., 1]) + np.eye(m) * 1e6
                ii, jj = np.nonzero(np.triu(dist < 2 * RB, 1))
                for a, b in zip(ii, jj):
                    i, j = idx[a], idx[b]
                    nrm = d[a, b] / dist[a, b]
                    ov = 2 * RB - dist[a, b]
                    pos[i] += nrm * ov / 2; pos[j] -= nrm * ov / 2
                    rv = (vel[i] - vel[j]) @ nrm
                    if rv < 0:
                        vel[i] -= rv * nrm; vel[j] += rv * nrm
            ga = gap_angle(t, phase, omega)
            for i in idx:
                rel = pos[i] - C
                rr = math.hypot(*rel)
                if rr > R - RB - 1.5:
                    th = math.atan2(rel[1], rel[0])
                    dd = (th - ga + math.pi) % (2 * math.pi) - math.pi
                    if abs(dd) < g - RB / R * 0.9 and alive.sum() > 1:
                        if rr > R - RB + 2:               # já passou da linha do anel: eliminado
                            alive[i] = False
                            out_t[i] = t
                            elims.append((t, int(i)))
                        continue
                    nr = rel / rr
                    vn = vel[i] @ nr
                    if vn > 0:
                        vel[i] -= 2 * vn * nr
                        pos[i] = C + nr * (R - RB - 1.5)
                        bounces.append((t, int(i)))
            sp = np.hypot(vel[:, 0], vel[:, 1])[:, None]
            vel = vel / sp * speed
            t += dt
            if alive.sum() == 1 and end_t is None:
                end_t = t
                break
        frames.append(dict(t=t, pos=pos.copy(), vel=vel.copy(), alive=alive.copy(), gap=gap_angle(t, phase, omega)))
        if end_t is not None:
            break
    winner = int(np.nonzero(alive)[0][0]) if end_t else None
    return dict(frames=frames, bounces=bounces, elims=elims, end=end_t, winner=winner, out_t=out_t, phase=phase,
                g=g, omega=omega)


if __name__ == '__main__':
    import sys
    ts = []
    for seed in range(1, 31):
        r = simulate(seed=seed, tmax=45)
        if r['end']:
            e = [x[0] for x in r['elims']]
            ts.append((round(r['end'], 1), round(e[0], 1), round(e[-1] - e[-2], 1)))
    ts.sort()
    print(len(ts), ts)
