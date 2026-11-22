#!/usr/bin/env python3
"""Retrieve Russian templates by discipline, cluster and global fallback.

Use --category and --query to search, or omit --query to browse by quality.
Stdout contains a JSON array, including the layer and reason for each hit.
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# CJK detection
CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
CJK_PUNCT_RE = re.compile(r'[，。；：！？、（）【】《》]')
CYRILLIC_RE = re.compile(r'[А-Яа-яЁё]')

def has_cjk(text):
    """Check if text contains CJK characters."""
    if not text:
        return False
    if isinstance(text, list):
        return any(has_cjk(item) for item in text)
    if isinstance(text, str):
        return bool(CJK_RE.search(text))
    return False

def has_cjk_punctuation(text):
    """Check if text contains Chinese/Japanese punctuation placeholders."""
    if not text:
        return False
    if isinstance(text, list):
        return any(has_cjk_punctuation(item) for item in text)
    if isinstance(text, str):
        return bool(CJK_PUNCT_RE.search(text))
    return False

def entry_has_cjk(entry):
    """Check if an entry has CJK or Chinese punctuation in visible text fields."""
    for field in ['template', 'text', 'subtype', 'when_to_use', 'function', 'slots']:
        if has_cjk(entry.get(field, '')) or has_cjk_punctuation(entry.get(field, '')):
            return True
    cm = entry.get('common_mistakes', [])
    if isinstance(cm, list) and (has_cjk(cm) or has_cjk_punctuation(cm)):
        return True
    if isinstance(cm, str) and (has_cjk(cm) or has_cjk_punctuation(cm)):
        return True
    return False

def has_russian_template(entry):
    """Russian dissertation templates should contain Cyrillic in the template text."""
    t = entry.get("template", "") or entry.get("text", "")
    return isinstance(t, str) and bool(CYRILLIC_RE.search(t))

PLACEHOLDER_MARKERS = (
    "требуется ручной перевод",
    "китайском языке удалено",
    "Описание требует уточнения",
)

def clean_visible_metadata(value):
    """Hide cleanup placeholders from user-facing retrieval output."""
    if isinstance(value, str):
        if any(marker in value for marker in PLACEHOLDER_MARKERS):
            return ""
        return value
    if isinstance(value, list):
        return [
            item for item in (clean_visible_metadata(v) for v in value)
            if item
        ]
    return value

def load_quality_jsonl(path, include_mixed=False):
    """Load a JSONL file, returning only runtime-safe entries by default."""
    if not path.exists():
        return []
    result = []
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if not isinstance(e, dict):
                    continue
                # Normal retrieval is Russian-first. Mixed/non-Russian templates
                # are retained in the assets for auditability, but hidden unless
                # the caller explicitly opts in.
                v5_lang = e.get('v5_lang', 'ru')
                if v5_lang == 'mixed' and not include_mixed:
                    continue
                if entry_has_cjk(e) or not has_russian_template(e):
                    continue
                result.append(e)
            except json.JSONDecodeError:
                continue
    return result

def semantic_score(template_text, query_words):
    """Simple semantic relevance score based on word overlap."""
    if not template_text or not query_words:
        return 0
    text_lower = template_text.lower()
    score = 0
    for qw in query_words:
        qw = qw.lower().strip('.,;:!?()[]{}"\'')
        if not qw or len(qw) < 3:
            continue
        if qw in text_lower:
            if re.search(r'\b' + re.escape(qw) + r'\b', text_lower):
                score += 2
            else:
                score += 1
    return score

def cluster_label(entry):
    """Return a normalized record label. The directory is only a storage shard."""
    label = entry.get("v5_cluster")
    if label is None:
        return ""
    if not isinstance(label, str):
        return None
    label = label.strip().upper()
    return "ARTS_SPORTS" if label == "ART_SPORT" else label


def quality_entries(directory, category, include_mixed):
    """Use the category shard or aggregate. Some installations only ship shards."""
    # An ALL file may contain only a subset. Include matching shards as well.
    aggregate = directory / "QUALITY2_ALL.jsonl"
    if category:
        shard = directory / f"QUALITY2_{category}.jsonl"
        paths = [p for p in dict.fromkeys((shard, aggregate)) if p.is_file()]
    else:
        paths = sorted(directory.glob("QUALITY2_*.jsonl"))
    for path in paths:
        yield from load_quality_jsonl(path, include_mixed)


def retrieve(args):
    category = args.get("category", "").strip().upper()
    discipline = "_".join(args.get("discipline", "").replace("_", " ").split())
    cluster = args.get("cluster", "TECH_LIFE").strip().upper()
    query = args.get("query", "").strip()
    limit = args.get("limit", 5)
    include_mixed = args.get("include_mixed", False)
    if limit <= 0 or any(sep in category for sep in ("/", '\\')):
        return []

    assets = BASE / "assets"
    mapping_path = assets / "references" / "cluster_mapping.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    canonical = set(mapping["canonical_labels"])
    aliases = mapping["legacy_aliases"]
    if cluster == "GLOBAL":
        allowed = canonical | {"GLOBAL"}
    elif cluster in canonical:
        allowed = {cluster}
    elif cluster in aliases:
        allowed = set(aliases[cluster])
    elif cluster == "UNKNOWN":
        allowed = set()
    else:
        raise ValueError(f"Unknown or ambiguous cluster {cluster!r}; choose a canonical label or GLOBAL")
    query_words = query.split()
    query_has_cyrillic = bool(CYRILLIC_RE.search(query))
    seen = set()
    output = []

    def append_hits(entries, layer, reason, labels=None):
        candidates = []
        for entry in entries:
            if category and str(entry.get("category", "")).upper() != category:
                continue
            label = cluster_label(entry)
            if labels is not None and label not in labels:
                continue
            template = entry.get("template") or entry.get("text", "")
            score = semantic_score(template, query_words)
            if query and not score:
                continue
            if include_mixed and query and not query_has_cyrillic and layer == "GLOBAL" and entry.get("v5_lang") == "mixed":
                score += 5
            candidates.append((score, entry, template, label))

        candidates.sort(key=lambda item: (-item[0], -item[1].get("quality_score", 0)))
        for _, entry, template, label in candidates:
            if template.strip() in seen:
                continue
            seen.add(template.strip())
            output.append({
                "template": template,
                "category": entry.get("category", ""),
                "subtype": entry.get("subtype", ""),
                "when_to_use": clean_visible_metadata(entry.get("when_to_use", "")),
                "common_mistakes": clean_visible_metadata(entry.get("common_mistakes", [])),
                "quality_score": entry.get("quality_score", 0),
                "hit_layer": layer,
                "hit_reason": reason,
                "v5_cluster": label or None,
                "classification_status": "unverified_source_label",
                "requested_cluster": cluster,
                "resolved_labels": sorted(labels if labels is not None else allowed),
                "alias_resolution": "legacy_lossy_mapping" if cluster in aliases else "explicit_scope",
                "lexical_score": semantic_score(template, query_words),
            })
            if len(output) == limit:
                return True
        return False

    if discipline and all(sep not in discipline for sep in ("/", '\\')):
        entries = load_quality_jsonl(assets / "discipline" / f"{discipline}.jsonl", include_mixed)
        if append_hits(entries, "DISCIPLINE", "discipline_file"):
            return output

    if allowed:
        entries = (
            entry for directory in sorted((assets / "cluster").glob("*/quality"))
            for entry in quality_entries(directory, category, include_mixed)
        )
        reason = "legacy_cluster_label" if cluster in aliases else "cluster_label"
        if append_hits(entries, "CLUSTER", reason, allowed):
            return output

    global_rows = list(quality_entries(assets / "global" / "quality", category, include_mixed))
    if allowed and append_hits(global_rows, "GLOBAL", "global_label", allowed):
        return output
    if cluster != "GLOBAL":
        append_hits(global_rows, "GLOBAL", "global_fallback", {"GLOBAL"})
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Template retrieval with 3-layer fallback")
    parser.add_argument("--category", "-c", default="", help="Category to filter")
    parser.add_argument("--discipline", "-d", default="", help="Optional discipline name for local assets")
    parser.add_argument("--cluster", "-k", default="TECH_LIFE", help="Cluster name")
    parser.add_argument("--query", "-q", default="", help="Semantic query text")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Max results")
    parser.add_argument("--include-mixed", action="store_true", help="Include mixed/non-Russian templates for audit/debug use")
    args = parser.parse_args()

    params = {
        "category": args.category,
        "discipline": args.discipline,
        "cluster": args.cluster,
        "query": args.query,
        "limit": args.limit,
        "include_mixed": args.include_mixed,
    }

    results = retrieve(params)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n--- {len(results)} results (limit={args.limit}) ---", file=sys.stderr)
