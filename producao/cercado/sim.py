"""Física do cercado: ovelhas (círculos) num cercado redondo com uma haste girando no centro.
Quando a haste prensa uma ovelha, ela vira duas. Para quando chega em NMAX (a cerca estoura)."""
import math, random
import numpy as np

CX, CY, R = 180.0, 360.0, 140.0     # cercado (px do canvas 360x640)
RS = 8.0                            # raio da ovelha
HW = 3.0                            # meia-largura da haste
FPS, SUB = 30, 4


def simulate(seed=1, omega=2.4, cooldown=0.9, p_split=0.85, nmax=210, tmax=40.0, speed=70.0,
             start=(1.95, 82.0), v_ang=None):
    rng = np.random.default_rng(seed)
    sa, sr = start
    pos = np.array([[CX + sr * math.cos(sa), CY + sr * math.sin(sa)]])
    a0 = rng.uniform(0, 2 * math.pi) if v_ang is None else v_ang
    vel = np.array([[math.cos(a0), math.sin(a0)]]) * speed
    cool = np.zeros(1)
    born = np.zeros(1)
    frames = []
    events = []                      # (t, tipo, x, y, n)
    dt = 1.0 / (FPS * SUB)
    t = 0.0
    burst_t = None
    while t < tmax:
        for _ in range(SUB):
            n = len(pos)
            # passeio: um empurrãozinho aleatório pra elas não pararem
            ang = np.arctan2(vel[:, 1], vel[:, 0]) + rng.normal(0, 0.6, n) * dt * 6
            sp = np.clip(np.hypot(vel[:, 0], vel[:, 1]), 25, 160)
            sp = sp + (speed - sp) * 0.02
            vel = np.stack([np.cos(ang) * sp, np.sin(ang) * sp], 1)
            pos = pos + vel * dt
            # ovelha x ovelha
            if n > 1:
                d = pos[:, None, :] - pos[None, :, :]
                dist = np.hypot(d[..., 0], d[..., 1]) + np.eye(n) * 1e6
                ov = (2 * RS - dist)
                ii, jj = np.nonzero(np.triu(ov > 0, 1))
                if len(ii):
                    nrm = d[ii, jj] / dist[ii, jj, None]
                    push = (ov[ii, jj] * 0.5)[:, None] * nrm
                    np.add.at(pos, ii, push * 0.9)
                    np.add.at(pos, jj, -push * 0.9)
                    rv = ((vel[ii] - vel[jj]) * nrm).sum(1)
                    imp = np.where(rv < 0, rv, 0)[:, None] * nrm
                    np.add.at(vel, ii, -imp)
                    np.add.at(vel, jj, imp)
            # haste girando
            th = omega * t
            u = np.array([math.cos(th), math.sin(th)])
            nperp = np.array([-u[1], u[0]])          # sentido do giro
            rel = pos - np.array([CX, CY])
            s = np.clip(rel @ u, 0, R)
            off = rel @ nperp
            hit = (np.abs(off) < RS + HW) & (s > 6)
            if hit.any():
                side = np.sign(off[hit]); side[side == 0] = 1
                pos[hit] = np.array([CX, CY]) + s[hit, None] * u + (side * (RS + HW))[:, None] * nperp
                rodv = omega * s[hit]                    # velocidade da haste naquele ponto
                vn = vel[hit] @ nperp
                newvn = np.where(side > 0, np.maximum(vn, rodv * 1.05), np.minimum(vn, -0.3 * rodv))
                vel[hit] += (newvn - vn)[:, None] * nperp
                # prensou na frente da haste: vira duas
                front = np.nonzero(hit)[0][side > 0]
                for i in front:
                    if cool[i] <= 0 and (len(pos) < 4 or rng.random() < p_split) and len(pos) < nmax:
                        tang = u * rng.choice([-1, 1])
                        newp = pos[i] + tang * RS * 1.1
                        pos[i] = pos[i] - tang * RS * 1.1
                        a = rng.uniform(0, 2 * math.pi)
                        pos = np.vstack([pos, newp])
                        vel = np.vstack([vel, [math.cos(a) * speed, math.sin(a) * speed]])
                        cool[i] = cooldown
                        cool = np.append(cool, cooldown)
                        born = np.append(born, t)
                        events.append((t, 'split', float(newp[0]), float(newp[1]), len(pos), int(i)))
            # cerca
            rel = pos - np.array([CX, CY])
            rr = np.hypot(rel[:, 0], rel[:, 1])
            out = rr > R - RS
            if out.any():
                nr = rel[out] / rr[out, None]
                pos[out] = np.array([CX, CY]) + nr * (R - RS)
                vr = (vel[out] * nr).sum(1)
                vel[out] -= (np.maximum(vr, 0) * 1.8)[:, None] * nr
            cool -= dt
            t += dt
        strain = float(np.clip((len(pos) / nmax), 0, 1))
        frames.append(dict(t=t, pos=pos.copy(), vel=vel.copy(), born=born.copy(), theta=omega * t, n=len(pos), strain=strain))
        if len(pos) >= nmax and burst_t is None:
            burst_t = t
            break
    return frames, events, burst_t


if __name__ == '__main__':
    import sys
    for seed in range(1, 9):
        fr, ev, bt = simulate(seed=seed)
        counts = [f['n'] for f in fr[::30]]
        print(seed, 'primeira', round(ev[0][0], 2), 'estoura', round(bt, 2) if bt else None, counts)
