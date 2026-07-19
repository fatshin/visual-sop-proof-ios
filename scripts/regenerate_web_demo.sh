#!/bin/zsh
set -euo pipefail

if (( $# != 4 )); then
  print -u2 "Usage: regenerate_web_demo.sh <site-directory> <port> <narration.txt> <output.mp4>"
  exit 1
fi

SITE_DIR=${1:A}
PORT=$2
NARRATION=${3:A}
OUTPUT=${4:A}
ROOT_DIR=${0:A:h:h}
NODE_BIN=${CODEX_BUNDLED_NODE:-$(command -v node || true)}
NODE_MODULES=${CODEX_BUNDLED_NODE_MODULES:-${NODE_PATH:-}}

if [[ -z "$NODE_BIN" || ! -x "$NODE_BIN" ]]; then
  print -u2 "Node.js was not found on PATH. Set CODEX_BUNDLED_NODE to an executable path."
  exit 1
fi
if [[ -n "$NODE_MODULES" ]]; then
  export NODE_PATH="$NODE_MODULES"
fi
if ! "$NODE_BIN" -e 'require.resolve("playwright")' >/dev/null 2>&1; then
  print -u2 "Playwright is not resolvable. Install it or set CODEX_BUNDLED_NODE_MODULES/NODE_PATH."
  exit 1
fi

WORK_DIR=$(mktemp -d)
FRAME_DIR="$WORK_DIR/frames"
SERVER_LOG="$WORK_DIR/site-server.log"
mkdir -p "$FRAME_DIR"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    pkill -TERM -P "$SERVER_PID" 2>/dev/null || true
    kill "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT INT TERM

(
  cd "$SITE_DIR"
  tail -f /dev/null | script -q /dev/null npm run dev -- --host 127.0.0.1 --port "$PORT"
) > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

READY=false
for _ in {1..80}; do
  if curl --silent --fail "http://localhost:$PORT/" >/dev/null; then
    READY=true
    break
  fi
  sleep 0.25
done

if [[ "$READY" != "true" ]]; then
  print -u2 "Site did not become ready:"
  sed -n '1,160p' "$SERVER_LOG" >&2
  exit 1
fi

"$NODE_BIN" \
  "$ROOT_DIR/scripts/capture_web_demo.mjs" \
  "http://localhost:$PORT/" \
  "$FRAME_DIR"

"$ROOT_DIR/scripts/render_demo_video.sh" \
  "$OUTPUT" "$NARRATION" "1280x720" \
  "$FRAME_DIR/01-overview.png" \
  "$FRAME_DIR/02-result.png" \
  "$FRAME_DIR/03-method.png"
