#!/usr/bin/env python3
"""
extract_structure_records.py — Read planning_layer/patterns/*.json and produce structure records.

Loads pattern files, derives section_sequence and boolean flags,
and outputs records matching structure_record.schema.json format.

Output: .phd_build/structure_records.jsonl (one JSON per line)
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PATTERNS_DIR = BASE / "planning_layer" / "patterns"
STRUCTURE_PATTERNS_FILE = PATTERNS_DIR / "STRUCTURE_PATTERNS.json"
BUILD_DIR = BASE / ".phd_build"
OUTPUT_PATH = BUILD_DIR / "structure_records.jsonl"

# Pattern type from logic_flow field
PATTERN_TYPE_MAP = {
    "deductive": "deductive",
    "inductive": "inductive",
    "hypothetico-deductive": "hypothetico-deductive",
    "mixed": "mixed",
    "other": "other",
}

# Russian chapter title to DIS category mapping
CHAPTER_CATEGORY_MAP = {
    "введение": "INTRO",
    "выводы": "CONCLUSION",
    "заключение": "CONCLUSION",
    "обзор": "SURVEY",
    "данные": "RESULT",
    "датасет": "METHOD",
    "метод": "METHOD",
    "модел": "MODEL",
    "эксперимент": "EXPERIMENT",
    "результат": "RESULT",
    "обсуждение": "DISCUSSION",
    "аналит": "SURVEY",
    "теорет": "MODEL",
    "формал": "FORMAL_DEFS",
    "архитектур": "ENGINEERING",
    "алгоритм": "METHOD",
}


def derive_section_sequence_from_chapters(chapters: list) -> list[str]:
    """Derive ordered DIS category sequence from Russian chapter titles."""
    sequence: list[str] = []
    seen: set[str] = set()
    for ch in chapters:
        title = ch if isinstance(ch, str) else ch.get("title", "")
        title_lower = title.lower()
        category: str = "SURVEY"  # default fallback
        for keyword, cat in CHAPTER_CATEGORY_MAP.items():
            if keyword in title_lower:
                category = cat
                break
        if category not in seen:
            sequence.append(category)
            seen.add(category)
    return sequence


def classify_pattern_type(section_sequence: list[str], logic_flow: str | None = None) -> str:
    """Classify pattern type from section_sequence ordering."""
    if logic_flow and logic_flow in PATTERN_TYPE_MAP:
        return PATTERN_TYPE_MAP[logic_flow]

    # Heuristic classification
    has_intro = "INTRO" in section_sequence
    has_model = "MODEL" in section_sequence
    has_method = "METHOD" in section_sequence
    has_experiment = "EXPERIMENT" in section_sequence
    has_survey = "SURVEY" in section_sequence
    has_result = "RESULT" in section_sequence

    if has_intro and has_model and has_method:
        return "deductive"
    if has_intro and has_survey and has_method and has_result:
        return "inductive"
    if has_intro and has_survey and has_model and has_experiment:
        return "hypothetico-deductive"
    return "other"


def build_structure_record(
    record_id: str,
    pattern_data: dict,
    section_sequence: list[str],
    pattern_type: str,
    source_label: str,
) -> dict:
    """Build a structure_record matching schema format."""
    cluster = pattern_data.get("cluster", "GLOBAL")
    evidence_raw = pattern_data.get("evidence_count", {})

    # Normalize evidence_count to schema format
    evidence_count = {
        "count": 0,
        "source": "pending",
        "confidence": "pending",
    }
    if isinstance(evidence_raw, dict):
        if "value" in evidence_raw:
            evidence_count["source"] = str(evidence_raw["value"])
        elif "count" in evidence_raw:
            evidence_count["count"] = evidence_raw["count"]
        if "confidence" in evidence_raw:
            evidence_count["confidence"] = evidence_raw["confidence"]

    # Build boolean flags
    seq_set = set(section_sequence)

    record = {
        "id": record_id,
        "paper_id": "paper_0000",  # placeholder — pattern-level record
        "section_sequence": section_sequence,
        "discipline": pattern_data.get("name", "unknown"),
        "cluster": cluster,
        "section_count": len(section_sequence),
        "has_intro": "INTRO" in seq_set,
        "has_survey": "SURVEY" in seq_set,
        "has_model": "MODEL" in seq_set,
        "has_method": "METHOD" in seq_set,
        "has_experiment": "EXPERIMENT" in seq_set,
        "has_result": "RESULT" in seq_set,
        "has_discussion": "DISCUSSION" in seq_set,
        "has_conclusion": "CONCLUSION" in seq_set,
        "has_transition": "TRANSITION" in seq_set,
        "has_formal_defs": "FORMAL_DEFS" in seq_set,
        "has_engineering": "ENGINEERING" in seq_set,
        "has_aref": "AREF" in seq_set,
        "has_utils": "UTILS" in seq_set,
        "pattern_type": pattern_type,
        "evidence_count": evidence_count,
        "source": source_label,
    }
    return record


def load_structured_patterns() -> list[tuple[dict, str]]:
    """Load patterns from STRUCTURE_PATTERNS.json and individual files."""
    patterns = []

    # Load main STRUCTURE_PATTERNS.json
    if STRUCTURE_PATTERNS_FILE.exists():
        with open(STRUCTURE_PATTERNS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        for p in data.get("patterns", []):
            patterns.append((p, "STRUCTURE_PATTERNS"))

    # Load individual pattern files (skip STRUCTURE_PATTERNS.json)
    for fp in sorted(PATTERNS_DIR.glob("*.json")):
        if fp.name == "STRUCTURE_PATTERNS.json":
            continue
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        patterns.append((data, fp.stem))

    return patterns


def main():
    if not PATTERNS_DIR.is_dir():
        print(f"ERROR: {PATTERNS_DIR} not found")
        sys.exit(1)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    patterns = load_structured_patterns()
    if not patterns:
        print("ERROR: No pattern files found")
        sys.exit(1)

    print(f"Loaded {len(patterns)} patterns from planning_layer/patterns/")

    records = []
    for idx, (pattern_data, source_label) in enumerate(patterns, 1):
        record_id = f"structure_{idx:04d}"

        # Derive section_sequence
        if "chapter_structure" in pattern_data:
            section_sequence = derive_section_sequence_from_chapters(
                pattern_data["chapter_structure"]
            )
        elif "chapters" in pattern_data:
            section_sequence = derive_section_sequence_from_chapters(
                pattern_data["chapters"]
            )
        else:
            section_sequence = ["INTRO", "SURVEY", "CONCLUSION"]

        # Classify pattern type
        logic_flow = pattern_data.get("logic_flow")
        pattern_type = classify_pattern_type(section_sequence, logic_flow)

        record = build_structure_record(
            record_id, pattern_data, section_sequence, pattern_type, source_label
        )
        records.append(record)

        pid = pattern_data.get("pattern_id", pattern_data.get("id", "unknown"))
        print(f"  [{record_id}] {pid}: "
              f"{len(section_sequence)} sections, type={pattern_type}")

    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nWritten: {OUTPUT_PATH}")
    print(f"Total structure records: {len(records)}")


if __name__ == "__main__":
    main()
