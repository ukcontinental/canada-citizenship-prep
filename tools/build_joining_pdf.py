"""聯邦擴張＋13 首府 隨身表 → A4 直式 PDF（中英對照，3 頁）。

內容與 interactive/joining.html 同源（interactive_data.JOINING），所以改資料
兩邊會一起變。PDF 本身不進 repo —— 跟其他題庫 PDF 一樣放 公民考試資料夾／iCloud。

用法：
    python3 tools/build_joining_pdf.py            # 產出到 /tmp 再自行複製
    bash ~/.claude/skills/magazine-cover-report/scripts/html2pdf.sh sheet.html sheet.pdf

排版注意：表格列一定要 break-inside:avoid，否則年份會跟內文被拆到兩頁。
"""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from interactive_data import JOINING, JOINING_TRICKS
from canada_map import CAPITALS_MAP_SVG
import html as H, re

def split(t):
    return t.split("｜", 1) if "｜" in t else (t, "")

def strong(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", H.escape(t)).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")

def bi(t, cls=""):
    zh, en = split(t)
    return (f'<div class="bi {cls}"><div class="z">{strong(zh)}</div>'
            f'<div class="e">{strong(en)}</div></div>')

rows = ""
for year, tag, members, story, notes in JOINING:
    kinds = {m[5] for m in members}
    kind = "g" if kinds == {"g"} else ("r" if kinds == {"r"} else "p")
    chips = ""
    for num, zh, en, cz, ce, k in members:
        badge = f'<u>{num}</u>' if num else '<u class="x">–</u>'
        chips += (f'<span class="chip c-{k}">{badge}<span class="cb>">'
                  f'<span class="n"><b>{H.escape(zh)}</b> <i>{H.escape(en)}</i></span>'
                  f'<span class="c"><b>{H.escape(cz)}</b> <i>{H.escape(ce)}</i></span>'
                  f'</span></span>')
    notes_html = "".join(bi(n, "sm") for n in notes)
    rows += (f'<tr class="yr-{kind}"><td class="yr">{year}</td><td class="cell">'
             f'{f"<div class=tag>{H.escape(split(tag)[0])} · {H.escape(split(tag)[1])}</div>" if tag else ""}'
             f'<div class="chips">{chips}</div>{bi(story)}{notes_html}</td></tr>')

tricks = ""
for i, (title, lines) in enumerate(JOINING_TRICKS, 1):
    tz, te = split(title)
    tricks += (f'<div class="tk"><div class="tkh"><span class="no">{i}</span>'
               f'<span><b>{strong(tz)}</b><i>{strong(te)}</i></span></div>'
               + "".join(bi(l, "sm") for l in lines) + "</div>")

ref = ""
for year, _t, members, _s, _n in JOINING:
    for num, zh, en, cz, ce, k in members:
        if not num:
            continue
        ref += (f'<tr><td class="n">{num}</td>'
                f'<td>{H.escape(zh)} <i>{H.escape(en)}</i></td>'
                f'<td>{H.escape(cz)} <i>{H.escape(ce)}</i></td>'
                f'<td class="y">{year}</td><td class="k">{"省 Prov." if k=="p" else "地區 Terr."}</td></tr>')

CSS = """
@page { size: A4; margin: 13mm 12mm 12mm; }
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,"PingFang TC","Helvetica Neue",sans-serif;
  color:#1f2328; font-size:9.6pt; line-height:1.5; background:#fff; }
i { font-style:normal; font-family:"Source Serif 4",Georgia,serif; }
h1 { font-size:17pt; margin:0 0 2pt; letter-spacing:.5pt; }
h1 small { font-size:10pt; font-weight:400; color:#5f5e5a; font-family:Georgia,serif; margin-left:6pt; }
.lead { font-size:8.8pt; color:#5f5e5a; margin:0 0 7pt; }
h2 { font-size:12pt; margin:0 0 6pt; padding-bottom:3pt; border-bottom:1.6pt solid #0F6E56; }
.map { width:88%; margin:0 auto 3pt; display:block; }
.key { display:flex; gap:14pt; font-size:8pt; color:#5f5e5a; margin:0 0 9pt; }
.key i { font-style:normal; }
.sw { display:inline-block; width:7pt; height:7pt; border-radius:50%; vertical-align:-0.5pt; margin-right:3pt; }
.sw.p{background:#0F6E56}.sw.r{background:#534AB7}
.st { display:inline-block; width:0;height:0;border-left:4pt solid transparent;border-right:4pt solid transparent;
  border-bottom:7pt solid #D85A30; vertical-align:-0.5pt; margin-right:3pt; }
.key b { color:#993C1D; }

table.tl { width:100%; border-collapse:collapse; }
table.tl tr { break-inside:avoid; }
table.tl td { vertical-align:top; padding:4pt 0 6pt; border-top:0.5pt solid #ddd9cf; }
table.tl tr:first-child td { border-top:none; }
td.yr { width:46pt; font-weight:700; font-size:10.5pt; font-family:"SF Mono",Menlo,monospace;
  padding-right:8pt; padding-top:6pt; white-space:nowrap; }
tr.yr-p td.yr{color:#0F6E56} tr.yr-r td.yr{color:#534AB7} tr.yr-g td.yr{color:#8a8880}
.tag { display:inline-block; font-size:7.6pt; padding:1pt 6pt; border-radius:7pt;
  background:#eef3ec; color:#3B6D11; margin-bottom:4pt; }
.chips { display:flex; flex-wrap:wrap; gap:4pt; margin-bottom:4pt; }
.chip { display:inline-flex; align-items:flex-start; gap:4pt; padding:3pt 7pt 3pt 3pt; border-radius:4pt; }
.chip u { text-decoration:none; width:12pt;height:12pt;border-radius:50%; color:#fff; font-size:7.4pt;
  display:inline-flex;align-items:center;justify-content:center; flex:none; margin-top:1pt; }
.chip .n { display:block; font-size:9.4pt; }
.chip .c { display:block; font-size:8.4pt; }
.c-p{background:#E1F5EE} .c-p u{background:#0F6E56} .c-p .n b{color:#085041} .c-p .n i{color:#0F6E56}
.c-p .c b,.c-p .c i{color:#3B6D11}
.c-r{background:#EEEDFE} .c-r u{background:#534AB7} .c-r .n b{color:#3C3489} .c-r .n i{color:#534AB7}
.c-r .c b,.c-r .c i{color:#534AB7}
.c-g{background:#F1EFE8} .c-g u.x{background:#B4B2A9} .c-g b,.c-g i{color:#5F5E5A}

.bi { display:flex; gap:10pt; margin-top:2pt; }
.bi .z, .bi .e { flex:1 1 0; min-width:0; }
.bi .e { font-family:"Source Serif 4",Georgia,serif; color:#3f3b36; border-left:1pt solid #e2ded4; padding-left:6pt; }
.bi.sm { font-size:8.6pt; color:#55514b; }

.pb { page-break-before:always; }
.tk { border:0.7pt solid #ddd9cf; border-radius:5pt; padding:5pt 9pt; margin-bottom:4.5pt; break-inside:avoid; }
.tkh { display:flex; gap:6pt; align-items:baseline; margin-bottom:3pt; }
.tkh .no { width:13pt;height:13pt;border-radius:50%;background:#EEEDFE;color:#3C3489;
  font-size:8pt;font-weight:700;display:inline-flex;align-items:center;justify-content:center;flex:none; }
.tkh b { font-size:10pt; } .tkh i { font-size:9pt; color:#5f5e5a; margin-left:5pt; }

table.ref { width:100%; border-collapse:collapse; font-size:8.8pt; margin-top:2pt; }
table.ref th { text-align:left; font-size:8pt; color:#5f5e5a; border-bottom:1.2pt solid #1f2328; padding:3pt 4pt; }
table.ref tr { break-inside:avoid; }
table.ref td { border-bottom:0.5pt solid #e6e2d8; padding:2.2pt 4pt; vertical-align:baseline; }
table.ref td.n { width:16pt; color:#0F6E56; font-weight:700; }
table.ref td.y { width:34pt; font-family:"SF Mono",Menlo,monospace; }
table.ref td.k { width:48pt; color:#5f5e5a; font-size:8pt; }
table.ref i { color:#3f3b36; }
.foot { margin-top:5pt; font-size:7.6pt; color:#8a8880; border-top:0.5pt solid #ddd9cf; padding-top:4pt; }
"""

html = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>聯邦擴張與 13 個首府</title><style>{CSS}</style></head><body>
<h1>聯邦擴張與 13 個首府 <small>Building the Federation &amp; the 13 Capitals</small></h1>
<p class="lead">1867 → 1999，132 年拼成今天的 10 省 3 地區。地圖號碼＝加入順序。年份取自官方教材第 4 章年表。</p>
{CAPITALS_MAP_SVG.replace('class="jn-map"', 'class="map"')}
<div class="key">
  <span><i class="sw p"></i>省 Provinces · 10</span>
  <span><i class="sw r"></i>地區 Territories · 3</span>
  <span><i class="st"></i>國都 Ottawa <b>不是多倫多 not Toronto</b></span>
</div>
<table class="tl">{rows}</table>

<div class="pb"></div>
<h2>背誦小妙招 Memory tricks</h2>
{tricks}

<h2 style="margin-top:7pt">速查表 Quick reference</h2>
<table class="ref">
<tr><th>#</th><th>省／地區 Province or territory</th><th>首府 Capital</th><th>加入</th><th></th></tr>
{ref}
</table>
<div class="foot">加拿大公民考試 · 線上互動版：ukcontinental.github.io/canada-citizenship-prep/html/interactive/joining.html　｜　輪廓資料 Natural Earth（公有領域）</div>
</body></html>"""

open("sheet.html", "w", encoding="utf-8").write(html)
print("sheet.html", round(len(html)/1024, 1), "KB")
