import os
import numpy as np
from PIL import Image, ImageDraw
os.environ.setdefault('N', '73')
import ep5 as G
import ep1hd as E
import ep2 as P

t = G.BR + 0.8
c = G.village(t)
G.footprints(c, G.STEP_T1 + 0.5)
f = P.camera(c, (124, 256, 5))
im = Image.fromarray(f).convert('RGBA')
d = ImageDraw.Draw(im)
title = 'EPISÓDIO 5 · A TAVERNA'
tw = E.font(78).getlength(title)
E.panel(d, (540 - tw / 2 - 36, 250, 540 + tw / 2 + 36, 372), b=6)
E.draw_line(d, 540, 278, [(title, (255, 255, 255))], 78)
E.draw_line(d, 540, 450, [('BRASA', G.GOLD)], 280, stroke=14)
E.draw_line(d, 540, 700, [('BRIGA NA ', (255, 255, 255)), ('TAVERNA', G.GOLD)], 120)
E.draw_line(d, 540, 820, [('E PEGADAS ', (255, 255, 255)), ('QUE BRILHAM', G.TEAL)], 104)
im.convert('RGB').save(os.path.join(G.OUTDIR, 'capa-brasa-ep5.jpg'), quality=93)
print('ok')
