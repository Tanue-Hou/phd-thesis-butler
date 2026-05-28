#!/usr/bin/env bash
# Retry handler: manage retry count and dead letter queue
# Usage: retry_handler.sh --paper-id 001 --file-type DIS --reason "slot rate < 98%"
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
PAPER_ID=""
FILE_TYPE=""
REASON=""
RETRY_LOG="$BASE/data/retry_log.jsonl"
DEAD_LETTER="$BASE/data/dead_letter.jsonl"
while [[ $# -gt 0 ]]; do
  case $1 in --paper-id) PAPER_ID="$2";; --file-type) FILE_TYPE="$2";; --reason) REASON="$2";; esac; shift
done
echo "{\"paper_id\":\"$PAPER_ID\",\"file_type\":\"$FILE_TYPE\",\"reason\":\"$REASON\",\"timestamp\":$(date +%s)}" >> "$RETRY_LOG"
echo "[RETRY] Logged retry for $PAPER_ID/$FILE_TYPE"
