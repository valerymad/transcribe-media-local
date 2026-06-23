#!/usr/bin/env python3
"""
Transcribe video/audio files using local Whisper.
Outputs TXT with timecodes and/or SRT subtitles.

Backends (auto-selected):
  - mlx    : Apple Silicon GPU via mlx-whisper (fast). macOS arm64 only.
  - openai : openai-whisper (PyTorch, CPU/CUDA). Cross-platform fallback.

Usage:
    python transcribe.py input.mp4
    python transcribe.py input.mp4 --format srt
    python transcribe.py input.mp4 --format both --language ru
    python transcribe.py input.mp4 --model small --output /path/to/output
    python transcribe.py input.mp4 --backend openai   # force PyTorch backend
"""

import argparse
import importlib.util
import os
import platform
import sys
from pathlib import Path


# Whisper model download URLs (from https://github.com/openai/whisper)
MODEL_URLS = {
    "tiny":   "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
    "base":   "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
    "small":  "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
    "medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
    "large":  "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
    "turbo":  "https://openaipublic.azureedge.net/main/whisper/models/aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a/large-v3-turbo.pt",
}

MODEL_SIZES = {
    "tiny":   "73 MB",
    "base":   "142 MB",
    "small":  "462 MB",
    "medium": "1.5 GB",
    "large":  "3 GB",
    "turbo":  "1.6 GB",
}

# Whisper caches each model under the URL's basename, which is not always
# "{name}.pt" (e.g. "turbo" is stored as "large-v3-turbo.pt").
MODEL_CACHE_STEM = {
    "tiny":   "tiny",
    "base":   "base",
    "small":  "small",
    "medium": "medium",
    "large":  "large-v3",
    "turbo":  "large-v3-turbo",
}

# Hugging Face repos for the MLX backend (mlx-community).
MLX_REPOS = {
    "tiny":   "mlx-community/whisper-tiny-mlx",
    "base":   "mlx-community/whisper-base-mlx",
    "small":  "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large":  "mlx-community/whisper-large-v3-mlx",
    "turbo":  "mlx-community/whisper-large-v3-turbo",
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


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------

def mlx_available() -> bool:
    """MLX runs only on Apple Silicon and requires the mlx-whisper package."""
    if sys.platform != "darwin" or platform.machine() != "arm64":
        return False
    return importlib.util.find_spec("mlx_whisper") is not None


def resolve_backend(forced: str) -> str:
    """Return the effective backend: 'mlx' or 'openai'."""
    if forced == "mlx":
        if not mlx_available():
            print("❌ --backend mlx requested but mlx-whisper is unavailable.")
            print("   It needs macOS on Apple Silicon and: pip install mlx-whisper")
            sys.exit(1)
        return "mlx"
    if forced == "openai":
        return "openai"
    # auto: prefer the fast GPU backend on Apple Silicon, else fall back
    return "mlx" if mlx_available() else "openai"


# ---------------------------------------------------------------------------
# openai-whisper backend (PyTorch, CPU/CUDA — cross-platform)
# ---------------------------------------------------------------------------

def check_model_available(model_name: str) -> bool:
    stem = MODEL_CACHE_STEM.get(model_name, model_name)
    model_path = os.path.join(WHISPER_CACHE, f"{stem}.pt")
    return os.path.exists(model_path) and os.path.getsize(model_path) > 1_000_000


def print_openai_install_instructions(model_name: str):
    url = MODEL_URLS.get(model_name, MODEL_URLS["small"])
    print(f"\n❌ Model '{model_name}' not found.")
    print(f"\nDownload manually:")
    print(f"  {url}")
    stem = MODEL_CACHE_STEM.get(model_name, model_name)
    print(f"\nPlace the file here:")
    print(f"  {WHISPER_CACHE}/{stem}.pt")


def transcribe_openai(input_path: str, model_name: str, language):
    """Transcribe via openai-whisper. Returns (segments, language)."""
    try:
        import whisper
    except ImportError:
        print("❌ openai-whisper is not installed. Install it with: pip install openai-whisper")
        sys.exit(1)

    if not check_model_available(model_name):
        size = MODEL_SIZES.get(model_name, "?")
        print(f"⬇️  Model '{model_name}' not cached. Downloading (~{size}, one-time)...")
        print(f"   Cache location: {WHISPER_CACHE}/")

    print(f"⏳ Loading '{model_name}' (openai-whisper)...")
    try:
        model = whisper.load_model(model_name)
    except Exception as e:
        print(f"❌ Failed to load model '{model_name}': {e}")
        print_openai_install_instructions(model_name)
        sys.exit(1)
    print(f"✅ Model '{model_name}' ready")

    # NOTE: no word_timestamps — TXT/SRT only use segment-level start/end,
    # and word-level alignment roughly triples runtime for data we discard.
    kwargs = {"verbose": False}
    if language:
        kwargs["language"] = language

    print(f"🎬 Transcribing: {Path(input_path).name}")
    result = model.transcribe(input_path, **kwargs)
    return result["segments"], result.get("language", "?")


# ---------------------------------------------------------------------------
# MLX backend (Apple Silicon GPU)
# ---------------------------------------------------------------------------

def transcribe_mlx(input_path: str, model_name: str, language):
    """Transcribe via mlx-whisper. Returns (segments, language)."""
    import mlx_whisper

    repo = MLX_REPOS.get(model_name, MLX_REPOS["turbo"])
    print(f"⏳ Loading '{model_name}' via MLX ({repo})...")
    print(f"   (first run downloads the model from Hugging Face to ~/.cache/huggingface)")

    kwargs = {"path_or_hf_repo": repo}
    if language:
        kwargs["language"] = language

    print(f"🎬 Transcribing: {Path(input_path).name}")
    try:
        result = mlx_whisper.transcribe(input_path, **kwargs)
    except Exception as e:
        print(f"❌ MLX transcription failed: {e}")
        print("   Tip: retry with --backend openai to use the PyTorch backend.")
        sys.exit(1)
    return result["segments"], result.get("language", "?")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

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
        "--model", choices=["tiny", "base", "small", "medium", "large", "turbo"], default="turbo",
        help="Whisper model (default: turbo — best quality/speed balance; use 'small' for low RAM)"
    )
    parser.add_argument(
        "--backend", choices=["auto", "mlx", "openai"], default="auto",
        help="Inference backend (default: auto — mlx on Apple Silicon, else openai-whisper)"
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

    backend = resolve_backend(args.backend)
    print(f"🧠 Backend: {backend}")

    if backend == "mlx":
        segments, lang = transcribe_mlx(args.input, args.model, args.language)
    else:
        segments, lang = transcribe_openai(args.input, args.model, args.language)

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
