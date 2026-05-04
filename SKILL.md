---
name: transcribe-media-local
description: "Transcribe video or audio files to text with timecodes and/or SRT subtitles using local Whisper. Use this skill when the user asks to: transcribe video, create subtitles, convert speech to text, transcribe a recording, make a text version of an audio or video file. Supported formats: mp4, mov, avi, mp3, m4a, wav, flac. Works fully offline after model installation."
argument-hint: "[file-path]"
license: MIT
compatibility: Requires Python 3, ffmpeg, and openai-whisper. No network access needed after model download.
metadata:
  author: valerymad
  version: "1.0.0"
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
| `--model` | `tiny`, `base`, `small`, `medium`, `large` | `small` | Whisper model size |
| `--language` | `ru`, `en`, `uk`... | auto | Language hint (omit for auto-detection) |
| `--output` | directory path | same as input | Output directory |

## Example output

```
⏳ Loading 'small'...
✅ Model 'small' ready
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
