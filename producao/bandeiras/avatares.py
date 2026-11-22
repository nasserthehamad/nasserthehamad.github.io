"""Bolinhas com o rosto de cada morador de Brasa (22x22, mesmo formato de flags.ball)."""
import sys, os
import numpy as np
sys.path.insert(0, os.environ.get('REINO', '/home/claude/reino'))
import folk as F

N = 22
yy, xx = np.mgrid[0:N, 0:N]
SKINS = np.array(F.SKINS, np.float32)


def _face_box(a):
    rgb, al = a[..., :3], a[..., 3] > 0.5
    d = np.min(np.abs(rgb[:, :, None, :] - SKINS[None, None]).sum(-1), -1)
    skin = al & (d < 6)
    skin[24:] = False                                  # só a cabeça (mãos ficam embaixo)
    ys, xs = np.nonzero(skin)
    if len(ys) == 0:
        top = np.nonzero(al.any(1))[0][0]
        return top + 9, 15
    return int(round(ys.mean())), int(round(xs.mean()))


def _body_color(a):
    rgb, al = a[..., :3], a[..., 3] > 0.5
    reg = rgb[26:32][al[26:32]]
    if len(reg) == 0:
        return np.array((120, 100, 90), np.float32)
    cols, cnt = np.unique(reg.astype(int), axis=0, return_counts=True)
    return cols[cnt.argmax()].astype(np.float32)


def avatar(name, role):
    a = F.folk(name, role or ('moradora' if name == 'Lila' else 'morador'), 0).astype(np.float32)
    fy, fx = _face_box(a)
    body = _body_color(a)
    out = np.zeros((N, N, 3), np.float32)
    r = np.hypot(xx - 10.5, yy - 10.5)
    m = r <= 10.6
    out[:] = body
    out[yy > 15] = body * 0.82                          # "ombros" mais escuros embaixo
    # cabeça: recorte 18x18 centrado no rosto, levemente acima do centro da bola
    oy, ox = fy - 9, fx - 9
    for y in range(N):
        for x in range(N):
            sy, sx = oy + (y - 2), ox + (x - 2)
            if 0 <= sy < a.shape[0] and 0 <= sx < a.shape[1] and a[sy, sx, 3] > 0.5 and sy < fy + 6:
                out[y, x] = a[sy, sx, :3]
    lit = -((xx - 11) + (yy - 11)) / 15
    out = out * (0.86 + 0.18 * np.clip(lit, -1, 1))[..., None]
    out[(np.hypot(xx - 5.5, yy - 5) < 1.3)] = (255, 255, 255)
    ring = (r > 10.6) & (r <= 11.6)
    res = np.zeros((N, N, 3), np.float32)
    res[m] = out[m]
    res[ring] = (30, 22, 26)
    return np.clip(res, 0, 255).astype(np.uint8), (m | ring)


if __name__ == '__main__':
    from PIL import Image
    os.environ.setdefault('N', '86')
    import ep8 as X8
    named = [p for p in X8.PEOPLE if not p[0].startswith('anon')]
    sheet = np.zeros((26 * 7, 26 * 9, 3), np.uint8) + 60
    for k, (n, r) in enumerate(named):
        rgb, m = avatar(n, r)
        y0, x0 = (k // 9) * 26 + 2, (k % 9) * 26 + 2
        sheet[y0:y0 + N, x0:x0 + N][m] = rgb[m]
    Image.fromarray(sheet).resize((sheet.shape[1] * 5, sheet.shape[0] * 5), 0).save(sys.argv[1])
