"""Interactive (visual) study modules — body HTML generators.

Each function returns inner-body HTML, ready to be wrapped by build_html.wrap_page().
Common interactive styles live in IV_SHARED_CSS; per-module CSS in each function.
"""

import html as _html
import json
import re as _re

import word_dict as _wd
from canada_map import CAPITALS_MAP_SVG
from interactive_data import (PROVINCES, HISTORY_EVENTS, PRIME_MINISTERS, PARTIES, VOTE_STEPS,
                              MUST_KNOW_FACTS, JUSTICE_PRINCIPLES, RCMP_FACTS, SYMBOLS,
                              CURRENCY_FIGURES, NATIONAL_HOLIDAYS, COINS, INDUSTRIES, TRADE_FACTS,
                              BILL_STEPS, GOV_LEGEND, PEOPLE, PEOPLE_CATS, JOINING, JOINING_TRICKS)


def _strong(t: str) -> str:
    return _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


# Every line that gets a 🔊 button is recorded here, so
# tools/build_interactive_audio.py can synthesize exactly what the pages ask for
# (no second list to keep in sync). Populated by calling the build_*_body().
BI_SEEN: dict[str, tuple[str, str]] = {}   # key -> (lang, plain text)


def say(text: str, lang: str) -> str:
    """A 🔊 button for one line. The clip is keyed by the text itself, so
    build_interactive_audio.py needs no index and stale clips simply 404 into
    the speechSynthesis fallback."""
    if not text.strip():
        return ""
    k = _wd.audio_key(text)
    BI_SEEN[k] = (lang, _re.sub(r"\*\*", "", text).strip())
    return (f'<button class="say" type="button" data-lang="{lang}" '
            f'data-k="{k}" aria-label="朗讀">🔊</button>')


def bi(text: str) -> str:
    """'中文｜English' -> a 中/英 pair, side by side when the box is wide enough
    and stacked when it is not (plain flex-wrap, no container queries), both at
    the same type size. English words are tappable for the dictionary."""
    if "｜" not in text:
        # Mixed line such as "Victoria 維多利亞" — no pairing to do, but the
        # English inside it should still be tappable.
        return _strong(_wd.wrap_words(text))
    zh, en = text.split("｜", 1)
    return (f'<span class="bi">'
            f'<span class="bi-zh">{_strong(_html.escape(zh))}{say(zh, "zh")}</span>'
            f'<span class="bi-en">{_strong(_wd.wrap_words(en))}{say(en, "en")}</span>'
            f'</span>')


def pair(zh: str, en: str) -> str:
    """Same rendering as bi() for data tables that keep 中/英 in separate fields."""
    return bi(f"{zh}｜{en}")

# ============================================================================
# SHARED CSS
# ============================================================================

IV_SHARED_CSS = """
<style>
.iv-hero {
  background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%);
  border-left: 4px solid var(--accent);
  padding: 18px 22px; border-radius: 8px; margin: 16px 0 24px;
}
.iv-hero h1 { margin: 0 0 6px; border: none; padding: 0; }
.iv-hero p { margin: 0; color: var(--muted); }
.iv-hero h1 small, .iv-section-title small { font-size: 0.8em; font-weight: 400; color: #45403a; font-family: "Source Serif 4", Georgia, serif; margin-left: 8px; }

.iv-section-title {
  margin: 32px 0 14px; padding-bottom: 6px;
  border-bottom: 2px solid var(--accent);
  font-size: 19px; font-weight: 700;
}

.iv-card-grid { display: grid; gap: 12px; margin: 16px 0 24px; }
.iv-card {
  background: #fff; border: 1px solid var(--line);
  border-radius: 10px; padding: 16px 18px;
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
  cursor: pointer;
}
.iv-card:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.iv-card.iv-active {
  border-color: var(--accent);
  background: linear-gradient(135deg, #fff 0%, #fff8f8 100%);
}
.iv-card h4 { margin: 0 0 6px; font-size: 16px; }
.iv-card .meta { font-size: 12px; color: var(--muted); margin-bottom: 8px; }
.iv-card p { margin: 0; font-size: 14px; line-height: 1.5; }

.iv-detail-panel {
  margin: 20px 0; padding: 20px 24px;
  background: #fff; border: 1px solid var(--line);
  border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.iv-detail-panel h3 { margin-top: 0; }

.iv-tag {
  display: inline-block; padding: 2px 8px; border-radius: 12px;
  background: #f3efe6; font-size: 11px; color: var(--muted);
  font-family: -apple-system, system-ui, sans-serif;
  letter-spacing: 0.04em; margin-right: 6px;
}
.iv-tag.accent { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
</style>
"""



def _gov_legend_html():
    return "".join(f'<div class="iv-gov-leg-item"><div class="iv-gov-dot" style="background:{c}"></div><div><strong>{t}</strong>{bi(d)}</div></div>' for c, t, d in GOV_LEGEND)


def _bill_steps_html():
    return "".join(f'<div class="iv-bill-step"><div class="num">{i}</div><div class="title">{t}</div><div class="desc">{bi(d)}</div></div>' for i, (t, d) in enumerate(BILL_STEPS, 1))


def _vote_steps_html():
    return "".join(f'<div class="iv-vote-step"><div class="icon">{ic}</div><strong>{bi(t)}</strong><p>{bi(d)}</p></div>' for ic, t, d in VOTE_STEPS)


def _must_know_html():
    return "".join(f'<div class="iv-fact-row"><strong>{bi(k)}</strong><span>{bi(v)}</span></div>' for k, v in MUST_KNOW_FACTS)


def _rcmp_html():
    return "".join(f'<li><strong>{bi(k)}</strong>{bi(v)}</li>' for k, v in RCMP_FACTS)


def _coins_html():
    return "".join(f'<div class="iv-card"><strong>{d}</strong> {n}<br><span class="meta">{bi(x)}</span></div>' for d, n, x in COINS)


# ============================================================================
# 11. GEOGRAPHY (already complete)
# ============================================================================


PROVINCE_BY_CODE = {p[0]: p for p in PROVINCES}

REGIONS = [
    ("West Coast", "西岸", "#4ea693", ["BC"]),
    ("Prairie Provinces", "草原三省", "#d4a943", ["AB", "SK", "MB"]),
    ("Central Canada", "中央加拿大", "#c8102e", ["ON", "QC"]),
    ("Atlantic Canada", "大西洋四省", "#5a9460", ["NB", "NS", "PE", "NL"]),
    ("Northern Territories", "北部三領地", "#4a7c9e", ["YT", "NT", "NU"]),
]

REGION_COLOR = {}
for _en, _zh, _color, codes in REGIONS:
    for c in codes:
        REGION_COLOR[c] = _color

PROVINCE_LAYOUT = {
    "YT": (50, 30, 130, 130), "NT": (190, 30, 180, 130), "NU": (380, 30, 320, 180),
    "BC": (50, 180, 130, 180), "AB": (190, 180, 85, 180), "SK": (285, 180, 85, 180),
    "MB": (380, 220, 85, 140), "ON": (475, 240, 170, 180), "QC": (655, 240, 170, 160),
    "NL": (835, 200, 130, 160), "NB": (685, 430, 75, 70),
    "PE": (770, 430, 50, 35), "NS": (830, 430, 130, 70),
}


def build_geography_body():
    rects = []
    for code, (x, y, w, h) in PROVINCE_LAYOUT.items():
        p = PROVINCE_BY_CODE[code]
        color = REGION_COLOR[code]
        is_ontario = code == "ON"
        cls = "iv-prov" + (" iv-prov-star" if is_ontario else "")
        label = code if w < 80 else f"{code} {p[2].split('（')[0]}"
        text_y = y + h / 2 + 5
        font_size = 14 if w < 80 else 18
        star = ""
        if is_ontario:
            star = f'<text x="{x + w - 10}" y="{y + 22}" text-anchor="end" font-size="18" fill="#fff100" pointer-events="none">★</text>'
        rects.append(
            f'<g class="{cls}" data-code="{code}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{color}" />'
            f'<text x="{x + w/2}" y="{text_y}" text-anchor="middle" font-size="{font_size}" '
            f'font-weight="700" fill="#fff" pointer-events="none">{label}</text>{star}</g>'
        )
    region_labels = (
        '<text x="850" y="555" font-size="11" fill="#5a9460" font-weight="600">大西洋四省</text>'
        '<text x="100" y="555" font-size="11" fill="#4ea693" font-weight="600">西岸</text>'
        '<text x="305" y="555" font-size="11" fill="#d4a943" font-weight="600">草原三省</text>'
        '<text x="555" y="555" font-size="11" fill="#c8102e" font-weight="600">中央加拿大</text>'
        '<text x="380" y="15" font-size="11" fill="#4a7c9e" font-weight="600">北部三領地</text>'
    )
    map_svg = '<svg viewBox="0 0 1000 580" class="iv-map" role="img" aria-label="加拿大省份地圖">' + "".join(rects) + region_labels + '</svg>'

    p = PROVINCE_BY_CODE["ON"]
    code, en, zh, region, capital, premier, lt_gov, facts = p
    facts_html = "".join(f"<li>{bi(f)}</li>" for f in facts)
    detail = f'''<div class="iv-detail" id="iv-prov-detail" data-current="ON">
  <div class="iv-detail-head">
    <h2><span class="iv-detail-code">{code}</span> {en} <span class="iv-detail-zh">{zh}</span></h2>
    <span class="iv-detail-region">{region}</span>
  </div>
  <div class="iv-detail-grid">
    <div class="iv-detail-stat"><label>首府 Capital</label><span>{capital}</span></div>
    <div class="iv-detail-stat"><label>省長 Premier</label><span>{premier}</span></div>
    <div class="iv-detail-stat"><label>省督 / 委員</label><span>{lt_gov}</span></div>
  </div>
  <h3>重點知識</h3>
  <ul class="iv-detail-facts">{facts_html}</ul>
</div>'''

    data = {}
    for p in PROVINCES:
        c, en, zh, region, capital, premier, lt_gov, facts = p
        data[c] = {"en": en, "zh": zh, "region": region, "capital": capital,
                   "premier": premier, "lt_gov": lt_gov, "facts": [bi(f) for f in facts]}
    data_json = json.dumps(data, ensure_ascii=False)

    table_rows = ""
    for p in PROVINCES:
        c, en, zh, region, capital, premier, lt_gov, facts = p
        zh_short = zh.split("（")[0]
        color = REGION_COLOR[c]
        table_rows += (
            f'<tr data-code="{c}" class="iv-row">'
            f'<td><span class="iv-dot" style="background:{color}"></span>{c}</td>'
            f'<td>{en}</td><td>{zh_short}</td><td>{capital}</td><td>{premier}</td></tr>'
        )

    region_cards = "".join(
        f'<div class="iv-region-card" style="background:{color}"><div class="label">Region</div>'
        f'<div class="name">{zh}</div><div class="name-en">{en}</div>'
        f'<div class="codes">{" · ".join(codes)}</div></div>'
        for en, zh, color, codes in REGIONS
    )

    return f'''{IV_SHARED_CSS}
<style>
.iv-map {{ width: 100%; height: auto; max-width: 100%; }}
.iv-prov {{ cursor: pointer; transition: filter 0.15s, transform 0.15s; transform-origin: center; transform-box: fill-box; }}
.iv-prov rect {{ transition: stroke 0.15s, stroke-width 0.15s; stroke: rgba(0,0,0,0.1); stroke-width: 1; }}
.iv-prov:hover rect {{ stroke: #1f2328; stroke-width: 3; }}
.iv-prov.iv-active rect {{ stroke: #1f2328; stroke-width: 4; filter: brightness(1.05); }}
.iv-prov-star rect {{ stroke: #c8102e; stroke-width: 2; stroke-dasharray: 4 2; }}
.iv-detail {{ margin: 20px 0; padding: 22px; background: #fff; border: 1px solid var(--line); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
.iv-detail-head {{ display: flex; align-items: baseline; flex-wrap: wrap; gap: 12px; margin-bottom: 14px; }}
.iv-detail-head h2 {{ margin: 0; border: none; padding: 0; font-size: 22px; }}
.iv-detail-code {{ display: inline-block; background: var(--accent); color: #fff; padding: 2px 10px; border-radius: 6px; font-family: monospace; font-size: 18px; margin-right: 4px; }}
.iv-detail-zh {{ color: var(--ink); font-weight: 400; font-size: 22px; }}
.iv-detail-region {{ display: inline-block; padding: 3px 10px; border-radius: 12px; background: #f3efe6; font-size: 12px; color: var(--muted); }}
.iv-detail-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 14px 0 20px; }}
.iv-detail-stat {{ padding: 10px 12px; background: #faf8f4; border-radius: 6px; }}
.iv-detail-stat label {{ display: block; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); margin-bottom: 3px; }}
.iv-detail-stat span {{ font-weight: 600; }}
.iv-detail h3 {{ font-size: 15px; margin: 0 0 8px; }}
.iv-detail-facts {{ margin: 0; padding-left: 20px; }}
.iv-detail-facts li {{ margin: 6px 0; }}
.iv-region-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 16px 0 30px; }}
.iv-region-card {{ padding: 12px 14px; border-radius: 8px; color: #fff; font-size: 14px; }}
.iv-region-card .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.85; }}
.iv-region-card .name {{ font-weight: 700; font-size: 15px; margin: 3px 0 1px; }}
.iv-region-card .name-en {{ font-size: 15px; font-family: "Source Serif 4", Georgia, serif; margin: 0 0 6px; }}
.iv-region-card .codes {{ font-family: monospace; font-size: 13px; }}
table.iv-quick {{ width: 100%; font-size: 14px; }}
table.iv-quick th {{ font-size: 12px; }}
.iv-row {{ cursor: pointer; }}
.iv-row:hover {{ background: #fff8f8; }}
.iv-row.iv-active {{ background: var(--accent-soft); }}
.iv-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }}
</style>
<div class="iv-hero">
  <h1>🗺️ 加拿大地理 <small>Canada's Regions</small></h1>
  <p>點任何省份看它的首府、省長、產業重點。<strong>Ontario ⭐</strong> 是考試重點省，預設展開。</p>
</div>
{map_svg}
{detail}
<h2 class="iv-section-title">5 大區域速記 <small>The Five Regions</small></h2>
<div class="iv-region-row">{region_cards}</div>
<h2 class="iv-section-title">速查表 <small>Provinces &amp; Capitals</small></h2>
<table class="iv-quick"><thead><tr><th>代碼</th><th>英文名</th><th>中文</th><th>首府</th><th>省長</th></tr></thead><tbody>{table_rows}</tbody></table>
<script>
(function() {{
  var DATA = {data_json};
  var detail = document.getElementById('iv-prov-detail');
  if (!detail) return;
  function show(code) {{
    var d = DATA[code]; if (!d) return;
    detail.dataset.current = code;
    detail.querySelector('.iv-detail-head h2').innerHTML =
      '<span class="iv-detail-code">' + code + '</span> ' + d.en +
      ' <span class="iv-detail-zh">' + d.zh + '</span>';
    detail.querySelector('.iv-detail-region').textContent = d.region;
    var stats = detail.querySelectorAll('.iv-detail-stat span');
    stats[0].textContent = d.capital;
    stats[1].textContent = d.premier;
    stats[2].textContent = d.lt_gov;
    detail.querySelector('.iv-detail-facts').innerHTML =
      d.facts.map(function(f){{ return '<li>' + f + '</li>'; }}).join('');
    document.querySelectorAll('.iv-prov.iv-active').forEach(function(e){{ e.classList.remove('iv-active'); }});
    var mapEl = document.querySelector('.iv-prov[data-code="' + code + '"]');
    if (mapEl) mapEl.classList.add('iv-active');
    document.querySelectorAll('.iv-row.iv-active').forEach(function(e){{ e.classList.remove('iv-active'); }});
    var rowEl = document.querySelector('.iv-row[data-code="' + code + '"]');
    if (rowEl) rowEl.classList.add('iv-active');
    if (window.innerWidth < 800) detail.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
  document.querySelectorAll('.iv-prov').forEach(function(el) {{
    el.addEventListener('click', function() {{ show(el.dataset.code); }});
  }});
  document.querySelectorAll('.iv-row').forEach(function(el) {{
    el.addEventListener('click', function() {{ show(el.dataset.code); }});
  }});
  var mapEl = document.querySelector('.iv-prov[data-code="ON"]');
  if (mapEl) mapEl.classList.add('iv-active');
  var rowEl = document.querySelector('.iv-row[data-code="ON"]');
  if (rowEl) rowEl.classList.add('iv-active');
}})();
</script>'''


# ============================================================================
# 04. HISTORY TIMELINE
# ============================================================================

# (year_label, title_zh, title_en, era, brief, details[])

ERAS = [
    ("new-france", "新法蘭西時期", "New France", "1497-1763", "#4a6fa5"),
    ("british", "英屬北美", "British North America", "1763-1867", "#b0413e"),
    ("confederation", "邦聯時代", "Confederation era", "1867-1914", "#c8a040"),
    ("wars", "兩戰與改革", "The World Wars and reform", "1914-1949", "#7a8c5c"),
    ("modern", "現代加拿大", "Modern Canada", "1949-至今 / present", "#5a9460"),
]

ERA_COLOR = {e[0]: e[4] for e in ERAS}


def build_history_body():
    timeline_html = ""
    for year, title_zh, title_en, era, brief, details in HISTORY_EVENTS:
        color = ERA_COLOR[era]
        details_html = ""
        if details:
            details_html = "<ul class='iv-tl-details'>" + "".join(f"<li>{bi(d)}</li>" for d in details) + "</ul>"
        is_star = "⭐" in year or "⭐" in title_zh
        timeline_html += f'''
<div class="iv-tl-event {'iv-tl-star' if is_star else ''}" data-era="{era}">
  <div class="iv-tl-marker" style="background:{color}"></div>
  <div class="iv-tl-year">{year}</div>
  <div class="iv-tl-content">
    <h3 class="iv-tl-title">{title_zh}</h3>
    <div class="iv-tl-en">{title_en}</div>
    <p class="iv-tl-brief">{bi(brief)}</p>
    {details_html}
  </div>
</div>'''

    era_filters = "".join(
        f'<button class="iv-era-btn" data-era="{era_id}" style="--era-color:{color}">'
        f'<span class="era-zh">{zh}</span><span class="era-en">{en}</span>'
        f'<span class="era-yr">{yr}</span></button>'
        for era_id, zh, en, yr, color in ERAS
    )

    return f'''{IV_SHARED_CSS}
<style>
.iv-era-filter {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 24px; }}
.iv-era-btn .era-zh {{ display: block; }}
.iv-era-btn .era-en {{ display: block; font-family: "Source Serif 4", Georgia, serif; font-weight: 400; }}
.iv-era-btn .era-yr {{ display: block; font-family: monospace; font-size: 11px; opacity: 0.75; }}
.iv-era-btn {{
  appearance: none; padding: 7px 14px; border-radius: 14px; text-align: left; line-height: 1.35;
  background: #fff; border: 2px solid var(--era-color);
  color: var(--era-color); cursor: pointer; font-size: 13px; font-weight: 600;
  font-family: -apple-system, system-ui, sans-serif;
  transition: all 0.15s;
}}
.iv-era-btn.iv-active {{ background: var(--era-color); color: #fff; }}
.iv-tl {{ position: relative; padding: 12px 0; }}
.iv-tl::before {{
  content: ''; position: absolute; left: 88px; top: 0; bottom: 0;
  width: 3px; background: linear-gradient(to bottom, #4a6fa5 0%, #b0413e 20%, #c8a040 40%, #7a8c5c 65%, #5a9460 85%, #5a9460 100%);
  border-radius: 2px;
}}
.iv-tl-event {{
  display: grid; grid-template-columns: 80px 30px 1fr;
  align-items: start; gap: 10px; padding: 10px 0;
  position: relative;
}}
.iv-tl-event.iv-hidden {{ display: none; }}
.iv-tl-year {{
  text-align: right; font-weight: 700; font-family: monospace;
  font-size: 14px; padding-top: 12px; color: var(--ink);
}}
.iv-tl-marker {{
  width: 14px; height: 14px; border-radius: 50%;
  border: 3px solid #fff; box-shadow: 0 0 0 2px currentColor;
  margin: 14px 8px 0;
}}
.iv-tl-content {{
  background: #fff; border: 1px solid var(--line); border-radius: 8px;
  padding: 12px 16px; transition: all 0.15s;
}}
.iv-tl-event:hover .iv-tl-content {{
  border-color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}
.iv-tl-star .iv-tl-content {{
  background: linear-gradient(135deg, #fff 0%, #fff8e8 100%);
  border-color: #d4a943;
}}
.iv-tl-title {{ margin: 0 0 2px; font-size: 16px; }}
.iv-tl-en {{ font-size: 16px; color: #45403a; font-family: "Source Serif 4", Georgia, serif; margin-bottom: 6px; }}
.iv-tl-brief {{ margin: 0 0 8px; font-size: 14px; }}
.iv-tl-details {{ margin: 6px 0 0; padding-left: 18px; font-size: 13px; color: var(--muted); }}
.iv-tl-details li {{ margin: 3px 0; }}
@media (max-width: 600px) {{
  .iv-tl::before {{ left: 60px; }}
  .iv-tl-event {{ grid-template-columns: 55px 24px 1fr; gap: 6px; }}
  .iv-tl-year {{ font-size: 12px; }}
}}
</style>
<div class="iv-hero">
  <h1>📜 加拿大歷史時間軸 <small>Canada's History Timeline</small></h1>
  <p>1497 → 2021 共 41 件考試重點事件。按時代色標分區，⭐ = 高頻考點。點時代按鈕篩選。</p>
</div>
<div class="iv-era-filter">
  <button class="iv-era-btn iv-active" data-era="all" style="--era-color:#1f2328">全部</button>
  {era_filters}
</div>
<div class="iv-tl">
{timeline_html}
</div>
<script>
(function() {{
  var buttons = document.querySelectorAll('.iv-era-btn');
  var events = document.querySelectorAll('.iv-tl-event');
  buttons.forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      buttons.forEach(function(b){{ b.classList.remove('iv-active'); }});
      btn.classList.add('iv-active');
      var era = btn.dataset.era;
      events.forEach(function(ev) {{
        if (era === 'all' || ev.dataset.era === era) ev.classList.remove('iv-hidden');
        else ev.classList.add('iv-hidden');
      }});
    }});
  }});
}})();
</script>'''


# ============================================================================
# 05. MODERN CANADA — PM Gallery
# ============================================================================

# (name_en, name_zh, party, years, key_facts[])

MODERN_MILESTONES = [
    ("1947", "公民身份法案", "Canadian Citizenship Act"),
    ("1965", "楓葉旗", "Maple Leaf Flag"),
    ("1969", "雙語法", "Official Languages Act"),
    ("1971", "多元文化政策", "Multiculturalism Policy"),
    ("1982", "權利與自由憲章", "Charter of Rights & Freedoms"),
    ("1988", "多元文化法案", "Multiculturalism Act"),
    ("1989", "美加自由貿易協定", "USFTA → NAFTA → CUSMA"),
    ("1999", "Nunavut 成立", "Nunavut created"),
    ("2008", "寄宿學校道歉", "Residential schools apology"),
    ("2018", "10 元換 Viola Desmond", "$10 bill = Viola Desmond"),
    ("2021", "TRC Day 9/30", "Truth & Reconciliation Day"),
]


def build_modern_body():
    pm_cards = ""
    for name_en, name_zh, party, years, facts in PRIME_MINISTERS:
        facts_html = "".join(f"<li>{bi(f)}</li>" for f in facts)
        party_color = {
            "Liberal": "#d71920", "Conservative": "#1A4782",
            "Progressive Conservative": "#1A4782", "NDP": "#F58220",
        }.get(party, "#888")
        pm_cards += f'''
<div class="iv-pm-card">
  <div class="iv-pm-head">
    <h3>{name_en}</h3>
    <span class="iv-pm-zh">{name_zh}</span>
    <span class="iv-pm-party" style="background:{party_color}">{party}</span>
  </div>
  <div class="iv-pm-years">{years}</div>
  <ul class="iv-pm-facts">{facts_html}</ul>
</div>'''

    milestone_html = ""
    for year, zh, en in MODERN_MILESTONES:
        milestone_html += f'<div class="iv-ms"><span class="iv-ms-year">{year}</span><span class="iv-ms-zh">{zh}</span><span class="iv-ms-en">{en}</span></div>'

    return f'''{IV_SHARED_CSS}
<style>
.iv-pm-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin: 16px 0; }}
.iv-pm-card {{ background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; }}
.iv-pm-card:hover {{ border-color: var(--accent); }}
.iv-pm-head {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 4px; }}
.iv-pm-head h3 {{ margin: 0; font-size: 16px; flex: 1; min-width: 200px; }}
.iv-pm-zh {{ color: var(--ink); font-size: 16px; }}
.iv-pm-party {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: #fff; letter-spacing: 0.04em; font-family: -apple-system, system-ui, sans-serif; }}
.iv-pm-years {{ font-family: monospace; font-size: 12px; color: var(--muted); margin-bottom: 8px; }}
.iv-pm-facts {{ margin: 0; padding-left: 18px; font-size: 14px; }}
.iv-pm-facts li {{ margin: 3px 0; }}
.iv-milestones {{ background: #faf8f4; border-radius: 10px; padding: 12px 16px; margin: 16px 0; }}
.iv-ms {{ display: grid; grid-template-columns: 70px 1fr 1.5fr; gap: 10px; padding: 6px 0; border-bottom: 1px dashed var(--line); align-items: center; }}
.iv-ms:last-child {{ border-bottom: none; }}
.iv-ms-year {{ font-family: monospace; font-weight: 700; color: var(--accent); }}
.iv-ms-zh {{ font-weight: 600; font-size: 14px; }}
.iv-ms-en {{ color: #45403a; font-size: 14px; font-family: "Source Serif 4", Georgia, serif; }}
</style>
<div class="iv-hero">
  <h1>🇨🇦 現代加拿大 <small>Modern Canada: Prime Ministers &amp; Milestones</small></h1>
  <p>14 位戰後總理畫廊 + 11 件現代加拿大關鍵法案／事件。⭐ = 考試重點。</p>
</div>
<h2 class="iv-section-title">歷任總理 <small>Prime Ministers since Confederation</small></h2>
<div class="iv-pm-grid">{pm_cards}</div>
<h2 class="iv-section-title">現代加拿大里程碑 <small>Modern Milestones</small></h2>
<div class="iv-milestones">{milestone_html}</div>
'''


# ============================================================================
# 06. GOVERNMENT — Three diagrams
# ============================================================================

def build_government_body():
    return f'''{IV_SHARED_CSS}
<style>
.iv-gov-diagram {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 20px; margin: 20px 0; }}
.iv-gov-svg {{ width: 100%; height: auto; }}
.iv-gov-legend {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 14px; }}
.iv-gov-leg-item {{ display: flex; align-items: flex-start; gap: 8px; padding: 8px 10px; background: #faf8f4; border-radius: 6px; font-size: 13px; }}
.iv-gov-leg-item strong {{ display: block; margin-bottom: 2px; }}
.iv-gov-dot {{ width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; margin-top: 2px; }}
.iv-bill-flow {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }}
.iv-bill-step {{
  flex: 1; min-width: 130px;
  padding: 12px 14px; border-radius: 8px;
  background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%);
  border-left: 4px solid var(--accent);
  position: relative;
}}
.iv-bill-step .num {{ font-family: monospace; font-weight: 700; color: var(--accent); font-size: 18px; }}
.iv-bill-step .title {{ font-weight: 600; margin: 3px 0; }}
.iv-bill-step .desc {{ font-size: 12px; color: var(--muted); }}
</style>
<div class="iv-hero">
  <h1>🏛️ 加拿大政府架構 <small>How Canadians Govern Themselves</small></h1>
  <p>三張流程圖：三級政府職責、國會三部分、法案如何變法律。</p>
</div>

<h2 class="iv-section-title">圖 1：三級政府 <small>Three Levels of Government</small></h2>
<div class="iv-gov-diagram">
<svg viewBox="0 0 800 380" class="iv-gov-svg">
  <!-- Federal box -->
  <rect x="280" y="20" width="240" height="90" rx="10" fill="#c8102e"/>
  <text x="400" y="50" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">聯邦政府 Federal</text>
  <text x="400" y="72" text-anchor="middle" font-size="13" fill="#fff">PM 總理 + 國會 Parliament</text>
  <text x="400" y="92" text-anchor="middle" font-size="11" fill="#ffe0e0">國防、外交、移民、貨幣、刑法、漁業</text>

  <!-- Provincial box -->
  <rect x="50" y="170" width="240" height="90" rx="10" fill="#4a6fa5"/>
  <text x="170" y="200" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">省 / 領地 Provincial</text>
  <text x="170" y="222" text-anchor="middle" font-size="13" fill="#fff">Premier 省長 + 省議會</text>
  <text x="170" y="242" text-anchor="middle" font-size="11" fill="#dceaf5">教育、醫療、高速公路、自然資源</text>

  <!-- Municipal box -->
  <rect x="510" y="170" width="240" height="90" rx="10" fill="#5a9460"/>
  <text x="630" y="200" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">市政 Municipal</text>
  <text x="630" y="222" text-anchor="middle" font-size="13" fill="#fff">Mayor 市長 + 議會</text>
  <text x="630" y="242" text-anchor="middle" font-size="11" fill="#e0f0e0">除雪、回收、地方道路、公園、圖書館</text>

  <!-- Citizens box -->
  <rect x="280" y="310" width="240" height="60" rx="10" fill="#1f2328"/>
  <text x="400" y="335" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">公民 Citizens</text>
  <text x="400" y="357" text-anchor="middle" font-size="12" fill="#ccc">每 4 年投票選出各級政府</text>

  <!-- Arrows -->
  <line x1="370" y1="110" x2="200" y2="170" stroke="#1f2328" stroke-width="2"/>
  <line x1="430" y1="110" x2="600" y2="170" stroke="#1f2328" stroke-width="2"/>
  <line x1="200" y1="260" x2="320" y2="310" stroke="#1f2328" stroke-width="2"/>
  <line x1="600" y1="260" x2="480" y2="310" stroke="#1f2328" stroke-width="2"/>
  <line x1="400" y1="110" x2="400" y2="310" stroke="#1f2328" stroke-width="2" stroke-dasharray="4 4"/>
</svg>
<div class="iv-gov-legend">{_gov_legend_html()}</div>
</div>

<h2 class="iv-section-title">圖 2：國會三部分 <small>The Three Parts of Parliament</small></h2>
<div class="iv-gov-diagram">
<svg viewBox="0 0 800 400" class="iv-gov-svg">
  <!-- Sovereign -->
  <rect x="280" y="10" width="240" height="80" rx="10" fill="#7a4caf"/>
  <text x="400" y="38" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">君主 Sovereign 👑</text>
  <text x="400" y="60" text-anchor="middle" font-size="13" fill="#fff">King Charles III</text>
  <text x="400" y="78" text-anchor="middle" font-size="11" fill="#e0d0f0">由 Governor General Mary Simon 代表</text>

  <!-- Senate -->
  <rect x="60" y="150" width="280" height="100" rx="10" fill="#b0413e"/>
  <text x="200" y="178" text-anchor="middle" font-size="17" font-weight="700" fill="#fff">參議院 Senate</text>
  <text x="200" y="200" text-anchor="middle" font-size="13" fill="#fff">105 位參議員</text>
  <text x="200" y="218" text-anchor="middle" font-size="11" fill="#f0d0d0">由 GG 依 PM 建議任命</text>
  <text x="200" y="234" text-anchor="middle" font-size="11" fill="#f0d0d0">代表區域、審議法案</text>

  <!-- House of Commons -->
  <rect x="460" y="150" width="280" height="100" rx="10" fill="#5a9460"/>
  <text x="600" y="178" text-anchor="middle" font-size="17" font-weight="700" fill="#fff">眾議院 House of Commons</text>
  <text x="600" y="200" text-anchor="middle" font-size="13" fill="#fff">MPs 國會議員（席次隨人口重劃增加）</text>
  <text x="600" y="218" text-anchor="middle" font-size="11" fill="#d0e0d0">由公民投票選出（每 4 年）</text>
  <text x="600" y="234" text-anchor="middle" font-size="11" fill="#d0e0d0">"the people's house" 立法主力</text>

  <!-- Connecting lines -->
  <line x1="350" y1="90" x2="200" y2="150" stroke="#1f2328" stroke-width="2"/>
  <line x1="450" y1="90" x2="600" y2="150" stroke="#1f2328" stroke-width="2"/>

  <!-- Bill flow text -->
  <text x="400" y="290" text-anchor="middle" font-size="14" fill="#1f2328" font-weight="600">法案先由眾議院辯論 → 送參議院審議 → 君主（GG 代簽）御准 → 成法</text>
  <text x="400" y="320" text-anchor="middle" font-size="12" fill="#5d646d">五大政黨：Liberal、Conservative、NDP、Bloc Québécois、Green</text>
  <text x="400" y="345" text-anchor="middle" font-size="12" fill="#5d646d">⭐ 加拿大是 Constitutional Monarchy（君主立憲）+ Parliamentary Democracy（議會民主）+ Federal State（聯邦制）</text>
</svg>
</div>

<h2 class="iv-section-title">圖 3：法案如何變法律 <small>How a Bill Becomes Law (7 steps)</small></h2>
<div class="iv-gov-diagram">
<div class="iv-bill-flow">{_bill_steps_html()}</div>
<p style="font-size:13px; color:var(--muted); margin-top:8px">⭐ <strong>考試重點</strong>：3 讀＋委員會＋送參議院＋御准。法案在每院都要 3 讀。</p>
</div>
'''


# ============================================================================
# 07. FEDERAL ELECTIONS
# ============================================================================



def build_elections_body():
    party_cards = ""
    for en, zh, color, leader, status, facts in PARTIES:
        facts_html = "".join(f"<li>{bi(f)}</li>" for f in facts)
        party_cards += f'''
<div class="iv-party-card" style="border-top-color:{color}">
  <div class="iv-party-name">{en}</div>
  <div class="iv-party-zh">{zh}</div>
  <div class="iv-party-leader">領袖：<strong>{leader}</strong></div>
  <div class="iv-party-status">{bi(status)}</div>
  <ul class="iv-party-facts">{facts_html}</ul>
</div>'''

    return f'''{IV_SHARED_CSS}
<style>
.iv-party-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 16px 0; }}
.iv-party-card {{ background: #fff; border: 1px solid var(--line); border-top-width: 4px; border-radius: 10px; padding: 14px 16px; }}
.iv-party-name {{ font-weight: 700; font-size: 15px; }}
.iv-party-zh {{ color: var(--ink); font-size: 15px; font-weight: 700; margin-bottom: 6px; }}
.iv-party-leader {{ font-size: 13px; margin: 8px 0 4px; }}
.iv-party-status {{ font-size: 12px; color: var(--muted); font-style: italic; margin-bottom: 8px; }}
.iv-party-facts {{ margin: 0; padding-left: 18px; font-size: 13px; }}
.iv-vote-steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin: 16px 0; }}
.iv-vote-step {{ background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%); padding: 14px 16px; border-radius: 8px; border-left: 4px solid var(--accent); }}
.iv-vote-step .icon {{ font-size: 24px; }}
.iv-vote-step strong {{ display: block; margin: 4px 0; }}
.iv-vote-step p {{ margin: 0; font-size: 12px; color: var(--muted); }}
.iv-fact-row {{ display: grid; grid-template-columns: 180px 1fr; gap: 10px; padding: 8px 0; border-bottom: 1px dashed var(--line); font-size: 14px; }}
.iv-fact-row strong {{ color: var(--accent); }}
</style>
<div class="iv-hero">
  <h1>🗳️ 加拿大聯邦選舉 <small>Federal Elections</small></h1>
  <p>5 大政黨 + 投票資格 + 選舉流程 + 5 個必考重點。</p>
</div>

<h2 class="iv-section-title">5 大主要政黨 <small>Major Political Parties</small></h2>
<div class="iv-party-grid">{party_cards}</div>

<h2 class="iv-section-title">投票資格 &amp; 流程 <small>Who Can Vote &amp; Voting Procedures</small></h2>
<div class="iv-vote-steps">{_vote_steps_html()}</div>

<h2 class="iv-section-title">考試 5 大必背重點 <small>Five Must-Know Facts</small></h2>
<div class="iv-facts">{_must_know_html()}</div>
'''


# ============================================================================
# 08. JUSTICE SYSTEM — Court hierarchy
# ============================================================================



def build_justice_body():
    principles_cards = ""
    for zh, en, desc in JUSTICE_PRINCIPLES:
        principles_cards += f'<div class="iv-principle"><h4>{zh}</h4><div class="en">{en}</div><p>{bi(desc)}</p></div>'

    return f'''{IV_SHARED_CSS}
<style>
.iv-court-hierarchy {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 20px; margin: 16px 0; }}
.iv-court-svg {{ width: 100%; height: auto; }}
.iv-principles-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }}
.iv-principle {{ background: #fff; border-left: 4px solid var(--accent); padding: 12px 16px; border-radius: 6px; }}
.iv-principle h4 {{ margin: 0 0 2px; font-size: 15px; }}
.iv-principle .en {{ font-size: 15px; color: #45403a; font-family: "Source Serif 4", Georgia, serif; margin-bottom: 6px; }}
.iv-principle p {{ margin: 0; font-size: 13px; }}
.iv-rcmp {{ background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%); padding: 20px 24px; border-radius: 10px; margin: 16px 0; }}
.iv-rcmp h3 {{ margin: 0 0 8px; }}
.iv-rcmp ul {{ margin: 8px 0 0; padding-left: 20px; font-size: 14px; }}
</style>
<div class="iv-hero">
  <h1>⚖️ 加拿大司法系統 <small>The Justice System</small></h1>
  <p>5 大法律原則 + 4 級法院階層 + RCMP 角色。</p>
</div>

<h2 class="iv-section-title">5 大法律原則 <small>Five Principles of Canadian Law</small></h2>
<div class="iv-principles-grid">{principles_cards}</div>

<h2 class="iv-section-title">4 級法院階層 <small>The Courts</small></h2>
<div class="iv-court-hierarchy">
<svg viewBox="0 0 800 480" class="iv-court-svg">
  <!-- Top: Supreme Court -->
  <rect x="280" y="20" width="240" height="80" rx="10" fill="#c8102e"/>
  <text x="400" y="48" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">Supreme Court of Canada</text>
  <text x="400" y="70" text-anchor="middle" font-size="13" fill="#fff">最高法院（9 位法官）</text>
  <text x="400" y="90" text-anchor="middle" font-size="11" fill="#ffe0e0">最終裁判，憲法解釋</text>

  <!-- Level 2: Appeals -->
  <rect x="180" y="140" width="440" height="70" rx="10" fill="#b0413e"/>
  <text x="400" y="168" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">Provincial Courts of Appeal</text>
  <text x="400" y="190" text-anchor="middle" font-size="12" fill="#fff">省上訴法院 / Federal Court of Appeal</text>

  <!-- Level 3: Superior -->
  <rect x="120" y="250" width="560" height="70" rx="10" fill="#7a8c5c"/>
  <text x="400" y="278" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">Provincial / Superior Courts</text>
  <text x="400" y="300" text-anchor="middle" font-size="12" fill="#fff">省高等法院（嚴重刑事、民事大案）</text>

  <!-- Level 4: Provincial -->
  <rect x="60" y="360" width="680" height="70" rx="10" fill="#4a6fa5"/>
  <text x="400" y="388" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">Provincial Courts</text>
  <text x="400" y="410" text-anchor="middle" font-size="12" fill="#fff">省級地方法院（最多日常案件、輕罪、交通）</text>

  <!-- Arrows -->
  <line x1="400" y1="430" x2="400" y2="100" stroke="#1f2328" stroke-width="2" marker-end="url(#arr)"/>
  <text x="430" y="450" font-size="11" fill="var(--muted)">↑ 上訴方向</text>

  <defs>
    <marker id="arr" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#1f2328"/>
    </marker>
  </defs>
</svg>
<p style="font-size:13px; color:var(--muted); margin-top:12px">⭐ <strong>考試重點</strong>：四級法院、Supreme Court 9 位法官、最高法院判決最終。</p>
</div>

<h2 class="iv-section-title">皇家騎警 RCMP（Royal Canadian Mounted Police）</h2>
<div class="iv-rcmp">
<h3>🐎 加拿大國家警察</h3>
<ul>{_rcmp_html()}</ul>
</div>
'''


# ============================================================================
# 09. NATIONAL SYMBOLS — visual gallery
# ============================================================================





def build_symbols_body():
    symbol_cards = ""
    for emoji, zh, en, brief, facts in SYMBOLS:
        facts_html = "".join(f"<li>{bi(f)}</li>" for f in facts)
        symbol_cards += f'''
<div class="iv-sym-card">
  <div class="iv-sym-emoji">{emoji}</div>
  <h3>{zh} <span class="en">{en}</span></h3>
  <p class="brief">{bi(brief)}</p>
  <ul>{facts_html}</ul>
</div>'''

    currency_rows = ""
    for denom, en, zh, note in CURRENCY_FIGURES:
        currency_rows += f'<div class="iv-bill-row"><div class="denom">{denom}</div><div class="figure"><strong>{en}</strong><div class="zh">{zh}</div></div><div class="note">{bi(note)}</div></div>'

    holidays_rows = ""
    for date, en, zh in NATIONAL_HOLIDAYS:
        is_star = "⭐" in date
        holidays_rows += f'<div class="iv-hol-row {"star" if is_star else ""}"><div class="date">{date}</div><div class="hol-en">{en}</div><div class="hol-zh">{zh}</div></div>'

    return f'''{IV_SHARED_CSS}
<style>
.iv-sym-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin: 16px 0; }}
.iv-sym-card {{ background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; }}
.iv-sym-emoji {{ font-size: 40px; line-height: 1; }}
.iv-sym-card h3 {{ margin: 8px 0 4px; font-size: 16px; }}
.iv-sym-card h3 .en {{ color: #45403a; font-weight: 400; font-size: 16px; font-family: "Source Serif 4", Georgia, serif; }}
.iv-sym-card .brief {{ font-size: 13px; color: var(--muted); margin: 0 0 8px; }}
.iv-sym-card ul {{ margin: 0; padding-left: 18px; font-size: 13px; }}
.iv-sym-card ul li {{ margin: 3px 0; }}
.iv-bill-row {{ display: grid; grid-template-columns: 70px 1fr 2fr; gap: 14px; padding: 10px 0; border-bottom: 1px dashed var(--line); align-items: center; font-size: 14px; }}
.iv-bill-row .denom {{ font-family: monospace; font-weight: 700; font-size: 20px; color: var(--accent); }}
.iv-bill-row .zh {{ font-size: 12px; color: var(--muted); }}
.iv-bill-row .note {{ font-size: 13px; }}
.iv-hol-row {{ display: grid; grid-template-columns: 120px 1fr 1fr; gap: 10px; padding: 7px 10px; border-bottom: 1px dashed var(--line); font-size: 15px; align-items: center; }}
.iv-hol-row.star {{ background: linear-gradient(90deg, #fff8e8 0%, transparent 100%); border-radius: 4px; }}
.iv-hol-row .date {{ font-family: monospace; font-size: 12px; color: var(--muted); }}
.iv-hol-row .hol-en {{ font-weight: 600; }}
.iv-hol-row .hol-zh {{ color: var(--ink); font-weight: 600; }}
</style>
<div class="iv-hero">
  <h1>🍁 加拿大國家象徵圖鑑 <small>Canadian Symbols</small></h1>
  <p>象徵、鈔票、硬幣、國定假日——視覺整理一次到位。</p>
</div>

<h2 class="iv-section-title">10 大國家象徵 <small>Ten National Symbols</small></h2>
<div class="iv-sym-grid">{symbol_cards}</div>

<h2 class="iv-section-title">鈔票上的人物 <small>Faces on Banknotes</small></h2>
<div>{currency_rows}</div>

<h2 class="iv-section-title">硬幣上的動物 <small>Animals on Coins</small></h2>
<div class="iv-card-grid" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr))">
  {_coins_html()}
</div>

<h2 class="iv-section-title">12 個國定/重要假日 <small>National Public Holidays</small></h2>
<div>{holidays_rows}</div>
'''


# ============================================================================
# 10. CANADA'S ECONOMY
# ============================================================================




def build_economy_body():
    pie_segments = ""
    cumulative = 0
    for zh, en, pct, color, _ in INDUSTRIES:
        start = cumulative
        cumulative += pct
        end = cumulative
        # Convert to SVG arc
        start_angle = start * 3.6 - 90  # 0 at top
        end_angle = end * 3.6 - 90
        import math
        cx, cy, r = 150, 150, 120
        sx = cx + r * math.cos(math.radians(start_angle))
        sy = cy + r * math.sin(math.radians(start_angle))
        ex = cx + r * math.cos(math.radians(end_angle))
        ey = cy + r * math.sin(math.radians(end_angle))
        large_arc = 1 if pct > 50 else 0
        path = f"M {cx} {cy} L {sx:.1f} {sy:.1f} A {r} {r} 0 {large_arc} 1 {ex:.1f} {ey:.1f} Z"
        # Label position
        mid_angle = (start + end) / 2 * 3.6 - 90
        lx = cx + 70 * math.cos(math.radians(mid_angle))
        ly = cy + 70 * math.sin(math.radians(mid_angle))
        pie_segments += f'<path d="{path}" fill="{color}"/><text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">{pct}%</text>'

    industry_cards = ""
    for zh, en, pct, color, desc in INDUSTRIES:
        industry_cards += f'''
<div class="iv-ind-card" style="border-top-color:{color}">
  <div class="iv-ind-pct" style="color:{color}">{pct}%</div>
  <h4>{zh}</h4>
  <div class="en">{en}</div>
  <p>{bi(desc)}</p>
</div>'''

    trade_rows = ""
    for k, v, note in TRADE_FACTS:
        trade_rows += f'<div class="iv-trade-row"><div class="key">{bi(k)}</div><div class="val"><strong>{bi(v)}</strong><div class="note">{bi(note)}</div></div></div>'

    return f'''{IV_SHARED_CSS}
<style>
.iv-pie-wrap {{ display: flex; flex-wrap: wrap; gap: 24px; align-items: center; margin: 16px 0; }}
.iv-pie {{ width: 300px; max-width: 100%; }}
.iv-ind-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; flex: 1; min-width: 280px; }}
.iv-ind-card {{ background: #fff; border: 1px solid var(--line); border-top-width: 4px; border-radius: 10px; padding: 14px 16px; }}
.iv-ind-pct {{ font-size: 28px; font-weight: 700; font-family: monospace; }}
.iv-ind-card h4 {{ margin: 4px 0; font-size: 16px; }}
.iv-ind-card .en {{ font-size: 16px; color: #45403a; font-family: "Source Serif 4", Georgia, serif; margin-bottom: 6px; }}
.iv-ind-card p {{ margin: 0; font-size: 13px; }}
.iv-trade-row {{ display: grid; grid-template-columns: 160px 1fr; gap: 16px; padding: 10px 0; border-bottom: 1px dashed var(--line); font-size: 14px; }}
.iv-trade-row .key {{ font-weight: 600; color: var(--accent); }}
.iv-trade-row .note {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
</style>
<div class="iv-hero">
  <h1>💼 加拿大經濟 <small>Canada's Economy</small></h1>
  <p>三大產業比例 + 5 個必考經濟事實。</p>
</div>

<h2 class="iv-section-title">三大產業 <small>Three Main Types of Industries</small></h2>
<div class="iv-pie-wrap">
  <svg viewBox="0 0 300 300" class="iv-pie">{pie_segments}</svg>
  <div class="iv-ind-cards">{industry_cards}</div>
</div>

<h2 class="iv-section-title">5 大必背經濟事實 <small>Five Economic Facts</small></h2>
<div>{trade_rows}</div>

<div class="iv-hero" style="margin-top:24px">
<h3 style="margin:0 0 8px">⭐ 考試重點記憶法</h3>
<p style="margin:0">「<strong>七成五服務、美國買、CUSMA 後 NAFTA、G7 圈、$2 兆 GDP</strong>」一句口訣抓住考試所有問題。</p>
</div>
'''


# ============================================================================
# HUB INDEX
# ============================================================================

def build_interactive_index_body():
    return '''
<style>
.iv-hub-hero {
  background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%);
  border-left: 4px solid var(--accent);
  padding: 22px 26px; border-radius: 10px; margin: 16px 0 28px;
}
.iv-hub-hero h1 { margin: 0 0 6px; font-size: 26px; border: none; padding: 0; }
.iv-hub-hero p { margin: 0; color: var(--muted); font-size: 15px; }
.iv-hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 24px 0; }
.iv-hub-card {
  display: block; padding: 18px 20px; background: #fff;
  border: 1px solid var(--line); border-radius: 12px;
  text-decoration: none; color: var(--ink);
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
}
.iv-hub-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  text-decoration: none;
}
.iv-hub-emoji { font-size: 36px; line-height: 1; display: block; margin-bottom: 8px; }
.iv-hub-chap { font-size: 11px; color: var(--accent); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; font-family: -apple-system, system-ui, sans-serif; }
.iv-hub-title { font-weight: 700; font-size: 17px; margin: 4px 0; }
.iv-hub-desc { font-size: 13px; color: var(--muted); line-height: 1.5; }
</style>

<div class="iv-hub-hero">
  <h1>🎯 每章重點互動記憶 <small>Interactive Memory Modules</small></h1>
  <p>把抽象的考試內容變成圖、地圖、時間軸、流程——用視覺記憶取代死背。對應教材 04~11 章。</p>
</div>

<div class="iv-hub-grid">
  <a href="history.html" class="iv-hub-card">
    <span class="iv-hub-emoji">📜</span>
    <div class="iv-hub-chap">04 章</div>
    <div class="iv-hub-title">歷史時間軸</div>
    <div class="iv-hub-desc">1497 → 2021，41 事件，5 時代色標、可篩選</div>
  </a>
  <a href="people.html" class="iv-hub-card">
    <span class="iv-hub-emoji">👤</span>
    <div class="iv-hub-chap">04–09 章 · 人物</div>
    <div class="iv-hub-title">人物時間軸</div>
    <div class="iv-hub-desc">68 位人物：哪年、什麼人、哪國人、在哪裡、為何有名，可連續朗讀</div>
  </a>
  <a href="joining.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🗺️</span>
    <div class="iv-hub-chap">04 章 · 地圖</div>
    <div class="iv-hub-title">聯邦擴張時間軸</div>
    <div class="iv-hub-desc">誰哪一年加入、首府在哪裡，中英對照＋背誦口訣</div>
  </a>
  <a href="story-04.html" class="iv-hub-card">
    <span class="iv-hub-emoji">📖</span>
    <div class="iv-hub-chap">04 章 · 邊聽邊玩</div>
    <div class="iv-hub-title">歷史故事聽學</div>
    <div class="iv-hub-desc">中文故事音頻＋記憶卡＋小測驗，手機隨時聽</div>
  </a>
  <a href="modern.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🇨🇦</span>
    <div class="iv-hub-chap">05 章</div>
    <div class="iv-hub-title">現代加拿大</div>
    <div class="iv-hub-desc">14 位總理畫廊 + 11 件現代里程碑</div>
  </a>
  <a href="government.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🏛️</span>
    <div class="iv-hub-chap">06 章</div>
    <div class="iv-hub-title">政府架構圖</div>
    <div class="iv-hub-desc">3 張圖：三級政府、國會三部分、法案 7 步驟</div>
  </a>
  <a href="elections.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🗳️</span>
    <div class="iv-hub-chap">07 章</div>
    <div class="iv-hub-title">聯邦選舉</div>
    <div class="iv-hub-desc">5 大政黨卡 + 投票流程 + 5 必考重點</div>
  </a>
  <a href="justice.html" class="iv-hub-card">
    <span class="iv-hub-emoji">⚖️</span>
    <div class="iv-hub-chap">08 章</div>
    <div class="iv-hub-title">司法系統</div>
    <div class="iv-hub-desc">5 原則 + 4 級法院金字塔 + RCMP</div>
  </a>
  <a href="symbols.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🍁</span>
    <div class="iv-hub-chap">09 章</div>
    <div class="iv-hub-title">國家象徵圖鑑</div>
    <div class="iv-hub-desc">10 象徵 + 鈔票人物 + 硬幣動物 + 12 假日</div>
  </a>
  <a href="economy.html" class="iv-hub-card">
    <span class="iv-hub-emoji">💼</span>
    <div class="iv-hub-chap">10 章</div>
    <div class="iv-hub-title">加拿大經濟</div>
    <div class="iv-hub-desc">三大產業圓餅圖 + 5 必考經濟事實</div>
  </a>
  <a href="geography.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🗺️</span>
    <div class="iv-hub-chap">11 章</div>
    <div class="iv-hub-title">地圖與省份</div>
    <div class="iv-hub-desc">13 省領地互動地圖 + Ontario 重點</div>
  </a>
</div>

<p style="color: var(--muted); font-size: 14px;">
  💡 學習建議：先看互動式抓住整體結構（圖／時間軸／流程），再回中英對照精讀文字、daily-quiz 驗收。
</p>
'''


# ============================================================================
# STORY MODE — bilingual audio storytelling + memory cards + light quiz
#
# Designed for: 中文母語、記性有限、對英文考試有恐懼感的學習者。
# 故事只用中文講，英文只在關鍵詞出現、放慢重複兩次，不做整段英文聽力。
# ============================================================================

STORY_04_SCENES = [
    ("🏕️", "原住民：加拿大最早的主人", [
        ("zh", "在歐洲人出現的好幾千年前，加拿大這片土地上已經住著許多原住民族——他們有自己的政府、自己的語言，還有自己的貿易網絡。"),
        ("zh", "可惜歐洲人後來帶來的疾病，讓原住民人口一下子少了將近一半到八成，非常慘烈。"),
    ]),
    ("⛵", "第一批歐洲人：維京人、卡伯特、卡蒂亞", [
        ("zh", "大概西元一千年，一群從冰島來的維京人，先到了格陵蘭，接著一路划到了紐芬蘭島，成為第一批踏上北美的歐洲人。"),
        ("zh", "1497 年，一位替英國國王工作的義大利探險家登陸紐芬蘭，宣告這塊地是英國的，他的名字是——"),
        ("en", "John Cabot. John Cabot."),
        ("zh", "接下來換法國人出手了。1534 到 1542 年之間，"),
        ("en", "Jacques Cartier."),
        ("zh", "三次橫渡大西洋，替法國宣告主權。他還從原住民嚮導口中聽到一個詞，叫「卡那塔」，意思是「村莊」——這就是「加拿大」這個名字的由來！"),
    ]),
    ("🏰", "新法蘭西誕生：魁北克城的誕生", [
        ("zh", "1608 年，法國探險家"),
        ("en", "Samuel de Champlain."),
        ("zh", "在今天的魁北克市蓋了一座堡壘，他被稱為「新法蘭西之父」。從此，法國人跟原住民一起靠著毛皮貿易，把生意做到哈德遜灣到墨西哥灣那麼大！"),
    ]),
    ("⚔️", "英法大對決：亞伯拉罕平原之役", [
        ("zh", "英國跟法國為了爭奪北美，打了一百多年的仗。決定勝負的關鍵一戰，發生在 1759 年的魁北克市，叫做——"),
        ("en", "Battle of the Plains of Abraham. Battle of the Plains of Abraham."),
        ("zh", "這一戰非常戲劇化：英軍將領沃夫，跟法軍將領蒙特卡姆，兩個人都在戰場上陣亡了！最後英國贏了，法國在北美的帝國，就這樣結束了。"),
    ]),
    ("🚣", "忠貞派大遷徙：四萬人逃亡潮", [
        ("zh", "1776 年，美國獨立革命爆發。大約四萬個效忠英國的人，不想留在剛獨立的美國，就往北逃到了加拿大，他們被稱為——"),
        ("en", "United Empire Loyalists."),
        ("zh", "這批新移民裡面還包括了自由黑人，跟一位莫霍克族的領袖約瑟夫．布蘭特。英國後來把魁北克分成了「上加拿大」跟「下加拿大」，也就是今天的安大略跟魁北克。"),
    ]),
    ("⛓️", "廢除奴隸制的先鋒", [
        ("zh", "1793 年，上加拿大的副總督"),
        ("en", "John Graves Simcoe."),
        ("zh", "推動立法，讓上加拿大成為整個大英帝國第一個禁止奴隸制的地方！後來還有三萬名美國黑奴，經過一條叫「地下鐵路」的秘密逃亡路線，來到加拿大尋求自由。"),
    ]),
    ("🎖️", "1812 年戰爭：保家衛國", [
        ("zh", "1812 年，美國出兵想要併吞加拿大。這時候站出來三位英雄：英軍司令布洛克，原住民首領特庫姆塞，還有一位傳奇女性——"),
        ("en", "Laura Secord."),
        ("zh", "她走了三十公里的路去通報美軍的作戰計畫，被視為加拿大的民族英雄。最後加拿大打贏了，沒有被美國併吞——這是加拿大能獨立存在到今天的關鍵一戰！"),
    ]),
    ("🎂", "建國的那一天：1867 年 7 月 1 日", [
        ("zh", "終於，來到整堂課最重要的一天！安大略、魁北克、新斯科細亞、新布藍瑞克這四個殖民地，決定聯合組成一個國家，這一天就叫——"),
        ("en", "Confederation. Confederation."),
        ("zh", "這就是加拿大的生日，後來變成了「加拿大日」。第一任總理，是——"),
        ("en", "Sir John Alexander Macdonald."),
        ("zh", "他的頭像，現在就印在十塊錢加幣的鈔票上。"),
    ]),
    ("🚂", "版圖擴張：橫貫鐵路的血與淚", [
        ("zh", "建國之後，加拿大的版圖越變越大。把東西兩岸串起來的關鍵建設，是 1885 年完工的——"),
        ("en", "Canadian Pacific Railway."),
        ("zh", "這條鐵路是由一萬五千名華人工人辛苦建造的，很多人因為工作環境太惡劣而喪命。完工那年，加拿大政府居然還對華人徵收「人頭稅」，一直到 2006 年，當時的總理哈珀才正式道歉並補償。"),
    ]),
    ("🗳️", "女性投票權：從曼尼托巴到最高法院", [
        ("zh", "1916 年，滿尼托巴省成為加拿大第一個讓女性投票的省份。到了 1929 年，五位女性運動者打贏了一場官司，叫做——"),
        ("en", "Persons Case."),
        ("zh", "她們證明了女性在法律上也算是「人」，從此才有資格進入加拿大的參議院。這五位女性，被稱為「Famous Five」。"),
    ]),
    ("🎖️", "兩次世界大戰：加拿大打出了名號", [
        ("zh", "第一次世界大戰，加拿大軍隊在法國打了一場關鍵戰役，叫做——"),
        ("en", "Battle of Vimy Ridge."),
        ("zh", "這一戰被認為是加拿大從英國殖民地，走向獨立國家認同的轉捩點。到了第二次世界大戰，加拿大軍隊參加了 1944 年 6 月 6 日的諾曼第登陸，那個海灘的代號叫——"),
        ("en", "Juno Beach."),
    ]),
    ("🍁", "現代加拿大：憲法回家了", [
        ("zh", "1965 年，現在這面紅白相間的楓葉旗正式誕生。到了 1982 年，時任總理老杜魯道推動了加拿大現代史上最重要的大事——把原本放在英國的加拿大憲法，正式「接回」加拿大，同時加入了保障所有人基本權利的——"),
        ("en", "Canadian Charter of Rights and Freedoms."),
        ("zh", "從這一刻起，加拿大才真正完全掌握了自己的命運。這，就是加拿大歷史，從原住民時代一路走到今天的故事。"),
    ]),
]

# (標題, 中文口訣, 補充細節)
STORY_04_CARDS = [
    ("1867/7/1 建國", "一八六七七月一，四省聯手把家立", "安大略、魁北克、新斯科細亞、新布藍瑞克 四個原始省份，Confederation 誕生"),
    ("1759 亞伯拉罕平原之役", "沃夫蒙特卡姆，雙雙戰死魁北克", "英軍 Wolfe 勝、法軍 Montcalm 敗，兩位將軍皆陣亡，法國在美洲帝國結束"),
    ("1812 戰爭", "一二年戰爭打得凶，加拿大保住沒被吞", "Brock、Tecumseh、Laura Secord 三英雄，保住加拿大不被美國併吞"),
    ("1885 橫貫鐵路", "一八八五鐵路通，華工血汗立奇功", "15,000 華工建 CPR，後遭徵人頭稅，2006 年 Harper 道歉補償"),
    ("1917 Vimy Ridge", "一九一七維米嶺，加拿大打出了名", "一戰關鍵戰役，被視為加拿大國家認同的轉捩點"),
    ("1929 Persons Case", "一九二九五姐妹，打贏官司變法人", "Famous Five 打贏官司，女性法律上正式算「person」，可進參議院"),
    ("1793 廢除奴隸制", "英帝國內第一個，上加拿大先禁奴", "Simcoe 推動立法，大英帝國第一個禁奴隸制的地方；後有 Underground Railroad"),
    ("1982 憲法回家", "八二年老杜魯道，憲法回家權利到", "Constitution Act + Charter of Rights and Freedoms，加拿大憲法正式脫離英國"),
]

# (題目, [選項3個], 正解索引, 解說)
STORY_04_QUIZ = [
    ("加拿大的「生日」Confederation 是哪一天？", ["1867 年 7 月 1 日", "1867 年 1 月 1 日", "1982 年 7 月 1 日"], 0,
     "1867/7/1，四個原始省份（安大略、魁北克、新斯科細亞、新布藍瑞克）組成加拿大自治領。"),
    ("加拿大第一任總理是誰？", ["Sir John A. Macdonald", "Pierre Trudeau", "Wilfrid Laurier"], 0,
     "Sir John Alexander Macdonald，頭像印在 $10 加幣鈔票上。"),
    ("1759 年英法決戰的地點叫什麼？", ["Battle of the Plains of Abraham", "Battle of Vimy Ridge", "Battle of Queenston Heights"], 0,
     "地點在魁北克市，英軍 Wolfe 對法軍 Montcalm，兩位將軍都戰死。"),
    ("1929 年 Persons Case 打贏官司的是哪一群人？", ["Famous Five（五位女性）", "United Empire Loyalists", "Fathers of Confederation"], 0,
     "五位女性運動者證明女性在法律上算「person」，可以進入參議院。"),
    ("加拿大憲法「回家」（patriated）是哪一年？", ["1982 年", "1867 年", "1965 年"], 0,
     "1982 年，PM Pierre Trudeau 推動 Constitution Act，同時通過 Charter of Rights and Freedoms。"),
    ("1885 年橫貫鐵路（CPR）完工，主要由誰辛苦建造？", ["華人工人", "英國軍隊", "美國移民"], 0,
     "15,000 名華工參與建造，後來還被徵收人頭稅，2006 年 Harper 總理道歉補償。"),
]

STORY_SHARED_CSS = """
<style>
.story-player { background:#fff; border:1px solid var(--line); border-radius:12px; padding:18px 20px; margin:16px 0 28px; }
.story-controls { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:14px; }
.story-btn { appearance:none; border:2px solid var(--accent); background:#fff; color:var(--accent); padding:8px 16px; border-radius:20px; font-size:14px; font-weight:600; cursor:pointer; font-family:-apple-system,system-ui,sans-serif; }
.story-btn-main { background:var(--accent); color:#fff; }
.story-btn:disabled { opacity:0.4; cursor:default; }
.story-progress { font-size:13px; color:var(--muted); margin-left:auto; }
.story-transcript { max-height:440px; overflow-y:auto; padding-right:6px; }
.story-scene { padding:14px 0; border-bottom:1px dashed var(--line); }
.story-scene:last-child { border-bottom:none; }
.story-scene-head { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
.story-emoji { font-size:22px; }
.story-scene-head h3 { margin:0; font-size:15px; }
.story-text { margin:0; line-height:2; font-size:15px; }
.story-chunk { transition:background 0.2s; border-radius:4px; padding:1px 2px; }
.story-chunk.story-en { color:#8a1f2e; font-weight:600; font-family:Georgia,serif; }
.story-chunk.current { background:#ffe9b3; }

.mem-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:16px 0 28px; perspective:1000px; }
.mem-card { min-height:150px; cursor:pointer; }
.mem-card-inner { position:relative; width:100%; height:100%; min-height:150px; transition:transform 0.5s; transform-style:preserve-3d; }
.mem-card.flipped .mem-card-inner { transform:rotateY(180deg); }
.mem-card-front, .mem-card-back { position:absolute; inset:0; backface-visibility:hidden; border-radius:10px; padding:16px 18px; border:1px solid var(--line); background:#fff; display:flex; flex-direction:column; justify-content:center; }
.mem-card-back { transform:rotateY(180deg); background:linear-gradient(135deg,#fff 0%,#fff8f8 100%); border-color:var(--accent); }
.mem-title { font-weight:700; font-size:14px; color:var(--accent); margin-bottom:8px; }
.mem-hook { font-size:16px; font-weight:600; line-height:1.5; }
.mem-tap { font-size:11px; color:var(--muted); margin-top:10px; }
.mem-detail { font-size:14px; line-height:1.6; }

.quiz-q { background:#fff; border:1px solid var(--line); border-radius:10px; padding:14px 18px; margin-bottom:12px; }
.quiz-qtext { font-weight:600; margin-bottom:10px; }
.quiz-opts { display:flex; flex-direction:column; gap:8px; }
.quiz-opt { appearance:none; text-align:left; padding:10px 14px; border-radius:8px; border:1px solid var(--line); background:#faf8f4; cursor:pointer; font-size:14px; font-family:-apple-system,system-ui,sans-serif; }
.quiz-opt.correct { border-color:#2e7d46; background:#e8f5ea; }
.quiz-opt.wrong { border-color:#c8102e; background:#fbe9ec; }
.quiz-opt:disabled { cursor:default; }
.quiz-explain { margin-top:10px; font-size:13px; color:var(--muted); background:#f3efe6; padding:10px 12px; border-radius:8px; }
.quiz-score { font-size:16px; font-weight:700; text-align:center; margin:16px 0; }
.quiz-reset { display:block; margin:0 auto; }
</style>
"""


def render_story_page(num, title_zh, subtitle, scenes, memory_cards, quiz):
    root_id = f"story-{num}-root"

    scenes_html = ""
    for i, (emoji, title, chunks) in enumerate(scenes):
        chunk_spans = ""
        for lang, text in chunks:
            cls = "story-chunk story-en" if lang == "en" else "story-chunk story-zh"
            chunk_spans += f'<span class="{cls}" data-lang="{lang}">{text}</span> '
        scenes_html += f'''
<div class="story-scene" data-scene="{i}">
  <div class="story-scene-head"><span class="story-emoji">{emoji}</span><h3>{title}</h3></div>
  <p class="story-text">{chunk_spans}</p>
</div>'''

    cards_html = ""
    for title, hook, detail in memory_cards:
        cards_html += f'''
<div class="mem-card">
  <div class="mem-card-inner">
    <div class="mem-card-front">
      <div class="mem-title">{title}</div>
      <div class="mem-hook">「{hook}」</div>
      <div class="mem-tap">點一下看細節 →</div>
    </div>
    <div class="mem-card-back">
      <div class="mem-detail">{detail}</div>
    </div>
  </div>
</div>'''

    quiz_html = ""
    for qi, (q, opts, ans, explain) in enumerate(quiz):
        opts_html = ""
        for oi, opt in enumerate(opts):
            opts_html += f'<button class="quiz-opt" data-correct="{1 if oi == ans else 0}" type="button">{opt}</button>'
        quiz_html += f'''
<div class="quiz-q" data-qidx="{qi}">
  <div class="quiz-qtext">{qi + 1}. {q}</div>
  <div class="quiz-opts">{opts_html}</div>
  <div class="quiz-explain" style="display:none">💡 {explain}</div>
</div>'''

    return f'''{IV_SHARED_CSS}{STORY_SHARED_CSS}
<div class="iv-hero">
  <h1>📖 {num} {title_zh}：故事聽學</h1>
  <p>{subtitle}——用中文故事講一遍，關鍵英文詞放慢重複兩次。開車、走路、躺著都能聽，聽完再翻記憶卡、玩小測驗。</p>
</div>

<div class="story-player" id="{root_id}">
  <div class="story-controls">
    <button class="story-btn story-btn-main story-play" type="button">▶ 播放故事</button>
    <button class="story-btn story-restart" type="button">⏮ 重來</button>
    <span class="story-progress">尚未開始</span>
  </div>
  <div class="story-transcript">
{scenes_html}
  </div>
</div>

<h2 class="iv-section-title">🧠 {len(memory_cards)} 張記憶卡（點一下翻面看細節）</h2>
<div class="mem-grid" id="mem-{num}-root">{cards_html}</div>

<h2 class="iv-section-title">🎮 小測驗（{len(quiz)} 題，答錯也沒關係，看解說就好）</h2>
<div class="quiz-wrap" id="quiz-{num}-root">{quiz_html}</div>
<div class="quiz-score" data-quiz-total="{len(quiz)}"></div>
<button class="story-btn quiz-reset" type="button">🔄 重新測驗</button>

<script>
(function() {{
  var root = document.getElementById('{root_id}');
  var quizRoot = document.getElementById('quiz-{num}-root');
  var memRoot = document.getElementById('mem-{num}-root');
  if (!root && !quizRoot && !memRoot) return;
  var synth = window.speechSynthesis;

  // ---------- memory card flip ----------
  if (memRoot) {{
    memRoot.addEventListener('click', function(e) {{
      var card = e.target.closest && e.target.closest('.mem-card');
      if (card) card.classList.toggle('flipped');
    }});
  }}

  // ---------- story player ----------
  if (root && synth) {{
    var chunks = Array.prototype.slice.call(root.querySelectorAll('.story-chunk'));
    var playBtn = root.querySelector('.story-play');
    var restartBtn = root.querySelector('.story-restart');
    var progressEl = root.querySelector('.story-progress');
    var idx = 0;
    var playing = false;
    var voicesReady = false;

    function ensureVoices(cb) {{
      if (voicesReady || !('speechSynthesis' in window)) return cb();
      var v = synth.getVoices();
      if (v && v.length) {{ voicesReady = true; return cb(); }}
      synth.onvoiceschanged = function() {{ voicesReady = true; cb(); }};
      setTimeout(function() {{ if (!voicesReady) {{ voicesReady = true; cb(); }} }}, 500);
    }}
    function pickVoice(lang) {{
      var voices = synth.getVoices();
      function find(pred) {{ for (var i = 0; i < voices.length; i++) if (pred(voices[i])) return voices[i]; return null; }}
      if (lang === 'en') {{
        return find(function(v) {{ return v.lang === 'en-US' && /Samantha|Karen|Allison|Ava/i.test(v.name); }})
            || find(function(v) {{ return v.lang && v.lang.indexOf('en') === 0; }})
            || null;
      }}
      return find(function(v) {{ return v.lang === 'zh-TW'; }})
          || find(function(v) {{ return v.lang === 'zh-CN'; }})
          || find(function(v) {{ return v.lang && v.lang.indexOf('zh') === 0; }})
          || null;
    }}
    function clearHighlight() {{ chunks.forEach(function(c) {{ c.classList.remove('current'); }}); }}
    function setProgress() {{ progressEl.textContent = playing ? ('播放中 ' + (idx + 1) + ' / ' + chunks.length) : '已暫停'; }}
    function setIdleUI() {{
      playing = false;
      playBtn.textContent = '▶ 播放故事';
      progressEl.textContent = idx >= chunks.length ? '播完了 🎉' : '已暫停';
    }}

    function speakChunk(i) {{
      if (i >= chunks.length) {{ clearHighlight(); setIdleUI(); idx = 0; return; }}
      idx = i;
      var el = chunks[i];
      clearHighlight();
      el.classList.add('current');
      el.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
      setProgress();
      var lang = el.dataset.lang === 'en' ? 'en' : 'zh';
      var u = new SpeechSynthesisUtterance(el.textContent.trim());
      u.lang = lang === 'en' ? 'en-US' : 'zh-TW';
      u.rate = lang === 'en' ? 0.8 : 1.02;
      var v = pickVoice(lang);
      if (v) u.voice = v;
      u.onend = function() {{ if (playing) speakChunk(i + 1); }};
      u.onerror = function() {{ if (playing) speakChunk(i + 1); }};
      synth.speak(u);
    }}

    playBtn.addEventListener('click', function() {{
      if (playing) {{
        playing = false;
        synth.cancel();
        setIdleUI();
        return;
      }}
      ensureVoices(function() {{
        synth.cancel();
        playing = true;
        playBtn.textContent = '⏸ 暫停';
        speakChunk(idx >= chunks.length ? 0 : idx);
      }});
    }});
    restartBtn.addEventListener('click', function() {{
      synth.cancel();
      playing = false;
      idx = 0;
      clearHighlight();
      setIdleUI();
      progressEl.textContent = '尚未開始';
    }});
    window.addEventListener('hashchange', function() {{ synth.cancel(); playing = false; }});
    window.addEventListener('pagehide', function() {{ synth.cancel(); }});
  }}

  // ---------- quiz ----------
  if (quizRoot) {{
    var scoreEl = quizRoot.parentElement.querySelector('.quiz-score');
    var resetBtn = quizRoot.parentElement.querySelector('.quiz-reset');
    var total = parseInt(scoreEl.getAttribute('data-quiz-total'), 10) || 0;
    var answered = 0, correct = 0;

    function resetQuiz() {{
      answered = 0; correct = 0;
      quizRoot.querySelectorAll('.quiz-q').forEach(function(q) {{
        q.querySelectorAll('.quiz-opt').forEach(function(b) {{
          b.disabled = false;
          b.classList.remove('correct', 'wrong');
        }});
        var ex = q.querySelector('.quiz-explain');
        if (ex) ex.style.display = 'none';
      }});
      scoreEl.textContent = '';
    }}
    resetBtn.addEventListener('click', resetQuiz);

    quizRoot.addEventListener('click', function(e) {{
      var btn = e.target.closest && e.target.closest('.quiz-opt');
      if (!btn || btn.disabled) return;
      var qEl = btn.closest('.quiz-q');
      var opts = qEl.querySelectorAll('.quiz-opt');
      var isCorrect = btn.getAttribute('data-correct') === '1';
      opts.forEach(function(b) {{
        b.disabled = true;
        if (b.getAttribute('data-correct') === '1') b.classList.add('correct');
      }});
      if (!isCorrect) btn.classList.add('wrong');
      var ex = qEl.querySelector('.quiz-explain');
      if (ex) ex.style.display = 'block';
      answered++;
      if (isCorrect) correct++;
      if (answered >= total) {{
        scoreEl.textContent = '你答對了 ' + correct + ' / ' + total + ' 題' + (correct === total ? '，太厲害了！🎉' : '，再翻一下記憶卡加深印象～');
      }}
    }});
  }}
}})();
</script>
'''


def build_story_04_body():
    return render_story_page(
        num="04",
        title_zh="加拿大歷史",
        subtitle="從原住民時代到現代加拿大，用 12 個場景記住考試最愛考的關鍵時刻",
        scenes=STORY_04_SCENES,
        memory_cards=STORY_04_CARDS,
        quiz=STORY_04_QUIZ,
    )


# ============================================================================
# PEOPLE TIMELINE — 人物時間軸 + 連續朗讀
#
# 版面沿用歷史時間軸（年 / 圓點 / 卡片），卡片裡固定回答同六個問題。
# 「像聽故事一樣」的部分不是瀏覽器合成音，而是把 bi() 已經錄好的人聲片段
# 一段接一段串起來播 —— 和全站其他頁同一批 Ava／Meijia 錄音。
# ============================================================================

PEOPLE_CAT_COLOR = {c[0]: c[3] for c in PEOPLE_CATS}
PEOPLE_CAT_ZH = {c[0]: c[1] for c in PEOPLE_CATS}


def _people_field(label_zh: str, label_en: str, value: str) -> str:
    if not value:
        return ""
    return (f'<div class="pp-f"><span class="pp-k">{label_zh}'
            f'<span class="pp-k-en">{label_en}</span></span>'
            f'<div class="pp-v">{bi(value)}</div></div>')


# ----------------------------------------------------------------------------
# 連續朗讀播放器（人物時間軸與聯邦擴張頁共用）
#
# 串的是站上已經錄好的人聲片段，不是瀏覽器合成音。只唸標了 [data-narrate]
# 的那幾行，所以聽起來像在講故事，不會把欄位標籤也唸出來。
# prefix 讓同一頁面（單檔版 study.html）能同時放兩個播放器而不撞 id。
# ----------------------------------------------------------------------------

NARRATION_CSS = """
.pp-player {
  position: sticky; top: 0; z-index: 30;
  background: #fffdf8; border: 1px solid var(--line); border-bottom-width: 2px;
  border-radius: 10px; padding: 12px 14px; margin: 16px 0 20px;
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.pp-btn {
  appearance: none; font: inherit; font-size: 14px; font-weight: 600;
  font-family: -apple-system, system-ui, sans-serif;
  border: 2px solid var(--accent); background: #fff; color: var(--accent);
  padding: 7px 14px; border-radius: 20px; cursor: pointer;
}
.pp-btn.main { background: var(--accent); color: #fff; }
.pp-btn.small { padding: 7px 11px; font-size: 13px; }
.pp-langs { display: flex; border: 1px solid var(--line); border-radius: 18px; overflow: hidden; }
.pp-langs button {
  appearance: none; font: inherit; font-size: 13px; border: none; background: #fff;
  color: var(--muted); padding: 7px 12px; cursor: pointer;
  font-family: -apple-system, system-ui, sans-serif;
}
.pp-langs button + button { border-left: 1px solid var(--line); }
.pp-langs button.on { background: var(--accent-soft); color: var(--accent); font-weight: 700; }
.pp-prog { font-size: 13px; color: var(--muted); margin-left: auto; font-variant-numeric: tabular-nums; }
.pp-hint { flex-basis: 100%; font-size: 12px; color: var(--muted); margin: 0; }

@media (max-width: 640px) {
  /* 手機上這條固定在頂端，說明文字收起來，不要一直佔掉四分之一螢幕 */
  .pp-player { padding: 8px 10px; gap: 6px 8px; }
  .pp-hint { display: none; }
  .pp-prog { flex-basis: 100%; margin-left: 0; text-align: right; }
}

"""


def narration_player_html(prefix: str, hint: str) -> str:
    return f'''<div class="pp-player" id="{prefix}-player">
  <button class="pp-btn main pp-play" type="button">▶ 從頭聽</button>
  <button class="pp-btn small pp-prev" type="button" title="上一句">⏪</button>
  <button class="pp-btn small pp-next" type="button" title="下一句">⏩</button>
  <div class="pp-langs">
    <button type="button" data-lang="zh" class="on">中文</button>
    <button type="button" data-lang="en">English</button>
    <button type="button" data-lang="both">中英對照</button>
  </div>
  <span class="pp-prog">尚未開始</span>
  <p class="pp-hint">{hint}</p>
</div>'''


def narration_player_js(prefix: str) -> str:
    return NARRATION_JS.replace("__PFX__", prefix)


NARRATION_JS = r"""
<script>
(function () {
  var tl = document.getElementById('__PFX__-tl');
  var player = document.getElementById('__PFX__-player');
  if (!tl || !player) return;

  // Same clip folder the single-line 🔊 buttons use, derived from the words.js
  // script tag so this works both in the per-page build (depth 1) and inside the
  // single-file study.html (depth 0). Resolved lazily: dict_bundle() appends that
  // tag AFTER this body, so at parse time it is not in the DOM yet.
  var base = null;
  function clipBase() {
    if (base === null) {
      var ws = document.querySelector('script[src$="dict/words.js"]');
      base = ws ? ws.getAttribute('src').replace(/dict\/words\.js$/, 'audio/iv/') : 'audio/iv/';
    }
    return base;
  }

  var playBtn = player.querySelector('.pp-play');
  var progEl = player.querySelector('.pp-prog');
  var audio = new Audio();
  var queue = [], idx = -1, playing = false, mode = 'zh';

  function clearMarks() {
    tl.querySelectorAll('.pp-cur').forEach(function (n) { n.classList.remove('pp-cur'); });
    tl.querySelectorAll('.pp-reading').forEach(function (n) { n.classList.remove('pp-reading'); });
  }
  function buildQueue() {
    var all = Array.prototype.slice.call(tl.querySelectorAll('[data-narrate] .say'));
    queue = all.filter(function (b) {
      if (b.closest('.pp-hidden')) return false;
      return mode === 'both' || b.dataset.lang === mode;
    });
  }
  function setProg(txt) { progEl.textContent = txt; }
  function idleUI(txt) {
    playing = false;
    playBtn.textContent = '▶ 從頭聽';
    setProg(txt);
  }
  function stop(txt) {
    audio.pause();
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    clearMarks();
    idleUI(txt || '已停止');
  }
  // The single-line 🔊 and the dictionary both call this, so two voices never overlap.
  (window.CIT_AUTOPLAY_LIST = window.CIT_AUTOPLAY_LIST || []).push(function () { if (playing || idx >= 0) stop('已停止'); });
  window.CIT_AUTOPLAY_STOP = function () { window.CIT_AUTOPLAY_LIST.forEach(function (f) { f(); }); };

  function speakFallback(btn, onDone) {
    if (!window.speechSynthesis) { onDone(); return; }
    var host = btn.parentElement;
    var txt = host ? host.textContent.replace(/🔊/g, '').trim() : '';
    var u = new SpeechSynthesisUtterance(txt);
    u.lang = (btn.dataset.lang === 'zh') ? 'zh-TW' : 'en-US';
    u.rate = 0.9;
    u.onend = onDone; u.onerror = onDone;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }

  function play(i) {
    if (i < 0 || i >= queue.length) { clearMarks(); idleUI('聽完了 🎉'); idx = -1; return; }
    idx = i;
    var btn = queue[i];
    clearMarks();
    var line = btn.parentElement;
    if (line) line.classList.add('pp-cur');
    var card = btn.closest('.nr-card');
    if (card) {
      card.classList.add('pp-reading');
      card.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
    setProg('播放中 ' + (i + 1) + ' / ' + queue.length);
    audio.onended = function () { if (playing) play(idx + 1); };
    audio.onerror = null;
    audio.src = clipBase() + btn.dataset.lang + '/' + btn.dataset.k + '.m4a';
    audio.play().catch(function () {
      // no recorded clip for this line — fall back to the browser voice and keep going
      speakFallback(btn, function () { if (playing) play(idx + 1); });
    });
  }

  playBtn.addEventListener('click', function () {
    if (playing) { stop('已暫停'); return; }
    buildQueue();
    if (!queue.length) { setProg('這個篩選下沒有可聽的內容'); return; }
    playing = true;
    playBtn.textContent = '⏸ 暫停';
    play(idx >= 0 && idx < queue.length ? idx : 0);
  });
  player.querySelector('.pp-prev').addEventListener('click', function () {
    if (!queue.length) buildQueue();
    playing = true; playBtn.textContent = '⏸ 暫停';
    play(Math.max(0, (idx < 0 ? 0 : idx) - 1));
  });
  player.querySelector('.pp-next').addEventListener('click', function () {
    if (!queue.length) buildQueue();
    playing = true; playBtn.textContent = '⏸ 暫停';
    play((idx < 0 ? 0 : idx) + 1);
  });
  player.querySelectorAll('.pp-langs button').forEach(function (b) {
    b.addEventListener('click', function () {
      player.querySelectorAll('.pp-langs button').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      mode = b.dataset.lang;
      idx = -1;
      stop('語言已切換，按 ▶ 重新開始');
    });
  });

  // ---------- category filter ----------
  var catBtns = tl.parentElement.querySelectorAll('.pp-cat-btn');
  catBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      catBtns.forEach(function (b) { b.classList.remove('pp-on'); });
      btn.classList.add('pp-on');
      var cat = btn.dataset.cat;
      tl.querySelectorAll('.pp-p').forEach(function (p) {
        if (cat === 'all' || p.dataset.cat === cat) p.classList.remove('pp-hidden');
        else p.classList.add('pp-hidden');
      });
      idx = -1;
      stop('篩選已變更，按 ▶ 重新開始');
    });
  });

  window.addEventListener('pagehide', function () { stop(''); });
})();
</script>"""


def build_people_body():
    cards = ""
    for (year, _sort, name_en, name_zh, cat, src, role, origin, place, story, extras) in \
            sorted(PEOPLE, key=lambda r: r[1]):
        color = PEOPLE_CAT_COLOR[cat]
        src_tag = ('<span class="pp-src pp-src-guide">教材</span>' if src == "guide"
                   else '<span class="pp-src pp-src-extra">補充</span>')
        extra_html = "".join(f'<div class="pp-extra">{bi(e)}</div>' for e in extras)
        cards += f'''
<div class="pp-p nr-card" data-cat="{cat}">
  <div class="pp-year">{year}</div>
  <div class="pp-marker" style="background:{color}"></div>
  <div class="pp-card" style="--pp-c:{color}">
    <div class="pp-head">
      <h3 class="pp-name">{name_zh}</h3>
      <div class="pp-name-en">{_wd.wrap_words(name_en)}</div>
      <div class="pp-tags">
        <span class="pp-tag" style="background:{color}">{PEOPLE_CAT_ZH[cat]}</span>{src_tag}
      </div>
    </div>
    <div class="pp-fields">
      {_people_field("什麼人", "who", role)}
      {_people_field("哪國人 · 族裔", "origin", origin)}
      {_people_field("在哪裡", "where", place)}
    </div>
    <div class="pp-why" data-narrate>
      <span class="pp-k pp-k-why">做了什麼而有名<span class="pp-k-en">why famous</span></span>
      <div class="pp-v">{bi(story)}</div>
      {extra_html}
    </div>
  </div>
</div>'''

    cat_filters = "".join(
        f'<button class="pp-cat-btn" data-cat="{cid}" style="--pp-c:{color}">'
        f'<span class="cz">{zh}</span><span class="ce">{en}</span></button>'
        for cid, zh, en, color in PEOPLE_CATS)

    return f'''{IV_SHARED_CSS}{NARRATION_CSS}
<style>
.pp-cat-filter {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 22px; }}
.pp-cat-btn {{
  appearance: none; padding: 6px 13px; border-radius: 14px; text-align: left; line-height: 1.3;
  background: #fff; border: 2px solid var(--pp-c); color: var(--pp-c);
  cursor: pointer; font-size: 13px; font-weight: 600;
  font-family: -apple-system, system-ui, sans-serif;
}}
.pp-cat-btn .cz {{ display: block; }}
.pp-cat-btn .ce {{ display: block; font-family: "Source Serif 4", Georgia, serif; font-weight: 400; font-size: 11px; opacity: 0.85; }}
.pp-cat-btn.pp-on {{ background: var(--pp-c); color: #fff; }}

.pp-tl {{ position: relative; padding: 4px 0 20px; }}
.pp-tl::before {{
  content: ''; position: absolute; left: 96px; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(to bottom, #4a6fa5 0%, #b0413e 22%, #7a8c5c 42%, #9c5a9b 60%, #2f7d8c 78%, #4f8f57 100%);
  border-radius: 2px;
}}
.pp-p {{ display: grid; grid-template-columns: 86px 26px 1fr; align-items: start; gap: 10px; padding: 9px 0; }}
.pp-p.pp-hidden {{ display: none; }}
.pp-year {{ text-align: right; font-weight: 700; font-family: monospace; font-size: 13.5px; padding-top: 15px; color: var(--ink); }}
.pp-marker {{ width: 13px; height: 13px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 0 2px rgba(0,0,0,0.12); margin: 17px 6px 0; }}
.pp-card {{
  background: #fff; border: 1px solid var(--line); border-left: 4px solid var(--pp-c);
  border-radius: 8px; padding: 12px 16px; transition: box-shadow 0.15s, border-color 0.15s;
}}
.pp-card:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.pp-p.pp-reading .pp-card {{ box-shadow: 0 0 0 2px var(--accent); }}

.pp-head {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 10px; margin-bottom: 9px; }}
.pp-name {{ margin: 0; font-size: 16.5px; }}
.pp-name-en {{ font-size: 16.5px; color: #45403a; font-family: "Source Serif 4", Georgia, serif; }}
.pp-tags {{ margin-left: auto; display: flex; gap: 5px; align-items: center; }}
.pp-tag {{ font-size: 11px; color: #fff; padding: 2px 8px; border-radius: 10px; font-family: -apple-system, system-ui, sans-serif; white-space: nowrap; }}
.pp-src {{ font-size: 11px; padding: 2px 7px; border-radius: 10px; font-family: -apple-system, system-ui, sans-serif; white-space: nowrap; }}
.pp-src-guide {{ background: #eef2ea; color: #4a5c3a; }}
.pp-src-extra {{ background: #fdf0e3; color: #8a5a22; }}

.pp-fields {{ display: grid; gap: 5px; padding-bottom: 9px; border-bottom: 1px dashed var(--line); }}
.pp-f {{ display: grid; grid-template-columns: 92px 1fr; gap: 10px; align-items: start; }}
.pp-k {{
  font-size: 12px; color: var(--muted); font-family: -apple-system, system-ui, sans-serif;
  padding-top: 2px; line-height: 1.35;
}}
.pp-k-en {{ display: block; font-family: "Source Serif 4", Georgia, serif; font-size: 10.5px; opacity: 0.8; }}
.pp-v {{ font-size: 14px; min-width: 0; }}
.pp-why {{ padding-top: 9px; display: grid; grid-template-columns: 92px 1fr; gap: 10px; align-items: start; }}
.pp-k-why {{ color: var(--accent); font-weight: 700; }}
.pp-why .pp-v {{ font-size: 14.5px; }}
.pp-extra {{ grid-column: 2; font-size: 13.5px; margin-top: 6px; color: #4a4540; }}
.pp-cur {{ background: #ffe9b3; border-radius: 4px; }}

@media (max-width: 640px) {{
  .pp-tl::before {{ left: 62px; }}
  .pp-p {{ grid-template-columns: 54px 22px 1fr; gap: 5px; }}
  .pp-year {{ font-size: 11.5px; }}
  .pp-f, .pp-why {{ grid-template-columns: 1fr; gap: 2px; }}
  .pp-extra {{ grid-column: 1; }}
  .pp-k-en {{ display: inline; margin-left: 5px; }}
  .pp-tags {{ margin-left: 0; }}
}}
</style>

<div class="iv-hero">
  <h1>👤 加拿大人物時間軸 <small>Who's Who in Canadian History</small></h1>
  <p>1497 → 2021，{len(PEOPLE)} 位考試會碰到的人物。每一位都回答同樣六件事：<strong>哪一年、是誰、什麼人、哪國人／哪個族裔、在哪裡、做了什麼而有名</strong>。中英同字級，按 ▶ 可以從頭連續聽下去。</p>
</div>

{narration_player_html('pp', '連續播放只唸「做了什麼而有名」那幾句，像聽故事。要單獨聽某一行，點那行後面的 🔊；英文字點下去可以查字典。')}

<div class="pp-cat-filter">
  <button class="pp-cat-btn pp-on" data-cat="all" style="--pp-c:#1f2328"><span class="cz">全部</span><span class="ce">All</span></button>
  {cat_filters}
</div>

<div class="pp-tl" id="pp-tl">
{cards}
</div>

{narration_player_js('pp')}'''


# ============================================================================
# JOINING — 聯邦擴張時間軸：地圖 ＋ 誰哪年加入 ＋ 首府 ＋ 背誦口訣
#
# 省名與首府名一律中英並列：考試是英文出題，只認得中文等於白背。
# 英文可以點開查字典，整頁也能用上面的播放器連續聽。
# ============================================================================

def _jn_member(num, zh, en, cap_zh, cap_en, kind) -> str:
    badge = f'<u>{num}</u>' if num else '<u class="jn-none">–</u>'
    return (f'<span class="jn-it jn-{kind}">{badge}'
            f'<span class="jn-b">'
            f'<span class="jn-name"><b>{zh}</b><em>{_wd.wrap_words(en)}</em></span>'
            f'<span class="jn-cap"><b>{cap_zh}</b><em>{_wd.wrap_words(cap_en)}</em></span>'
            f'</span></span>')


def build_joining_body():
    rows = ""
    for year, tag, members, story, notes in JOINING:
        kinds = {m[5] for m in members}
        dot = "g" if kinds == {"g"} else ("r" if kinds == {"r"} else "p")
        tag_html = f'<div class="jn-tag jn-tag-{dot}">{bi(tag)}</div>' if tag else ""
        notes_html = "".join(f'<div class="jn-note">{bi(n)}</div>' for n in notes)
        rows += f'''
<div class="jn-row nr-card{' jn-dim' if dot == 'g' else ''}">
  <div class="jn-year">{year}</div>
  <div class="jn-dot jn-{dot}"></div>
  <div class="jn-card">
    {tag_html}
    <div class="jn-items">{"".join(_jn_member(*m) for m in members)}</div>
    <div class="jn-say" data-narrate>
      <div class="jn-story">{bi(story)}</div>
      {notes_html}
    </div>
  </div>
</div>'''

    tricks = ""
    for i, (title, lines) in enumerate(JOINING_TRICKS, 1):
        body = "".join(f'<div class="jn-tline">{bi(l)}</div>' for l in lines)
        tricks += f'''
<div class="jn-tk nr-card">
  <div class="jn-tkno">{i}</div>
  <div class="jn-tkbody">
    <div class="jn-tkh">{bi(title)}</div>
    <div class="jn-say" data-narrate>{body}</div>
  </div>
</div>'''

    return f'''{IV_SHARED_CSS}{NARRATION_CSS}
<style>
.jn-map {{ display: block; margin: 4px auto 6px; max-width: 100%; }}
.jn-key {{ display: flex; flex-wrap: wrap; gap: 8px 18px; font-size: 12.5px; color: var(--muted); margin: 0 0 24px; }}
.jn-key span {{ display: inline-flex; align-items: center; gap: 6px; }}
.jn-sw {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
.jn-sw.p {{ background: #0F6E56; }} .jn-sw.r {{ background: #534AB7; }}
.jn-star {{ width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-bottom: 10px solid #D85A30; display: inline-block; }}
.jn-key b {{ color: #993C1D; }}

.jn-tl {{ position: relative; }}
.jn-row {{ display: grid; grid-template-columns: 58px 20px 1fr; gap: 10px; align-items: start; position: relative; padding-bottom: 14px; }}
.jn-row::before {{ content: ""; position: absolute; left: 67px; top: 18px; bottom: -2px; width: 2px; background: var(--line); }}
.jn-row:last-of-type::before {{ display: none; }}
.jn-row.jn-dim {{ opacity: 0.85; }}
.jn-year {{ text-align: right; font-weight: 700; font-family: monospace; font-size: 14px; padding-top: 9px; }}
.jn-dot {{ width: 12px; height: 12px; border-radius: 50%; margin: 12px 0 0 4px; position: relative; z-index: 1; border: 2px solid #fff; }}
.jn-dot.jn-p {{ background: #0F6E56; }} .jn-dot.jn-r {{ background: #534AB7; }} .jn-dot.jn-g {{ background: #B4B2A9; }}
.jn-card {{ background: #fff; border: 1px solid var(--line); border-radius: 9px; padding: 11px 14px; }}
.jn-row.nr-reading .jn-card, .jn-tk.nr-reading {{ box-shadow: 0 0 0 2px var(--accent); }}

.jn-tag {{ font-size: 12px; margin-bottom: 8px; padding: 3px 10px; border-radius: 10px; display: inline-block; }}
.jn-tag-p {{ background: #E1F5EE; }} .jn-tag-g {{ background: #f1efe8; }}
.jn-tag .bi {{ gap: 0 8px; }} .jn-tag .bi-zh, .jn-tag .bi-en {{ flex: 0 1 auto; }}
.jn-tag .bi-en {{ border-left: none; padding-left: 0; }}

.jn-items {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }}
.jn-it {{ display: inline-flex; align-items: flex-start; gap: 8px; padding: 6px 12px 6px 6px; border-radius: 8px; }}
.jn-it u {{ text-decoration: none; width: 21px; height: 21px; border-radius: 50%; font-size: 12px;
  display: inline-flex; align-items: center; justify-content: center; color: #fff; flex: none;
  font-family: -apple-system, system-ui, sans-serif; margin-top: 1px; }}
.jn-it u.jn-none {{ background: #B4B2A9; }}
.jn-b {{ display: grid; gap: 1px; }}
.jn-name, .jn-cap {{ display: flex; flex-wrap: wrap; gap: 0 7px; align-items: baseline; }}
.jn-name b {{ font-size: 15px; }}
.jn-name em, .jn-cap em {{ font-style: normal; font-family: "Source Serif 4", Georgia, serif; }}
.jn-name em {{ font-size: 15px; }}
.jn-cap b, .jn-cap em {{ font-size: 13.5px; font-weight: 400; }}
.jn-p {{ background: #E1F5EE; }} .jn-p u {{ background: #0F6E56; }}
.jn-p .jn-name b {{ color: #085041; }} .jn-p .jn-name em {{ color: #0F6E56; }}
.jn-p .jn-cap b, .jn-p .jn-cap em {{ color: #3B6D11; }}
.jn-r {{ background: #EEEDFE; }} .jn-r u {{ background: #534AB7; }}
.jn-r .jn-name b {{ color: #3C3489; }} .jn-r .jn-name em {{ color: #534AB7; }}
.jn-r .jn-cap b, .jn-r .jn-cap em {{ color: #534AB7; }}
.jn-g {{ background: #F1EFE8; }} .jn-g .jn-name b, .jn-g .jn-name em,
.jn-g .jn-cap b, .jn-g .jn-cap em {{ color: #5F5E5A; }}

.jn-story {{ font-size: 14px; padding-top: 9px; border-top: 1px dashed var(--line); }}
.jn-note {{ font-size: 13.5px; margin-top: 7px; }}

.jn-tk {{ display: grid; grid-template-columns: 26px 1fr; gap: 12px; margin-bottom: 16px;
  background: #fff; border: 1px solid var(--line); border-radius: 9px; padding: 12px 14px; }}
.jn-tkno {{ width: 24px; height: 24px; border-radius: 50%; background: var(--accent-soft); color: var(--accent);
  font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
.jn-tkh {{ font-weight: 700; margin-bottom: 8px; }}
.jn-tkh .bi-en {{ font-weight: 400; }}
.jn-tline {{ font-size: 14px; margin-bottom: 7px; }}
.jn-tline:last-child {{ margin-bottom: 0; }}

@media (max-width: 640px) {{
  .jn-row {{ grid-template-columns: 46px 18px 1fr; gap: 6px; }}
  .jn-row::before {{ left: 54px; }}
  .jn-year {{ font-size: 12.5px; }}
  .jn-it {{ width: 100%; }}
}}
</style>

<div class="iv-hero">
  <h1>🗺️ 聯邦擴張時間軸 <small>Building the Federation</small></h1>
  <p>1867 → 1999，132 年拼成今天的 <strong>10 省 3 地區</strong>。地圖上的號碼＝加入順序，和下面的時間軸一一對應；首府是按實際經緯度標的。<strong>省名和首府都給你中英對照</strong>——考試是英文出題。</p>
</div>

{narration_player_html('jn', '連續播放唸的是每一年那句話和補充，像聽故事。要單獨聽某一行，點那行後面的 🔊；英文字點下去可以查字典。')}

{CAPITALS_MAP_SVG}

<div class="jn-key">
  <span><i class="jn-sw p"></i>省 Provinces · 10</span>
  <span><i class="jn-sw r"></i>地區 Territories · 3</span>
  <span><i class="jn-star"></i>國都 Ottawa <b>不是多倫多 not Toronto</b></span>
</div>

<div class="jn-tl" id="jn-tl">
{rows}
</div>

<h2 class="iv-section-title">🧠 背誦小妙招 <small>Memory tricks</small></h2>
{tricks}

{narration_player_js('jn')}'''
