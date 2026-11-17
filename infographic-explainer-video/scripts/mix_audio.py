"""Lay voice lines on the timeline + an original synthesized ambient pad + soft whooshes.
100% generated in code, so the music is copyright-free.

Usage: python3 mix_audio.py timeline.json vo_dir mix.wav [--music file.mp3] [--music-vol 0.16]
Each scene with a `voAt` gets vo_dir/NN.wav placed at that time.
Pass --music to use your own (licensed) track instead of the generated pad.
"""
import argparse, json, os, subprocess
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, lfilter

ap = argparse.ArgumentParser()
ap.add_argument("timeline"); ap.add_argument("vo"); ap.add_argument("out")
ap.add_argument("--music"); ap.add_argument("--music-vol", type=float, default=0.16)
a = ap.parse_args()
SR = 48000
tl = json.load(open(a.timeline)); D = tl[-1]["start"] + tl[-1]["dur"]; N = int(D * SR) + SR

def add(arr, st, sig):
    if st >= len(arr): return
    e = min(len(arr), st + len(sig)); arr[st:e] += sig[:e - st]

voice = np.zeros(N)
for i, s in enumerate(tl):
    if s.get("voAt") is None: continue
    w, sr = sf.read(os.path.join(a.vo, f"{i:02d}.wav"))
    if w.ndim > 1: w = w.mean(1)
    if sr != SR: w = resample_poly(w, SR, sr)
    add(voice, int(s["voAt"] * SR), w)
voice = voice / (np.max(np.abs(voice)) or 1) * 0.89

t = np.arange(N) / SR
if a.music:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.music, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).astype(float); m = np.resize(m, N)
else:  # Cmaj7 - Am7 - Fmaj7 - G6 pad + bell arpeggio
    m = np.zeros(N); f = lambda n: 440 * 2 ** ((n - 69) / 12)
    chords = [[48, 55, 59, 64], [45, 52, 57, 60], [41, 48, 52, 57], [43, 50, 55, 59]]; L = 8.0
    for c in range(int(D / L) + 2):
        notes = chords[c % 4]; s0 = int(c * L * SR); seg = np.arange(int((L + 2) * SR)) / SR
        env = np.minimum(1, seg / 2.5) * np.minimum(1, np.maximum(0, (L + 2 - seg) / 2.5))
        add(m, s0, env * sum(np.sin(2*np.pi*f(n)*seg) + .5*np.sin(2*np.pi*f(n)*1.003*seg) + .2*np.sin(2*np.pi*f(n+12)*seg) for n in notes))
        for j, n in enumerate(notes + [notes[1] + 12]):
            bl = np.arange(int(2.5 * SR)) / SR
            add(m, s0 + int((j * 1.5 + .5) * SR), np.sin(2*np.pi*f(n+24)*bl) * np.exp(-bl*2.2) * .6)
    bb, aa = butter(2, 2500 / (SR / 2)); m = lfilter(bb, aa, m)
m = m * np.minimum(1, t / 2) * np.minimum(1, np.maximum(0, (D - t) / 3))
m = m / (np.max(np.abs(m)) or 1) * a.music_vol

fx = np.zeros(N); rng = np.random.default_rng(1)
b2, a2 = butter(2, [300 / (SR / 2), 3000 / (SR / 2)], "band")
for s in tl[1:]:  # whoosh into every scene change
    l = int(.7 * SR); x = np.linspace(0, 1, l)
    w = lfilter(b2, a2, rng.standard_normal(l)) * np.sin(np.pi * x) ** 2
    add(fx, int((s["start"] - .25) * SR), w / np.max(np.abs(w)) * .06)

mix = (voice + m + fx)[: int(D * SR)]; mix = mix / max(1, np.max(np.abs(mix)) / .95)
sf.write(a.out, np.stack([mix, mix], 1), SR); print("mix", round(D, 2), "s ->", a.out)
