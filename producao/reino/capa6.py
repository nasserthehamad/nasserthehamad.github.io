import os
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '77')
import ep6 as G
import ep1hd as E
import ep2 as P

t = 0.9
c = G.village(t)
f = P.camera(c, (154, 320, 6))
im = Image.fromarray(f).convert('RGBA')
d = ImageDraw.Draw(im)
title = 'EPISÓDIO 6 · O VIAJANTE'
tw = E.font(78).getlength(title)
E.panel(d, (540 - tw / 2 - 36, 250, 540 + tw / 2 + 36, 372), b=6)
E.draw_line(d, 540, 278, [(title, (255, 255, 255))], 78)
E.draw_line(d, 540, 450, [('BRASA', G.GOLD)], 280, stroke=14)
E.draw_line(d, 540, 700, [('AS PEGADAS ', (255, 255, 255)), ('ERAM DELE', G.TEAL)], 116)
im.convert('RGB').save(os.path.join(G.OUTDIR, 'capa-brasa-ep6.jpg'), quality=93)
print('ok')
