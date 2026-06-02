#!/usr/bin/env python3
"""
build_corpus_inventory.py — Scan assets/discipline/*.jsonl and produce .phd_build/inventory.json.

For each of 34 discipline files:
  - Count total templates
  - Count per category
  - Count per quality score (Q2=2, Q1=1, Q0=0)

Output: .phd_build/inventory.json
Reports discrepancies vs BUILD_INFO.json expected counts.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
DISCIPLINE_DIR = BASE / "assets" / "discipline"
BUILD_DIR = BASE / ".phd_build"
OUTPUT_PATH = BUILD_DIR / "inventory.json"
BUILD_INFO_PATH = BASE / "BUILD_INFO.json"

QUALITY_MAP = {2: "Q2", 1: "Q1", 0: "Q0"}


def scan_discipline_file(filepath: Path) -> dict:
    """Scan a single JSONL file and return counts."""
    total = 0
    by_category = defaultdict(int)
    by_quality = {"Q2": 0, "Q1": 0, "Q0": 0}

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1

            cat = entry.get("category", "UNKNOWN")
            by_category[cat] += 1

            qs = entry.get("quality_score")
            if qs is not None:
                q_label = QUALITY_MAP.get(qs)
                if q_label:
                    by_quality[q_label] += 1

    return {
        "total": total,
        "by_category": dict(sorted(by_category.items())),
        "by_quality": by_quality,
    }


def load_build_info() -> dict | None:
    """Load BUILD_INFO.json for expected counts."""
    if not BUILD_INFO_PATH.exists():
        return None
    with open(BUILD_INFO_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    if not DISCIPLINE_DIR.is_dir():
        print(f"ERROR: {DISCIPLINE_DIR} not found")
        sys.exit(1)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    jsonl_files = sorted(DISCIPLINE_DIR.glob("*.jsonl"))
    if not jsonl_files:
        print("ERROR: No .jsonl files found in assets/discipline/")
        sys.exit(1)

    print(f"Scanning {len(jsonl_files)} discipline files...")

    disciplines = {}
    total_templates = 0
    global_by_category = defaultdict(int)
    global_by_quality = {"Q2": 0, "Q1": 0, "Q0": 0}

    for filepath in jsonl_files:
        name = filepath.stem
        stats = scan_discipline_file(filepath)
        disciplines[name] = stats
        total_templates += stats["total"]

        for cat, count in stats["by_category"].items():
            global_by_category[cat] += count
        for q in ("Q2", "Q1", "Q0"):
            global_by_quality[q] += stats["by_quality"][q]

        print(f"  {name}: {stats['total']} templates, "
              f"{len(stats['by_category'])} categories")

    inventory = {
        "total_templates": total_templates,
        "disciplines": disciplines,
    }

    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)
    print(f"\nWritten: {OUTPUT_PATH}")
    print(f"Total templates: {total_templates}")

    # Compare with BUILD_INFO
    build_info = load_build_info()
    if build_info:
        expected_total = build_info.get("templates", {}).get("total")
        print(f"\n--- BUILD_INFO comparison ---")
        if expected_total is not None:
            diff = total_templates - expected_total
            if diff == 0:
                print(f"  total_templates: {total_templates} == expected {expected_total}  OK")
            else:
                print(f"  total_templates: {total_templates} vs expected {expected_total}  "
                      f"DISCREPANCY ({diff:+d})")

        expected_quality = build_info.get("quality", {})
        for q in ("Q2", "Q1", "Q0"):
            exp = expected_quality.get(q)
            if exp is not None:
                actual = global_by_quality[q]
                d = actual - exp
                if d == 0:
                    print(f"  {q}: {actual} == expected {exp}  OK")
                else:
                    print(f"  {q}: {actual} vs expected {exp}  DISCREPANCY ({d:+d})")

        expected_disciplines = build_info.get("layers", {}).get("DISCIPLINE_subjects")
        if expected_disciplines is not None:
            actual_count = len(disciplines)
            if actual_count == expected_disciplines:
                print(f"  disciplines: {actual_count} == expected {expected_disciplines}  OK")
            else:
                print(f"  disciplines: {actual_count} vs expected {expected_disciplines}  "
                      f"DISCREPANCY")
    else:
        print("\nWARNING: BUILD_INFO.json not found — no comparison done.")

    # Summary
    print(f"\nCategory summary:")
    for cat in sorted(global_by_category.keys()):
        print(f"  {cat}: {global_by_category[cat]}")

    print(f"\nQuality summary:")
    for q in ("Q2", "Q1", "Q0"):
        print(f"  {q}: {global_by_quality[q]}")


if __name__ == "__main__":
    main()
