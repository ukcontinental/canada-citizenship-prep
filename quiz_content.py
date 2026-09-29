"""English multiple-choice quiz pages built from quiz/q*.json and data/trap-questions.js.

One engine (QUIZ_JS) serves every bank:
  * 328 題練習／模擬考   — window.CIT_QUIZ   {id, ch, q, zq, o[], zo[], a, e, ze, p, slug}
  * 陷阱題 第一～三套     — window.CIT_TRAP   {id, set, ch, t, q, zq, o[], zo[], a, f, e, k[]}
  * 錯題本重練           — both banks, only the ids in the wrong-book

Trap-only fields: t = trap type (N/R/S/T/W/C/F), **word** in q = the trap word
(rendered as an orange mark), f = 1 keeps option order (True/False), k = keywords.
Options are shuffled per render unless f=1; data-i keeps the ORIGINAL index so
`a` stays valid.

Wrong-book (localStorage cit_wrong_v2): { id: {n: times wrong, last: what was
picked, t: epoch ms, bank: 'quiz'|'trap'} }. Wrong answers, 「我不會」 and unanswered
exam questions all land here; a correct answer in practice removes the entry.
v1 (a plain id list) is migrated on first load.

Audio: html/audio/quiz/{en,zh}/<id>.m4a from tools/build_quiz_audio.py.
"""

from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parent
QUIZ_DIR = ROOT / "quiz"

CHAPTER_NAMES = {
    "00": "誓詞與前言", "01": "申請公民", "02": "權利與責任", "03": "我們是誰",
    "04": "加拿大歷史", "05": "現代加拿大", "06": "政府體制", "07": "聯邦選舉",
    "08": "司法系統", "09": "加拿大象徵", "10": "加拿大經濟", "11": "各個地區", "12": "考試與安大略",
}

TRAP_TYPES = {"N": "否定題", "R": "反問題", "S": "換字題", "T": "是非題",
              "W": "找正確句", "C": "情境題", "F": "最／第一"}

SET_NAMES = {"A": "第一套", "B": "第二套", "C": "第三套", "D": "第四套", "E": "第五套", "F": "第六套"}


def load_questions() -> list[dict]:
    out = []
    for f in sorted(QUIZ_DIR.glob("q[0-9]*.json")):
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


_TRAP_CACHE: list[dict] | None = None


def load_trap_bank_cached() -> list[dict]:
    """單次建置只解析一次 data/trap-questions*.js，其他呼叫端都共用這份。"""
    global _TRAP_CACHE
    if _TRAP_CACHE is None:
        from tools.trap_bank import load_trap_bank
        _TRAP_CACHE = load_trap_bank()
    return _TRAP_CACHE


def trap_js() -> str:
    from tools.trap_bank import bank_js
    return bank_js(load_trap_bank_cached())


QUIZ_CSS = r"""
<style>
.qz-hero { background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%); border-left: 4px solid var(--accent);
  padding: 18px 22px; border-radius: 8px; margin: 16px 0 12px; }
.qz-hero h1 { margin: 0 0 6px; border: none; padding: 0; }
.qz-hero p { margin: 0; color: var(--muted); font-size: 14px; }
.qz-modes { display: inline-flex; border: 1px solid var(--line); border-radius: 20px; overflow: hidden; margin: 4px 0 8px; }
.qz-modes button { appearance: none; border: none; background: #fff; color: var(--muted); padding: 8px 16px; font-size: 14px;
  cursor: pointer; font-family: -apple-system, system-ui, sans-serif; font-weight: 600; }
.qz-modes button + button { border-left: 1px solid var(--line); }
.qz-modes button.on { background: var(--accent); color: #fff; }
.qz-bar { position: sticky; top: 0; z-index: 5; background: var(--bg); display: flex; gap: 8px; align-items: center;
  flex-wrap: wrap; padding: 10px 0; border-bottom: 1px solid var(--line); margin-bottom: 10px; }
.qz-btn { appearance: none; border: 2px solid var(--accent); background: #fff; color: var(--accent); padding: 6px 12px;
  border-radius: 18px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: -apple-system, system-ui, sans-serif; }
.qz-btn.on, .qz-btn.main { background: var(--accent); color: #fff; }
.qz-btn.danger { border-color: #8a1f2e; color: #8a1f2e; }
.qz-btn.danger.armed { background: #8a1f2e; color: #fff; }
.qz-btn:disabled { opacity: .45; cursor: default; }
.qz-status { margin-left: auto; font-size: 13px; color: var(--muted); }
.qz-chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 14px; }
.qz-chip { appearance: none; border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 4px 10px;
  border-radius: 14px; font-size: 12.5px; cursor: pointer; font-family: -apple-system, system-ui, sans-serif; }
.qz-chip.on { background: #3f1a1f; color: #fff; border-color: #3f1a1f; }
.qz-q { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; margin-bottom: 14px; }
.qz-q.hidden { display: none; }
.qz-head { display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; font-size: 12px; color: var(--muted); margin-bottom: 6px;
  font-family: -apple-system, system-ui, sans-serif; }
.qz-head .n { font-weight: 700; color: var(--accent); }
.qz-head .id { font-family: monospace; color: #8a8880; }
.qz-type { padding: 1px 8px; border-radius: 9px; background: #fdf0e3; color: #8a5a22; font-weight: 600; }
.qz-type.T { background: #EEEDFE; color: #3C3489; }
.qz-type.N, .qz-type.W { background: #FCEBEB; color: #791F1F; }
.qz-wrongn { color: #8a1f2e; font-weight: 600; }
.qz-text { font-size: 17px; line-height: 1.6; font-family: "Source Serif 4", Georgia, serif; color: var(--en-ink); }
.qz-text mark.trap, .qz-ex mark.trap { background: #ffd28a; color: #5a3200; padding: 0 3px; border-radius: 3px; font-weight: 700; }
.qz-zh { font-size: 17px; line-height: 1.6; color: var(--ink); }
/* 中／英同級：夠寬左右並排，不夠自動上下 */
.qz-pair { display: flex; flex-wrap: wrap; gap: 4px 20px; align-items: flex-start; }
.qz-pair > * { flex: 1 1 250px; min-width: 0; }
.qz-pair > .qz-text, .qz-pair > .e { border-left: 2px solid var(--line); padding-left: 12px; }
.qz-q.nozh .qz-zh, .qz-q.nozh .qz-opt .z, .qz-q.nozh .qz-ex .zh { display: none; }
.qz-opts { display: grid; gap: 8px; margin-top: 12px; }
.qz-opt { appearance: none; text-align: left; padding: 10px 14px; border-radius: 10px; border: 1.5px solid var(--line);
  background: #faf8f4; cursor: pointer; font-size: 15px; font-family: "Source Serif 4", Georgia, serif; line-height: 1.5;
  display: grid; grid-template-columns: 26px 1fr; gap: 8px; align-items: start; color: var(--ink); }
.qz-opt .k { font-weight: 700; color: var(--accent); font-family: -apple-system, system-ui, sans-serif; }
.qz-opt .z { font-size: 15px; color: var(--ink); font-family: -apple-system, "PingFang TC", system-ui, sans-serif; }
.qz-opt .e { font-size: 15px; }
.qz-opt:hover { border-color: var(--accent); }
.qz-opt.correct { border-color: #2e7d46; background: #e8f5ea; }
.qz-opt.wrong { border-color: #c8102e; background: #fbe9ec; }
.qz-opt.picked { box-shadow: inset 0 0 0 2px #3f1a1f; }
.qz-opt:disabled { cursor: default; }
.qz-ex { display: none; margin-top: 10px; padding: 10px 12px; background: #f3efe6; border-radius: 8px; font-size: 14px; line-height: 1.6; }
.qz-ex .zh { color: var(--ink); font-size: 14px; }
.qz-ex .en { font-family: "Source Serif 4", Georgia, serif; font-size: 14px; }
.qz-ex a { color: var(--accent); }
.qz-kw { margin-top: 8px; padding-top: 8px; border-top: 1px dashed #d9d3c4; font-size: 13.5px; }
.qz-kw b { font-family: "Source Serif 4", Georgia, serif; color: #5a3200; background: #ffe9c7; padding: 0 4px; border-radius: 3px; }
.qz-kw span { margin-right: 12px; white-space: nowrap; }
.qz-q.done .qz-ex { display: block; }
.qz-tools { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
.qz-mini { appearance: none; border: 1px solid var(--line); background: #fff; color: var(--muted); padding: 3px 9px;
  border-radius: 12px; font-size: 12px; cursor: pointer; font-family: -apple-system, system-ui, sans-serif; }
.qz-mini.on { border-color: var(--accent); color: var(--accent); }
.qz-mini.dunno { border-color: #c47a1a; color: #8a5a22; font-weight: 600; }
.qz-mini.learned { border-color: #2e7d46; color: #2e7d46; }
.qz-q.done .qz-dunno { display: none; }
.qz-timer { font-family: monospace; font-size: 18px; font-weight: 700; color: #3f1a1f; }
.qz-timer.low { color: var(--accent); }
.qz-result { background: #fff; border: 2px solid var(--accent); border-radius: 12px; padding: 18px 20px; margin: 12px 0; }
.qz-result h2 { margin: 0 0 6px; border: none; padding: 0; font-size: 22px; }
.qz-result .big { font-size: 40px; font-weight: 700; font-family: Georgia, serif; }
.qz-result .pass { color: #2e7d46; } .qz-result .fail { color: var(--accent); }
.qz-start { text-align: center; padding: 30px 10px; }
.qz-start p { color: var(--muted); }
.qz-empty { color: var(--muted); padding: 20px 0; }
</style>
"""

QUIZ_JS = r"""
<script>
(function() {
  var root = document.getElementById('__ROOT__');
  if (!root) return;
  var ALL = (__BANK__) || [];
  var MODE = '__MODE__';           // 'practice' | 'mock'; a page with .qz-modes can switch
  var WRONG_ONLY_PAGE = __WRONG_ONLY__;
  var base = (location.pathname.indexOf('/quiz/') >= 0 ? '../' : '');
  var audio = new Audio();
  var LS_V1 = 'cit_wrong_v1', LS = 'cit_wrong_v2', LS_ZH = 'cit_zh_hidden';
  var CH_NAMES = __CH_NAMES__, TYPES = __TYPES__;
  var LETTERS = ['A', 'B', 'C', 'D', 'E'];

  // ---------------- wrong-book (v2 object; v1 list migrated once) ----------------
  function loadBook() {
    var book = {};
    try { book = JSON.parse(localStorage.getItem(LS) || '{}') || {}; } catch (e) { book = {}; }
    try {
      var v1 = JSON.parse(localStorage.getItem(LS_V1) || 'null');
      if (Array.isArray(v1)) {
        v1.forEach(function(id) { if (!book[id]) book[id] = { n: 1, last: '', t: 0, bank: 'quiz' }; });
        localStorage.removeItem(LS_V1);
        localStorage.setItem(LS, JSON.stringify(book));
      }
    } catch (e) {}
    return book;
  }
  function saveBook(b) { try { localStorage.setItem(LS, JSON.stringify(b)); } catch (e) {} }
  function wrongSet() { return new Set(Object.keys(loadBook())); }
  function addWrong(id, last) {
    var b = loadBook(); var e = b[id] || { n: 0, last: '', t: 0, bank: /^q\d/.test(id) ? 'quiz' : 'trap' };
    e.n += 1; e.last = last || ''; e.t = Date.now(); b[id] = e; saveBook(b);
  }
  function delWrong(id) { var b = loadBook(); if (b[id]) { delete b[id]; saveBook(b); } }
  window.CIT_WRONGBOOK = { load: loadBook, save: saveBook, add: addWrong, del: delWrong };

  function esc(s) { return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function zhHidden() { try { return localStorage.getItem(LS_ZH) === '1'; } catch (e) { return false; } }
  function setZhHidden(v) { try { localStorage.setItem(LS_ZH, v ? '1' : '0'); } catch (e) {} }

  // Same word rule as word_dict.EN_WORD_RE: Latin script only, so Chinese
  // characters in a mixed line never become tappable "words".
  var WRE = /[A-Za-zÀ-ɏḀ-ỿ](?:[A-Za-zÀ-ɏḀ-ỿ]|['’\-](?=[A-Za-zÀ-ɏḀ-ỿ]))*/g;
  function wrapW(s) {
    s = String(s); var out = '', last = 0, m;
    WRE.lastIndex = 0;
    while ((m = WRE.exec(s)) !== null) {
      out += esc(s.slice(last, m.index)) + '<span class="w">' + esc(m[0]) + '</span>';
      last = m.index + m[0].length;
    }
    return out + esc(s.slice(last));
  }
  // **word** → orange trap mark (trap bank); plain text otherwise
  function wrapTrap(s) {
    return String(s).split('**').map(function(seg, i) {
      return i % 2 ? '<mark class="trap">' + wrapW(seg) + '</mark>' : wrapW(seg);
    }).join('');
  }

  function card(q, n) {
    var order = q.o.map(function(_, i) { return i; });
    if (!q.f) shuffle(order);
    var opts = order.map(function(i, pos) {
      return '<button class="qz-opt" type="button" data-i="' + i + '"><span class="k">' + LETTERS[pos] + '</span>' +
        '<span class="qz-pair"><span class="z">' + esc(q.zo[i]) + '</span>' +
        '<span class="e">' + wrapW(q.o[i]) + '</span></span></button>';
    }).join('');
    var link = q.slug ? '<a href="' + base + 'reading/' + q.slug + '.html#p' + q.p + '">看原文 ↗</a>' : '';
    var book = loadBook(), w = book[q.id];
    var head = '<span class="n">' + n + '</span>' +
      (q.t ? '<span class="qz-type ' + q.t + '">' + (TYPES[q.t] || q.t) + '</span>' : '') +
      '<span>第 ' + q.ch + ' 章 · ' + (CH_NAMES[q.ch] || '') + '</span>' +
      '<span class="id">' + q.id + '</span>' +
      (w && WRONG_ONLY_PAGE ? '<span class="qz-wrongn">錯 ' + w.n + ' 次' + (w.last ? '，上次選 ' + esc(w.last) : '') + '</span>' : '');
    var kw = (q.k && q.k.length) ? '<div class="qz-kw">關鍵字：' + q.k.map(function(p){ return '<span><b>' + esc(p[0]) + '</b> ' + esc(p[1]) + '</span>'; }).join('') + '</div>' : '';
    var tools = '<button class="qz-mini qz-say" data-lang="zh" type="button">🔊 中文</button>' +
      '<button class="qz-mini qz-say" data-lang="en" type="button">🔊 English</button>' +
      '<button class="qz-mini qz-tzh" type="button">遮住中文</button>' +
      (MODE === 'practice' ? '<button class="qz-mini dunno qz-dunno" type="button">我不會</button>' : '') +
      (WRONG_ONLY_PAGE ? '<button class="qz-mini learned qz-learned" type="button">✓ 已學會，移除</button>' : '');
    return '<div class="qz-q" data-id="' + q.id + '" data-ch="' + q.ch + '" data-a="' + q.a + '">' +
      '<div class="qz-head">' + head + '</div>' +
      '<div class="qz-pair"><div class="qz-zh">' + esc(q.zq) + '</div>' +
      '<div class="qz-text">' + wrapTrap(q.q) + '</div></div>' +
      '<div class="qz-opts">' + opts + '</div>' +
      '<div class="qz-tools">' + tools + '</div>' +
      '<div class="qz-ex"><div class="qz-pair"><div class="zh">' + esc(q.ze || q.e || '') + '</div>' +
      (q.ze ? '<div class="en">' + wrapW(q.e) + ' ' + link + '</div>' : (link ? '<div class="en">' + link + '</div>' : '')) +
      '</div>' + kw + '</div></div>';
  }
  function letterOf(qEl, i) {
    var b = qEl.querySelector('.qz-opt[data-i="' + i + '"]');
    return b ? b.querySelector('.k').textContent : '';
  }

  function reveal(qEl, picked) {
    var a = parseInt(qEl.dataset.a, 10);
    qEl.querySelectorAll('.qz-opt').forEach(function(b) {
      b.disabled = true;
      var i = parseInt(b.dataset.i, 10);
      if (i === a) b.classList.add('correct');
      if (i === picked && picked !== a) b.classList.add('wrong');
      if (i === picked) b.classList.add('picked');
    });
    qEl.classList.add('done');
  }
  function answer(qEl, picked, instant) {
    if (qEl.classList.contains('done')) return;
    if (!instant) {
      // exam mode: record the choice only; answers can be changed until submit
      qEl.querySelectorAll('.qz-opt').forEach(function(b){ b.classList.remove('picked'); });
      var chosen = qEl.querySelector('.qz-opt[data-i="' + picked + '"]');
      if (chosen) chosen.classList.add('picked');
      qEl.dataset.picked = picked;
      qEl.classList.add('answered');
      return;
    }
    var ok = picked === parseInt(qEl.dataset.a, 10);
    reveal(qEl, picked);
    qEl.dataset.ok = ok ? '1' : '0';
    if (ok) delWrong(qEl.dataset.id); else addWrong(qEl.dataset.id, letterOf(qEl, picked));
    return ok;
  }
  function dunno(qEl) {
    if (qEl.classList.contains('done')) return;
    reveal(qEl, -1);
    qEl.dataset.ok = '0';
    addWrong(qEl.dataset.id, '不會');
  }

  var list = root.querySelector('.qz-list');
  var status = root.querySelector('.qz-status');

  root.addEventListener('click', function(e) {
    var t = e.target;
    var qEl = t.closest && t.closest('.qz-q');
    if (t.closest('.qz-tzh') && qEl) {
      var hid = qEl.classList.toggle('nozh');
      var tb = t.closest('.qz-tzh');
      tb.classList.toggle('on', hid); tb.textContent = hid ? '顯示中文' : '遮住中文';
      return;
    }
    if (t.closest('.qz-dunno') && qEl) { dunno(qEl); refreshStatus(); return; }
    if (t.closest('.qz-learned') && qEl) {
      delWrong(qEl.dataset.id); qEl.remove(); refreshStatus();
      if (!list.querySelector('.qz-q')) list.innerHTML = '<p class="qz-empty">錯題本清空了，太棒了 🎉</p>';
      return;
    }
    var sayBtn = t.closest && t.closest('.qz-say');
    if (sayBtn && qEl) {
      var lang = sayBtn.dataset.lang || 'en';
      audio.pause();
      audio.src = base + 'audio/quiz/' + lang + '/' + qEl.dataset.id + '.m4a';
      audio.play().catch(function(){});
      audio.onerror = function() {
        if (!window.speechSynthesis) return;
        var q = ALL.find(function(x){ return x.id === qEl.dataset.id; });
        var txt = (lang === 'zh')
          ? q.zq + ' ' + q.zo.map(function(o,i){ return LETTERS[i] + '、' + o; }).join('。')
          : q.q.replace(/\*\*/g, '') + '. ' + q.o.map(function(o,i){ return LETTERS[i] + '. ' + o; }).join('. ');
        var u = new SpeechSynthesisUtterance(txt);
        u.lang = (lang === 'zh') ? 'zh-TW' : 'en-CA'; u.rate = 0.85;
        window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
      };
      return;
    }
    var opt = t.closest && t.closest('.qz-opt');
    if (opt && qEl && !opt.disabled) {
      answer(qEl, parseInt(opt.dataset.i, 10), MODE === 'practice');
      refreshStatus();
    }
  });
  function refreshStatus() { if (MODE === 'practice') updatePracticeStatus(); else updateMockStatus(); }
  function applyZh(on) {
    list.querySelectorAll('.qz-q').forEach(function(q){ q.classList.toggle('nozh', on); });
    list.querySelectorAll('.qz-tzh').forEach(function(b){ b.classList.toggle('on', on); b.textContent = on ? '顯示中文' : '遮住中文'; });
  }

  // ---------------- practice ----------------
  var curCh = 'all', onlyWrong = WRONG_ONLY_PAGE;
  function practicePool() {
    var book = loadBook();
    var qs = ALL.filter(function(q) { return (curCh === 'all' || q.ch === curCh) && (!onlyWrong || book[q.id]); });
    if (WRONG_ONLY_PAGE) qs.sort(function(x, y) { return (book[y.id].n - book[x.id].n) || (book[y.id].t - book[x.id].t); });
    return qs;
  }
  function renderPractice() {
    var qs = practicePool();
    list.innerHTML = qs.length ? qs.map(function(q, i) { return card(q, i + 1); }).join('') :
      '<p class="qz-empty">這個範圍沒有題目' + (onlyWrong ? '（錯題本是空的，太棒了）' : '') + '。</p>';
    var allzh = root.querySelector('.qz-allzh');
    if (allzh && allzh.classList.contains('on')) applyZh(true);
    updatePracticeStatus();
  }
  function updatePracticeStatus() {
    if (!status) return;
    var qs = list.querySelectorAll('.qz-q'), done = list.querySelectorAll('.qz-q.done'), ok = list.querySelectorAll('.qz-q[data-ok="1"]');
    status.textContent = '答了 ' + done.length + ' / ' + qs.length + '，答對 ' + ok.length + '　錯題本 ' + wrongSet().size + ' 題';
  }
  function initPractice() {
    var chips = root.querySelector('.qz-chips');
    if (chips && !chips.dataset.ready) {
      chips.dataset.ready = '1';
      var chs = Array.from(new Set(ALL.map(function(q){ return q.ch; }))).sort();
      chips.innerHTML = '<button class="qz-chip on" data-ch="all" type="button">全部 ' + ALL.length + '</button>' +
        chs.map(function(c){ var n = ALL.filter(function(q){return q.ch===c;}).length; return '<button class="qz-chip" data-ch="' + c + '" type="button">' + c + ' ' + (CH_NAMES[c]||'') + ' ' + n + '</button>'; }).join('');
      chips.addEventListener('click', function(e) {
        var b = e.target.closest('.qz-chip'); if (!b) return;
        chips.querySelectorAll('.qz-chip').forEach(function(x){ x.classList.remove('on'); }); b.classList.add('on');
        curCh = b.dataset.ch; renderPractice();
      });
    }
    var wb = root.querySelector('.qz-wrong');
    if (wb && !wb.dataset.ready) { wb.dataset.ready = '1'; wb.addEventListener('click', function() { onlyWrong = !onlyWrong; this.classList.toggle('on', onlyWrong); renderPractice(); }); }
    var allzh = root.querySelector('.qz-allzh');
    if (allzh && !allzh.dataset.ready) {
      allzh.dataset.ready = '1';
      if (zhHidden()) allzh.classList.add('on');
      allzh.addEventListener('click', function() { this.classList.toggle('on'); var on = this.classList.contains('on'); setZhHidden(on); applyZh(on); });
    }
    var rs = root.querySelector('.qz-reset');
    if (rs && !rs.dataset.ready) { rs.dataset.ready = '1'; rs.addEventListener('click', function() { renderPractice(); window.scrollTo(0, 0); }); }
    var clr = root.querySelector('.qz-clear');
    if (clr && !clr.dataset.ready) {
      clr.dataset.ready = '1';
      clr.addEventListener('click', function() {
        if (!this.classList.contains('armed')) { this.classList.add('armed'); this.textContent = '再按一次確定清空'; var me = this;
          setTimeout(function(){ me.classList.remove('armed'); me.textContent = '清空錯題本'; }, 4000); return; }
        saveBook({}); this.classList.remove('armed'); this.textContent = '清空錯題本'; renderPractice();
      });
    }
    renderPractice();
  }

  // ---------------- mock exam ----------------
  var timerId = null, deadline = 0;
  function fmt(s) { s = Math.max(0, s); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
  function updateMockStatus() {
    if (!status) return;
    var done = list.querySelectorAll('.qz-q.answered').length, tot = list.querySelectorAll('.qz-q').length;
    status.textContent = '已作答 ' + done + ' / ' + tot;
  }
  function startMock() {
    var ont = shuffle(ALL.filter(function(q){ return /^ONTARIO/.test(q.q); })).slice(0, 2);
    var rest = shuffle(ALL.filter(function(q){ return !/^ONTARIO/.test(q.q); })).slice(0, 20 - ont.length);
    var qs = shuffle(ont.concat(rest));
    list.innerHTML = qs.map(function(q, i) { return card(q, i + 1); }).join('');
    // a real test paper is English-only; the Chinese is there as a lifeline, per question
    applyZh(true);
    var paperNo = 1;
    try { paperNo = (parseInt(localStorage.getItem('cit_mock_count') || '0', 10) || 0) + 1; localStorage.setItem('cit_mock_count', String(paperNo)); } catch (e) {}
    var dist = {};
    qs.forEach(function(q){ dist[q.ch] = (dist[q.ch] || 0) + 1; });
    var distText = Object.keys(dist).sort().map(function(c){ return c + '章×' + dist[c]; }).join('　');
    var paper = root.querySelector('.qz-paper');
    if (paper) paper.textContent = '第 ' + paperNo + ' 份考卷（每次隨機重抽 ' + qs.length + ' 題，可無限次）· 本份章節分布：' + distText;
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
      reveal(q, picked);
      q.dataset.ok = good ? '1' : '0';
      if (good) { ok++; delWrong(q.dataset.id); } else addWrong(q.dataset.id, picked < 0 ? '未作答' : letterOf(q, picked));
    });
    var r = root.querySelector('.qz-result');
    var pass = ok >= 15;
    r.innerHTML = '<h2>' + (timeout ? '時間到！' : '交卷') + '</h2><div class="big ' + (pass ? 'pass' : 'fail') + '">' + ok + ' / ' + qs.length + '</div>' +
      '<p>' + (pass ? '通過（15 題以上）🎉' : '未達 15 題，再練一次。') + '　錯的與沒作答的題目已進錯題本，下面每題都有解說。</p>' +
      '<button class="qz-btn main qz-again" type="button">再考一次</button>';
    r.style.display = 'block';
    root.querySelector('.qz-submit').disabled = true;
    r.querySelector('.qz-again').addEventListener('click', startMock);
    r.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function initMock() {
    var b = root.querySelector('.qz-begin'), s = root.querySelector('.qz-submit');
    if (b && !b.dataset.ready) { b.dataset.ready = '1'; b.addEventListener('click', startMock); }
    if (s && !s.dataset.ready) { s.dataset.ready = '1'; s.addEventListener('click', function(){ finishMock(false); }); }
    clearInterval(timerId);
    list.innerHTML = '';
    root.querySelector('.qz-start').style.display = '';
    root.querySelector('.qz-result').style.display = 'none';
    s.disabled = true;
    var tEl = root.querySelector('.qz-timer'); if (tEl) tEl.textContent = '30:00';
    if (status) status.textContent = '';
  }

  // ---------------- mode switch (one page, two modes) ----------------
  function showMode(m) {
    MODE = m;
    root.querySelectorAll('[data-mode]').forEach(function(el){ el.style.display = (el.dataset.mode === m) ? '' : 'none'; });
    root.querySelectorAll('.qz-modes button').forEach(function(b){ b.classList.toggle('on', b.dataset.m === m); });
    if (m === 'practice') initPractice(); else initMock();
    window.scrollTo(0, 0);
  }
  var modes = root.querySelector('.qz-modes');
  if (modes) {
    modes.addEventListener('click', function(e){ var b = e.target.closest('button'); if (b) showMode(b.dataset.m); });
    showMode(MODE);
  } else if (MODE === 'practice') initPractice(); else initMock();
})();
</script>
"""


def _bar_practice(extra_btns: str = "") -> str:
    return ('<div class="qz-bar" data-mode="practice">'
            '<button class="qz-btn qz-allzh" type="button">全部遮住中文（自我測驗）</button>'
            + extra_btns +
            '<button class="qz-btn qz-reset" type="button">重新作答</button>'
            '<span class="qz-status"></span></div><div class="qz-chips" data-mode="practice"></div>')


def _bar_mock() -> str:
    return ('<div class="qz-bar" data-mode="mock"><span class="qz-timer">30:00</span>'
            '<button class="qz-btn main qz-submit" type="button" disabled>交卷</button>'
            '<span class="qz-status"></span></div>'
            '<p class="qz-paper" data-mode="mock" style="font-size:13px;color:var(--muted);margin:0 0 8px"></p>'
            '<div class="qz-start" data-mode="mock"><button class="qz-btn main qz-begin" type="button" style="font-size:18px;padding:12px 28px">開始模擬考</button>'
            '<p>20 題、30 分鐘、答對 15 題通過，跟真考一樣。考卷預設把中文遮起來；卡住時按該題的「顯示中文」，或點單字查字典。</p></div>'
            '<div class="qz-result" data-mode="mock" style="display:none"></div>')


def _page(mode: str, root_id: str, hero: str, inner: str, bank: str, wrong_only: bool = False) -> str:
    return (QUIZ_CSS + f'<div class="qz" id="{root_id}">{hero}{inner}<div class="qz-list"></div></div>'
            + QUIZ_JS.replace("__ROOT__", root_id).replace("__MODE__", mode)
            .replace("__BANK__", bank).replace("__WRONG_ONLY__", "true" if wrong_only else "false")
            .replace("__CH_NAMES__", json.dumps(CHAPTER_NAMES, ensure_ascii=False))
            .replace("__TYPES__", json.dumps(TRAP_TYPES, ensure_ascii=False)))


# ---------------------------------------------------------------- 328 題（原有兩頁）
def build_practice_body() -> str:
    n = len(load_questions())
    hero = f'''<div class="qz-hero"><h1>📝 英文選擇題練習</h1>
<p>{n} 題，格式與真考相同（英文、四選一或是非）。選項每次都會洗牌。中英左右對照、字級一樣；點任何英文單字查字典並聽發音；中英各有一顆朗讀鈕。答錯或按「我不會」的題自動進錯題本。</p></div>'''
    bar = _bar_practice('<button class="qz-btn qz-wrong" type="button">只看錯題本</button>')
    return _page("practice", "qz-practice", hero, bar, "window.CIT_QUIZ")


def build_mock_body() -> str:
    hero = '''<div class="qz-hero"><h1>⏱ 模擬考</h1>
<p>照真考規格：隨機 20 題（含 1–2 題安大略省題）、30 分鐘倒數、答對 15 題通過。作答中不顯示對錯，交卷後才看解說。中文預設遮住，卡住可以逐題打開。</p></div>'''
    return _page("mock", "qz-mock", hero, _bar_mock(), "window.CIT_QUIZ")


# ---------------------------------------------------------------- 陷阱題
def trap_sets() -> list[str]:
    return sorted({q["set"] for q in load_trap_bank_cached()})


def build_trap_set_body(letter: str) -> str:
    qs = [q for q in load_trap_bank_cached() if q["set"] == letter]
    name = SET_NAMES.get(letter, letter)
    from collections import Counter
    types = Counter(q["t"] for q in qs)
    type_line = "、".join(f"{TRAP_TYPES[t]} {n}" for t, n in sorted(types.items(), key=lambda x: -x[1]))
    hero = f'''<div class="qz-hero"><h1>🎯 陷阱題 {name} <small style="font-size:.6em;color:var(--muted);font-weight:400">Set {letter}</small></h1>
<p>{len(qs)} 題，涵蓋全部章節。答案跟你背的一樣，<strong>問法換掉了</strong>——<mark class="trap" style="background:#ffd28a;padding:0 4px;border-radius:3px">橘色字</mark>就是把人騙走的那個字。本套：{type_line}。逐題練習會立刻給對錯、解說、關鍵字；模擬考跟真考一樣 20 題 30 分鐘。</p></div>
<div class="qz-modes"><button type="button" data-m="practice">逐題練習</button><button type="button" data-m="mock">模擬考</button></div>'''
    inner = _bar_practice('<button class="qz-btn qz-wrong" type="button">只看錯題本</button>') + _bar_mock()
    bank = f'window.CIT_TRAP.filter(function(q){{return q.set==="{letter}";}})'
    return _page("practice", f"qz-trap-{letter}", hero, inner, bank)


def build_wrong_body() -> str:
    hero = '''<div class="qz-hero"><h1>📕 錯題本重練</h1>
<p>答錯、按過「我不會」、模擬考沒作答的題目都在這裡，<strong>錯最多次的排最前面</strong>，兩個題庫（328 題＋陷阱題）合在一起。答對一次就自動移出；也可以按「已學會，移除」。<br>
<span style="font-size:12.5px">注意：錯題本存在這台裝置的瀏覽器裡，iPhone、iPad、電腦各自一本，不會互通。</span></p></div>'''
    bar = _bar_practice('<button class="qz-btn danger qz-clear" type="button">清空錯題本</button>')
    bank = "window.CIT_QUIZ.concat(window.CIT_TRAP)"
    return _page("practice", "qz-wrongbook", hero, bar, bank, wrong_only=True)
