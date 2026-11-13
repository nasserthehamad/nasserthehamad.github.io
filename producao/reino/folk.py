#!/usr/bin/env python3
"""Moradores de Brasa: boneco único por nome, roupa e objeto pela função."""
import zlib, unicodedata
import numpy as np

OUT = (34, 26, 32)
SKINS = [(246, 208, 172), (184, 128, 90), (226, 174, 132), (132, 90, 62), (100, 66, 48), (214, 160, 120)]
HAIRS = [(46, 34, 30), (212, 160, 76), (98, 60, 36), (162, 66, 44), (28, 28, 40), (70, 46, 34), (120, 80, 50)]
TUNICS = [(204, 72, 72), (70, 122, 206), (232, 182, 62), (92, 164, 92), (164, 92, 174), (232, 132, 62), (72, 174, 172)]
PANTS = [(84, 66, 58), (62, 62, 96), (112, 92, 62), (70, 84, 70)]


def shade(c, f):
    return tuple(int(max(0, min(255, v * f))) for v in c)


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return ''.join(ch for ch in s if not unicodedata.combining(ch))


ROLES = {
    'ferreir': dict(tunic=(96, 84, 80), apron=(120, 76, 44), item='hammer'),
    'confeit': dict(tunic=(246, 240, 236), apron=(240, 150, 180), hat='chef', item='cake'),
    'padeir': dict(tunic=(246, 240, 236), apron=(226, 206, 160), hat='bandana', item='bread'),
    'adestr': dict(tunic=(120, 140, 70), item='leash', dog=True),
    'cavaleir': dict(tunic=(170, 176, 196), armor=True, hat='helmet_plume', item='sword'),
    'cacador': dict(tunic=(70, 112, 60), hat='hood', item='bow'),
    'cacadora': dict(tunic=(70, 112, 60), hat='hood', item='bow'),
    'guarda': dict(tunic=(56, 82, 150), hat='helmet', item='spear'),
    'pescad': dict(tunic=(60, 140, 160), hat='bucket', item='rod'),
    'bibliotec': dict(tunic=(110, 70, 150), glasses=True, item='book'),
    'fazend': dict(tunic=(214, 196, 150), pants=(66, 92, 150), straps=True, hat='straw', item='pitchfork'),
    'construt': dict(tunic=(222, 132, 56), pants=(90, 74, 60), hat='bandana_y', item='saw'),
    'aventur': dict(tunic=(56, 148, 136), hat='feather', item='map', cape=(150, 60, 50)),
    'costur': dict(tunic=(232, 142, 172), item='yarn', tape=True),
    'acougu': dict(tunic=(244, 240, 236), apron=(214, 70, 70), apron_stripes=True, item='ham'),
    'artes': dict(tunic=(196, 120, 80), apron=(150, 110, 80), item='vase'),
    'medic': dict(tunic=(246, 246, 250), item='potion_red', badge=True),
    'enferm': dict(tunic=(246, 246, 250), hat='nurse', item='potion_red'),
    'brux': dict(tunic=(80, 50, 110), hat='witch', item='potion'),
    'escult': dict(tunic=(150, 150, 160), apron=(110, 110, 120), item='chisel'),
    'filosof': dict(tunic=(236, 230, 214), hat='laurel', item='scroll'),
    'artist': dict(tunic=(236, 200, 90), hat='beret', item='brush'),
    'magico': dict(tunic=(60, 150, 100), hat='wizard_g', item='potion'),
    'mago': dict(tunic=(60, 70, 160), hat='wizard', item='staff'),
    'minera': dict(tunic=(120, 100, 80), hat='miner', item='pickaxe'),
    'matemat': dict(tunic=(70, 110, 170), glasses=True, item='abacus'),
    'arqueir': dict(tunic=(80, 120, 60), hat='hood', item='bow'),
    'vaqueir': dict(tunic=(190, 90, 60), hat='cowboy', item='lasso'),
    'cantor': dict(tunic=(220, 90, 160), item='lute'),
    'dancar': dict(tunic=(240, 120, 90), hat='flower', item='ribbon'),
    'louc': dict(tunic=(140, 220, 120), pants=(200, 80, 200), item='spiral', wild=True),
    'bobo': dict(tunic=(220, 60, 60), jester=True, hat='jester', item='bells'),
    'alquim': dict(tunic=(90, 130, 120), hat='goggles', item='potion_green'),
    # Ep. 4
    'apotec': dict(tunic=(110, 150, 96), apron=(226, 214, 180), item='potion_green'),
    'padre': dict(tunic=(52, 48, 64), pants=(40, 38, 50), badge=True, item='book'),
    'desbrav': dict(tunic=(84, 112, 62), hat='hood', item='spear', cape=(104, 70, 44)),
    'veterin': dict(tunic=(150, 210, 196), badge=True, item='leash'),
    'curand': dict(tunic=(126, 176, 116), hat='flower', item='potion_green'),
    'feitic': dict(tunic=(70, 44, 130), hat='witch', item='staff'),
    'escrib': dict(tunic=(206, 186, 146), glasses=True, item='scroll'),
    'cozinh': dict(tunic=(246, 240, 236), apron=(214, 96, 70), hat='chef', item='ham'),
    'explor': dict(tunic=(60, 120, 160), hat='feather', item='map', cape=(70, 70, 130)),
    'botanic': dict(tunic=(96, 156, 76), hat='straw', item='vase'),
    'arqueolog': dict(tunic=(186, 152, 100), hat='cowboy', item='brush'),
    'music': dict(tunic=(96, 120, 206), item='lute'),
    'colet': dict(tunic=(156, 124, 84), straps=True, hat='bandana', item='pitchfork'),
    # Ep. 5
    'banqueir': dict(tunic=(52, 96, 76), buttons=True, glasses=True, item='coins'),
    'taverna': dict(tunic=(150, 66, 56), apron=(232, 222, 200), hat='bandana', item='mug'),
    'santa': dict(tunic=(240, 240, 250), pants=(200, 210, 236), hat='halo', item='book'),
}


def role_spec(role):
    r = norm(role)
    for k, v in ROLES.items():
        if k in r:
            return dict(v)
    return {}


def gender(role):
    """'f' / 'm' pela forma que a pessoa escreveu a função; None se for neutra (ex.: guarda)."""
    w = norm(role).split()[0] if role.strip() else ''
    if w in ('guarda', 'artista', 'atleta', 'dentista', 'chef'):
        return None
    if w.endswith('a'):
        return 'f'
    if w.endswith(('o', 'or', 'es', 'ao')):
        return 'm'
    return None


def feminine(role):
    r = norm(role).split()[0] if role.strip() else ''
    return r.endswith('a') and r not in ('guarda',)


def make_folk(name, role, frame=0, hair_style=None):
    h = zlib.crc32(norm(name).encode())
    spec = role_spec(role)
    skin = SKINS[h % len(SKINS)]
    hair = HAIRS[(h // 7) % len(HAIRS)]
    if hair_style is None:
        opts = [1, 2, 3] if feminine(role) else [0, 3, 0]
        hair_style = opts[(h // 13) % 3]
    tun = spec.get('tunic', TUNICS[(h // 3) % len(TUNICS)])
    pants = spec.get('pants', PANTS[(h // 5) % len(PANTS)])
    SW, SH = 30, 42
    a = np.zeros((SH, SW, 4), np.float32)
    bx, by = 7, 9

    def px(x, y, c):
        x, y = x + bx, y + by
        if 0 <= x < SW and 0 <= y < SH:
            a[y, x, :3] = c
            a[y, x, 3] = 1

    oy = 3
    # cabeça
    for y in range(oy + 1, oy + 10):
        for x in range(3, 13):
            if (y in (oy + 1, oy + 9)) and x in (3, 12):
                continue
            px(x, y, shade(skin, 0.84) if (x >= 11 or y == oy + 9) else skin)
    for ex in (5, 10):
        px(ex, oy + 5, (36, 26, 30)); px(ex, oy + 6, (36, 26, 30))
    px(4, oy + 7, shade(skin, 0.9) if skin[0] < 150 else (236, 150, 140))
    px(11, oy + 7, shade(skin, 0.8) if skin[0] < 150 else (220, 140, 132))
    px(7, oy + 8, shade(skin, 0.72)); px(8, oy + 8, shade(skin, 0.72))
    if spec.get('glasses'):
        fr_ = (60, 40, 44)
        for x in (4, 6, 9, 11):
            px(x, oy + 5, fr_); px(x, oy + 6, fr_)
        for x in (5, 10):
            px(x, oy + 4, fr_); px(x, oy + 7, (200, 222, 240))
        px(7, oy + 5, fr_); px(8, oy + 5, fr_)
    hh, hs = shade(hair, 1.25), shade(hair, 0.78)
    hat = spec.get('hat')
    if spec.get('wild'):
        hair_style = 3
    if hair_style == 3 and hat not in ('helmet', 'helmet_plume', 'hood'):
        for y in range(oy - 2, oy + 6):
            for x in range(1, 15):
                if ((x - 7.5) / 7) ** 2 + ((y - oy - 2) / 4.5) ** 2 <= 1 and not (y >= oy + 3 and 4 <= x <= 11):
                    px(x, y, hh if (x + y) % 3 == 0 and x < 8 else (hs if x > 10 else hair))
    else:
        for y in range(oy, oy + 4):
            for x in range(3, 13):
                if y == oy and x in (3, 12):
                    continue
                px(x, y, hh if (x < 7 and y <= oy + 1) else (hs if x >= 11 else hair))
        for x in (3, 4, 11, 12):
            px(x, oy + 4, hair if x < 11 else hs)
        px(5, oy + 4, hair); px(6, oy + 3, hair)
        if hair_style == 1:
            for y in range(oy + 4, oy + 14):
                px(2, y, hair); px(3, y, hair if y < oy + 10 else hs)
                px(12, y, hs); px(13, y, hs)
        if hair_style == 2 and hat is None:
            for y in range(oy - 3, oy):
                for x in range(6, 10):
                    if not (y == oy - 3 and x in (6, 9)):
                        px(x, y, hh if x < 8 else hair)
    # corpo
    tsh, thi = shade(tun, 0.74), shade(tun, 1.14)
    for y in range(oy + 10, oy + 19):
        for x in range(4, 12):
            c = tun if x < 10 else tsh
            if x == 4 and y < oy + 16:
                c = thi
            if spec.get('armor') and (x + y) % 4 == 0:
                c = (220, 224, 236)
            if spec.get('jester') and x >= 8:
                c = (250, 200, 60) if x < 10 else (210, 160, 40)
            px(x, y, c)
    if not spec.get('armor'):
        px(7, oy + 10, skin); px(8, oy + 10, skin); px(7, oy + 11, shade(skin, 0.84))
    else:
        for x in range(4, 12):
            px(x, oy + 10, (130, 136, 156))
        px(7, oy + 13, (230, 190, 80)); px(8, oy + 13, (196, 150, 60))
    ap = spec.get('apron')
    if ap:
        for y in range(oy + 13, oy + 20):
            for x in range(5, 11):
                c_ = ap if x < 9 else shade(ap, 0.84)
                if spec.get('apron_stripes') and x % 2 == 0:
                    c_ = (250, 246, 240)
                px(x, y, c_)
        px(5, oy + 12, ap); px(10, oy + 12, shade(ap, 0.84))
    elif spec.get('straps'):
        for y in range(oy + 10, oy + 19):
            px(5, y, pants); px(10, y, shade(pants, 0.8))
        for y in range(oy + 15, oy + 19):
            for x in range(5, 11):
                px(x, y, pants if x < 9 else shade(pants, 0.8))
    else:
        for x in range(4, 12):
            px(x, oy + 16, (96, 64, 40))
        px(7, oy + 16, (230, 190, 80)); px(8, oy + 16, (196, 150, 60))
    if spec.get('badge'):
        px(5, oy + 12, (220, 50, 50)); px(5, oy + 13, (220, 50, 50)); px(4, oy + 13, (220, 50, 50)); px(6, oy + 13, (220, 50, 50))
        px(5, oy + 14, (220, 50, 50))
    if spec.get('buttons'):               # colete com botões dourados (banqueira)
        for y in range(oy + 11, oy + 16, 2):
            px(7, y, (255, 214, 80))
        px(6, oy + 11, (236, 230, 214)); px(8, oy + 11, (236, 230, 214))
    if spec.get('tape'):
        for y in range(oy + 10, oy + 18):
            px(5, y, (250, 210, 70)); px(10, y, (230, 190, 50))
        for y in range(oy + 11, oy + 18, 2):
            px(5, y, (60, 50, 40))
    # braços
    sw = {0: (0, 0), 1: (-1, 1), 2: (1, -1)}[frame]
    sleeve = tun
    for side, x0, dy in ((0, 2, sw[0]), (1, 12, sw[1])):
        for y in range(oy + 11 + dy, oy + 16 + dy):
            px(x0, y, sleeve if side == 0 else tsh)
            px(x0 + 1, y, sleeve if side == 0 else tsh)
        px(x0, oy + 16 + dy, skin); px(x0 + 1, oy + 16 + dy, shade(skin, 0.86))
        px(x0, oy + 17 + dy, shade(skin, 0.9)); px(x0 + 1, oy + 17 + dy, shade(skin, 0.8))
    # pernas e botas
    lift = {0: (0, 0), 1: (1, 0), 2: (0, 1)}[frame]
    boots, bsh = ((150, 156, 176), (110, 116, 136)) if spec.get('armor') else ((70, 48, 36), (50, 34, 28))
    for leg, xs in ((0, (5, 6, 7)), (1, (8, 9, 10))):
        up = lift[leg]
        for y in range(oy + 19, oy + 23 - up):
            for x in xs:
                px(x, y, pants if x != xs[-1] else shade(pants, 0.78))
        for y in range(oy + 23 - up, oy + 25 - up):
            for x in (xs[0] - (1 if leg == 0 else 0),) + xs + ((xs[-1] + 1,) if leg == 1 else ()):
                px(x, y, boots if x < xs[-1] else bsh)
    # chapéus
    if hat == 'chef':
        for y in range(oy - 6, oy + 1):
            for x in range(4, 12):
                if not (y == oy - 6 and x in (4, 11)):
                    px(x, y, (255, 255, 255) if x < 10 else (220, 220, 230))
        for x in range(3, 13):
            px(x, oy + 1, (236, 236, 244))
    elif hat == 'bandana':
        for y in range(oy - 1, oy + 2):
            for x in range(3, 13):
                if not (y == oy - 1 and x in (3, 12)):
                    px(x, y, (250, 250, 250) if x < 11 else (214, 214, 224))
        px(13, oy + 1, (214, 214, 224)); px(14, oy + 2, (214, 214, 224))
    elif hat in ('helmet', 'helmet_plume'):
        met, mets = (184, 190, 206), (130, 136, 156)
        for y in range(oy - 2, oy + 4):
            for x in range(2, 14):
                if ((x - 7.5) / 6) ** 2 + ((y - oy - 2.5) / 4.6) ** 2 <= 1:
                    px(x, y, met if x < 10 else mets)
        for x in range(2, 14):
            px(x, oy + 4, mets)
        px(7, oy + 5, mets); px(8, oy + 5, mets)
        if hat == 'helmet_plume':
            for k, (x, y) in enumerate([(8, oy - 3), (9, oy - 4), (10, oy - 5), (11, oy - 5), (12, oy - 4), (9, oy - 3),
                                        (10, oy - 4), (11, oy - 4)]):
                px(x, y, (220, 50, 60) if k % 2 == 0 else (180, 30, 44))
    elif hat == 'hood':
        hc, hcs = shade(tun, 0.9), shade(tun, 0.66)
        for y in range(oy - 1, oy + 11):
            for x in range(2, 14):
                inside = 4 <= x <= 11 and oy + 3 <= y <= oy + 9
                if ((x - 7.5) / 6.5) ** 2 + ((y - oy - 4) / 6.5) ** 2 <= 1 and not inside:
                    px(x, y, hc if x < 10 else hcs)
    elif hat == 'bucket':
        hc = (200, 176, 110)
        for y in range(oy - 1, oy + 2):
            for x in range(4, 12):
                px(x, y, hc if x < 10 else shade(hc, 0.8))
        for x in range(2, 14):
            px(x, oy + 2, shade(hc, 0.9))
    elif hat in ('witch', 'wizard', 'wizard_g'):
        hc = {'witch': (60, 40, 80), 'wizard': (50, 60, 150), 'wizard_g': (40, 120, 80)}[hat]
        for y in range(oy - 9, oy + 2):
            k_ = (y - (oy - 9)) / 11
            hw_ = int(1 + k_ * 4)
            for x in range(8 - hw_, 8 + hw_ + 1):
                px(x, y, hc if x < 9 else shade(hc, 0.75))
        for x in range(1, 15):
            px(x, oy + 2, shade(hc, 0.85))
        if hat != 'witch':
            px(7, oy - 3, (255, 230, 120)); px(9, oy - 1, (255, 230, 120)); px(6, oy, (255, 230, 120))
        else:
            px(8, oy - 1, (230, 160, 40)); px(9, oy - 1, (230, 160, 40))
    elif hat == 'beret':
        for y in range(oy - 2, oy + 2):
            for x in range(3, 14):
                if ((x - 8) / 5.5) ** 2 + ((y - oy) / 2.4) ** 2 <= 1:
                    px(x, y, (200, 40, 60) if x < 11 else (160, 30, 46))
        px(8, oy - 3, (160, 30, 46))
    elif hat == 'miner':
        for y in range(oy - 2, oy + 3):
            for x in range(2, 14):
                if ((x - 7.5) / 6) ** 2 + ((y - oy - 1.5) / 3.6) ** 2 <= 1:
                    px(x, y, (250, 200, 50) if x < 10 else (210, 160, 30))
        px(7, oy, (255, 255, 200)); px(8, oy, (255, 255, 200)); px(7, oy + 1, (255, 240, 150)); px(8, oy + 1, (255, 240, 150))
    elif hat == 'cowboy':
        hc = (150, 100, 56)
        for y in range(oy - 3, oy + 1):
            for x in range(4, 12):
                px(x, y, hc if x < 10 else shade(hc, 0.8))
        px(7, oy - 3, shade(hc, 0.7)); px(8, oy - 3, shade(hc, 0.7))
        for x in range(0, 16):
            px(x, oy + 1, shade(hc, 0.9))
        px(0, oy, shade(hc, 0.9)); px(15, oy, shade(hc, 0.9))
    elif hat == 'jester':
        for y in range(oy - 3, oy + 2):
            for x in range(3, 13):
                px(x, y, (220, 60, 60) if x < 8 else (250, 200, 60))
        for (x, y) in [(2, oy - 4), (1, oy - 5), (13, oy - 4), (14, oy - 5)]:
            px(x, y, (220, 60, 60) if x < 8 else (250, 200, 60))
        px(0, oy - 6, (255, 230, 120)); px(15, oy - 6, (255, 230, 120))
    elif hat == 'nurse':
        for y in range(oy - 2, oy + 1):
            for x in range(4, 12):
                px(x, y, (250, 250, 252) if x < 10 else (220, 220, 230))
        px(7, oy - 1, (220, 50, 50)); px(8, oy - 1, (220, 50, 50)); px(7, oy - 2, (220, 50, 50)); px(7, oy, (220, 50, 50))
        px(6, oy - 1, (220, 50, 50))
    elif hat == 'goggles':
        for x in range(3, 13):
            px(x, oy + 1, (80, 60, 50))
        for x0 in (4, 9):
            for x in range(x0, x0 + 3):
                px(x, oy, (140, 200, 220)); px(x, oy + 1, (100, 160, 190))
    elif hat == 'halo':
        for x in range(4, 12):
            px(x, oy - 4, (255, 214, 80))
        px(3, oy - 3, (255, 214, 80)); px(12, oy - 3, (255, 214, 80))
        for x in range(5, 11):
            px(x, oy - 3, (255, 246, 190)) if x in (5, 10) else None
    elif hat == 'laurel':
        for x in range(3, 13):
            if x % 2 == 0:
                px(x, oy, (90, 160, 70)); px(x, oy - 1, (120, 190, 90))
            else:
                px(x, oy + 1, (90, 160, 70))
    elif hat == 'flower':
        for (x, y, c_) in [(11, oy, (255, 120, 160)), (12, oy, (255, 120, 160)), (11, oy - 1, (255, 120, 160)),
                           (12, oy + 1, (255, 120, 160)), (11, oy + 1, (255, 230, 120))]:
            px(x, y, c_)
    elif hat == 'bandana_y':
        for y in range(oy - 1, oy + 2):
            for x in range(3, 13):
                if not (y == oy - 1 and x in (3, 12)):
                    px(x, y, (250, 206, 60) if x < 11 else (214, 172, 40))
        px(13, oy + 1, (214, 172, 40)); px(14, oy + 2, (214, 172, 40))
    elif hat == 'feather':
        hc, hcs = (60, 100, 70), (44, 76, 54)
        for y in range(oy - 2, oy + 2):
            for x in range(4, 13):
                px(x, y, hc if x < 10 else hcs)
        for x in range(2, 15):
            px(x, oy + 2, hcs)
        for k_, (x, y) in enumerate([(12, oy - 3), (13, oy - 4), (14, oy - 5), (15, oy - 6), (13, oy - 3), (14, oy - 4)]):
            px(x, y, (230, 60, 50) if k_ % 2 == 0 else (250, 200, 60))
    elif hat == 'straw':
        straw, strs = (226, 192, 110), (186, 150, 78)
        for x in range(0, 16):
            px(x, oy + 2, straw if x < 12 else strs)
        for y in range(oy - 2, oy + 2):
            for x in range(4, 12):
                px(x, y, straw if x < 10 else strs)
        for x in range(4, 12):
            px(x, oy + 1, (170, 60, 50))
    if spec.get('cape'):
        cp = spec['cape']
        for y in range(oy + 10, oy + 21):
            px(2, y, cp); px(13, y, shade(cp, 0.8))
            if y > oy + 12:
                px(1, y, shade(cp, 0.9)); px(14, y, shade(cp, 0.7))
    # objetos (mão direita fica em x 12..13, y oy+16)
    it = spec.get('item')
    hy = oy + 16 + sw[1]
    wood, wsh = (150, 104, 60), (110, 72, 40)
    steel, stsh = (214, 220, 232), (150, 156, 176)
    if it == 'hammer':
        for y in range(hy - 7, hy + 1):
            px(14, y, wood)
        for y in range(hy - 10, hy - 6):
            for x in range(12, 18):
                px(x, y, (120, 124, 136) if y > hy - 9 else (170, 174, 188))
    elif it == 'cake':
        for y in range(hy - 4, hy):
            for x in range(13, 19):
                px(x, y, (250, 210, 220) if y < hy - 2 else (200, 140, 90))
        px(15, hy - 5, (220, 40, 60)); px(16, hy - 5, (220, 40, 60))
    elif it == 'bread':
        for k in range(9):
            x, y = 13 + k // 2 + 1, hy - k
            px(x, y, (214, 160, 80)); px(x + 1, y, (176, 120, 56))
            if k % 3 == 1:
                px(x, y, (240, 200, 130))
    elif it == 'sword':
        for y in range(hy - 15, hy - 1):
            px(14, y, steel); px(15, y, stsh)
        px(14, hy - 16, steel)
        for x in range(12, 18):
            px(x, hy - 1, (200, 160, 60))
        px(14, hy, wood); px(14, hy + 1, (200, 160, 60))
    elif it == 'spear':
        for y in range(hy - 20, hy + 7):
            px(14, y, wood if y > hy - 18 else steel)
        px(13, hy - 18, steel); px(15, hy - 18, steel); px(14, hy - 21, steel); px(14, hy - 22, steel)
    elif it == 'bow':
        for k in range(-9, 10):
            x = 15 + int(round(3 * (1 - (k / 9.5) ** 2)))
            px(x, hy + k - 2, wood)
        for k in range(-9, 10):
            px(14, hy + k - 2, (230, 230, 230)) if k % 2 == 0 else None
    elif it == 'rod':
        for k in range(16):
            px(13 + k // 2, hy - k, wood if k < 12 else (120, 90, 60))
        for k in range(1, 8):
            px(21, hy - 15 + k, (220, 220, 230)) if k % 2 else None
    elif it == 'mug':
        for y in range(hy - 5, hy + 1):
            for x in range(13, 18):
                px(x, y, (150, 96, 52) if x < 17 else (112, 70, 38))
        for x in range(13, 18):
            px(x, hy - 6, (250, 248, 240)); px(x, hy - 7, (250, 248, 240)) if x in (14, 15) else None
        px(18, hy - 4, (112, 70, 38)); px(18, hy - 2, (112, 70, 38)); px(19, hy - 3, (112, 70, 38))
    elif it == 'coins':
        for y in range(hy - 4, hy + 2):
            for x in range(12, 18):
                if (x - 15) ** 2 * 0.8 + (y - hy + 1) ** 2 <= 9:
                    px(x, y, (176, 136, 80) if x < 16 else (140, 104, 60))
        px(14, hy - 5, (110, 80, 50)); px(15, hy - 5, (110, 80, 50))
        px(17, hy - 6, (255, 214, 80)); px(18, hy - 6, (255, 236, 150)); px(17, hy - 7, (230, 180, 60))
    elif it == 'book':
        for y in range(hy - 4, hy + 1):
            for x in range(12, 18):
                px(x, y, (160, 40, 50) if x != 14 else (240, 230, 200))
    elif it == 'pitchfork':
        for y in range(hy - 16, hy + 6):
            px(14, y, wood)
        for x in (12, 14, 16):
            for y in range(hy - 21, hy - 16):
                px(x, y, steel)
        for x in range(12, 17):
            px(x, hy - 16, stsh)
    elif it in ('potion', 'potion_red', 'potion_green'):
        lc = {'potion': (170, 90, 230), 'potion_red': (230, 70, 80), 'potion_green': (90, 220, 120)}[it]
        for y in range(hy - 4, hy + 1):
            for x in range(13, 18):
                if (x - 15) ** 2 + (y - hy + 2) ** 2 <= 5:
                    px(x, y, lc if y > hy - 3 else (220, 236, 250))
        px(15, hy - 5, (220, 236, 250)); px(15, hy - 6, (150, 100, 60))
        if it == 'potion_green':
            px(16, hy - 8, (150, 240, 170)); px(14, hy - 9, (150, 240, 170))
    elif it == 'staff':
        for y in range(hy - 18, hy + 6):
            px(14, y, wood)
        for (x, y) in [(13, hy - 20), (14, hy - 20), (15, hy - 20), (14, hy - 21), (14, hy - 19)]:
            px(x, y, (150, 220, 255))
    elif it == 'brush':
        for k_ in range(8):
            px(13 + k_ // 3, hy - k_, wood)
        px(16, hy - 8, (230, 60, 80)); px(16, hy - 9, (230, 60, 80))
        for (x, y, c_) in [(12, hy + 1, (240, 220, 170)), (13, hy + 1, (240, 220, 170)), (12, hy + 2, (240, 220, 170)),
                           (13, hy + 2, (60, 140, 230)), (12, hy + 3, (250, 200, 60))]:
            px(x - 10, y, c_)
    elif it == 'pickaxe':
        for y in range(hy - 12, hy + 3):
            px(14, y, wood)
        for x in range(10, 20):
            px(x, hy - 12 + abs(x - 14) // 2, (160, 166, 180))
    elif it == 'lasso':
        for k_ in range(14):
            ang = k_ / 14 * 2 * 3.1416
            px(16 + int(round(3 * __import__('math').cos(ang))), hy - 4 + int(round(2.5 * __import__('math').sin(ang))), (210, 180, 110))
        px(14, hy - 1, (210, 180, 110))
    elif it == 'lute':
        for y in range(hy - 4, hy + 2):
            for x in range(12, 18):
                if ((x - 14.5) / 3) ** 2 + ((y - hy + 1) / 3) ** 2 <= 1:
                    px(x, y, (190, 120, 60) if x < 16 else (150, 90, 44))
        px(14, hy - 1, (60, 40, 30))
        for k_ in range(6):
            px(17 + k_ // 2, hy - 4 - k_, (110, 70, 40))
    elif it == 'ribbon':
        for k_ in range(12):
            px(14 + k_ // 2, hy - 2 - k_ + int(2 * __import__('math').sin(k_ * 0.9)), (250, 90, 150) if k_ % 2 else (255, 150, 190))
    elif it == 'scroll':
        for y in range(hy - 5, hy + 1):
            for x in range(13, 17):
                px(x, y, (240, 226, 186))
        for x in range(12, 18):
            px(x, hy - 5, (200, 170, 120)); px(x, hy + 1, (200, 170, 120))
    elif it == 'chisel':
        for k_ in range(7):
            px(13 + k_ // 3, hy - k_, (160, 166, 180) if k_ > 3 else wood)
        for y in range(hy - 3, hy + 2):
            for x in range(17, 21):
                px(x - 0, y + 4, (200, 196, 190))
    elif it == 'abacus':
        for y in range(hy - 5, hy + 1):
            for x in range(12, 19):
                edge = y in (hy - 5, hy) or x in (12, 18)
                px(x, y, wood if edge else ((230, 80, 80) if (x + y) % 3 == 0 else (240, 230, 200)))
    elif it == 'vase':
        for y in range(hy - 5, hy + 1):
            for x in range(13, 18):
                if (x - 15) ** 2 / 6 + (y - hy + 2) ** 2 / 9 <= 1:
                    px(x, y, (200, 110, 70) if x < 16 else (160, 84, 50))
        px(15, hy - 2, (240, 200, 120))
    elif it == 'spiral':
        for k_ in range(10):
            ang = k_ * 0.9
            r_ = 0.6 + k_ * 0.3
            px(16 + int(round(r_ * __import__('math').cos(ang))), hy - 7 + int(round(r_ * __import__('math').sin(ang))),
               (255, 120, 220) if k_ % 2 else (120, 220, 255))
    elif it == 'bells':
        px(14, hy - 1, (255, 220, 80)); px(15, hy - 2, (255, 220, 80)); px(16, hy - 1, (255, 220, 80))
        for y in range(hy - 4, hy):
            px(15, y, wood)
    elif it == 'saw':
        for k_ in range(9):
            for j_ in range(3 + k_ // 3):
                px(14 + j_, hy - 2 - k_, (200, 206, 220) if j_ < 2 + k_ // 3 else (150, 156, 176))
        for k_ in range(0, 9, 2):
            px(13, hy - 2 - k_, (150, 156, 176))
        px(14, hy - 1, wood); px(15, hy - 1, wood); px(14, hy, wsh); px(15, hy, wood)
    elif it == 'map':
        for y in range(hy - 6, hy + 1):
            for x in range(12, 18):
                px(x, y, (240, 222, 170) if (x + y) % 5 else (210, 186, 130))
        px(14, hy - 4, (200, 50, 50)); px(15, hy - 3, (200, 50, 50)); px(16, hy - 4, (200, 50, 50))
        px(12, hy - 6, (176, 140, 90)); px(12, hy, (176, 140, 90))
    elif it == 'yarn':
        for y in range(hy - 4, hy + 2):
            for x in range(12, 18):
                if (x - 14.5) ** 2 + (y - hy + 1) ** 2 <= 9:
                    px(x, y, (150, 90, 200) if (x + y) % 3 else (190, 140, 230))
        px(16, hy - 6, (200, 200, 210)); px(17, hy - 7, (200, 200, 210)); px(18, hy - 8, (200, 200, 210))
    elif it == 'ham':
        for y in range(hy - 6, hy):
            for x in range(13, 19):
                if (x - 16) ** 2 / 9 + (y - hy + 3) ** 2 / 9 <= 1:
                    px(x, y, (200, 110, 80) if x < 17 else (170, 86, 60))
        px(13, hy, (240, 236, 220)); px(12, hy + 1, (240, 236, 220)); px(13, hy + 1, (240, 236, 220))
    elif it == 'leash':
        for k in range(6):
            px(13 + k, hy + 1 + k // 2, (180, 60, 50))
    # contorno
    m = a[..., 3] > 0
    ring = np.zeros_like(m)
    ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    a[ring, :3] = OUT
    a[ring, 3] = 1
    return a


def make_dog(frame=0):
    rows = ["....BB......", "...BBBB.....", "..BBEBBB....", "..BBBBBBN...", "...BBBB.....", "...BBBBBBBB.",
            "..BBBBBBBBBT", "..BBBBBBBBB.", "..L.L..L.L..", "..L.L..L.L.."]
    if frame == 1:
        rows[6] = "..BBBBBBBBB."
        rows[5] = "...BBBBBBBBT"
    pal = {'B': (120, 84, 52), 'E': (30, 20, 20), 'N': (40, 30, 30), 'T': (140, 100, 64), 'L': (96, 64, 40)}
    h, w = len(rows), len(rows[0])
    a = np.zeros((h + 2, w + 2, 4), np.float32)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != '.':
                col = pal[c]
                if c == 'B' and (x + y) % 5 == 0:
                    col = (150, 110, 70)
                a[y + 1, x + 1, :3] = col
                a[y + 1, x + 1, 3] = 1
    m = a[..., 3] > 0
    ring = np.zeros_like(m)
    ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    a[ring, :3] = OUT
    a[ring, 3] = 1
    return a


_cache = {}


def folk(name, role, frame=0):
    k = (name, role, frame)
    if k not in _cache:
        _cache[k] = make_folk(name, role, frame)
    return _cache[k]


FOUNDERS = [("Gabriel", "ferreiro"), ("Lívia", "construtora de casas"), ("Naty", "confeiteira"),
            ("Ana Sofia", "adestradora de cão de caça"), ("Raviela", "cavaleira"), ("Rafael", "pescador"),
            ("Emanuel", "bibliotecário"), ("Victor", "fazendeiro"), ("Antônio", "padeiro"), ("Izabelly", "caçadora"),
            ("Francini", "padeira"), ("Cristal", "guarda"), ("Rafaela", "aventureira"), ("Maria", "costureira"),
            ("Gustavo", "açougueiro")]

NEW_EP2 = [("Kelly", "artesã"), ("Izabelle", "médica"), ("Oliveti", "bruxa (poções)"), ("Alerrandro", "escultor"),
           ("Lorena", "filósofa/pensadora"), ("Rubens", "bruxo (visões e espíritos)"), ("Viviane", "artista"),
           ("Cathe", "mago (previsões/visões)"), ("João", "ferreiro"), ("Bernardo", "mágico curandeiro"),
           ("Samuel", "minerador"), ("Cauby", "matemático"), ("Cauã", "arqueiro"), ("Valdemir", "vaqueiro"),
           ("Yasmim", "cantora"), ("Aurora", "dançarina"), ("Laura", "louca"), ("Nic", "bobo da corte"),
           ("Clara", "enfermeira"), ("Giovanni", "alquimista")]


# Ep. 4 — comentários até 11/11 22h (ordem de chegada). '#n' só diferencia o boneco de nomes repetidos.
MISSED_FOUNDERS = [("Julielen", "arqueóloga e musicista"), ("Robson", "ajudante de coleta")]
NEW_EP4 = [("Hanna", "padeira"), ("Amanda", "açougueira"), ("Giovanna", "apotecária"), ("Lila", ""),
           ("Caio", "padre"), ("Andréa", "desbravadora"), ("Yuki", "veterinário"), ("Ester", "curandeira"),
           ("Lavinia", "feiticeira"), ("Amanda#2", "artista e comerciante de tecidos"), ("Amanda#3", "escriba"),
           ("Trubel", "cozinheira"), ("Luiza", "bruxa"), ("Alexandra", "exploradora e diplomata"),
           ("???#bruxo", "bruxo"), ("Matheus", "botânico"), ("Sabrina", "fazendeira")]


# Ep. 5 — comentários até 13/11 08h. A Vitória e a Meize entram mesmo sem seguir (decisão do Nasser).
NEW_EP5 = [("cubo", "guarda da vila"), ("Delox", "curandeiro de ervas"), ("Vitória", "banqueira"),
           ("Meize", "artista da vila"), ("Miyuki", "dona de uma taverna")]
EP5_CHANGES = {"Luiza": "santa", "???#bruxo": ("Pepze", "bruxo")}


def shown(name):
    """Nome como aparece na tela (sem o '#n')."""
    return name.split('#')[0]
