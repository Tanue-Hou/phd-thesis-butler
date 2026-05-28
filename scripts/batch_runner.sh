#!/usr/bin/env bash
# Batch runner: process a batch of papers through extract → QA → aggregate
# Usage: batch_runner.sh --input batch.json --output /out/batch_001
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
INPUT=""
OUTPUT=""
while [[ $# -gt 0 ]]; do
  case $1 in --input) INPUT="$2"; shift;; --output) OUTPUT="$2"; shift;; *) echo "Unknown: $1"; exit 1;; esac; shift
done
[ -n "$INPUT" ] || { echo "ERROR: --input required"; exit 1; }
[ -n "$OUTPUT" ] || { echo "ERROR: --output required"; exit 1; }
mkdir -p "$OUTPUT"
echo "[BATCH] Starting batch from $INPUT → $OUTPUT"
echo "[BATCH] Run DIS and AREF extraction for each paper..."
# Placeholder: here you would iterate over papers and run router/gm prompts
echo "[BATCH] Batch complete. Output in $OUTPUT"
