#!/usr/bin/env python3
"""
extract_logic_chains.py — Extract logic chain records from category co-occurrence.

Reads assets/discipline/*.jsonl to analyze which DIS categories appear together,
infers logic chains, and outputs to .phd_build/logic_chains.jsonl.

Usage:
    python3 scripts/extract_logic_chains.py
    python3 scripts/extract_logic_chains.py --discipline технические_науки
"""

import json, sys, argparse
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / ".phd_build"

CATEGORY_ORDER = [
    "INTRO", "SURVEY", "MODEL", "METHOD", "EXPERIMENT",
    "RESULT", "DISCUSSION", "CONCLUSION", "TRANSITION",
    "FORMAL_DEFS", "ENGINEERING",
]

CATEGORY_RU = {
    "INTRO": "Введение", "SURVEY": "Обзор литературы",
    "MODEL": "Модель", "METHOD": "Метод",
    "EXPERIMENT": "Эксперимент", "RESULT": "Результаты",
    "DISCUSSION": "Обсуждение", "CONCLUSION": "Заключение",
    "TRANSITION": "Переходы", "FORMAL_DEFS": "Определения",
    "ENGINEERING": "Инженерная реализация",
}


def get_discipline_cluster(discipline_name: str) -> str:
    """Rough cluster assignment based on discipline name keywords."""
    tech_keywords = ["техническ", "физик", "математи", "хими", "биологи",
                     "медицин", "геологи", "географи", "фармацевт"]
    hum_keywords = ["филологи", "историческ", "философ", "экономи",
                    "социологи", "педагоги", "психологи", "юриди",
                    "политическ", "культуролог", "искусствовед"]
    for kw in tech_keywords:
        if kw in discipline_name.lower():
            return "TECH_LIFE"
    for kw in hum_keywords:
        if kw in discipline_name.lower():
            return "HUM_SOC"
    return "GLOBAL"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discipline", help="Filter by discipline name")
    parser.add_argument("--cluster", help="Filter by cluster (TECH_LIFE/HUM_SOC)")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    discipline_files = sorted(BASE.glob("assets/discipline/*.jsonl"))

    chains = []
    chain_id = 0

    for f in discipline_files:
        disc_name = f.stem
        if args.discipline and args.discipline not in disc_name:
            continue
        cluster = get_discipline_cluster(disc_name)
        if args.cluster and args.cluster != cluster:
            continue

        # Read all templates, track which categories appear
        cats_seen = defaultdict(int)
        total = 0
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
                if cat in CATEGORY_ORDER:
                    cats_seen[cat] += 1
                total += 1

        if total == 0:
            continue

        chain_id += 1
        stages = []
        present_count = 0
        first_gap = None

        for cat in CATEGORY_ORDER:
            if cat in cats_seen:
                present_count += 1
                stages.append({
                    "stage_name": CATEGORY_RU.get(cat, cat),
                    "category": cat,
                    "required_subtypes": [],
                    "min_templates": cats_seen[cat],
                    "typical_transition_to_next": ""
                })
            elif first_gap is None:
                first_gap = cat

        score = round(present_count / len(CATEGORY_ORDER), 2)

        chain = {
            "chain_id": f"chain_{chain_id:04d}",
            "discipline": disc_name,
            "cluster": cluster,
            "stages": stages,
            "chain_completeness_score": score,
            "gap_category": first_gap if first_gap else None,
            "evidence_count": {
                "count": total,
                "source": f"discipline:{disc_name}",
                "confidence": "high" if total > 200 else ("medium" if total > 50 else "low")
            }
        }
        chains.append(chain)

    out_path = OUT / "logic_chains.jsonl"
    with open(out_path, "w") as f:
        for c in chains:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"✅ {len(chains)} logic chains written to {out_path}")
    print(f"   Disciplines: {[c['discipline'] for c in chains[:5]]}{'...' if len(chains)>5 else ''}")
    print(f"   Avg completeness: {sum(c['chain_completeness_score'] for c in chains)/len(chains):.2f}" if chains else "   No chains")


if __name__ == "__main__":
    main()
