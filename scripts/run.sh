#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../site"
npm run dev
