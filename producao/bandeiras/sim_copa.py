"""Copa das bandeiras (versão grande): 48 bolinhas numa arena em forma de estádio (cápsula) com um POÇO DE LAVA no meio.
Quem cai na lava é eliminado. Objetos móveis:
  etapa 1 (48→24): duas pás girando (em cima e embaixo do poço)
  etapa 2 (24→8):  a lava cresce + 3 rebatedores orbitando o poço
  etapa 3 (8→1):   a lava cresce de novo e as paredes vão fechando
A física não sabe de país nenhum; os países são distribuídos depois."""
import math
import numpy as np

CX, CY = 180.0, 404.0
HSEG = 70.0                        # meia-altura do segmento da cápsula (arena em pé)
RC0 = 140.0                        # raio da cápsula
RB = 11.0                          # raio da bolinha
SPIN = [((CX, CY - 116.0), 2.1), ((CX, CY + 116.0), -2.1)]   # (pivô, velocidade angular) das pás
ARM, ARM_W = 48.0, 3.5
BUMP_R, BUMP_ORB, BUMP_W = 10.0, 88.0, 0.75
L1, L2, L3 = 22.0, 33.0, 42.0       # raio da lava em cada etapa
FPS, SUB = 30, 4


def seg_closest(p, a, b):
    ab = b - a
    s = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return a + s[:, None] * ab, s


def simulate(n=48, seed=1, speed=170.0, tmax=60.0, shrink_to=110.0, shrink_dur=6.0, lavas=(15.0, 24.0, 31.0)):
    L1, L2, L3 = lavas
    rng = np.random.default_rng(seed)
    C = np.array([CX, CY])
    A, Bp = np.array([CX, CY - HSEG]), np.array([CX, CY + HSEG])
    # posições iniciais: grade espalhada, longe da lava e das pás
    cand = []
    for y in np.arange(CY - HSEG - RC0 + 16, CY + HSEG + RC0 - 16, 2 * RB + 4):
        for x in np.arange(CX - RC0 + 16, CX + RC0 - 16, 2 * RB + 4):
            p = np.array([x, y])
            cp, _ = seg_closest(p[None], A, Bp)
            if np.hypot(*(p - cp[0])) > RC0 - RB - 6:
                continue
            if np.hypot(*(p - C)) < L1 + RB + 40:
                continue
            if any(np.hypot(*(p - np.array(pv))) < ARM + RB + 4 for pv, _ in SPIN):
                continue
            cand.append(p)
    cand = np.array(cand)
    pick = rng.choice(len(cand), n, replace=False)
    pos = cand[pick].astype(float)
    ang = rng.uniform(0, 2 * math.pi, n)
    vel = np.stack([np.cos(ang), np.sin(ang)], 1) * speed
    alive = np.ones(n, bool)
    out_t = np.full(n, -1.0)
    dt = 1.0 / (FPS * SUB)
    t = 0.0
    stage, ts2, ts3 = 1, None, None
    bphase = rng.uniform(0, 2 * math.pi)
    frames, hits, elims = [], [], []
    end_t = None

    def lava_r(t):
        if ts2 is None:
            return L1
        if ts3 is None:
            return L1 + (L2 - L1) * min(1, (t - ts2) / 1.0)
        return L2 + (L3 - L2) * min(1, (t - ts3) / 1.0)

    def cap_r(t):
        if ts3 is None:
            return RC0
        return RC0 + (shrink_to - RC0) * min(1, (t - ts3) / shrink_dur)

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
            P = pos[idx]
            # pás girando (barra inteira passando pelo pivô)
            for k, (pv, w) in enumerate(SPIN):
                th = w * t
                u = np.array([math.cos(th), math.sin(th)])
                a0, a1 = np.array(pv) - u * ARM, np.array(pv) + u * ARM
                cp, s = seg_closest(P, a0, a1)
                dd = P - cp
                dist = np.hypot(dd[:, 0], dd[:, 1])
                hit = np.nonzero(dist < RB + ARM_W)[0]
                for h in hit:
                    i = idx[h]
                    nr = dd[h] / (dist[h] + 1e-6)
                    pos[i] = cp[h] + nr * (RB + ARM_W)
                    rv_ = cp[h] - np.array(pv)
                    vs = w * np.array([-rv_[1], rv_[0]])        # velocidade da pá naquele ponto
                    vn = (vel[i] - vs) @ nr
                    if vn < 0:
                        vel[i] -= 2 * vn * nr
                        hits.append((t, 'spin', int(i)))
            # rebatedores orbitando (etapa 2 em diante)
            if stage >= 2:
                for k in range(3):
                    a = bphase + BUMP_W * t + k * 2 * math.pi / 3
                    bc = C + BUMP_ORB * np.array([math.cos(a), math.sin(a)])
                    bv = BUMP_W * BUMP_ORB * np.array([-math.sin(a), math.cos(a)])
                    dd = pos[idx] - bc
                    dist = np.hypot(dd[:, 0], dd[:, 1])
                    for h in np.nonzero(dist < RB + BUMP_R)[0]:
                        i = idx[h]
                        nr = dd[h] / (dist[h] + 1e-6)
                        pos[i] = bc + nr * (RB + BUMP_R)
                        vn = (vel[i] - bv) @ nr
                        if vn < 0:
                            vel[i] -= 2 * vn * nr
                            hits.append((t, 'bump', int(i)))
            # parede da arena (cápsula)
            rc = cap_r(t)
            P = pos[idx]
            cp, _ = seg_closest(P, A, Bp)
            dd = P - cp
            dist = np.hypot(dd[:, 0], dd[:, 1])
            for h in np.nonzero(dist > rc - RB)[0]:
                i = idx[h]
                nr = dd[h] / dist[h]
                pos[i] = cp[h] + nr * (rc - RB)
                vn = vel[i] @ nr
                if vn > 0:
                    vel[i] -= 2 * vn * nr
                    hits.append((t, 'wall', int(i)))
            # lava
            lr = lava_r(t)
            dl = np.hypot(pos[idx, 0] - CX, pos[idx, 1] - CY)
            for h in np.nonzero(dl < lr - 2)[0]:
                i = idx[h]
                if alive.sum() <= 1:
                    break
                alive[i] = False
                out_t[i] = t
                elims.append((t, int(i)))
            na = int(alive.sum())
            if stage == 1 and na <= 24:
                stage, ts2 = 2, t
            if stage == 2 and na <= 8:
                stage, ts3 = 3, t
            sp = np.hypot(vel[:, 0], vel[:, 1])[:, None]
            vel = vel / sp * speed
            t += dt
            if na == 1:
                end_t = t
                break
        frames.append(dict(t=t, pos=pos.copy(), vel=vel.copy(), alive=alive.copy(), stage=stage, lava=lava_r(t),
                           cap=cap_r(t), spin=[w * t for _, w in SPIN], bump=bphase + BUMP_W * t))
        if end_t is not None:
            break
    winner = int(np.nonzero(alive)[0][0]) if end_t else None
    return dict(frames=frames, hits=hits, elims=elims, end=end_t, winner=winner, ts2=ts2, ts3=ts3, bphase=bphase)


if __name__ == '__main__':
    import sys, json
    lv = tuple(json.loads(sys.argv[1])) if len(sys.argv) > 1 else (15.0, 24.0, 31.0)
    rows = []
    for seed in range(1, 25):
        r = simulate(seed=seed, tmax=70, lavas=lv)
        if r['end']:
            e = [x[0] for x in r['elims']]
            rows.append((round(r['end'], 1), round(r['ts2'], 1), round(r['ts3'], 1), round(e[-1] - e[-2], 1), round(e[0], 1)))
    rows.sort()
    import statistics
    print('fim mediana', statistics.median([x[0] for x in rows]), 'etapa2', statistics.median([x[1] for x in rows]),
          'etapa3', statistics.median([x[2] for x in rows]))
    print(rows)
