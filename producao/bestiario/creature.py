#!/usr/bin/env python3
"""Bestiário — cada nome vira uma criatura em pixel art, sempre a mesma pro mesmo nome.
Tudo sai do crc32 do nome normalizado (minúsculo, sem acento): tipo, corpo, traços, raridade, status e nome da espécie."""
import hashlib, json, math, os, random, unicodedata, zlib
import numpy as np
from PIL import Image, ImageDraw

S = 40  # lado do sprite

TYPES = {
    #  nome      base            claro           escuro         destaque        barriga         sufixo
    'FOGO':    ((232, 92, 52), (255, 156, 84), (150, 44, 36), (255, 214, 72), (255, 214, 160), 'flama'),
    'ÁGUA':    ((58, 136, 222), (120, 196, 255), (34, 70, 150), (180, 240, 255), (200, 236, 255), 'maré'),
    'PLANTA':  ((84, 176, 82), (150, 220, 112), (40, 106, 56), (255, 120, 160), (214, 240, 170), 'folha'),
    'PEDRA':   ((150, 128, 104), (198, 178, 146), (92, 76, 64), (120, 200, 220), (210, 196, 170), 'rocha'),
    'RAIO':    ((246, 204, 52), (255, 240, 130), (180, 128, 30), (120, 90, 220), (255, 246, 196), 'raio'),
    'SOMBRA':  ((92, 66, 140), (140, 108, 196), (46, 32, 78), (120, 255, 200), (170, 150, 210), 'breu'),
    'GELO':    ((150, 214, 236), (220, 248, 255), (78, 132, 178), (90, 120, 255), (236, 250, 255), 'neve'),
    'CRISTAL': ((226, 110, 196), (255, 176, 236), (140, 52, 128), (120, 250, 255), (255, 210, 240), 'cristal'),
}
TYPE_NAMES = list(TYPES)
BODIES = ['bolha', 'fera', 'ave', 'dragão', 'golem']
RARITIES = [('COMUM', 40), ('INCOMUM', 30), ('RARO', 17), ('ÉPICO', 9), ('LENDÁRIO', 4)]
RAR_COL = {'COMUM': (206, 206, 214), 'INCOMUM': (96, 214, 96), 'RARO': (72, 156, 255), 'ÉPICO': (184, 96, 255),
           'LENDÁRIO': (255, 150, 40)}
OUTC = (24, 18, 30)
C_GLOW = {3: (184, 96, 255), 4: (255, 176, 50)}


def norm(name):
    s = unicodedata.normalize('NFKD', name.strip().lower())
    return ''.join(c for c in s if not unicodedata.combining(c) and (c.isalnum() or c == ' '))


def h32(name, salt=''):
    return int.from_bytes(hashlib.blake2b((salt + '|' + norm(name)).encode(), digest_size=8).digest(), 'big')


# nome da espécie: começo que lembra o elemento + final que lembra a forma (não usa o nome da pessoa)
SP_PRE = {
    'FOGO': ['IGN', 'CHAM', 'LAV', 'BRAS', 'ARD', 'FULG'],
    'ÁGUA': ['AQU', 'MAR', 'OND', 'HIDR', 'NAU', 'CORAL'],
    'PLANTA': ['FOL', 'RAM', 'FLOR', 'SILV', 'MUSG', 'SEIV'],
    'PEDRA': ['ROK', 'GRAN', 'LIT', 'BASALT', 'TERR', 'CASC'],
    'RAIO': ['VOLT', 'TRON', 'FAISC', 'ZAP', 'ELETR', 'TROV'],
    'GELO': ['GLAC', 'NEV', 'CRIO', 'GEL', 'BOR', 'FROST'],
    'SOMBRA': ['UMBR', 'NOX', 'NEBL', 'VULT', 'ECLIP', 'SPECTR'],
    'CRISTAL': ['QUARTZ', 'LUM', 'PRISM', 'GEM', 'AMETIST', 'OPAL'],
}
SP_SUF = {
    'bolha': ['IX', 'OLO', 'UBA', 'IM', 'OTE'],
    'fera': ['AX', 'OX', 'ORA', 'UZ', 'INO'],
    'ave': ['ILO', 'IRA', 'ÁRIO', 'ÉRIO', 'ÍDEO'],
    'dragão': ['DRAK', 'UR', 'OTH', 'DRAGO', 'AXIS'],
    'golem': ['GOR', 'ON', 'ATH', 'DOR', 'ULO'],
}
VOW = 'AEIOUÁÉÍÓÚ'


# pedaços que não podem aparecer em nome de criatura (palavrão, ofensa ou parecido)
BAD = ('PIRU', 'PIROC', 'CU', 'BOST', 'MERD', 'PUT', 'CACET', 'PINT', 'XOT', 'BUCET', 'PORR', 'MARIC', 'VIAD', 'BICH',
       'PENIS', 'ANUS', 'TETA', 'ROLA', 'PICA', 'FODA', 'CORN', 'GAY', 'NAZI', 'KKK')


def species(name, typ, body):
    r = random.Random(h32(name, 'sp'))
    for _ in range(30):
        pre = r.choice(SP_PRE[typ])
        suf = r.choice(SP_SUF[body])
        if pre[-1] not in VOW and suf[0] not in VOW:
            pre += r.choice('AIO')
        elif pre[-1] in VOW and suf[0] in VOW:
            suf = suf[1:]
        out = pre + suf
        if not any(b in norm(out).upper() for b in BAD):
            return out
    return out


WHEELS = {
    'ELEMENTO': [('FOGO', 18), ('ÁGUA', 18), ('PLANTA', 18), ('PEDRA', 14), ('RAIO', 12), ('GELO', 10), ('SOMBRA', 6),
                 ('CRISTAL', 4)],
    'RARIDADE': RARITIES,
    'FORMA': [('BOLHA', 20), ('FERA', 20), ('AVE', 20), ('DRAGÃO', 20), ('GOLEM', 20)],
    'ATRIB': [(str(v), w) for v, w in zip(range(1, 11), (4, 6, 9, 12, 15, 15, 13, 11, 9, 6))],
}
RAR_BONUS = {'COMUM': 0, 'INCOMUM': 8, 'RARO': 15, 'ÉPICO': 22, 'LENDÁRIO': 30}


_OV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overrides.json')


def overrides():
    """Resultados forçados por decisão editorial (ex.: o sorteado do #001 ganhou LENDÁRIO). Ficam registrados em overrides.json."""
    try:
        return json.load(open(_OV_PATH))
    except Exception:
        return {}


def spin(name, wheel, salt):
    ov = overrides().get(norm(name), {})
    if wheel == 'RARIDADE' and 'rarity' in ov:
        for i, (lab, p) in enumerate(WHEELS[wheel]):
            if lab == ov['rarity']:
                return i, lab, p
    """Resultado determinístico de uma roleta: (índice, rótulo, %)."""
    roll = h32(name, salt) % 100
    acc = 0
    for i, (lab, p) in enumerate(WHEELS[wheel]):
        acc += p
        if roll < acc:
            return i, lab, p
    return len(WHEELS[wheel]) - 1, WHEELS[wheel][-1][0], WHEELS[wheel][-1][1]


def traits(name):
    h = h32(name)
    r = random.Random(h)
    _, typ, p_el = spin(name, 'ELEMENTO', 'el')
    _, rar, p_ra = spin(name, 'RARIDADE', 'rar')
    _, forma, p_fo = spin(name, 'FORMA', 'fo')
    stats, pst = {}, {}
    for k, salt in (('FORÇA', 'f'), ('VELOCIDADE', 'v'), ('MAGIA', 'm')):
        _, v, pv = spin(name, 'ATRIB', salt)
        stats[k], pst[k] = int(v), pv
    lvl = {'COMUM': 0, 'INCOMUM': 1, 'RARO': 2, 'ÉPICO': 3, 'LENDÁRIO': 4}[rar]
    total = round(sum(stats.values()) / 30 * 70) + RAR_BONUS[rar]
    body = {'BOLHA': 'bolha', 'FERA': 'fera', 'AVE': 'ave', 'DRAGÃO': 'dragão', 'GOLEM': 'golem'}[forma]
    return dict(name=name, type=typ, rarity=rar, body=body, forma=forma, stats=stats, total=total,
                pct={'ELEMENTO': p_el, 'RARIDADE': p_ra, 'FORMA': p_fo, **pst},
                species=species(name, typ, body),
                eyes=r.choice([2, 2, 2, 1, 3]) if lvl >= 1 else r.choice([2, 2, 1]),
                ears=r.choice(['pontuda', 'redonda', 'chifre', 'antena', 'nenhuma']),
                mouth=r.choice(['sorriso', 'presas', 'bico_o', 'linha']),
                spots=r.random() < 0.5, seed=h, lvl=lvl)


def _ell(d, cx, cy, rx, ry, fill):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill)


def draw(name, frame=0):
    """RGBA 40x40 (uint8). frame 0/1 = respiração."""
    t = traits(name)
    base, light, dark, acc, belly, _ = TYPES[t['type']]
    r = random.Random(t['seed'] + 7)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = S // 2
    bob = frame
    B = t['body']
    typ = t['type']
    # ---- corpo
    head_c, head_r = None, None
    if B == 'bolha':
        _ell(d, cx, 25 + bob, 13, 11 - bob, base)
        _ell(d, cx, 28 + bob, 8, 6, belly)
        for fx in (cx - 7, cx + 7):
            _ell(d, fx, 36, 3, 2, dark)
        head_c, head_r = (cx, 22 + bob), 10
    elif B == 'fera':
        for fx in (cx - 9, cx + 9):
            d.rectangle((fx - 2, 30, fx + 2, 37), fill=dark)
        _ell(d, cx, 29 + bob, 12, 7, base)
        _ell(d, cx, 31 + bob, 6, 4, belly)
        for fx in (cx - 5, cx + 5):
            d.rectangle((fx - 2, 32, fx + 2, 38), fill=base)
            d.rectangle((fx - 2, 37, fx + 2, 38), fill=dark)
        _ell(d, cx, 18 + bob, 10, 9, base)
        head_c, head_r = (cx, 18 + bob), 9
    elif B == 'ave':
        wing = 3 if frame else 0
        d.polygon([(cx - 9, 22 + bob), (cx - 19, 18 + bob - wing), (cx - 17, 30 + bob), (cx - 9, 31 + bob)], fill=dark)
        d.polygon([(cx + 9, 22 + bob), (cx + 19, 18 + bob - wing), (cx + 17, 30 + bob), (cx + 9, 31 + bob)], fill=dark)
        _ell(d, cx, 26 + bob, 11, 10, base)
        _ell(d, cx, 29 + bob, 7, 6, belly)
        for fx in (cx - 4, cx + 4):
            d.line((fx, 36, fx, 38), fill=acc)
            d.line((fx - 1, 38, fx + 1, 38), fill=acc)
        head_c, head_r = (cx, 20 + bob), 9
    elif B == 'dragão':
        d.polygon([(cx + 9, 32), (cx + 17, 30), (cx + 19, 24), (cx + 15, 27), (cx + 9, 28)], fill=base)
        d.polygon([(cx - 8, 20 + bob), (cx - 18, 10 + bob), (cx - 17, 24 + bob)], fill=dark)
        d.polygon([(cx + 8, 20 + bob), (cx + 18, 10 + bob), (cx + 17, 24 + bob)], fill=dark)
        _ell(d, cx, 28 + bob, 10, 9, base)
        _ell(d, cx, 30 + bob, 6, 6, belly)
        for fx in (cx - 6, cx + 6):
            _ell(d, fx, 36, 3, 2, dark)
        _ell(d, cx, 17 + bob, 9, 8, base)
        head_c, head_r = (cx, 17 + bob), 8
    else:  # golem
        d.rectangle((cx - 15, 18 + bob, cx - 11, 32 + bob), fill=dark)
        d.rectangle((cx + 11, 18 + bob, cx + 15, 32 + bob), fill=dark)
        d.rectangle((cx - 10, 17 + bob, cx + 10, 34), fill=base)
        d.rectangle((cx - 6, 24 + bob, cx + 6, 31), fill=belly)
        d.rectangle((cx - 9, 34, cx - 4, 38), fill=dark)
        d.rectangle((cx + 4, 34, cx + 9, 38), fill=dark)
        d.rectangle((cx - 8, 6 + bob, cx + 8, 18 + bob), fill=base)
        head_c, head_r = (cx, 12 + bob), 8
    hx, hy = head_c
    top = hy - head_r
    # ---- orelhas / chifres
    E = t['ears']
    if E == 'pontuda':
        for s_ in (-1, 1):
            d.polygon([(hx + s_ * 3, top + 3), (hx + s_ * 8, top - 6), (hx + s_ * 9, top + 5)], fill=base)
            d.polygon([(hx + s_ * 5, top + 2), (hx + s_ * 8, top - 3), (hx + s_ * 8, top + 3)], fill=belly)
    elif E == 'redonda':
        for s_ in (-1, 1):
            _ell(d, hx + s_ * 7, top + 1, 3, 3, base)
            _ell(d, hx + s_ * 7, top + 1, 1, 1, belly)
    elif E == 'chifre':
        for s_ in (-1, 1):
            d.polygon([(hx + s_ * 3, top + 2), (hx + s_ * 7, top - 7), (hx + s_ * 6, top + 3)], fill=acc)
    elif E == 'antena':
        for s_ in (-1, 1):
            d.line((hx + s_ * 3, top + 1, hx + s_ * 6, top - 6), fill=dark)
            _ell(d, hx + s_ * 6, top - 7, 1, 1, acc)
    # ---- marca do tipo
    if typ == 'FOGO':
        fl = 1 if frame else 0
        d.polygon([(hx - 3, top + 2), (hx, top - 6 - fl), (hx + 3, top + 2)], fill=(255, 196, 60))
        d.polygon([(hx - 1, top + 2), (hx, top - 2 - fl), (hx + 1, top + 2)], fill=(255, 245, 190))
    elif typ == 'PLANTA':
        d.polygon([(hx, top + 1), (hx + 6, top - 5), (hx + 2, top + 1)], fill=(110, 210, 90))
        d.line((hx, top + 1, hx + 4, top - 3), fill=(40, 120, 50))
    elif typ == 'ÁGUA':
        for s_ in (-1, 1):
            d.polygon([(hx + s_ * (head_r - 1), hy), (hx + s_ * (head_r + 4), hy - 4), (hx + s_ * (head_r + 3), hy + 3)], fill=light)
    elif typ == 'GELO':
        for k in range(3):
            x = hx - 4 + k * 4
            d.polygon([(x - 1, top + 2), (x, top - 4 + (k % 2) * 2), (x + 1, top + 2)], fill=(236, 252, 255))
    elif typ == 'CRISTAL':
        d.polygon([(hx, top + 1), (hx + 3, top + 4), (hx, top + 7), (hx - 3, top + 4)], fill=acc)
    elif typ == 'RAIO':
        d.line([(hx + head_r - 1, hy - 2), (hx + head_r + 4, hy - 6), (hx + head_r + 2, hy - 6), (hx + head_r + 6, hy - 11)], fill=acc, width=1)
    elif typ == 'PEDRA':
        for k in range(r.randint(2, 4)):
            x, y = r.randint(cx - 9, cx + 9), r.randint(22, 32)
            d.rectangle((x, y, x + 2, y + 1), fill=dark)
    elif typ == 'SOMBRA':
        for k in range(3):
            x = r.randint(cx - 12, cx + 12)
            d.point((x, 6 + k * 2), fill=(170, 150, 220))
    if t['lvl'] == 4 and top >= 13:
        d.ellipse((hx - 6, top - 12, hx + 6, top - 8), outline=(255, 214, 72))
    # ---- manchas
    if t['spots'] and B != 'golem':
        for k in range(3):
            x, y = r.randint(cx - 8, cx + 8), r.randint(hy + 4, 31)
            if im.getpixel((x, y))[:3] == base:
                d.rectangle((x, y, x + 1, y + 1), fill=light)
    # ---- olhos
    ne = t['eyes']
    ey = hy - 1
    xs = {1: [hx], 2: [hx - 4, hx + 4], 3: [hx - 5, hx, hx + 5]}[ne]
    big = 3 if ne == 1 else 2
    glow = typ == 'SOMBRA'
    for x in xs:
        _ell(d, x, ey, big - (1 if ne == 3 else 0), big, (250, 250, 255) if not glow else (150, 255, 210))
        d.rectangle((x - (1 if ne != 3 else 0), ey - 1, x, ey + 1), fill=OUTC if not glow else (20, 60, 50))
        d.point((x - 1, ey - 1), fill=(255, 255, 255))
    # ---- boca
    my = ey + 4
    M = t['mouth']
    if B == 'ave' or M == 'bico_o':
        d.polygon([(hx - 2, my - 1), (hx + 2, my - 1), (hx, my + 2)], fill=(255, 176, 60))
    elif M == 'sorriso':
        d.line((hx - 2, my, hx - 1, my + 1), fill=OUTC); d.line((hx - 1, my + 1, hx + 1, my + 1), fill=OUTC)
        d.line((hx + 1, my + 1, hx + 2, my), fill=OUTC)
    elif M == 'presas':
        d.line((hx - 3, my, hx + 3, my), fill=OUTC)
        d.point((hx - 2, my + 1), fill=(255, 255, 255)); d.point((hx + 2, my + 1), fill=(255, 255, 255))
    else:
        d.line((hx - 2, my, hx + 2, my), fill=OUTC)
    # bochechas
    for s_ in (-1, 1):
        if im.getpixel((hx + s_ * 6, my - 1))[3]:
            d.point((hx + s_ * 6, my - 1), fill=(255, 140, 150))
    # ---- sombreamento + contorno
    a = np.array(im).astype(np.int16)
    op = a[..., 3] > 0
    up = np.zeros_like(op); up[1:] = op[:-1]
    dn = np.zeros_like(op); dn[:-1] = op[1:]
    lf = np.zeros_like(op); lf[:, 1:] = op[:, :-1]
    rt = np.zeros_like(op); rt[:, :-1] = op[:, 1:]
    rgb = a[..., :3]
    keep = np.isin(rgb.reshape(-1, 3).view([('', rgb.dtype)] * 3), np.array([OUTC, (250, 250, 255), (255, 255, 255)], np.int16).view([('', np.int16)] * 3)).reshape(op.shape)
    hi = op & ~up & ~keep
    sh = op & ~dn & ~keep
    shr = op & ~rt & ~keep
    a[..., :3] = np.where(hi[..., None], np.minimum(255, rgb * 1.18 + 12), rgb)
    a[..., :3] = np.where((sh | shr)[..., None] & ~hi[..., None], rgb * 0.72, a[..., :3])
    edge = ~op & (up | dn | lf | rt)
    a[edge] = OUTC + (255,)
    if t['lvl'] >= 3:                                   # contorno de brilho: dourado (lendário) ou roxo (épico)
        op2 = a[..., 3] > 0
        nb = np.zeros_like(op2)
        nb[1:] |= op2[:-1]; nb[:-1] |= op2[1:]; nb[:, 1:] |= op2[:, :-1]; nb[:, :-1] |= op2[:, 1:]
        ring = ~op2 & nb
        if t['lvl'] == 3:
            yy, xx = np.mgrid[0:S, 0:S]
            ring &= ((yy + xx) % 2 == 0)
        a[ring] = (C_GLOW[t['lvl']] + (255,))
    return a.clip(0, 255).astype(np.uint8)


if __name__ == '__main__':
    import sys
    names = sys.argv[1:] or ['Ana', 'Gabriel', 'Júlia', 'Lucas', 'Amanda', 'Matheus', 'Larissa', 'Pedro', 'Bruna', 'João',
                             'Maria', 'Rafael', 'Beatriz', 'Guilherme', 'Letícia', 'Felipe', 'Camila', 'Gustavo', 'Isabela',
                             'Vinícius', 'Mariana', 'Leonardo', 'Fernanda', 'Thiago']
    cols = 6
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 200, rows * 230), (28, 24, 44))
    dd = ImageDraw.Draw(sheet)
    for k, n in enumerate(names):
        t = traits(n)
        sp = Image.fromarray(draw(n)).resize((160, 160), Image.NEAREST)
        x, y = (k % cols) * 200 + 20, (k // cols) * 230 + 10
        sheet.paste(sp, (x, y), sp)
        dd.text((x, y + 165), f"{n} · {t['species']}", fill=(255, 255, 255))
        dd.text((x, y + 182), f"{t['type']} · {t['body']}", fill=(200, 200, 200))
        dd.text((x, y + 199), t['rarity'], fill=RAR_COL[t['rarity']])
    sheet.save('/tmp/claude-0/-home-claude/1ad023e2-0d5f-5b6d-b2b7-ef96b3fdfd1a/scratchpad/criaturas.png')
    print('ok')
