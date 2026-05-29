#!/usr/bin/env bash
# Smoke Test — PhD Thesis Butler v3.0
# Run: bash scripts/smoke_test.sh
# Exit code 0 = pass, 1+ = fail

set -e
BASE="/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler"
FAIL=0

echo "========================================"
echo "PhD Thesis Butler — Smoke Test v3.0"
echo "========================================"

# T1: Check zero overlap between layers
echo ""
echo "[T1] Checking layer overlap..."
for pair in "global,cluster/TECH_LIFE" "global,cluster/HUM_SOC" "global,cluster/ART_SPORT"; do
    IFS=',' read -r a b <<< "$pair"
    overlap=$(python3 -c "
import json
a_templates = set()
with open('$BASE/assets/$a/master/MASTER.jsonl') as f:
    for line in f:
        e = json.loads(line)
        a_templates.add(e.get('template','')[:100])
b_count = 0
with open('$BASE/assets/$b/master/MASTER.jsonl') as f:
    for line in f:
        e = json.loads(line)
        if e.get('template','')[:100] in a_templates:
            b_count += 1
print(b_count)
")
    if [ "$overlap" = "0" ]; then
        echo "  ✅ $a vs $b: 0 overlap"
    else
        echo "  ❌ $a vs $b: $overlap overlaps!"
        FAIL=$((FAIL+1))
    fi
done

# T2: Check placeholders (only [...], no ___)
echo ""
echo "[T2] Checking placeholders..."
for layer in global/master/MASTER.jsonl cluster/TECH_LIFE/master/MASTER.jsonl; do
    f="$BASE/assets/$layer"
    if [ ! -f "$f" ] || [ ! -s "$f" ]; then
        echo "  ⚠️  $layer: empty or missing, skipping"
        continue
    fi
    count=$(grep -c '___' "$f" 2>/dev/null || echo 0)
    count=${count%%$'\n'*}
    if [ "$count" = "0" ]; then
        echo "  ✅ $layer: no ___ placeholders"
    else
        echo "  ❌ $layer: $count ___ placeholders!"
        FAIL=$((FAIL+1))
    fi
done

# T3: Check Router outputs all required fields
echo ""
echo "[T3] Checking Router output contract..."
python3 -c "
import json, sys
sys.path.insert(0, '$BASE/agents/router')
from router_agent import infer
result = infer('Тестовая строка для проверки роутера.')
required = ['version','inference','retrieval','polish']
inf_keys = ['cluster','cluster_name','cluster_confidence','discipline','discipline_confidence','category','subtype','scene_confidence']
pol_keys = ['level','hit_layer','hit_quality','hit_count']
all_ok = True
for k in required:
    if k not in result: print(f'Missing: {k}'); all_ok=False
for k in inf_keys:
    if k not in result.get('inference',{}): print(f'Missing inference.{k}'); all_ok=False
for k in pol_keys:
    if k not in result.get('polish',{}): print(f'Missing polish.{k}'); all_ok=False
if all_ok:
    print('✅ All router fields present')
else:
    print('❌ Router contract broken')
    sys.exit(1)
" && echo "  ✅ Router contract valid" || { echo "  ❌ Router contract FAILED"; FAIL=$((FAIL+1)); }

# T4: Check layers exist
echo ""
echo "[T4] Checking all cluster directories..."
for c in TECH_LIFE HUM_SOC ART_SPORT; do
    d="$BASE/assets/cluster/$c"
    if [ -d "$d" ]; then
        echo "  ✅ CLUSTER($c): exists"
    else
        echo "  ❌ CLUSTER($c): missing!"
        FAIL=$((FAIL+1))
    fi
done

# T5: Check GLOBAL has content
echo ""
echo "[T5] Checking GLOBAL layer..."
gl_count=$(wc -l < "$BASE/assets/global/master/MASTER.jsonl" 2>/dev/null || echo 0)
if [ "$gl_count" -gt 0 ]; then
    echo "  ✅ GLOBAL: $gl_count entries"
else
    echo "  ❌ GLOBAL: empty!"
    FAIL=$((FAIL+1))
fi

# Summary
echo ""
echo "========================================"
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ $FAIL TEST(S) FAILED"
    exit 1
fi
