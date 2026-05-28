"""Interactive (visual) study modules — body HTML generators.

Each function returns inner-body HTML, ready to be wrapped by build_html.wrap_page().
All content shared CSS uses the .iv prefix to avoid leaking into other pages.
"""

# ---- 13 provinces / territories (2026 current data) ----

# (code, name_en, name_zh_display, region, capital, premier, lt_gov_or_commissioner, facts[])
PROVINCES = [
    ("BC", "British Columbia", "卑詩省（不列顛哥倫比亞）", "West Coast",
     "Victoria 維多利亞",
     "David Eby（NDP）",
     "Wendy Cocchia（Lt. Governor）",
     ["木材、礦業、鮭魚捕撈、電影業（Hollywood North）",
      "華人移民歷史悠久，溫哥華是亞太門戶",
      "Vancouver 是大城，**Victoria** 才是首府（位於溫哥華島）"]),
    ("AB", "Alberta", "亞伯達省", "Prairie Provinces",
     "Edmonton 愛德蒙頓",
     "Danielle Smith（UCP）",
     "Salma Lakhani（Lt. Governor）",
     ["石油、天然氣（油砂 Oil Sands）、農業、牛肉",
      "Rocky Mountains 落磯山脈、Banff/Jasper 國家公園",
      "**Calgary** 是最大城但 **Edmonton** 才是首府"]),
    ("SK", "Saskatchewan", "薩斯喀徹溫省（沙省）", "Prairie Provinces",
     "Regina 雷吉納",
     "Scott Moe（Sask Party）",
     "Russ Mirasty（Lt. Governor，原住民出身）",
     ["小麥（Wheat Province）、鉀礦、鈾礦",
      "加拿大穀倉、世界最大鉀肥出口",
      "Saskatoon 是大城但 **Regina** 才是首府"]),
    ("MB", "Manitoba", "曼尼托巴省（曼省）", "Prairie Provinces",
     "Winnipeg 溫尼伯",
     "Wab Kinew（NDP，**首位原住民省長**）",
     "Anita Neville（Lt. Governor）",
     ["農業、礦業、水力發電",
      "Louis Riel 反抗運動的核心地（Métis 文化）",
      "1870 年加入聯邦（第 5 省）"]),
    ("ON", "Ontario ⭐", "安大略省（安省）", "Central Canada",
     "Toronto 多倫多",
     "Doug Ford（Progressive Conservative）",
     "Edith Dumont（Lt. Governor，**首位法裔安省人，2023 起**）",
     ["製造業、金融、服務業、科技",
      "**國都 Ottawa 渥太華位於此省**（不是 Toronto！）",
      "人口最多的省（約 1,500 萬，全國 40%）",
      "主要城市：Toronto、Ottawa、Hamilton、Mississauga、London",
      "**考試 Ontario 省題重點**：省長 Doug Ford 自 2018 連任至今，省督 Edith Dumont 2023 起",
      "你的選區記住：聯邦議員 MP & 省議員 MPP",
      "與美國邊境最長，五大湖區（Great Lakes）"]),
    ("QC", "Quebec", "魁北克省", "Central Canada",
     "Quebec City 魁北克市",
     "François Legault（CAQ）",
     "Manon Jeannotte（Lt. Governor）",
     ["航太、水電、礦業、軟體",
      "**唯一以法語為唯一官方語言的省**",
      "Montreal 蒙特婁是大城但 **Quebec City** 才是首府",
      "天主教文化深厚、有獨特民法系統",
      "1995 公投差點獨立（50.58% 反對）"]),
    ("NB", "New Brunswick", "新布倫瑞克省", "Atlantic Canada",
     "Fredericton 弗雷德里克頓",
     "Susan Holt（Liberal，2024 起）",
     "Louise Imbeault（Lt. Governor）",
     ["林業、漁業、食品加工",
      "**加拿大唯一官方雙語（英＋法）的省份**",
      "Acadian 文化重鎮（法裔但獨立於魁北克）"]),
    ("NS", "Nova Scotia", "新斯科舍省", "Atlantic Canada",
     "Halifax 哈利法克斯",
     "Tim Houston（Progressive Conservative）",
     "Mike Savage（Lt. Governor）",
     ["漁業、造船、旅遊",
      "**Bluenose 帆船**——10 分硬幣圖案",
      "**Pier 21** 全國移民登陸博物館",
      "**Bay of Fundy** 全球最高潮汐",
      "1605 法國人 Port-Royal 北美第一個歐洲殖民地"]),
    ("PE", "Prince Edward Island", "愛德華王子島（PEI）", "Atlantic Canada",
     "Charlottetown 夏洛特鎮",
     "Rob Lantz（Progressive Conservative，2025 起）",
     "Wassim Salamoun（Lt. Governor）",
     ["馬鈴薯（產量全國第一）、觀光業、漁業",
      "**面積最小的省**",
      "**Confederation 發源地**——1864 Charlottetown Conference",
      "《清秀佳人 Anne of Green Gables》故鄉"]),
    ("NL", "Newfoundland and Labrador", "紐芬蘭與拉布拉多省", "Atlantic Canada",
     "St. John's 聖約翰斯",
     "Andrew Furey（Liberal）",
     "Joan Marie Aylward（Lt. Governor）",
     ["漁業（鱈魚 Cod）、海上石油、水電",
      "**最晚加入聯邦的省（1949）**",
      "**最東邊的省份**（時區比其他省早 30 分鐘）",
      "獨特方言；維京人 L'Anse aux Meadows 北美最早歐洲遺址"]),
    ("YT", "Yukon", "育空地區", "Northern Territories",
     "Whitehorse 白馬市",
     "Ranj Pillai（Liberal）",
     "Adeline Webber（Commissioner）",
     ["礦業、觀光",
      "**1898 Klondike 淘金潮**（人口曾經高達 4 萬）",
      "Yukon River、Mount Logan 加拿大最高峰"]),
    ("NT", "Northwest Territories", "西北地區", "Northern Territories",
     "Yellowknife 黃刀鎮",
     "R.J. Simpson（Independent）",
     "Gerald W. Kisoun（Commissioner）",
     ["鑽石、石油、天然氣",
      "Great Bear / Great Slave 兩大湖泊",
      "Dene 原住民、Métis 為主要族群",
      "11 種官方語言（含英、法、9 種原住民語）"]),
    ("NU", "Nunavut", "努納武特地區", "Northern Territories",
     "Iqaluit 伊魁特",
     "P.J. Akeeagok",
     "Eva Aariak（Commissioner）",
     ["礦業（金、鐵、鑽石）、傳統手工藝",
      "**1999 從 NT 分出來新建**（最年輕的領地）",
      "**Inuit 因紐特人為多數**（85%）",
      "**面積最大的領地**（佔加拿大 20% 土地）",
      "Inuktitut 為官方語言之一"]),
]

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

# Approximate position on viewBox 0 0 1000 600 (abstract Canada layout)
PROVINCE_LAYOUT = {
    # code: (x, y, w, h)
    "YT": (50,   30, 130, 130),
    "NT": (190,  30, 180, 130),
    "NU": (380,  30, 320, 180),
    "BC": (50,  180, 130, 180),
    "AB": (190, 180,  85, 180),
    "SK": (285, 180,  85, 180),
    "MB": (380, 220,  85, 140),
    "ON": (475, 240, 170, 180),
    "QC": (655, 240, 170, 160),
    "NL": (835, 200, 130, 160),
    "NB": (685, 430,  75,  70),
    "PE": (770, 430,  50,  35),
    "NS": (830, 430, 130,  70),
}


# ----------------------------- Geography ----------------------------- #

def _province_data_attrs(p):
    code, en, zh, region, capital, premier, lt_gov, facts = p
    return code, en, zh, region, capital, premier, lt_gov, facts


def _render_svg_map():
    rects = []
    for code, (x, y, w, h) in PROVINCE_LAYOUT.items():
        p = PROVINCE_BY_CODE[code]
        color = REGION_COLOR[code]
        is_ontario = code == "ON"
        cls = "iv-prov" + (" iv-prov-star" if is_ontario else "")
        label = code if w < 80 else f"{code} {p[2].split('（')[0]}"
        text_y = y + h / 2 + 5
        font_size = 14 if w < 80 else 18
        rects.append(
            f'<g class="{cls}" data-code="{code}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{color}" />'
            f'<text x="{x + w/2}" y="{text_y}" text-anchor="middle" font-size="{font_size}" '
            f'font-weight="700" fill="#fff" pointer-events="none">{label}</text>'
            f'{("<text x=\"" + str(x + w - 10) + "\" y=\"" + str(y + 22) + "\" text-anchor=\"end\" font-size=\"18\" fill=\"#fff100\" pointer-events=\"none\">★</text>") if is_ontario else ""}'
            f'</g>'
        )
    # Add region labels
    region_labels = (
        '<text x="850" y="555" font-size="11" fill="#5a9460" font-weight="600">大西洋四省</text>'
        '<text x="100" y="555" font-size="11" fill="#4ea693" font-weight="600">西岸</text>'
        '<text x="305" y="555" font-size="11" fill="#d4a943" font-weight="600">草原三省</text>'
        '<text x="555" y="555" font-size="11" fill="#c8102e" font-weight="600">中央加拿大</text>'
        '<text x="380" y="15" font-size="11" fill="#4a7c9e" font-weight="600">北部三領地</text>'
    )
    return (
        '<svg viewBox="0 0 1000 580" class="iv-map" role="img" aria-label="加拿大省份地圖">'
        + "".join(rects) + region_labels +
        '</svg>'
    )


def _render_detail_panel(initial_code="ON"):
    p = PROVINCE_BY_CODE[initial_code]
    code, en, zh, region, capital, premier, lt_gov, facts = p
    facts_html = "".join(f"<li>{f}</li>" for f in facts)
    return f'''
<div class="iv-detail" id="iv-prov-detail" data-current="{code}">
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
</div>
'''


def _render_province_data_json():
    """Generate JS object with all province data for client-side switching."""
    import json
    data = {}
    for p in PROVINCES:
        code, en, zh, region, capital, premier, lt_gov, facts = p
        data[code] = {
            "en": en, "zh": zh, "region": region,
            "capital": capital, "premier": premier, "lt_gov": lt_gov,
            "facts": facts,
        }
    return json.dumps(data, ensure_ascii=False)


def build_geography_body():
    map_svg = _render_svg_map()
    detail = _render_detail_panel("ON")
    data_json = _render_province_data_json()

    # Quick reference table
    table_rows = ""
    for p in PROVINCES:
        code, en, zh, region, capital, premier, lt_gov, facts = p
        zh_short = zh.split("（")[0]
        color = REGION_COLOR[code]
        table_rows += (
            f'<tr data-code="{code}" class="iv-row">'
            f'<td><span class="iv-dot" style="background:{color}"></span>{code}</td>'
            f'<td>{en}</td><td>{zh_short}</td><td>{capital}</td><td>{premier}</td>'
            f'</tr>'
        )

    return f'''
<style>
.iv-hero {{
  background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%);
  border-left: 4px solid var(--accent);
  padding: 18px 22px; border-radius: 8px; margin: 16px 0 24px;
}}
.iv-hero h1 {{ margin: 0 0 6px; }}
.iv-hero p {{ margin: 0; color: var(--muted); }}
.iv-map {{ width: 100%; height: auto; max-width: 100%; }}
.iv-prov {{ cursor: pointer; transition: filter 0.15s, transform 0.15s; transform-origin: center; transform-box: fill-box; }}
.iv-prov rect {{ transition: stroke 0.15s, stroke-width 0.15s; stroke: rgba(0,0,0,0.1); stroke-width: 1; }}
.iv-prov:hover rect {{ stroke: #1f2328; stroke-width: 3; }}
.iv-prov.iv-active rect {{ stroke: #1f2328; stroke-width: 4; filter: brightness(1.05); }}
.iv-prov-star rect {{ stroke: #c8102e; stroke-width: 2; stroke-dasharray: 4 2; }}

.iv-detail {{
  margin: 20px 0; padding: 22px;
  background: #fff; border: 1px solid var(--line);
  border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
.iv-detail-head {{ display: flex; align-items: baseline; flex-wrap: wrap; gap: 12px; margin-bottom: 14px; }}
.iv-detail-head h2 {{ margin: 0; border: none; padding: 0; font-size: 22px; }}
.iv-detail-code {{
  display: inline-block; background: var(--accent); color: #fff;
  padding: 2px 10px; border-radius: 6px; font-family: monospace;
  font-size: 18px; margin-right: 4px;
}}
.iv-detail-zh {{ color: var(--muted); font-weight: 400; font-size: 18px; }}
.iv-detail-region {{
  display: inline-block; padding: 3px 10px; border-radius: 12px;
  background: #f3efe6; font-size: 12px; color: var(--muted);
  font-family: -apple-system, system-ui, sans-serif;
}}
.iv-detail-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 14px 0 20px; }}
.iv-detail-stat {{ padding: 10px 12px; background: #faf8f4; border-radius: 6px; }}
.iv-detail-stat label {{ display: block; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); font-family: -apple-system, system-ui, sans-serif; margin-bottom: 3px; }}
.iv-detail-stat span {{ font-weight: 600; }}
.iv-detail h3 {{ font-size: 15px; margin: 0 0 8px; }}
.iv-detail-facts {{ margin: 0; padding-left: 20px; }}
.iv-detail-facts li {{ margin: 6px 0; }}

.iv-region-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 16px 0 30px; }}
.iv-region-card {{ padding: 12px 14px; border-radius: 8px; color: #fff; font-size: 14px; }}
.iv-region-card .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.85; }}
.iv-region-card .name {{ font-weight: 700; font-size: 15px; margin: 3px 0 6px; }}
.iv-region-card .codes {{ font-family: monospace; font-size: 13px; }}

table.iv-quick {{ width: 100%; font-size: 14px; }}
table.iv-quick th {{ font-size: 12px; }}
.iv-row {{ cursor: pointer; }}
.iv-row:hover {{ background: #fff8f8; }}
.iv-row.iv-active {{ background: var(--accent-soft); }}
.iv-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }}
</style>

<div class="iv-hero">
  <h1>🗺️ 加拿大地理（互動地圖）</h1>
  <p>點任何省份看它的首府、省長、產業重點。<strong>Ontario ⭐</strong> 因為是你考試的省題，預設展開、欄位最多。</p>
</div>

{map_svg}

{detail}

<h2>5 大區域速記</h2>
<div class="iv-region-row">
{"".join(
    f'<div class="iv-region-card" style="background:{color}"><div class="label">Region</div><div class="name">{zh}</div><div class="codes">{" · ".join(codes)}</div></div>'
    for en, zh, color, codes in REGIONS
)}
</div>

<h2>速查表</h2>
<table class="iv-quick">
<thead><tr><th>代碼</th><th>英文名</th><th>中文</th><th>首府</th><th>省長</th></tr></thead>
<tbody>{table_rows}</tbody>
</table>

<script>
(function() {{
  var DATA = {data_json};
  var detail = document.getElementById('iv-prov-detail');
  if (!detail) return;

  function show(code) {{
    var d = DATA[code]; if (!d) return;
    detail.dataset.current = code;
    detail.querySelector('.iv-detail-code').textContent = code;
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
    // Mark active on map + table
    document.querySelectorAll('.iv-prov.iv-active').forEach(function(e){{ e.classList.remove('iv-active'); }});
    var mapEl = document.querySelector('.iv-prov[data-code="' + code + '"]');
    if (mapEl) mapEl.classList.add('iv-active');
    document.querySelectorAll('.iv-row.iv-active').forEach(function(e){{ e.classList.remove('iv-active'); }});
    var rowEl = document.querySelector('.iv-row[data-code="' + code + '"]');
    if (rowEl) rowEl.classList.add('iv-active');
    // scroll detail into view on mobile
    if (window.innerWidth < 800) detail.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}

  document.querySelectorAll('.iv-prov').forEach(function(el) {{
    el.addEventListener('click', function() {{ show(el.dataset.code); }});
  }});
  document.querySelectorAll('.iv-row').forEach(function(el) {{
    el.addEventListener('click', function() {{ show(el.dataset.code); }});
  }});

  // initial active
  var mapEl = document.querySelector('.iv-prov[data-code="ON"]');
  if (mapEl) mapEl.classList.add('iv-active');
  var rowEl = document.querySelector('.iv-row[data-code="ON"]');
  if (rowEl) rowEl.classList.add('iv-active');
}})();
</script>
'''


# ----------------------------- Stubs (coming soon) ----------------------------- #

def _stub(title, emoji, what_will_have):
    items = "".join(f"<li>{x}</li>" for x in what_will_have)
    return f'''
<div class="iv-hero">
  <h1>{emoji} {title}</h1>
  <p>製作中。預計會有：</p>
  <ul>{items}</ul>
  <p style="margin-top:14px;color:var(--muted);font-style:italic">告訴 AI「下一個做 {title}」就會展開。</p>
</div>
<style>.iv-hero {{ background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%); border-left: 4px solid var(--accent); padding: 18px 22px; border-radius: 8px; margin: 16px 0 24px; }}
.iv-hero ul {{ margin: 8px 0; }}</style>
'''


def build_history_body():
    return _stub("歷史時間軸", "📜", [
        "垂直時間軸，1497 → 2021，按時代色標分區",
        "新法蘭西（1497-1763 藍）/ 英屬北美（1763-1867 紅）/ 邦聯（1867-1914 金）/ 兩戰與改革（1914-1949 橄欖）/ 現代加拿大（1949-今 綠）",
        "點任何事件展開：年代、事件名、為什麼考、相關人物",
        "Plains of Abraham 1759、Confederation 1867、Vimy Ridge 1917、1982 Charter、2021 TRC Day 都會在",
    ])


def build_government_body():
    return _stub("政府架構圖", "🏛️", [
        "圖 1：三級政府（聯邦 / 省 / 市）——各自管什麼，畫成樹狀圖",
        "圖 2：國會三部分（君主 → 參議院 + 眾議院）——權力結構流程圖",
        "圖 3：法案如何變法律（First Reading → Committee → Senate → Royal Assent）——橫向流程圖",
        "每個節點點開有英中對照解釋與考題提示",
    ])


def build_symbols_body():
    return _stub("國家象徵圖鑑", "🍁", [
        "國旗（1965 楓葉旗）、楓葉、河狸、皇冠、皇家紋章",
        "鈔票人物：$5 Laurier、$10 Viola Desmond（2018 起，首位非白人女性）、$20 女王伊麗莎白二世、$50 Mackenzie King、$100 Borden",
        "硬幣：1¢ Maple Leaf、5¢ Beaver、10¢ Bluenose、25¢ Caribou、$1 Loon（Loonie）、$2 Polar Bear（Toonie）",
        "國徽、皇家騎警 RCMP 制服、Order of Canada 楓葉勳章",
        "每張圖配上「為什麼考」「2026 最新狀態」",
    ])


def build_interactive_index_body():
    return '''
<style>
.iv-hub-hero {
  background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%);
  border-left: 4px solid var(--accent);
  padding: 22px 26px; border-radius: 10px; margin: 16px 0 28px;
}
.iv-hub-hero h1 { margin: 0 0 6px; font-size: 26px; }
.iv-hub-hero p { margin: 0; color: var(--muted); font-size: 15px; }

.iv-hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin: 24px 0; }
.iv-hub-card {
  display: block; padding: 22px 24px; background: #fff;
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
.iv-hub-emoji { font-size: 36px; line-height: 1; display: block; margin-bottom: 10px; }
.iv-hub-title { font-weight: 700; font-size: 18px; margin-bottom: 4px; }
.iv-hub-desc { font-size: 13px; color: var(--muted); line-height: 1.5; }
.iv-hub-status {
  display: inline-block; margin-top: 10px; padding: 2px 8px;
  border-radius: 4px; font-size: 11px; font-family: -apple-system, system-ui, sans-serif;
  letter-spacing: 0.04em; text-transform: uppercase;
}
.iv-hub-status.ready { background: #e8f5e8; color: #2d7a2d; }
.iv-hub-status.wip { background: #fff8e1; color: #b08400; }
</style>

<div class="iv-hub-hero">
  <h1>🎯 互動式學習中心</h1>
  <p>把抽象的考試內容變成圖、地圖、流程——用視覺記憶取代死背。</p>
</div>

<div class="iv-hub-grid">
  <a href="geography.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🗺️</span>
    <div class="iv-hub-title">地圖：13 省領地</div>
    <div class="iv-hub-desc">點省份看首府、省長、產業；Ontario 重點加大版面（你考試會被問）。</div>
    <span class="iv-hub-status ready">已完成</span>
  </a>

  <a href="history.html" class="iv-hub-card">
    <span class="iv-hub-emoji">📜</span>
    <div class="iv-hub-title">歷史時間軸</div>
    <div class="iv-hub-desc">1497 Cabot → 2021 TRC Day，按時代色標分區、每個事件點開有解說。</div>
    <span class="iv-hub-status wip">製作中</span>
  </a>

  <a href="government.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🏛️</span>
    <div class="iv-hub-title">政府架構圖</div>
    <div class="iv-hub-desc">3 張流程圖：三級政府、國會三部分、法案三讀流程。</div>
    <span class="iv-hub-status wip">製作中</span>
  </a>

  <a href="symbols.html" class="iv-hub-card">
    <span class="iv-hub-emoji">🍁</span>
    <div class="iv-hub-title">國家象徵圖鑑</div>
    <div class="iv-hub-desc">國旗、楓葉、河狸、鈔票人物、硬幣動物——全部視覺整理。</div>
    <span class="iv-hub-status wip">製作中</span>
  </a>
</div>

<p style="color: var(--muted); font-size: 14px;">
  進度條 ✓：覺得地圖頁好用嗎？告訴 AI「下一個做 [時間軸 / 政府架構 / 國家象徵]」就會展開。
</p>
'''
