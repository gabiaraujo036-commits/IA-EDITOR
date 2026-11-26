"""Trilha do reels: batida 124 bpm + whoosh em cada deslize de carta + impacto na tela final."""
import sys, wave, numpy as np
sr = 44100; bpm = 124; B = 60 / bpm
T0, STEP, TR, N = 4 * B, 6 * B, 0.6, 6
TEND = T0 + N * STEP; dur = TEND + 5.6
n = int(sr * dur); out = np.zeros(n); rng = np.random.default_rng(7)
def add(sig, start, g=1.0):
    i = int(start * sr)
    if i >= n: return
    j = min(n, i + len(sig)); out[i:j] += sig[:j - i] * g
kt = np.arange(int(.35 * sr)) / sr
kick = np.sin(2 * np.pi * (48 + 100 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 8)
L = int(.05 * sr); hat = np.diff(rng.standard_normal(L) * np.exp(-np.arange(L) / sr * 90), prepend=0)
L = int(.2 * sr); clap = rng.standard_normal(L) * np.exp(-np.arange(L) / sr * 20)
roots = [220.0, 174.61, 261.63, 196.0]; th = [261.63, 220.0, 329.63, 246.94]; fi = [329.63, 261.63, 392.0, 293.66]
b = 0
while b * B < dur:
    s = b * B
    full = s >= T0 - 0.01
    add(kick, s, .9 if full or b % 2 == 0 else 0)
    add(hat, s + B / 2, .25); add(hat, s + B / 4, .1 if full else 0)
    if b % 2 == 1 and full: add(clap, s, .35)
    if b % 4 == 0:
        c = (b // 4) % 4; Ln = int(4 * B * sr); t = np.arange(Ln) / sr
        env = np.minimum(1, t * 20) * np.exp(-t * .5)
        pad = sum(np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sin(2 * np.pi * f * 1.006 * t) for f in (roots[c], th[c], fi[c]))
        add(pad * env, s, .04)
        bass = np.sin(2 * np.pi * roots[c] / 2 * t); seg = np.zeros(Ln)
        for q in range(8):
            i = int(q * B / 2 * sr); m = int(B / 2 * sr * .8); seg[i:i + m] += bass[i:i + m] * np.exp(-np.arange(m) / sr * 6)
        add(seg, s, .22 if full else .1)
    b += 1
def whoosh(d=.55):
    L = int(d * sr); t = np.arange(L) / sr; x = rng.standard_normal(L)
    f = 300 + 4000 * np.sin(np.pi * t / d) ** 2; y = np.zeros(L); a = 0.0
    for k in range(L):  # passa-baixa com corte variável
        al = 1 - np.exp(-2 * np.pi * f[k] / sr); a += al * (x[k] - a); y[k] = a
    return y * np.sin(np.pi * t / d) ** 1.5
W = whoosh(); W /= np.abs(W).max()
for k in range(N):
    add(W, T0 + k * STEP + STEP - TR - .05, .5)
add(W, .3, .45)  # entrada do baralho
L = int(.08 * sr); tick = np.sin(2 * np.pi * 1800 * np.arange(L) / sr) * np.exp(-np.arange(L) / sr * 60)
for k in range(N): add(tick, T0 + k * STEP, .25)
imp = np.sin(2 * np.pi * (40 + 120 * np.exp(-np.arange(int(1.2 * sr)) / sr * 6)) * np.arange(int(1.2 * sr)) / sr) * np.exp(-np.arange(int(1.2 * sr)) / sr * 3)
add(imp, TEND + 1.5, .8)
fl = int(1.2 * sr); out[-fl:] *= np.linspace(1, 0, fl)
out /= np.abs(out).max(); out *= .85
d = (out * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.stack([d, d], 1).tobytes())
print("dur", dur)
