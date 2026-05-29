#!/usr/bin/env python3
"""
Retriever Agent — 3层回退链 + quality优先模板检索
"""

import json, os, sys, re
from pathlib import Path

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")

# Asset paths by layer
ASSET_PATHS = {
    "GLOBAL": BASE / "assets/global",
    "CLUSTER": BASE / "assets/cluster",
    "DISCIPLINE": BASE / "assets/discipline",
}


def retrieve(plan_json):
    """Execute retrieval plan with fallback chain"""
    query = plan_json.get("plan", [{}])[0].get("query", {})
    fallback_chain = plan_json.get("plan", [{}])[0].get("fallback_chain", [])
    category = query.get("category", "INTRO")
    subtype = query.get("subtype", "")
    need_utils = query.get("need_utils", [])
    disc_info = plan_json.get("discipline_inference", {})
    discipline = disc_info.get("discipline", "ENGINEERING")
    cluster = disc_info.get("cluster", "TECH_LIFE")

    hits = []
    seen_ids = set()

    for chain_link in fallback_chain:
        # Parse chain link: LAYER(identifier).QUALITY
        parts = chain_link.split(".")
        layer_with_id = parts[0]
        quality = parts[1] if len(parts) > 1 else "QUALITY2"

        if "(" in layer_with_id:
            layer, layer_id = layer_with_id.split("(")
            layer_id = layer_id.rstrip(")")
        else:
            layer = layer_with_id
            layer_id = ""

        # Determine quality filter
        q_filter = 2 if "2" in quality else 1

        # Determine search paths
        search_paths = []
        if layer == "DISCIPLINE" and layer_id:
            search_paths.append(ASSET_PATHS["DISCIPLINE"] / layer_id)
        elif layer == "CLUSTER" and layer_id:
            search_paths.append(ASSET_PATHS["CLUSTER"] / layer_id)
        elif layer == "GLOBAL":
            search_paths.append(ASSET_PATHS["GLOBAL"])

        # Search in quality first, then master
        for sp in search_paths:
            q_file = sp / "quality" / f"QUALITY2_{category}.jsonl"
            if not q_file.exists():
                q_file = sp / "quality" / f"QUALITY2.jsonl"

            if q_file.exists():
                new_hits = _search_jsonl(q_file, category, subtype, q_filter, seen_ids)
                hits.extend(new_hits)

            # If quality yields < 3, fallback to master
            if len([h for h in hits if h["layer"] == layer]) < 3:
                m_file = sp / "master" / f"MASTER_{category}.jsonl"
                if not m_file.exists():
                    m_file = sp / "master" / "MASTER.jsonl"
                if m_file.exists():
                    new_hits = _search_jsonl(m_file, category, subtype, q_filter, seen_ids)
                    hits.extend(new_hits)

        # If we have enough hits, stop
        cat_hits = [h for h in hits if h["category"] == category]
        if len(cat_hits) >= 3:
            break

    # Also search for UTIL templates
    util_hits = []
    for util_type in need_utils:
        for sp in [ASSET_PATHS["GLOBAL"]]:
            u_file = sp / "quality" / f"UTILS.jsonl"
            if u_file.exists():
                uh = _search_jsonl(u_file, util_type, "", 2, seen_ids, is_util=True)
                util_hits.extend(uh)

    return {
        "templates": hits[:5],
        "utils": util_hits[:3],
        "count": len(hits),
        "fallback_used": len(hits),
    }


def _search_jsonl(filepath, category, subtype, q_filter, seen_ids, is_util=False):
    """Search a JSONL file for matching templates"""
    hits = []
    try:
        with open(filepath) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    eid = entry.get("id", entry.get("template_id", ""))
                    if eid in seen_ids:
                        continue

                    qs = entry.get("quality_score", 0)
                    if qs < q_filter:
                        continue

                    if is_util:
                        kind = entry.get("kind", "")
                        if kind == category or category in kind.split(","):
                            seen_ids.add(eid)
                            hits.append({
                                "layer": "UTIL",
                                "kind": kind,
                                "template": entry.get("template", entry.get("text", "")),
                                "when_to_use": entry.get("when_to_use", ""),
                                "quality_score": qs,
                            })
                        continue

                    if not is_util:
                        entry_cat = entry.get("category", "")
                        entry_sub = entry.get("subtype", "")

                        if entry_cat != category:
                            continue
                        if subtype and entry_sub != subtype:
                            continue

                        seen_ids.add(eid)
                        hits.append({
                            "layer": entry.get("layer", "DISCIPLINE"),
                            "category": entry_cat,
                            "subtype": entry_sub,
                            "template": entry.get("template", entry.get("text", "")),
                            "when_to_use": entry.get("when_to_use", ""),
                            "common_mistakes": entry.get("common_mistakes", []),
                            "quality_score": qs,
                            "strength": entry.get("strength", "neutral"),
                        })
                except:
                    continue
    except FileNotFoundError:
        pass
    return hits


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", help="Path to Router plan JSON")
    parser.add_argument("--output", "-o", default="/dev/stdout")
    args = parser.parse_args()

    with open(args.plan) as f:
        plan = json.load(f)

    result = retrieve(plan)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Retrieved {result['count']} templates + {len(result['utils'])} utils")
