"""Física do "Será que as abelhas enchem a colmeia?": um favo grande hexagonal (pontudo em cima) cheio de alvéolos
hexagonais. As abelhas voam reto com velocidade constante (com um leve zigue-zague), quicam nas bordas e uma na outra.
Todo alvéolo que uma abelha sobrevoa enche de mel. A cada K alvéolos cheios nasce mais uma abelha. Acaba quando enche."""
import math
import numpy as np

CX, CY = 180.0, 392.0
RB = 150.0                          # raio (centro→vértice) do favo grande, pontudo em cima
CELL = 8.6                          # raio do alvéolo
RS = 6.0
FPS, SUB = 30, 4
SQ3 = math.sqrt(3)
# bordas do hexágono grande (pontudo): normais nos ângulos 0, 60, ..., 300 graus; apótema
APO = RB * SQ3 / 2
NORMALS = np.array([[math.cos(math.radians(a)), math.sin(math.radians(a))] for a in range(0, 360, 60)])


def inside_big(x, y, margin=0.0):
    p = np.stack([x - CX, y - CY], -1)
    return (p @ NORMALS.T).max(-1) <= APO - margin


def make_cells():
    cells = []
    for r in range(-30, 31):
        for q in range(-30, 31):
            x = CX + CELL * SQ3 * (q + r / 2)
            y = CY + CELL * 1.5 * r
            if inside_big(np.array(x), np.array(y), margin=CELL * 0.95):
                cells.append((x, y))
    return np.array(cells)


CELLS = make_cells()


def simulate(seed=1, speed=150.0, k_spawn=25, wander=0.9, tmax=60.0, max_bees=14, smell=0.0, smell_r=70.0):
    rng = np.random.default_rng(seed)
    C = np.array([CX, CY])
    a = rng.uniform(0, 2 * math.pi)
    pos = np.array([[CX, CY]])
    vel = np.array([[math.cos(a), math.sin(a)]]) * speed
    born = [0.0]
    filled = np.full(len(CELLS), -1.0)            # tempo em que encheu (-1 = vazio)
    nfill = 0
    dt = 1.0 / (FPS * SUB)
    t = 0.0
    frames, bounces, fills = [], [], []
    full_t = None
    while t < tmax:
        for _ in range(SUB):
            n = len(pos)
            ang = np.arctan2(vel[:, 1], vel[:, 0]) + rng.normal(0, wander, n) * math.sqrt(dt)
            if smell > 0 and nfill > len(CELLS) * 0.6:
                emp = CELLS[filled < 0]
                if len(emp):
                    dx = emp[None, :, 0] - pos[:, None, 0]; dy = emp[None, :, 1] - pos[:, None, 1]
                    dd = np.hypot(dx, dy)
                    j = dd.argmin(1)
                    near = dd[np.arange(n), j] < smell_r
                    want = np.arctan2(dy[np.arange(n), j], dx[np.arange(n), j])
                    diff = (want - ang + math.pi) % (2 * math.pi) - math.pi
                    ang = ang + np.where(near, np.clip(diff, -smell * dt, smell * dt), 0)
            vel = np.stack([np.cos(ang), np.sin(ang)], 1) * speed
            pos = pos + vel * dt
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
            # bordas do favo
            rel = pos - C
            proj = rel @ NORMALS.T                    # n x 6
            for e in range(6):
                over = proj[:, e] > APO - RS
                for i in np.nonzero(over)[0]:
                    nrm = NORMALS[e]
                    vn = vel[i] @ nrm
                    pos[i] -= nrm * (proj[i, e] - (APO - RS))
                    if vn > 0:
                        vel[i] -= 2 * vn * nrm
                        bounces.append((t, i, float(pos[i, 0]), float(pos[i, 1])))
            # mel: alvéolo sobrevoado enche
            dc = np.hypot(CELLS[None, :, 0] - pos[:, None, 0], CELLS[None, :, 1] - pos[:, None, 1])
            hit = np.nonzero((dc.min(0) < CELL * 0.95) & (filled < 0))[0]
            for c in hit:
                filled[c] = t
                nfill += 1
                fills.append((t, int(c), nfill))
                if nfill % k_spawn == 0 and len(pos) < max_bees:
                    b = rng.uniform(0, 2 * math.pi)
                    pos = np.vstack([pos, CELLS[c]])
                    vel = np.vstack([vel, [math.cos(b) * speed, math.sin(b) * speed]])
                    born.append(t)
            sp = np.hypot(vel[:, 0], vel[:, 1])[:, None]
            vel = vel / sp * speed
            if nfill == len(CELLS):
                full_t = t
                break
            t += dt
        frames.append(dict(t=t, pos=pos.copy(), vel=vel.copy(), n=len(pos), born=list(born), nfill=nfill))
        if full_t is not None:
            break
    return dict(frames=frames, bounces=bounces, fills=fills, filled=filled, full=full_t)


if __name__ == '__main__':
    import sys
    print('alvéolos:', len(CELLS))
    sp = float(sys.argv[1]) if len(sys.argv) > 1 else 150
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    w = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9
    res = []
    for seed in range(1, 41):
        r = simulate(seed=seed, speed=sp, k_spawn=k, wander=w, tmax=45)
        if r['full'] is None:
            res.append((seed, None)); continue
        ft = [f[0] for f in r['fills']]
        n = len(ft)
        res.append((seed, round(r['full'], 1), round(ft[int(n * 0.5)], 1), round(ft[int(n * 0.9)], 1), round(r['full'] - ft[-4], 1)))
    ok = [x for x in res if x[1]]
    print('encheu', len(ok), 'de', len(res), '; tempos:', sorted(x[1] for x in ok))
    print([x for x in ok][:10])
