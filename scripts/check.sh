#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
python3 product.py \
  --obsidian fixtures/obsidian-vault \
  --memory-text "$(cat fixtures/chatgpt-memory.txt)" \
  --birth-date 1990-04-18 \
  --birth-time "around 08:00" \
  --birth-place "Tokyo, Japan" \
  --time-precision approximate \
  --place-precision exact \
  --language en \
  --question "What evidence should I create before moving into my next role?" \
  --output /tmp/oracle-council-reading.md \
  >/tmp/oracle-council-result.json
python3 -m json.tool /tmp/oracle-council-result.json >/dev/null
node --check site/public/app.js
node --test site/tests/*.test.mjs
test -s /tmp/oracle-council-reading.md
test -f site/public/oracle.html
test -f site/public/app.js
test -f site/public/styles.css
(cd site && npm run build >/dev/null && npm audit >/dev/null)
echo "ORACLE_COUNCIL_CHECK_OK"
