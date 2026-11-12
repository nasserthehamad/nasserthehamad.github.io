#!/usr/bin/env python3
"""Sorteio de verdade da carta: python3 sortear.py "Ana,Bia,Caio" [--lendario]
Grava o resultado em sorteios.json. Com --lendario, o sorteado ganha raridade LENDÁRIO (fica em overrides.json)."""
import datetime, json, os, secrets, sys
import creature as C

deck = [n.strip() for n in sys.argv[1].split(',') if n.strip()]
name = secrets.choice(deck)
now = datetime.datetime.now().isoformat(timespec='seconds')
here = os.path.dirname(os.path.abspath(__file__))
log_p = os.path.join(here, 'sorteios.json')
try:
    log = json.load(open(log_p))
except Exception:
    log = []
log.append({'quando': now, 'baralho': deck, 'sorteado': name, 'lendario_forcado': '--lendario' in sys.argv})
json.dump(log, open(log_p, 'w'), ensure_ascii=False, indent=1)
if '--lendario' in sys.argv:
    ov = C.overrides()
    ov[C.norm(name)] = {'rarity': 'LENDÁRIO', 'motivo': 'sorteado do Bestiário #001; lendário forçado pra estreia (pedido do Nasser)',
                        'data': now}
    json.dump(ov, open(C._OV_PATH, 'w'), ensure_ascii=False, indent=1)
print(name)
