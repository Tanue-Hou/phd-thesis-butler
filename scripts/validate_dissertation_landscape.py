#!/usr/bin/env python3
"""
validate_dissertation_landscape.py — v5.4.0 Dissertation Landscape Validator

Validates:
- Sample input files are valid JSON
- JSON landscape output has all required fields
- Markdown report has all 12 sections
- Every record has read_depth, source_access, structure_confidence
- No large verbatim text snippets
- No Zotero local attachment paths in public examples

Usage:
    python3 scripts/validate_dissertation_landscape.py
    python3 scripts/validate_dissertation_landscape.py --samples
    python3 scripts/validate_dissertation_landscape.py --output-json FILE --output-md FILE

By default, validate the existing .phd_build outputs. --samples builds and
validates the bundled examples in a temporary directory.

Pure standard library — no external dependencies.
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

LANDSCAPE_DIR = os.path.join(PROJECT_ROOT, "research_layer", "landscape")
EXAMPLES_DIR = os.path.join(LANDSCAPE_DIR, "examples")
BUILD_DIR = os.path.join(PROJECT_ROOT, ".phd_build")
ZOTERO_DIR = os.path.join(BUILD_DIR, "zotero")

SAMPLE_INPUT = os.path.join(EXAMPLES_DIR, "dissercat_landscape_input_sample.json")
BUILD_SCRIPT = os.path.join(SCRIPT_DIR, "build_dissertation_landscape.py")
IMPORT_SCRIPT = os.path.join(SCRIPT_DIR, "import_zotero_landscape_records.py")

# Output files from build_dissertation_landscape.py
LANDSCAPE_JSON_OUTPUT = os.path.join(BUILD_DIR, "landscape_output.json")
LANDSCAPE_MD_OUTPUT = os.path.join(BUILD_DIR, "landscape_report.md")

PASS = "\u2705"
FAIL = "\u274c"
WARN = "\u26a0\ufe0f"

results = []


def check(label, condition, detail=""):
    """Record a check result."""
    ok = bool(condition)
    symbol = PASS if ok else FAIL
    msg = f"  {symbol} {label}"
    if detail and not ok:
        msg += f"  ({detail})"
    print(msg)
    results.append(ok)
    return ok


def warn(label, detail=""):
    """Record a warning (does not affect pass/fail)."""
    msg = f"  {WARN} {label}"
    if detail:
        msg += f"  ({detail})"
    print(msg)


# ---------------------------------------------------------------------------
# Required fields for landscape output JSON
# ---------------------------------------------------------------------------

REQUIRED_LANDSCAPE_FIELDS = [
    "topic",
    "user_direction",
    "records_count",
    "source_summary",
    "read_depth_summary",
    "theme_clusters",
    "structure_patterns",
    "methodology_patterns",
    "validation_patterns",
    "positioning_gaps",
    "borrowable_moves",
    "risk_warnings",
    "recommended_outline",
    "planning_layer_routes",
    "evidence_layer_routes",
]

# Required fields for each record in the input
REQUIRED_RECORD_FIELDS = [
    "id",
    "source_name",
    "author",
    "year",
    "degree_type",
    "specialty_code",
]

RECORD_QUALITY_FIELDS = [
    "read_depth",
    "source_access",
    "structure_confidence",
]

# Valid enum values for read_depth and source_access
VALID_READ_DEPTH = {"metadata_only", "abstract_toc", "zotero_indexed_fulltext", "fulltext_local"}
VALID_SOURCE_ACCESS = {"public_page", "zotero_metadata", "zotero_indexed_fulltext", "user_provided_pdf", "manual"}
VALID_CONFIDENCE = {"high", "medium", "low"}


# The 12 required Markdown sections
MD_SECTIONS = [
    "1. Research Direction",
    "2. Source Coverage",
    "3. Comparable Dissertations",
    "4. Theme Clusters",
    "5. Chapter Structure Comparison",
    "6. Methodology Landscape",
    "7. Validation/Argumentation Patterns",
    "8. User Positioning",
    "9. Borrowable Writing Moves",
    "10. Risk Warnings",
    "11. Recommended Thesis Outline",
    "12. Next Actions",
]

# Patterns that indicate Zotero local attachment paths
ZOTERO_PATH_PATTERNS = [
    r"storage:[\\/]",
    r"C:\\Users\\",
    r"/home/[^/]+/Zotero",
    r"zotero/storage/",
    r"attachments/[A-Z0-9]{8}/",
]

VERBATIM_MAX_LENGTH = 500  # characters


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_json_file(path, label):
    """Validate that a file is valid JSON. Returns (data, ok)."""
    if not os.path.isfile(path):
        print(f"  {FAIL} {label}: file not found ({path})")
        results.append(False)
        return None, False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  {PASS} {label}: valid JSON")
        results.append(True)
        return data, True
    except json.JSONDecodeError as e:
        print(f"  {FAIL} {label}: invalid JSON — {e}")
        results.append(False)
        return None, False


def validate_sample_input():
    """Validate the sample input file."""
    print("\n--- Sample Input Validation ---")
    data, ok = validate_json_file(SAMPLE_INPUT, "dissercat_landscape_input_sample.json")
    if not ok or not isinstance(data, list):
        if data is not None:
            check("Input is a JSON array", False, f"got {type(data).__name__}")
        return []

    check("Input is a JSON array", True)

    for i, rec in enumerate(data):
        rec_id = rec.get("id", f"record_{i}")

        for field in REQUIRED_RECORD_FIELDS:
            check(f"  Record '{rec_id}' has '{field}'", field in rec,
                  f"missing field '{field}'")

        for field in RECORD_QUALITY_FIELDS:
            check(f"  Record '{rec_id}' has '{field}'", field in rec,
                  f"missing field '{field}'")

        # Check structure_confidence (accepts string or numeric)
        sc = rec.get("structure_confidence")
        if sc is not None:
            if isinstance(sc, str):
                ok = sc.lower().strip() in VALID_CONFIDENCE
                check(f"  Record '{rec_id}' structure_confidence in {VALID_CONFIDENCE}",
                      ok, f"got '{sc}'")
            elif isinstance(sc, (int, float)):
                ok = 0.0 <= float(sc) <= 1.0
                check(f"  Record '{rec_id}' structure_confidence in [0,1]",
                      ok, f"got {sc}")
        
        # Check read_depth enum
        rd = rec.get("read_depth")
        if rd is not None:
            check(f"  Record '{rec_id}' read_depth in VALID_READ_DEPTH",
                  rd in VALID_READ_DEPTH,
                  f"got '{rd}'")
        
        # Check source_access enum
        sa = rec.get("source_access")
        if sa is not None:
            check(f"  Record '{rec_id}' source_access in VALID_SOURCE_ACCESS",
                  sa in VALID_SOURCE_ACCESS,
                  f"got '{sa}'")

        # Check for large verbatim text
        abstract = rec.get("abstract_ru", "")
        if abstract and len(abstract) > VERBATIM_MAX_LENGTH:
            warn(f"  Record '{rec_id}' abstract_ru is long ({len(abstract)} chars)",
                 "may contain verbatim text")

    return data


def validate_landscape_output(path):
    """Validate the landscape JSON output."""
    print("\n--- Landscape Output Validation ---")
    data, ok = validate_json_file(path, "landscape_output.json")
    if not ok:
        return None

    for field in REQUIRED_LANDSCAPE_FIELDS:
        check(f"Output has '{field}'", field in data,
              f"missing field '{field}'")

    # Check records_count is positive
    rc = data.get("records_count", 0)
    check("records_count > 0", rc > 0, f"got {rc}")

    # Check theme_clusters is a non-empty array
    clusters = data.get("theme_clusters", [])
    check("theme_clusters is non-empty array",
          isinstance(clusters, list) and len(clusters) > 0)

    # Check structure_patterns is an array
    sp = data.get("structure_patterns", [])
    check("structure_patterns is array", isinstance(sp, list))

    # Check recommended_outline is array of objects with required fields
    outline = data.get("recommended_outline", [])
    check("recommended_outline is non-empty array",
          isinstance(outline, list) and len(outline) > 0)

    outline_fields = {"chapter_id", "title", "role", "purpose"}
    for ch in outline:
        missing = outline_fields - set(ch.keys())
        check(f"  Outline chapter '{ch.get('chapter_id', '?')}' has all fields",
              len(missing) == 0, f"missing: {missing}")

    return data


def validate_markdown_report(path):
    """Validate the Markdown report has all 12 sections."""
    print("\n--- Markdown Report Validation ---")

    if not os.path.isfile(path):
        check("landscape_report.md exists", False, "file not found")
        return False

    with open(path, encoding="utf-8") as f:
        content = f.read()

    check("Markdown report is non-empty", len(content) > 0)

    for section in MD_SECTIONS:
        # Check if section header exists (## prefix or plain text)
        found = section in content
        check(f"Section '{section}' present", found)

    # Check no Zotero local paths
    for pattern in ZOTERO_PATH_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            check("No Zotero local paths in report", False,
                  f"found pattern: {match.group()}")
            break
    else:
        check("No Zotero local paths in report", True)

    return True


def validate_no_zotero_paths_in_examples():
    """Check that example files don't contain Zotero local attachment paths."""
    print("\n--- Zotero Path Check ---")
    if not os.path.isdir(EXAMPLES_DIR):
        warn("Examples directory not found", EXAMPLES_DIR)
        return

    for fname in os.listdir(EXAMPLES_DIR):
        fpath = os.path.join(EXAMPLES_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        if not fname.endswith(".json"):
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        for pattern in ZOTERO_PATH_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                check(f"No Zotero paths in {fname}", False,
                      f"found: {match.group()[:60]}")
                break
        else:
            check(f"No Zotero paths in {fname}", True)


def validate_no_large_verbatim_text(data):
    """Check that no record contains large verbatim text blocks."""
    print("\n--- Verbatim Text Check ---")
    if not data:
        warn("No data to check")
        return

    for i, rec in enumerate(data):
        rec_id = rec.get("id", f"record_{i}")
        for field, value in rec.items():
            if isinstance(value, str) and len(value) > VERBATIM_MAX_LENGTH:
                warn(f"Record '{rec_id}' field '{field}' is {len(value)} chars",
                     "may contain verbatim text")


def deep_validate(check_local_zotero):
    """Run deep validation checks."""
    print("\n" + "=" * 60)
    print("DEEP VALIDATION")
    print("=" * 60)

    # Check all scripts exist and are importable
    scripts = [
        ("build_dissertation_landscape.py", BUILD_SCRIPT),
        ("import_zotero_landscape_records.py", IMPORT_SCRIPT),
    ]

    for name, path in scripts:
        exists = os.path.isfile(path)
        check(f"Script {name} exists", exists)
        if exists:
            # Try to import (syntax check)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                check(f"Script {name} is importable", True)
            except Exception as e:
                check(f"Script {name} is importable", False, str(e)[:100])

    # Check landscape directory structure
    check("research_layer/landscape/ directory exists",
          os.path.isdir(LANDSCAPE_DIR))
    check("research_layer/landscape/examples/ directory exists",
          os.path.isdir(EXAMPLES_DIR))

    # Validate all JSON files in examples
    if os.path.isdir(EXAMPLES_DIR):
        json_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".json")]
        check("At least one example JSON exists", len(json_files) > 0,
              f"found {len(json_files)} files")

        for fname in json_files:
            fpath = os.path.join(EXAMPLES_DIR, fname)
            data, ok = validate_json_file(fpath, f"examples/{fname}")
            if ok and isinstance(data, list):
                for rec in data:
                    rec_id = rec.get("id", "?")
                    for field in RECORD_QUALITY_FIELDS:
                        check(f"  [{fname}] '{rec_id}' has '{field}'",
                              field in rec)

    # Check .phd_build/zotero/ if it exists
    if check_local_zotero and os.path.isdir(ZOTERO_DIR):
        json_files = [f for f in os.listdir(ZOTERO_DIR) if f.endswith(".json")]
        for fname in json_files:
            fpath = os.path.join(ZOTERO_DIR, fname)
            validate_json_file(fpath, f".phd_build/zotero/{fname}")



def main():
    results.clear()
    parser = argparse.ArgumentParser(
        description="Validate dissertation landscape inputs and outputs."
    )
    parser.add_argument("--deep", action="store_true",
                        help="Run full deep validation")
    parser.add_argument("--samples", action="store_true",
                        help="Build and validate bundled examples in isolated temporary directories")
    parser.add_argument("--output-json", help="Path to the generated landscape JSON")
    parser.add_argument("--output-md", help="Path to the generated landscape Markdown")
    args = parser.parse_args()
    explicit_output = bool(args.output_json or args.output_md)
    if args.samples and explicit_output:
        parser.error("--samples cannot be combined with existing outputs")

    print("Dissertation Landscape Validator")
    sample_data = validate_sample_input()
    validate_no_zotero_paths_in_examples()
    if sample_data:
        validate_no_large_verbatim_text(sample_data)

    if not args.samples:
        output_data = validate_landscape_output(args.output_json or LANDSCAPE_JSON_OUTPUT)
        validate_markdown_report(args.output_md or LANDSCAPE_MD_OUTPUT)
        if args.deep and not explicit_output and output_data and sample_data:
            check("Output records_count matches input length",
                  output_data.get("records_count") == len(sample_data))

    if args.deep:
        deep_validate(check_local_zotero=not (args.samples or explicit_output))
    if args.samples or args.deep:
        if validate_e2e_build() is False:
            check("End-to-end sample builds", False)

    # Summary
    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed

    if failed == 0:
        print(f"All passed: {passed}/{total} checks")
    else:
        print(f"Result: {passed} passed, {failed} failed (total {total})")
    print("=" * 60)

    return 0 if failed == 0 else 1




def validate_e2e_build():
    """End-to-end: run builder on raw sample inputs and verify output."""
    import subprocess
    import tempfile
    
    print(f"\n--- End-to-End Build Test ---")
    
    test_cases = [
        ("dissercat", "dissercat_landscape_input_sample.json", "vehicle state estimation"),
        ("zotero", "zotero_landscape_input_sample.json", "vehicle state estimation from Zotero"),
    ]
    
    for name, sample_file, topic in test_cases:
        sample_path = os.path.join(EXAMPLES_DIR, sample_file)
        if not check(f"{name}: sample exists", os.path.isfile(sample_path)):
            continue
        with tempfile.TemporaryDirectory(prefix="ptb-landscape-") as directory:
            json_path = os.path.join(directory, "landscape.json")
            md_path = os.path.join(directory, "landscape.md")
            try:
                result = subprocess.run(
                    [sys.executable, "-X", "utf8", BUILD_SCRIPT,
                     "--input", sample_path, "--output-json", json_path,
                     "--output-md", md_path, "--topic", topic],
                    capture_output=True, encoding="utf-8", timeout=60
                )
            except subprocess.TimeoutExpired:
                check(f"{name}: builder finished", False, "timed out")
                continue
            if not check(f"{name}: builder finished", result.returncode == 0,
                         result.stderr.strip()[:200]):
                continue
            output = validate_landscape_output(json_path)
            validate_markdown_report(md_path)
            if output:
                with open(sample_path, encoding="utf-8") as sample:
                    check(f"{name}: output records_count matches input",
                          output.get("records_count") == len(json.load(sample)))
                platforms = output.get("source_summary", {}).get("platforms", {})
                check(f"{name}: source platforms identified",
                      any(platform != "unknown" for platform in platforms))


if __name__ == "__main__":
    sys.exit(main())
