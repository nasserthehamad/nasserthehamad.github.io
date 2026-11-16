"""Física do cercado v2: a ovelha só vira duas quando fica ESPREMIDA entre a ponta da haste e um bloco (a prensa) preso
na cerca. A haste é mais curta que o cercado: quem está no vão perto da cerca ou mais pra dentro escapa. Fator sorte.
Para quando chega em NMAX (a cerca estoura)."""
import math
import numpy as np

CX, CY, R = 180.0, 360.0, 140.0     # cercado (px do canvas 360x640)
RS = 8.0                            # raio da ovelha
HW = 3.0                            # meia-largura da haste
HB = 6.0                            # meia-largura do bloco da prensa
FPS, SUB = 30, 4


def seg_dist(pos, a, b):
    """distância de cada ponto ao segmento a-b, ponto mais próximo e parâmetro (0..1)."""
    ab = b - a
    L2 = ab @ ab
    s = np.clip(((pos - a) @ ab) / L2, 0, 1)
    cp = a + s[:, None] * ab
    d = pos - cp
    dist = np.hypot(d[:, 0], d[:, 1])
    return dist, cp, d, s


def simulate(seed=1, omega=2.4, gap=24.0, anvils=(-90.0,), nmax=240, tmax=45.0, speed=80.0,
             theta0=None, first=True, fling=0.25, lb=60.0, t_first=0.6, rest=0.3):
    rng = np.random.default_rng(seed)
    C = np.array([CX, CY])
    L = R - gap                                   # comprimento da haste
    AV = [math.radians(a) for a in anvils]
    if theta0 is None:
        theta0 = AV[0] - omega * t_first          # a haste chega na 1ª prensa em t_first
    # 1ª ovelha: no ponto da prensa, um pouco antes do bloco
    if first:
        rf = R - lb / 2 - gap / 2
        a = AV[0] - (HB + RS + 1) / rf
        pos = np.array([[CX + rf * math.cos(a), CY + rf * math.sin(a)]])
        vel = np.array([[-math.sin(a), math.cos(a)]]) * 30.0
    else:
        a = rng.uniform(0, 2 * math.pi)
        pos = np.array([[CX + 60 * math.cos(a), CY + 60 * math.sin(a)]])
        vel = np.array([[math.cos(a), math.sin(a)]]) * speed
    born = np.zeros(1)
    frames, events, passes = [], [], []
    dt = 1.0 / (FPS * SUB)
    t = 0.0
    burst_t = None
    last_th = theta0
    while t < tmax:
        for _ in range(SUB):
            n = len(pos)
            ang = np.arctan2(vel[:, 1], vel[:, 0]) + rng.normal(0, 0.6, n) * dt * 6
            sp = np.clip(np.hypot(vel[:, 0], vel[:, 1]), 25, 260)
            sp = sp + (speed - sp) * 0.03
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
            th = theta0 + omega * t
            u = np.array([math.cos(th), math.sin(th)])
            fwd = np.array([-u[1], u[0]])
            # prensas (blocos fixos)
            for av in AV:
                ua = np.array([math.cos(av), math.sin(av)])
                a0, a1 = C + ua * (R - lb), C + ua * (R + 2)
                dist, cp, dd, _ = seg_dist(pos, a0, a1)
                hit = dist < RS + HB
                if hit.any():
                    nr = dd[hit] / (dist[hit, None] + 1e-6)
                    pos[hit] = cp[hit] + nr * (RS + HB)
                    vn = (vel[hit] * nr).sum(1)
                    vel[hit] -= (np.minimum(vn, 0) * 1.6)[:, None] * nr
            # haste
            dist, cp, dd, s = seg_dist(pos, C + u * 4, C + u * L)
            hit = dist < RS + HW
            if hit.any():
                nr = dd[hit] / (dist[hit, None] + 1e-6)
                pos[hit] = cp[hit] + nr * (RS + HW)
                rodv = omega * (4 + s[hit] * (L - 4))
                vrod = rodv[:, None] * fwd
                rel = vel[hit] - vrod
                vn = (rel * nr).sum(1)
                vel[hit] -= (np.minimum(vn, 0) * (1 + rest))[:, None] * nr
                # quem é empurrado escorrega pra fora (força centrífuga)
                vel[hit] += (fling * rodv)[:, None] * u
            # PRENSOU: encostada na ponta da haste e no bloco ao mesmo tempo, com a haste chegando no bloco
            for av in AV:
                dlt = (av - th) % (2 * math.pi)
                if not (0 < dlt < 0.7):
                    continue
                ua = np.array([math.cos(av), math.sin(av)])
                fa = np.array([-ua[1], ua[0]])
                a0, a1 = C + ua * (R - lb), C + ua * (R + 2)
                da, _, _, _ = seg_dist(pos, a0, a1)
                dr, cpr, _, _ = seg_dist(pos, C + u * 4, C + u * L)
                rel = pos - C
                ang_s = (np.arctan2(rel[:, 1], rel[:, 0]) - th) % (2 * math.pi)
                pin = (da < RS + HB + 1.5) & (dr < RS + HW + 1.5) & (ang_s < dlt + 0.2)
                for i in np.nonzero(pin)[0]:
                    if len(pos) >= nmax:
                        break
                    r_s = float(np.clip(np.hypot(*rel[i]), R - lb, L))
                    px, py = pos[i]
                    pa = C + u * min(r_s, L - 1) - fwd * (HW + RS + 1.0)            # sai por trás da haste
                    pb = C + ua * r_s + fa * (HB + RS + 1.0)                       # sai do outro lado do bloco
                    pos[i] = pa
                    vel[i] = -fwd * speed * 0.9 + u * 20
                    pos = np.vstack([pos, pb])
                    vel = np.vstack([vel, fa * speed * 1.3])
                    born = np.append(born, t)
                    events.append((t, float(px), float(py), len(pos), int(i), len(pos) - 1))
            # cerca
            rel = pos - C
            rr = np.hypot(rel[:, 0], rel[:, 1])
            out = rr > R - RS
            if out.any():
                nr = rel[out] / rr[out, None]
                pos[out] = C + nr * (R - RS)
                vr = (vel[out] * nr).sum(1)
                vel[out] -= (np.maximum(vr, 0) * 1.8)[:, None] * nr
            # passagem da haste por um bloco (pra contar acertos/erros)
            for k, av in enumerate(AV):
                if (av - last_th) % (2 * math.pi) > (av - th) % (2 * math.pi) + 1e-9 or \
                        ((av - last_th) % (2 * math.pi) < 1e-9):
                    pass
                if ((av - last_th) % (2 * math.pi)) < ((th - last_th) % (2 * math.pi)) + 1e-12 and t > 0:
                    passes.append((t, k))
            last_th = th
            t += dt
        frames.append(dict(t=t, pos=pos.copy(), vel=vel.copy(), born=born.copy(), theta=theta0 + omega * t, n=len(pos)))
        if len(pos) >= nmax and burst_t is None:
            burst_t = t
            break
    return frames, events, burst_t, passes, theta0


def catches(events, passes, win=0.35):
    """quantas ovelhas novas em cada passagem da haste por um bloco."""
    out = []
    for (tp, k) in passes:
        c = sum(1 for e in events if tp - win <= e[0] <= tp + 0.05)
        out.append(c)
    return out


if __name__ == '__main__':
    import sys, json
    cfgs = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [{}]
    for cfg in cfgs:
        print(cfg)
        for seed in cfg.pop('seeds', (1, 2, 3, 4)) if False else (cfg.get('_seeds') or (1, 2, 3, 4)):
            fr, ev, bt, ps, th0 = simulate(seed=seed, **{k: v for k, v in cfg.items() if k != '_seeds'})
            cs = catches(ev, ps)
            print('  seed', seed, 'primeira', round(ev[0][0], 2) if ev else None, 'estoura', round(bt, 1) if bt else None,
                  'n/s', [f['n'] for f in fr[::30]][:30], 'pegas', cs[:14])
