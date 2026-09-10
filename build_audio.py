"""Generate paragraph narration audio from aligned/*.json using macOS premium voices.

Each paragraph is synthesized in ONE pass (natural prosody) through
tools/tts_align (AVSpeechSynthesizer), which also reports when each word
starts. Sentence start/end times are derived from those word marks, so the
reader page can highlight the sentence being spoken.

Output:
  html/audio/<num>/<lang>/p<idx>.m4a
  html/audio/<num>/timings.json   {lang: [[ [start,end], ... ] per paragraph], "hash": {...}}

Run: python3 build_audio.py            # all chapters in aligned/
     python3 build_audio.py 04         # one chapter
"""

from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
ALIGNED = ROOT / "aligned"
OUT = ROOT / "html" / "audio"
TOOL_SRC = ROOT / "tools" / "tts_align.swift"
TOOL_BIN = ROOT / "tools" / "tts_align"

VOICE = {
    "en": "com.apple.voice.premium.en-US.Ava",
    "zh": "com.apple.voice.premium.zh-TW.Meijia",
}
# AVSpeechUtterance rate; 0.5 is the system default.
RATE = {"en": 0.5, "zh": 0.5}
JOIN = {"en": " ", "zh": ""}
AAC_BITRATE = "64000"


def ensure_tool() -> None:
    if TOOL_BIN.exists() and TOOL_BIN.stat().st_mtime >= TOOL_SRC.stat().st_mtime:
        return
    print("compiling tools/tts_align ...")
    subprocess.run(["swiftc", "-O", "-o", str(TOOL_BIN), str(TOOL_SRC)], check=True)


def utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def synth_paragraph(sentences: list[str], lang: str, m4a: Path, tmp: Path) -> list[list[float]]:
    text = JOIN[lang].join(sentences)
    txt = tmp / "in.txt"
    wav = tmp / "out.wav"
    js = tmp / "out.json"
    txt.write_text(text, encoding="utf-8")
    subprocess.run(
        [str(TOOL_BIN), VOICE[lang], str(RATE[lang]), str(txt), str(wav), str(js)],
        check=True, capture_output=True,
    )
    info = json.loads(js.read_text(encoding="utf-8"))
    marks = sorted(info["marks"], key=lambda m: m["loc"])
    duration = float(info["duration"])

    # sentence start offsets in UTF-16 units (what AVSpeech reports)
    offsets = []
    pos = 0
    for i, s in enumerate(sentences):
        offsets.append(pos)
        pos += utf16_len(s) + (utf16_len(JOIN[lang]) if i < len(sentences) - 1 else 0)

    starts = []
    for off in offsets:
        t = next((m["t"] for m in marks if m["loc"] >= off), None)
        if t is None:
            t = starts[-1] if starts else 0.0
        starts.append(float(t))
    starts[0] = 0.0
    timings = []
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else duration
        timings.append([round(st, 3), round(en, 3)])

    subprocess.run(
        ["afconvert", "-f", "m4af", "-d", "aac", "-b", AAC_BITRATE, str(wav), str(m4a)],
        check=True, capture_output=True,
    )
    return timings


def para_hash(lang: str, sentences: list[str]) -> str:
    h = hashlib.md5()
    h.update(f"{VOICE[lang]}|{RATE[lang]}|whole".encode())
    for s in sentences:
        h.update(b"\x00" + s.encode("utf-8"))
    return h.hexdigest()


def build_chapter(json_path: Path) -> None:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    num = data["num"]
    chap_out = OUT / num
    timings_path = chap_out / "timings.json"
    old = json.loads(timings_path.read_text(encoding="utf-8")) if timings_path.exists() else {}
    old_hash = old.get("hash", {})

    paras = [p for sec in data["sections"] for p in sec["paras"]]
    result = {"en": [], "zh": [], "hash": {}}
    made = skipped = 0

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for lang in ("en", "zh"):
            (chap_out / lang).mkdir(parents=True, exist_ok=True)
            for pi, para in enumerate(paras):
                sentences = [pair[lang] for pair in para]
                key = f"{lang}/p{pi}"
                h = para_hash(lang, sentences)
                m4a = chap_out / lang / f"p{pi}.m4a"
                if m4a.exists() and old_hash.get(key) == h and len(old.get(lang, [])) > pi:
                    result[lang].append(old[lang][pi])
                    result["hash"][key] = h
                    skipped += 1
                    continue
                t = synth_paragraph(sentences, lang, m4a, tmp)
                result[lang].append(t)
                result["hash"][key] = h
                made += 1
                print(f"  {key}: {len(sentences)} sentences, {t[-1][1]:.1f}s")

    timings_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    total_en = sum(t[-1][1] for t in result["en"]) / 60
    total_zh = sum(t[-1][1] for t in result["zh"]) / 60
    print(f"Chapter {num}: {len(paras)} paragraphs, made {made}, reused {skipped}; "
          f"EN {total_en:.1f} min, ZH {total_zh:.1f} min")


def main():
    ensure_tool()
    targets = sys.argv[1:]
    files = sorted(ALIGNED.glob("*.json"))
    if targets:
        files = [f for f in files if f.name[:2] in targets]
    for f in files:
        print(f"== {f.name}")
        build_chapter(f)


if __name__ == "__main__":
    main()
