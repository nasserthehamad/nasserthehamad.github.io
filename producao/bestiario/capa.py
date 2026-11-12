import os, sys
os.environ.setdefault('NAME', 'Letícia')
import roleta as R
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/reino')
import ep1hd as E
im = Image.fromarray(R.frame(R.COUNT1 + 0.6)).convert('RGBA')
d = ImageDraw.Draw(im)
title = 'ROLETA DO NOME #001'
tw = E.font(64).getlength(title)
E.panel(d, (540 - tw / 2 - 30, 96, 540 + tw / 2 + 30, 196), b=6)
E.draw_line(d, 540, 122, [(title, (255, 255, 255))], 64)
E.draw_line(d, 540, 1560, [(f"{R.TR['rarity']} · {R.TR['pct']['RARIDADE']}%", R.RC)], 120)
slug = R.C.norm(R.NAME).replace(' ', '-')
im.convert('RGB').save(os.path.join(R.OUT, f'capa-bestiario-{slug}.jpg'), quality=93)
print('ok')
