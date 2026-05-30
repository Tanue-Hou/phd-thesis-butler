#!/usr/bin/env python3
"""
Deterministic template retrieval — DISCIPLINE → CLUSTER → GLOBAL → data fallback
True tiered fallback: only proceeds to next layer if current layer < K results.

Usage:
  python scripts/retrieve_templates.py \\
    --category MODEL \\
    --discipline "технические науки" \\
    --cluster TECH_LIFE \\
    --query "математическая модель допущение ограничения" \\
    --limit 5

Output: JSON array of matched templates with hit_layer and quality_score.
"""

import json, sys, re
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
    for field in ['template', 'text', 'when_to_use', 'function']:
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
    return bool(CYRILLIC_RE.search(t))

def load_quality_jsonl(path):
    """Load a JSONL file, return list of dicts, filtering CJK entries."""
    if not path.exists():
        return []
    result = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                # Filter out contaminated and non-Russian entries entirely.
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

def retrieve(args):
    category = args.get("category", "").upper()
    discipline = args.get("discipline", "технические науки")
    cluster = args.get("cluster", "TECH_LIFE").upper()
    query = args.get("query", "")
    limit = args.get("limit", 5)

    query_words = query.split() if query else []
    results = []  # list of (semantic_score, layer_name, entry)

    # Normalise discipline name
    disc_name = discipline.replace("_", " ").strip()
    disc_file = disc_name.replace(" ", "_")

    seen_templates = set()

    def try_add(entries, layer_name):
        """Add entries from a layer, deduplicating by template text."""
        for e in entries:
            if category and e.get("category", "").upper() != category:
                continue
            t = e.get("template", "") or e.get("text", "")
            if not t or t in seen_templates:
                continue
            seen_templates.add(t)
            score = semantic_score(t, query_words)
            results.append((score, layer_name, e))

    # --- L2: DISCIPLINE (primary) ---
    discipline_path = BASE / "assets/discipline" / f"{disc_file}.jsonl"
    disc_entries = load_quality_jsonl(discipline_path)
    try_add(disc_entries, "DISCIPLINE")

    # If DISCIPLINE already has >= limit results, stop here
    discipline_count = sum(1 for _, ln, _ in results if ln == "DISCIPLINE")
    if discipline_count >= limit:
        final = [r for r in results if r[1] == "DISCIPLINE"][:limit]
    else:
        # --- L1: CLUSTER (fallback) ---
        cluster_path = BASE / f"assets/cluster/{cluster}/quality/QUALITY2_{category}.jsonl"
        if not cluster_path.exists():
            cluster_path = BASE / f"assets/cluster/{cluster}/quality/QUALITY2_ALL.jsonl"
        cluster_entries = load_quality_jsonl(cluster_path)
        try_add(cluster_entries, "CLUSTER")

        cluster_count = sum(1 for _, ln, _ in results if ln == "CLUSTER")
        if discipline_count + cluster_count >= limit:
            # Take all DISCIPLINE + enough CLUSTER to reach limit
            disc_r = [r for r in results if r[1] == "DISCIPLINE"]
            clust_r = [r for r in results if r[1] == "CLUSTER"]
            needed = limit - len(disc_r)
            final = disc_r + clust_r[:needed]
        else:
            # --- L0: GLOBAL (deep fallback) ---
            global_path = BASE / f"assets/global/quality/QUALITY2_{category}.jsonl"
            if not global_path.exists():
                global_path = BASE / "assets/global/quality/QUALITY2_ALL.jsonl"
            global_entries = load_quality_jsonl(global_path)
            try_add(global_entries, "GLOBAL")

            disc_r = [r for r in results if r[1] == "DISCIPLINE"]
            clust_r = [r for r in results if r[1] == "CLUSTER"]
            glob_r = [r for r in results if r[1] == "GLOBAL"]
            needed = limit - len(disc_r) - len(clust_r)
            final = disc_r + clust_r + glob_r[:needed]

    # Sort within final list: quality_score desc, semantic_score desc
    final.sort(key=lambda r: (-r[2].get("quality_score", 0), -r[0]))

    # Format output — filter CJK one more time (belt and suspenders)
    output = []
    for score, layer_name, entry in final:
        t = entry.get("template", entry.get("text", ""))
        if entry_has_cjk(entry):
            continue
        output.append({
            "template": t,
            "category": entry.get("category", ""),
            "subtype": entry.get("subtype", ""),
            "when_to_use": entry.get("when_to_use", ""),
            "common_mistakes": entry.get("common_mistakes", []),
            "quality_score": entry.get("quality_score", 0),
            "hit_layer": layer_name,
        })

    return output[:limit]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Template retrieval with 3-layer fallback")
    parser.add_argument("--category", "-c", default="", help="Category to filter")
    parser.add_argument("--discipline", "-d", default="технические науки", help="Discipline name")
    parser.add_argument("--cluster", "-k", default="TECH_LIFE", help="Cluster name")
    parser.add_argument("--query", "-q", default="", help="Semantic query text")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Max results")
    args = parser.parse_args()

    params = {
        "category": args.category,
        "discipline": args.discipline,
        "cluster": args.cluster,
        "query": args.query,
        "limit": args.limit,
    }

    results = retrieve(params)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n--- {len(results)} results (limit={args.limit}) ---", file=sys.stderr)
