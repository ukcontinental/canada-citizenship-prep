"""Slow, isolated pronunciation for every English surface form in aligned/*.json.

Each word is synthesized on its own with tools/tts_align (AVSpeech, Ava Premium,
rate 0.35 ~ 0.7x) so the pronunciation is clean and complete. Output:
html/audio/words/<key>.m4a where key = lowercase, curly apostrophe normalized.

Run: python3 tools/build_word_audio.py   (skips words that already have a file)
"""

from __future__ import annotations
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALIGNED = ROOT / "aligned"
OUT = ROOT / "html" / "audio" / "words"
TOOL = ROOT / "tools" / "tts_align"
VOICE = "com.apple.voice.premium.en-US.Ava"
RATE = "0.35"
WORKERS = 3
WORD_RE = re.compile(r"[^\W\d_](?:[^\W\d_'’\-]|['’\-](?=[^\W\d_]))*")


def key(w: str) -> str:
    return w.lower().replace("’", "'")


def all_words() -> dict[str, str]:
    seen: dict[str, str] = {}
    for f in sorted(ALIGNED.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for s in d["sections"]:
            for p in s["paras"]:
                for pair in p:
                    for w in WORD_RE.findall(pair["en"]):
                        seen.setdefault(key(w), w)
    return seen


def synth_word(k: str, surface: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        txt, wav, js = tmp / "w.txt", tmp / "w.wav", tmp / "w.json"
        txt.write_text(surface, encoding="utf-8")
        subprocess.run([str(TOOL), VOICE, RATE, str(txt), str(wav), str(js)], check=True, capture_output=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(wav), str(OUT / f"{k}.m4a")],
                       check=True, capture_output=True)
    return k


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    words = all_words()
    todo = {k: w for k, w in words.items() if not (OUT / f"{k}.m4a").exists()}
    print(f"{len(todo)} words to synthesize ({len(words)} total)", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(synth_word, k, w) for k, w in todo.items()]
        for f in as_completed(futs):
            try:
                f.result()
            except Exception as e:  # keep going; report at the end
                print("  FAILED:", e, flush=True)
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(todo)}", flush=True)
    n = len(list(OUT.glob("*.m4a")))
    size = sum(p.stat().st_size for p in OUT.glob("*.m4a")) / 1e6
    print(f"done: {n} files, {size:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
