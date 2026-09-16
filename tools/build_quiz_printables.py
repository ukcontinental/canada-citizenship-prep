"""Offline study artifacts from the 328-question bank, for 公民考試資料夾 (not the website).

Produces:
  1. <folder>/模擬考題庫_328題_中英對照_答案綠字.pdf     print layout, correct answer in green
  2. <folder>/模擬考題庫_328題_可朗讀版/                  self-contained HTML + audio/, opens offline

Run: python3 tools/build_quiz_printables.py [target_folder]
     (default target: /Users/willie/code/公民考試資料夾)
"""

from __future__ import annotations
import html
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from quiz_content import load_questions, CHAPTER_NAMES  # noqa: E402

DEFAULT_DEST = Path("/Users/willie/code/公民考試資料夾")
HTML2PDF = Path.home() / ".claude/skills/magazine-cover-report/scripts/html2pdf.sh"
L = "ABCDE"
E = html.escape

PRINT_CSS = """
@page { size: A4; margin: 14mm 12mm 14mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "PingFang TC","Noto Sans TC",sans-serif; font-size: 9.2pt; line-height: 1.5; color: #111; -webkit-print-color-adjust: exact; }
.en { font-family: "Source Serif 4", Georgia, "Times New Roman", serif; }
h1 { font-family: Georgia, "Songti TC", serif; font-size: 22pt; font-weight: 400; margin-bottom: 4pt; }
.sub { color: #666; font-size: 9pt; margin-bottom: 10pt; padding-bottom: 6pt; border-bottom: 1pt solid #111; }
h2 { font-size: 13pt; font-weight: 700; margin: 12pt 0 6pt; padding: 4pt 8pt; background: #f1ede4; border-left: 4pt solid #c8102e; page-break-after: avoid; }
.q { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; padding: 6pt 0 7pt; border-bottom: 0.5pt solid #ddd; page-break-inside: avoid; }
.n { font-weight: 700; color: #c8102e; margin-right: 4pt; }
.qt { font-weight: 700; margin-bottom: 2pt; }
.o { padding-left: 14pt; text-indent: -14pt; }
.o.ok { color: #1a7f37; font-weight: 700; }
.ex { grid-column: 1 / -1; color: #777; font-size: 8pt; line-height: 1.4; margin-top: 1pt; }
.ex b { color: #1a7f37; font-weight: 700; }
.toc { columns: 2; font-size: 9pt; margin-bottom: 8pt; }
"""

WEB_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "PingFang TC","Noto Sans TC",sans-serif; font-size: 15px; line-height: 1.6; color: #111; background: #fdfcf9; padding: 24px; max-width: 1200px; margin: 0 auto; }
.en { font-family: "Source Serif 4", Georgia, "Times New Roman", serif; }
h1 { font-family: Georgia, "Songti TC", serif; font-size: 28px; font-weight: 400; margin-bottom: 6px; }
.sub { color: #666; font-size: 13px; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid #111; }
.bar { position: sticky; top: 0; background: #fdfcf9; padding: 10px 0; border-bottom: 1px solid #ddd; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; z-index: 5; }
.bar button, .bar select { font-size: 14px; padding: 6px 12px; border-radius: 16px; border: 1.5px solid #c8102e; background: #fff; color: #c8102e; cursor: pointer; font-family: inherit; }
.bar button.main { background: #c8102e; color: #fff; }
.bar .st { margin-left: auto; color: #666; font-size: 13px; }
h2 { font-size: 18px; font-weight: 700; margin: 22px 0 8px; padding: 6px 10px; background: #f1ede4; border-left: 5px solid #c8102e; display: flex; align-items: center; gap: 10px; }
h2 button { font-size: 12px; padding: 3px 10px; border-radius: 12px; border: 1px solid #c8102e; background: #fff; color: #c8102e; cursor: pointer; font-family: inherit; }
.q { display: grid; grid-template-columns: 34px 1fr 1fr; gap: 14px; padding: 10px 0 12px; border-bottom: 1px solid #ddd; }
.q.playing { background: #fff8e6; }
.pl { width: 30px; height: 30px; border-radius: 50%; border: 1.5px solid #c8102e; background: #fff; color: #c8102e; cursor: pointer; font-size: 12px; margin-top: 2px; }
.pl.on { background: #c8102e; color: #fff; }
.n { font-weight: 700; color: #c8102e; margin-right: 4px; }
.qt { font-weight: 700; margin-bottom: 3px; }
.o { padding-left: 22px; text-indent: -22px; }
.o.ok { color: #1a7f37; font-weight: 700; }
.ex { grid-column: 2 / -1; color: #777; font-size: 12.5px; line-height: 1.45; margin-top: 2px; }
.ex b { color: #1a7f37; }
body.hide .o.ok { color: #111; font-weight: 400; }
body.hide .ex { display: none; }
@media (max-width: 760px) { .q { grid-template-columns: 34px 1fr; } .q > div:nth-child(3) { grid-column: 2; } .ex { grid-column: 2; } }
"""

WEB_JS = """
(function(){
  var audio=new Audio(); var cur=null; var chain=null;
  function reset(q){ if(!q) return; q.classList.remove('playing'); var b=q.querySelector('.pl'); b.classList.remove('on'); b.textContent='\\u25b6'; }
  function stop(){ audio.pause(); reset(cur); cur=null; chain=null; document.getElementById('st').textContent=''; }
  function play(q, next){ reset(cur);
    cur=q; chain=next||null; q.classList.add('playing'); var b=q.querySelector('.pl'); b.classList.add('on'); b.textContent='\\u275a\\u275a';
    audio.src='audio/'+q.dataset.id+'.m4a'; audio.play(); q.scrollIntoView({block:'center',behavior:'smooth'});
    document.getElementById('st').textContent='\\u64ad\\u653e\\u7b2c '+q.dataset.n+' \\u984c'; }
  audio.addEventListener('ended', function(){ if(chain && chain.length){ play(chain.shift(), chain); } else stop(); });
  document.addEventListener('click', function(e){
    var b=e.target.closest('.pl'); if(b){ var q=b.closest('.q');
      if(cur===q && !audio.paused){ audio.pause(); b.textContent='\\u25b6'; }
      else if(cur===q){ audio.play(); b.textContent='\\u275a\\u275a'; } else play(q); return; }
    var c=e.target.closest('.chap'); if(c){ var list=[].slice.call(document.querySelectorAll('.q[data-ch="'+c.dataset.ch+'"]')); play(list.shift(), list); return; }
  });
  document.getElementById('all').onclick=function(){ var list=[].slice.call(document.querySelectorAll('.q')); play(list.shift(), list); };
  document.getElementById('stop').onclick=stop;
  document.getElementById('hide').onclick=function(){ document.body.classList.toggle('hide');
    this.textContent=document.body.classList.contains('hide')?'\\u986f\\u793a\\u7b54\\u6848':'\\u96b1\\u85cf\\u7b54\\u6848\\uff08\\u81ea\\u6e2c\\uff09'; };
  document.getElementById('jump').onchange=function(){ var h=document.getElementById('ch-'+this.value); if(h) h.scrollIntoView({behavior:'smooth'}); };
})();
"""


def question_block(q: dict, n: int, web: bool) -> str:
    zo = "".join(f"<div class='o{' ok' if k == q['a'] else ''}'>{L[k]}. {E(o)}</div>" for k, o in enumerate(q["zo"]))
    eo = "".join(f"<div class='o en{' ok' if k == q['a'] else ''}'>{L[k]}. {E(o)}</div>" for k, o in enumerate(q["o"]))
    zh = f"<div><div class='qt'><span class='n'>{n}.</span>{E(q['zq'])}</div>{zo}</div>"
    en = f"<div><div class='qt en'><span class='n'>{n}.</span>{E(q['q'])}</div>{eo}</div>"
    ex = f"<div class='ex'><b>答案 {L[q['a']]}</b>　{E(q['ze'])}　<span class='en'>{E(q['e'])}</span></div>"
    if web:
        return (f"<div class='q' data-id='{q['id']}' data-ch='{q['ch']}' data-n='{n}'>"
                f"<button class='pl' title='念這題'>▶</button>{zh}{en}{ex}</div>")
    return f"<div class='q'>{zh}{en}{ex}</div>"


def build_pages(qs: list[dict], cnt: Counter, web: bool) -> str:
    out, cur, n = [], None, 0
    for q in qs:
        if q["ch"] != cur:
            cur = q["ch"]
            name = E(CHAPTER_NAMES.get(cur, ""))
            btn = f"<button class='chap' data-ch='{cur}'>▶ 連續播放本章</button>" if web else ""
            out.append(f"<h2 id='ch-{cur}'>第 {cur} 章 · {name}（{cnt[cur]} 題）{btn}</h2>")
        n += 1
        out.append(question_block(q, n, web))
    return "\n".join(out)


def main():
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DEST
    # load order follows the quiz/*.json filenames, which interleaves chapters;
    # a study document must run chapter by chapter, so regroup before rendering.
    qs = sorted(load_questions(), key=lambda q: (q["ch"], int(q["id"][1:])))
    cnt = Counter(q["ch"] for q in qs)
    note = ("題目全數出自 Discover Canada；安大略省題以 2026 年現況為準，考前一週請再確認。")

    # ---- print / PDF ----
    toc = "".join(f"<div>第 {c} 章 {CHAPTER_NAMES.get(c,'')}：{n} 題</div>" for c, n in sorted(cnt.items()))
    doc = (f"<!DOCTYPE html><html lang='zh-Hant'><head><meta charset='utf-8'><title>模擬考題庫 {len(qs)} 題</title>"
           f"<style>{PRINT_CSS}</style></head><body>"
           f"<h1>加拿大公民考試 · 模擬考題庫 {len(qs)} 題</h1>"
           f"<div class='sub'>左中文、右英文；<span style='color:#1a7f37;font-weight:700'>綠字＝正確答案</span>，"
           f"黑字＝其他選項；灰字＝解說。{note}</div><div class='toc'>{toc}</div>"
           f"{build_pages(qs, cnt, web=False)}</body></html>")
    tmp_html = Path("/tmp/_quizbank_print.html")
    tmp_html.write_text(doc, encoding="utf-8")
    pdf = dest / f"模擬考題庫_{len(qs)}題_中英對照_答案綠字.pdf"
    subprocess.run(["bash", str(HTML2PDF), str(tmp_html), str(pdf), "qbank"], check=True, capture_output=True)
    print(f"PDF  -> {pdf}  ({pdf.stat().st_size/1e6:.1f} MB)")

    # ---- offline listenable ----
    web_dir = dest / f"模擬考題庫_{len(qs)}題_可朗讀版"
    audio_out = web_dir / "audio"
    audio_out.mkdir(parents=True, exist_ok=True)
    src_audio = ROOT / "html" / "audio" / "quiz"
    for q in qs:
        f = src_audio / f"{q['id']}.m4a"
        if f.exists():
            shutil.copy2(f, audio_out / f.name)
    opts = "".join(f"<option value='{c}'>第 {c} 章 {CHAPTER_NAMES.get(c,'')}（{n} 題）</option>"
                   for c, n in sorted(cnt.items()))
    page = (f"<!DOCTYPE html><html lang='zh-Hant'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>模擬考題庫 {len(qs)} 題（可朗讀）</title><style>{WEB_CSS}</style></head><body>"
            f"<h1>加拿大公民考試 · 模擬考題庫 {len(qs)} 題（可朗讀）</h1>"
            f"<div class='sub'>左中文、右英文；<span style='color:#1a7f37;font-weight:700'>綠字＝正確答案</span>。"
            f"每題 ▶ 用 Ava 念英文題目與選項；「連續播放本章」一題接一題念。離線可用，"
            f"音檔在同資料夾的 audio/ 裡，<b>請整個資料夾一起搬</b>。{note}</div>"
            f"<div class='bar'><button class='main' id='all'>▶ 從頭連續播放全部</button>"
            f"<button id='stop'>■ 停</button><button id='hide'>隱藏答案（自測）</button>"
            f"<label>跳到 <select id='jump'><option value=''>章節…</option>{opts}</select></label>"
            f"<span class='st' id='st'></span></div>"
            f"{build_pages(qs, cnt, web=True)}<script>{WEB_JS}</script></body></html>")
    (web_dir / "模擬考題庫_可朗讀.html").write_text(page, encoding="utf-8")
    size = sum(p.stat().st_size for p in web_dir.rglob("*")) / 1e6
    print(f"HTML -> {web_dir}  ({size:.0f} MB, {len(list(audio_out.glob('*.m4a')))} clips)")


if __name__ == "__main__":
    main()
