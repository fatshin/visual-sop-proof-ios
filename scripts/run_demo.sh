#!/bin/zsh
set -euo pipefail

ROOT_DIR=${0:A:h:h}
RUNTIME_DIR="$ROOT_DIR/.runtime"
DERIVED_DATA="$ROOT_DIR/DerivedData"
DEVICE_NAME="${VISUAL_SOP_SIMULATOR:-iPhone 17 Pro}"
MODE="${1:-sample}"

if [[ "$MODE" != "sample" && "$MODE" != "live" ]]; then
  print -u2 "Usage: ./scripts/run_demo.sh [sample|live]"
  exit 1
fi

mkdir -p "$RUNTIME_DIR"
TOKEN=""

cleanup() {
  if [[ -f "$RUNTIME_DIR/proxy.pid" ]]; then
    kill "$(cat "$RUNTIME_DIR/proxy.pid")" 2>/dev/null || true
    rm -f "$RUNTIME_DIR/proxy.pid"
  fi
  rm -f "$RUNTIME_DIR/proxy-token"
}
trap cleanup EXIT INT TERM

if [[ "$MODE" == "live" ]]; then
  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    print -u2 "OPENAI_API_KEY is required for Live GPT-5.6 mode."
    exit 1
  fi
  TOKEN=$(openssl rand -hex 24)
  umask 077
  print -r -- "$TOKEN" > "$RUNTIME_DIR/proxy-token"
  VISUAL_SOP_PROXY_TOKEN="$TOKEN" python3 "$ROOT_DIR/backend/server.py" > "$RUNTIME_DIR/proxy.log" 2>&1 &
  print $! > "$RUNTIME_DIR/proxy.pid"

  PROXY_READY=false
  for _ in {1..30}; do
    if curl --silent --fail \
      -H "Authorization: Bearer $TOKEN" \
      "http://127.0.0.1:8787/health" >/dev/null; then
      PROXY_READY=true
      break
    fi
    sleep 0.2
  done
  if [[ "$PROXY_READY" != "true" ]]; then
    print -u2 "The local proxy did not become ready. See .runtime/proxy.log."
    exit 1
  fi
fi

xcodegen generate --spec "$ROOT_DIR/project.yml" --project "$ROOT_DIR"
xcrun simctl boot "$DEVICE_NAME" 2>/dev/null || true
open -a Simulator
xcodebuild \
  -project "$ROOT_DIR/VisualSOPProof.xcodeproj" \
  -scheme VisualSOPProof \
  -sdk iphonesimulator \
  -destination "platform=iOS Simulator,name=$DEVICE_NAME" \
  -derivedDataPath "$DERIVED_DATA" \
  build

APP_PATH="$DERIVED_DATA/Build/Products/Debug-iphonesimulator/VisualSOPProof.app"
xcrun simctl install booted "$APP_PATH"
if [[ "$MODE" == "live" ]]; then
  SIMCTL_CHILD_VISUAL_SOP_PROXY_TOKEN="$TOKEN" \
    xcrun simctl launch --terminate-running-process booted com.visualsopproof.app
else
  xcrun simctl launch --terminate-running-process booted com.visualsopproof.app
fi

print "Visual SOP Proof launched in $MODE mode."
if [[ "$MODE" == "live" ]]; then
  print "The proxy remains active while this script runs. Press Control-C to stop it."
  wait "$(cat "$RUNTIME_DIR/proxy.pid")"
fi
