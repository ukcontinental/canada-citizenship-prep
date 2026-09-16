"""One listenable audio file per chapter from the 328-question bank.

Per question: English question + options (Ava) → 1s pause → English answer
line (Ava) → Chinese answer line (Meijia) → 1.2s gap. Chapters are written
as m4a with chapter titles spoken at the start.

Output: <out_dir>/公民考試題庫_NN_<chapter>.m4a  (default: the iCloud folder)
Run: python3 tools/build_quiz_podcast.py [out_dir]
"""

from __future__ import annotations
import array
import subprocess
import sys
import tempfile
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from quiz_content import load_questions, CHAPTER_NAMES  # noqa: E402

TOOL = ROOT / "tools" / "tts_align"
EN_VOICE = "com.apple.voice.premium.en-US.Ava"
ZH_VOICE = "com.apple.voice.premium.zh-TW.Meijia"
EN_RATE, ZH_RATE = "0.47", "0.5"
SR = 22050
LETTERS = "ABCDE"
DEFAULT_OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/加拿大公民考試/題庫朗讀"


def say(text: str, lang: str, wav: Path) -> Path:
    voice, rate = (EN_VOICE, EN_RATE) if lang == "en" else (ZH_VOICE, ZH_RATE)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        txt = f.name
    subprocess.run([str(TOOL), voice, rate, txt, str(wav), str(wav.with_suffix(".json"))],
                   check=True, capture_output=True)
    Path(txt).unlink(missing_ok=True)
    return wav


def read_frames(wav: Path) -> bytes:
    with wave.open(str(wav), "rb") as r:
        assert r.getframerate() == SR and r.getsampwidth() == 2 and r.getnchannels() == 1, wav
        return r.readframes(r.getnframes())


def silence(ms: int) -> bytes:
    return array.array("h", [0] * int(SR * ms / 1000)).tobytes()


def build_chapter(ch: str, questions: list[dict], out_dir: Path, tmp: Path) -> Path:
    name = CHAPTER_NAMES.get(ch, "")
    pieces: list[bytes] = []
    jobs = []
    for i, q in enumerate(questions):
        opts = ". ".join(f"{LETTERS[k]}. {o}" for k, o in enumerate(q["o"]))
        ans = f"The answer is {LETTERS[q['a']]}. {q['o'][q['a']]}. {q['e']}"
        zh = f"答案 {LETTERS[q['a']]}。{q['ze']}"
        jobs += [(f"{i}_q", f"Question {i + 1}. {q['q']} {opts}.", "en"),
                 (f"{i}_a", ans, "en"),
                 (f"{i}_z", zh, "zh")]
    jobs.insert(0, ("intro_en", f"Chapter {ch}. {len(questions)} questions.", "en"))
    jobs.insert(1, ("intro_zh", f"第 {ch} 章，{name}，共 {len(questions)} 題。", "zh"))

    def run(job):
        key, text, lang = job
        say(text, lang, tmp / f"{ch}_{key}.wav")
        return key

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(run, jobs))

    pieces.append(read_frames(tmp / f"{ch}_intro_en.wav"))
    pieces.append(read_frames(tmp / f"{ch}_intro_zh.wav"))
    pieces.append(silence(1200))
    for i in range(len(questions)):
        pieces.append(read_frames(tmp / f"{ch}_{i}_q.wav"))
        pieces.append(silence(1000))          # think
        pieces.append(read_frames(tmp / f"{ch}_{i}_a.wav"))
        pieces.append(silence(300))
        pieces.append(read_frames(tmp / f"{ch}_{i}_z.wav"))
        pieces.append(silence(1200))          # before next question

    merged = tmp / f"chapter_{ch}.wav"
    with wave.open(str(merged), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for p in pieces:
            w.writeframes(p)

    out_dir.mkdir(parents=True, exist_ok=True)
    safe = name.replace("/", "-")
    m4a = out_dir / f"公民考試題庫_{ch}_{safe}.m4a"
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(merged), str(m4a)],
                   check=True, capture_output=True)
    secs = sum(len(p) for p in pieces) / 2 / SR
    print(f"  ch {ch} {name}: {len(questions)} questions, {secs/60:.1f} min -> {m4a.name}", flush=True)
    return m4a


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    qs = load_questions()
    by_ch: dict[str, list[dict]] = {}
    for q in qs:
        by_ch.setdefault(q["ch"], []).append(q)
    print(f"{len(qs)} questions in {len(by_ch)} chapters -> {out_dir}", flush=True)
    total = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for ch in sorted(by_ch):
            m = build_chapter(ch, by_ch[ch], out_dir, tmp)
            total += m.stat().st_size
            for f in tmp.glob(f"{ch}_*"):
                f.unlink()
            (tmp / f"chapter_{ch}.wav").unlink(missing_ok=True)
    print(f"done: {total/1e6:.0f} MB in {out_dir}", flush=True)


if __name__ == "__main__":
    main()
