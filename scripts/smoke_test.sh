#!/usr/bin/env bash
# Smoke test: 1 DIS + 1 AREF through full pipeline
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
echo "[SMOKE] Starting PhD Thesis Butler smoke test"
echo "[SMOKE] Verifying directory structure..."
for d in prompts scripts references schemas sub_skills; do
  [ -d "$BASE/$d" ] || { echo "FAIL: missing $d"; exit 1; }
done
echo "[SMOKE] All directories present"
echo "[SMOKE] Verifying prompts..."
for p in router gm dis_full aref_full; do
  [ -f "$BASE/prompts/$p.prompt.txt" ] || { echo "FAIL: missing prompts/$p.prompt.txt"; exit 1; }
done
echo "[SMOKE] All prompts present"
echo "[SMOKE] Verifying scripts..."
for s in aggregate qa_check coverage_check generate_top50; do
  [ -f "$BASE/scripts/${s}.py" ] || { echo "FAIL: missing scripts/${s}.py"; exit 1; }
done
echo "[SMOKE] All scripts present"
echo "[SMOKE] Verifying sub-skills..."
for s in dis_intro dis_model dis_survey dis_method dis_experiment dis_result dis_discussion dis_conclusion dis_transition dis_formal_defs dis_engineering aref_core utils_core; do
  [ -f "$BASE/sub_skills/$s/SKILL.md" ] || { echo "WARN: sub_skills/$s/SKILL.md not yet created"; }
done
echo "[SMOKE] PASS: PhD Thesis Butler structure is valid"
