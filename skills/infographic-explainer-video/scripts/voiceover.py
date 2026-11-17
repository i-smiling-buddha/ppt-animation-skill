"""Offline narration with Kokoro TTS (no API key, no internet once the model is downloaded).

Usage:
  python3 voiceover.py lines.txt OUT_DIR [--voice hm_omega] [--lang hi] [--speed 1.05]

lines.txt : one narration line per row (one line = one shot).
Writes OUT_DIR/00.wav, 01.wav ..., OUT_DIR/dur.json (seconds per line) and OUT_DIR/lines.json (the text, for captions).

Model files (download once, ~120 MB total) into ./tts or set KOKORO_DIR:
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
Install: pip install kokoro-onnx soundfile

Voices: Hindi hm_omega, hm_psi (male), hf_alpha, hf_beta (female) with --lang hi
        English am_michael, af_heart, bm_george ... with --lang en-us / en-gb
Tip for Hindi: write English words in Devanagari (स्लीप प्रेशर) so they are pronounced naturally.
"""
import argparse, json, os
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser()
ap.add_argument("lines"); ap.add_argument("out")
ap.add_argument("--voice", default="hm_omega"); ap.add_argument("--lang", default="hi")
ap.add_argument("--speed", type=float, default=1.05)
a = ap.parse_args()

d = os.environ.get("KOKORO_DIR", "tts")
k = Kokoro(os.path.join(d, "kokoro-v1.0.int8.onnx"), os.path.join(d, "voices-v1.0.bin"))
os.makedirs(a.out, exist_ok=True)
lines = [l.strip() for l in open(a.lines, encoding="utf-8") if l.strip()]
durs = []
for i, line in enumerate(lines):
    s, sr = k.create(line, voice=a.voice, speed=a.speed, lang=a.lang)
    idx = np.where(np.abs(s) > 0.01)[0]          # trim leading/trailing silence
    s = s[max(0, idx[0] - 800): idx[-1] + 2400]
    sf.write(os.path.join(a.out, f"{i:02d}.wav"), s, sr)
    durs.append(round(len(s) / sr, 3))
    print(f"{i:02d} {durs[-1]:.2f}s  {line[:50]}")
json.dump(durs, open(os.path.join(a.out, "dur.json"), "w"))
json.dump(lines, open(os.path.join(a.out, "lines.json"), "w", encoding="utf-8"), ensure_ascii=False)  # for captions
print("total", round(sum(durs), 2), "s")
