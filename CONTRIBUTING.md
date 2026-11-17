# Contributing to PPT Animation Skill

Thanks for helping make free animated explainers easier for everyone! 🎬

## Ways to help

- **Bug reports:** a scene that renders wrong, audio out of sync, a script error. Include your OS, Python version, the command you ran and the error output.
- **Scene templates:** new reusable art (characters, planets, maps, charts, icons) or motion helpers for `templates/master_template.html`.
- **Palettes and styles:** new colour palettes with a short note on when to use them.
- **Example videos:** a `lines.txt` + `video.html` pair under `examples/<topic>/`, with a small preview image in `docs/`. Keep facts sourced.
- **Voices and languages:** tips for Kokoro voices in other languages, or support for other offline TTS engines.
- **Docs and translations:** improvements to `README.md`, `README.hi.md` or `SKILL.md`.

## Ground rules

- **Original work only.** No copyrighted characters, logos, intros, music, fonts you can't redistribute, or other people's animation files (PPTX, AEP, Lottie and so on).
- **Deterministic scenes.** Every attribute in `seek(t)` must come from `t` alone: no timers, CSS animations or `Math.random` (use `rng(seed)`).
- **Unique ids.** Prefix every element id with its scene id.
- **Check before you send.** Run `build.py` (no JS errors) and `peek.py`, and look at the contact sheet. For pipeline changes, render a short test video end to end.
- **No secrets or large binaries.** Don't commit API keys, model files (`tts/`), rendered MP4s or WAVs. `.gitignore` covers the usual ones.

## Pull requests

1. Fork the repo and create a branch: `feat/<short-name>` or `fix/<short-name>`.
2. Keep the change focused, and describe what it does and how you tested it.
3. Add a preview image for visual changes.
4. Be kind in reviews. Beginners are welcome here.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).

Made by **Smiling Buddha** · [DESITechnology](https://desitechnology.com).
