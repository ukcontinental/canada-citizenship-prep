"""Per-line narration for the interactive memory modules.

Every 🔊 button on an interactive page names a clip by sha1 of its own text
(word_dict.audio_key). interactive_content records those calls in BI_SEEN while
the pages are generated, so this script synthesizes exactly the lines the pages
ask for — there is no second list to keep in sync.

Whole line at a time, same as build_audio.py: splitting a line into sentences and
concatenating is what made the first narration sound robotic.

Also covers the Day 01-14 pages, which use the same bi() pairs.

Output: html/audio/iv/{en,zh}/<key>.m4a   (existing files are skipped)
Run:    python3 tools/build_interactive_audio.py [--prune]
"""

from __future__ import annotations
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import interactive_content as iv  # noqa: E402

OUT = ROOT / "html" / "audio" / "iv"
TOOL = ROOT / "tools" / "tts_align"
VOICE = {"en": "com.apple.voice.premium.en-US.Ava",
         "zh": "com.apple.voice.premium.zh-TW.Meijia"}
RATE = {"en": "0.47", "zh": "0.5"}
WORKERS = 3

MODULES = ["geography", "history", "modern", "government",
           "elections", "justice", "symbols", "economy"]


def collect() -> dict[str, tuple[str, str]]:
    """Render everything that uses iv.bi() so BI_SEEN holds exactly the lines the
    pages will ask for — the interactive modules and the Day 01-14 pages."""
    iv.BI_SEEN.clear()
    for name in MODULES:
        getattr(iv, f"build_{name}_body")()
    import build_html as bh
    for md_file in sorted((ROOT / "daily-quiz").glob("*.md")):
        bh.render_daily_quiz(md_file)
    return dict(iv.BI_SEEN)


def synth(key: str, lang: str, text: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        txt, wav, js = tmp / "t.txt", tmp / "t.wav", tmp / "t.json"
        txt.write_text(text, encoding="utf-8")
        subprocess.run([str(TOOL), VOICE[lang], RATE[lang], str(txt), str(wav), str(js)],
                       check=True, capture_output=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000",
                        str(wav), str(OUT / lang / f"{key}.m4a")],
                       check=True, capture_output=True)
    return key


def main():
    for lang in ("en", "zh"):
        (OUT / lang).mkdir(parents=True, exist_ok=True)
    lines = collect()
    todo = [(k, l, t) for k, (l, t) in lines.items() if not (OUT / l / f"{k}.m4a").exists()]
    print(f"{len(lines)} lines on the pages, {len(todo)} to synthesize", flush=True)

    done = failed = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(synth, k, l, t) for k, l, t in todo]
        for f in as_completed(futs):
            try:
                f.result()
            except Exception as e:
                failed += 1
                print("  FAILED:", e, flush=True)
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(todo)}", flush=True)

    if "--prune" in sys.argv:
        keep = {(l, k) for k, (l, _) in lines.items()}
        gone = 0
        for lang in ("en", "zh"):
            for p in (OUT / lang).glob("*.m4a"):
                if (lang, p.stem) not in keep:
                    p.unlink()
                    gone += 1
        print(f"pruned {gone} stale clips", flush=True)

    n = sum(len(list((OUT / l).glob("*.m4a"))) for l in ("en", "zh"))
    size = sum(p.stat().st_size for l in ("en", "zh") for p in (OUT / l).glob("*.m4a")) / 1e6
    print(f"done: {n} clips, {size:.1f} MB, {failed} failed", flush=True)


if __name__ == "__main__":
    main()
