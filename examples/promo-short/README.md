# Example: promo Short (9:16)

The 38-second vertical promo for this skill, made with the same pipeline. English narration, Kokoro voice `am_michael`.

```bash
S=../../skills/infographic-explainer-video/scripts
python3 $S/voiceover.py lines.txt vo --voice am_michael --lang en-us --speed 1.08
bash   $S/make_video.sh promo.html vo promo.mp4
```

Scene 3 ("This is what it made") leaves a black 1080x608 box at y = 656 and holds for 16.9 s (`MIN`).
Clips from the Why We Sleep example were laid into that box afterwards:

```bash
# 4 x 4 s highlights from the 16:9 video, scaled to 1080 wide
ffmpeg -ss 4 -t 4 -i why_we_sleep.mp4 -an -vf scale=1080:608,fps=30 clip0.mp4   # repeat for 18.6, 38.4, 73.6
# concat them to clips.mp4, then overlay at the scene's start (+0.45 s crossfade)
ffmpeg -i promo.mp4 -itsoffset 10.45 -i clips.mp4 \
  -filter_complex "[0:v][1:v]overlay=0:656:enable='between(t,10.45,26.44)'[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy promo_final.mp4
```
