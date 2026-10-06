"""Cloud sync for the wrong-book (cit_wrong_v2), shared sign-in with the quiz site.

Each person signs in with a name + 4-digit PIN. The sign-in is the same one
https://ukcontinental.github.io/citizenship-quiz/ uses (same origin, same
localStorage key `citz-me`, same hash), so signing in on either site covers both.

The wrong-book itself still lives in localStorage (the quiz engine reads it
synchronously); this script mirrors it to Firestore so it follows the person
across devices:
  * Firestore doc  books/<sha256(personId + "|prep")>, fields {items, updated}
    (the quiz site keeps its own book under the person's id; ids differ per site)
  * cit_wrong_owner   — whose book the local copy is
  * cit_wrong_pending — person id whose local edits are not uploaded yet
A local edit that has not reached the cloud always wins over the cloud copy.
A device's book from before sign-in existed (no owner) is merged into the first
person who signs in there.
"""

SYNC_JS = r"""
<script>
(function() {
  var KEY = 'AIzaSyBoo7eK2jYNIzKIpOwV-gQ5rk7OLdDaJO0';
  var URL = 'https://firestore.googleapis.com/v1/projects/citizenship-quiz-27223/databases/(default)/documents/books/';
  var QUIZ_SITE = 'https://ukcontinental.github.io/citizenship-quiz/';
  var LS = 'cit_wrong_v2', OWN = 'cit_wrong_owner', PEND = 'cit_wrong_pending', ME = 'citz-me';
  var state = 'none';   // none | ok | saving | offline

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} }
  function me() { try { return JSON.parse(get(ME) || 'null'); } catch (e) { return null; } }
  function localBook() { try { return JSON.parse(get(LS) || '{}') || {}; } catch (e) { return {}; } }
  function hex(buf) { return Array.prototype.map.call(new Uint8Array(buf), function(x) { return ('0' + x.toString(16)).slice(-2); }).join(''); }
  function sha(s) { return crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)).then(hex); }
  function docOf(personId) { return sha(personId + '|prep'); }

  function fetchBook(personId) {
    return docOf(personId).then(function(d) {
      return fetch(URL + d + '?key=' + KEY, { cache: 'no-store' });
    }).then(function(r) {
      if (r.status === 404) return {};
      if (!r.ok) throw new Error('http ' + r.status);
      return r.json().then(function(j) { return JSON.parse(((j.fields || {}).items || {}).stringValue || '{}'); });
    });
  }
  function saveBook(personId, items) {
    return docOf(personId).then(function(d) {
      return fetch(URL + d + '?key=' + KEY, { method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fields: { items: { stringValue: JSON.stringify(items) },
                                         updated: { stringValue: new Date().toISOString() } } }) });
    }).then(function(r) { if (!r.ok) throw new Error('http ' + r.status); });
  }
  function merge(a, b) {
    var out = {}, k;
    for (k in a) out[k] = a[k];
    for (k in b) if (!out[k] || (b[k].n || 0) > (out[k].n || 0)) out[k] = b[k];
    return out;
  }

  // ---- upload (debounced; called by the quiz engine after every wrong-book save)
  var timer = null, busy = false;
  function push() {
    var m = me(); if (!m) return;
    set(OWN, m.id); set(PEND, m.id);
    clearTimeout(timer); timer = setTimeout(doPush, 800);
  }
  function doPush() {
    var m = me(); if (!m) return Promise.resolve();
    if (busy) { push(); return Promise.resolve(); }
    busy = true; state = 'saving'; paint();
    var snapshot = get(LS) || '{}';
    return saveBook(m.id, localBook()).then(function() {
      if (get(PEND) === m.id && (get(LS) || '{}') === snapshot) set(PEND, null);
      state = 'ok';
    }, function() { state = 'offline'; }).then(function() { busy = false; paint(); });
  }

  // ---- download / hand the device's book to whoever is signed in
  function pull(first) {
    var m = me(), owner = get(OWN), pend = get(PEND);
    if (!m) {
      // signed out: upload a leftover edit, then keep the last person's book off this screen
      var flush = (pend && owner && pend === owner)
        ? saveBook(owner, localBook()).then(function() { set(PEND, null); }, function() {})
        : Promise.resolve();
      return flush.then(function() {
        if (owner && get(PEND) !== owner) { set(LS, null); set(OWN, null); }
        state = 'none'; paint();
      });
    }
    if (busy) return Promise.resolve();
    var before = get(LS) || '{}';
    var step = Promise.resolve();
    if (owner && owner !== m.id) {
      // someone else's book is on this device: save their unsent edits, then clear it
      if (pend === owner) step = saveBook(owner, localBook()).then(function() { set(PEND, null); }, function() {});
      step = step.then(function() { if (get(PEND) !== owner) { set(LS, null); set(OWN, null); } });
    }
    return step.then(function() {
      if (get(OWN) && get(OWN) !== m.id) { state = 'offline'; paint(); return; }   // could not hand over yet
      if (get(PEND) === m.id) return doPush();                                     // our unsent edits win
      var legacy = !get(OWN) ? localBook() : null;                                 // pre-sign-in book on this device
      return fetchBook(m.id).then(function(remote) {
        if (busy || get(PEND) === m.id) return;
        var next = remote;
        if (legacy && Object.keys(legacy).length) next = merge(remote, legacy);
        set(LS, JSON.stringify(next)); set(OWN, m.id);
        state = 'ok';
        if (legacy && Object.keys(legacy).length && JSON.stringify(next) !== JSON.stringify(remote)) push();
        paint();
        var changed = (get(LS) || '{}') !== before;
        if (changed && first && document.querySelector('.qz-q, .qz-start, .qz-empty')) {
          // the quiz on this page was drawn from the old copy: redraw it once
          try { if (!sessionStorage.getItem('cit_sync_reloaded')) { sessionStorage.setItem('cit_sync_reloaded', '1'); location.reload(); } } catch (e) {}
        }
      }, function() { state = 'offline'; paint(); });
    });
  }

  // ---- who's signed in (top of the sidebar)
  var box = null;
  function paint() {
    if (!box) return;
    var m = me();
    if (!m) {
      box.innerHTML = '<div class="cs-t">錯題本只存在這台裝置</div>' +
        '<button type="button" class="cs-b" id="cs-open">登入，各裝置同步錯題本</button>' +
        '<form class="cs-f" id="cs-form" hidden>' +
        '<input id="cs-n" placeholder="名字（例如：太太）" maxlength="20" autocomplete="username">' +
        '<input id="cs-p" type="password" inputmode="numeric" maxlength="4" placeholder="4 位數密碼" autocomplete="current-password">' +
        '<button type="submit" class="cs-b">登入</button><div class="cs-e" id="cs-e"></div>' +
        '<div class="cs-t">跟「陷阱題特訓」網站用同一組名字和密碼。第一次用就自己取一組，記下來。</div></form>';
      document.getElementById('cs-open').onclick = function() {
        document.getElementById('cs-form').hidden = false; this.hidden = true; document.getElementById('cs-n').focus();
      };
      document.getElementById('cs-form').onsubmit = function(ev) {
        ev.preventDefault();
        var n = document.getElementById('cs-n').value.trim(), p = document.getElementById('cs-p').value.trim();
        var er = document.getElementById('cs-e');
        if (!n) { er.textContent = '請輸入名字。'; return; }
        if (!/^\d{4}$/.test(p)) { er.textContent = '密碼請輸入 4 個數字。'; return; }
        sha('citz-v1|' + n.toLowerCase() + '|' + p).then(function(id) {
          set(ME, JSON.stringify({ name: n, id: id }));
          box.innerHTML = '<div class="cs-t">載入中…</div>';
          pull(true);
        });
      };
      return;
    }
    var label = state === 'offline' ? '離線中，連上網路會自動同步' : state === 'saving' ? '同步中…' : '錯題本已同步';
    box.innerHTML = '<div class="cs-who">👤 <b></b> <button type="button" class="cs-x" id="cs-out">切換</button></div>' +
      '<div class="cs-t">' + label + '</div>';
    box.querySelector('b').textContent = m.name;
    document.getElementById('cs-out').onclick = function() { set(ME, null); pull(false); };
  }

  window.CIT_SYNC = { push: push, pull: pull };
  var css = document.createElement('style');
  css.textContent = '.cs-box{margin:4px 0 12px;padding:10px 12px;border:1px solid var(--line,#ddd);border-radius:10px;background:#fff;font-size:13px}' +
    '.cs-box[hidden],.cs-f[hidden],.cs-b[hidden]{display:none!important}' +
    '.cs-who{font-size:14px}.cs-t{color:var(--muted,#666);font-size:12.5px;margin-top:4px;line-height:1.5}' +
    '.cs-b{appearance:none;border:0;background:var(--accent,#c8102e);color:#fff;border-radius:16px;padding:6px 12px;font-size:13px;font-weight:600;cursor:pointer;margin-top:6px}' +
    '.cs-x{appearance:none;border:0;background:none;color:var(--accent,#c8102e);text-decoration:underline;font-size:13px;cursor:pointer;padding:0 2px}' +
    '.cs-f input{display:block;width:100%;box-sizing:border-box;margin-top:6px;padding:7px 9px;border:1px solid var(--line,#ccc);border-radius:7px;font-size:15px}' +
    '.cs-e{color:#c8102e;font-size:12.5px;min-height:1em;margin-top:4px}';
  document.head.appendChild(css);
  var nav = document.querySelector('.sidebar');
  if (nav) {
    box = document.createElement('div'); box.className = 'cs-box';
    var home = nav.querySelector('.home');
    home && home.nextSibling ? nav.insertBefore(box, home.nextSibling) : nav.insertBefore(box, nav.firstChild);
  }
  paint();
  pull(true).then(function() { try { sessionStorage.removeItem('cit_sync_reloaded'); } catch (e) {} });
  document.addEventListener('visibilitychange', function() { if (document.visibilityState === 'visible') pull(false); });
  window.addEventListener('online', function() { pull(false); });
  window.addEventListener('storage', function(e) { if (e.key === ME) pull(false); });
})();
</script>
"""

# Sidebar link to the companion quiz site (per-person wrong-book, mock exams).
QUIZ_SITE_LINK = ('<a href="https://ukcontinental.github.io/citizenship-quiz/" class="ext">'
                  '🎯 陷阱題特訓網站 ↗</a>')
