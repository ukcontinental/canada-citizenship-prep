"""Measure trailing silence in narration clips — the regression test for the tail bug.

AVSpeechSynthesizer.write() used to cut the last word's audio short (see
tools/tts_align.swift). The objective symptom is trailing silence: a clip that
finished speaking naturally keeps roughly 0.23-0.36 s of quiet at the end, while a
truncated one has only 0.03-0.09 s. Anything at or under 0.12 s is suspect.

Run:  python3 tools/check_tails.py html/audio/iv/en          # whole folder
      python3 tools/check_tails.py html/audio/iv/en --n 40    # random sample
"""

from __future__ import annotations
import random
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

SUSPECT = 0.12          # seconds of trailing silence at or below which a clip looks cut
FLOOR = 0.006           # amplitude (0-1) below which a sample counts as silence


def trailing_silence(m4a: Path) -> float | None:
    """Seconds of near-silence at the end of the clip, or None if it cannot be read."""
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "t.wav"
        r = subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(m4a), str(wav)],
                           capture_output=True)
        if r.returncode != 0 or not wav.exists():
            return None
        with wave.open(str(wav), "rb") as w:
            n, ch, sw, rate = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
            if sw != 2 or n == 0:
                return None
            raw = w.readframes(n)
    limit = int(FLOOR * 32768)
    step = 2 * ch
    quiet = 0
    for i in range(len(raw) - step, -1, -step):
        s = int.from_bytes(raw[i:i + 2], "little", signed=True)
        if abs(s) > limit:
            break
        quiet += 1
    return quiet / rate


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    folder = Path(args[0])
    files = sorted(folder.glob("*.m4a"))
    if not files:
        sys.exit(f"no .m4a under {folder}")
    if "--n" in sys.argv:
        k = int(sys.argv[sys.argv.index("--n") + 1])
        files = random.sample(files, min(k, len(files)))

    vals, unreadable, suspect = [], [], []
    for f in files:
        t = trailing_silence(f)
        if t is None:
            unreadable.append(f.name)
            continue
        vals.append(t)
        if t <= SUSPECT:
            suspect.append((t, f.name))

    vals.sort()
    if vals:
        print(f"{len(vals)} clips measured  min {vals[0]:.3f}s  "
              f"median {vals[len(vals) // 2]:.3f}s  max {vals[-1]:.3f}s")
    if unreadable:
        print(f"unreadable: {len(unreadable)}  e.g. {unreadable[:3]}")
    print(f"suspect (<= {SUSPECT}s trailing silence): {len(suspect)}")
    for t, name in sorted(suspect)[:20]:
        print(f"  {t:.3f}s  {name}")
    sys.exit(1 if suspect else 0)


if __name__ == "__main__":
    main()
