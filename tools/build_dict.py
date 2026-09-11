"""Build html/dict/words.json: every English surface form used in aligned/*.json
-> {p: IPA, t: Traditional-Chinese gloss, x: matched headword}.

Source: ECDICT (skywind3000/ECDICT, ecdict.csv). Simplified -> Traditional via OpenCC.
Run: python3 tools/build_dict.py /path/to/ecdict.csv
"""

from __future__ import annotations
import csv
import json
import re
import sys
from pathlib import Path

import opencc

ROOT = Path(__file__).resolve().parent.parent
ALIGNED = ROOT / "aligned"
OUT = ROOT / "html" / "dict"
WORD_RE = re.compile(r"[^\W\d_](?:[^\W\d_'’\-]|['’\-](?=[^\W\d_]))*")

cc = opencc.OpenCC("s2twp")


def surface_forms() -> set[str]:
    forms = set()
    for f in ALIGNED.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for s in d["sections"]:
            for p in s["paras"]:
                for pair in p:
                    for w in WORD_RE.findall(pair["en"]):
                        forms.add(w.replace("’", "'"))
    return forms


def candidates(w: str) -> list[str]:
    """Lookup keys to try, most specific first."""
    lw = w.lower()
    out = [w, lw, lw.replace("'", "’")]
    if lw.endswith("'s"):
        out.append(lw[:-2])
    for suf, rep in (("ies", "y"), ("es", ""), ("s", ""), ("ied", "y"), ("ed", ""), ("ed", "e"),
                     ("ing", ""), ("ing", "e"), ("er", ""), ("est", ""), ("ly", "")):
        if lw.endswith(suf) and len(lw) > len(suf) + 2:
            out.append(lw[: -len(suf)] + rep)
    # doubled consonant: running -> run, stopped -> stop
    m = re.match(r"^(.*?)([bdglmnprt])\2(ing|ed)$", lw)
    if m:
        out.append(m.group(1) + m.group(2))
    return list(dict.fromkeys(out))


def clean_translation(t: str) -> str:
    if not t:
        return ""
    lines = [ln.strip() for ln in t.replace("\\n", "\n").split("\n") if ln.strip()]
    lines = [ln for ln in lines if not ln.startswith("[网络]")]
    return cc.convert("\n".join(lines[:4]))


def main():
    csv_path = Path(sys.argv[1])
    forms = surface_forms()
    need = {}
    for w in forms:
        for c in candidates(w):
            need.setdefault(c, set()).add(w)

    hits: dict[str, dict] = {}
    csv.field_size_limit(1 << 24)
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            k = row["word"]
            if k in need or k.lower() in need:
                hits[k] = row
                hits.setdefault(k.lower(), row)

    overrides = json.loads((ROOT / "tools" / "dict_overrides.json").read_text(encoding="utf-8"))
    ov_lower = {k.lower(): v for k, v in overrides.items()}

    def lookup(w: str):
        for c in candidates(w):
            row = hits.get(c) or hits.get(c.lower())
            if row and row.get("translation"):
                return {
                    "p": row.get("phonetic", ""),
                    "t": clean_translation(row.get("translation", "")),
                    "x": row["word"] if row["word"].lower() != w.lower() else "",
                }
        return None

    result = {}
    missing = []
    for w in sorted(forms):
        ov = overrides.get(w) or ov_lower.get(w.lower()) or (ov_lower.get(w.lower()[:-2]) if w.lower().endswith("'s") else None)
        entry = lookup(w)
        if ov:
            entry = {"p": ov.get("p") or (entry or {}).get("p", ""), "t": ov["t"], "x": ""}
        elif not entry and "-" in w:
            parts = [lookup(p) for p in w.split("-")]
            if all(parts):
                entry = {"p": "", "t": " ＋ ".join(f"{p}: {e['t'].splitlines()[0]}" for p, e in zip(w.split("-"), parts)), "x": ""}
        if not entry:
            missing.append(w)
            continue
        result[w] = entry

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "words.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "words.js").write_text("window.CIT_DICT=" + json.dumps(result, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    (OUT / "missing.txt").write_text("\n".join(missing), encoding="utf-8")
    print(f"forms {len(forms)}, matched {len(result)}, missing {len(missing)} -> {OUT/'words.json'} "
          f"({(OUT/'words.json').stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
