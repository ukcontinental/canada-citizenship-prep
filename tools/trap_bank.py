"""陷阱題題庫：data/trap-questions.js → 站內格式。

來源檔是 JS 物件字面量（單引號、鍵不加引號），不是 JSON，所以這裡自己寫一個
小型解析器，不動原檔——原檔保持 ChatGPT 給的樣子，方便日後對照。

做的事：
  1. 解析 Q1/Q2 兩個陣列 → list[dict]
  2. 稽核：欄位齊全、a 在選項範圍內、是非題 f=1、題目不重複
  3. 中文地名／人名改成站上既有的台灣寫法（新布藍瑞克、薩克其萬、蒙特婁…）
  4. 「每章輪流分配」拆成 N 套，題號固定（A01…、B01…），只要原檔順序不變就不會變
  5. 章節代碼 rights/people/… 對到站上的章號 02/03/…

用法：
  python3 tools/trap_bank.py            # 印稽核報告
  from tools.trap_bank import load_trap_bank
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "trap-questions.js"

N_SETS = 3
SET_LETTERS = "ABCDEF"

# 章節代碼 → 站上章號（對應 reading/ 與 CHAPTER_NAMES）
CH_MAP = {"rights": "02", "people": "03", "history": "04", "modern": "05",
          "gov": "06", "vote": "07", "justice": "08", "symbols": "09",
          "economy": "10", "regions": "11"}
CH_ORDER = list(CH_MAP)

TYPE_NAMES = {"N": "否定題 NOT / EXCEPT", "R": "反問題", "S": "換字題", "T": "是非題",
              "W": "找正確句 TRUE / FALSE", "C": "情境題", "F": "最／第一"}

# 站上既有的台灣寫法；來源檔混用港／陸譯名
ZH_FIX = [
    ("新布倫瑞克省（紐賓士域）", "新布藍瑞克"), ("新布倫瑞克", "新布藍瑞克"),
    ("薩斯喀徹溫", "薩克其萬"), ("蒙特利爾", "蒙特婁"), ("新斯科舍", "新斯科細亞"),
    ("努納武特", "努納福特"), ("伊卡盧伊特", "伊魁特"), ("卑詩", "卑詩省"), ("卑詩省省", "卑詩省"),
    ("約翰·卡博特", "約翰・卡伯特"), ("雅克·卡蒂埃", "雅克・卡蒂亞"), ("卡蒂埃爵士", "卡蒂埃爵士"),
    ("拉方丹", "拉封丹"), ("麥克菲爾", "麥克費爾"), ("席科德", "塞科德"), ("德罕勳爵", "德倫勳爵"),
    ("勞雷爾", "勞里埃"), ("皮埃爾·德蒙", "皮耶・德蒙"), ("詹姆斯·沃爾夫", "詹姆斯・沃夫"),
    ("梅蒂人", "梅蒂斯人"), ("袋棍球", "長曲棍球"), ("加式足球", "加拿大式足球"),
    ("國殤紀念日", "陣亡將士紀念日"), ("國殤日", "陣亡將士紀念日"),
    ("·", "・"),
]


# ---------------------------------------------------------------- JS 字面量解析
class _P:
    def __init__(self, s: str):
        self.s, self.i = s, 0

    def ws(self):
        while self.i < len(self.s):
            c = self.s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif self.s.startswith("//", self.i):
                self.i = self.s.find("\n", self.i)
                if self.i < 0:
                    self.i = len(self.s)
            else:
                break

    def val(self):
        self.ws()
        c = self.s[self.i]
        if c == "[":
            return self.arr()
        if c == "{":
            return self.obj()
        if c in "'\"":
            return self.string()
        m = re.match(r"-?\d+(\.\d+)?", self.s[self.i:])
        if m:
            self.i += m.end()
            return float(m.group()) if "." in m.group() else int(m.group())
        for lit, v in (("true", True), ("false", False), ("null", None)):
            if self.s.startswith(lit, self.i):
                self.i += len(lit)
                return v
        raise SyntaxError(f"unexpected {self.s[self.i:self.i+30]!r} at {self.i}")

    def string(self):
        q = self.s[self.i]
        self.i += 1
        out = []
        while True:
            c = self.s[self.i]
            if c == "\\":
                n = self.s[self.i + 1]
                out.append({"n": "\n", "t": "\t"}.get(n, n))
                self.i += 2
            elif c == q:
                self.i += 1
                return "".join(out)
            else:
                out.append(c)
                self.i += 1

    def arr(self):
        self.i += 1
        out = []
        while True:
            self.ws()
            if self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.val())
            self.ws()
            if self.s[self.i] == ",":
                self.i += 1

    def obj(self):
        self.i += 1
        out = {}
        while True:
            self.ws()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            m = re.match(r"[A-Za-z_]\w*", self.s[self.i:])
            key = m.group()
            self.i += m.end()
            self.ws()
            assert self.s[self.i] == ":", self.s[self.i:self.i+20]
            self.i += 1
            out[key] = self.val()
            self.ws()
            if self.s[self.i] == ",":
                self.i += 1


def _extract_array(src: str, name: str) -> list:
    m = re.search(rf"const\s+{name}\s*=\s*\[", src)
    p = _P(src)
    p.i = m.end() - 1
    return p.arr()


# ---------------------------------------------------------------- 主流程
def fix_zh(s: str) -> str:
    for a, b in ZH_FIX:
        s = s.replace(a, b)
    return s


def load_trap_bank(n_sets: int = N_SETS) -> list[dict]:
    src = SRC.read_text(encoding="utf-8")
    raw = _extract_array(src, "Q1") + _extract_array(src, "Q2")
    problems = []
    seen = set()
    qs = []
    for i, r in enumerate(raw):
        q = {
            "c": r["c"], "ch": CH_MAP.get(r["c"]), "t": r["t"],
            "q": r["q"], "zq": fix_zh(r["z"]),
            "o": [o[0] for o in r["o"]], "zo": [fix_zh(o[1]) for o in r["o"]],
            "a": int(r.get("a", 0)), "f": int(r.get("f", 0)),
            "e": fix_zh(r["e"]), "k": [[k[0], fix_zh(k[1])] for k in r.get("k", [])],
            "src_index": i,
        }
        # 「否定題」必須真的有 NOT / EXCEPT，否則按換字題處理（來源有一題標錯）
        if q["t"] == "N" and not re.search(r"\b(NOT|EXCEPT)\b", q["q"]):
            q["t"] = "S"
        if q["ch"] is None:
            problems.append(f"#{i} 未知章節 {r['c']}")
        if not (0 <= q["a"] < len(q["o"])):
            problems.append(f"#{i} 答案索引 {q['a']} 超出 {len(q['o'])} 個選項")
        if q["t"] == "T" and q["f"] != 1:
            problems.append(f"#{i} 是非題沒標 f=1")
        if len(q["o"]) < 2:
            problems.append(f"#{i} 選項不足")
        key = re.sub(r"\W+", " ", q["q"].lower()).strip()
        if key in seen:
            problems.append(f"#{i} 題目重複：{q['q'][:50]}")
        seen.add(key)
        qs.append(q)
    if problems:
        raise SystemExit("陷阱題稽核失敗：\n  " + "\n  ".join(problems))

    # 每章輪流分配到 N 套；每章從不同套起手，套與套題數才會平均
    buckets: dict[str, list[dict]] = {L: [] for L in SET_LETTERS[:n_sets]}
    for ci, c in enumerate(CH_ORDER):
        chapter_qs = [q for q in qs if q["c"] == c]
        for j, q in enumerate(chapter_qs):
            L = SET_LETTERS[(ci + j) % n_sets]
            buckets[L].append(q)
    out = []
    for L, items in buckets.items():
        for n, q in enumerate(items, 1):
            q["set"] = L
            q["id"] = f"{L}{n:02d}"
            out.append(q)
    return out


def bank_js(qs: list[dict]) -> str:
    slim = [{k: q[k] for k in ("id", "set", "ch", "t", "q", "zq", "o", "zo", "a", "f", "e", "k")} for q in qs]
    return "window.CIT_TRAP=" + json.dumps(slim, ensure_ascii=False, separators=(",", ":")) + ";"


if __name__ == "__main__":
    qs = load_trap_bank()
    from collections import Counter
    print(f"共 {len(qs)} 題，{N_SETS} 套")
    for L in SET_LETTERS[:N_SETS]:
        s = [q for q in qs if q["set"] == L]
        chs = Counter(q["ch"] for q in s)
        types = Counter(q["t"] for q in s)
        print(f"  第 {L} 套 {len(s):3d} 題 | 章節 " + " ".join(f"{c}×{n}" for c, n in sorted(chs.items()))
              + " | 類型 " + " ".join(f"{t}{n}" for t, n in sorted(types.items())))
    print("類型總計：", dict(sorted(Counter(q["t"] for q in qs).items())))
    left = [q["zq"][:40] for q in qs if re.search(r"新布倫瑞克|薩斯喀徹溫|蒙特利爾|新斯科舍|努納武特", q["zq"] + q["e"] + "".join(q["zo"]))]
    print("殘留非台灣譯名：", left or "無")
