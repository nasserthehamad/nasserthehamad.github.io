#!/usr/bin/env python3
"""Quem Bate à Porta Ep. 1 — narrated version. Usage: porta_narr.py narration.mp3"""
import os, sys, json, subprocess, wave
import numpy as np
sys.path.insert(0, '/home/claude/video')
import make as M
from make import Caption, WHITE, WARM

SR = 44100
OUT = '/home/claude/video/narr'
os.makedirs(OUT, exist_ok=True)
LEAD = 0.35
ORDER = ['s1', 's2', 's3', 's4', 's5', 's6']
SENTS = {
    's1': [('3h17 da manhã.', WARM, 'Três e dezessete da manhã.'), ('Lia mora sozinha na última casa da rua.', WHITE, None)],
    's2': [('O celular vibrou.', WHITE, None), ('Ela nunca tinha visto esse número.', WHITE, None)],
    's3': [('Três segundos depois…', WHITE, None), ('alguém bateu na porta.', WHITE, None)],
    's4': [('Ela espiou pela janela.', WHITE, None), ('Tinha alguém parado embaixo do poste.', WHITE, None), ('Mexendo no celular.', WARM, None)],
    's5': [('Outra mensagem.', WHITE, None), ('E as batidas continuaram.', WHITE, None)],
}

src = sys.argv[1]
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR), OUT + '/nar.wav'], check=True)
with wave.open(OUT + '/nar.wav') as w:
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
hop = int(0.01 * SR)
rms = np.sqrt(np.convolve(x * x, np.ones(hop * 3) / (hop * 3), 'same'))[::hop]
db = 20 * np.log10(rms / rms.max() + 1e-9)
loud = db > -38
runs, i = [], 0
while i < len(loud):
    if not loud[i]:
        j = i
        while j < len(loud) and not loud[j]: j += 1
        runs.append((i * 0.01, j * 0.01)); i = j
    else:
        i += 1
first = next(k for k in range(len(loud)) if loud[k]) * 0.01
last = (len(loud) - next(k for k in range(len(loud)) if loud[::-1][k])) * 0.01
inner = [r for r in runs if r[0] > first and r[1] < last]
bounds = sorted(sorted(inner, key=lambda r: r[1] - r[0], reverse=True)[:5])
print('scene pauses:', [(round(a, 2), round(b - a, 2)) for a, b in bounds])
segs, s0 = [], first
for a, b in bounds: segs.append((s0, a)); s0 = b
segs.append((s0, last))

def splits(a, b, sents):
    """start offsets (rel. to a) and durations for each sentence."""
    L = b - a
    spoken = [s[2] or s[0] for s in sents]
    tot = sum(len(s) for s in spoken)
    cands = [r for r in inner if r[0] > a + 0.1 and r[1] < b - 0.1 and r[1] - r[0] >= 0.06]
    starts, chosen, acc, prev = [0.0], [], 0, a
    for s in spoken[:-1]:
        acc += len(s)
        f = acc / tot
        pool = [r for r in cands if r[0] > prev + 0.15]
        r = min(pool, key=lambda r: abs((r[0] - a) / L - f)) if pool else (a + L * f, a + L * f)
        chosen.append(r); starts.append(r[1] - a); prev = r[1]
    ends = [c[0] - a for c in chosen] + [L]
    return starts, [e - s for s, e in zip(starts, ends)]

M.setup()
timing = {}
for k, (a, b) in zip(ORDER, segs):
    L = b - a
    timing[k] = {'a': a, 'b': b, 'L': L}
    if k in SENTS:
        st, du = splits(a, b, SENTS[k])
        timing[k]['st'], timing[k]['du'] = st, du

def r30(v): return round(v * 30) / 30
T = timing
M.S1_DUR = r30(max(5.0, LEAD + T['s1']['L'] + 0.8))
M.S2_DUR = r30(max(5.0, LEAD + T['s2']['L'] + 1.0))
end3 = LEAD + T['s3']['L']
M.S3_KNOCKS = [end3 + 0.15, end3 + 0.5, end3 + 0.85]
M.S3_DUR = r30(end3 + 2.1)
st4 = T['s4']['st']
M.S4_PHONE = LEAD + st4[2] - 0.15
end4 = LEAD + T['s4']['L']
M.S4_KNOCKS = [end4 + 0.35, end4 + 0.7]
M.S4_DUR = r30(max(6.5, end4 + 1.3))
end5 = LEAD + T['s5']['L']
M.S5_KNOCKS = [end5 + 0.1, end5 + 0.45, end5 + 0.8]
M.S5_DUR = r30(end5 + 1.9)
M.S6_DUR = r30(max(8.5, LEAD + T['s6']['L'] + 1.6))
DURS = {'s1': M.S1_DUR, 's2': M.S2_DUR, 's3': M.S3_DUR, 's4': M.S4_DUR, 's5': M.S5_DUR, 's6': M.S6_DUR}

def gap_for(k):
    sents = SENTS[k]; du = T[k]['du']
    per = [d / len((s[2] or s[0]).split()) for s, d in zip(sents, du)]
    return float(np.clip(0.8 * min(per), 0.06, 0.3))

def times(k): return [LEAD + s for s in T[k]['st']]

t1 = times('s1'); M.S1_CAP = Caption([(LEAD - 0.05, M.S1_DUR, [(t1[0], SENTS['s1'][0][0], WARM), (t1[1], SENTS['s1'][1][0], WHITE)])], gap=gap_for('s1'))
t2 = times('s2'); M.S2_CAP = Caption([(LEAD - 0.05, t2[1] - 0.1, [(t2[0], SENTS['s2'][0][0], WHITE)]),
                                      (t2[1] - 0.05, M.S2_DUR, [(t2[1], SENTS['s2'][1][0], WHITE)])], gap=gap_for('s2'))
t3 = times('s3'); M.S3_CAP = Caption([(LEAD - 0.05, M.S3_DUR, [(t3[0], SENTS['s3'][0][0], WHITE), (t3[1], SENTS['s3'][1][0], WHITE)])], gap=gap_for('s3'))
t4 = times('s4'); M.S4_CAP = Caption([(LEAD - 0.05, t4[1] - 0.1, [(t4[0], SENTS['s4'][0][0], WHITE)]),
                                      (t4[1] - 0.05, M.S4_DUR, [(t4[1], SENTS['s4'][1][0], WHITE), (t4[2], SENTS['s4'][2][0], WARM)])], gap=gap_for('s4'))
t5 = times('s5'); M.S5_CAP = Caption([(LEAD - 0.05, t5[1] - 0.1, [(t5[0], SENTS['s5'][0][0], WHITE)]),
                                      (t5[1] - 0.05, M.S5_DUR, [(t5[1], SENTS['s5'][1][0], WHITE)])], gap=gap_for('s5'))
M.SCENES = [('s1', M.S1_DUR, M.frame_s1, True), ('s2', M.S2_DUR, M.frame_s2, True), ('s3', M.S3_DUR, M.frame_s3, True),
            ('s4', M.S4_DUR, M.frame_s4, True), ('s5', M.S5_DUR, M.frame_s5, True), ('s6', M.S6_DUR, M.frame_s6, False)]
print('durs', DURS, 'knocks3', [round(v, 2) for v in M.S3_KNOCKS], 'phone4', round(M.S4_PHONE, 2))

if len(sys.argv) > 2 and sys.argv[2] == 'preview':
    for k, tt in [('s1', t1[1] + 1.0), ('s3', M.S3_KNOCKS[1] + 0.05), ('s4', M.S4_PHONE + 0.6), ('s5', t5[1] + 0.8)]:
        fn = dict((n, f) for n, _, f, _ in M.SCENES)[k]
        fn(tt).save(f'{OUT}/prev_{k}.png')
    sys.exit(0)

M.WORK = OUT
for name, dur, fn, fo in M.SCENES:
    M.encode_scene(name, dur, fn, fo)
total = M.make_audio(OUT + '/base.wav')
with wave.open(OUT + '/base.wav') as w:
    base = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64).reshape(-1, 2) / 32768
n = len(base)
nar = np.zeros(n)
starts, acc = {}, 0.0
for name, dur, _, _ in M.SCENES:
    starts[name] = acc; acc += int(round(dur * 30)) / 30
for k in ORDER:
    a, b = T[k]['a'] - 0.04, T[k]['b'] + 0.1
    seg = x[int(a * SR):int(b * SR)]
    i = int((starts[k] + LEAD - 0.04) * SR); j = min(n, i + len(seg)); nar[i:j] += seg[:j - i]
nar *= 0.85 / np.abs(nar).max()
env = np.convolve(np.abs(nar), np.ones(int(0.15 * SR)) / int(0.15 * SR), 'same')
duck = 1 - 0.55 * np.clip(env / 0.02, 0, 1)
duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
mix = base * 0.75 * duck[:, None] + nar[:, None]
mix *= 0.89 / np.abs(mix).max()
with wave.open(OUT + '/audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
with open(OUT + '/list.txt', 'w') as f:
    for name, _, _, _ in M.SCENES: f.write(f"file '{name}.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + '/list.txt', '-c', 'copy', OUT + '/video.mp4'], check=True)
final = '/home/claude/video/quem-bate-a-porta-ep1-narrado.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', OUT + '/video.mp4', '-i', OUT + '/audio.wav', '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final + '.part.mp4'], check=True)
os.replace(final + '.part.mp4', final)
print('done', total)
