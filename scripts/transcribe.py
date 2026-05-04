#!/usr/bin/env python3
"""
Transcribe video/audio files using local Whisper model.
Outputs TXT with timecodes and/or SRT subtitles.

Usage:
    python transcribe.py input.mp4
    python transcribe.py input.mp4 --format srt
    python transcribe.py input.mp4 --format both --language ru
    python transcribe.py input.mp4 --model small --output /path/to/output
"""

import argparse
import os
import sys
from pathlib import Path


# Whisper model download URLs (from https://github.com/openai/whisper)
MODEL_URLS = {
    "tiny":   "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
    "base":   "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
    "small":  "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
    "medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
    "large":  "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
}

MODEL_SIZES = {
    "tiny":   "73 MB",
    "base":   "142 MB",
    "small":  "462 MB",
    "medium": "1.5 GB",
    "large":  "3 GB",
}

WHISPER_CACHE = os.path.expanduser("~/.cache/whisper")


def format_timestamp_txt(seconds: float) -> str:
    """MM:SS for TXT output."""
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def format_timestamp_srt(seconds: float) -> str:
    """HH:MM:SS,mmm for SRT output."""
    total_ms = int(seconds * 1000)
    h = total_ms // 3_600_000
    m = (total_ms % 3_600_000) // 60_000
    s = (total_ms % 60_000) // 1000
    ms = total_ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def check_model_available(model_name: str) -> bool:
    model_path = os.path.join(WHISPER_CACHE, f"{model_name}.pt")
    return os.path.exists(model_path) and os.path.getsize(model_path) > 1_000_000


def print_install_instructions(model_name: str):
    url = MODEL_URLS.get(model_name, MODEL_URLS["small"])
    print(f"\n❌ Model '{model_name}' not found.")
    print(f"\nDownload manually:")
    print(f"  {url}")
    print(f"\nPlace the file here:")
    print(f"  {WHISPER_CACHE}/{model_name}.pt")


def load_model(preferred: str):
    """Load model. If not cached, Whisper downloads it to ~/.cache/whisper/."""
    import whisper

    if not check_model_available(preferred):
        size = MODEL_SIZES.get(preferred, "?")
        print(f"⬇️  Model '{preferred}' not cached. Downloading (~{size}, one-time)...")
        print(f"   Cache location: {WHISPER_CACHE}/")

    print(f"⏳ Loading '{preferred}'...")
    try:
        model = whisper.load_model(preferred)
        print(f"✅ Model '{preferred}' ready")
        return model
    except Exception as e:
        print(f"❌ Failed to load model '{preferred}': {e}")
        print_install_instructions(preferred)
        sys.exit(1)


def generate_txt(segments: list) -> str:
    lines = []
    for seg in segments:
        text = seg["text"].strip()
        if text:
            lines.append(f"{format_timestamp_txt(seg['start'])} {text}")
    return "\n".join(lines)


def generate_srt(segments: list) -> str:
    blocks = []
    for i, seg in enumerate(segments, 1):
        text = seg["text"].strip()
        if text:
            start = format_timestamp_srt(seg["start"])
            end = format_timestamp_srt(seg["end"])
            blocks.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(blocks)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe video/audio using local Whisper"
    )
    parser.add_argument("input", help="Path to video or audio file")
    parser.add_argument(
        "--format", choices=["txt", "srt", "both"], default="both",
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--model", choices=["tiny", "base", "small", "medium", "large"], default="small",
        help="Whisper model (default: small)"
    )
    parser.add_argument(
        "--language", default=None,
        help="Language: ru, en, uk, etc. (default: auto-detect)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output directory (default: same as input file)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    output_dir = Path(args.output or Path(args.input).parent)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(args.input).stem

    model = load_model(args.model)

    print(f"🎬 Transcribing: {Path(args.input).name}")
    kwargs = {"word_timestamps": True, "verbose": False}
    if args.language:
        kwargs["language"] = args.language

    result = model.transcribe(args.input, **kwargs)
    segments = result["segments"]
    lang = result.get("language", "?")
    print(f"🌐 Language: {lang} | Segments: {len(segments)}")

    saved = []
    if args.format in ("txt", "both"):
        path = output_dir / f"{stem}.txt"
        path.write_text(generate_txt(segments), encoding="utf-8")
        print(f"📄 TXT: {path}")
        saved.append(str(path))

    if args.format in ("srt", "both"):
        path = output_dir / f"{stem}.srt"
        path.write_text(generate_srt(segments), encoding="utf-8")
        print(f"📄 SRT: {path}")
        saved.append(str(path))

    print(f"\n✅ Done! Saved: {len(saved)} file(s)")


if __name__ == "__main__":
    main()
