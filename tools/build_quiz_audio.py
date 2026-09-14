"""Narrate each quiz question (question + lettered options) with Ava Premium.

Output: html/audio/quiz/<id>.m4a. Skips ids whose text hash is unchanged.
Run: python3 tools/build_quiz_audio.py
"""

from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from quiz_content import load_questions  # noqa: E402

OUT = ROOT / "html" / "audio" / "quiz"
TOOL = ROOT / "tools" / "tts_align"
VOICE = "com.apple.voice.premium.en-US.Ava"
RATE = "0.47"
LETTERS = "ABCDE"


def text_of(q: dict) -> str:
    opts = ". ".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(q["o"]))
    return f"{q['q']} {opts}."


def synth(qid: str, text: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "q.txt").write_text(text, encoding="utf-8")
        subprocess.run([str(TOOL), VOICE, RATE, str(tmp / "q.txt"), str(tmp / "q.wav"), str(tmp / "q.json")],
                       check=True, capture_output=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(tmp / "q.wav"), str(OUT / f"{qid}.m4a")],
                       check=True, capture_output=True)
    return qid


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hpath = OUT / "hashes.json"
    hashes = json.loads(hpath.read_text()) if hpath.exists() else {}
    todo = []
    for q in load_questions():
        t = text_of(q)
        h = hashlib.md5((VOICE + RATE + t).encode()).hexdigest()
        if hashes.get(q["id"]) == h and (OUT / f"{q['id']}.m4a").exists():
            continue
        todo.append((q["id"], t, h))
    print(f"{len(todo)} questions to narrate", flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(synth, qid, t): (qid, h) for qid, t, h in todo}
        for i, f in enumerate(as_completed(futs), 1):
            qid, h = futs[f]
            try:
                f.result(); hashes[qid] = h
            except Exception as e:
                print("  FAILED", qid, e, flush=True)
            if i % 25 == 0:
                print(f"  {i}/{len(todo)}", flush=True)
    hpath.write_text(json.dumps(hashes))
    n = len(list(OUT.glob("*.m4a")))
    print(f"done: {n} files, {sum(p.stat().st_size for p in OUT.glob('*.m4a'))/1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
