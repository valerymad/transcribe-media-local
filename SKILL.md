---
name: transcribe-media-local
description: "Transcribe video or audio files to text with timecodes and/or SRT subtitles using local Whisper. Use this skill when the user asks to: transcribe video, create subtitles, convert speech to text, transcribe a recording, make a text version of an audio or video file. Supported formats: mp4, mov, avi, mp3, m4a, wav, flac. Works fully offline after model installation."
argument-hint: "[file-path]"
license: MIT
compatibility: Requires Python 3, ffmpeg, and openai-whisper (cross-platform). On Apple Silicon, optionally install mlx-whisper for GPU-accelerated transcription. No network access needed after model download.
metadata:
  author: valerymad
  version: "1.2.0"
---

# Transcribe video/audio

Run the bundled script via Bash to transcribe a video or audio file.

## Steps

1. Resolve the absolute path to the input file
2. Run the script:

```bash
python3 scripts/transcribe.py /absolute/path/to/file.mp4
```

3. Show the user the output and provide paths to the generated files

## CLI arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `input` | file path | required | Video or audio file |
| `--format` | `txt`, `srt`, `both` | `both` | Output format |
| `--model` | `tiny`, `base`, `small`, `medium`, `large`, `turbo` | `turbo` | Whisper model |
| `--backend` | `auto`, `mlx`, `openai` | `auto` | Inference backend (see below) |
| `--language` | `ru`, `en`, `uk`... | auto | Language hint (omit for auto-detection) |
| `--output` | directory path | same as input | Output directory |

### Backend (speed)

The script auto-selects an inference backend:

- **mlx** — runs Whisper on the Apple Silicon GPU via `mlx-whisper`. Chosen
  automatically on macOS (arm64) when `mlx-whisper` is installed. Same model,
  same quality as openai-whisper, but several times faster. Models download from
  Hugging Face (`mlx-community/...`) to `~/.cache/huggingface` on first use.
- **openai** — openai-whisper (PyTorch). Cross-platform fallback used on
  Windows/Linux/Intel Macs, or when `mlx-whisper` isn't installed. Models cache
  to `~/.cache/whisper`.

On Apple Silicon, install the fast backend once with `pip install mlx-whisper`.
Force a backend with `--backend mlx` / `--backend openai` (e.g. to reproduce
identical output across machines). The TXT/SRT output is identical either way.

Rough throughput on an M2 (`turbo`): mlx ≈ 8–10× real time, openai ≈ 3–4×.

### Choosing a model

`turbo` (large-v3-turbo) is the default — clearly the best transcription quality
of the lineup, still faster than real time, ~1.6 GB download, ~5 GB RAM at runtime.
Drop to `small` only when RAM is tight (~2.3 GB) or for quick rough drafts; it is
noticeably weaker on noisy/quiet audio. `medium`/`large` are rarely worth it now —
`turbo` matches or beats them for most languages at a fraction of the cost.

## Example output

```
⏳ Loading 'turbo'...
✅ Model 'turbo' ready
🎬 Transcribing: video.mp4
🌐 Language: en | Segments: 12
📄 TXT: /Users/user/video.txt
📄 SRT: /Users/user/video.srt

✅ Done! Saved: 2 file(s)
```

## Notes

- On first run with a model not yet cached, the script prints a "downloading" message and Whisper fetches it to `~/.cache/whisper/` automatically.
- If automatic download fails (e.g. no network), the script prints the manual download URL — show it to the user.
- If `whisper` or `ffmpeg` is missing, tell the user to install: `pip install openai-whisper` / `brew install ffmpeg`.
- On Apple Silicon, `pip install mlx-whisper` enables the faster GPU backend (auto-selected). Without it, the skill still works via openai-whisper.
