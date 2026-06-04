#!/usr/bin/env python3
"""
bind_evidence_to_chapters.py — v5.3.1 Chapter Evidence Binding

Pure-rule (no LLM) binding of normalized literature records to thesis chapters
based on evidence role intersection and keyword overlap.

Inputs:
  --outline      Path to user_outline_sample.md (or any outline .md)
  --literature   Path to normalized_literature_sample.json
  --chapter      Chapter ID: INTRO|SURVEY|THEORY|MODEL|METHOD|EXPERIMENT|RESULT|DISCUSSION|CONCLUSION
  --output       Path for chapter_evidence_map.json
  --bindings-output  Path for evidence_binding_records.json (array)

Outputs:
  1. chapter_evidence_map.json   (conforms to chapter_evidence_map.schema.json)
  2. evidence_binding_records.json (conforms to evidence_binding_record.schema.json)

Exit code: 0 = success, 1 = error.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone


# ─── Constants ───────────────────────────────────────────────────────────────

VALID_CHAPTERS = [
    "INTRO", "SURVEY", "THEORY", "MODEL", "METHOD",
    "EXPERIMENT", "RESULT", "DISCUSSION", "CONCLUSION"
]

CHAPTER_TO_CH = {
    "INTRO": "CH1", "SURVEY": "CH2", "THEORY": "CH3", "MODEL": "CH4",
    "METHOD": "CH5", "EXPERIMENT": "CH6", "RESULT": "CH7",
    "DISCUSSION": "CH8", "CONCLUSION": "CH8",  # Both DISCUSSION & CONCLUSION → CH8
}

CHAPTER_NAMES = {
    "INTRO": "Введение (Introduction)",
    "SURVEY": "Обзор литературы (Literature Review)",
    "THEORY": "Теоретические основы (Theoretical Foundations)",
    "MODEL": "Математическая модель (Mathematical Model)",
    "METHOD": "Методология (Methodology)",
    "EXPERIMENT": "Экспериментальные исследования (Experiments)",
    "RESULT": "Результаты (Results)",
    "DISCUSSION": "Обсуждение (Discussion)",
    "CONCLUSION": "Заключение (Conclusion)",
}

CHAPTER_FUNCTIONS = {
    "INTRO": "introduction",
    "SURVEY": "literature_review",
    "THEORY": "theoretical_foundations",
    "MODEL": "architecture",
    "METHOD": "methodology",
    "EXPERIMENT": "evaluation",
    "RESULT": "results",
    "DISCUSSION": "discussion",
    "CONCLUSION": "conclusion",
}

# Role → required evidence roles per chapter
CHAPTER_REQUIRED_ROLES = {
    "INTRO":      ["background_context", "research_gap", "contribution_positioning"],
    "SURVEY":     ["background_context", "research_gap", "method_comparison"],
    "THEORY":     ["definition", "method_basis"],
    "MODEL":      ["method_basis", "definition"],
    "METHOD":     ["method_basis", "definition", "method_comparison"],
    "EXPERIMENT": ["benchmark", "validation_standard", "empirical_support"],
    "RESULT":     ["empirical_support"],
    "DISCUSSION": ["contradiction", "empirical_support"],
    "CONCLUSION": ["contribution_positioning", "empirical_support"],
}

# Role → default claim_type
ROLE_TO_CLAIM_TYPE = {
    "background_context":      "descriptive_claim",
    "research_gap":            "gap_claim",
    "definition":              "factual_claim",
    "method_basis":            "methodological_claim",
    "method_comparison":       "evaluative_claim",
    "benchmark":               "factual_claim",
    "validation_standard":     "methodological_claim",
    "empirical_support":       "factual_claim",
    "contradiction":           "evaluative_claim",
    "contribution_positioning":"contribution_claim",
    "structure_reference":     "theoretical_claim",
    "supplementary_detail":    "descriptive_claim",
}

# Role → default claim text templates (EN + RU)
ROLE_CLAIM_TEXT = {
    "background_context": {
        "INTRO":      "Domain background and current state of {topic}.",
        "SURVEY":     "General overview of research landscape in {topic}.",
    },
    "research_gap": {
        "INTRO":      "Existing approaches to {topic} have known limitations.",
        "SURVEY":     "Unresolved research gaps identified in {topic}.",
    },
    "contribution_positioning": {
        "INTRO":      "This work contributes a novel approach to {topic}.",
        "CONCLUSION": "The proposed approach advances the state of {topic}.",
    },
    "definition": {
        "THEORY":  "Key terms and constructs for {topic} are formally defined.",
        "MODEL":   "Definitions of model parameters for {topic}.",
        "METHOD":  "Terminology and operational definitions for {topic}.",
    },
    "method_basis": {
        "THEORY":  "Theoretical foundation of the chosen method for {topic}.",
        "MODEL":   "Mathematical basis of the model for {topic}.",
        "METHOD":  "Algorithmic basis and implementation of {topic}.",
    },
    "method_comparison": {
        "SURVEY":  "Comparison of alternative methods for {topic}.",
        "METHOD":  "Justification of method selection for {topic}.",
    },
    "benchmark": {
        "EXPERIMENT": "Established benchmarks and datasets used for {topic}.",
    },
    "validation_standard": {
        "EXPERIMENT": "Validation protocols and quality criteria for {topic}.",
    },
    "empirical_support": {
        "EXPERIMENT": "Empirical evidence from prior studies supporting {topic}.",
        "RESULT":     "Empirical results confirming the effectiveness of {topic}.",
        "DISCUSSION": "Empirical findings discussed in context of {topic}.",
        "CONCLUSION": "Summary of empirical contributions to {topic}.",
    },
    "contradiction": {
        "DISCUSSION": "Contradictory findings or alternative perspectives on {topic}.",
    },
}

# Role → recommended action templates
ROLE_GAP_ACTION = {
    "background_context":       "Search eLIBRARY for overview articles on {topic}",
    "research_gap":             "Search DisserCat for dissertations identifying gaps in {topic}",
    "definition":               "Find authoritative textbook or review for definitions in {topic}",
    "method_basis":             "Locate seminal paper proposing the method for {topic}",
    "method_comparison":        "Find comparative studies or meta-analyses on {topic}",
    "benchmark":                "Identify standard benchmark datasets for {topic}",
    "validation_standard":      "Find methodology papers establishing validation protocols for {topic}",
    "empirical_support":        "Search for empirical studies supporting claims about {topic}",
    "contradiction":            "Find papers presenting alternative or contradictory views on {topic}",
    "contribution_positioning": "Position novelty relative to recent publications on {topic}",
    "structure_reference":      "Find foundational frameworks for {topic}",
    "supplementary_detail":     "Add supplementary references for {topic}",
}

# Role → recommended source types when missing
ROLE_RECOMMENDED_SOURCE_TYPE = {
    "background_context":       "elibrary",
    "research_gap":             "dissercat",
    "definition":               "textbook",
    "method_basis":             "elibrary",
    "method_comparison":        "elibrary",
    "benchmark":                "elibrary",
    "validation_standard":      "elibrary",
    "empirical_support":        "elibrary",
    "contradiction":            "elibrary",
    "contribution_positioning": "elibrary",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────


def parse_outline_headings(outline_text):
    """Extract section headings (##, ###) from outline markdown."""
    headings = []
    for line in outline_text.splitlines():
        m = re.match(r"^#{2,4}\s+(.+)$", line)
        if m:
            headings.append(m.group(1).strip())
    return headings


def extract_outline_keywords(outline_text):
    """Extract significant tokens from outline headings and body."""
    headings = parse_outline_headings(outline_text)
    text = " ".join(headings)
    # Also include bullet-point content
    for line in outline_text.splitlines():
        if line.strip().startswith("- "):
            text += " " + line.strip()[2:]
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]{3,}", text, re.UNICODE)
    return set(t.lower() for t in tokens)


def extract_source_keywords(source):
    """Extract keywords from a literature record for matching."""
    kws = set()
    for field in ("title_en", "title_ru", "abstract_ru"):
        val = source.get(field, "")
        if val:
            tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]{3,}", val, re.UNICODE)
            kws.update(t.lower() for t in tokens)
    for kw in source.get("keywords_ru", []):
        tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]{3,}", kw, re.UNICODE)
        kws.update(t.lower() for t in tokens)
    return kws


def role_keywords(role):
    """Generate representative keywords for an evidence role."""
    mapping = {
        "background_context":       {"background", "overview", "context", "state", "landscape", "survey", "обзор", "состояние", "контекст", "актуальн"},
        "research_gap":             {"gap", "limitation", "unresolved", "challenge", "проблема", "ограничени", "недостат", "неизучен"},
        "definition":               {"definition", "terminology", "concept", "construct", "определени", "термин", "понятие"},
        "method_basis":             {"method", "algorithm", "technique", "approach", "метод", "алгоритм", "подход", "фильтр", "модел"},
        "method_comparison":        {"comparison", "comparative", "versus", "benchmark", "сравнени", "сопоставлени"},
        "benchmark":                {"benchmark", "dataset", "evaluation", "standard", "эталон", "датасет", "оценк"},
        "validation_standard":      {"validation", "protocol", "criteria", "standard", "валидац", "протокол", "критери"},
        "empirical_support":        {"empirical", "experiment", "result", "finding", "эксперимент", "результат", "исследовани"},
        "contradiction":            {"contradiction", "alternative", "however", "противоречи", "альтернатив", "однако"},
        "contribution_positioning": {"novel", "contribution", "proposed", "unlike", "вклад", "новизна", "предложен"},
        "structure_reference":      {"framework", "architecture", "structure", "модульност", "архитектур"},
        "supplementary_detail":     {"detail", "appendix", "parameter", "подробн", "параметр"},
    }
    return mapping.get(role, set())


def keyword_overlap(set_a, set_b):
    """Return count of overlapping tokens between two sets."""
    return len(set_a & set_b)


def classify_strength(overlap_count, has_role_match):
    """Classify evidence_strength based on keyword overlap and role match."""
    if overlap_count >= 4 and has_role_match:
        return "strong"
    elif overlap_count >= 2 and has_role_match:
        return "medium"
    elif has_role_match:
        return "weak"
    else:
        return "none"


def classify_gap_status(has_source, strength):
    """Classify gap_status: covered / partial / missing."""
    if not has_source:
        return "missing"
    if strength in ("strong", "medium"):
        return "covered"
    # strength == "weak" with a source → partial
    return "partial"


# ─── Core binding logic ─────────────────────────────────────────────────────


def find_candidates(role, literature, outline_kws):
    """
    Find literature sources whose evidence_role intersects with `role`
    and rank by keyword overlap with outline keywords + role keywords.
    Returns list of (source, overlap_score, has_role_match) sorted desc.
    """
    r_kws = role_keywords(role)
    search_kws = outline_kws | r_kws

    candidates = []
    for src in literature:
        src_roles = set(src.get("evidence_role", []))
        has_role = role in src_roles
        src_kws = extract_source_keywords(src)
        overlap = keyword_overlap(search_kws, src_kws)
        if has_role or overlap >= 2:
            candidates.append((src, overlap, has_role))

    # Sort by (has_role desc, overlap desc, year desc)
    candidates.sort(key=lambda c: (c[2], c[1], c[0].get("year", 0)), reverse=True)
    return candidates


def generate_binding_records(chapter, literature, outline_text):
    """
    Generate evidence_binding_records for the given chapter.
    Returns (bindings_list, topic_str).
    """
    required_roles = CHAPTER_REQUIRED_ROLES.get(chapter, [])
    outline_kws = extract_outline_keywords(outline_text)
    headings = parse_outline_headings(outline_text)

    # Infer topic from outline headings
    topic = "the research topic"
    # Try to extract a topic-like phrase from the first H2 heading
    for h in headings:
        cleaned = re.sub(r"^Глава\s+\d+\.\s*", "", h)
        if cleaned:
            topic = cleaned
            break

    ch_number = CHAPTER_TO_CH.get(chapter, "CH1")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    bindings = []
    for idx, role in enumerate(required_roles, 1):
        binding_id = f"BIND-{chapter}-{idx:03d}"

        # Find best matching source
        candidates = find_candidates(role, literature, outline_kws)

        matched_ids = []
        evidence_strength = "none"
        gap_status = "missing"

        if candidates:
            best_src, overlap, has_role = candidates[0]
            matched_ids = [best_src.get("id", best_src.get("source_id", ""))]
            evidence_strength = classify_strength(overlap, has_role)
            gap_status = classify_gap_status(True, evidence_strength)
            # If strength is "none" even with a source, treat as partial
            if evidence_strength == "none":
                gap_status = "partial"
                evidence_strength = "weak"

        # Claim text
        claim_templates = ROLE_CLAIM_TEXT.get(role, {})
        raw_claim = claim_templates.get(chapter, f"Evidence of type '{role}' for {{topic}}")
        claim_text = raw_claim.format(topic=topic)

        # Claim type
        claim_type = ROLE_TO_CLAIM_TYPE.get(role, "descriptive_claim")

        # Recommended action
        if gap_status == "missing":
            action_template = ROLE_GAP_ACTION.get(role, "Find a source for {topic}")
            action = action_template.format(topic=topic)
        elif gap_status == "partial":
            action = f"Strengthen '{role}' evidence for {topic} with additional sources"
        else:
            action = f"Verify relevance of source {matched_ids[0]} for '{role}'"

        # Recommended query (for missing/partial)
        recommended_query = None
        if gap_status in ("missing", "partial"):
            query_kws = list(outline_kws)[:5]
            recommended_query = f"{role} {' '.join(query_kws)}"

        binding = {
            "binding_id": binding_id,
            "chapter": ch_number,
            "chapter_function": CHAPTER_FUNCTIONS.get(chapter, "introduction"),
            "claim_text": claim_text,
            "claim_type": claim_type,
            "required_evidence_roles": [role],
            "matched_source_ids": matched_ids,
            "evidence_strength": evidence_strength,
            "gap_status": gap_status,
            "recommended_action": action,
            "created_at": ts,
            "updated_at": ts,
        }
        if recommended_query:
            binding["recommended_query"] = recommended_query

        bindings.append(binding)

    return bindings, topic


def build_chapter_evidence_map(chapter, bindings, topic):
    """
    Build the chapter_evidence_map.json structure from bindings.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build bound_records (summary view)
    bound_records = []
    for b in bindings:
        record = {
            "binding_id": b["binding_id"],
            "source_id": b["matched_source_ids"][0] if b["matched_source_ids"] else "",
            "evidence_role": b["required_evidence_roles"][0],
            "evidence_strength": b["evidence_strength"],
            "gap_status": b["gap_status"],
            "recommended_action": b["recommended_action"],
        }
        bound_records.append(record)

    # Gap analysis
    total_bound = len(bindings)
    covered = sum(1 for b in bindings if b["gap_status"] == "covered")
    partial = sum(1 for b in bindings if b["gap_status"] == "partial")
    missing = sum(1 for b in bindings if b["gap_status"] == "missing")
    not_needed = sum(1 for b in bindings if b["gap_status"] == "not_needed")
    denom = total_bound if total_bound > 0 else 1
    coverage_ratio = round((covered + not_needed) / denom, 2)

    unresolved_gaps = []
    for b in bindings:
        if b["gap_status"] in ("missing", "partial"):
            role = b["required_evidence_roles"][0]
            risk = "high" if b["gap_status"] == "missing" else "medium"
            gap_entry = {
                "evidence_role": role,
                "status": b["gap_status"],
                "recommended_source_type": ROLE_RECOMMENDED_SOURCE_TYPE.get(role, "elibrary"),
                "risk_level": risk,
            }
            if b.get("recommended_query"):
                gap_entry["recommended_query"] = b["recommended_query"]
            unresolved_gaps.append(gap_entry)

    # Required roles presence
    required_roles = CHAPTER_REQUIRED_ROLES.get(chapter, [])
    role_presence = {}
    for role in required_roles:
        role_bindings = [b for b in bindings if role in b["required_evidence_roles"]]
        if not role_bindings:
            role_presence[role] = "missing"
        elif any(b["gap_status"] == "covered" for b in role_bindings):
            role_presence[role] = "present"
        else:
            role_presence[role] = "partial"

    evidence_map = {
        "chapter_id": chapter,
        "chapter_name": CHAPTER_NAMES.get(chapter, chapter),
        "bound_records": bound_records,
        "gap_analysis": {
            "total_bound": total_bound,
            "covered": covered,
            "partial": partial,
            "missing": missing,
            "not_needed": not_needed,
            "coverage_ratio": coverage_ratio,
            "unresolved_gaps": unresolved_gaps,
        },
        "required_roles_present": role_presence,
        "generated_at": ts,
    }

    return evidence_map


# ─── CLI ─────────────────────────────────────────────────────────────────────


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Bind evidence roles to a thesis chapter using rule-based matching."
    )
    parser.add_argument("--outline", required=True,
                        help="Path to outline .md file")
    parser.add_argument("--literature", required=True,
                        help="Path to normalized_literature JSON")
    parser.add_argument("--chapter", required=True,
                        choices=VALID_CHAPTERS,
                        help="Chapter ID (INTRO, SURVEY, THEORY, MODEL, METHOD, EXPERIMENT, RESULT, DISCUSSION, CONCLUSION)")
    parser.add_argument("--output", required=True,
                        help="Output path for chapter_evidence_map.json")
    parser.add_argument("--bindings-output", required=True,
                        help="Output path for evidence_binding_records.json")
    return parser.parse_args(argv)


def main():
    args = parse_args()

    # Load inputs
    if not os.path.isfile(args.outline):
        print(f"ERROR: Outline file not found: {args.outline}", file=sys.stderr)
        return 1
    if not os.path.isfile(args.literature):
        print(f"ERROR: Literature file not found: {args.literature}", file=sys.stderr)
        return 1

    with open(args.outline, "r", encoding="utf-8") as f:
        outline_text = f.read()

    with open(args.literature, "r", encoding="utf-8") as f:
        literature = json.load(f)

    if not isinstance(literature, list):
        print("ERROR: Literature file must contain a JSON array.", file=sys.stderr)
        return 1

    chapter = args.chapter
    print(f"[bind_evidence] Chapter: {chapter}")
    print(f"[bind_evidence] Literature records: {len(literature)}")
    print(f"[bind_evidence] Required roles: {CHAPTER_REQUIRED_ROLES.get(chapter, [])}")

    # Generate bindings
    bindings, topic = generate_binding_records(chapter, literature, outline_text)

    # Build evidence map
    evidence_map = build_chapter_evidence_map(chapter, bindings, topic)

    # Write outputs
    os.makedirs(os.path.dirname(os.path.abspath(args.bindings_output)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.bindings_output, "w", encoding="utf-8") as f:
        json.dump(bindings, f, ensure_ascii=False, indent=2)
    print(f"[bind_evidence] Wrote {len(bindings)} bindings → {args.bindings_output}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(evidence_map, f, ensure_ascii=False, indent=2)
    print(f"[bind_evidence] Wrote chapter evidence map → {args.output}")

    # Print summary
    ga = evidence_map["gap_analysis"]
    print(f"\n[bind_evidence] Gap analysis:")
    print(f"  Total bound:  {ga['total_bound']}")
    print(f"  Covered:      {ga['covered']}")
    print(f"  Partial:      {ga['partial']}")
    print(f"  Missing:      {ga['missing']}")
    print(f"  Coverage:     {ga['coverage_ratio']*100:.0f}%")
    if ga["unresolved_gaps"]:
        print(f"  Unresolved gaps: {len(ga['unresolved_gaps'])}")
        for g in ga["unresolved_gaps"]:
            print(f"    - {g['evidence_role']}: {g['status']}")

    print(f"\n[bind_evidence] DONE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
