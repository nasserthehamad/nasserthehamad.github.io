"""Melodia puxada pelas batidas: cada batida libera a próxima nota da melodia, mas a nota toca no ritmo da música.
Batida rápida: as notas fazem fila e tocam no tempo certo (até ~1,7x mais rápido se a fila crescer).
Batida devagar: a música espera a próxima batida. O acompanhamento ('b') segue o relógio da música sem gastar batida."""

# Für Elise (Beethoven, 1810, domínio público), seção A em semicolcheias (3/8 = 6 por compasso). 'm' = melodia, 'b' = baixo.
_P = [[(76, 'm')], [(75, 'm')]]
_M1 = [[(76, 'm')], [(75, 'm')], [(76, 'm')], [(71, 'm')], [(74, 'm')], [(72, 'm')]]
_M2 = [[(69, 'm'), (45, 'b')], [(52, 'b')], [(57, 'b')], [(60, 'm')], [(64, 'm')], [(69, 'm')]]
_M3 = [[(71, 'm'), (40, 'b')], [(52, 'b')], [(56, 'b')], [(64, 'm')], [(68, 'm')], [(71, 'm')]]
_M4 = [[(72, 'm'), (45, 'b')], [(52, 'b')], [(57, 'b')], [(64, 'm')], [(76, 'm')], [(75, 'm')]]
_M7 = [[(71, 'm'), (40, 'b')], [(52, 'b')], [(56, 'b')], [(64, 'm')], [(72, 'm')], [(71, 'm')]]
_M8 = [[(69, 'm'), (45, 'b')], [(52, 'b')], [(57, 'b')], [], [(76, 'm')], [(75, 'm')]]
FUR_ELISE = _P + (_M1 + _M2 + _M3 + _M4 + _M1 + _M2 + _M7 + _M8) * 8


def schedule(score, credits, q, t_end, lead=5, max_speed=1.7, max_backlog=6):
    """devolve [(tempo, midi, papel)]. credits = tempos das batidas (em ordem).
    A j-ésima nota da melodia precisa da batida j-lead (a música pode andar 'lead' notas na frente das batidas,
    pra frase de abertura sair no ritmo). Se as batidas acumulam, a música acelera até max_speed."""
    import bisect
    credits = sorted(credits)
    out = []
    if not credits:
        return out
    t = credits[0]
    j = 0
    speed = 1.0
    for step in score:
        has_m = any(r == 'm' for _, r in step)
        if has_m:
            need = j - lead
            if need >= len(credits):
                break
            if need >= 0:
                t = max(t, credits[need])
            j += 1
            done = bisect.bisect_right(credits, t)          # batidas que já aconteceram
            backlog = done - max(0, j - lead)
            speed = 1 + (max_speed - 1) * min(1.0, max(0, backlog) / max_backlog)
        if t >= t_end:
            break
        for m, r in step:
            out.append((t, m, r))
        t += q / speed
    return out
