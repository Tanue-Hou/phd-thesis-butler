#!/usr/bin/env python3
"""
validate_planning_assets.py — Validate planning_layer/ structure and completeness.
"""

import json
import sys
import os
import re
from pathlib import Path

PLANNING_DIR = Path(__file__).resolve().parent.parent / "planning_layer"

REQUIRED = {
    "guides": [
        "THESIS_PLANNER.md", "METHODOLOGY_GUIDE.md",
        "LOGIC_FLOW_GUIDE.md", "EXPERIMENT_DESIGN_GUIDE.md",
    ],
    "clusters": [
        "clusters/ENGINEERING_CONTROL.md", "clusters/COMPUTER_AI.md",
        "clusters/NATURAL_SCIENCE.md", "clusters/LIFE_MEDICAL.md",
        "clusters/SOCIAL_ECON_MANAGEMENT.md", "clusters/HUMANITIES_ARTS.md",
    ],
    "patterns": [
        "patterns/STRUCTURE_PATTERNS.json",
        "patterns/engineering_model_method_experiment.json",
        "patterns/ai_method_dataset_ablation.json",
        "patterns/empirical_social_science.json",
        "patterns/life_science_imrad.json",
        "patterns/humanities_argumentative_analysis.json",
    ],
    "templates": [
        "templates/chapter_plan_template.md",
        "templates/experiment_plan_template.md",
        "templates/thesis_outline_template.md",
        "templates/supervisor_report_template.md",
    ],
    "schemas": [
        "schemas/chapter_plan.schema.json",
        "schemas/experiment_plan.schema.json",
    ],
}

ALL_FILES = []
for group in REQUIRED.values():
    ALL_FILES.extend(group)


def check_existence():
    errors = []
    for rel_path in ALL_FILES:
        if not (PLANNING_DIR / rel_path).exists():
            errors.append(f"  ❌ MISSING: {rel_path}")
    return errors


def check_json_parse():
    errors = []
    for rel_path in REQUIRED["patterns"] + REQUIRED["schemas"]:
        full = PLANNING_DIR / rel_path
        if not full.exists():
            continue
        try:
            with open(full) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"  ❌ JSON PARSE ERROR: {rel_path}: {e}")
    return errors


def check_markdown_nonempty():
    errors = []
    for rel_path in ALL_FILES:
        if not rel_path.endswith(".md"):
            continue
        full = PLANNING_DIR / rel_path
        if not full.exists():
            continue
        with open(full) as f:
            body = re.sub(r"^---\n.*?\n---\n", "", f.read(), count=1, flags=re.DOTALL)
        if len(body.strip()) < 50:
            errors.append(f"  ❌ TOO SHORT ({len(body.strip())} chars): {rel_path}")
    return errors


def check_schemas():
    errors = []
    for rel_path in REQUIRED["schemas"]:
        full = PLANNING_DIR / rel_path
        if not full.exists():
            continue
        with open(full) as f:
            schema = json.load(f)
        if "type" not in schema:
            errors.append(f"  ⚠️  No type field: {rel_path}")
        if "properties" not in schema:
            errors.append(f"  ⚠️  No properties field: {rel_path}")
    return errors


def check_patterns():
    full = PLANNING_DIR / "patterns/STRUCTURE_PATTERNS.json"
    if not full.exists():
        return ["  ❌ STRUCTURE_PATTERNS.json not found"]
    with open(full) as f:
        data = json.load(f)
    errors = []
    if isinstance(data, dict) and "zones" in data:
        required_kw = {"empirical", "heuristic", "limitations"}
        found = set()
        for key in data.get("zones", {}):
            for kw in required_kw:
                if kw in key.lower():
                    found.add(kw)
        missing = required_kw - found
        if missing:
            errors.append(f"  ⚠️  Missing zone keywords: {missing}")
    return errors


def main():
    print("=" * 60)
    print(f"Planning Layer Validation: {PLANNING_DIR}")
    print("=" * 60)

    if not PLANNING_DIR.exists():
        print(f"\n❌ Planning directory does not exist")
        sys.exit(1)

    all_errors = []
    for name, fn in [("File existence", check_existence),
                     ("JSON parse", check_json_parse),
                     ("Markdown content", check_markdown_nonempty),
                     ("Schema validity", check_schemas),
                     ("Pattern zones", check_patterns)]:
        print(f"\n📁 {name}...")
        e = fn()
        all_errors.extend(e)
        if not e:
            print("   ✅ OK")
        else:
            for err in e:
                print(err)

    present = sum(1 for f in ALL_FILES if (PLANNING_DIR / f).exists())
    print(f"\n{'=' * 60}")
    print(f"📊 {present}/{len(ALL_FILES)} files present, {len(ALL_FILES) - len(all_errors)}/{len(ALL_FILES)} checks passed")
    if all_errors:
        print(f"\n❌ FAILED — {len(all_errors)} issue(s)")
        sys.exit(1)
    else:
        print("\n✅ ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
