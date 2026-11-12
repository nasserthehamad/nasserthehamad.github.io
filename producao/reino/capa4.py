import os
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '67')
import ep4 as G
import ep1hd as E
import ep2 as P

t = 10.95
c, td = G.scene(t)
f = P.camera(c, (0, 0, 3))
im = Image.fromarray(f).convert('RGBA')
d = ImageDraw.Draw(im)
title = f'EPISÓDIO 4 · A ESTÁTUA'
tw = E.font(78).getlength(title)
E.panel(d, (540 - tw / 2 - 36, 290, 540 + tw / 2 + 36, 412), b=6)
E.draw_line(d, 540, 318, [(title, (255, 255, 255))], 78)
E.draw_line(d, 540, 500, [('BRASA', G.GOLD)], 280, stroke=14)
E.draw_line(d, 540, 760, [(f'{G.N_FOLLOW} MORADORES', (255, 255, 255))], 130)
E.draw_line(d, 540, 880, [('E UMA PEDRA ', (255, 255, 255)), ('QUE BRILHA', G.TEAL)], 112)
im.convert('RGB').save(os.path.join(G.OUTDIR, 'capa-brasa-ep4.jpg'), quality=93)
print('ok')
