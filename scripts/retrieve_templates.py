#!/usr/bin/env python3
"""
Deterministic template retrieval — DISCIPLINE → CLUSTER → GLOBAL → data fallback

Usage:
  python scripts/retrieve_templates.py \\
    --category MODEL \\
    --discipline "технические науки" \\
    --cluster TECH_LIFE \\
    --query "математическая модель допущение ограничения" \\
    --limit 5

Output: JSON array of matched templates with hit_layer and hit_quality.
"""

import json, sys, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

def load_jsonl(path):
    """Load a JSONL file, return list of dicts."""
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]

def semantic_score(template_text, query_words):
    """Simple semantic relevance score based on word overlap."""
    if not template_text or not query_words:
        return 0
    text_lower = template_text.lower()
    # Score: exact word match = 2, substring match = 1
    score = 0
    for qw in query_words:
        qw = qw.lower().strip('.,;:!?()[]{}"\'')
        if not qw or len(qw) < 3:
            continue
        if qw in text_lower:
            # Check if it appears as a whole word
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
    results = []
    hit_layers = []

    # Normalise discipline name: underscores → spaces
    disc_name = discipline.replace("_", " ").strip()
    # Also try with underscores for filename
    disc_file = disc_name.replace(" ", "_")

    # --- L2: DISCIPLINE ---
    discipline_path = BASE / "assets/discipline" / f"{disc_file}.jsonl"
    entries = load_jsonl(discipline_path)
    for e in entries:
        if e.get("category", "").upper() == category or not category:
            score = semantic_score(e.get("template", ""), query_words)
            results.append((score, 2, "DISCIPLINE", e))

    # --- L1: CLUSTER ---
    cluster_path = BASE / f"assets/cluster/{cluster}/quality/QUALITY2_{category}.jsonl"
    if not cluster_path.exists():
        # Try quality master
        cluster_path = BASE / f"assets/cluster/{cluster}/quality/QUALITY2_ALL.jsonl"
    entries = load_jsonl(cluster_path)
    for e in entries:
        if e.get("category", "").upper() == category or not category:
            t = e.get("template", "")
            if not any(t == r[3].get("template", "") for _, _, _, r in results):  # dedup
                score = semantic_score(t, query_words)
                results.append((score, 1, "CLUSTER", e))

    # --- L0: GLOBAL ---
    global_path = BASE / f"assets/global/quality/QUALITY2_{category}.jsonl"
    if not global_path.exists():
        global_path = BASE / "assets/global/quality/QUALITY2_ALL.jsonl"
    entries = load_jsonl(global_path)
    for e in entries:
        if e.get("category", "").upper() == category or not category:
            t = e.get("template", "")
            if not any(t == r[3].get("template", "") for _, _, _, r in results):
                score = semantic_score(t, query_words)
                results.append((score, 0, "GLOBAL", e))

    # Sort: quality_score desc → semantic_score desc
    results.sort(key=lambda r: (-r[3].get("quality_score", 0), -r[0]))

    # Take top N
    top = results[:limit]

    # Format output
    output = []
    for score, layer_priority, layer_name, entry in top:
        output.append({
            "template": entry.get("template", ""),
            "category": entry.get("category", ""),
            "subtype": entry.get("subtype", ""),
            "when_to_use": entry.get("when_to_use", ""),
            "common_mistakes": entry.get("common_mistakes", []),
            "quality_score": entry.get("quality_score", 0),
            "hit_layer": layer_name,
        })

    return output

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Template retrieval with 3-layer fallback")
    parser.add_argument("--category", "-c", default="", help="Category to filter (e.g. MODEL, INTRO)")
    parser.add_argument("--discipline", "-d", default="технические науки", help="Discipline name")
    parser.add_argument("--cluster", "-k", default="TECH_LIFE", help="Cluster name (TECH_LIFE/HUM_SOC)")
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
