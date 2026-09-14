"""English multiple-choice quiz pages (practice + mock exam) built from quiz/q*.json.

Each question: {ch, q, zq, o[], zo[], a, e, ze, p}
  ch = chapter number, p = paragraph index in the reading page (deep link),
  a  = index of the correct option.
Audio (optional): html/audio/quiz/<id>.m4a produced by tools/build_quiz_audio.py.
"""

from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
QUIZ_DIR = ROOT / "quiz"

CHAPTER_NAMES = {
    "00": "誓詞與前言", "01": "申請公民", "02": "權利與責任", "03": "我們是誰",
    "04": "加拿大歷史", "05": "現代加拿大", "06": "政府體制", "07": "聯邦選舉",
    "08": "司法系統", "09": "加拿大象徵", "10": "加拿大經濟", "11": "各個地區", "12": "考試與安大略",
}


def load_questions() -> list[dict]:
    out = []
    for f in sorted(QUIZ_DIR.glob("q*.json")):
        for q in json.loads(f.read_text(encoding="utf-8")):
            q = dict(q)
            q["id"] = f"q{len(out) + 1:04d}"
            out.append(q)
    return out


def reading_slug(num: str) -> str:
    for js in sorted((ROOT / "aligned").glob(f"{num}-*.json")):
        return js.stem
    return ""


def questions_js() -> str:
    qs = load_questions()
    slugs = {q["ch"]: reading_slug(q["ch"]) for q in qs}
    for q in qs:
        q["slug"] = slugs[q["ch"]]
    return "window.CIT_QUIZ=" + json.dumps(qs, ensure_ascii=False, separators=(",", ":")) + ";"


QUIZ_CSS = r"""
<style>
.qz-hero { background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%); border-left: 4px solid var(--accent);
  padding: 18px 22px; border-radius: 8px; margin: 16px 0 12px; }
.qz-hero h1 { margin: 0 0 6px; border: none; padding: 0; }
.qz-hero p { margin: 0; color: var(--muted); font-size: 14px; }
.qz-bar { position: sticky; top: 0; z-index: 5; background: var(--bg); display: flex; gap: 8px; align-items: center;
  flex-wrap: wrap; padding: 10px 0; border-bottom: 1px solid var(--line); margin-bottom: 10px; }
.qz-btn { appearance: none; border: 2px solid var(--accent); background: #fff; color: var(--accent); padding: 6px 12px;
  border-radius: 18px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: -apple-system, system-ui, sans-serif; }
.qz-btn.on, .qz-btn.main { background: var(--accent); color: #fff; }
.qz-btn:disabled { opacity: .45; cursor: default; }
.qz-bar label { font-size: 13px; color: var(--muted); display: inline-flex; align-items: center; gap: 4px; }
.qz-status { margin-left: auto; font-size: 13px; color: var(--muted); }
.qz-chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 14px; }
.qz-chip { appearance: none; border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 4px 10px;
  border-radius: 14px; font-size: 12.5px; cursor: pointer; font-family: -apple-system, system-ui, sans-serif; }
.qz-chip.on { background: #3f1a1f; color: #fff; border-color: #3f1a1f; }
.qz-q { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; margin-bottom: 14px; }
.qz-q.hidden { display: none; }
.qz-head { display: flex; gap: 10px; align-items: baseline; font-size: 12px; color: var(--muted); margin-bottom: 6px;
  font-family: -apple-system, system-ui, sans-serif; }
.qz-head .n { font-weight: 700; color: var(--accent); }
.qz-text { font-size: 17px; line-height: 1.6; font-family: "Source Serif 4", Georgia, serif; color: var(--en-ink); }
.qz-zh { font-size: 14.5px; color: var(--muted); margin-top: 4px; display: none; }
.qz-q.zh .qz-zh { display: block; }
.qz-opts { display: grid; gap: 8px; margin-top: 12px; }
.qz-opt { appearance: none; text-align: left; padding: 10px 14px; border-radius: 10px; border: 1.5px solid var(--line);
  background: #faf8f4; cursor: pointer; font-size: 15px; font-family: "Source Serif 4", Georgia, serif; line-height: 1.5;
  display: grid; grid-template-columns: 26px 1fr; gap: 8px; align-items: start; color: var(--ink); }
.qz-opt .k { font-weight: 700; color: var(--accent); font-family: -apple-system, system-ui, sans-serif; }
.qz-opt .z { display: none; font-size: 13px; color: var(--muted); grid-column: 2; }
.qz-q.zh .qz-opt .z { display: block; }
.qz-opt:hover { border-color: var(--accent); }
.qz-opt.correct { border-color: #2e7d46; background: #e8f5ea; }
.qz-opt.wrong { border-color: #c8102e; background: #fbe9ec; }
.qz-opt.picked { box-shadow: inset 0 0 0 2px #3f1a1f; }
.qz-opt:disabled { cursor: default; }
.qz-ex { display: none; margin-top: 10px; padding: 10px 12px; background: #f3efe6; border-radius: 8px; font-size: 14px; line-height: 1.6; }
.qz-ex .zh { color: var(--muted); font-size: 13.5px; margin-top: 4px; }
.qz-ex a { color: var(--accent); }
.qz-q.done .qz-ex { display: block; }
.qz-tools { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
.qz-mini { appearance: none; border: 1px solid var(--line); background: #fff; color: var(--muted); padding: 3px 9px;
  border-radius: 12px; font-size: 12px; cursor: pointer; font-family: -apple-system, system-ui, sans-serif; }
.qz-mini.on { border-color: var(--accent); color: var(--accent); }
.qz-timer { font-family: monospace; font-size: 18px; font-weight: 700; color: #3f1a1f; }
.qz-timer.low { color: var(--accent); }
.qz-result { background: #fff; border: 2px solid var(--accent); border-radius: 12px; padding: 18px 20px; margin: 12px 0; }
.qz-result h2 { margin: 0 0 6px; border: none; padding: 0; font-size: 22px; }
.qz-result .big { font-size: 40px; font-weight: 700; font-family: Georgia, serif; }
.qz-result .pass { color: #2e7d46; } .qz-result .fail { color: var(--accent); }
.qz-start { text-align: center; padding: 30px 10px; }
.qz-start p { color: var(--muted); }
</style>
"""

QUIZ_JS = r"""
<script>
(function() {
  var root = document.getElementById('__ROOT__');
  if (!root || !window.CIT_QUIZ) return;
  var MODE = '__MODE__';
  var ALL = window.CIT_QUIZ;
  var base = (location.pathname.indexOf('/quiz/') >= 0 ? '../' : '');
  var audio = new Audio();
  var LS_WRONG = 'cit_wrong_v1';
  var CH_NAMES = __CH_NAMES__;
  var LETTERS = ['A', 'B', 'C', 'D', 'E'];

  function wrongSet() { try { return new Set(JSON.parse(localStorage.getItem(LS_WRONG) || '[]')); } catch (e) { return new Set(); } }
  function saveWrong(s) { try { localStorage.setItem(LS_WRONG, JSON.stringify(Array.from(s))); } catch (e) {} }
  function addWrong(id) { var s = wrongSet(); s.add(id); saveWrong(s); }
  function delWrong(id) { var s = wrongSet(); s.delete(id); saveWrong(s); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }

  function card(q, n) {
    var opts = q.o.map(function(o, i) {
      return '<button class="qz-opt" type="button" data-i="' + i + '"><span class="k">' + LETTERS[i] + '</span><span>' + esc(o) +
        '</span><span class="z">' + esc(q.zo[i]) + '</span></button>';
    }).join('');
    var link = q.slug ? '<a href="' + base + 'reading/' + q.slug + '.html#p' + q.p + '">看原文 ↗</a>' : '';
    return '<div class="qz-q" data-id="' + q.id + '" data-ch="' + q.ch + '" data-a="' + q.a + '">' +
      '<div class="qz-head"><span class="n">' + n + '</span><span>第 ' + q.ch + ' 章 · ' + (CH_NAMES[q.ch] || '') + '</span></div>' +
      '<div class="qz-text">' + esc(q.q) + '</div><div class="qz-zh">' + esc(q.zq) + '</div>' +
      '<div class="qz-opts">' + opts + '</div>' +
      '<div class="qz-tools"><button class="qz-mini qz-tzh" type="button">中</button>' +
      '<button class="qz-mini qz-say" type="button">🔊 念題目</button></div>' +
      '<div class="qz-ex"><div class="en">' + esc(q.e) + ' ' + link + '</div><div class="zh">' + esc(q.ze) + '</div></div>' +
      '</div>';
  }

  function answer(qEl, picked, opts) {
    if (qEl.classList.contains('done')) return;
    if (!opts.instant) {
      // exam mode: record the choice only; answers can be changed until submit
      qEl.querySelectorAll('.qz-opt').forEach(function(b){ b.classList.remove('picked'); });
      var chosen = qEl.querySelector('.qz-opt[data-i="' + picked + '"]');
      if (chosen) chosen.classList.add('picked');
      qEl.dataset.picked = picked;
      qEl.classList.add('answered');
      return;
    }
    var a = parseInt(qEl.dataset.a, 10);
    var btns = qEl.querySelectorAll('.qz-opt');
    btns.forEach(function(b) { b.disabled = true; if (parseInt(b.dataset.i, 10) === a) b.classList.add('correct'); });
    var pk = qEl.querySelector('.qz-opt[data-i="' + picked + '"]');
    if (pk) pk.classList.add('picked');
    var ok = picked === a;
    if (!ok && pk) pk.classList.add('wrong');
    qEl.classList.add('done');
    qEl.dataset.ok = ok ? '1' : '0';
    if (opts.instant) qEl.classList.add('reveal');
    if (ok) { if (opts.instant) delWrong(qEl.dataset.id); } else addWrong(qEl.dataset.id);
    return ok;
  }

  root.addEventListener('click', function(e) {
    var t = e.target;
    var qEl = t.closest && t.closest('.qz-q');
    if (t.closest('.qz-tzh') && qEl) { qEl.classList.toggle('zh'); t.closest('.qz-tzh').classList.toggle('on'); return; }
    if (t.closest('.qz-say') && qEl) {
      audio.pause(); audio.src = base + 'audio/quiz/' + qEl.dataset.id + '.m4a'; audio.play().catch(function(){});
      audio.onerror = function() {
        if (!window.speechSynthesis) return;
        var q = ALL.find(function(x){ return x.id === qEl.dataset.id; });
        var u = new SpeechSynthesisUtterance(q.q + '. ' + q.o.map(function(o,i){ return LETTERS[i] + '. ' + o; }).join('. '));
        u.lang = 'en-US'; u.rate = 0.9; window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
      };
      return;
    }
    var opt = t.closest && t.closest('.qz-opt');
    if (opt && qEl && !opt.disabled) {
      var ok = answer(qEl, parseInt(opt.dataset.i, 10), { instant: MODE === 'practice' });
      if (MODE === 'practice') updatePracticeStatus();
      else updateMockStatus();
    }
  });

  // ---------------- practice ----------------
  var list = root.querySelector('.qz-list');
  var status = root.querySelector('.qz-status');
  var curCh = 'all', onlyWrong = false;

  function renderPractice() {
    var ws = wrongSet();
    var qs = ALL.filter(function(q) { return (curCh === 'all' || q.ch === curCh) && (!onlyWrong || ws.has(q.id)); });
    list.innerHTML = qs.length ? qs.map(function(q, i) { return card(q, i + 1); }).join('') :
      '<p style="color:var(--muted)">這個範圍沒有題目' + (onlyWrong ? '（錯題本是空的，太棒了）' : '') + '。</p>';
    if (root.querySelector('.qz-allzh').classList.contains('on')) list.querySelectorAll('.qz-q').forEach(function(q){ q.classList.add('zh'); });
    updatePracticeStatus();
  }
  function updatePracticeStatus() {
    var qs = list.querySelectorAll('.qz-q'), done = list.querySelectorAll('.qz-q.done'), ok = list.querySelectorAll('.qz-q[data-ok="1"]');
    status.textContent = '答了 ' + done.length + ' / ' + qs.length + '，答對 ' + ok.length + '　錯題本 ' + wrongSet().size + ' 題';
  }
  if (MODE === 'practice') {
    var chips = root.querySelector('.qz-chips');
    var chs = Array.from(new Set(ALL.map(function(q){ return q.ch; }))).sort();
    chips.innerHTML = '<button class="qz-chip on" data-ch="all" type="button">全部 ' + ALL.length + '</button>' +
      chs.map(function(c){ var n = ALL.filter(function(q){return q.ch===c;}).length; return '<button class="qz-chip" data-ch="' + c + '" type="button">' + c + ' ' + (CH_NAMES[c]||'') + ' ' + n + '</button>'; }).join('');
    chips.addEventListener('click', function(e) {
      var b = e.target.closest('.qz-chip'); if (!b) return;
      chips.querySelectorAll('.qz-chip').forEach(function(x){ x.classList.remove('on'); }); b.classList.add('on');
      curCh = b.dataset.ch; renderPractice();
    });
    root.querySelector('.qz-wrong').addEventListener('click', function() {
      onlyWrong = !onlyWrong; this.classList.toggle('on', onlyWrong); renderPractice();
    });
    root.querySelector('.qz-allzh').addEventListener('click', function() {
      this.classList.toggle('on'); var on = this.classList.contains('on');
      list.querySelectorAll('.qz-q').forEach(function(q){ q.classList.toggle('zh', on); });
    });
    root.querySelector('.qz-reset').addEventListener('click', function() { renderPractice(); window.scrollTo(0, 0); });
    renderPractice();
  }

  // ---------------- mock exam ----------------
  var timerId = null, deadline = 0;
  function fmt(s) { s = Math.max(0, s); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
  function updateMockStatus() {
    var done = list.querySelectorAll('.qz-q.answered').length;
    root.querySelector('.qz-status').textContent = '已作答 ' + done + ' / 20';
  }
  function startMock() {
    var ont = shuffle(ALL.filter(function(q){ return /^ONTARIO/.test(q.q); })).slice(0, 2);
    var rest = shuffle(ALL.filter(function(q){ return !/^ONTARIO/.test(q.q); })).slice(0, 20 - ont.length);
    var qs = shuffle(ont.concat(rest));
    list.innerHTML = qs.map(function(q, i) { return card(q, i + 1); }).join('');
    root.querySelector('.qz-start').style.display = 'none';
    root.querySelector('.qz-result').style.display = 'none';
    root.querySelector('.qz-submit').disabled = false;
    deadline = Date.now() + 30 * 60 * 1000;
    var tEl = root.querySelector('.qz-timer');
    clearInterval(timerId);
    timerId = setInterval(function() {
      var left = Math.round((deadline - Date.now()) / 1000);
      tEl.textContent = fmt(left); tEl.classList.toggle('low', left < 300);
      if (left <= 0) finishMock(true);
    }, 500);
    tEl.textContent = '30:00';
    updateMockStatus();
    window.scrollTo(0, 0);
  }
  function finishMock(timeout) {
    clearInterval(timerId);
    var qs = list.querySelectorAll('.qz-q'); var ok = 0;
    qs.forEach(function(q) {
      var a = parseInt(q.dataset.a, 10);
      var picked = q.dataset.picked === undefined ? -1 : parseInt(q.dataset.picked, 10);
      var good = picked === a;
      q.querySelectorAll('.qz-opt').forEach(function(b) {
        b.disabled = true;
        var i = parseInt(b.dataset.i, 10);
        if (i === a) b.classList.add('correct');
        if (i === picked && !good) b.classList.add('wrong');
      });
      q.classList.add('done');
      q.dataset.ok = good ? '1' : '0';
      if (good) { ok++; delWrong(q.dataset.id); } else addWrong(q.dataset.id);
    });
    var r = root.querySelector('.qz-result');
    var pass = ok >= 15;
    r.innerHTML = '<h2>' + (timeout ? '時間到！' : '交卷') + '</h2><div class="big ' + (pass ? 'pass' : 'fail') + '">' + ok + ' / 20</div>' +
      '<p>' + (pass ? '通過（15 題以上）🎉' : '未達 15 題，再練一次。') + '　錯的題目已進錯題本，下面每題都有解說與原文連結。</p>' +
      '<button class="qz-btn main qz-again" type="button">再考一次</button>';
    r.style.display = 'block';
    root.querySelector('.qz-submit').disabled = true;
    r.querySelector('.qz-again').addEventListener('click', startMock);
    r.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  if (MODE === 'mock') {
    root.querySelector('.qz-begin').addEventListener('click', startMock);
    root.querySelector('.qz-submit').addEventListener('click', function(){ finishMock(false); });
  }
})();
</script>
"""


def _page(mode: str, root_id: str, hero: str, bar: str, extra: str = "") -> str:
    ch_names = json.dumps(CHAPTER_NAMES, ensure_ascii=False)
    return (QUIZ_CSS + f'<div class="qz" id="{root_id}">{hero}{bar}{extra}<div class="qz-list"></div></div>'
            + QUIZ_JS.replace("__ROOT__", root_id).replace("__MODE__", mode).replace("__CH_NAMES__", ch_names))


def build_practice_body() -> str:
    n = len(load_questions())
    hero = f'''<div class="qz-hero"><h1>📝 英文選擇題練習</h1>
<p>{n} 題，格式與真考相同（英文、四選一或是非）。按選項立刻看對錯與解說；按「中」看中文；「看原文」跳到人聲頁那一段。答錯的題自動進錯題本。</p></div>'''
    bar = '''<div class="qz-bar">
<button class="qz-btn qz-allzh" type="button">全部顯示中文</button>
<button class="qz-btn qz-wrong" type="button">只看錯題本</button>
<button class="qz-btn qz-reset" type="button">重新作答</button>
<span class="qz-status"></span></div><div class="qz-chips"></div>'''
    return _page("practice", "qz-practice", hero, bar)


def build_mock_body() -> str:
    hero = '''<div class="qz-hero"><h1>⏱ 模擬考</h1>
<p>照真考規格：隨機 20 題（含 1–2 題安大略省題）、30 分鐘倒數、答對 15 題通過。作答中不顯示對錯，交卷後才看解說。</p></div>'''
    bar = '''<div class="qz-bar"><span class="qz-timer">30:00</span>
<button class="qz-btn main qz-submit" type="button" disabled>交卷</button>
<span class="qz-status"></span></div>'''
    extra = '''<div class="qz-start"><button class="qz-btn main qz-begin" type="button" style="font-size:18px;padding:12px 28px">開始模擬考</button>
<p>考試時可以按每題的「中」偷看中文，但真考沒有——建議先不看。</p></div>
<div class="qz-result" style="display:none"></div>'''
    return _page("mock", "qz-mock", hero, bar, extra)
