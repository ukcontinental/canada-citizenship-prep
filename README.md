# 加拿大公民考試 14 天衝刺課程

> 對象：永久居民申請入籍，需通過 IRCC（移民部）公民考試。
> 教材：以官方《Discover Canada：The Rights and Responsibilities of Citizenship》為唯一範圍。
> 設計原則：每天 60～90 分鐘，含閱讀、重點筆記、20～40 題自我驗收。

## 考試規格

| 項目 | 內容 |
|---|---|
| 題型 | 選擇題＋是非題 |
| 題數 | 20 題（隨機抽自題庫，含 Ontario 省題） |
| 通過分數 | **15/20（75%）** |
| 作答時間 | 30 分鐘 |
| 題目來源 | **全部出自** Discover Canada |
| 考試語言 | 英文或法文（你自選） |

## 資料夾結構

```
canada-citizenship-prep/
├─ README.md                       ← 本檔，從這裡開始
├─ official/
│  ├─ download.sh                  ← 下載官方 PDF 腳本（已驗證有效）
│  ├─ discover-canada.pdf          ← 官方 PDF 11MB ✅
│  └─ discover-canada-large.pdf    ← 大字版 PDF ✅
├─ bilingual/                      ← 🆕 中英對照 PDF 原文（13 章）
│  ├─ README.md                    ← 章節索引
│  ├─ 00-intro-oath.md             ← 前言＋誓詞
│  ├─ 01-applying-citizenship.md   ← 申請入籍
│  ├─ 02-rights-responsibilities.md ← 權利與義務
│  ├─ 03-who-we-are.md             ← 我們是誰
│  ├─ 04-canadas-history.md        ← 加拿大歷史
│  ├─ 05-modern-canada.md          ← 現代加拿大
│  ├─ 06-how-canadians-govern.md   ← 政府架構
│  ├─ 07-federal-elections.md      ← 聯邦選舉
│  ├─ 08-justice-system.md         ← 司法系統
│  ├─ 09-canadian-symbols.md       ← 國家象徵＋國歌
│  ├─ 10-canadas-economy.md        ← 加拿大經濟
│  ├─ 11-canadas-regions.md        ← 五大區域＋10 省 3 領地
│  └─ 12-study-questions.md        ← 官方 28 條練習題
├─ curriculum/
│  └─ 14-day-plan.md               ← 14 天整體規劃表
├─ daily-quiz/
│  ├─ day-01.md … day-14.md        ← 每日教材＋驗收題＋答案
└─ practice/
   └─ question-bank.md             ← 220+ 題庫（依章節分類）
```

## 兩種使用方式

### 方式 A：跟著 14 天計畫走（推薦給新手）
從 [curriculum/14-day-plan.md](curriculum/14-day-plan.md) 開始，每天打開對應的 [daily-quiz/day-XX.md](daily-quiz/)。
驗收沒過 → 隔天重做。

### 方式 B：精讀 PDF 原文（推薦給想徹底搞懂的人）
從 [bilingual/README.md](bilingual/README.md) 開始，逐章對照英文與中文翻譯。
所有不一致的地方（PDF 2021 vs 2026 實際）都有「2026 更新」標註。

兩種方式可以混合：早上讀 bilingual 的某章，晚上做 daily-quiz 同一範圍的驗收題。

## 第一步：下載官方資料

```bash
bash /Users/willie/code/canada-citizenship-prep/official/download.sh
```

如果腳本回報「connection reset」（canada.ca 對部分網路 IP 有 bot 阻擋），請改用 **瀏覽器** 直接開以下網址，按右鍵「另存新檔」放到 `official/`：

- 標準 PDF：https://www.canada.ca/content/dam/ircc/migration/ircc/english/pdf/pub/discover.pdf
- 大字版 PDF：https://www.canada.ca/content/dam/ircc/migration/ircc/english/pdf/pub/discover-large.pdf
- 線上目錄頁：https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/discover-canada/read-online.html
- 官方練習題：https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/discover-canada/read-online/study-questions.html

## 第二步：照表操課

打開 `curriculum/14-day-plan.md`，從 Day 1 開始，每天：

1. **早上（30 分鐘）**：讀 `daily-quiz/day-XX.md` 上半的「今日重點」＋對照官方 PDF 該章節
2. **晚上（30 分鐘）**：做 `daily-quiz/day-XX.md` 下半的驗收題
3. **對答案**：每份檔案最底 `## 答案與解析` 折疊區
4. **記分**：低於 75% 隔天重做該章；連續兩天 90%+ 才可往下走

Day 7 與 Day 14 是模擬考，模擬真實考試環境（30 分鐘、20 題、不能翻書）。

## 第三步：考前一週

- 每天再跑一次 `practice/question-bank.md` 中你不熟的章節
- Ontario 省題務必背熟（Premier、Lt. Governor、首府、選區、產業）

## 重要：Ontario 省題會變動

省級政治人物隨選舉更替。考前 1 週請上 [Ontario.ca](https://www.ontario.ca) 確認當下：
- Premier（省長）
- Lieutenant Governor（省督）
- 你選區的 MP（聯邦國會議員）與 MPP（省議員）
- 在野黨領袖

本課程使用 2026 年 5 月當下最新資訊，但仍請臨考前再核對一次。

## 給自己的提醒

> 不要只「讀完」就以為會了——每天的驗收題沒拿到 15/20 就算當天沒過，**重來**。
