#!/usr/bin/env python3
"""
normalize_russian_metadata.py — Normalize raw Russian literature metadata records.

Accepts JSON array input from various platforms (eLIBRARY, CyberLeninka, DisserCat, RSL, Crossref, OpenAlex)
and produces a unified JSON array conforming to russian_literature_record.schema.json
or russian_dissertation_record.schema.json.

Usage:
    python3 scripts/normalize_russian_metadata.py --input raw.json --output normalized.json
    python3 scripts/normalize_russian_metadata.py --input raw.json --output normalized.json --validate

Pure standard library — no external dependencies.
"""

import argparse
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLATFORM_ALIASES = {
    "elibrary": "elibrary",
    "eLIBRARY": "elibrary",
    "rinc": "elibrary",
    "РИНЦ": "elibrary",
    "cyberleninka": "cyberleninka",
    "CyberLeninka": "cyberleninka",
    "crossref": "crossref",
    "Crossref": "crossref",
    "openalex": "openalex",
    "OpenAlex": "openalex",
    "dissercat": "dissercat",
    "DisserCat": "dissercat",
    "rsl": "rsl",
    "RSL": "rsl",
    "РГБ": "rsl",
    "manual": "manual",
}

PUB_TYPE_ALIASES = {
    "journal_article": "journal_article",
    "article": "journal_article",
    "статья": "journal_article",
    "conference_paper": "conference_paper",
    "conference": "conference_paper",
    "конференция": "conference_paper",
    "тезисы": "conference_paper",
    "monograph": "monograph",
    "монография": "monograph",
    "preprint": "preprint",
    "препринт": "preprint",
    "other": "other",
}

DEGREE_ALIASES = {
    "candidate": "candidate",
    "кандидат": "candidate",
    "кандидат наук": "candidate",
    "кандидатская": "candidate",
    "doctoral": "doctoral",
    "доктор": "doctoral",
    "доктор наук": "doctoral",
    "докторская": "doctoral",
    "abstract": "abstract",
    "автореферат": "abstract",
    "unknown": "unknown",
}

FULLTEXT_ALIASES = {
    "open": "open",
    "открытый": "open",
    "free": "open",
    "preview_only": "preview_only",
    "preview": "preview_only",
    "предпросмотр": "preview_only",
    "needs_payment": "needs_payment",
    "paid": "needs_payment",
    "needs_institution": "needs_institution",
    "restricted": "needs_institution",
    "unknown": "unknown",
}

# Discipline cluster mapping by VAK specialty code prefix
SPECIALTY_TO_CLUSTER = {
    "05.13": "AUTOMATION_CONTROL",
    "05.11": "AUTOMATION_CONTROL",
    "05.12": "AUTOMATION_CONTROL",
    "05.02": "SCI_TECH",
    "05.13.11": "SCI_TECH",
    "05.13.15": "SCI_TECH",
    "05.13.18": "SCI_TECH",
    "05.20": "AGRI_MED",
    "06.01": "AGRI_MED",
    "06.02": "AGRI_MED",
    "03.00": "AGRI_MED",
    "14.00": "AGRI_MED",
    "13.00": "ARTS_SPORTS",
    "17.00": "ARTS_SPORTS",
    "08.00": "HUM_POL_ECON",
    "22.00": "HUM_POL_ECON",
    "12.00": "HUM_POL_ECON",
    "10.00": "HUM_POL_ECON",
}

# Keyword-based fallback cluster detection
KEYWORD_TO_CLUSTER = {
    "автоматическ": "AUTOMATION_CONTROL",
    "управлени": "AUTOMATION_CONTROL",
    "системы управления": "AUTOMATION_CONTROL",
    "адаптивн": "AUTOMATION_CONTROL",
    "устойчивость": "AUTOMATION_CONTROL",
    "нейронн": "SCI_TECH",
    "информационн": "SCI_TECH",
    "программн": "SCI_TECH",
    "вычислительн": "SCI_TECH",
    "машинное обучение": "SCI_TECH",
    "сельскохозяйственн": "AGRI_MED",
    "медицинск": "AGRI_MED",
    "биомедицинск": "AGRI_MED",
    "физическ": "ARTS_SPORTS",
    "спортивн": "ARTS_SPORTS",
    "экономик": "HUM_POL_ECON",
    "социолог": "HUM_POL_ECON",
    "политолог": "HUM_POL_ECON",
    "менеджмент": "HUM_POL_ECON",
}

TITLE_SIMILARITY_THRESHOLD = 0.88


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr)


def detect_record_type(record):
    """Determine if a record is a literature or dissertation type."""
    # DisserCat/RSL with dissertation-specific fields
    platform = _norm_platform(record.get("platform", record.get("source_platform", "")))
    if platform in ("dissercat", "rsl"):
        return "dissertation"
    if record.get("degree") or record.get("degree_type"):
        return "dissertation"
    if record.get("specialty_code"):
        return "dissertation"
    if record.get("institution") and not record.get("journal"):
        # Has institution but no journal — likely dissertation
        if record.get("table_of_contents") is not None or record.get("intro_text") is not None:
            return "dissertation"
    return "literature"


def _norm_platform(raw):
    """Normalize platform string."""
    if not raw:
        return "manual"
    return PLATFORM_ALIASES.get(raw, raw.lower())


def _norm_pub_type(raw):
    if not raw:
        return "other"
    return PUB_TYPE_ALIASES.get(raw, raw.lower())


def _norm_degree(raw):
    if not raw:
        return "unknown"
    return DEGREE_ALIASES.get(raw, raw.lower())


def _norm_fulltext(raw):
    if not raw:
        return "unknown"
    return FULLTEXT_ALIASES.get(raw, raw.lower())


def _norm_authors(raw):
    """Normalize author field to list of strings."""
    if isinstance(raw, list):
        return [str(a).strip() for a in raw if a]
    if isinstance(raw, str):
        # Split on semicolons or commas (if multiple authors)
        parts = re.split(r'[;,]\s*', raw)
        return [p.strip() for p in parts if p.strip()]
    return []


def _map_specialty_to_cluster(code, keywords=None):
    """Map VAK specialty code to discipline cluster."""
    if code:
        # Try exact match first, then prefix
        for prefix in sorted(SPECIALTY_TO_CLUSTER.keys(), key=len, reverse=True):
            if code.startswith(prefix):
                return SPECIALTY_TO_CLUSTER[prefix]
    # Fallback: keyword-based
    if keywords:
        kw_text = " ".join(keywords).lower() if isinstance(keywords, list) else str(keywords).lower()
        for kw, cluster in KEYWORD_TO_CLUSTER.items():
            if kw in kw_text:
                return cluster
    return "UNCLASSIFIED"


def _generate_id(record, record_type):
    """Generate a unique ID for the record."""
    platform = _norm_platform(record.get("platform", record.get("source_platform", "")))
    # Try existing identifiers
    if record.get("elibrary_article_id"):
        return f"elibrary_{record['elibrary_article_id']}"
    if record.get("elibrary_id"):
        return f"elibrary_{record['elibrary_id']}"
    if record.get("doi"):
        return f"doi_{record['doi'].replace('/', '_')}"
    if record.get("rsl_id"):
        return f"rsl_{record['rsl_id']}"
    # Generate from title hash
    title = record.get("title", record.get("title_ru", ""))
    title_hash = str(abs(hash(title)) % 10**8)
    return f"{platform}_{title_hash}"


def _title_similarity(t1, t2):
    """Compute similarity between two titles (normalized)."""
    def norm(t):
        return re.sub(r'\s+', ' ', t.lower().strip())
    if not t1 or not t2:
        return 0.0
    return SequenceMatcher(None, norm(t1), norm(t2)).ratio()


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize_literature(record):
    """Normalize a raw record to russian_literature_record format."""
    platform = _norm_platform(record.get("platform", record.get("source_platform", "")))
    authors = _norm_authors(record.get("author_list", record.get("authors", [])))
    year = record.get("publication_year", record.get("year"))
    if year:
        year = int(year)

    raw_keywords = record.get("keywords", record.get("keywords_ru", []))
    if isinstance(raw_keywords, str):
        raw_keywords = [k.strip() for k in re.split(r'[;,]', raw_keywords) if k.strip()]

    specialty = record.get("specialty", record.get("specialty_code", ""))
    cluster = _map_specialty_to_cluster(specialty, raw_keywords)

    result = {
        "id": _generate_id(record, "literature"),
        "title_ru": record.get("title", record.get("title_ru", "")),
        "title_en": record.get("title_en"),
        "authors": authors,
        "year": year,
        "source_platform": platform,
        "publication_type": _norm_pub_type(record.get("type", record.get("publication_type", ""))),
        "journal": record.get("journal_name", record.get("journal", record.get("venue"))),
        "doi": record.get("doi"),
        "elibrary_id": str(record.get("elibrary_article_id", record.get("elibrary_id", record.get("elibrary_article_id_num", "")))) or None,
        "rinc_citation_count": record.get("citations_rinc", record.get("rinc_citation_count")),
        "keywords_ru": raw_keywords if isinstance(raw_keywords, list) else [],
        "abstract_ru": record.get("abstract", record.get("abstract_ru")),
        "full_text_status": _norm_fulltext(record.get("fulltext", record.get("full_text_status", record.get("access")))),
        "url": record.get("url"),
        "discipline_cluster": cluster,
        "evidence_role": record.get("evidence_role", []),
        "notes_for_writer": record.get("notes_for_writer"),
    }
    # Remove None values for optional fields, keep required
    return {k: v for k, v in result.items() if v is not None or k in ("id", "title_ru", "authors", "year", "source_platform", "publication_type")}


def normalize_dissertation(record):
    """Normalize a raw record to russian_dissertation_record format."""
    platform = _norm_platform(record.get("platform", record.get("source_platform", "")))
    year = record.get("year")
    if year:
        year = int(year)

    raw_keywords = record.get("keywords", record.get("keywords_ru", []))
    if isinstance(raw_keywords, str):
        raw_keywords = [k.strip() for k in re.split(r'[;,]', raw_keywords) if k.strip()]

    specialty_code = record.get("specialty_code", record.get("specialty", ""))
    cluster = _map_specialty_to_cluster(specialty_code, raw_keywords)

    result = {
        "id": _generate_id(record, "dissertation"),
        "title_ru": record.get("title", record.get("title_ru", "")),
        "author": record.get("author", ""),
        "year": year,
        "degree_type": _norm_degree(record.get("degree", record.get("degree_type", ""))),
        "specialty_code": specialty_code,
        "specialty_name": record.get("specialty_name"),
        "institution": record.get("institution"),
        "source_platform": platform,
        "dissercat_url": record.get("url", record.get("dissercat_url")),
        "rsl_id": record.get("rsl_id"),
        "toc_available": bool(record.get("table_of_contents", record.get("toc_available", False))),
        "intro_available": bool(record.get("intro_text", record.get("intro_available", False))),
        "bibliography_available": bool(record.get("bibliography", record.get("bibliography_available", False))),
        "chapter_count": record.get("chapter_count"),
        "page_count": record.get("page_count"),
        "keywords_ru": raw_keywords if isinstance(raw_keywords, list) else [],
        "abstract_ru": record.get("abstract_ru", record.get("abstract")),
        "full_text_status": _norm_fulltext(record.get("access", record.get("full_text_status", ""))),
        "discipline_cluster": cluster,
        "evidence_role": record.get("evidence_role", []),
        "related_papers": record.get("related_papers", []),
        "notes_for_writer": record.get("notes_for_writer"),
    }
    return {k: v for k, v in result.items() if v is not None or k in ("id", "title_ru", "author", "year", "degree_type", "specialty_code", "source_platform")}


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(records):
    """Remove duplicates based on DOI or title similarity."""
    seen_dois = {}
    unique = []
    dupes = 0

    for rec in records:
        doi = rec.get("doi")
        title = rec.get("title_ru", "")

        # DOI-based dedup
        if doi and doi in seen_dois:
            dupes += 1
            log(f"  [dedup] Duplicate DOI: {doi}")
            continue

        # Title similarity dedup
        is_dupe = False
        for existing in unique:
            existing_title = existing.get("title_ru", "")
            if _title_similarity(title, existing_title) >= TITLE_SIMILARITY_THRESHOLD:
                is_dupe = True
                dupes += 1
                log(f"  [dedup] Similar title: '{title[:50]}...' ≈ '{existing_title[:50]}...'")
                break

        if is_dupe:
            continue

        if doi:
            seen_dois[doi] = True
        unique.append(rec)

    return unique, dupes


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

SCHEMA_DIR = "assets/references/schemas"

LITERATURE_REQUIRED = {"id", "title_ru", "authors", "year", "source_platform", "publication_type"}
DISSERTATION_REQUIRED = {"id", "title_ru", "author", "year", "degree_type", "specialty_code", "source_platform"}

VALID_PLATFORMS_LIT = {"elibrary", "cyberleninka", "crossref", "openalex", "manual"}
VALID_PLATFORMS_DISS = {"dissercat", "rsl", "manual"}
VALID_PUB_TYPES = {"journal_article", "conference_paper", "monograph", "preprint", "other"}
VALID_DEGREE_TYPES = {"candidate", "doctoral", "abstract", "unknown"}
VALID_FULLTEXT = {"open", "preview_only", "needs_payment", "needs_institution", "unknown"}
VALID_CLUSTERS = {"AUTOMATION_CONTROL", "SCI_TECH", "AGRI_MED", "ARTS_SPORTS", "HUM_POL_ECON", "UNCLASSIFIED"}
VALID_EVIDENCE_LIT = {"background", "gap", "method", "validation", "comparison", "definition", "result"}
VALID_EVIDENCE_DISS = {"structure_reference", "method_reference", "literature_pool", "comparison_case", "citation_example"}


def validate_record(rec, rec_type):
    """Validate a normalized record against schema constraints. Returns list of errors."""
    errs = []
    if rec_type == "literature":
        required = LITERATURE_REQUIRED
        for field in required:
            if field not in rec or rec[field] is None:
                errs.append(f"Missing required field: {field}")
        if rec.get("source_platform") not in VALID_PLATFORMS_LIT:
            errs.append(f"Invalid source_platform: {rec.get('source_platform')}")
        if rec.get("publication_type") not in VALID_PUB_TYPES:
            errs.append(f"Invalid publication_type: {rec.get('publication_type')}")
        if rec.get("full_text_status") and rec["full_text_status"] not in VALID_FULLTEXT:
            errs.append(f"Invalid full_text_status: {rec['full_text_status']}")
    else:
        required = DISSERTATION_REQUIRED
        for field in required:
            if field not in rec or rec[field] is None:
                errs.append(f"Missing required field: {field}")
        if rec.get("source_platform") not in VALID_PLATFORMS_DISS:
            errs.append(f"Invalid source_platform: {rec.get('source_platform')}")
        if rec.get("degree_type") not in VALID_DEGREE_TYPES:
            errs.append(f"Invalid degree_type: {rec.get('degree_type')}")
        if rec.get("full_text_status") and rec["full_text_status"] not in VALID_FULLTEXT:
            errs.append(f"Invalid full_text_status: {rec['full_text_status']}")

    cluster = rec.get("discipline_cluster")
    if cluster and cluster not in VALID_CLUSTERS:
        errs.append(f"Invalid discipline_cluster: {cluster}")

    year = rec.get("year")
    if year is not None:
        if not isinstance(year, int) or year < 1990 or year > 2030:
            errs.append(f"Year out of range: {year}")

    return errs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Normalize raw Russian literature/dissertation metadata records."
    )
    parser.add_argument("--input", "-i", required=True, help="Input JSON file (array of raw records)")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file (normalized records)")
    parser.add_argument("--validate", action="store_true", help="Validate output against schema constraints")
    args = parser.parse_args()

    # Read input
    log(f"Reading input: {args.input}")
    with open(args.input, encoding="utf-8") as f:
        raw_records = json.load(f)

    if not isinstance(raw_records, list):
        log("ERROR: Input must be a JSON array")
        sys.exit(1)

    total = len(raw_records)
    log(f"Total raw records: {total}")

    # Classify and normalize
    normalized = []
    type_counts = Counter()
    platform_counts = Counter()
    error_counts = 0

    for i, raw in enumerate(raw_records):
        rec_type = detect_record_type(raw)
        type_counts[rec_type] += 1
        platform_counts[_norm_platform(raw.get("platform", raw.get("source_platform", "")))] += 1

        try:
            if rec_type == "dissertation":
                norm = normalize_dissertation(raw)
            else:
                norm = normalize_literature(raw)
            normalized.append((rec_type, norm))
        except Exception as ex:
            log(f"  [error] Record {i}: {ex}")
            error_counts += 1

    log(f"Normalized: {len(normalized)} records")
    log(f"  Types: {dict(type_counts)}")
    log(f"  Platforms: {dict(platform_counts)}")
    if error_counts:
        log(f"  Errors during normalization: {error_counts}")

    # Deduplicate
    norm_only = [r for _, r in normalized]
    deduped, dupe_count = deduplicate(norm_only)
    if dupe_count:
        log(f"Duplicates removed: {dupe_count}")

    # Validate if requested
    validation_errors = 0
    if args.validate:
        log("Validating output against schema constraints...")
        for rec in deduped:
            # Re-detect type from normalized structure
            if "author" in rec and "degree_type" in rec:
                errs = validate_record(rec, "dissertation")
            else:
                errs = validate_record(rec, "literature")
            if errs:
                validation_errors += len(errs)
                for e in errs:
                    log(f"  [validation] {rec.get('id', '?')}: {e}")
        log(f"Validation: {validation_errors} error(s)")

    # Write output
    log(f"Writing output: {args.output}")
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    # Summary to stderr
    log("")
    log("=" * 50)
    log("NORMALIZATION SUMMARY")
    log("=" * 50)
    log(f"  Input records:      {total}")
    log(f"  Output records:     {len(deduped)}")
    log(f"  Duplicates removed: {dupe_count}")
    log(f"  Errors:             {error_counts}")
    if args.validate:
        log(f"  Validation errors:  {validation_errors}")
    log("=" * 50)

    # Cluster distribution
    cluster_counts = Counter()
    for rec in deduped:
        cluster_counts[rec.get("discipline_cluster", "UNCLASSIFIED")] += 1
    log(f"  Cluster distribution: {dict(cluster_counts)}")

    if args.validate and validation_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
