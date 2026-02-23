# transcribe-media-local

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for transcribing video and audio files using local [Whisper](https://github.com/openai/whisper).

Works **fully offline** after one-time model download. Supports 100+ languages.

## Installation

Copy the skill directory into your Claude Code skills folder:

```bash
cp -r transcribe-media-local ~/.claude/skills/transcribe-media-local
```

### Dependencies

```bash
pip install openai-whisper
```

ffmpeg must be installed:

```bash
# macOS
brew install ffmpeg

# Linux
apt install ffmpeg
```

### Whisper model (one-time download)

Download a model and place it in `~/.cache/whisper/`:

| Model | Size | Quality | Download |
|-------|------|---------|----------|
| tiny | 73 MB | low | [tiny.pt](https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt) |
| small | 462 MB | good | [small.pt](https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt) (recommended) |
| medium | 1.5 GB | high | [medium.pt](https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt) |
| large | 3 GB | best | [large-v3.pt](https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt) |

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

## License

MIT
