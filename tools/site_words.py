"""Every English word the site makes tappable — one list, used by both
tools/build_dict.py (definitions) and tools/build_word_audio.py (pronunciation).

Reading pages come from aligned/*.json. Every other page (interactive modules,
quiz, Day 01-14) is asked to render itself and the <span class="w"> spans are
read back out, so the word list is by construction exactly what a reader can tap
— no separate list to drift out of sync.
"""

from __future__ import annotations
import html as _html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import word_dict as wd  # noqa: E402

W_SPAN_RE = re.compile(r'<span class="w">([^<]+)</span>')
# JS that *generates* .w spans at runtime would otherwise be read as content
SCRIPT_RE = re.compile(r"<script\b.*?</script>", re.S)


def key(w: str) -> str:
    return w.lower().replace("’", "'")


def _from_aligned() -> dict[str, str]:
    seen: dict[str, str] = {}
    for f in sorted((ROOT / "aligned").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for s in d["sections"]:
            for p in s["paras"]:
                for pair in p:
                    for w in wd.EN_WORD_RE.findall(pair["en"]):
                        seen.setdefault(key(w), w)
    return seen


def _from_rendered() -> dict[str, str]:
    seen: dict[str, str] = {}
    bodies: list[str] = []

    import interactive_content as iv
    for name in ("geography", "history", "modern", "government",
                 "elections", "justice", "symbols", "economy"):
        bodies.append(getattr(iv, f"build_{name}_body")())

    try:
        import quiz_content as qz
        bodies.append(qz.build_practice_body())
        bodies.append(qz.build_mock_body())
    except Exception as e:                      # quiz not wired for tapping yet
        print(f"  (quiz skipped: {e})", file=sys.stderr)

    import build_html as bh
    for md_file in sorted((ROOT / "daily-quiz").glob("*.md")):
        bodies.append(bh.render_daily_quiz(md_file))

    for b in bodies:
        for raw in W_SPAN_RE.findall(SCRIPT_RE.sub("", b)):
            w = _html.unescape(raw)
            seen.setdefault(key(w), w)
    return seen


def all_surface_forms() -> dict[str, str]:
    """key (lowercase, straight apostrophe) -> one surface spelling."""
    seen = _from_aligned()
    for k, w in _from_rendered().items():
        seen.setdefault(k, w)
    return seen


if __name__ == "__main__":
    a = _from_aligned()
    r = _from_rendered()
    new = {k for k in r if k not in a}
    print(f"aligned {len(a)}、其他頁 {len(r)}，其他頁多出的新字 {len(new)}")
    print("  " + ", ".join(sorted(new)[:40]))
