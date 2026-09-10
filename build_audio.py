"""Generate paragraph narration audio from aligned/*.json using macOS premium voices.

For each paragraph: every sentence is synthesized separately with `say`, the
sentence WAVs are concatenated (with a short gap) so we know each sentence's
start/end time inside the paragraph file, then converted to AAC .m4a.

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
import wave
from pathlib import Path

ROOT = Path(__file__).parent
ALIGNED = ROOT / "aligned"
OUT = ROOT / "html" / "audio"

VOICE = {"en": "Ava (Premium)", "zh": "Meijia (Premium)"}
GAP_MS = {"en": 380, "zh": 320}
RATE = 22050
AAC_BITRATE = "64000"


def say_to_wav(text: str, lang: str, wav_path: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write(text)
        txt = tf.name
    # NOTE: premium voices reject the -r rate flag; keep default rate.
    subprocess.run(
        ["say", "-v", VOICE[lang], "-f", txt, "-o", str(wav_path), f"--data-format=LEI16@{RATE}"],
        check=True,
    )
    Path(txt).unlink(missing_ok=True)


def concat_wavs(parts: list[Path], gap_ms: int, out_wav: Path) -> list[list[float]]:
    """Concatenate mono 16-bit WAVs; return [[start,end],...] seconds per part."""
    timings = []
    with wave.open(str(out_wav), "wb") as w:
        params_set = False
        pos_frames = 0
        gap_frames = int(RATE * gap_ms / 1000)
        for i, p in enumerate(parts):
            with wave.open(str(p), "rb") as r:
                if not params_set:
                    w.setnchannels(r.getnchannels())
                    w.setsampwidth(r.getsampwidth())
                    w.setframerate(r.getframerate())
                    params_set = True
                    sw = r.getsampwidth() * r.getnchannels()
                frames = r.readframes(r.getnframes())
                n = r.getnframes()
            start = pos_frames / RATE
            w.writeframes(frames)
            pos_frames += n
            end = pos_frames / RATE
            timings.append([round(start, 3), round(end, 3)])
            if i < len(parts) - 1:
                w.writeframes(b"\x00" * (gap_frames * sw))
                pos_frames += gap_frames
    return timings


def wav_to_m4a(wav_path: Path, m4a_path: Path) -> None:
    subprocess.run(
        ["afconvert", "-f", "m4af", "-d", "aac", "-b", AAC_BITRATE, str(wav_path), str(m4a_path)],
        check=True,
        capture_output=True,
    )


def para_hash(lang: str, sentences: list[str]) -> str:
    h = hashlib.md5()
    h.update(VOICE[lang].encode())
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
        tdp = Path(td)
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
                parts = []
                for si, s in enumerate(sentences):
                    wp = tdp / f"{lang}_{pi}_{si}.wav"
                    say_to_wav(s, lang, wp)
                    parts.append(wp)
                merged = tdp / f"{lang}_{pi}.wav"
                t = concat_wavs(parts, GAP_MS[lang], merged)
                wav_to_m4a(merged, m4a)
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
    targets = sys.argv[1:]
    files = sorted(ALIGNED.glob("*.json"))
    if targets:
        files = [f for f in files if f.name[:2] in targets]
    for f in files:
        print(f"== {f.name}")
        build_chapter(f)


if __name__ == "__main__":
    main()
