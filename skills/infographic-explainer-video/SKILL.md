---
name: infographic-explainer-video
description: Make Kurzgesagt / Infographics Show style animated explainer videos (flat-vector SVG art, motion graphics, voiceover, MP4) from a topic or script.
license: MIT
compatibility: Needs code execution with Python 3.10+, ffmpeg and headless Chromium (Playwright); one-time GitHub access to download the Kokoro voice model.
metadata:
  author: Smiling Buddha · DESITechnology
  repository: https://github.com/i-smiling-buddha/ppt-animation-skill
---

# Infographic Explainer Video

Produce a finished MP4 explainer in the *spirit* of channels like Kurzgesagt and The Infographics Show: bold flat-vector illustration, glossy gradients, glowing light, constant gentle motion, and a narrated, curiosity-driven script. Art and animation are built as code (SVG + JS timeline) and rendered frame-by-frame with Playwright + ffmpeg, so every frame is deterministic and editable.

Originality rule: imitate the *genre* (flat vector, explainer pacing), never copy a channel's characters (e.g. Kurzgesagt's birds), logos, intros, music or exact designs. Every character and scene is invented fresh.

Talk to the user in their preferred language; keep code in English.

## Bundled files (paths relative to this skill folder)

| File | Purpose |
|---|---|
| `templates/master_template.html` | 16:9 starter (1920x1080): gradients, helpers, character, brain, cloud, stars, crossfading scene engine, built-in captions. Copy it and replace the scenes. |
| `templates/vertical_template.html` | Same engine for 9:16 Shorts / Reels (1080x1920), with a vertical layout and the bottom kept clear for captions. |
| `scripts/voiceover.py` | Offline narration with Kokoro TTS (Hindi + English voices), one wav per line + `dur.json` + `lines.json` (text for captions). |
| `scripts/build.py` | Injects voice durations (`__DUR__`) and narration text (`__LINES__`), exports `timeline.json` + `captions.json`; detects 9:16; reports JS errors. |
| `scripts/captions.py` | Writes an `.srt` from `captions.json` for YouTube closed captions. |
| `scripts/peek.py` | One frame per scene → contact sheet, for checking before the full render. |
| `scripts/render.py` | Deterministic frame-range renderer (JPEG q92 → x264 CRF 18, safe temp-file rename). |
| `scripts/mix_audio.py` | Places voice lines on the timeline, adds a code-synthesized (copyright-free) ambient pad + whooshes, or your own `--music`. |
| `scripts/make_video.sh` | Whole pipeline: build → parallel render → concat → mix → mux → QA sheet → `.srt`. Detects 9:16 automatically. |

Two worked examples live in the repo, two folders above this skill folder: `examples/why-we-sleep/` (82 s, 16:9, Hindi, 11 scenes) and `examples/promo-short/` (38 s, 9:16, English, with real clips laid into a scene). Read them for scene ideas before writing new ones.

## Setup (once)

```bash
pip install playwright kokoro-onnx soundfile scipy pillow --break-system-packages
playwright install chromium          # skip if Chromium already present
mkdir -p tts && cd tts
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
ffmpeg must be on PATH. Set `KOKORO_DIR` if the model folder is not `./tts`.

## 1. Workflow (follow in order)

1. **Brief** – topic, length (default 60–90 s; Shorts = 30–58 s), aspect (16:9 1920x1080 or 9:16 1080x1920), narration language, voice source. If any is missing and the user is present, ask once; otherwise use defaults and say so.
2. **Research + script** – web-search facts for anything current or numeric, and note the source of each number. Structure: hook → question → explain in 3–5 beats → twist/scale moment → takeaway. ~150 words per minute. Short sentences, one idea each, concrete numbers and comparisons. If a finding is from animals or a single study, say so in the narration.
3. **lines.txt** – one narration line per row; one line = one scene (≈ 4–8 s). For Hindi TTS, write English loanwords in Devanagari (स्लीप प्रेशर) so they're pronounced naturally; keep on-screen text in English/Latin unless a Devanagari font is installed.
4. **Voiceover first** – `python3 scripts/voiceover.py lines.txt vo --voice hm_omega --lang hi` (English: `--voice am_michael --lang en-us`). Durations drive the timeline, never the other way round. A user-recorded voice is always better: split it into one file per line as `vo/NN.wav` and write `vo/dur.json`.
5. **Build scenes** – copy `templates/master_template.html` (16:9) or `templates/vertical_template.html` (9:16), write one `scene(...)` per line (+ optional outro). Every scene: always-on idle motion + one hero action. Use the style bible + animation kit below.
6. **Preview** – `python3 scripts/build.py video.html vo/dur.json _work/build.html && python3 scripts/peek.py _work/build.html 0.8`; LOOK at the sheet (also try 0.3) and fix overlaps, clipping, empty frames before rendering.
7. **Render + mix** – `bash scripts/make_video.sh video.html vo final.mp4` (runs one chunk per CPU core; ~3 s wall time per video second per core at 1080p).
8. **QA** – open `final_sheet.png`; check palette consistency, safe area, nothing clipped, text readable at thumbnail size, `ffprobe` duration ≈ timeline duration. Fix only broken scenes and re-render.
9. **Deliver** – the MP4, its `.srt` (upload it to YouTube as subtitles), the script text, and offer a title/description/tags + thumbnail.

## 2. Style bible

- **Shapes**: simple primitives (ellipse, roundRect, smooth freeform paths). No outlines on most shapes; a darker same-hue stroke only on hero objects.
- **Layered gradients**: almost every shape gets a 2-stop linear gradient of one hue (light top-left → saturated bottom-right) plus a white highlight at 25–40% opacity for the glossy look.
- **Glow**: light sources = radial gradient near-white → transparent, radius pulsing ±5%. Sparkles = 4-point stars twinkling via opacity sine.
- **Depth via layers**: sky gradient → far hills → mid hills → ground band with lighter blobs → subject → foreground particles; move layers at different speeds.
- **Palettes** (one per video, max 5–6 hues + a dark):
  - Space/Night: `#211840 #423AA8 #7F79D1 #E565FF #33F5FF #1552FF`
  - Day/Nature: `#00A7E2 #00D2EE #6EED65 #01CB79 #FFE4AF #FFFFFF`
  - Warm story: `#290D1C #B15141 #FFE4AF #FFCE85 #FF5F2D #FFFF47`
  - Neon pop: `#232453 #5759B9 #B6FF55 #FF0066 #A14BFF #00FFFF`
- **Background**: never pure black/white; deep tinted dark (`#12253A`, `#162B36`) or warm beige (`#E6DDC4`). Switch to a reddish dark for "danger" beats.
- **Characters**: round blob bodies, big simple eyes (white + dark pupil + catchlight), no nose, blush cheeks. Blink every ~3 s, breathe (scale 1 → 1.025). Asleep = closed-eye arcs + floating "z".
- **Text**: heavy rounded sans (Poppins Bold / Nunito ExtraBold), few words, key numbers big, labels as pill badges, inside the 90% safe area.
- **Infographics flavor**: counters that count up, bars that grow/shrink, gauges, before/after comparisons, a character reacting.

## 3. Animation kit (PowerPoint effects → code)

| PowerPoint effect | Code equivalent (helpers in the template) |
|---|---|
| Fly-in / Rise up | translate from off-screen with `outBack` ease |
| Fade / Zoom / Grow | `pop(el,t,start,x,y)` → opacity + scale with overshoot |
| Spin emphasis | `rotate(${t*deg})` around the shape's own center |
| Motion path | `along(pathEl,p)` / `getPointAtLength` |
| Morph transition | keep shared objects in place between scenes; the engine crossfades scenes (`FADE`) |
| Particle trails / fireflies | seeded `rng(seed)` particles with phase offsets, lag and size falloff |
| Wipe / draw-on | `stroke-dasharray` + `stroke-dashoffset` |
| Exit | reverse of entry with `in` ease |

Always-on idle motion: float, twinkle, glow pulse, slow parallax drift, cloud drift, the engine's slow camera push-in (`scale 1 → 1.045`). Anticipation wobble before big actions, squash-and-stretch on landings. Entries 0.4–0.8 s, stagger 60–120 ms. Never leave a frame fully still.

## 4. Engine rules (template)

- Each scene: `scene(id, bgGradientId, build() => svgString, seek(localT, sceneDuration))`.
- `seek` sets every attribute purely from `t` — no CSS animations, timers or `Math.random` (use `rng(seed)`), so any frame can be rendered alone and chunks join seamlessly.
- Element ids must be unique across the whole file (prefix with the scene id).
- Scene `i` length = `LEAD[i] + VO[i] + TAIL`; scenes beyond the narration lines are 3.2 s (outro). `MIN={2:16}` holds scene 2 for at least 16 s (e.g. for a clip laid in later). The engine exports `window.DURATION`, `window.TIMELINE`, `window.CAPTION_CUES`, `window.seek`.
- `scene(..., {cam:false})` switches off the slow camera push-in for one scene (needed when a video clip is overlaid on it).
- Captions: `CAPTIONS=true` burns word-chunk captions (from `LINES`, timed by characters within each line) into the frames; Chromium shapes Devanagari correctly. Keep the bottom ~120 px (16:9) / ~300 px (9:16) free of important art. Set `CAPTIONS=false` to turn them off; the `.srt` is still written.
- 9:16: start from `vertical_template.html` (hook text in the top third, hero visual in the middle). Scripts detect 9:16 from the SVG viewBox; never crop a 16:9 video.

## 5. Audio

- Voice: user recording → Kokoro (`scripts/voiceover.py`) → any other TTS the session offers. Kokoro Hindi voices: `hm_omega`, `hm_psi`, `hf_alpha`, `hf_beta`.
- Music: the default synthesized pad in `mix_audio.py` is original and copyright-free; or pass `--music` with a track the user owns/licensed. Never use copyrighted music.
- Captions are built in (engine rules above). `make_video.sh` also writes `final.srt`; upload it to YouTube so viewers can switch captions on and YouTube can auto-translate them.

## 6. Extras on request

- **Thumbnail**: render one hero frame at 1280x720 with a big 2–4 word label.
- **Series look**: keep palette, fonts and character functions in a shared file and reuse across episodes.
- **Outro card**: channel / pen name on the last 2–3 s.
