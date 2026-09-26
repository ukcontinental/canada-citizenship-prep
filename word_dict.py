"""Word-tap dictionary + per-item narration, shared by the non-reading pages.

The reading pages (build_html.render_reading) have their own copy wired to
sentence-level playback; this module is the standalone version used by the
interactive modules, the quiz pages and the Day 01-14 pages, where there are no
sentences to seek into — only a word to look up and a line to hear.

Text keys: sha1 of the exact string, so build_interactive_audio.py and the page
generators agree on a filename without passing an index around.
"""

from __future__ import annotations
import hashlib
import html
import re

# Latin-script only. build_html's EN_WORD_RE uses [^\W\d_] (any Unicode letter),
# which is fine there because it only ever sees pure-English sentences. Here the
# text is mixed ("Victoria 維多利亞"), so a class that matched any letter would wrap
# Chinese characters as tappable "words". Accented Latin stays in: Métis, Québec.
_L = r"[A-Za-z\u00C0-\u024F\u1E00-\u1EFF]"
EN_WORD_RE = re.compile(rf"{_L}(?:{_L}|['’\-](?={_L}))*")


def audio_key(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:16]


def wrap_words(en: str) -> str:
    """Escape, then wrap every word in <span class="w"> so it can be tapped."""
    out, pos = [], 0
    for m in EN_WORD_RE.finditer(en):
        out.append(html.escape(en[pos:m.start()]))
        out.append(f'<span class="w">{html.escape(m.group(0))}</span>')
        pos = m.end()
    out.append(html.escape(en[pos:]))
    return "".join(out)


DICT_CSS = """
<style>
/* 中／英同級：夠寬就左右並排，不夠就自動上下堆疊 */
.bi { display: flex; flex-wrap: wrap; gap: 3px 18px; align-items: flex-start; }
.bi-zh, .bi-en { flex: 1 1 240px; min-width: 0; }
.bi-en {
  color: #45403a; font-family: "Source Serif 4", Georgia, serif;
  line-height: 1.5; border-left: 2px solid var(--line); padding-left: 10px;
}
.say {
  border: none; background: none; cursor: pointer; padding: 0 2px;
  font-size: 0.82em; line-height: 1; opacity: 0.32; vertical-align: baseline;
  transition: opacity 0.12s, transform 0.12s;
}
.say:hover { opacity: 0.85; }
.say.playing { opacity: 1; transform: scale(1.25); }
/* 名稱列：中文與英文同級並排（省名、總理、政黨、節日…） */
.nm { display: inline-flex; flex-wrap: wrap; gap: 0 8px; align-items: baseline; }
.nm-en { font-family: "Source Serif 4", Georgia, serif; color: #45403a; }

.w { cursor: pointer; border-radius: 3px; padding: 0 0.5px; }
.w:hover { background: #ffe9c7; }
.wd-pop {
  position: fixed; z-index: 90; width: min(340px, calc(100vw - 24px));
  background: #fff; border: 1px solid var(--line); border-radius: 12px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.16); padding: 14px 16px 12px;
}
.wd-pop.hidden { display: none; }
.wd-w { font-family: Georgia, "Source Serif 4", serif; font-size: 26px; font-weight: 700; color: #3f1a1f; padding-right: 24px; }
.wd-p { font-size: 15px; color: var(--muted); margin: 2px 0 8px; font-family: "Charis SIL", "Doulos SIL", "Gentium Plus", Georgia, serif; }
.wd-t { font-size: 14.5px; line-height: 1.6; white-space: pre-line; margin-bottom: 10px; color: var(--ink); }
.wd-btns { display: flex; gap: 6px; flex-wrap: wrap; }
.wd-btns button {
  font: inherit; font-size: 12.5px; padding: 5px 10px; border-radius: 6px;
  border: 1px solid var(--line); background: #fff; cursor: pointer; color: var(--ink);
}
.wd-btns button.main { background: var(--accent); color: #fff; border-color: var(--accent); }
.wd-x { position: absolute; top: 6px; right: 10px; border: none; background: none; font-size: 20px; color: var(--muted); cursor: pointer; }
.wd-note { font-size: 11px; color: var(--muted); margin-top: 8px; }
</style>
"""

DICT_POPUP_HTML = """
<div class="wd-pop hidden" role="dialog" aria-label="字典">
  <button class="wd-x" type="button" aria-label="關閉">×</button>
  <div class="wd-w"></div>
  <div class="wd-p"></div>
  <div class="wd-t"></div>
  <div class="wd-btns">
    <button class="wd-slow main" type="button">🔊 慢速再聽</button>
    <button class="wd-normal" type="button">🔊 正常速</button>
  </div>
  <div class="wd-note">釋義來源：ECDICT 開源字典＋加拿大語境補充。點其他地方或按 Esc 關閉。</div>
</div>
"""


def dict_js(word_base: str, line_base: str) -> str:
    """word_base: folder of per-word clips. line_base: folder of per-line clips."""
    return (
        r"""
<script>
(function () {
  var WORD_BASE = '__WORD_BASE__', LINE_BASE = '__LINE_BASE__';
  var pop = document.querySelector('.wd-pop');
  var wordAudio = new Audio(), lineAudio = new Audio();
  var ctx = null, playingBtn = null;

  // ---------- per-line narration (the 🔊 buttons next to 中文 / English) ----------
  function stopLine() {
    lineAudio.pause();
    if (playingBtn) { playingBtn.classList.remove('playing'); playingBtn = null; }
  }
  lineAudio.addEventListener('ended', stopLine);
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.say');
    if (!b) return;
    e.stopPropagation();
    // A hand-picked line wins over a running continuous read-through.
    if (window.CIT_AUTOPLAY_STOP) window.CIT_AUTOPLAY_STOP();
    var wasPlaying = (b === playingBtn);
    stopLine();
    if (wasPlaying) return;
    lineAudio.src = LINE_BASE + b.dataset.lang + '/' + b.dataset.k + '.m4a';
    lineAudio.playbackRate = 1;
    playingBtn = b; b.classList.add('playing');
    lineAudio.play().catch(function () {
      // no clip for this line (content changed since the last audio build)
      stopLine();
      if (!window.speechSynthesis) return;
      var host = b.parentElement;
      var txt = host ? host.textContent.replace(/🔊/g, '').trim() : '';
      var u = new SpeechSynthesisUtterance(txt);
      u.lang = (b.dataset.lang === 'zh') ? 'zh-TW' : 'en-US'; u.rate = 0.85;
      window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
    });
  });

  // ---------- word dictionary ----------
  if (!pop) return;
  function lookup(w) {
    var D = window.CIT_DICT || {};
    var k = w.replace(/’/g, "'");
    var tries = [k, k.toLowerCase()];
    if (/'s$/i.test(k)) tries.push(k.slice(0, -2), k.slice(0, -2).toLowerCase());
    for (var i = 0; i < tries.length; i++) if (D[tries[i]]) return D[tries[i]];
    return null;
  }
  function say(rate) {
    if (!ctx) return;
    if (window.CIT_AUTOPLAY_STOP) window.CIT_AUTOPLAY_STOP();
    stopLine();
    var key = ctx.word.toLowerCase().replace(/’/g, "'");
    wordAudio.pause();
    wordAudio.src = WORD_BASE + encodeURIComponent(key) + '.m4a';
    wordAudio.playbackRate = rate;
    try { wordAudio.preservesPitch = true; wordAudio.mozPreservesPitch = true; } catch (err) {}
    wordAudio.onerror = function () {
      if (!window.speechSynthesis) return;
      var u = new SpeechSynthesisUtterance(ctx.word);
      u.lang = 'en-US'; u.rate = 0.7 * rate;
      window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
    };
    wordAudio.play().catch(function () {});
  }
  function place(el) {
    var r = el.getBoundingClientRect();
    pop.style.top = Math.max(8, Math.min(r.bottom + 8, window.innerHeight - pop.offsetHeight - 8)) + 'px';
    var maxLeft = document.documentElement.clientWidth - pop.offsetWidth - 12;
    pop.style.left = Math.max(12, Math.min(r.left, maxLeft)) + 'px';
  }
  function show(el) {
    var w = el.textContent.trim(), e = lookup(w);
    pop.querySelector('.wd-w').textContent = w;
    pop.querySelector('.wd-p').textContent = (e && e.p) ? '/' + e.p + '/' : '';
    pop.querySelector('.wd-t').textContent = e ? (e.x ? e.t + '\n（原形：' + e.x + '）' : e.t) : '字典裡沒有這個字';
    ctx = { word: w };
    pop.classList.remove('hidden');
    place(el);
    say(1);
  }
  function hide() { pop.classList.add('hidden'); ctx = null; wordAudio.pause(); }
  pop.querySelector('.wd-slow').addEventListener('click', function (e) { e.stopPropagation(); say(1); });
  pop.querySelector('.wd-normal').addEventListener('click', function (e) { e.stopPropagation(); say(1.45); });
  pop.querySelector('.wd-x').addEventListener('click', hide);
  document.addEventListener('click', function (e) {
    var wEl = e.target.closest && e.target.closest('.w');
    if (wEl) { e.stopPropagation(); show(wEl); return; }
    if (!pop.classList.contains('hidden') && !pop.contains(e.target)) hide();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
})();
</script>
"""
        .replace("__WORD_BASE__", word_base)
        .replace("__LINE_BASE__", line_base)
    )
