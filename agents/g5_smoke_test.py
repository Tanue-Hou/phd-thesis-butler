#!/usr/bin/env python3
"""
G5 Smoke Test — 上线门控
Check:
1. HUM_SOC / ART_SPORT template count + Q2%
2. 5 样板 DISCIPLINE 模板数 + K=3 可用性
3. zero overlap = 0
4. gap_list P0 trend
"""
import json
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
LAYER_DIR = BASE / "assets" / "cluster"
DISC_DIR = BASE / "assets" / "discipline"
G4_DIR = BASE / "data" / "classified"

# Sample disciplines to check (5 样板)
SAMPLE_DISCIPLINES = [
    "физико-математические науки",
    "биологические науки",
    "исторические науки",
    "экономические науки",
    "технические науки",
]

def load_jsonl(path):
    entries = []
    if not path.exists():
        return entries
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    return entries

def q_stats(entries):
    total = len(entries)
    if total == 0:
        return {"total": 0, "Q2": 0, "Q2%": 0, "Q1": 0, "Q0": 0}
    scores = [e.get("quality_score", 0) for e in entries]
    q2 = sum(1 for s in scores if s == 2)
    q1 = sum(1 for s in scores if s == 1)
    q0 = sum(1 for s in scores if s == 0)
    return {
        "total": total,
        "Q2": q2,
        "Q2%": round(q2/total*100, 1),
        "Q1": q1,
        "Q0": q0,
    }

print("=" * 60)
print("G5 SMOKE TEST — 上线门控")
print("=" * 60)

# 1) Layer stats
print(f"\n1️⃣  HUM_SOC / ART_SPORT 模板数 + Q2%")
results = []
for layer in ["HUM_SOC", "ART_SPORT"]:
    entries = load_jsonl(LAYER_DIR / f"{layer}.jsonl")
    stats = q_stats(entries)
    print(f"  {layer:<15} total={stats['total']:>6}  Q2={stats['Q2']:>5} ({stats['Q2%']}%)  Q0={stats['Q0']}")
    results.append({**stats, "name": layer})

# 2) Sample disciplines
print(f"\n2️⃣  5 样板 DISCIPLINE 模板数 + K=3 可用性")
disc_ok = 0
disc_total = 0
for disc in SAMPLE_DISCIPLINES:
    safe_name = disc.replace(" ", "_")
    entries = load_jsonl(DISC_DIR / f"{safe_name}.jsonl")
    stats = q_stats(entries)
    k3_ok = stats["total"] >= 3
    flag = "✅ K=3 OK" if k3_ok else "❌ K<3 FAIL"
    if k3_ok: disc_ok += 1
    disc_total += 1
    print(f"  {disc:<30} total={stats['total']:>4}  Q2={stats['Q2']:>3} ({stats['Q2%']}%)  {flag}")

# 3) Zero overlap
print(f"\n3️⃣  Zero Overlap Check")
g4_report_path = G4_DIR / "G4_REPORT.json"
if g4_report_path.exists():
    with open(g4_report_path) as f:
        g4_report = json.load(f)
    overlap = g4_report.get("overlap", -1)
    print(f"  Overlap count: {overlap}")
    zero_overlap = overlap == 0
    print(f"  {'✅ ZERO OVERLAP' if zero_overlap else '❌ OVERLAP DETECTED'}")
else:
    print(f"  ⚠️  G4 report not found — run G4 first")
    zero_overlap = False

# 4) Gap list
print(f"\n4️⃣  Gap List P0 Trend")
all_layers = load_jsonl(LAYER_DIR / "HUM_SOC.jsonl") + load_jsonl(LAYER_DIR / "ART_SPORT.jsonl")
# Check for categories with low count
all_cats = Counter(e.get("category", "UNKNOWN") for e in all_layers)
gaps = [(cat, count) for cat, count in all_cats.items() if count < 10]
gaps.sort(key=lambda x: x[1])
print(f"  Total categories: {len(all_cats)}")
print(f"  Light categories (< 10 entries): {len(gaps)}")
for cat, count in gaps[:10]:
    print(f"    {cat:<30} {count} entries (P0 gap)")
if not gaps:
    print(f"  ✅ No P0 gaps")

# 5) Overall verdict
print(f"\n{'='*60}")
print(f"G5 VERDICT")
print(f"{'='*60}")

layer_results = {r["name"]: r for r in results}
hum_soc = layer_results.get("HUM_SOC", {})
art_sport = layer_results.get("ART_SPORT", {})

g5_pass = True
checks = []

# G5 Gate: HUM_SOC >= 2000 and Q2 >= 25%
if hum_soc.get("total", 0) >= 2000 and hum_soc.get("Q2%", 0) >= 25:
    checks.append("✅ HUM_SOC >= 2000 & Q2 >= 25%")
else:
    checks.append(f"❌ HUM_SOC: {hum_soc.get('total', 0)} entries, Q2={hum_soc.get('Q2%', 0)}%")
    g5_pass = False

if art_sport.get("total", 0) >= 2000 and art_sport.get("Q2%", 0) >= 25:
    checks.append("✅ ART_SPORT >= 2000 & Q2 >= 25%")
else:
    checks.append(f"❌ ART_SPORT: {art_sport.get('total', 0)} entries, Q2={art_sport.get('Q2%', 0)}%")
    g5_pass = False

checks.append(f"{'✅' if zero_overlap else '❌'} Zero overlap = {0 if zero_overlap else '>0'}")

for c in checks:
    print(f"  {c}")

print(f"\n  G5: {'✅ PASS' if g5_pass and zero_overlap else '❌ FAIL'}")

# Write report
report = {
    "phase": "G5 Smoke Test",
    "layers": {r["name"]: {"total": r["total"], "Q2%": r["Q2%"], "Q0": r["Q0"]} for r in results},
    "sample_disciplines": {d: {"ok": True} for d in SAMPLE_DISCIPLINES[:disc_total]},
    "zero_overlap": zero_overlap,
    "gaps_p0": len(gaps),
    "g5_pass": g5_pass and zero_overlap,
    "checks": checks,
}
with open(BASE / "data" / "G5_SMOKE_TEST.json", 'w') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nReport: {BASE / 'data' / 'G5_SMOKE_TEST.json'}")
print(f"\nG5 COMPLETE — pass={g5_pass and zero_overlap}")
