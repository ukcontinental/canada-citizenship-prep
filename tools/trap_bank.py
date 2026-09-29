"""陷阱題題庫：data/trap-questions*.js → 站內格式。

來源檔是 JS 物件字面量（單引號、鍵不加引號），不是 JSON，所以這裡自己寫一個
小型解析器，不動原檔——原檔保持給的樣子，方便日後對照。

兩批來源，分開處理但共用同一套稽核／分套邏輯：
  data/trap-questions.js       — 第一批 134 題（Q1+Q2），**題號釘死在 A/B/C**，
                                  這批絕對不重新分配，換頁重刷題號也不會變。
  data/trap-questions-more.js  — 追加批（QM1+QM2+QM3），分進 D/E 兩套；
                                  之後再加新內容就繼續往 F、G… 疊，不動前面的字母。

做的事：
  1. 解析每批來源 → list[dict]
  2. 稽核：欄位齊全、a 在選項範圍內、是非題 f=1、題目不重複（跨批一起查重）
  3. 中文地名／人名改成站上既有的台灣寫法（新布藍瑞克、薩克其萬、蒙特婁…）
  4. 「每章輪流分配」拆成每批各自的套數，題號固定；只要來源檔順序不變就不會變
  5. 章節代碼 rights/people/… 對到站上的章號 02/03/…（含 00/01/12 三個原本缺的章）

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
SRC_MORE = ROOT / "data" / "trap-questions-more.js"

SET_LETTERS = "ABCDEFGHIJ"

# 章節代碼 → 站上章號（對應 reading/ 與 CHAPTER_NAMES）
CH_MAP = {"rights": "02", "people": "03", "history": "04", "modern": "05",
          "gov": "06", "vote": "07", "justice": "08", "symbols": "09",
          "economy": "10", "regions": "11", "oath": "00", "apply": "01", "ontario": "12"}

# 分套用的「每章輪流」順序。CH_ORDER_BASE 是原始 134 題的十個章節，**永遠不准改動
# 順序或增減**——A/B/C 的題號是照這個順序算出來的，動了這行等於讓題號全部重排。
# 新章節（oath/apply/ontario）只接在後面給追加批（D/E…）用，不影響 A/B/C。
CH_ORDER_BASE = ["rights", "people", "history", "modern", "gov", "vote",
                 "justice", "symbols", "economy", "regions"]
CH_ORDER_ALL = CH_ORDER_BASE + ["oath", "apply", "ontario"]

TYPE_NAMES = {"N": "否定題 NOT / EXCEPT", "R": "反問題", "S": "換字題", "T": "是非題",
              "W": "找正確句 TRUE / FALSE", "C": "情境題", "F": "最／第一"}

SET_NAMES = {"A": "第一套", "B": "第二套", "C": "第三套", "D": "第四套", "E": "第五套",
             "F": "第六套", "G": "第七套", "H": "第八套"}

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


def _normalize(raw: list[dict], seen: set[str], problems: list[str], tag: str) -> list[dict]:
    """單一來源檔的原始物件 → 站內格式，順便做欄位稽核；seen 跨來源共用才能抓到
    兩批之間互相重複的題目。"""
    qs = []
    for i, r in enumerate(raw):
        q = {
            "c": r["c"], "ch": CH_MAP.get(r["c"]), "t": r["t"],
            "q": r["q"], "zq": fix_zh(r["z"]),
            "o": [o[0] for o in r["o"]], "zo": [fix_zh(o[1]) for o in r["o"]],
            "a": int(r.get("a", 0)), "f": int(r.get("f", 0)),
            "e": fix_zh(r["e"]), "k": [[k[0], fix_zh(k[1])] for k in r.get("k", [])],
        }
        # 「否定題」必須真的有 NOT / EXCEPT，否則按換字題處理
        if q["t"] == "N" and not re.search(r"\b(NOT|EXCEPT)\b", q["q"]):
            q["t"] = "S"
        loc = f"{tag}#{i}"
        if q["ch"] is None:
            problems.append(f"{loc} 未知章節 {r['c']}")
        if not (0 <= q["a"] < len(q["o"])):
            problems.append(f"{loc} 答案索引 {q['a']} 超出 {len(q['o'])} 個選項")
        if q["t"] == "T" and q["f"] != 1:
            problems.append(f"{loc} 是非題沒標 f=1")
        if len(q["o"]) < 2:
            problems.append(f"{loc} 選項不足")
        key = re.sub(r"\W+", " ", q["q"].lower()).strip()
        if key in seen:
            problems.append(f"{loc} 題目重複：{q['q'][:50]}")
        seen.add(key)
        qs.append(q)
    return qs


def _assign_sets(qs: list[dict], letters: str, order: list[str]) -> list[dict]:
    """每章輪流分配到 letters 指定的幾套；每章從不同套起手，套與套題數才會平均。"""
    buckets: dict[str, list[dict]] = {L: [] for L in letters}
    for ci, c in enumerate(order):
        chapter_qs = [q for q in qs if q["c"] == c]
        for j, q in enumerate(chapter_qs):
            L = letters[(ci + j) % len(letters)]
            buckets[L].append(q)
    out = []
    for L, items in buckets.items():
        for n, q in enumerate(items, 1):
            q["set"] = L
            q["id"] = f"{L}{n:02d}"
            out.append(q)
    return out


def load_trap_bank() -> list[dict]:
    problems: list[str] = []
    seen: set[str] = set()

    base_src = SRC.read_text(encoding="utf-8")
    base_raw = _extract_array(base_src, "Q1") + _extract_array(base_src, "Q2")
    base_qs = _normalize(base_raw, seen, problems, "base")
    # 第一批釘死在 A/B/C —— 這裡的字母與數量永遠不變
    base_assigned = _assign_sets(base_qs, "ABC", CH_ORDER_BASE)

    more_qs: list[dict] = []
    if SRC_MORE.exists():
        more_src = SRC_MORE.read_text(encoding="utf-8")
        more_raw = []
        for name in re.findall(r"const\s+(QM\d+)\s*=", more_src):
            more_raw += _extract_array(more_src, name)
        more_qs = _normalize(more_raw, seen, problems, "more")

    if problems:
        raise SystemExit("陷阱題稽核失敗：\n  " + "\n  ".join(problems))

    # 追加批接著往後排字母（目前 D/E），以後再加檔案就繼續往 F、G 疊，
    # 不會動到已經釘死的 A/B/C 或既有的 D/E 題號。
    more_assigned = _assign_sets(more_qs, "DE", CH_ORDER_ALL) if more_qs else []
    return base_assigned + more_assigned


def bank_js(qs: list[dict]) -> str:
    slim = [{k: q[k] for k in ("id", "set", "ch", "t", "q", "zq", "o", "zo", "a", "f", "e", "k")} for q in qs]
    return "window.CIT_TRAP=" + json.dumps(slim, ensure_ascii=False, separators=(",", ":")) + ";"


if __name__ == "__main__":
    qs = load_trap_bank()
    from collections import Counter
    sets_present = sorted({q["set"] for q in qs})
    print(f"共 {len(qs)} 題，{len(sets_present)} 套：{sets_present}")
    for L in sets_present:
        s = [q for q in qs if q["set"] == L]
        chs = Counter(q["ch"] for q in s)
        types = Counter(q["t"] for q in s)
        print(f"  第 {L} 套 {len(s):3d} 題 | 章節 " + " ".join(f"{c}×{n}" for c, n in sorted(chs.items()))
              + " | 類型 " + " ".join(f"{t}{n}" for t, n in sorted(types.items())))
    print("類型總計：", dict(sorted(Counter(q["t"] for q in qs).items())))
    left = [q["zq"][:40] for q in qs if re.search(r"新布倫瑞克|薩斯喀徹溫|蒙特利爾|新斯科舍|努納武特", q["zq"] + q["e"] + "".join(q["zo"]))]
    print("殘留非台灣譯名：", left or "無")
    missing_ch = [q["c"] for q in qs if q["ch"] is None]
    print("章節對不到的：", missing_ch or "無")
