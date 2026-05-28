"""Interactive (visual) study modules — body HTML generators.

Each function returns inner-body HTML, ready to be wrapped by build_html.wrap_page().
Common interactive styles live in IV_SHARED_CSS; per-module CSS in each function.
"""

import json

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


# ============================================================================
# 11. GEOGRAPHY (already complete)
# ============================================================================

PROVINCES = [
    ("BC", "British Columbia", "卑詩省（不列顛哥倫比亞）", "West Coast",
     "Victoria 維多利亞", "David Eby（NDP）", "Wendy Cocchia（Lt. Governor）",
     ["木材、礦業、鮭魚捕撈、電影業（Hollywood North）",
      "華人移民歷史悠久，溫哥華是亞太門戶",
      "Vancouver 是大城，**Victoria** 才是首府（位於溫哥華島）"]),
    ("AB", "Alberta", "亞伯達省", "Prairie Provinces",
     "Edmonton 愛德蒙頓", "Danielle Smith（UCP）", "Salma Lakhani（Lt. Governor）",
     ["石油、天然氣（油砂 Oil Sands）、農業、牛肉",
      "Rocky Mountains 落磯山脈、Banff/Jasper 國家公園",
      "**Calgary** 是最大城但 **Edmonton** 才是首府"]),
    ("SK", "Saskatchewan", "薩斯喀徹溫省（沙省）", "Prairie Provinces",
     "Regina 雷吉納", "Scott Moe（Sask Party）", "Russ Mirasty（Lt. Governor）",
     ["小麥（Wheat Province）、鉀礦、鈾礦", "加拿大穀倉",
      "Saskatoon 是大城但 **Regina** 才是首府"]),
    ("MB", "Manitoba", "曼尼托巴省（曼省）", "Prairie Provinces",
     "Winnipeg 溫尼伯", "Wab Kinew（NDP，首位原住民省長）", "Anita Neville（Lt. Governor）",
     ["農業、礦業、水力發電", "Louis Riel 反抗運動的核心地（Métis 文化）",
      "1870 年加入聯邦（第 5 省）"]),
    ("ON", "Ontario ⭐", "安大略省（安省）", "Central Canada",
     "Toronto 多倫多", "Doug Ford（Progressive Conservative）",
     "Edith Dumont（Lt. Governor，首位法裔安省人，2023 起）",
     ["製造業、金融、服務業、科技",
      "**國都 Ottawa 渥太華位於此省**（不是 Toronto！）",
      "人口最多的省（約 1,500 萬，全國 40%）",
      "主要城市：Toronto、Ottawa、Hamilton、Mississauga、London",
      "**考試 Ontario 省題重點**：省長 Doug Ford 自 2018 連任至今，省督 Edith Dumont 2023 起",
      "你的選區記住：聯邦議員 MP & 省議員 MPP",
      "與美國邊境最長，五大湖區（Great Lakes）"]),
    ("QC", "Quebec", "魁北克省", "Central Canada",
     "Quebec City 魁北克市", "François Legault（CAQ）", "Manon Jeannotte（Lt. Governor）",
     ["航太、水電、礦業、軟體", "**唯一以法語為唯一官方語言的省**",
      "Montreal 蒙特婁是大城但 **Quebec City** 才是首府",
      "天主教文化深厚、有獨特民法系統",
      "1995 公投差點獨立（50.58% 反對）"]),
    ("NB", "New Brunswick", "新布倫瑞克省", "Atlantic Canada",
     "Fredericton 弗雷德里克頓", "Susan Holt（Liberal，2024 起）", "Louise Imbeault（Lt. Governor）",
     ["林業、漁業、食品加工", "**加拿大唯一官方雙語（英＋法）的省份**",
      "Acadian 文化重鎮（法裔但獨立於魁北克）"]),
    ("NS", "Nova Scotia", "新斯科舍省", "Atlantic Canada",
     "Halifax 哈利法克斯", "Tim Houston (Progressive Conservative)", "Mike Savage (Lt. Governor)",
     ["漁業、造船、旅遊", "**Bluenose 帆船**——10 分硬幣圖案",
      "**Pier 21** 全國移民登陸博物館", "**Bay of Fundy** 全球最高潮汐",
      "1605 法國人 Port-Royal 北美第一個歐洲殖民地"]),
    ("PE", "Prince Edward Island", "愛德華王子島（PEI）", "Atlantic Canada",
     "Charlottetown 夏洛特鎮", "Rob Lantz (PC, 2025 起)", "Wassim Salamoun (Lt. Governor)",
     ["馬鈴薯（產量全國第一）、觀光業、漁業", "**面積最小的省**",
      "**Confederation 發源地**——1864 Charlottetown Conference",
      "《清秀佳人 Anne of Green Gables》故鄉"]),
    ("NL", "Newfoundland and Labrador", "紐芬蘭與拉布拉多省", "Atlantic Canada",
     "St. John's 聖約翰斯", "Andrew Furey (Liberal)", "Joan Marie Aylward (Lt. Governor)",
     ["漁業（鱈魚 Cod）、海上石油、水電", "**最晚加入聯邦的省（1949）**",
      "**最東邊的省份**（時區比其他省早 30 分鐘）",
      "獨特方言；維京人 L'Anse aux Meadows 北美最早歐洲遺址"]),
    ("YT", "Yukon", "育空地區", "Northern Territories",
     "Whitehorse 白馬市", "Ranj Pillai (Liberal)", "Adeline Webber (Commissioner)",
     ["礦業、觀光", "**1898 Klondike 淘金潮**（人口曾經高達 4 萬）",
      "Yukon River、Mount Logan 加拿大最高峰"]),
    ("NT", "Northwest Territories", "西北地區", "Northern Territories",
     "Yellowknife 黃刀鎮", "R.J. Simpson (Independent)", "Gerald W. Kisoun (Commissioner)",
     ["鑽石、石油、天然氣", "Great Bear / Great Slave 兩大湖泊",
      "Dene 原住民、Métis 為主要族群",
      "11 種官方語言（含英、法、9 種原住民語）"]),
    ("NU", "Nunavut", "努納武特地區", "Northern Territories",
     "Iqaluit 伊魁特", "P.J. Akeeagok", "Eva Aariak (Commissioner)",
     ["礦業（金、鐵、鑽石）、傳統手工藝", "**1999 從 NT 分出來新建**（最年輕的領地）",
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
    facts_html = "".join(f"<li>{f}</li>" for f in facts)
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
                   "premier": premier, "lt_gov": lt_gov, "facts": facts}
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
        f'<div class="iv-region-card" style="background:{color}"><div class="label">Region</div><div class="name">{zh}</div><div class="codes">{" · ".join(codes)}</div></div>'
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
.iv-detail-zh {{ color: var(--muted); font-weight: 400; font-size: 18px; }}
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
  <p>點任何省份看它的首府、省長、產業重點。<strong>Ontario ⭐</strong> 是考試重點省，預設展開。</p>
</div>
{map_svg}
{detail}
<h2 class="iv-section-title">5 大區域速記</h2>
<div class="iv-region-row">{region_cards}</div>
<h2 class="iv-section-title">速查表</h2>
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
HISTORY_EVENTS = [
    ("1497", "John Cabot 抵達加拿大東岸", "John Cabot reaches Atlantic shores", "new-france",
     "為英王 Henry VII 宣稱大西洋岸土地，是歐洲人首次有記錄登陸加東",
     ["威尼斯航海家受英王委派", "登陸地點可能是 Newfoundland", "為日後英國對加宣稱主權奠基"]),
    ("1534", "Cartier 命名 'Canada'", "Cartier names 'Canada'", "new-france",
     "Jacques Cartier 第一次航行，從原住民 Iroquois 學到 'kanata'（村莊）一詞",
     ["第一次航行 1534、第二次 1535、第三次 1541", "為法王 François I 宣稱聖羅倫斯地區",
      "'Canada' 名字源自 Iroquois 語 'kanata'（kanata = 村莊/居住地）"]),
    ("1604", "首座歐洲永久定居 Port-Royal", "Port-Royal — first permanent settlement", "new-france",
     "Pierre du Gua de Monts 與 Samuel de Champlain 在 Acadia 建立",
     ["位於今日 Nova Scotia", "1605 年是北美第一個永久歐洲殖民地",
      "Acadia 文化由此開始"]),
    ("1608", "Champlain 建立 Québec City", "Champlain founds Quebec City", "new-france",
     "Samuel de Champlain 在聖羅倫斯河岸建立 Québec City，'Father of New France'",
     ["這是 New France 的首都", "Champlain 與原住民結盟貿易毛皮",
      "為法屬北美奠定基石"]),
    ("1670", "Hudson's Bay Company 成立", "Hudson's Bay Company chartered", "new-france",
     "英王 Charles II 給予 HBC 對 Hudson Bay 流域的貿易壟斷權",
     ["HBC 是現存最古老的商業公司之一", "推動英國在北方的擴張",
      "與法國的毛皮貿易競爭白熱化"]),
    ("1701", "Great Peace of Montreal", "Great Peace of Montreal", "new-france",
     "法國與 39 個原住民族在 Montreal 簽訂大和平條約",
     ["結束 Iroquois 與法國/盟友的戰爭", "新法蘭西進入和平擴張期"]),
    ("1755", "Acadian 大流亡", "Acadian Deportation", "new-france",
     "英國驅逐 Acadia 地區法裔居民（約 1 萬人）",
     ["稱為 'Le Grand Dérangement'",
      "部分人流亡到 Louisiana（後來變成 Cajun）",
      "部分人返回成為今日的 Acadian"]),
    ("1759", "Plains of Abraham 之戰 ⚔️", "Battle of the Plains of Abraham", "british",
     "**英軍 James Wolfe vs. 法軍 Montcalm**，英軍奪下 Québec City，新法蘭西結束",
     ["**考試重點戰役**", "兩位將軍都陣亡", "1763 Paris 條約正式將北美交給英國"]),
    ("1763", "Treaty of Paris：法割讓北美", "Treaty of Paris", "british",
     "七年戰爭結束，法國將北美除聖皮埃爾與密克隆外全部割讓給英國",
     ["新法蘭西成為英國殖民地 'Province of Quebec'",
      "Royal Proclamation 1763 承認原住民權利"]),
    ("1774", "Quebec Act 保障法裔權利", "Quebec Act", "british",
     "英國保障 Québec 法裔居民的天主教信仰、法國民法、語言",
     ["保留 French Civil Law（民事）", "保留天主教",
      "**為 Québec 法語文化存續的關鍵法案**"]),
    ("1776-83", "美國革命，Loyalists 北逃", "American Revolution — Loyalists flee north", "british",
     "約 4 萬 'United Empire Loyalists' 從美國逃到英屬北美",
     ["大量英裔人口湧入加拿大", "在 Nova Scotia、New Brunswick、Ontario 建立新社區",
      "1791 Constitutional Act 將 Quebec 分為 Upper / Lower Canada"]),
    ("1812-14", "1812 戰爭 — 加拿大守住了 ⚔️", "War of 1812 — Canada survives", "british",
     "美國入侵英屬北美，**加拿大、英軍、原住民聯軍擊退美軍**",
     ["**考試重點**", "Sir Isaac Brock 在 Queenston Heights 陣亡（英雄）",
      "原住民領袖 Tecumseh 也陣亡",
      "Laura Secord 徒步通報英軍美軍動向",
      "1814 英軍燒了 Washington 白宮"]),
    ("1837-38", "Upper / Lower Canada 叛亂", "Rebellions of 1837-38", "british",
     "改革派要求 'responsible government' 起義被鎮壓但促成改革",
     ["Upper Canada（今 Ontario）：William Lyon Mackenzie",
      "Lower Canada（今 Quebec）：Louis-Joseph Papineau",
      "促成 Lord Durham 報告 → 1840 Act of Union"]),
    ("1840", "Act of Union 統一兩 Canada", "Act of Union", "british",
     "Upper + Lower Canada 合併為 'Province of Canada'",
     ["Durham 報告建議責任政府", "1848 'Responsible Government' 實現於 Nova Scotia 與 Canada"]),
    ("1864", "Charlottetown Conference", "Charlottetown Conference", "confederation",
     "Confederation 規劃會議在 PEI Charlottetown 舉行",
     ["**'Birthplace of Confederation'**", "PEI 因此被稱為邦聯發源地",
      "與會者後稱 'Fathers of Confederation'"]),
    ("1867 ⭐", "邦聯誕生 — Dominion of Canada", "Confederation — Dominion of Canada", "confederation",
     "**英國國會通過 British North America Act**，加拿大成為英聯邦下的 Dominion",
     ["**考試最重要日期之一**",
      "成立四省：Ontario、Quebec、Nova Scotia、New Brunswick",
      "**首任總理 Sir John A. Macdonald**（保守黨）",
      "George-Étienne Cartier 是法裔共同創建者",
      "7 月 1 日 = **Canada Day**"]),
    ("1869-70", "Manitoba 加入 + Riel 起義", "Manitoba joins + Riel Rebellion", "confederation",
     "Métis 領袖 Louis Riel 起義，Manitoba 隨後加入聯邦",
     ["1870 Manitoba 加入（第 5 省）", "Louis Riel 是 Métis 民族英雄",
      "1885 Riel 第二次起義（North-West Rebellion）後被處決"]),
    ("1871", "British Columbia 加入", "British Columbia joins", "confederation",
     "BC 同意加入聯邦，條件是建一條橫貫鐵路", []),
    ("1873", "Prince Edward Island 加入", "PEI joins", "confederation", "PEI 1873 加入", []),
    ("1885", "太平洋鐵路完成 🚂", "Canadian Pacific Railway completed", "confederation",
     "鐵路橫貫加拿大東西，把 BC 連入聯邦",
     ["**Last Spike** 在 BC Craigellachie 釘下", "華工大量參與築路（許多人罹難）",
      "為加拿大統一的物理象徵"]),
    ("1898", "Yukon Territory 與 Klondike 淘金潮", "Yukon Territory & Klondike Gold Rush", "confederation",
     "Klondike 淘金潮帶來人口爆炸，Yukon 正式成為 territory", []),
    ("1905", "Alberta、Saskatchewan 加入", "Alberta & Saskatchewan join", "confederation",
     "兩省同時從 North-West Territories 切出", []),
    ("1914-18", "WWI — Vimy Ridge 🌹", "WWI — Vimy Ridge", "wars",
     "**1917 加拿大四師團首次合作攻下 Vimy Ridge**——加拿大民族認同的關鍵時刻",
     ["**考試重點**", "Vimy Ridge：1917 年 4 月，攻下英法都打不下的據點",
      "Passchendaele、Somme 也是慘烈戰役",
      "全國陣亡 ~6 萬", "1918 第一次世界大戰結束"]),
    ("1916-18", "婦女選舉權", "Women's suffrage", "wars",
     "Manitoba 1916 首先給女性投票權，聯邦 1918 跟進",
     ["Nellie McClung 等 'Famous Five' 推動",
      "**Manitoba 1916 = 第一個給女性投票權的省**"]),
    ("1929", "Persons Case — 女性是 'persons'", "Persons Case — women as legal persons", "wars",
     "Privy Council 裁定加拿大女性在法律上是 'persons'，可被任命為參議員",
     ["**Famous Five**：Emily Murphy 等 5 位女性推動",
      "勝訴後 Cairine Wilson 1930 成為首位女參議員"]),
    ("1931", "Statute of Westminster", "Statute of Westminster", "wars",
     "英國國會確認加拿大等 Dominion 在外交與立法上完全自主",
     ["加拿大實質獨立的法律基礎"]),
    ("1939-45", "WWII — D-Day Juno Beach", "WWII — D-Day at Juno Beach", "wars",
     "加軍在 D-Day（1944/6/6）登陸 Juno Beach，意大利戰役也激烈",
     ["**考試重點**", "Juno Beach 是五個 D-Day 灘頭之一（加拿大負責）",
      "全國陣亡 ~4 萬",
      "二戰結束後加拿大成為世界第 4 大空軍"]),
    ("1947", "Canadian Citizenship Act 通過", "Canadian Citizenship Act", "wars",
     "**加拿大公民身份首次法定**——之前是英國臣民",
     ["**考試重點**：首次有 'Canadian citizen' 這個身份",
      "首任公民身份證頒給總理 Mackenzie King"]),
    ("1949", "Newfoundland 加入（最後一省）", "Newfoundland joins (last province)", "wars",
     "公投通過後 Newfoundland 1949 加入聯邦，完成 10 省版圖",
     ["**考試重點**", "之前是英國自治領"]),
    ("1960", "原住民獲聯邦投票權", "Indigenous federal vote", "modern",
     "Status Indians 終於可以在聯邦選舉投票（不必放棄身份）", []),
    ("1965 ⭐", "楓葉旗誕生", "Maple Leaf flag adopted", "modern",
     "**2 月 15 日新國旗首次升起**——紅白楓葉旗取代英國 Red Ensign",
     ["**考試重點**", "Lester B. Pearson 總理推動",
      "**2 月 15 日 = National Flag of Canada Day**"]),
    ("1967", "Centennial / Expo '67", "Centennial / Expo '67", "modern",
     "聯邦 100 週年慶 + Montreal 世博會，是加拿大現代認同的形成期",
     ["Bobby Gimby 名曲 'Ca-na-da'", "Pierre Trudeau 1968 上任"]),
    ("1969", "Official Languages Act", "Official Languages Act", "modern",
     "聯邦政府所有服務必須英法雙語",
     ["**考試重點**", "Pierre Trudeau 推動",
      "聯邦政府工作必須提供雙語服務"]),
    ("1971", "多元文化主義政策", "Multiculturalism policy", "modern",
     "**加拿大成為世界第一個正式採取多元文化主義為國策**",
     ["1988 Canadian Multiculturalism Act 入法",
      "**'Mosaic' 而不是 'Melting Pot'**"]),
    ("1976", "Quebec PQ 上台 + 1980 公投", "Quebec PQ + 1980 referendum", "modern",
     "Parti Québécois 1976 上台，1980 第一次主權公投（59.6% No）", []),
    ("1982 ⭐", "Constitution Act / Charter", "Constitution Act + Charter", "modern",
     "**Constitution Act 1982**：憲法回到加拿大，含《加拿大權利與自由憲章》",
     ["**考試最重要日期**", "Pierre Trudeau 推動",
      "**Charter of Rights and Freedoms 保障：4 大自由、6 項權利、Aboriginal、Mobility、Official Language**",
      "Queen Elizabeth II 在 Ottawa 簽署"]),
    ("1995", "第二次 Quebec 公投", "Second Quebec referendum", "modern",
     "**50.58% No vs 49.42% Yes** — 差 5 萬票",
     ["1999 Clarity Act 規範未來公投程序"]),
    ("1999", "Nunavut 從 NT 分出", "Nunavut created", "modern",
     "**第三個 territory**，從 Northwest Territories 切出",
     ["**考試重點**：Nunavut 1999 年成立",
      "Inuit 為多數人口", "首府 Iqaluit"]),
    ("2008", "PM Harper 為寄宿學校道歉", "Harper apologizes for residential schools", "modern",
     "Stephen Harper 代表加拿大政府對 Indian Residential Schools 倖存者正式道歉", []),
    ("2015", "TRC 真相與和解報告", "TRC report", "modern",
     "Truth and Reconciliation Commission 發表報告與 94 項行動呼籲",
     ["揭露寄宿學校系統性暴力與文化滅絕"]),
    ("2021 ⭐", "TRC Day 國定假日", "TRC Day becomes national holiday", "modern",
     "**National Day for Truth and Reconciliation（9/30）正式列為國定假日**",
     ["**考試重點**：Truth and Reconciliation Day = 9 月 30 日",
      "穿橘色衣（Orange Shirt Day）紀念寄宿學校受害者"]),
]

ERAS = [
    ("new-france", "新法蘭西時期 (1497-1763)", "#4a6fa5"),
    ("british", "英屬北美 (1763-1867)", "#b0413e"),
    ("confederation", "邦聯時代 (1867-1914)", "#c8a040"),
    ("wars", "兩戰與改革 (1914-1949)", "#7a8c5c"),
    ("modern", "現代加拿大 (1949-至今)", "#5a9460"),
]

ERA_COLOR = {era_id: color for era_id, _, color in ERAS}


def build_history_body():
    timeline_html = ""
    for year, title_zh, title_en, era, brief, details in HISTORY_EVENTS:
        color = ERA_COLOR[era]
        details_html = ""
        if details:
            details_html = "<ul class='iv-tl-details'>" + "".join(f"<li>{d}</li>" for d in details) + "</ul>"
        is_star = "⭐" in year or "⭐" in title_zh
        timeline_html += f'''
<div class="iv-tl-event {'iv-tl-star' if is_star else ''}" data-era="{era}">
  <div class="iv-tl-marker" style="background:{color}"></div>
  <div class="iv-tl-year">{year}</div>
  <div class="iv-tl-content">
    <h3 class="iv-tl-title">{title_zh}</h3>
    <div class="iv-tl-en">{title_en}</div>
    <p class="iv-tl-brief">{brief}</p>
    {details_html}
  </div>
</div>'''

    era_filters = "".join(
        f'<button class="iv-era-btn" data-era="{era_id}" style="--era-color:{color}">{label}</button>'
        for era_id, label, color in ERAS
    )

    return f'''{IV_SHARED_CSS}
<style>
.iv-era-filter {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 24px; }}
.iv-era-btn {{
  appearance: none; padding: 6px 12px; border-radius: 20px;
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
.iv-tl-en {{ font-size: 12px; color: var(--muted); font-style: italic; margin-bottom: 6px; }}
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
  <h1>📜 加拿大歷史時間軸</h1>
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
PRIME_MINISTERS = [
    ("Sir John A. Macdonald", "麥當勞爵士", "Conservative", "1867-1873, 1878-1891",
     ["**首任總理（建國之父）**", "推動 Confederation 與太平洋鐵路", "Kingston ON 紀念雕像"]),
    ("Wilfrid Laurier", "勞瑞葉", "Liberal", "1896-1911",
     ["**第一位法裔總理**", "推動 Alberta、Saskatchewan 1905 加入", "$5 鈔票人物"]),
    ("Sir Robert Borden", "波頓爵士", "Conservative", "1911-1920",
     ["帶領加拿大度過 WWI", "**Vimy Ridge 1917** 期間任內", "$100 鈔票人物"]),
    ("William Lyon Mackenzie King", "麥肯齊·金", "Liberal", "1921-1930, 1935-1948",
     ["**任期最長的總理**（22 年）", "**1947 Canadian Citizenship Act** 首位公民身份證得主",
      "$50 鈔票人物"]),
    ("Louis St-Laurent", "聖羅倫", "Liberal", "1948-1957",
     ["推動 Newfoundland 1949 加入", "創建 NATO 北約", "建立 Trans-Canada Highway"]),
    ("John Diefenbaker", "迪芬貝克", "Progressive Conservative", "1957-1963",
     ["**1960 通過 Canadian Bill of Rights**", "**1960 給原住民聯邦投票權**",
      "Saskatchewan 出身"]),
    ("Lester B. Pearson", "皮爾遜", "Liberal", "1963-1968",
     ["**諾貝爾和平獎得主**（1957，推動 UN 維和）", "**1965 推動楓葉旗誕生**",
      "**1966 全民健保 Medicare** 立法", "Toronto Pearson 機場以他命名"]),
    ("Pierre Trudeau", "老杜魯道", "Liberal", "1968-1979, 1980-1984",
     ["**1969 Official Languages Act**", "**1971 多元文化主義**",
      "**1982 Constitution Act + Charter ⭐**", "魅力型總理"]),
    ("Brian Mulroney", "穆隆尼", "Progressive Conservative", "1984-1993",
     ["1988 **Multiculturalism Act 入法**", "**1989 USFTA 自由貿易協定**（後 NAFTA、CUSMA）",
      "1991 GST 消費稅"]),
    ("Jean Chrétien", "克雷蒂安", "Liberal", "1993-2003",
     ["**1995 第二次 Quebec 公投**期間任內", "1999 創建 Nunavut", "拒絕加入 2003 伊拉克戰爭"]),
    ("Paul Martin", "馬丁", "Liberal", "2003-2006",
     ["前財政部長，被譽為平衡預算之父", "短暫任期"]),
    ("Stephen Harper", "哈珀", "Conservative", "2006-2015",
     ["**2008 為寄宿學校道歉 ⭐**", "Alberta 出身", "推動經濟保守政策"]),
    ("Justin Trudeau", "小杜魯道", "Liberal", "2015-2025",
     ["**老杜魯道之子**", "**2021 TRC Day 國定假日 ⭐**", "推動大麻合法化（2018）",
      "**多次原住民和解政策**"]),
    ("Mark Carney", "卡尼", "Liberal", "2025-至今",
     ["**前 Bank of Canada 與 Bank of England 行長**",
      "**2025 春季就任，2026 大選後續任**",
      "金融專業背景"]),
]

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
        facts_html = "".join(f"<li>{f}</li>" for f in facts)
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
.iv-pm-zh {{ color: var(--muted); font-size: 14px; }}
.iv-pm-party {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: #fff; letter-spacing: 0.04em; font-family: -apple-system, system-ui, sans-serif; }}
.iv-pm-years {{ font-family: monospace; font-size: 12px; color: var(--muted); margin-bottom: 8px; }}
.iv-pm-facts {{ margin: 0; padding-left: 18px; font-size: 13px; }}
.iv-pm-facts li {{ margin: 3px 0; }}
.iv-milestones {{ background: #faf8f4; border-radius: 10px; padding: 12px 16px; margin: 16px 0; }}
.iv-ms {{ display: grid; grid-template-columns: 70px 1fr 1.5fr; gap: 10px; padding: 6px 0; border-bottom: 1px dashed var(--line); align-items: center; }}
.iv-ms:last-child {{ border-bottom: none; }}
.iv-ms-year {{ font-family: monospace; font-weight: 700; color: var(--accent); }}
.iv-ms-zh {{ font-weight: 600; font-size: 14px; }}
.iv-ms-en {{ color: var(--muted); font-size: 13px; font-style: italic; }}
</style>
<div class="iv-hero">
  <h1>🇨🇦 現代加拿大（PM 與里程碑）</h1>
  <p>14 位戰後總理畫廊 + 11 件現代加拿大關鍵法案／事件。⭐ = 考試重點。</p>
</div>
<h2 class="iv-section-title">歷任總理（建國至今 14 位重要人物）</h2>
<div class="iv-pm-grid">{pm_cards}</div>
<h2 class="iv-section-title">現代加拿大里程碑</h2>
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
  <h1>🏛️ 加拿大政府架構（圖解）</h1>
  <p>三張流程圖：三級政府職責、國會三部分、法案如何變法律。</p>
</div>

<h2 class="iv-section-title">圖 1：三級政府（誰管什麼）</h2>
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
<div class="iv-gov-legend">
  <div class="iv-gov-leg-item"><div class="iv-gov-dot" style="background:#c8102e"></div><div><strong>聯邦 Federal</strong>管全國事務，總理 Mark Carney（2025-）</div></div>
  <div class="iv-gov-leg-item"><div class="iv-gov-dot" style="background:#4a6fa5"></div><div><strong>省 Provincial</strong>管教育/醫療，Ontario 省長 Doug Ford</div></div>
  <div class="iv-gov-leg-item"><div class="iv-gov-dot" style="background:#5a9460"></div><div><strong>市政 Municipal</strong>管在地事務，Toronto 市長 Olivia Chow</div></div>
</div>
</div>

<h2 class="iv-section-title">圖 2：國會 Parliament 三部分</h2>
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
  <text x="600" y="200" text-anchor="middle" font-size="13" fill="#fff">338 位 MPs（國會議員）</text>
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

<h2 class="iv-section-title">圖 3：法案如何變法律（7 步驟）</h2>
<div class="iv-gov-diagram">
<div class="iv-bill-flow">
  <div class="iv-bill-step"><div class="num">1</div><div class="title">一讀 First Reading</div><div class="desc">眾議院介紹法案</div></div>
  <div class="iv-bill-step"><div class="num">2</div><div class="title">二讀 Second Reading</div><div class="desc">辯論原則</div></div>
  <div class="iv-bill-step"><div class="num">3</div><div class="title">委員會 Committee</div><div class="desc">逐條審議</div></div>
  <div class="iv-bill-step"><div class="num">4</div><div class="title">報告 Report</div><div class="desc">考慮修正</div></div>
  <div class="iv-bill-step"><div class="num">5</div><div class="title">三讀 Third Reading</div><div class="desc">最後辯論與表決</div></div>
  <div class="iv-bill-step"><div class="num">6</div><div class="title">參議院 Senate</div><div class="desc">同樣 3 讀流程</div></div>
  <div class="iv-bill-step"><div class="num">7</div><div class="title">御准 Royal Assent</div><div class="desc">GG 代簽 → 法律</div></div>
</div>
<p style="font-size:13px; color:var(--muted); margin-top:8px">⭐ <strong>考試重點</strong>：3 讀＋委員會＋送參議院＋御准。法案在每院都要 3 讀。</p>
</div>
'''


# ============================================================================
# 07. FEDERAL ELECTIONS
# ============================================================================

PARTIES = [
    ("Liberal Party", "自由黨", "#d71920", "Mark Carney", "現執政黨（2025-）",
     ["中間偏左", "支持多元文化、社會福利", "現任 PM 政黨"]),
    ("Conservative Party", "保守黨", "#1A4782", "Pierre Poilievre", "主要在野黨",
     ["中間偏右", "支持經濟自由、傳統價值", "前身 PC 黨於 2003 與聯盟黨合併"]),
    ("New Democratic Party (NDP)", "新民主黨", "#F58220", "Don Davies (interim, 2025)",
     "第三大黨", ["左派、勞工", "推動社會醫療與社福"]),
    ("Bloc Québécois", "魁北克集團", "#0088CE", "Yves-François Blanchet", "只在魁北克省競選",
     ["主張魁北克利益與獨立可能", "只在 Quebec 推候選人"]),
    ("Green Party", "綠黨", "#3D9B35", "Jonathan Pedneault & Elizabeth May",
     "環保政黨", ["氣候變遷、永續政策", "規模較小但在西岸有支持"]),
]


def build_elections_body():
    party_cards = ""
    for en, zh, color, leader, status, facts in PARTIES:
        facts_html = "".join(f"<li>{f}</li>" for f in facts)
        party_cards += f'''
<div class="iv-party-card" style="border-top-color:{color}">
  <div class="iv-party-name">{en}</div>
  <div class="iv-party-zh">{zh}</div>
  <div class="iv-party-leader">領袖：<strong>{leader}</strong></div>
  <div class="iv-party-status">{status}</div>
  <ul class="iv-party-facts">{facts_html}</ul>
</div>'''

    return f'''{IV_SHARED_CSS}
<style>
.iv-party-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 16px 0; }}
.iv-party-card {{ background: #fff; border: 1px solid var(--line); border-top-width: 4px; border-radius: 10px; padding: 14px 16px; }}
.iv-party-name {{ font-weight: 700; font-size: 15px; }}
.iv-party-zh {{ color: var(--muted); font-size: 13px; margin-bottom: 6px; }}
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
  <h1>🗳️ 加拿大聯邦選舉</h1>
  <p>5 大政黨 + 投票資格 + 選舉流程 + 5 個必考重點。</p>
</div>

<h2 class="iv-section-title">5 大主要政黨</h2>
<div class="iv-party-grid">{party_cards}</div>

<h2 class="iv-section-title">投票資格 & 流程</h2>
<div class="iv-vote-steps">
  <div class="iv-vote-step"><div class="icon">🇨🇦</div><strong>1. 公民身份</strong><p>必須是 Canadian Citizen（永久居民不能投）</p></div>
  <div class="iv-vote-step"><div class="icon">🎂</div><strong>2. 年滿 18 歲</strong><p>投票日當天滿 18</p></div>
  <div class="iv-vote-step"><div class="icon">📬</div><strong>3. 收 Voter Card</strong><p>Elections Canada 寄出</p></div>
  <div class="iv-vote-step"><div class="icon">🏠</div><strong>4. 到指定投票所</strong><p>帶身份證明 + 地址證明</p></div>
  <div class="iv-vote-step"><div class="icon">✏️</div><strong>5. 圈選候選人</strong><p>選你選區（Riding）的 MP 候選人</p></div>
</div>

<h2 class="iv-section-title">考試 5 大必背重點</h2>
<div class="iv-facts">
  <div class="iv-fact-row"><strong>選舉週期</strong><span>每 <strong>4 年</strong>最長一次（PM 可提早解散）</span></div>
  <div class="iv-fact-row"><strong>眾議院席次</strong><span>共 <strong>338 位 MP</strong>（每個選區 Riding 一位）</span></div>
  <div class="iv-fact-row"><strong>誰當總理 PM</strong><span>眾議院席次最多政黨的領袖通常成為 PM</span></div>
  <div class="iv-fact-row"><strong>誰能投票</strong><span>公民 + 18 歲 + 在 Voter List 上</span></div>
  <div class="iv-fact-row"><strong>Ontario 你的選區</strong><span>記住你的 <strong>MP（聯邦）</strong>和 <strong>MPP（省議員）</strong>姓名</span></div>
</div>
'''


# ============================================================================
# 08. JUSTICE SYSTEM — Court hierarchy
# ============================================================================

JUSTICE_PRINCIPLES = [
    ("法治", "Rule of Law", "沒人凌駕於法律之上，包括政府"),
    ("無罪推定", "Presumption of Innocence", "被告在被定罪前推定無罪"),
    ("人身保護令", "Habeas Corpus", "防止任意拘禁，被拘留者可請求出庭"),
    ("公平審判", "Fair Trial", "公開、獨立、公正、由陪審團或法官審理"),
    ("法律之前人人平等", "Equality before the Law", "Charter 第 15 條"),
]


def build_justice_body():
    principles_cards = ""
    for zh, en, desc in JUSTICE_PRINCIPLES:
        principles_cards += f'<div class="iv-principle"><h4>{zh}</h4><div class="en">{en}</div><p>{desc}</p></div>'

    return f'''{IV_SHARED_CSS}
<style>
.iv-court-hierarchy {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 20px; margin: 16px 0; }}
.iv-court-svg {{ width: 100%; height: auto; }}
.iv-principles-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }}
.iv-principle {{ background: #fff; border-left: 4px solid var(--accent); padding: 12px 16px; border-radius: 6px; }}
.iv-principle h4 {{ margin: 0 0 2px; font-size: 15px; }}
.iv-principle .en {{ font-size: 12px; color: var(--muted); font-style: italic; margin-bottom: 6px; }}
.iv-principle p {{ margin: 0; font-size: 13px; }}
.iv-rcmp {{ background: linear-gradient(135deg, #fff8f8 0%, #fef0e8 100%); padding: 20px 24px; border-radius: 10px; margin: 16px 0; }}
.iv-rcmp h3 {{ margin: 0 0 8px; }}
.iv-rcmp ul {{ margin: 8px 0 0; padding-left: 20px; font-size: 14px; }}
</style>
<div class="iv-hero">
  <h1>⚖️ 加拿大司法系統</h1>
  <p>5 大法律原則 + 4 級法院階層 + RCMP 角色。</p>
</div>

<h2 class="iv-section-title">5 大法律原則</h2>
<div class="iv-principles-grid">{principles_cards}</div>

<h2 class="iv-section-title">4 級法院階層（金字塔）</h2>
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
<ul>
  <li><strong>聯邦警察</strong>：執行聯邦法律（毒品、洗錢、跨省犯罪）</li>
  <li><strong>省/地方警察</strong>：8 省與 3 領地外包 RCMP 為省警（Ontario 跟 Quebec 例外有自己的省警）</li>
  <li><strong>市政警察</strong>：少數小鎮外包 RCMP</li>
  <li><strong>象徵</strong>：紅色制服 Red Serge、Stetson 帽、Musical Ride 表演</li>
  <li><strong>歷史</strong>：1873 成立為 North-West Mounted Police</li>
  <li><strong>總部</strong>：Ottawa</li>
</ul>
</div>
'''


# ============================================================================
# 09. NATIONAL SYMBOLS — visual gallery
# ============================================================================

SYMBOLS = [
    ("🍁", "楓葉", "Maple Leaf", "國家象徵植物，國旗中心",
     ["1965 楓葉旗誕生", "11 個葉尖代表 10 省 3 領地的整體", "硬幣 1¢ 圖案"]),
    ("🚩", "國旗", "National Flag", "紅白楓葉旗",
     ["**1965 年 2 月 15 日**首次升起", "Pearson 總理推動",
      "**2/15 = National Flag Day**", "前身是 Red Ensign（含 Union Jack）"]),
    ("👑", "皇冠 / 君主", "The Crown", "King Charles III",
     ["**2022 年 9 月 8 日 Elizabeth II 過世，Charles III 即位**",
      "加拿大是 Constitutional Monarchy", "Governor General Mary Simon 代表"]),
    ("🦫", "河狸", "Beaver", "國家動物，5 分硬幣圖案",
     ["毛皮貿易歷史核心", "Hudson's Bay Company 早期主要交易商品",
      "1975 正式列為國家象徵"]),
    ("🛡️", "皇家紋章", "Coat of Arms", "1921 採用，加拿大政府正式徽記",
     ["四等分顯示英、蘇、愛、法歷史血脈", "獅與獨角獸守護",
      "底部楓葉與 'A Mari Usque Ad Mare'（from sea to sea）"]),
    ("🎵", "國歌", "O Canada", "1980 正式國歌",
     ["1880 由 Calixa Lavallée 譜曲（英法雙詞）",
      "**2018 改 'in all of us command'**（去性別化）",
      "皇室國歌仍是 'God Save the King'"]),
    ("🌹", "Vimy Ridge", "Vimy Ridge", "1917 加拿大關鍵戰役",
     ["四師團首次合作", "民族認同的關鍵時刻", "法國 Vimy 有加拿大紀念碑"]),
    ("🪶", "Order of Canada", "楓葉勳章", "1967 設立的最高榮譽制度",
     ["3 級：Companion、Officer、Member",
      "格言：'Desiderantes meliorem patriam'（願望更好的祖國）"]),
    ("💰", "Loonie & Toonie", "1元、2元硬幣", "Loonie 1987、Toonie 1996",
     ["Loonie：1 元，刻 Loon 潛鳥", "Toonie：2 元，刻 Polar Bear 北極熊",
      "都是 1987 後設計"]),
    ("📜", "Magna Carta", "大憲章 1215", "權利傳統 800 年起源",
     ["雖在英國，但影響加拿大法律", "**Habeas Corpus** 源於此",
      "Charter 序言提及"]),
]

CURRENCY_FIGURES = [
    ("$5", "Wilfrid Laurier", "勞瑞葉", "第一位法裔總理"),
    ("$10", "Viola Desmond ⭐", "Viola Desmond", "**2018 起首位非白人女性**——民權運動先驅"),
    ("$20", "Queen Elizabeth II", "伊莉莎白二世", "（2024 起印新版可能換 Charles III）"),
    ("$50", "Mackenzie King", "麥肯齊·金", "任期最長的總理"),
    ("$100", "Robert Borden", "波頓爵士", "WWI 期間總理"),
]

NATIONAL_HOLIDAYS = [
    ("1/1", "New Year's Day", "元旦"),
    ("4 月", "Good Friday & Easter Monday", "復活節週五與週一"),
    ("5 月 月底週一", "Victoria Day", "維多利亞日（女王生日）"),
    ("6/24", "Saint-Jean-Baptiste Day（QC only）", "聖讓巴蒂斯特日（魁省）"),
    ("7/1 ⭐", "Canada Day", "加拿大國慶日（邦聯 1867）"),
    ("8 月 第一個週一", "Civic Holiday（多省）", "公民日"),
    ("9 月 第一個週一", "Labour Day", "勞動節"),
    ("9/30 ⭐", "Truth and Reconciliation Day", "真相與和解日（2021 起）"),
    ("10 月 第二個週一", "Thanksgiving", "感恩節"),
    ("11/11", "Remembrance Day", "陣亡將士紀念日（戴紅罌粟）"),
    ("12/25", "Christmas Day", "聖誕節"),
    ("12/26", "Boxing Day", "節禮日"),
]


def build_symbols_body():
    symbol_cards = ""
    for emoji, zh, en, brief, facts in SYMBOLS:
        facts_html = "".join(f"<li>{f}</li>" for f in facts)
        symbol_cards += f'''
<div class="iv-sym-card">
  <div class="iv-sym-emoji">{emoji}</div>
  <h3>{zh} <span class="en">{en}</span></h3>
  <p class="brief">{brief}</p>
  <ul>{facts_html}</ul>
</div>'''

    currency_rows = ""
    for denom, en, zh, note in CURRENCY_FIGURES:
        currency_rows += f'<div class="iv-bill-row"><div class="denom">{denom}</div><div class="figure"><strong>{en}</strong><div class="zh">{zh}</div></div><div class="note">{note}</div></div>'

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
.iv-sym-card h3 .en {{ color: var(--muted); font-weight: 400; font-size: 13px; font-style: italic; }}
.iv-sym-card .brief {{ font-size: 13px; color: var(--muted); margin: 0 0 8px; }}
.iv-sym-card ul {{ margin: 0; padding-left: 18px; font-size: 13px; }}
.iv-sym-card ul li {{ margin: 3px 0; }}
.iv-bill-row {{ display: grid; grid-template-columns: 70px 1fr 2fr; gap: 14px; padding: 10px 0; border-bottom: 1px dashed var(--line); align-items: center; font-size: 14px; }}
.iv-bill-row .denom {{ font-family: monospace; font-weight: 700; font-size: 20px; color: var(--accent); }}
.iv-bill-row .zh {{ font-size: 12px; color: var(--muted); }}
.iv-bill-row .note {{ font-size: 13px; }}
.iv-hol-row {{ display: grid; grid-template-columns: 130px 1fr 1fr; gap: 10px; padding: 6px 10px; border-bottom: 1px dashed var(--line); font-size: 13px; align-items: center; }}
.iv-hol-row.star {{ background: linear-gradient(90deg, #fff8e8 0%, transparent 100%); border-radius: 4px; }}
.iv-hol-row .date {{ font-family: monospace; font-size: 12px; color: var(--muted); }}
.iv-hol-row .hol-en {{ font-weight: 600; }}
.iv-hol-row .hol-zh {{ color: var(--muted); }}
</style>
<div class="iv-hero">
  <h1>🍁 加拿大國家象徵圖鑑</h1>
  <p>象徵、鈔票、硬幣、國定假日——視覺整理一次到位。</p>
</div>

<h2 class="iv-section-title">10 大國家象徵</h2>
<div class="iv-sym-grid">{symbol_cards}</div>

<h2 class="iv-section-title">鈔票上的人物</h2>
<div>{currency_rows}</div>

<h2 class="iv-section-title">硬幣上的動物</h2>
<div class="iv-card-grid" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr))">
  <div class="iv-card"><strong>1¢</strong> Maple Leaf 楓葉<br><span class="meta">已停產 2013</span></div>
  <div class="iv-card"><strong>5¢</strong> Beaver 河狸 🦫</div>
  <div class="iv-card"><strong>10¢</strong> Bluenose 帆船 ⛵</div>
  <div class="iv-card"><strong>25¢</strong> Caribou 馴鹿 🦌</div>
  <div class="iv-card"><strong>$1 Loonie</strong> Loon 潛鳥</div>
  <div class="iv-card"><strong>$2 Toonie</strong> Polar Bear 北極熊 🐻‍❄️</div>
</div>

<h2 class="iv-section-title">12 個國定/重要假日</h2>
<div>{holidays_rows}</div>
'''


# ============================================================================
# 10. CANADA'S ECONOMY
# ============================================================================

INDUSTRIES = [
    ("服務業", "Services Industries", 75, "#c8102e",
     "金融、零售、教育、醫療、政府、餐飲、IT —— 約四分之三的工作"),
    ("製造業", "Manufacturing", 13, "#4a6fa5",
     "汽車（Ontario）、航太（Quebec）、鋼鐵、紙業 —— Ontario / Quebec 為主"),
    ("天然資源", "Natural Resources", 12, "#5a9460",
     "石油天然氣（AB/SK）、礦業（鈾、鉀、鎳）、林業、漁業 —— 草原省與大西洋"),
]

TRADE_FACTS = [
    ("最大貿易夥伴", "United States 美國", "75%+ 的出口都到美國"),
    ("USMCA / CUSMA", "美加墨自由貿易協定", "2020 年取代 NAFTA"),
    ("國際組織會員", "G7、G20、NATO、UN、WTO、APEC、Commonwealth、La Francophonie",
     "G7 等於老牌工業大國（從 G8 改回 G7，因 2014 俄羅斯被剔除）"),
    ("貨幣", "Canadian Dollar（CAD / $）", "由 Bank of Canada 發行管理"),
    ("經濟體規模", "全球第 9 大經濟體（GDP 約 $2.2 兆美元）", "人均高度發達"),
]


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
  <p>{desc}</p>
</div>'''

    trade_rows = ""
    for k, v, note in TRADE_FACTS:
        trade_rows += f'<div class="iv-trade-row"><div class="key">{k}</div><div class="val"><strong>{v}</strong><div class="note">{note}</div></div></div>'

    return f'''{IV_SHARED_CSS}
<style>
.iv-pie-wrap {{ display: flex; flex-wrap: wrap; gap: 24px; align-items: center; margin: 16px 0; }}
.iv-pie {{ width: 300px; max-width: 100%; }}
.iv-ind-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; flex: 1; min-width: 280px; }}
.iv-ind-card {{ background: #fff; border: 1px solid var(--line); border-top-width: 4px; border-radius: 10px; padding: 14px 16px; }}
.iv-ind-pct {{ font-size: 28px; font-weight: 700; font-family: monospace; }}
.iv-ind-card h4 {{ margin: 4px 0; font-size: 16px; }}
.iv-ind-card .en {{ font-size: 12px; color: var(--muted); font-style: italic; margin-bottom: 6px; }}
.iv-ind-card p {{ margin: 0; font-size: 13px; }}
.iv-trade-row {{ display: grid; grid-template-columns: 160px 1fr; gap: 16px; padding: 10px 0; border-bottom: 1px dashed var(--line); font-size: 14px; }}
.iv-trade-row .key {{ font-weight: 600; color: var(--accent); }}
.iv-trade-row .note {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
</style>
<div class="iv-hero">
  <h1>💼 加拿大經濟</h1>
  <p>三大產業比例 + 5 個必考經濟事實。</p>
</div>

<h2 class="iv-section-title">三大產業（GDP / 就業比重）</h2>
<div class="iv-pie-wrap">
  <svg viewBox="0 0 300 300" class="iv-pie">{pie_segments}</svg>
  <div class="iv-ind-cards">{industry_cards}</div>
</div>

<h2 class="iv-section-title">5 大必背經濟事實</h2>
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
  <h1>🎯 互動式學習中心</h1>
  <p>把抽象的考試內容變成圖、地圖、時間軸、流程——用視覺記憶取代死背。對應教材 04~11 章。</p>
</div>

<div class="iv-hub-grid">
  <a href="history.html" class="iv-hub-card">
    <span class="iv-hub-emoji">📜</span>
    <div class="iv-hub-chap">04 章</div>
    <div class="iv-hub-title">歷史時間軸</div>
    <div class="iv-hub-desc">1497 → 2021，41 事件，5 時代色標、可篩選</div>
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
