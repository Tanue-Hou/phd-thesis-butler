#!/usr/bin/env bash
# Smoke Test — PhD Thesis Butler v5.1
# Run: bash scripts/smoke_test.sh
# Exit code: 0 = all pass, 1 = one or more failures, 2 = environment error

set -euo pipefail

# ── Auto-resolve BASE to repo root (parent of scripts/) ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"

FAIL=0
TOTAL=0

pass() { echo "  ✅ $1"; }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
run_test() { TOTAL=$((TOTAL+1)); echo ""; echo "[$1] $2"; }

# ── Read version from BUILD_INFO.json ──
if [ ! -f "$BASE/BUILD_INFO.json" ]; then
    echo "FATAL: BUILD_INFO.json not found at $BASE"; exit 2
fi
VERSION=$(python3 -c "import json; print(json.load(open('$BASE/BUILD_INFO.json'))['version'])")
echo "========================================"
echo "PhD Thesis Butler — Smoke Test"
echo "Version: $VERSION"
echo "Base:    $BASE"
echo "========================================"

# ─────────────────────────────────────────
# T1: retrieve_templates.py returns results
# ─────────────────────────────────────────
run_test "T1" "retrieve_templates.py — must return ≥1 result"
_t1_tmp=$(mktemp)
python3 "$BASE/scripts/retrieve_templates.py" \
    --category MODEL \
    --cluster TECH_LIFE \
    --query "модель метод эксперимент" \
    --limit 3 >"$_t1_tmp" 2>/dev/null || true
_t1_count=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        data = json.load(f)
    print(len(data))
except:
    print(0)
" "$_t1_tmp" 2>/dev/null || echo 0)
rm -f "$_t1_tmp"
if [ "$_t1_count" -gt 0 ]; then
    pass "retrieve_templates returned $_t1_count results"
else
    fail "retrieve_templates returned 0 results"
fi

# ─────────────────────────────────────────
# T2: planning_layer validator passes
# ─────────────────────────────────────────
run_test "T2" "Planning layer validator"
if python3 "$BASE/scripts/validate_planning_assets.py" >/dev/null 2>&1; then
    pass "validate_planning_assets passed"
else
    fail "validate_planning_assets failed (exit $?)"
fi

# ─────────────────────────────────────────
# T3: All discipline JSONs parse cleanly
# ─────────────────────────────────────────
run_test "T3" "Discipline JSON parse (assets/references/disciplines/)"
DISC_DIR="$BASE/assets/references/disciplines"
if [ ! -d "$DISC_DIR" ]; then
    fail "Discipline directory missing: $DISC_DIR"
else
    _disc_ok=0
    _disc_fail=0
    for f in "$DISC_DIR"/*.json; do
        [ -f "$f" ] || continue
        _name=$(basename "$f")
        if python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
            _disc_ok=$((_disc_ok+1))
        else
            echo "    ❌ Cannot parse: $_name"
            _disc_fail=$((_disc_fail+1))
        fi
    done
    if [ "$_disc_fail" -eq 0 ] && [ "$_disc_ok" -gt 0 ]; then
        pass "$_disc_ok discipline JSONs parsed OK"
    else
        fail "$_disc_fail / $((_disc_ok+_disc_fail)) discipline JSONs failed"
    fi
fi

# ─────────────────────────────────────────
# T4: Planning schemas are valid JSON + have required keys
# ─────────────────────────────────────────
run_test "T4" "Planning schema validation"
SCHEMA_DIR="$BASE/planning_layer/schemas"
if [ ! -d "$SCHEMA_DIR" ]; then
    fail "Schema directory missing: $SCHEMA_DIR"
else
    _schema_ok=0
    _schema_fail=0
    for f in "$SCHEMA_DIR"/*.schema.json; do
        [ -f "$f" ] || continue
        _name=$(basename "$f")
        _result=$(python3 -c "
import json, sys
with open('$f') as fh:
    s = json.load(fh)
missing = [k for k in ('type','properties') if k not in s]
if missing:
    print('MISSING:' + ','.join(missing))
    sys.exit(1)
print('OK')
" 2>&1) || true
        if [ "$_result" = "OK" ]; then
            _schema_ok=$((_schema_ok+1))
        else
            echo "    ❌ $_name: $_result"
            _schema_fail=$((_schema_fail+1))
        fi
    done
    if [ "$_schema_fail" -eq 0 ] && [ "$_schema_ok" -gt 0 ]; then
        pass "$_schema_ok schema(s) valid"
    else
        fail "$_schema_fail / $((_schema_ok+_schema_fail)) schema(s) failed"
    fi
fi

# ─────────────────────────────────────────
# T5: Version consistency (BUILD_INFO.json)
# ─────────────────────────────────────────
run_test "T5" "Version consistency check"
_ver_major=$(echo "$VERSION" | cut -d. -f1)
_ver_minor=$(echo "$VERSION" | cut -d. -f2)
if [ "$_ver_major" -ge 5 ] 2>/dev/null; then
    pass "VERSION=$VERSION (major=$_ver_major ≥ 5)"
else
    fail "VERSION=$VERSION — expected major ≥ 5"
fi

# ─────────────────────────────────────────
# T6: Cluster layer structure exists
# ─────────────────────────────────────────
run_test "T6" "Cluster layer directories"
_cl_ok=0
for c in TECH_LIFE HUM_SOC; do
    if [ -d "$BASE/assets/cluster/$c" ]; then
        _cl_ok=$((_cl_ok+1))
    else
        fail "Missing cluster: $c"
    fi
done
if [ "$_cl_ok" -eq 2 ]; then
    pass "TECH_LIFE, HUM_SOC present"
fi

# ─────────────────────────────────────────
# T7: GLOBAL MASTER.jsonl has content
# ─────────────────────────────────────────
run_test "T7" "GLOBAL MASTER.jsonl non-empty"
_gf="$BASE/assets/global/master/MASTER.jsonl"
if [ -f "$_gf" ] && [ -s "$_gf" ]; then
    _gc=$(wc -l < "$_gf")
    pass "GLOBAL MASTER.jsonl: $_gc lines"
else
    fail "GLOBAL MASTER.jsonl missing or empty"
fi

# ═════════════════════════════════════════
# Summary
# ═════════════════════════════════════════
echo ""
echo "========================================"
echo "Version: $VERSION"
echo "Tests run: $TOTAL"
echo "Passed:    $((TOTAL-FAIL))"
echo "Failed:    $FAIL"
echo "========================================"
if [ "$FAIL" -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ $FAIL TEST(S) FAILED"
    exit 1
fi
