#!/usr/bin/env python3
"""
G3 Merge — 归并 DIS + AREF 原始抽取结果
合并所有 raw JSONL → 按 category 归组 → 去重 → 输出 master JSONL
Gate: 每 category ≥3 条
"""
import json, sys, re
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
RAW = BASE / "data/raw"
OUT = BASE / "data/merged"
OUT.mkdir(parents=True, exist_ok=True)

def load_jsonl(filepath):
    """Load JSONL file, return list of entries"""
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def deduplicate_templates(entries):
    """Remove duplicate templates (same template text)"""
    seen = set()
    unique = []
    for e in entries:
        tmpl = e.get("template", "").strip()
        if tmpl and tmpl not in seen:
            seen.add(tmpl)
            unique.append(e)
    return unique

def quality_report(entries, name):
    """Generate quality stats for a group"""
    total = len(entries)
    if total == 0:
        return {"name": name, "total": 0, "Q2": 0, "Q1": 0, "Q0": 0}
    
    q_scores = [e.get("quality_score", 0) for e in entries]
    q2 = sum(1 for q in q_scores if q == 2)
    q1 = sum(1 for q in q_scores if q == 1)
    q0 = sum(1 for q in q_scores if q == 0)
    
    return {
        "name": name,
        "total": total,
        "Q2": q2,
        "Q2%": round(q2/total*100, 1),
        "Q1": q1,
        "Q1%": round(q1/total*100, 1),
        "Q0": q0,
        "Q0%": round(q0/total*100, 1),
    }

print("=" * 60)
print("G3 MERGE — 归并 DIS + AREF")
print("=" * 60)

# 1) Load all raw data
all_entries = []
source_counts = defaultdict(int)

# DIS MSU
for f in sorted((RAW / "MSU").iterdir()):
    entries = load_jsonl(f)
    all_entries.extend(entries)
    source_counts["DIS_MSU"] += len(entries)

# DIS SPbSU
for f in sorted((RAW / "SPbSU").iterdir()):
    entries = load_jsonl(f)
    all_entries.extend(entries)
    source_counts["DIS_SPbSU"] += len(entries)

# AREF
aref_dir = RAW / "AREF" / "MSU"
if aref_dir.exists():
    for f in sorted(aref_dir.iterdir()):
        entries = load_jsonl(f)
        all_entries.extend(entries)
        source_counts["AREF"] += len(entries)

print(f"\nSource breakdown:")
for src, count in sorted(source_counts.items()):
    print(f"  {src}: {count} entries")
print(f"  TOTAL: {len(all_entries)} entries")

# 2) Deduplicate
print(f"\nDeduplicating...")
unique_entries = deduplicate_templates(all_entries)
print(f"  Before: {len(all_entries)} → After: {len(unique_entries)} ({len(all_entries)-len(unique_entries)} duplicates removed)")

# 3) Write master merged file
master_file = OUT / "MASTER_MERGED.jsonl"
with open(master_file, 'w') as f:
    for entry in unique_entries:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print(f"\nMaster merged: {master_file} ({len(unique_entries)} entries)")

# 4) Group by category
by_category = defaultdict(list)
for e in unique_entries:
    cat = e.get("category", "UNCATEGORIZED")
    by_category[cat].append(e)

print(f"\n=== Category Breakdown ===")
cat_stats = []
for cat in sorted(by_category.keys()):
    entries = by_category[cat]
    unique_deduped = deduplicate_templates(entries)
    r = quality_report(unique_deduped, cat)
    cat_stats.append(r)
    flag = " ✅" if r["total"] >= 3 else " ❌ GATE FAIL"
    print(f"  {cat:<30} {r['total']:>5} entries | Q2={r['Q2%']}% | Q0={r['Q0%']}%{flag}")

# 5) Write per-category files
cat_dir = OUT / "by_category"
cat_dir.mkdir(exist_ok=True)
for cat in by_category:
    entries = deduplicate_templates(by_category[cat])
    with open(cat_dir / f"{cat}.jsonl", 'w') as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')

# 6) G3 Gate Check
print(f"\n=== G3 GATE ===")
g3_pass = True
for r in cat_stats:
    if r["total"] < 3:
        print(f"  ❌ {r['name']}: only {r['total']} entries (< 3)")
        g3_pass = False
if g3_pass:
    print(f"  ✅ ALL categories ≥ 3 entries — G3 PASS")
else:
    print(f"  ❌ Some categories below threshold — G3 FAIL")

# 7) Write report
report = {
    "phase": "G3 Merge",
    "source_counts": dict(source_counts),
    "total_raw": len(all_entries),
    "total_unique": len(unique_entries),
    "dedup_removed": len(all_entries) - len(unique_entries),
    "categories": {r["name"]: {"total": r["total"], "Q2%": r["Q2%"], "Q0%": r["Q0%"]} for r in cat_stats},
    "g3_pass": g3_pass,
}

with open(OUT / "G3_REPORT.json", 'w') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nReport: {OUT / 'G3_REPORT.json'}")
print(f"\nG3 COMPLETE — {len(unique_entries)} unique entries in {len(by_category)} categories")
