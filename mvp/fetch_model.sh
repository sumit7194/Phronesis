#!/bin/bash
# Fetch a HF repo with curl instead of huggingface_hub.
# Why: on 2026-08-09 the Python downloader stalled repeatedly at 0 B/s while raw curl to the same
# CDN URL got 4 MB/s with working HTTP 206 range resume. Network was never the problem.
# Usage: ./fetch_model.sh <hf-id> <dest-dir>
set -u
ID="$1"; DEST="$2"
mkdir -p "$DEST"
TOKEN=$(.venv/bin/python -c "from huggingface_hub import get_token; print(get_token() or '')")
# The token goes in a 0600 curl config file, NOT on the command line. Passing it as -H put it in
# argv, where `ps` shows it to every process on the machine. 2026-08-11.
CURLRC=""
AUTH=()
if [ -n "$TOKEN" ]; then
  CURLRC=$(mktemp "${TMPDIR:-/tmp}/.hfcurl.XXXXXX")
  chmod 600 "$CURLRC"
  printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" > "$CURLRC"
  AUTH=(-K "$CURLRC")
  trap 'rm -f "$CURLRC"' EXIT INT TERM
fi
unset TOKEN
FILES=$(.venv/bin/python - "$ID" << 'PY'
import sys
from huggingface_hub import HfApi
i = HfApi().model_info(sys.argv[1])
for s in i.siblings:
    n = s.rfilename
    # Take every top-level file except docs/git metadata. An extension allow-list dropped
    # chat_template.jinja (so an instruct model was prompted with no turn structure and said yes
    # to everything) and merges.txt (needed by BPE tokenizers). 2026-08-10.
    if '/' in n:
        continue
    if n in ('.gitattributes', 'README.md', 'LICENSE', 'USE_POLICY.md') or n.endswith('.md'):
        continue
    print(n)
PY
)
[ -z "$FILES" ] && { echo "no files listed for $ID"; exit 1; }
for f in $FILES; do
  OUT="$DEST/$f"
  URL="https://huggingface.co/$ID/resolve/main/$f"
  SZ=$(curl -sIL "${AUTH[@]}" "$URL" | awk 'BEGIN{IGNORECASE=1}/^content-length:/{v=$2}END{gsub(/\r/,"",v);print v+0}')
  OK=0
  for attempt in 1 2 3 4 5 6 7 8; do
    HAVE=$(stat -f%z "$OUT" 2>/dev/null || echo 0)
    # verify against the SERVER-REPORTED size, never an arbitrary floor: config.json is
    # legitimately <1KB and a fixed minimum flagged it as a failure.
    if [ "$SZ" -gt 0 ] && [ "$HAVE" -ge "$SZ" ]; then OK=1; echo "  ok      $f ($((SZ/1048576))MB)"; break; fi
    echo "  fetch   $f  attempt $attempt  have $((HAVE/1048576))MB / $((SZ/1048576))MB"
    curl -sL "${AUTH[@]}" -C - --retry 3 --retry-delay 3 --speed-limit 10000 --speed-time 30 -o "$OUT" "$URL"
  done
  [ "$OK" -eq 0 ] && { echo "  FAILED  $f (have $(stat -f%z "$OUT" 2>/dev/null || echo 0) of $SZ)"; exit 1; }
done
echo "COMPLETE -> $DEST"
