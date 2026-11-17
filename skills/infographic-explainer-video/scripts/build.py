"""Inject voice durations into a master scene file and export its timeline.

Usage: python3 build.py video.html vo/dur.json build.html
video.html must contain the placeholder __DUR__ (e.g. `const VO=__DUR__;`); an optional
__LINES__ placeholder gets the narration text from lines.json next to dur.json (for captions). It must set
window.DURATION and window.TIMELINE (list of {id,start,dur,voAt}).
Writes build.html and timeline.json (next to build.html).
"""
import json, os, sys
from playwright.sync_api import sync_playwright

src, durf, out = sys.argv[1:4]
html = open(src, encoding="utf-8").read().replace("__DUR__", json.dumps(json.load(open(durf))))
linesf = os.path.join(os.path.dirname(os.path.abspath(durf)), "lines.json")
lines = json.load(open(linesf, encoding="utf-8")) if os.path.exists(linesf) else []
html = html.replace("__LINES__", json.dumps(lines, ensure_ascii=False))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "w", encoding="utf-8").write(html)
with sync_playwright() as p:
    vertical = 'viewBox="0 0 1080 1920"' in html
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920} if vertical else {"width": 1920, "height": 1080})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + os.path.abspath(out)); pg.wait_for_load_state("networkidle")
    tl = pg.evaluate("window.TIMELINE"); dur = pg.evaluate("window.DURATION")
    cues = pg.evaluate("window.CAPTION_CUES || []"); b.close()
outdir = os.path.dirname(os.path.abspath(out))
json.dump(tl, open(os.path.join(outdir, "timeline.json"), "w"), indent=1)
json.dump(cues, open(os.path.join(outdir, "captions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("duration", round(dur, 2), "s,", len(tl), "scenes,", len(cues), "caption cues,", "vertical" if vertical else "16:9", "| JS errors:", errs or "none")
