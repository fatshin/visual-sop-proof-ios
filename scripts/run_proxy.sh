#!/bin/zsh
set -euo pipefail

ROOT_DIR=${0:A:h:h}
RUNTIME_DIR="$ROOT_DIR/.runtime"
mkdir -p "$RUNTIME_DIR"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  print -u2 "OPENAI_API_KEY is required for Live GPT-5.6 mode."
  exit 1
fi

TOKEN=$(openssl rand -hex 24)
umask 077
print -r -- "$TOKEN" > "$RUNTIME_DIR/proxy-token"

cleanup() {
  rm -f "$RUNTIME_DIR/proxy-token"
}
trap cleanup EXIT INT TERM

export VISUAL_SOP_PROXY_TOKEN="$TOKEN"
python3 "$ROOT_DIR/backend/server.py"
