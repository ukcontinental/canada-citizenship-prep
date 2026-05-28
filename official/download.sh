#!/usr/bin/env bash
# 下載官方 Discover Canada PDF（驗證有效，2026-05-22）
# canada.ca 對某些 user-agent / 缺 Referer 會擋；下方 headers 是實際驗證可用的組合

set -e
cd "$(dirname "$0")"

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
REF="https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/discover-canada/download.html"

download_and_unzip () {
  local url="$1"; local out="$2"
  echo "→ $out"
  curl -L --connect-timeout 10 --max-time 90 \
    -H "User-Agent: $UA" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
    -H "Accept-Language: en-CA,en;q=0.9,fr-CA;q=0.8" \
    -H "Accept-Encoding: gzip, deflate, br" \
    -H "Referer: $REF" \
    -o "${out}.gz" "$url" -w "  HTTP:%{http_code} size:%{size_download}\n"
  # 回應為 gzip 時解壓；否則 rename
  if gunzip -t "${out}.gz" 2>/dev/null; then
    gunzip -f "${out}.gz"
  else
    mv "${out}.gz" "$out"
  fi
  file "$out"
}

download_and_unzip "https://www.canada.ca/content/dam/ircc/migration/ircc/english/pdf/pub/discover.pdf"        "discover-canada.pdf"
download_and_unzip "https://www.canada.ca/content/dam/ircc/migration/ircc/english/pdf/pub/discover-large.pdf"  "discover-canada-large.pdf"

echo
echo "完成。檔案："
ls -lh *.pdf
