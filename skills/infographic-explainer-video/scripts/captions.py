"""Write an .srt subtitle file from the caption cues build.py exported (captions.json).

Usage: python3 captions.py _work/captions.json out.srt

Upload the .srt to YouTube (Subtitles -> Upload file) for closed captions that viewers
can switch on, search can index, and YouTube can auto-translate. The same cues are also
burned into the frames when CAPTIONS=true in the scene file.
"""
import json, sys

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

cues = json.load(open(sys.argv[1], encoding="utf-8"))
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for i, c in enumerate(cues, 1):
        end = c['b'] + 0.12 if i == len(cues) else min(c['b'] + 0.12, cues[i]['a'])
        f.write(f"{i}\n{ts(c['a'])} --> {ts(end)}\n{c['text']}\n\n")
print(len(cues), "cues ->", sys.argv[2])
