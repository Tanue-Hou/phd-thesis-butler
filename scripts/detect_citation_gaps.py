#!/usr/bin/env python3
"""
detect_citation_gaps.py — v5.3.2  Citation Gap Detection (rule-based)

Detects claims in thesis chapter text and identifies citation gaps.
Pure regex/keyword approach, no LLM, no external dependencies.

Usage:
    python3 scripts/detect_citation_gaps.py \
        --input   evidence_layer/examples/user_chapter_sample.md \
        --literature evidence_layer/examples/normalized_literature_sample.json \
        --output  /tmp/citation_gap_report.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

# ─── Pattern definitions (multilingual RU/EN) ───────────────────────────

RESEARCH_GAP_PATTERNS = [
    r"недостаточно\s+изучен",
    r"отсутствует",
    r"ограничивается",
    r"оста(?:ётся|ется)\s+(?:неизучен|нерешен|недооценен)",
    r"пробел",
    r"мало\s+исследован",
    r"ещё\s+не\s+решен",
    r"не\s+(?:был[аио]?\s+)?(?:достаточно|полностью)\s+(?:изучен|исследован|решен)",
    r"limited",
    r"lacks",
    r"remains\s+unresolved",
    r"little\s+research",
    r"not\s+been\s+fully",
    r"understudied",
    r"gap\s+in",
    r"not\s+yet\s+addressed",
    r"few\s+studies",
    r"insufficiently\s+studied",
]

EVALUATIVE_PATTERNS = [
    r"улучшает",
    r"превосходит",
    r"повышает",
    r"более\s+эффективно",
    r"значительно\s+(?:улучш|повыш|увеличив)",
    r"устойчив",
    r"improves",
    r"achieves",
    r"higher\s+accuracy",
    r"outperforms",
    r"better\s+than",
    r"superior",
    r"more\s+effective",
    r"significant(?:ly)?",
    r"robust",
    r"пр[ие]емлем[аоы]?й\s+(?:точност|эффективност)",
]

THEORETICAL_PATTERNS = [
    r"основан\w*\s+на",
    r"применяется",
    r"теори[яюи]",
    r"модел[ьию]",
    r"is\s+based\s+on",
    r"derived\s+from",
    r"theoretical\s+foundation",
    r"framework",
    r"principle",
]

DESCRIPTIVE_PATTERNS = [
    r"is\s+described",
    r"состоит\s+из",
    r"содержит",
    r"describes",
    r"presents",
    r"chapter",
    r"включает",
    r"описан[аыо]?\s+в",
    r"рассматривается",
    r"записываются",
    r"производится",
    r"вычисляется",
    r"извлекаются",
]

CONTRIBUTION_PATTERNS = [
    r"впервые",
    r"предложен\s+нов",
    r"мы\s+предлагаем",
    r"наш\s+вклад",
    r"developed",
    r"novel",
    r"first",
    r"contribution",
    r"proposed",
    r"we\s+propose",
    r"we\s+introduce",
    r"we\s+present",
    r"this\s+work\s+advances",
]

COMMON_KNOWLEDGE_PATTERNS = [
    r"widely\s+used",
    r"well[- ]known",
    r"общеизвестно",
    r"broadly\s+accepted",
    r"является\s+(?:распространён|стандартн|классическ)",
    r"является\s+интерпретируемым",
]

CITATION_PATTERN = re.compile(
    r"\[\d+(?:[,\s\-–—]\d+)*\]"
    r"|(?:\((?:[A-ZА-ЯЁ][a-zа-яё]+(?:\s+(?:et\s+al\.?|и\s+др\.?))?)"
    r"(?:,?\s*\d{4}(?:[a-z]?)?(?:;\s*[A-ZА-ЯЁ][a-zа-яё]+\s*,?\s*\d{4})*)?\))",
    re.IGNORECASE,
)

# ─── Risk level matrix: claim_type → {chapter_range: risk_level} ────────

RISK_TABLE = {
    "factual_claim":      {"1-2": "high",     "3-4": "high",     "5-6": "critical", "7-8": "high"},
    "methodological_claim": {"1-2": "medium",  "3-4": "critical", "5-6": "high",     "7-8": "medium"},
    "evaluative_claim":   {"1-2": "medium",   "3-4": "medium",   "5-6": "critical", "7-8": "high"},
    "gap_claim":          {"1-2": "critical", "3-4": "high",     "5-6": "medium",   "7-8": "high"},
    "contribution_claim": {"1-2": "high",     "3-4": "medium",   "5-6": "medium",   "7-8": "critical"},
    "theoretical_claim":  {"1-2": "high",     "3-4": "critical", "5-6": "medium",   "7-8": "medium"},
    "descriptive_claim":  {"1-2": "low",      "3-4": "medium",   "5-6": "low",      "7-8": "low"},
    "common_knowledge":   {"1-2": "low",      "3-4": "low",      "5-6": "low",      "7-8": "low"},
}

CLAIM_TYPE_TO_EVIDENCE_ROLE = {
    "factual_claim":      "background_context",
    "methodological_claim": "method_basis",
    "evaluative_claim":   "benchmark",
    "gap_claim":          "research_gap",
    "contribution_claim": "contribution_positioning",
    "theoretical_claim":  "definition",
    "descriptive_claim":  "definition",
    "common_knowledge":   "background_context",
}

RISK_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# ─── Helpers ─────────────────────────────────────────────────────────────

def parse_args():
    ap = argparse.ArgumentParser(description="Detect citation gaps in thesis chapters (rule-based).")
    ap.add_argument("--input", required=True, help="Path to thesis chapter markdown file.")
    ap.add_argument("--literature", default=None, help="Path to normalized literature JSON array.")
    ap.add_argument("--output", required=True, help="Path for output JSON report.")
    return ap.parse_args()


def detect_chapter(text):
    """Extract chapter identifier from text. Returns 'CHn' or 'UNKNOWN'."""
    patterns = [
        r"(?:^|\n)\s*#{1,3}\s*Глав[аы]\s*\.?\s*(\d+)",
        r"(?:^|\n)\s*#{1,3}\s*(?:Chapter|ГЛАВА|Часть)\s*\.?\s*(\d+)",
        r"(?:^|\n)\s*Глав[аы]\s*\.?\s*(\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return f"CH{m.group(1)}"
    return "UNKNOWN"


def has_inline_citation(text):
    """Check whether text already contains a citation marker."""
    return bool(CITATION_PATTERN.search(text))


def extract_sentences(text):
    """Split markdown text into meaningful sentences."""
    lines = text.splitlines()
    paragraphs = []
    current = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if stripped.startswith("#") or stripped.startswith("    ") or stripped.startswith("```"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            if stripped.startswith("#"):
                paragraphs.append(stripped.lstrip("#").strip())
            continue
        current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))

    sentences = []
    ABBREVIATIONS = {"т.е.", "и.о.", "и.т.д.", "и.д.", "проф.", "доц.", "ст.", "рис.", "табл.", "гл.", "стр.", "см.", "им.", "руб.", "тыс.", "млн.", "млрд.", "e.g.", "i.e.", "etc.", "vs.", "dr.", "mr.", "mrs.", "fig.", "tab.", "vol.", "approx."}

    for para in paragraphs:
        if len(para) < 10:
            continue
        parts = re.split(r"(?<=[.!?…])\s+", para)
        for part in parts:
            p = part.strip()
            if len(p) < 10:
                continue
            last_word = p.rsplit(" ", 1)[-1].lower() if " " in p else ""
            if last_word in ABBREVIATIONS or any(p.endswith(a) for a in ABBREVIATIONS):
                continue
            sentences.append(p)
    return sentences


def classify_claim_type(text):
    """Classify a sentence by claim type using keyword regex."""
    lower = text.lower()

    if _matches(lower, RESEARCH_GAP_PATTERNS):
        return "gap_claim"
    if _matches(lower, THEORETICAL_PATTERNS):
        return "theoretical_claim"
    if _matches(lower, EVALUATIVE_PATTERNS):
        return "evaluative_claim"
    if _matches(lower, CONTRIBUTION_PATTERNS):
        return "contribution_claim"
    if _matches(lower, COMMON_KNOWLEDGE_PATTERNS):
        return "common_knowledge"
    if _matches(lower, DESCRIPTIVE_PATTERNS):
        return "descriptive_claim"
    return "descriptive_claim"


def determine_citation_need(claim_type, text):
    """Determine citation necessity for a classified claim."""
    if has_inline_citation(text):
        return "optional"
    NEED_MAP = {
        "gap_claim":          "required",
        "contribution_claim": "required",
        "evaluative_claim":   "recommended",
        "theoretical_claim":  "recommended",
        "methodological_claim": "recommended",
        "factual_claim":      "recommended",
        "descriptive_claim":  "not_needed",
        "common_knowledge":   "optional",
    }
    return NEED_MAP.get(claim_type, "recommended")


def risk_for_claim(claim_type, chapter):
    """Look up risk level from the risk table."""
    m = re.search(r"\d+", chapter)
    ch_num = int(m.group()) if m else 0
    if 1 <= ch_num <= 2:
        bucket = "1-2"
    elif 3 <= ch_num <= 4:
        bucket = "3-4"
    elif 5 <= ch_num <= 6:
        bucket = "5-6"
    else:
        bucket = "7-8"
    return RISK_TABLE.get(claim_type, {}).get(bucket, "medium")


def match_literature(text, literature):
    """Match a sentence against known literature records.

    Returns (gap_status, matched_source_ids) where gap_status ∈ {covered, partial, missing}.
    If literature is None/empty and a citation is needed, returns ('missing', []).
    """
    if not literature:
        return "missing", []

    lower = text.lower()
    # Extract meaningful keywords (>3 chars) for matching
    keywords = set(re.findall(r"\b\w{4,}\b", lower))

    matched_sources = []
    for rec in literature:
        title = (rec.get("title_ru", "") or "").lower()
        abstract = (rec.get("abstract_ru", "") or "").lower()
        keywords_field = " ".join(rec.get("keywords_ru", [])).lower()
        text_to_match = f"{title} {abstract} {keywords_field}"

        if not text_to_match.strip():
            continue

        source_keywords = set(re.findall(r"\b\w{4,}\b", text_to_match))
        overlap = keywords & source_keywords
        if len(overlap) >= 2:
            matched_sources.append(rec.get("id", ""))

    if matched_sources:
        # Heuristic: ≥2 sources → covered, 1 source → partial
        return ("covered", matched_sources) if len(matched_sources) >= 2 else ("partial", matched_sources)
    return "missing", []


def generate_recommended_query(text):
    """Generate a simple search query from the claim text."""
    # Take first 8 significant words (>3 chars)
    words = [w for w in re.findall(r"\b\w{4,}\b", text)][:8]
    return " ".join(words) if words else text[:80]


def _matches(text, patterns):
    """Check whether text matches any regex in the pattern list."""
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


# ─── Main detection pipeline ─────────────────────────────────────────────

def detect_gaps(input_path, literature):
    """Run the full citation gap detection pipeline."""
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    chapter = detect_chapter(text)
    sentences = extract_sentences(text)

    claims = []
    for idx, sentence in enumerate(sentences, start=1):
        claim_type = classify_claim_type(sentence)
        citation_need = determine_citation_need(claim_type, sentence)
        has_cite = has_inline_citation(sentence)

        # Determine gap_status
        if claim_type == "common_knowledge":
            gap_status = "not_needed"
            matched_ids = []
        elif citation_need == "not_needed" and claim_type == "descriptive_claim":
            gap_status = "not_needed"
            matched_ids = []
        elif has_cite:
            gap_status = "covered"
            matched_ids = []
        elif literature is not None:
            gap_status, matched_ids = match_literature(sentence, literature)
            # If citation not needed, override
            if citation_need == "not_needed":
                gap_status = "not_needed"
        else:
            # No literature provided: any claim needing citation is missing
            if citation_need in ("required", "recommended"):
                gap_status = "missing"
            else:
                gap_status = "not_needed"
            matched_ids = []

        evidence_role = CLAIM_TYPE_TO_EVIDENCE_ROLE.get(claim_type, "definition")
        risk = risk_for_claim(claim_type, chapter)
        matched_source = matched_ids[0] if matched_ids else None

        # Build claim object
        claim = {
            "claim_id": f"c{idx:03d}",
            "claim_text": sentence,
            "claim_type": claim_type,
            "citation_need": citation_need,
            "gap_status": gap_status,
            "recommended_evidence_role": evidence_role,
            "risk_level": risk,
        }
        if matched_source is not None:
            claim["matched_source_id"] = matched_source
        else:
            claim["matched_source_id"] = None

        # Evidence strength heuristic
        if gap_status == "covered":
            claim["evidence_strength"] = "strong"
        elif gap_status == "partial":
            claim["evidence_strength"] = "weak"
        elif gap_status == "not_needed":
            claim["evidence_strength"] = "none"
        else:
            claim["evidence_strength"] = "none"

        # recommended_action for missing claims
        if gap_status == "missing":
            claim["recommended_action"] = (
                f"Find source for {claim_type.replace('_', ' ')}: "
                f"search literature databases for relevant evidence"
            )
            claim["recommended_query"] = generate_recommended_query(sentence)

        claims.append(claim)

    return chapter, claims


def build_summary(claims):
    """Compute the summary section of the report."""
    by_gap = {"covered": 0, "partial": 0, "missing": 0, "not_needed": 0}
    by_risk = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    needs_citation = 0

    for c in claims:
        gs = c["gap_status"]
        by_gap[gs] = by_gap.get(gs, 0) + 1
        rl = c["risk_level"]
        by_risk[rl] = by_risk.get(rl, 0) + 1
        if c["citation_need"] in ("required", "recommended"):
            needs_citation += 1

    total = len(claims)
    not_needed = by_gap["not_needed"]
    covered_or_not_needed = by_gap["covered"] + not_needed
    coverage_ratio = round(covered_or_not_needed / total, 4) if total > 0 else 0.0

    return {
        "total_claims": total,
        "by_gap_status": by_gap,
        "by_risk_level": by_risk,
        "coverage_ratio": coverage_ratio,
        "needs_citation": needs_citation,
        "covered": by_gap["covered"],
        "partial": by_gap["partial"],
        "missing": by_gap["missing"],
    }


def main():
    args = parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    literature = None
    if args.literature:
        if not os.path.isfile(args.literature):
            print(f"Error: literature file not found: {args.literature}", file=sys.stderr)
            sys.exit(1)
        with open(args.literature, "r", encoding="utf-8") as f:
            literature = json.load(f)

    chapter, claims = detect_gaps(args.input, literature)
    summary = build_summary(claims)

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    report = {
        "report_id": f"GAP-{chapter}-{today}",
        "chapter": chapter,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claims": claims,
        "summary": summary,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary to stderr for CLI feedback
    print(f"Report: {report['report_id']}", file=sys.stderr)
    print(f"  Chapter: {chapter}", file=sys.stderr)
    print(f"  Total claims: {summary['total_claims']}", file=sys.stderr)
    print(f"  Needs citation: {summary['needs_citation']}", file=sys.stderr)
    print(f"  Covered: {summary['covered']}, Partial: {summary['partial']}, Missing: {summary['missing']}", file=sys.stderr)
    print(f"  Coverage ratio: {summary['coverage_ratio']:.1%}", file=sys.stderr)
    print(f"Output: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
