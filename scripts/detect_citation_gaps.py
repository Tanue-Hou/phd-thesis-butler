#!/usr/bin/env python3
"""
detect_citation_gaps.py — v5.3.4  Citation Gap Detection (rule-based)

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

BACKGROUND_PATTERNS = [
    r"широко\s+используется",
    r"является\s+основой",
    r"представляет\s+собой",
    r"широко\s+применяется",
    r"служит\s+основой",
    r"is\s+widely\s+used\s+(?:as|in|for)",
    r"is\s+the\s+basis",
    r"forms\s+the\s+basis",
    r"represents\s+(?:a|the)\s+(?:standard|common|fundamental)",
]

FIELD_STATUS_PATTERNS = [
    r"в\s+настоящее\s+время",
    r"современн(?:ые|ых|ому)",
    r"последние\s+годы",
    r"актуальн(?:ость|ые|ым)",
    r"в\s+последнее\s+время",
    r"currently",
    r"modern\s+(?:approaches|methods|systems)",
    r"in\s+recent\s+years",
    r"state[\s-]of[\s-]the[\s-]art",
    r"contemporary",
]

METHOD_PATTERNS = [
    r"используется\s+метод",
    r"применяется\s+алгоритм",
    r"основан\s+на\s+(?:методе|алгоритме|подходе)",
    r"метод(?:\s+|\s*\()\s*[А-Яа-яA-Za-z]",
    r"алгоритм(?:\s+|\s*\()\s*[А-Яа-яA-Za-z]",
    r"uses?\s+(?:the\s+)?(?:method|algorithm|technique|procedure)",
    r"based\s+on\s+(?:the\s+)?(?:method|algorithm|approach|technique)",
    r"applies?\s+(?:the\s+)?(?:method|algorithm|technique)",
    r"employs?\s+(?:the\s+)?(?:method|algorithm|technique)",
    r"implemented\s+(?:using|with|via)",
]

COMPARISON_PATTERNS = [
    r"превосходит",
    r"уступает",
    r"более\s+эффективно",
    r"по\s+сравнению\s+с",
    r"превосходит\s+(?:по|в)",
    r"outperforms",
    r"is\s+inferior\s+to",
    r"more\s+efficient\s+than",
    r"compared\s+(?:to|with)",
    r"better\s+than",
    r"worse\s+than",
    r"surpasses",
    r"exceeds",
]

RESULT_PATTERNS = [
    r"результаты\s+показывают",
    r"эксперимент\s+подтверждает",
    r"достигнута\s+(?:точност|эффективност|производительн)",
    r"получен(?:ы|ные)\s+результат",
    r"экспериментальн(?:ые|ых)\s+(?:результат|данные)",
    r"results?\s+(?:show|demonstrate|confirm|indicate)",
    r"experiment(?:s|al)?\s+(?:confirm|show|demonstrate)",
    r"achieved\s+(?:accuracy|performance|efficiency|precision)",
    r"experimental\s+(?:results?|data|evaluation)",
    r"our\s+(?:experiments?|evaluation|results?)\s+(?:show|confirm)",
]

COMMON_KNOWLEDGE_PATTERNS = [
    r"widely\s+used",
    r"well[- ]known",
    r"общеизвестно",
    r"broadly\s+accepted",
    r"является\s+(?:распространён|стандартн|классическ)",
    r"является\s+интерпретируемым",
    r"широко\s+признано",
    r"стандартный\s+подход",
    r"is\s+commonly\s+known",
    r"standard\s+(?:approach|practice|technique)",
]

CITATION_PATTERN = re.compile(
    r"\[\d+(?:[,\s\-–—]\d+)*\]"
    r"|(?:\((?:[A-ZА-ЯЁ][a-zа-яё]+(?:\s+(?:et\s+al\.?|и\s+др\.?))?)"
    r"(?:,?\s*\d{4}(?:[a-z]?)?(?:;\s*[A-ZА-ЯЁ][a-zа-яё]+\s*,?\s*\d{4})*)?\))",
    re.IGNORECASE,
)

# ─── Reason templates for claim types ──────────────────────────────────

REASON_TEMPLATES = {
    "gap_claim": (
        "该句描述了研究空白（research gap），属于gap_claim，"
        "需要引用相关文献来支撑空白的存在性论证"
    ),
    "evaluative_claim": (
        "该句包含评估性判断，属于evaluative_claim，"
        "需要引用基准文献或实验数据支撑"
    ),
    "theoretical_claim": (
        "该句涉及理论基础，属于theoretical_claim，"
        "需要引用理论来源或框架定义文献"
    ),
    "methodological_claim": (
        "该句描述方法论，属于methodological_claim，"
        "需要引用方法原始文献或方法论综述"
    ),
    "factual_claim": (
        "该句陈述事实性断言，属于factual_claim，"
        "需要引用权威来源支撑"
    ),
    "contribution_claim": (
        "该句陈述本文贡献，属于contribution_claim，"
        "需要引用相关对比工作以定位贡献"
    ),
    "descriptive_claim": (
        "该句为描述性陈述，属于descriptive_claim，"
        "通常不需要引用，除非涉及特定方法或数据"
    ),
    "common_knowledge": (
        "该句描述常识性内容，属于common_knowledge，"
        "不需要引用"
    ),
    "background_claim": (
        "该句描述了领域背景或现有方法现状，属于background_claim，"
        "需要引用综述或方法类文献支撑"
    ),
    "field_status_claim": (
        "该句描述了领域当前状态或发展趋势，属于field_status_claim，"
        "需要引用综述或最新进展类文献支撑"
    ),
    "method_claim": (
        "该句描述了具体方法或算法，属于method_claim，"
        "需要引用该方法的原始文献"
    ),
    "comparison_claim": (
        "该句包含方法对比或优劣判断，属于comparison_claim，"
        "需要引用对比实验或基准文献"
    ),
    "result_claim": (
        "该句陈述实验结果或结论，属于result_claim，"
        "需要引用实验数据或相关验证文献"
    ),
}

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
    "background_claim":   {"1-2": "medium",   "3-4": "medium",   "5-6": "low",      "7-8": "low"},
    "field_status_claim": {"1-2": "medium",   "3-4": "medium",   "5-6": "low",      "7-8": "low"},
    "method_claim":       {"1-2": "high",     "3-4": "critical", "5-6": "high",     "7-8": "medium"},
    "comparison_claim":   {"1-2": "medium",   "3-4": "high",     "5-6": "critical", "7-8": "high"},
    "result_claim":       {"1-2": "low",      "3-4": "medium",   "5-6": "critical", "7-8": "high"},
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
    "background_claim":   "background_context",
    "field_status_claim": "background_context",
    "method_claim":       "method_basis",
    "comparison_claim":   "benchmark",
    "result_claim":       "empirical_support",
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
    if _matches(lower, RESULT_PATTERNS):
        return "result_claim"
    if _matches(lower, COMPARISON_PATTERNS):
        return "comparison_claim"
    if _matches(lower, METHOD_PATTERNS):
        return "method_claim"
    if _matches(lower, FIELD_STATUS_PATTERNS):
        return "field_status_claim"
    if _matches(lower, BACKGROUND_PATTERNS):
        return "background_claim"
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
        "common_knowledge":   "not_needed",
        "background_claim":   "recommended",
        "field_status_claim": "recommended",
        "method_claim":       "required",
        "comparison_claim":   "required",
        "result_claim":       "required",
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
            # Inline citation exists, but we need actual literature records to confirm
            if literature is not None:
                gap_status, matched_ids = match_literature(sentence, literature)
                if gap_status != "covered":
                    gap_status = "partial"  # cited but can't verify from our literature
            else:
                gap_status = "partial"
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
        
        # INVARIANT: covered requires a real source ID
        if gap_status == "covered" and matched_source is None:
            gap_status = "partial"

        # Generate reason explanation
        reason = REASON_TEMPLATES.get(claim_type, "未分类的claim，建议人工审查引用需求")

        # Build claim object
        claim = {
            "claim_id": f"c{idx:03d}",
            "claim_text": sentence,
            "claim_type": claim_type,
            "citation_need": citation_need,
            "gap_status": gap_status,
            "recommended_evidence_role": evidence_role,
            "risk_level": risk,
            "reason": reason,
        }
        if matched_source is not None:
            claim["matched_source_id"] = matched_source
        else:
            claim["matched_source_id"] = None

        # Evidence strength heuristic (with source ID invariant)
        if gap_status == "covered" and matched_source is not None:
            claim["evidence_strength"] = "strong"
        elif gap_status == "covered" and matched_source is None:
            claim["evidence_strength"] = "medium"
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
    by_type = {}

    for c in claims:
        gs = c["gap_status"]
        by_gap[gs] = by_gap.get(gs, 0) + 1
        rl = c["risk_level"]
        by_risk[rl] = by_risk.get(rl, 0) + 1
        if c["citation_need"] in ("required", "recommended"):
            needs_citation += 1
        ct = c["claim_type"]
        by_type[ct] = by_type.get(ct, 0) + 1

    total = len(claims)
    resolved = by_gap["covered"] + by_gap["partial"] + by_gap["not_needed"]
    evidence_covered = by_gap["covered"]
    evidence_total = by_gap["covered"] + by_gap["partial"] + by_gap["missing"]

    overall_resolution_ratio = round(resolved / total, 4) if total > 0 else 0.0
    evidence_coverage_ratio = round(evidence_covered / evidence_total, 4) if evidence_total > 0 else 0.0
    citation_gap_ratio = round(needs_citation / total, 4) if total > 0 else 0.0

    return {
        "total_claims": total,
        "by_gap_status": by_gap,
        "by_risk_level": by_risk,
        "by_claim_type": by_type,
        "overall_resolution_ratio": overall_resolution_ratio,
        "evidence_coverage_ratio": evidence_coverage_ratio,
        "citation_gap_ratio": citation_gap_ratio,
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
    print(f"  Resolution ratio: {summary['overall_resolution_ratio']:.1%}", file=sys.stderr)
    print(f"  Evidence coverage: {summary['evidence_coverage_ratio']:.1%}", file=sys.stderr)
    print(f"  Citation gap ratio: {summary['citation_gap_ratio']:.1%}", file=sys.stderr)
    print(f"Output: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
