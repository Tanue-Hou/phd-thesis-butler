#!/usr/bin/env python3
"""
validate_corpus_layer.py — Validate corpus_layer/ integrity.

Checks:
  1. All schemas in corpus_layer/schemas/ parse as valid JSON
  2. corpus_layer/WORKFLOW.md exists and has content
  3. .phd_build/ directory exists (warn if not, don't fail)
  4. evidence_count format in any JSONL files

Exit 0 if all checks pass, exit 1 with specific errors.
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CORPUS_LAYER = BASE / "corpus_layer"
SCHEMAS_DIR = CORPUS_LAYER / "schemas"
WORKFLOW_PATH = CORPUS_LAYER / "WORKFLOW.md"
BUILD_DIR = BASE / ".phd_build"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str):
    errors.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"  WARN: {msg}")


def ok(msg: str):
    print(f"  OK:   {msg}")


def check_schemas():
    """Check that all schema files parse as valid JSON."""
    print("\n[1/4] Schema JSON validity")
    if not SCHEMAS_DIR.is_dir():
        err(f"Schema directory not found: {SCHEMAS_DIR}")
        return

    schema_files = sorted(SCHEMAS_DIR.glob("*.schema.json"))
    if not schema_files:
        err("No .schema.json files found in corpus_layer/schemas/")
        return

    for sf in schema_files:
        try:
            with open(sf, encoding="utf-8") as f:
                data = json.load(f)
            # Verify it's a dict (not a bare value)
            if not isinstance(data, dict):
                err(f"{sf.name}: parsed but not a JSON object")
            else:
                ok(f"{sf.name}")
        except json.JSONDecodeError as e:
            err(f"{sf.name}: JSON parse error: {e}")
        except Exception as e:
            err(f"{sf.name}: read error: {e}")


def check_workflow():
    """Check that WORKFLOW.md exists and has content."""
    print("\n[2/4] WORKFLOW.md existence and content")
    if not WORKFLOW_PATH.exists():
        err(f"WORKFLOW.md not found at {WORKFLOW_PATH}")
        return

    try:
        content = WORKFLOW_PATH.read_text(encoding="utf-8").strip()
        if len(content) < 50:
            err(f"WORKFLOW.md has only {len(content)} chars — suspiciously short")
        else:
            ok(f"WORKFLOW.md exists ({len(content)} chars)")
    except Exception as e:
        err(f"WORKFLOW.md read error: {e}")


def check_build_dir():
    """Check that .phd_build/ directory exists."""
    print("\n[3/4] .phd_build/ directory")
    if BUILD_DIR.is_dir():
        files = list(BUILD_DIR.iterdir())
        ok(f".phd_build/ exists ({len(files)} files)")
    else:
        warn(".phd_build/ directory not found — run build_corpus_inventory.py first")


def check_evidence_count_format():
    """Check evidence_count format in JSONL files if present."""
    print("\n[4/4] evidence_count format in JSONL files")
    # Check structure_records.jsonl if it exists
    struct_file = BUILD_DIR / "structure_records.jsonl"
    if not struct_file.exists():
        warn("structure_records.jsonl not found — skipping evidence_count check")
        return

    valid_confidences = {"high", "medium", "low", "pending"}
    checked = 0
    bad = 0

    with open(struct_file, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                err(f"structure_records.jsonl:{line_num}: JSON parse error")
                continue

            ec = record.get("evidence_count")
            if ec is None:
                err(f"structure_records.jsonl:{line_num}: missing evidence_count")
                bad += 1
                continue

            if not isinstance(ec, dict):
                err(f"structure_records.jsonl:{line_num}: evidence_count is not a dict")
                bad += 1
                continue

            # Check required fields
            if "count" not in ec:
                err(f"structure_records.jsonl:{line_num}: evidence_count missing 'count'")
                bad += 1
            elif not isinstance(ec["count"], int) or ec["count"] < 0:
                err(f"structure_records.jsonl:{line_num}: "
                    f"evidence_count.count must be non-negative int, got {ec['count']}")
                bad += 1

            if "source" not in ec:
                err(f"structure_records.jsonl:{line_num}: evidence_count missing 'source'")
                bad += 1

            if "confidence" not in ec:
                err(f"structure_records.jsonl:{line_num}: "
                    f"evidence_count missing 'confidence'")
                bad += 1
            elif ec["confidence"] not in valid_confidences:
                err(f"structure_records.jsonl:{line_num}: "
                    f"evidence_count.confidence={ec['confidence']!r} "
                    f"not in {valid_confidences}")
                bad += 1

            checked += 1

    if checked > 0:
        ok(f"Checked {checked} records, {bad} with issues")
    else:
        warn("No records found in structure_records.jsonl")


def main():
    print("=" * 60)
    print(f"Corpus Layer Validation  |  {BASE.name}")
    print("=" * 60)

    check_schemas()
    check_workflow()
    check_build_dir()
    check_evidence_count_format()

    print(f"\n{'=' * 60}")
    print(f"Results: {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        print(f"\nFAILED — errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
