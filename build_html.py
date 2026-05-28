"""Convert canada-citizenship-prep markdown files to a clean static HTML site.

Layout:
- bilingual/*.md  → EN | 中 side-by-side
- daily-quiz/*.md → collapsible "答案與解析" section
- curriculum, practice, README → standard rendering
- index.html      → dashboard landing page

Run: python3 build_html.py
"""

from __future__ import annotations
import html
import re
import shutil
from pathlib import Path

import markdown as md

import interactive_content as iv

ROOT = Path(__file__).parent
OUT = ROOT / "html"

MD_EXT = ["extra", "sane_lists", "smarty", "tables"]


# ----------------------------- shared template ----------------------------- #

CSS = r"""
:root {
  --bg: #faf8f4;
  --panel: #ffffff;
  --ink: #1f2328;
  --muted: #5d646d;
  --line: #e7e2d6;
  --accent: #c8102e;        /* maple red */
  --accent-soft: #fbe9ec;
  --en-bg: #f3efe6;
  --en-ink: #2b2620;
  --zh-bg: #ffffff;
  --quote: #8a6d3b;
  --max: 1180px;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: "Source Serif 4","Source Serif Pro","Noto Serif TC","Noto Serif CJK TC","PingFang TC","Songti TC", Georgia, serif;
  font-size: 17px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  max-width: var(--max);
  margin: 0 auto;
  padding: 0 24px;
  gap: 36px;
}
nav.sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  overflow-y: auto;
  padding: 28px 0 40px;
  border-right: 1px solid var(--line);
  font-family: -apple-system, "Helvetica Neue", "PingFang TC", system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.45;
}
nav.sidebar h1 {
  font-family: inherit;
  font-size: 14px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 10px;
}
nav.sidebar h2 {
  font-family: inherit;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 22px 0 6px;
  font-weight: 600;
}
nav.sidebar a {
  display: block;
  color: var(--ink);
  text-decoration: none;
  padding: 4px 10px 4px 0;
  border-radius: 4px;
}
nav.sidebar a:hover { color: var(--accent); }
nav.sidebar a.current {
  color: var(--accent);
  font-weight: 600;
}
nav.sidebar .home {
  display: inline-block;
  font-weight: 700;
  font-size: 18px;
  color: var(--ink);
  text-decoration: none;
  margin-bottom: 14px;
}
nav.sidebar .home::before { content: "🍁 "; }
main {
  padding: 36px 0 80px;
  min-width: 0;
}
main h1, main h2, main h3, main h4 {
  font-family: -apple-system, "Helvetica Neue", "PingFang TC", system-ui, sans-serif;
  line-height: 1.3;
  color: var(--ink);
}
main h1 {
  font-size: 28px;
  margin: 0 0 8px;
  letter-spacing: -0.01em;
}
main > p:first-of-type {
  color: var(--muted);
  margin-top: 4px;
}
main h2 {
  font-size: 21px;
  margin: 40px 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--line);
}
main h3 { font-size: 18px; margin: 28px 0 8px; }
main h4 { font-size: 16px; margin: 22px 0 6px; color: var(--muted); }
main p { margin: 0 0 12px; }
main ul, main ol { margin: 0 0 14px; padding-left: 1.4em; }
main li { margin: 4px 0; }
main hr {
  border: none;
  border-top: 1px solid var(--line);
  margin: 32px 0;
}
main a { color: var(--accent); text-decoration: none; }
main a:hover { text-decoration: underline; }
main code {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.9em;
  background: #f3efe6;
  padding: 1px 5px;
  border-radius: 4px;
}
main blockquote {
  margin: 14px 0;
  padding: 12px 18px;
  background: var(--accent-soft);
  border-left: 3px solid var(--accent);
  color: var(--ink);
  border-radius: 0 6px 6px 0;
}
main blockquote p:last-child { margin-bottom: 0; }
main table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0 22px;
  font-size: 15px;
}
main th, main td {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}
main th {
  background: #f3efe6;
  font-family: -apple-system, "Helvetica Neue", "PingFang TC", system-ui, sans-serif;
  font-weight: 600;
}

/* --- bilingual pairing --- */
.bilingual {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  margin: 14px 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--zh-bg);
}
.bilingual .en, .bilingual .zh {
  padding: 16px 20px;
}
.bilingual .en {
  background: var(--en-bg);
  color: var(--en-ink);
  font-family: "Source Serif 4","Source Serif Pro", Georgia, serif;
  font-style: normal;
  border-right: 1px solid var(--line);
}
.bilingual .en p, .bilingual .zh p { margin: 0 0 8px; }
.bilingual .en p:last-child, .bilingual .zh p:last-child { margin-bottom: 0; }
.bilingual .en ul, .bilingual .en ol,
.bilingual .zh ul, .bilingual .zh ol {
  margin: 0 0 6px;
  padding-left: 1.3em;
}
.bilingual .en em { font-style: italic; }
.bilingual .label {
  display: inline-block;
  font-family: -apple-system, "Helvetica Neue", system-ui, sans-serif;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 6px;
  font-weight: 600;
}

/* --- callouts (⚠️ blocks) --- */
.callout {
  margin: 18px 0;
  padding: 14px 18px;
  background: #fff8e1;
  border-left: 4px solid #f0a500;
  border-radius: 0 6px 6px 0;
}
.callout p { margin: 0 0 6px; }
.callout p:last-child { margin: 0; }

/* --- collapsible answers --- */
details.answers {
  margin: 22px 0;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0;
  overflow: hidden;
}
details.answers > summary {
  cursor: pointer;
  padding: 14px 18px;
  font-family: -apple-system, "Helvetica Neue", "PingFang TC", system-ui, sans-serif;
  font-weight: 600;
  font-size: 16px;
  background: #f3efe6;
  border-bottom: 1px solid transparent;
  user-select: none;
  list-style: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
details.answers > summary::-webkit-details-marker { display: none; }
details.answers > summary::after {
  content: "▸";
  color: var(--muted);
  transition: transform 0.18s ease;
  font-size: 14px;
}
details.answers[open] > summary {
  border-bottom-color: var(--line);
}
details.answers[open] > summary::after { transform: rotate(90deg); }
details.answers .answers-body { padding: 14px 22px 6px; }
details.answers .answers-body ol { margin: 0; padding-left: 1.4em; }
details.answers .answers-body li { margin: 8px 0; }

/* --- dashboard cards on index --- */
.dash {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin: 24px 0;
}
.dash a {
  display: block;
  padding: 18px 20px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--ink);
  text-decoration: none;
  transition: border-color 0.15s, transform 0.15s;
}
.dash a:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
}
.dash a .kicker {
  font-family: -apple-system, system-ui, sans-serif;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  display: block;
  margin-bottom: 6px;
}
.dash a .title {
  font-weight: 600;
  font-size: 17px;
  line-height: 1.35;
}
.dash a .meta {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: var(--muted);
  font-family: -apple-system, system-ui, sans-serif;
}

/* --- speak (TTS) button --- */
.speak-btn {
  appearance: none;
  background: rgba(255,255,255,0.85);
  border: 1px solid var(--line);
  color: var(--muted);
  cursor: pointer;
  padding: 4px 9px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-family: -apple-system, "Helvetica Neue", system-ui, sans-serif;
  transition: all 0.15s;
  -webkit-tap-highlight-color: transparent;
  min-width: 64px;
  justify-content: center;
}
.speak-btn .speak-icon { display: inline-flex; }
.speak-btn svg { display: block; }
.speak-btn:hover { color: var(--accent); border-color: var(--accent); }
.speak-btn:active { transform: scale(0.96); }
.speak-btn.speaking {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  animation: speak-pulse 1.4s ease-in-out infinite;
}
.speak-btn.paused {
  background: #f0a500;
  color: #fff;
  border-color: #f0a500;
  animation: none;
}
@keyframes speak-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(200,16,46,0.5); }
  50%      { box-shadow: 0 0 0 6px rgba(200,16,46,0); }
}

/* --- per-word highlight during TTS + click-to-play-from-here --- */
.w {
  border-radius: 3px;
  padding: 0 1px;
  transition: color 0.08s ease, background 0.08s ease;
  cursor: pointer;
  -webkit-tap-highlight-color: rgba(200, 16, 46, 0.15);
}
.w:hover {
  background: rgba(200, 16, 46, 0.07);
  text-decoration: underline;
  text-decoration-color: rgba(200, 16, 46, 0.3);
  text-decoration-style: dotted;
  text-underline-offset: 3px;
}
.w.current {
  color: var(--accent);
  background: rgba(200, 16, 46, 0.14);
  font-weight: 600;
  text-decoration: none;
}
.bilingual .en { position: relative; }
.bilingual .en > .speak-btn {
  position: absolute;
  top: 12px;
  right: 12px;
}
.bilingual .en > .label + .speak-btn { /* fallback positioning if absolute fails */ }
blockquote.speakable, .callout.speakable {
  position: relative;
  padding-right: 60px;
}
blockquote.speakable > .speak-btn,
.callout.speakable > .speak-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fff;
}

/* --- mobile --- */
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; padding: 0 16px; gap: 0; }
  nav.sidebar {
    position: static;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--line);
    padding: 18px 0;
  }
  .bilingual { grid-template-columns: 1fr; }
  .bilingual .en { border-right: none; border-bottom: 1px solid var(--line); }
}

/* --- print --- */
@media print {
  nav.sidebar { display: none; }
  .layout { display: block; padding: 0; }
  main { padding: 0; }
  details.answers { border: 1px solid #999; }
  details.answers > summary { display: none; }
  details.answers > .answers-body { display: block !important; }
  .bilingual { break-inside: avoid; }
}
"""


def make_sidebar(current: str) -> str:
    """current is the relative path from html/ root, e.g. 'bilingual/00-intro-oath.html'."""
    def link(href: str, label: str, key: str) -> str:
        cls = ' class="current"' if current == key else ""
        return f'<a href="{href}"{cls}>{label}</a>'

    bilingual_items = [
        ("00-intro-oath.html", "00 · 前言＋誓詞"),
        ("01-applying-citizenship.html", "01 · 申請入籍"),
        ("02-rights-responsibilities.html", "02 · 權利與義務"),
        ("03-who-we-are.html", "03 · 我們是誰"),
        ("04-canadas-history.html", "04 · 加拿大歷史"),
        ("05-modern-canada.html", "05 · 現代加拿大"),
        ("06-how-canadians-govern.html", "06 · 政府架構"),
        ("07-federal-elections.html", "07 · 聯邦選舉"),
        ("08-justice-system.html", "08 · 司法系統"),
        ("09-canadian-symbols.html", "09 · 國家象徵"),
        ("10-canadas-economy.html", "10 · 加拿大經濟"),
        ("11-canadas-regions.html", "11 · 五大區域"),
        ("12-study-questions.html", "12 · 官方練習題"),
    ]
    quiz_items = [(f"day-{i:02d}.html", f"Day {i:02d}") for i in range(1, 15)]

    # path prefix depending on current depth
    depth = current.count("/")
    up = "../" * depth
    home = up + "index.html"

    parts = [f'<a href="{home}" class="home">加拿大公民考試</a>']
    parts.append(f'<a href="{up}curriculum/14-day-plan.html"' +
                 (' class="current"' if current == "curriculum/14-day-plan.html" else "") +
                 ">📅 14 天計畫表</a>")
    parts.append(f'<a href="{up}practice/question-bank.html"' +
                 (' class="current"' if current == "practice/question-bank.html" else "") +
                 ">📝 220 題題庫</a>")

    parts.append('<h2>中英對照（13 章）</h2>')
    for fn, label in bilingual_items:
        key = f"bilingual/{fn}"
        cls = ' class="current"' if current == key else ""
        parts.append(f'<a href="{up}bilingual/{fn}"{cls}>{label}</a>')

    parts.append('<h2>每日驗收（14 天）</h2>')
    for fn, label in quiz_items:
        key = f"daily-quiz/{fn}"
        cls = ' class="current"' if current == key else ""
        parts.append(f'<a href="{up}daily-quiz/{fn}"{cls}>{label}</a>')

    parts.append('<h2>互動式（圖解）</h2>')
    for fn, label in INTERACTIVE_ITEMS:
        key = f"interactive/{fn}"
        cls = ' class="current"' if current == key else ""
        parts.append(f'<a href="{up}interactive/{fn}"{cls}>{label}</a>')

    return '<nav class="sidebar">\n' + "\n".join(parts) + "\n</nav>"


INTERACTIVE_ITEMS = [
    ("index.html", "🎯 互動式入口"),
    ("geography.html", "🗺️ 地圖：13 省領地"),
    ("history.html", "📜 時間軸"),
    ("government.html", "🏛️ 政府架構圖"),
    ("symbols.html", "🍁 國家象徵圖鑑"),
]


SPEAK_JS = r"""
(function() {
  if (!('speechSynthesis' in window)) return;
  var synth = window.speechSynthesis;
  var voicesReady = false;

  var ICON_SPEAKER = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 10v4h4l5 4V6L7 10H3zm12.5 2c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM13 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
  var ICON_PAUSE = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';
  var ICON_PLAY = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';

  // single global state — only one TTS session at a time
  var state = {
    btn: null, chunks: null, words: null, chunkIdx: 0, paused: false
  };

  function ensureVoices(cb) {
    if (voicesReady) return cb();
    var v = synth.getVoices();
    if (v && v.length) { voicesReady = true; return cb(); }
    synth.onvoiceschanged = function() { voicesReady = true; cb(); };
    setTimeout(function(){ if (!voicesReady) { voicesReady = true; cb(); } }, 500);
  }

  function pickVoice() {
    var voices = synth.getVoices();
    function find(pred){ for (var i=0;i<voices.length;i++) if (pred(voices[i])) return voices[i]; return null; }
    return find(function(v){return v.lang==='en-CA' && /Samantha|Karen|Tessa|Victoria|Allison|Siri/i.test(v.name);})
        || find(function(v){return v.lang==='en-CA';})
        || find(function(v){return v.lang==='en-US' && /Samantha|Karen|Allison|Ava|Siri/i.test(v.name);})
        || find(function(v){return v.lang==='en-US';})
        || find(function(v){return v.lang && v.lang.indexOf('en')===0;})
        || null;
  }

  // Wrap each word in container in a <span class="w" data-idx="N"> for highlighting.
  function wrapWords(container) {
    if (container.dataset.wrapped === '1') return;
    var walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
    var nodes = [];
    var n;
    while ((n = walker.nextNode())) {
      if (!n.parentElement) continue;
      if (n.parentElement.closest('.speak-btn, .label')) continue;
      if (!/\S/.test(n.nodeValue)) continue;
      nodes.push(n);
    }
    var idx = 0;
    nodes.forEach(function(tn) {
      var text = tn.nodeValue;
      var tokens = text.split(/(\s+)/);
      var frag = document.createDocumentFragment();
      tokens.forEach(function(tok) {
        if (tok.length === 0) return;
        if (/^\s+$/.test(tok)) {
          frag.appendChild(document.createTextNode(tok));
        } else {
          var sp = document.createElement('span');
          sp.className = 'w';
          sp.setAttribute('data-idx', idx++);
          sp.textContent = tok;
          frag.appendChild(sp);
        }
      });
      tn.parentNode.replaceChild(frag, tn);
    });
    container.dataset.wrapped = '1';
  }

  // Group words into chunks split on punctuation, with a pause duration after each chunk.
  function buildChunks(words) {
    var chunks = [];
    var cur = { words: [] };
    function commit(pauseMs) {
      if (!cur.words.length) return;
      cur.text = cur.words.map(function(w){ return w.text; }).join(' ');
      cur.pauseAfterMs = pauseMs;
      chunks.push(cur);
      cur = { words: [] };
    }
    words.forEach(function(wEl, i) {
      var text = wEl.textContent;
      cur.words.push({ el: wEl, idx: i, text: text });
      // sentence-ending punctuation → long pause
      if (/[.!?]+["')\]]*$/.test(text) && text.length > 1) {
        commit(420);
      }
      // semicolon / colon → medium pause
      else if (/[;:]+["')\]]*$/.test(text)) {
        commit(300);
      }
      // comma or em-dash → short pause
      else if (/[,—–][")'\]]*$/.test(text)) {
        commit(220);
      }
    });
    commit(0);
    return chunks;
  }

  function highlight(globalIdx) {
    if (!state.words) return;
    for (var i = 0; i < state.words.length; i++) {
      if (i === globalIdx) state.words[i].classList.add('current');
      else state.words[i].classList.remove('current');
    }
  }

  function clearHighlight() {
    if (!state.words) return;
    state.words.forEach(function(w){ w.classList.remove('current'); });
  }

  function findWordAtChar(chunk, charIndex) {
    var pos = 0;
    for (var i = 0; i < chunk.words.length; i++) {
      var len = chunk.words[i].text.length;
      if (charIndex >= pos && charIndex < pos + len) return i;
      pos += len + 1; // space
    }
    return -1;
  }

  function setBtnState(btn, s) {
    if (!btn) return;
    btn.classList.remove('speaking', 'paused');
    if (s === 'speaking') btn.classList.add('speaking');
    else if (s === 'paused') btn.classList.add('paused');
    btn.setAttribute('data-state', s);
    var icon = btn.querySelector('.speak-icon');
    var label = btn.querySelector('.speak-label');
    if (s === 'idle')     { if (icon) icon.innerHTML = ICON_SPEAKER; if (label) label.textContent = '朗讀'; }
    else if (s === 'speaking') { if (icon) icon.innerHTML = ICON_PAUSE;   if (label) label.textContent = '暫停'; }
    else if (s === 'paused')   { if (icon) icon.innerHTML = ICON_PLAY;    if (label) label.textContent = '繼續'; }
  }

  function stopAll() {
    state.suppressNextEnd = true;  // ignore the cancel-induced end/error
    synth.cancel();
    if (state.btn) setBtnState(state.btn, 'idle');
    clearHighlight();
    state.btn = null; state.chunks = null; state.words = null;
    state.chunkIdx = 0; state.paused = false;
    // reset suppression on next tick
    setTimeout(function(){ state.suppressNextEnd = false; }, 100);
  }

  function findChunkForWord(chunks, wordIdx) {
    for (var i = 0; i < chunks.length; i++) {
      for (var j = 0; j < chunks[i].words.length; j++) {
        if (chunks[i].words[j].idx === wordIdx) return i;
      }
    }
    return -1;
  }

  function speakFrom(chunkIdx) {
    if (!state.chunks || chunkIdx >= state.chunks.length) { stopAll(); return; }
    state.chunkIdx = chunkIdx;
    var chunk = state.chunks[chunkIdx];
    var u = new SpeechSynthesisUtterance(chunk.text);
    u.lang = 'en-CA';
    u.rate = 0.92;
    u.pitch = 1.0;
    var v = pickVoice();
    if (v) u.voice = v;

    u.onstart = function() {
      if (chunk.words[0]) highlight(chunk.words[0].idx);
    };
    u.onboundary = function(e) {
      if (e.name && e.name !== 'word') return;
      var w = findWordAtChar(chunk, e.charIndex || 0);
      if (w >= 0) highlight(chunk.words[w].idx);
    };
    u.onend = function() {
      // ignore the end event if it was triggered by our own cancel (pause/jump/stop)
      if (state.suppressNextEnd) { state.suppressNextEnd = false; return; }
      if (state.paused) return;
      var next = chunkIdx + 1;
      if (next >= state.chunks.length) { stopAll(); return; }
      setTimeout(function() {
        if (!state.paused && state.chunks) speakFrom(next);
      }, chunk.pauseAfterMs);
    };
    u.onerror = function() {
      if (state.suppressNextEnd) { state.suppressNextEnd = false; return; }
      if (state.paused) return; // user paused — keep state for resume
      stopAll();
    };

    synth.speak(u);
  }

  // Start fresh speech for a container, optionally from a specific chunk index.
  function startFresh(container, btn, fromChunk) {
    stopAll();
    wrapWords(container);
    var words = Array.prototype.slice.call(container.querySelectorAll('.w'));
    if (!words.length) return;
    state.btn = btn;
    state.words = words;
    state.chunks = buildChunks(words);
    state.chunkIdx = Math.max(0, Math.min(fromChunk || 0, state.chunks.length - 1));
    state.paused = false;
    setBtnState(btn, 'speaking');
    speakFrom(state.chunkIdx);
  }

  // Jump speech to a specific word — restart the chunk containing it.
  function jumpToWord(container, btn, wordIdx) {
    // Same container that's currently speaking/paused → in-place jump
    if (state.btn === btn && state.chunks && state.words) {
      var ci = findChunkForWord(state.chunks, wordIdx);
      if (ci < 0) return;
      state.suppressNextEnd = true;
      synth.cancel();
      state.chunkIdx = ci;
      state.paused = false;
      setBtnState(btn, 'speaking');
      setTimeout(function() {
        state.suppressNextEnd = false;
        if (state.chunks) speakFrom(ci);
      }, 60);
      return;
    }
    // Different container or fresh start — figure out chunk first
    wrapWords(container);
    var words = Array.prototype.slice.call(container.querySelectorAll('.w'));
    if (!words.length) return;
    var chunks = buildChunks(words);
    var ci2 = findChunkForWord(chunks, wordIdx);
    startFresh(container, btn, ci2 >= 0 ? ci2 : 0);
  }

  function speakableContainerOf(el) {
    return el.closest && el.closest('.bilingual .en, blockquote.speakable, .callout.speakable');
  }

  document.addEventListener('click', function(e) {
    // --- speak button ---
    var btn = e.target.closest && e.target.closest('.speak-btn');
    if (btn) {
      e.preventDefault();
      var s = btn.getAttribute('data-state') || 'idle';
      if (s === 'speaking') {
        // pause: set flag BEFORE cancel so onend/onerror preserve state
        state.paused = true;
        synth.cancel();
        setBtnState(btn, 'paused');
        return;
      }
      if (s === 'paused') {
        // resume: restart current chunk
        state.paused = false;
        setBtnState(btn, 'speaking');
        if (state.chunks) speakFrom(state.chunkIdx);
        return;
      }
      // idle → new speech from start
      ensureVoices(function() { startFresh(btn.parentElement, btn, 0); });
      return;
    }

    // --- word click (play from here) ---
    var w = e.target.closest && e.target.closest('.w');
    if (!w) return;
    // skip if user is selecting text
    var sel = window.getSelection && window.getSelection();
    if (sel && sel.toString && sel.toString().length > 0) return;
    var container = speakableContainerOf(w);
    if (!container) return;
    var speakBtn = container.querySelector('.speak-btn');
    if (!speakBtn) return;
    e.preventDefault();
    var widx = parseInt(w.getAttribute('data-idx'), 10);
    if (isNaN(widx)) return;
    ensureVoices(function() { jumpToWord(container, speakBtn, widx); });
  });

  // Pre-wrap all speakable containers during idle time so word-click works without first hitting the button
  function preWrapAll() {
    var containers = document.querySelectorAll('.bilingual .en, blockquote.speakable, .callout.speakable');
    var i = 0;
    function step() {
      if (i >= containers.length) return;
      try { wrapWords(containers[i]); } catch (e) {}
      i++;
      if (window.requestIdleCallback) requestIdleCallback(step, { timeout: 200 });
      else setTimeout(step, 0);
    }
    step();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', preWrapAll);
  else preWrapAll();

  window.addEventListener('hashchange', stopAll);
  window.addEventListener('pagehide', stopAll);
})();
"""

SPEAKER_SVG_INITIAL = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M3 10v4h4l5 4V6L7 10H3zm12.5 2c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM13 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>'
    '</svg>'
)

SPEAK_BTN_HTML = (
    '<button class="speak-btn" type="button" aria-label="朗讀英文" '
    'title="朗讀英文 / Read aloud" data-state="idle">'
    f'<span class="speak-icon">{SPEAKER_SVG_INITIAL}</span>'
    '<span class="speak-label">朗讀</span>'
    '</button>'
)


def wrap_page(title: str, body: str, current: str) -> str:
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="加拿大公民考">
<meta name="theme-color" content="#c8102e">
<title>{html.escape(title)} · 加拿大公民考試</title>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
{make_sidebar(current)}
<main>{body}</main>
</div>
<script>{SPEAK_JS}</script>
</body>
</html>
"""


# --------------------------- markdown helpers --------------------------- #

def md_to_html(text: str) -> str:
    return md.markdown(text, extensions=MD_EXT, output_format="html5")


BLOCKQUOTE_LINE = re.compile(r"^>\s?(.*)$")


def split_blocks(text: str) -> list[str]:
    """Split markdown into block-level chunks separated by blank lines."""
    blocks = []
    cur: list[str] = []
    for line in text.split("\n"):
        if line.strip() == "":
            if cur:
                blocks.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def classify(block: str) -> str:
    s = block.lstrip()
    if s.startswith("#"):
        return "heading"
    if s.startswith("---") and set(s.strip()) <= {"-"}:
        return "hr"
    if s.startswith("|"):
        return "table"
    if s.startswith("> "):
        # could be callout (⚠️) or English blockquote
        first_inner = s.split("\n", 1)[0][2:].lstrip()
        if first_inner.startswith("⚠️") or first_inner.startswith("⚠"):
            return "callout"
        return "blockquote"
    if s.startswith(">"):
        return "blockquote"
    return "para"


def strip_bq_prefix(block: str) -> str:
    out_lines = []
    for line in block.split("\n"):
        m = BLOCKQUOTE_LINE.match(line)
        out_lines.append(m.group(1) if m else line)
    return "\n".join(out_lines)


def ensure_list_breaks(text: str) -> str:
    """Insert a blank line before the first list item in a paragraph so markdown parses it as a list."""
    lines = text.split("\n")
    out: list[str] = []
    prev_is_list = False
    for line in lines:
        is_list = bool(re.match(r"^\s*([-*+]|\d+\.)\s", line))
        if is_list and not prev_is_list and out and out[-1].strip() != "":
            out.append("")
        out.append(line)
        prev_is_list = is_list
    return "\n".join(out)


def looks_like_english(text: str) -> bool:
    """True if the blockquote content is predominantly English (a translation source)."""
    en_letters = len(re.findall(r"[A-Za-z]", text))
    cjk = len(re.findall(r"[一-鿿]", text))
    return en_letters >= 30 and en_letters > cjk * 3


def render_bilingual(md_path: Path) -> str:
    """Render bilingual chapter.

    Rules:
    - English-looking blockquote → pair with the following ZH blocks (paragraph + optional list/sub-blocks)
      until the next blockquote / heading / hr.
    - Chinese-looking blockquote (metadata, callouts) → render as a standalone styled block.
    """
    text = md_path.read_text(encoding="utf-8")
    blocks = split_blocks(text)
    out: list[str] = []

    i = 0
    while i < len(blocks):
        b = blocks[i]
        kind = classify(b)

        if kind == "heading":
            out.append(md_to_html(b))
            i += 1
            continue
        if kind == "hr":
            out.append("<hr>")
            i += 1
            continue
        if kind == "callout":
            inner = strip_bq_prefix(b)
            out.append(f'<div class="callout">{md_to_html(inner)}</div>')
            i += 1
            continue
        if kind == "table":
            out.append(md_to_html(b))
            i += 1
            continue
        if kind == "blockquote":
            inner = strip_bq_prefix(b)

            # Chinese-only blockquote → not a translation pair, render standalone
            if not looks_like_english(inner):
                out.append(f'<div class="callout">{md_to_html(ensure_list_breaks(inner))}</div>')
                i += 1
                continue

            # English source → consume following non-structural blocks as ZH translation
            en_text = ensure_list_breaks(inner)
            j = i + 1
            zh_blocks: list[str] = []
            while j < len(blocks):
                nxt_kind = classify(blocks[j])
                if nxt_kind in ("heading", "hr", "blockquote", "callout"):
                    break
                zh_blocks.append(blocks[j])
                j += 1

            en_html = md_to_html(en_text)
            if zh_blocks:
                zh_text = "\n\n".join(zh_blocks)
                zh_html = md_to_html(zh_text)
            else:
                zh_html = '<p style="color:#888">（未提供翻譯）</p>'

            out.append(
                f'<div class="bilingual">'
                f'<div class="en"><span class="label">English</span>{SPEAK_BTN_HTML}{en_html}</div>'
                f'<div class="zh"><span class="label">中文</span>{zh_html}</div>'
                f'</div>'
            )
            i = j
            continue

        # plain paragraph or list at top level (not preceded by blockquote)
        out.append(md_to_html(b))
        i += 1

    return "\n".join(out)


def render_daily_quiz(md_path: Path) -> str:
    """Convert daily-quiz file; wrap '## 答案與解析' section in <details>."""
    text = md_path.read_text(encoding="utf-8")
    # Split at "## 答案與解析"
    m = re.search(r"^## 答案與解析\s*$", text, re.MULTILINE)
    if not m:
        return md_to_html(text)

    pre = text[: m.start()]
    rest = text[m.end():]

    # Find next "## " heading or end
    m2 = re.search(r"^## ", rest, re.MULTILINE)
    if m2:
        ans = rest[: m2.start()]
        post = rest[m2.start():]
    else:
        ans = rest
        post = ""

    pre_html = md_to_html(pre)
    ans_html = md_to_html(ans)
    post_html = md_to_html(post) if post else ""

    detail = (
        '<details class="answers">'
        '<summary>答案與解析（點擊展開）</summary>'
        f'<div class="answers-body">{ans_html}</div>'
        '</details>'
    )
    return pre_html + "\n" + detail + "\n" + post_html


def render_plain(md_path: Path) -> str:
    return md_to_html(md_path.read_text(encoding="utf-8"))


def add_speak_to_english_blockquotes(html_str: str) -> str:
    """Find <blockquote> elements with predominantly English content and inject a speak button."""
    def repl(m: re.Match) -> str:
        inner = m.group(1)
        text = re.sub(r"<[^>]+>", "", inner)
        if looks_like_english(text):
            return f'<blockquote class="speakable">{SPEAK_BTN_HTML}{inner}</blockquote>'
        return m.group(0)
    return re.sub(r"<blockquote>(.*?)</blockquote>", repl, html_str, flags=re.S)


def rewrite_md_links(html_str: str) -> str:
    """Rewrite .md links to .html and adjust relative paths."""
    def repl(m: re.Match) -> str:
        href = m.group(1)
        # Skip absolute URLs and anchors
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        new = href.replace(".md", ".html")
        return f'href="{new}"'
    return re.sub(r'href="([^"]+)"', repl, html_str)


def title_from_md(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem


# ----------------------------- index page ----------------------------- #

INDEX_INTRO = """
<h1>加拿大公民考試 · 學習中心</h1>
<p>對照 IRCC 官方《Discover Canada》（2024-12-18 最新版本），14 天衝刺到考試合格。</p>

<h2>從這裡開始</h2>
<div class="dash">
  <a href="curriculum/14-day-plan.html">
    <span class="kicker">總覽</span>
    <span class="title">14 天計畫表</span>
    <span class="meta">每日主題、驗收門檻、進度儀表板</span>
  </a>
  <a href="daily-quiz/day-01.html">
    <span class="kicker">今天 · Day 1</span>
    <span class="title">入籍誓詞＋權利義務</span>
    <span class="meta">PDF p.2–9 · 20 題驗收 · 通過 15/20</span>
  </a>
  <a href="bilingual/00-intro-oath.html">
    <span class="kicker">對照精讀</span>
    <span class="title">中英對照原文（13 章）</span>
    <span class="meta">EN 左 · 中 右 · 逐段對照</span>
  </a>
  <a href="practice/question-bank.html">
    <span class="kicker">考前衝刺</span>
    <span class="title">220+ 題題庫</span>
    <span class="meta">依章節分類，反覆練習弱點</span>
  </a>
</div>

<h2>考試規格速覽</h2>
<table>
<tr><th>項目</th><th>內容</th></tr>
<tr><td>題型</td><td>選擇題 + 是非題</td></tr>
<tr><td>題數</td><td>20 題（含 Ontario 省題）</td></tr>
<tr><td>通過分數</td><td><strong>15 / 20（75%）</strong></td></tr>
<tr><td>作答時間</td><td>30 分鐘</td></tr>
<tr><td>題目來源</td><td><strong>全部</strong>出自 Discover Canada</td></tr>
<tr><td>考試語言</td><td>英文或法文（自選）</td></tr>
</table>

<h2>每日 14 天</h2>
<div class="dash">
"""

DAY_TOPICS = [
    ("Day 01", "入籍誓詞＋權利與義務", "Oath · 6 大責任 · 4 大自由"),
    ("Day 02", "我們是誰", "三大開國民族 · 3 類原住民"),
    ("Day 03", "歷史 ① 早期—英法戰爭", "維京人 · 卡帝亞 · 1759 亞伯拉罕"),
    ("Day 04", "歷史 ② 1812—邦聯 1867", "1812 戰爭 · Macdonald · 邦聯四省"),
    ("Day 05", "歷史 ③ 邦聯後—WWII", "太平洋鐵路 · Vimy Ridge"),
    ("Day 06", "現代加拿大＋憲章 1982", "戰後移民 · 雙語法 · 1982 憲章"),
    ("Day 07", "週一模擬考", "Day 1–6 綜合 · 40 題 · 通過 30/40"),
    ("Day 08", "政府架構", "君主立憲 · 3 級政府 · 國會 3 部分"),
    ("Day 09", "聯邦選舉＋立法", "5 大政黨 · 4 年任期 · 法案三讀"),
    ("Day 10", "司法系統", "無罪推定 · 陪審 · 4 級法院 · RCMP"),
    ("Day 11", "象徵＋國歌＋國定假日", "國旗 1965 · 楓葉 · 11 國定假日"),
    ("Day 12", "加拿大經濟", "3 大產業 · CUSMA · G7 / G20"),
    ("Day 13", "五大區域與省份（含 Ontario）", "10 省 3 領地 · 首府 · 省題加強"),
    ("Day 14", "期末模擬考", "真實考試模擬：20 題 / 30 分鐘 / 不翻書"),
]


def build_index_body() -> str:
    parts = [INDEX_INTRO]
    for i, (day, title, meta) in enumerate(DAY_TOPICS, start=1):
        parts.append(
            f'<a href="daily-quiz/day-{i:02d}.html">'
            f'<span class="kicker">{day}</span>'
            f'<span class="title">{title}</span>'
            f'<span class="meta">{meta}</span>'
            f'</a>'
        )
    parts.append("</div>")
    return "\n".join(parts)


# ----------------------------- single-file build ----------------------------- #

SINGLE_CSS_EXTRA = r"""
/* SPA-style section switching via pure CSS :target — works without JavaScript */
main > .page { display: none; }
main > .page#home { display: block; }
main > .page:target { display: block; }
/* Hide home when another section is targeted (requires :has, modern Safari/iOS 15.4+) */
@supports selector(:has(*)) {
  main:has(> .page:target:not(#home)) > #home { display: none; }
}
main > .page { scroll-margin-top: 16px; }
nav.sidebar { font-size: 13px; }
nav.sidebar a:target,
nav.sidebar a[href="#home"] { /* no-op, kept for future */ }
"""

SINGLE_ROUTER_JS = r"""
/* Optional enhancement: cancel ongoing speech and scroll-to-top on section change.
   Navigation itself works without JS (via :target). */
(function() {
  window.addEventListener('hashchange', function() {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    document.querySelectorAll('.speak-btn.speaking').forEach(function(b){ b.classList.remove('speaking'); });
  });
  // Highlight current sidebar link on hash change
  function syncSidebar() {
    var hash = location.hash || '#home';
    document.querySelectorAll('nav.sidebar a').forEach(function(a) {
      a.classList.toggle('current', a.getAttribute('href') === hash);
    });
  }
  window.addEventListener('hashchange', syncSidebar);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', syncSidebar);
  else syncSidebar();
})();
"""


def section_id(rel_path: str) -> str:
    """bilingual/02-foo.html → bilingual-02-foo"""
    return rel_path.replace(".html", "").replace("/", "-")


def rewrite_links_to_hash(html_str: str, current_dir: str) -> str:
    """Rewrite href links to use #hash navigation within single-file build.

    current_dir is the dir of the current page relative to OUT, e.g. 'bilingual' or '' for index.
    """
    def repl(m: re.Match) -> str:
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        # Resolve relative path
        if href.startswith("../"):
            # parent-relative
            parts = href.split("/")
            depth_up = sum(1 for p in parts if p == "..")
            rest = "/".join(p for p in parts if p != "..")
            base_parts = current_dir.split("/") if current_dir else []
            base_parts = base_parts[: max(0, len(base_parts) - depth_up)]
            resolved = "/".join(base_parts + [rest]) if base_parts else rest
        elif "/" in href:
            resolved = href if current_dir == "" else f"{current_dir}/{href}"
        else:
            resolved = f"{current_dir}/{href}" if current_dir else href
        if resolved.endswith(".html"):
            return f'href="#{section_id(resolved)}"'
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, html_str)


def make_single_sidebar() -> str:
    bilingual_items = [
        ("00-intro-oath", "00 · 前言＋誓詞"),
        ("01-applying-citizenship", "01 · 申請入籍"),
        ("02-rights-responsibilities", "02 · 權利與義務"),
        ("03-who-we-are", "03 · 我們是誰"),
        ("04-canadas-history", "04 · 加拿大歷史"),
        ("05-modern-canada", "05 · 現代加拿大"),
        ("06-how-canadians-govern", "06 · 政府架構"),
        ("07-federal-elections", "07 · 聯邦選舉"),
        ("08-justice-system", "08 · 司法系統"),
        ("09-canadian-symbols", "09 · 國家象徵"),
        ("10-canadas-economy", "10 · 加拿大經濟"),
        ("11-canadas-regions", "11 · 五大區域"),
        ("12-study-questions", "12 · 官方練習題"),
    ]
    quiz_items = [(f"day-{i:02d}", f"Day {i:02d}") for i in range(1, 15)]
    interactive_items = [
        ("index", "🎯 互動式入口"),
        ("geography", "🗺️ 地圖"),
        ("history", "📜 時間軸"),
        ("government", "🏛️ 政府架構"),
        ("symbols", "🍁 象徵圖鑑"),
    ]

    parts = ['<nav class="sidebar">']
    parts.append('<a href="#home" class="home">加拿大公民考試</a>')
    parts.append('<a href="#curriculum-14-day-plan">📅 14 天計畫表</a>')
    parts.append('<a href="#practice-question-bank">📝 220 題題庫</a>')
    parts.append('<h2>中英對照（13 章）</h2>')
    for slug, label in bilingual_items:
        parts.append(f'<a href="#bilingual-{slug}">{label}</a>')
    parts.append('<h2>每日驗收（14 天）</h2>')
    for slug, label in quiz_items:
        parts.append(f'<a href="#daily-quiz-{slug}">{label}</a>')
    parts.append('<h2>互動式（圖解）</h2>')
    for slug, label in interactive_items:
        parts.append(f'<a href="#interactive-{slug}">{label}</a>')
    parts.append('</nav>')
    return "\n".join(parts)


def build_single():
    """Build a single self-contained study.html with hash-based navigation."""
    sections: list[str] = []

    # index → #home
    index_body = build_index_body()
    # rewrite the index page's dashboard cards to hash links
    index_body = rewrite_links_to_hash(index_body, "")
    sections.append(f'<section id="home" class="page">{index_body}</section>')

    def add_section(rel: str, body: str):
        body = add_speak_to_english_blockquotes(body)
        cur_dir = "/".join(rel.split("/")[:-1])
        body = rewrite_links_to_hash(body, cur_dir)
        sid = section_id(rel)
        sections.append(f'<section id="{sid}" class="page">{body}</section>')

    # bilingual
    for md_file in sorted((ROOT / "bilingual").glob("*.md")):
        if md_file.name == "README.md":
            body = render_plain(md_file)
        else:
            body = render_bilingual(md_file)
        add_section(f"bilingual/{md_file.stem}.html", body)

    # daily-quiz
    for md_file in sorted((ROOT / "daily-quiz").glob("*.md")):
        add_section(f"daily-quiz/{md_file.stem}.html", render_daily_quiz(md_file))

    # curriculum
    for md_file in sorted((ROOT / "curriculum").glob("*.md")):
        add_section(f"curriculum/{md_file.stem}.html", render_plain(md_file))

    # practice
    for md_file in sorted((ROOT / "practice").glob("*.md")):
        add_section(f"practice/{md_file.stem}.html", render_plain(md_file))

    # interactive
    iv_pages = [
        ("interactive/index.html", iv.build_interactive_index_body()),
        ("interactive/geography.html", iv.build_geography_body()),
        ("interactive/history.html", iv.build_history_body()),
        ("interactive/government.html", iv.build_government_body()),
        ("interactive/symbols.html", iv.build_symbols_body()),
    ]
    for rel, body in iv_pages:
        add_section(rel, body)

    body_html = "\n".join(sections)
    sidebar = make_single_sidebar()
    page = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="加拿大公民考">
<meta name="theme-color" content="#c8102e">
<title>加拿大公民考試 · 單檔版</title>
<style>{CSS}{SINGLE_CSS_EXTRA}</style>
</head>
<body>
<div class="layout">
{sidebar}
<main>
{body_html}
</main>
</div>
<script>{SPEAK_JS}</script>
<script>{SINGLE_ROUTER_JS}</script>
</body>
</html>
"""
    out_path = OUT / "study.html"
    out_path.write_text(page, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"Built single-file: {out_path} ({size_kb:.0f} KB)")
    return out_path


# ----------------------------- build ----------------------------- #

def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "bilingual").mkdir(parents=True)
    (OUT / "daily-quiz").mkdir()
    (OUT / "curriculum").mkdir()
    (OUT / "practice").mkdir()
    (OUT / "interactive").mkdir()

    def write(rel: str, title: str, body: str):
        body = add_speak_to_english_blockquotes(body)
        body = rewrite_md_links(body)
        (OUT / rel).write_text(wrap_page(title, body, rel), encoding="utf-8")

    # bilingual
    for md_file in sorted((ROOT / "bilingual").glob("*.md")):
        if md_file.name == "README.md":
            body = render_plain(md_file)
        else:
            body = render_bilingual(md_file)
        write(f"bilingual/{md_file.stem}.html", title_from_md(md_file), body)

    # daily quiz
    for md_file in sorted((ROOT / "daily-quiz").glob("*.md")):
        write(f"daily-quiz/{md_file.stem}.html", title_from_md(md_file), render_daily_quiz(md_file))

    # curriculum
    for md_file in sorted((ROOT / "curriculum").glob("*.md")):
        write(f"curriculum/{md_file.stem}.html", title_from_md(md_file), render_plain(md_file))

    # practice
    for md_file in sorted((ROOT / "practice").glob("*.md")):
        write(f"practice/{md_file.stem}.html", title_from_md(md_file), render_plain(md_file))

    # index
    write("index.html", "學習中心", build_index_body())

    # interactive modules
    interactive_pages = [
        ("interactive/index.html", "互動式入口", iv.build_interactive_index_body()),
        ("interactive/geography.html", "互動地圖", iv.build_geography_body()),
        ("interactive/history.html", "歷史時間軸", iv.build_history_body()),
        ("interactive/government.html", "政府架構圖", iv.build_government_body()),
        ("interactive/symbols.html", "國家象徵圖鑑", iv.build_symbols_body()),
    ]
    for rel, title, body in interactive_pages:
        # Interactive pages contain raw HTML (not markdown), so skip TTS-augmentation
        # and only rewrite md links (which there aren't any).
        (OUT / rel).write_text(wrap_page(title, body, rel), encoding="utf-8")

    # single-file build (for iOS Files App preview, AirDrop, etc.)
    build_single()

    # report
    files = sorted(OUT.rglob("*.html"))
    print(f"Built {len(files)} HTML files into {OUT}")

    # iCloud Drive sync
    icloud_root = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"
    if icloud_root.exists():
        dest = icloud_root / "加拿大公民考試"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(OUT, dest)
        print(f"Synced to iCloud Drive: {dest}")
        print("Mobile access:")
        print("  iPhone → Files App → iCloud Drive → 加拿大公民考試 → index.html → tap")
    else:
        print("iCloud Drive folder not found; skipped mobile sync.")


if __name__ == "__main__":
    build()
