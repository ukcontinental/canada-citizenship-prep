"""Narrate each quiz question (question + lettered options) in both languages.

English with Ava Premium, Chinese with Meijia Premium — the quiz pages show the
two side by side, so both need a voice.

Output: html/audio/quiz/{en,zh}/<id>.m4a. Skips ids whose text hash is unchanged.
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
VOICE = {"en": "com.apple.voice.premium.en-US.Ava",
         "zh": "com.apple.voice.premium.zh-TW.Meijia"}
RATE = {"en": "0.47", "zh": "0.5"}
LETTERS = "ABCDE"


def text_of(q: dict, lang: str) -> str:
    if lang == "zh":
        opts = "。".join(f"{LETTERS[i]}、{o}" for i, o in enumerate(q["zo"]))
        return f"{q['zq']} {opts}。"
    opts = ". ".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(q["o"]))
    return f"{q['q']} {opts}."


def synth(qid: str, lang: str, text: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "q.txt").write_text(text, encoding="utf-8")
        subprocess.run([str(TOOL), VOICE[lang], RATE[lang], str(tmp / "q.txt"), str(tmp / "q.wav"), str(tmp / "q.json")],
                       check=True, capture_output=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000",
                        str(tmp / "q.wav"), str(OUT / lang / f"{qid}.m4a")],
                       check=True, capture_output=True)
    return qid


def main():
    for lang in ("en", "zh"):
        (OUT / lang).mkdir(parents=True, exist_ok=True)
    # clips used to live flat in html/audio/quiz/ (English only)
    for old in OUT.glob("*.m4a"):
        old.rename(OUT / "en" / old.name)

    hpath = OUT / "hashes.json"
    hashes = json.loads(hpath.read_text()) if hpath.exists() else {}
    todo = []
    for q in load_questions():
        for lang in ("en", "zh"):
            t = text_of(q, lang)
            hk = f"{q['id']}:{lang}"
            h = hashlib.md5((VOICE[lang] + RATE[lang] + t).encode()).hexdigest()
            if hashes.get(hk) == h and (OUT / lang / f"{q['id']}.m4a").exists():
                continue
            todo.append((q["id"], lang, t, h))
    print(f"{len(todo)} clips to narrate", flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(synth, qid, lang, t): (f"{qid}:{lang}", h) for qid, lang, t, h in todo}
        for i, f in enumerate(as_completed(futs), 1):
            hk, h = futs[f]
            try:
                f.result(); hashes[hk] = h
            except Exception as e:
                print("  FAILED", hk, e, flush=True)
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}", flush=True)
    hpath.write_text(json.dumps(hashes))
    files = [p for lang in ("en", "zh") for p in (OUT / lang).glob("*.m4a")]
    print(f"done: {len(files)} files, {sum(p.stat().st_size for p in files)/1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
