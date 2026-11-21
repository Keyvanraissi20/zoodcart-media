#!/usr/bin/env python3
"""Gemini text-to-speech for ZoodCart content.

API key is read from the GEMINI_API_KEY environment variable (never hard-code it).

Usage:
  python tts/gemini_tts.py --text "سلام" --out out.wav [--voice Kore] [--style "..."]
  python tts/gemini_tts.py --request tts/requests/foo.json        # one request file
  python tts/gemini_tts.py --process-all                          # every request without output

Request file (tts/requests/<id>.json):
  {"text": "...", "voice": "Kore", "style": "با لحن گرم و صمیمی بخوان", "model": "optional"}
Output: tts/output/<id>.wav (+ .m4a when ffmpeg is available)
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQ_DIR = ROOT / "requests"
OUT_DIR = ROOT / "output"

# Tried in order; override with --model or GEMINI_TTS_MODEL.
DEFAULT_MODELS = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts"]
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SAMPLE_RATE = 24000  # Gemini TTS returns 16-bit mono PCM at 24 kHz


def synthesize(text, voice="Kore", style=None, model=None):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set")
    prompt = f"{style}:\n{text}" if style else text
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    models = [model] if model else ([os.environ["GEMINI_TTS_MODEL"]] if os.environ.get("GEMINI_TTS_MODEL") else DEFAULT_MODELS)
    last_err = None
    for m in models:
        for attempt in range(3):
            req = urllib.request.Request(
                API.format(model=m),
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json", "x-goog-api-key": key},
            )
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = json.load(r)
                part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
                print(f"model={m} mime={part.get('mimeType')}")
                return base64.b64decode(part["data"]), part.get("mimeType", "")
            except urllib.error.HTTPError as e:
                last_err = f"{m}: HTTP {e.code} {e.read().decode(errors='ignore')[:300]}"
                if e.code in (429, 500, 503):
                    time.sleep(5 * (attempt + 1))
                    continue
                break  # 404 / 400 → try next model
            except (KeyError, IndexError) as e:
                last_err = f"{m}: unexpected response ({e})"
                break
    sys.exit(f"TTS failed. Last error: {last_err}")


def save(audio, mime, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if "wav" in mime:
        out_path.write_bytes(audio)
    else:  # raw PCM (audio/L16)
        with wave.open(str(out_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            w.writeframes(audio)
    print(f"saved {out_path}")
    if shutil.which("ffmpeg"):
        m4a = out_path.with_suffix(".m4a")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out_path), "-c:a", "aac", "-b:a", "128k", str(m4a)], check=True)
        print(f"saved {m4a}")


def run_request(path):
    path = Path(path)
    req = json.loads(path.read_text(encoding="utf-8"))
    audio, mime = synthesize(req["text"], req.get("voice", "Kore"), req.get("style"), req.get("model"))
    save(audio, mime, OUT_DIR / f"{path.stem}.wav")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text")
    p.add_argument("--out", default="out.wav")
    p.add_argument("--voice", default="Kore")
    p.add_argument("--style")
    p.add_argument("--model")
    p.add_argument("--request")
    p.add_argument("--process-all", action="store_true")
    a = p.parse_args()

    if a.process_all:
        todo = [r for r in sorted(REQ_DIR.glob("*.json")) if not (OUT_DIR / f"{r.stem}.wav").exists()]
        print(f"{len(todo)} request(s) to process")
        for r in todo:
            run_request(r)
    elif a.request:
        run_request(a.request)
    elif a.text:
        audio, mime = synthesize(a.text, a.voice, a.style, a.model)
        save(audio, mime, a.out)
    else:
        p.error("give --text, --request or --process-all")


if __name__ == "__main__":
    main()
