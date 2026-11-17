"""Deterministic frame-by-frame render of a scene file to MP4.

Usage:
  python3 render.py build.html out.mp4 [--from F0] [--to F1] [--fps 30] [--vertical]

The page must expose window.DURATION (s) and window.seek(t).
--from/--to render a frame range (for parallel chunks; join with the concat demuxer).
Writes to out.part.mp4 first and renames only when ffmpeg succeeds.
"""
import argparse, os, subprocess
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out")
ap.add_argument("--from", dest="f0", type=int, default=0); ap.add_argument("--to", dest="f1", type=int, default=None)
ap.add_argument("--fps", type=int, default=30); ap.add_argument("--vertical", action="store_true")
a = ap.parse_args()
W, H = (1080, 1920) if a.vertical else (1920, 1080)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
    pg.goto("file://" + os.path.abspath(a.html)); pg.wait_for_load_state("networkidle")
    n = int(pg.evaluate("window.DURATION") * a.fps); f1 = min(n, a.f1 if a.f1 is not None else n)
    tmp = a.out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(a.fps), tmp],
                          stdin=subprocess.PIPE)
    for i in range(a.f0, f1):
        pg.evaluate(f"window.seek({i / a.fps})")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
    ff.stdin.close(); rc = ff.wait(); b.close()
if rc == 0:
    os.replace(tmp, a.out); print("ok", a.out, f1 - a.f0, "frames")
else:
    raise SystemExit("ffmpeg failed")
