# transcribe-media-local

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for transcribing video and audio files using local [Whisper](https://github.com/openai/whisper).

Works **fully offline** after one-time model download. Supports 100+ languages.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.8+
- ffmpeg

## Installation

### 1. Clone the skill into your Claude Code skills folder

```bash
git clone https://github.com/valerymad/transcribe-media-local.git \
  ~/.claude/skills/transcribe-media-local
```

### 2. Install dependencies

```bash
pip install openai-whisper

# macOS
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt install ffmpeg
```

That's it. The Whisper model downloads automatically on first run (~1.6 GB for the default `turbo` model, cached to `~/.cache/whisper/`). On a low-RAM machine, pass `--model small` (~462 MB) instead.

## Updating

```bash
cd ~/.claude/skills/transcribe-media-local && git pull
```

No restart needed — the next skill invocation picks up the new version automatically.

### Manual model download (optional, e.g. for offline machines)

If automatic download fails or you need to prepare an offline machine, download a model manually:

```bash
mkdir -p ~/.cache/whisper
curl -L -o ~/.cache/whisper/large-v3-turbo.pt \
  https://openaipublic.azureedge.net/main/whisper/models/aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a/large-v3-turbo.pt
```

Available models (note the cache filename differs from the `--model` name for `large`/`turbo`):

| `--model` | Cache file | Download size | RAM at runtime | Quality | Download |
|-----------|------------|---------------|----------------|---------|----------|
| tiny | tiny.pt | 73 MB | ~0.4 GB | low | [tiny.pt](https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt) |
| small | small.pt | 462 MB | ~2.3 GB | good (low-RAM pick) | [small.pt](https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt) |
| medium | medium.pt | 1.5 GB | ~5 GB | high | [medium.pt](https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt) |
| large | large-v3.pt | 3 GB | ~10 GB | very high | [large-v3.pt](https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt) |
| **turbo** | large-v3-turbo.pt | 1.6 GB | ~5 GB | **best balance (default)** | [large-v3-turbo.pt](https://openaipublic.azureedge.net/main/whisper/models/aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a/large-v3-turbo.pt) |

`turbo` (large-v3-turbo) is a pruned large-v3 with 4 decoder layers instead of 32 — near-large quality, far less compute. It is the default. Use `small` only when RAM is constrained.

All model URLs: [openai/whisper](https://github.com/openai/whisper/blob/main/whisper/__init__.py)

## Usage with Claude Code

Just ask Claude:

> "Transcribe video.mp4"
> "Create subtitles for recording.mp4"
> "Convert meeting.m4a speech to text"

## CLI usage

```bash
# TXT + SRT (default)
python scripts/transcribe.py video.mp4

# SRT only
python scripts/transcribe.py video.mp4 --format srt

# Specify language and model
python scripts/transcribe.py video.mp4 --language ru --model medium

# Custom output directory
python scripts/transcribe.py video.mp4 --output ~/Desktop/
```

## Output formats

**TXT** — one phrase per line with timecodes:

```
00:00 What if your brain itself becomes technology?
00:02 This is exactly where Neuralink comes in.
```

**SRT** — standard subtitle format:

```
1
00:00:00,000 --> 00:00:02,640
What if your brain itself becomes technology?

2
00:00:02,820 --> 00:00:05,320
This is exactly where Neuralink comes in.
```

## Project structure

```
transcribe-media-local/
├── SKILL.md          # Instructions for Claude (Agent Skills standard)
├── README.md         # This file
├── LICENSE
├── .gitignore
└── scripts/
    └── transcribe.py # CLI script
```

## Troubleshooting

**`whisper: command not found` or `ModuleNotFoundError: No module named 'whisper'`**
Run `pip install openai-whisper`. If you use `pyenv`/`conda`, make sure it's the same Python that Claude Code's Bash tool sees (`python3 -c "import whisper"`).

**`ffmpeg: command not found`**
Install via `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux), then restart your terminal.

**Script says "model not found"**
Check that the `.pt` file is exactly in `~/.cache/whisper/` (not in a subfolder) and the filename matches Whisper's cache name. Most models use `{name}.pt` (`small.pt`, `medium.pt`), but `turbo` is cached as `large-v3-turbo.pt` and `large` as `large-v3.pt` — see the table above.

**Claude doesn't pick up the skill**
Restart Claude Code after copying the folder. Verify it's in the right place: `ls ~/.claude/skills/transcribe-media-local/SKILL.md`.

---

Built by [@valerymad](https://github.com/valerymad). If this saved you time, a ⭐ helps others find it.

## License

MIT
