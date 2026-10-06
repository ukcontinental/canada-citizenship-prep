# 加拿大公民考試學習網站 · 專案紀錄

給之後接手的 Claude（或人）看的。使用者是 Willie 一家人（本人、太太、兒子）。

## 網站

- 網址：https://ukcontinental.github.io/canada-citizenship-prep/ （GitHub Pages，`main` 分支根目錄；根目錄 `index.html` 跳轉到 `html/`）。push 後 1～2 分鐘上線。
- 姊妹站「陷阱題特訓」：https://ukcontinental.github.io/citizenship-quiz/ ，repo `ukcontinental/citizenship-quiz`（單一 `index.html`，細節看那邊的 CLAUDE.md）。

## 怎麼改

- `html/` 底下全是**產生出來的**，不要直接改 HTML。改 `build_html.py`、`quiz_content.py`、`interactive_content.py`、`cloud_sync.py` 等原始檔，再重新產生：
  ```
  pip install markdown   # 雲端環境沒裝
  python3 build_html.py  # 產生 52 頁 + html/study.html（單檔版）
  ```
  未改原始檔時重新產生，結果和 repo 內完全一樣（2026-10-06 驗證過），可以用 `git status` 確認改動範圍。
- 在 Willie 的 Mac 上執行時，`build_html.py` 最後會同步一份到 iCloud Drive「加拿大公民考試」資料夾（手機用「檔案」App 開的離線版）。雲端環境沒有 iCloud，會略過。
- repo 約 367MB（主要是錄好的音檔），clone 用 `--depth 1`。

## 錯題本與登入（cloud_sync.py）

- 題目引擎（`quiz_content.QUIZ_JS`）的錯題本仍存在 localStorage `cit_wrong_v2`，`saveBook` 存完會呼叫 `window.CIT_SYNC.push()`。
- `cloud_sync.SYNC_JS` 插在每一頁（`wrap_page`）和 `study.html` 結尾：在左側選單最上面放登入框，把 `cit_wrong_v2` 同步到 Firestore。
- 登入：名字＋4 位數密碼，`id = SHA-256("citz-v1|" + 名字小寫 + "|" + 密碼)`，存在 localStorage `citz-me`。**和 citizenship-quiz 同網域同 key，登入一次兩站都生效。**
- 雲端文件：Firebase 專案 `citizenship-quiz-27223` 的 Firestore `books/<SHA-256(id + "|prep")>`，欄位 `items`（JSON 字串）、`updated`。和陷阱題特訓站的錯題本是分開的兩本（題目 id 不同）。安全規則只允許 get／create／update，不能列出、不能刪除（規則全文見 citizenship-quiz 的 CLAUDE.md）。
- 本機狀態：`cit_wrong_owner`（本機這本是誰的）、`cit_wrong_pending`（誰有未上傳的修改，未上傳的本機修改優先）。換人時先把上一個人未上傳的修改送出，再清掉本機那本；登入前就存在的舊錯題本（沒有 owner）會併入**第一個登入的人**。
- 首次載入若雲端資料和本機不同，會重新整理頁面一次，讓題目重畫（用 sessionStorage `cit_sync_reloaded` 防止重複）。

## 測試方式

把 `html/` 和 citizenship-quiz 一起用本機 http server 放在同一個網域下（例如 `/canada-citizenship-prep/`、`/citizenship-quiz/`），用 Playwright 開多個 browser context 模擬多台裝置：舊錯題併入、同人跨裝置同步、移除同步、登出清空、換人分開、兩站共用登入。雲端環境的 Playwright 要設 `executablePath: '/opt/pw-browsers/chromium'`、proxy 加 `bypass: '<-loopback>'`、`--ignore-certificate-errors`。

## 進度紀錄

- 2026-10-06 加上登入與錯題本雲端同步（`cloud_sync.py`）、左側選單加上連到陷阱題特訓站的連結。
- 2026-10-06 修正 `interactive_content.NARRATION_CSS` 少了 `<style>` 標籤，造成人物時間軸、聯邦擴張時間軸、陷阱字典、study.html 上方出現一大段 CSS 文字、播放列沒有樣式。
