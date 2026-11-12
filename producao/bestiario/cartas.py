#!/usr/bin/env python3
"""Cartas do sorteio da Roleta: cada carta é o "print" de um comentário (nome + texto, no visual de comentário do TikTok).
Sem foto de perfil e sem @ (regra do canal); no lugar da foto, um círculo colorido com a inicial."""
import unicodedata
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import creature as C

INTER = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
AV_COLS = [(255, 112, 112), (255, 170, 70), (120, 200, 110), (80, 170, 240), (170, 120, 240), (240, 110, 190),
           (90, 200, 200), (230, 190, 60)]


@lru_cache(maxsize=None)
def ft(path, size):
    return ImageFont.truetype(path, size)


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x2764, 0x2B50)


@lru_cache(maxsize=256)
def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new('RGBA', (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb)
    s = size / max(im.size)
    return im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.LANCZOS)


def clean(text):
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C' and ch not in '️‍')
    return ' '.join(text.split())


def text_w(s, f, size):
    return sum(size * 1.05 if is_emoji(ch) else f.getlength(ch) for ch in s)


def wrap(text, f, size, maxw, maxlines):
    words, lines, cur = clean(text).split(' '), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if text_w(t, f, size) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        while text_w(lines[-1] + '…', f, size) > maxw and ' ' in lines[-1]:
            lines[-1] = lines[-1].rsplit(' ', 1)[0]
        lines[-1] += '…'
    return lines


def draw_rich(im, d, x, y, s, f, size, fill):
    for ch in s:
        if is_emoji(ch):
            e = emoji_img(ch, int(size * 1.0))
            if e is not None:
                im.alpha_composite(e, (int(x), int(y + size * 0.12)))
            x += size * 1.05
        else:
            d.text((x, y), ch, font=f, fill=fill)
            x += f.getlength(ch)


def card_face(name, comment, w=410, h=118):
    k = h / 118
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(16 * k), fill=(255, 196, 70, 255))
    d.rounded_rectangle((int(4 * k), int(4 * k), w - 1 - int(4 * k), h - 1 - int(4 * k)), radius=int(13 * k), fill=(255, 255, 255, 255))
    av = int(44 * k)
    ax, ay = int(16 * k), int(16 * k)
    col = AV_COLS[C.h32(name, 'av') % len(AV_COLS)]
    d.ellipse((ax, ay, ax + av, ay + av), fill=col + (255,))
    ini = C.norm(name)[:1].upper() or '?'
    d.text((ax + av / 2, ay + av / 2), ini, font=ft(INTER_SB, int(24 * k)), fill=(255, 255, 255), anchor='mm')
    tx = ax + av + int(12 * k)
    fc = ft(INTER, int(22 * k))
    size = int(22 * k)
    # o nome aparece uma vez só: se a pessoa já escreveu o nome no comentário, não repete em cima
    name_line = C.norm(shown(name)) not in C.norm(comment)
    if name_line:
        d.text((tx, int(14 * k)), shown(name), font=ft(INTER_SB, int(19 * k)), fill=(115, 115, 125))
        lines = wrap(comment, fc, size, w - tx - int(46 * k), 2)
        y0 = int(40 * k)
    else:
        lines = wrap(comment, fc, size, w - tx - int(46 * k), 3)
        y0 = int((h - len(lines) * 27 * k - (22 * k if len(lines) < 3 else 0)) / 2) - int(2 * k)
    for j, ln in enumerate(lines):
        draw_rich(im, d, tx, y0 + j * int(27 * k), ln, fc, size, (22, 22, 28))
    # coração e "Responder"
    d.text((w - int(28 * k), int(52 * k)), '♡', font=ft('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(26 * k)),
           fill=(150, 150, 160), anchor='mm')
    if len(lines) < 3 and (len(lines) < 2 or not name_line):
        d.text((tx, y0 + len(lines) * int(27 * k) + int(4 * k)), 'Responder', font=ft(INTER_SB, int(16 * k)), fill=(150, 150, 160))
    return im


def shown(name):
    return name.split('#')[0]


@lru_cache(maxsize=4)
def card_back(w=410, h=118):
    import numpy as np
    import logo as L
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=16, fill=(255, 196, 70, 255))
    d.rounded_rectangle((5, 5, w - 6, h - 6), radius=12, fill=(48, 28, 86, 255))
    for x in range(-h, w, 22):                      # losangos
        d.line((x, 6, x + h, h - 6), fill=(64, 40, 110, 255), width=2)
        d.line((x + h, 6, x, h - 6), fill=(64, 40, 110, 255), width=2)
    lg = L.opt_a().resize((h - 18, h - 18), Image.NEAREST)
    im.alpha_composite(lg, ((w - lg.size[0]) // 2, 9))
    return im


DEFAULT_DECK = [  # moradores do Brasa que seguem o perfil (comentários reais, 10–11/11)
    ('Hanna', 'oi meu nome e Hanna vou ser a padeira 🥰'),
    ('Giovanna', 'Giovanna - Apotecaria'),
    ('Andréa', 'Andréa, responsável desbravar as floresta, e organizar o grupo de caça e proteger o reino.'),
    ('Yuki', 'Yuki o veterinário'),
    ('Ester', 'Ester - curandeira (antes era cozinheira)'),
    ('Lavinia', 'Lavinia - feiticeira'),
    ('Trubel', 'R (se não puder bota trubel), cozinheira'),
    ('Alexandra', 'Alexandra, exploradora de terras e recursos. diplomática mas quando precisa de força bruta está na linha de frente'),
    ('Matheus', 'Matheus- botânico ou domador'),
    ('Sabrina', 'Sabrina fazendeira'),
    ('Lila', 'LILA POR FAVOR'),
    ('Delox', 'Delox, curandeiro especializado em ervas medicinais'),
]

if __name__ == '__main__':
    sheet = Image.new('RGBA', (900, 820), (40, 26, 70, 255))
    for i, (n, c) in enumerate(DEFAULT_DECK):
        sheet.alpha_composite(card_face(n, c), (20 + (i % 2) * 440, 20 + (i // 2) * 130))
    sheet.alpha_composite(card_back(), (20, 20 + 6 * 130 - 40))
    sheet.convert('RGB').save('/tmp/claude-0/-home-claude/1ad023e2-0d5f-5b6d-b2b7-ef96b3fdfd1a/scratchpad/cartas.png')
    print('ok')
