#!/usr/bin/env python3
"""
extract_rhetorical_moves.py — Extract rhetorical move patterns from template data.

Groups discipline templates by (category, subtype), aggregates quality distributions,
and outputs rhetorical move records to .phd_build/rhetorical_moves.jsonl.

Usage:
    python3 scripts/extract_rhetorical_moves.py
    python3 scripts/extract_rhetorical_moves.py --discipline технические_науки
"""

import json, sys, argparse
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / ".phd_build"

VALID_CATEGORIES = {
    "INTRO", "SURVEY", "MODEL", "METHOD", "EXPERIMENT", "RESULT",
    "DISCUSSION", "CONCLUSION", "TRANSITION", "FORMAL_DEFS", "ENGINEERING",
}


def get_discipline_cluster(name: str) -> str:
    tech = ["техническ", "физик", "математи", "хими", "биологи",
            "медицин", "геологи", "географи", "фармацевт"]
    hum = ["филологи", "историческ", "философ", "экономи",
           "социологи", "педагоги", "психологи", "юриди",
           "политическ", "культуролог", "искусствовед"]
    for kw in tech:
        if kw in name.lower():
            return "TECH_LIFE"
    for kw in hum:
        if kw in name.lower():
            return "HUM_SOC"
    return "GLOBAL"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discipline", help="Filter by discipline name")
    parser.add_argument("--cluster", help="Filter by cluster")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(BASE.glob("assets/discipline/*.jsonl"))

    # Group by (category, subtype)
    groups = defaultdict(lambda: {
        "templates": [],
        "qualities": [],
        "when_to_use_set": set(),
        "common_mistakes_set": set(),
        "disciplines": set(),
    })

    for f in files:
        disc = f.stem
        if args.discipline and args.discipline not in disc:
            continue
        cl = get_discipline_cluster(disc)
        if args.cluster and args.cluster != cl:
            continue

        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except:
                    continue
                cat = d.get("category", "")
                if cat not in VALID_CATEGORIES:
                    continue
                sub = d.get("subtype", "unknown")
                key = (cat, sub)
                groups[key]["templates"].append(d.get("template", "")[:80])
                groups[key]["qualities"].append(d.get("quality_score", 1))
                groups[key]["disciplines"].add(disc)
                wtu = d.get("when_to_use", "")
                if wtu:
                    groups[key]["when_to_use_set"].add(wtu[:100])
                cm = d.get("common_mistakes", [])
                if isinstance(cm, list):
                    for m in cm[:3]:
                        if isinstance(m, str) and m.strip():
                            groups[key]["common_mistakes_set"].add(m[:100])

    moves = []
    move_id = 0

    for (cat, sub), data in sorted(groups.items()):
        move_id += 1
        qs = data["qualities"]
        q2 = sum(1 for q in qs if q == 2)
        q1 = sum(1 for q in qs if q == 1)
        q0 = sum(1 for q in qs if q == 0)
        clusters = {get_discipline_cluster(d) for d in data["disciplines"]}

        moves.append({
            "move_id": f"move_{move_id:04d}",
            "category": cat,
            "russian_category": sub,
            "rhetorical_function": sub,
            "typical_triggers": list(data["when_to_use_set"])[:5],
            "template_count": len(data["templates"]),
            "quality_distribution": {"Q2": q2, "Q1": q1, "Q0": q0},
            "when_to_use": next(iter(data["when_to_use_set"]), ""),
            "common_mistakes": list(data["common_mistakes_set"])[:5],
            "related_moves": [],
            "evidence_count": {
                "count": len(data["templates"]),
                "source": f"disciplines:{','.join(sorted(clusters)[:3])}",
                "confidence": "high" if len(data["templates"]) > 50 else "medium"
            }
        })

    out_path = OUT / "rhetorical_moves.jsonl"
    with open(out_path, "w") as f:
        for m in moves:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    print(f"✅ {len(moves)} rhetorical moves written to {out_path}")
    print(f"   Categories covered: {len(set(m['category'] for m in moves))}")
    print(f"   Total template instances: {sum(m['template_count'] for m in moves)}")


if __name__ == "__main__":
    main()
