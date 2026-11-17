"""Preview: one frame per scene (at a fraction of each scene) tiled into a contact sheet.

Usage: python3 peek.py build.html [fraction=0.8] [--vertical]
Writes peek_<fraction>.jpg next to build.html. Look at it before the full render.
"""
import json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image

html = os.path.abspath(sys.argv[1])
frac = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 0.8
W, H = (1080, 1920) if "--vertical" in sys.argv else (1920, 1080)
tw, th = (W // 3, H // 3)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
    pg.goto("file://" + html); pg.wait_for_load_state("networkidle")
    tl = pg.evaluate("window.TIMELINE"); ims = []
    for s in tl:
        pg.evaluate(f"window.seek({s['start'] + s['dur'] * frac})")
        pg.screenshot(path="/tmp/_peek.jpg", type="jpeg", quality=80)
        ims.append(Image.open("/tmp/_peek.jpg").resize((tw, th)))
    b.close()
cols = 3; rows = (len(ims) + cols - 1) // cols
g = Image.new("RGB", (tw * cols, th * rows))
for i, im in enumerate(ims): g.paste(im, ((i % cols) * tw, (i // cols) * th))
out = os.path.join(os.path.dirname(html), f"peek_{frac}.jpg"); g.save(out); print(out)
