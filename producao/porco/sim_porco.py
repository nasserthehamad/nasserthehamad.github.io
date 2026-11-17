"""Física do "Será que o porco escapa?": cercas redondas concêntricas girando, cada uma com uma porteira aberta.
Os porcos quicam com velocidade constante dentro da cerca ativa (a mais de dentro que ainda está de pé). Quando um porco
passa pela porteira, aquela cerca estoura e o porco que passou vira dois (+1 porco). A última cerca = escapou."""
import math
import numpy as np

CX, CY = 180.0, 384.0
NR = 8
R0, DR = 30.0, 16.0
RADII = [R0 + DR * k for k in range(NR)]
RS = 6.0
FPS, SUB = 30, 4


def ring_angle(k, t, phase):
    w = (0.85 + 0.12 * k) * (1 if k % 2 == 0 else -1)
    return phase[k] + w * t


def simulate(seed=1, speed=150.0, gap_px=None, tmax=60.0, start_ang=None):
    rng = np.random.default_rng(seed)
    phase = rng.uniform(0, 2 * math.pi, NR)
    C = np.array([CX, CY])
    a = rng.uniform(0, 2 * math.pi) if start_ang is None else start_ang
    pos = np.array([[CX, CY]])
    vel = np.array([[math.cos(a), math.sin(a)]]) * speed
    born = [0.0]
    active = 0
    gap_px = gap_px or [30.0] * NR
    dt = 1.0 / (FPS * SUB)
    t = 0.0
    frames, bounces, breaks, nears = [], [], [], []
    esc_t = None
    while t < tmax:
        for _ in range(SUB):
            pos = pos + vel * dt
            n = len(pos)
            # porco x porco (elástico)
            if n > 1:
                d = pos[:, None, :] - pos[None, :, :]
                dist = np.hypot(d[..., 0], d[..., 1]) + np.eye(n) * 1e6
                ii, jj = np.nonzero(np.triu(dist < 2 * RS, 1))
                for i, j in zip(ii, jj):
                    nrm = d[i, j] / dist[i, j]
                    ov = 2 * RS - dist[i, j]
                    pos[i] += nrm * ov / 2; pos[j] -= nrm * ov / 2
                    rv = (vel[i] - vel[j]) @ nrm
                    if rv < 0:
                        vel[i] -= rv * nrm; vel[j] += rv * nrm
            # cerca ativa
            R = RADII[active]
            rel = pos - C
            rr = np.hypot(rel[:, 0], rel[:, 1])
            hit = np.nonzero(rr > R - RS - 1.5)[0]
            broke = False
            for i in hit:
                th = math.atan2(rel[i, 1], rel[i, 0])
                gc = ring_angle(active, t, phase)
                dd = (th - gc + math.pi) % (2 * math.pi) - math.pi
                g = gap_px[active] / 2 / R
                if abs(dd) < g - RS / R * 0.9 and not broke:
                    # passou na porteira: a cerca estoura e ele vira dois
                    breaks.append((t, active, float(pos[i, 0]), float(pos[i, 1])))
                    b = math.atan2(vel[i, 1], vel[i, 0]) + rng.choice([-1, 1]) * rng.uniform(0.5, 0.9)
                    pos = np.vstack([pos, pos[i] - rel[i] / rr[i] * 3])
                    vel = np.vstack([vel, [math.cos(b) * speed, math.sin(b) * speed]])
                    born.append(t)
                    broke = True
                    if active == NR - 1:
                        esc_t = t
                    else:
                        active += 1
                    continue
                nr = rel[i] / rr[i]
                vn = vel[i] @ nr
                if vn > 0:
                    vel[i] -= 2 * vn * nr
                    pos[i] = C + nr * (R - RS - 1.5)
                    bounces.append((t, i, float(pos[i, 0]), float(pos[i, 1]), active))
                    if abs(dd) < g * 2.2:
                        nears.append((t, active, float(dd)))
            # velocidade constante (com um tiquinho de ruído pra não ficar periódico)
            sp = np.hypot(vel[:, 0], vel[:, 1])[:, None]
            vel = vel / sp * speed
            if esc_t is not None:
                break
            t += dt
        frames.append(dict(t=t, pos=pos.copy(), vel=vel.copy(), active=active, n=len(pos), born=list(born)))
        if esc_t is not None:
            break
    return dict(frames=frames, bounces=bounces, breaks=breaks, nears=nears, esc=esc_t, phase=phase, gap_px=gap_px)


if __name__ == '__main__':
    import sys, json
    gp = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None
    durs = [[] for _ in range(NR)]
    esc = []
    for seed in range(1, 81):
        r = simulate(seed=seed, gap_px=gp, tmax=45)
        bt = [0.0] + [b[0] for b in r['breaks']]
        for k in range(len(bt) - 1):
            durs[k].append(bt[k + 1] - bt[k])
        if r['esc']:
            esc.append(r['esc'])
    print('media por cerca:', [round(sum(d) / max(1, len(d)), 2) for d in durs])
    print('escaparam', len(esc), 'mediana', sorted(esc)[len(esc) // 2] if esc else None)
