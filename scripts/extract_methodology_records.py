#!/usr/bin/env python3
"""
extract_methodology_records.py — Extract methodology routes from discipline JSONL data.

Reads assets/discipline/*.jsonl to discover category sequencing patterns per discipline.
For each discipline, determines:
  - typical approach_type (theoretical/experimental/simulation/hybrid/field_study/comparative)
  - typical_sections order (which DIS categories appear in sequence)
  - common_chapter_structure with section_name + purpose_ru
Outputs records matching methodology_record.schema.json format.

Usage:
    python extract_methodology_records.py [--discipline NAME] [--cluster NAME]

Options:
    --discipline   Filter to a single discipline (Russian name, e.g. "педагогические науки")
    --cluster      Filter to a cluster (TECH_LIFE / HUM_SOC / ART_SPORT / MATH_PHYS / GLOBAL)

Output: .phd_build/methodology_records.jsonl
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DISCIPLINE_DIR = BASE / "assets" / "discipline"
BUILD_DIR = BASE / ".phd_build"
OUTPUT_PATH = BUILD_DIR / "methodology_records.jsonl"

# Canonical DIS category order for typical_sections
DIS_CATEGORIES = [
    "INTRO", "SURVEY", "MODEL", "METHOD", "EXPERIMENT",
    "RESULT", "DISCUSSION", "CONCLUSION", "TRANSITION",
    "FORMAL_DEFS", "ENGINEERING", "AREF", "UTILS",
]

# Russian AREF categories that map to DIS categories
AREF_TO_DIS = {
    "АКТУАЛЬНОСТЬ": "INTRO",
    "НОВИЗНА": "RESULT",
    "ЦЕЛЬ_ЗАДАЧИ": "INTRO",
    "МЕТОДЫ": "METHOD",
    "ОБЪЕКТ_ПРЕДМЕТ": "INTRO",
    "ПОЛОЖЕНИЯ": "RESULT",
    "ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ": "DISCUSSION",
    "ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ": "DISCUSSION",
    "АПРОБАЦИЯ": "EXPERIMENT",
    "ВЫВОДЫ": "CONCLUSION",
    "ПЕРСПЕКТИВЫ": "CONCLUSION",
    "СТЕПЕНЬ_РАЗРАБОТАННОСТИ": "SURVEY",
    "ДОСТОВЕРНОСТЬ": "RESULT",
}

# Discipline-to-cluster heuristic mapping
CLUSTER_MAP = {
    "физико-математические науки": "MATH_PHYS",
    "физико-математических наук": "MATH_PHYS",
    "математических наук": "MATH_PHYS",
    "физических наук": "MATH_PHYS",
    "информационных технологий": "TECH_LIFE",
    "информатика": "TECH_LIFE",
    "технические науки": "TECH_LIFE",
    "технических наук": "TECH_LIFE",
    "медицинские науки": "TECH_LIFE",
    "медицинских наук": "TECH_LIFE",
    "биологические науки": "TECH_LIFE",
    "биологических наук": "TECH_LIFE",
    "химические науки": "TECH_LIFE",
    "химических наук": "TECH_LIFE",
    "сельскохозяйственных наук": "TECH_LIFE",
    "ветеринарных наук": "TECH_LIFE",
    "фармацевтических наук": "TECH_LIFE",
    "геолого-минералогические науки": "TECH_LIFE",
    "географических наук": "TECH_LIFE",
    "географические науки": "TECH_LIFE",
    "педагогические науки": "HUM_SOC",
    "педагогических наук": "HUM_SOC",
    "психологические науки": "HUM_SOC",
    "психологических наук": "HUM_SOC",
    "юридические науки": "HUM_SOC",
    "юридических наук": "HUM_SOC",
    "экономические науки": "HUM_SOC",
    "экономических наук": "HUM_SOC",
    "социологические науки": "HUM_SOC",
    "социологических наук": "HUM_SOC",
    "политические науки": "HUM_SOC",
    "политических наук": "HUM_SOC",
    "философские науки": "HUM_SOC",
    "философских наук": "HUM_SOC",
    "исторические науки": "HUM_SOC",
    "исторических наук": "HUM_SOC",
    "филологические науки": "HUM_SOC",
    "филологических наук": "HUM_SOC",
    "искусствоведение": "ART_SPORT",
    "другие науки": "GLOBAL",
    "engineering": "TECH_LIFE",
}

# Approach type heuristics based on dominant categories
APPROACH_RULES = {
    "experimental": lambda cats: cats.get("EXPERIMENT", 0) > cats.get("MODEL", 0)
    and cats.get("EXPERIMENT", 0) > 0,
    "simulation": lambda cats: cats.get("MODEL", 0) > 0
    and cats.get("METHOD", 0) > 0
    and cats.get("EXPERIMENT", 0) == 0,
    "theoretical": lambda cats: cats.get("MODEL", 0) > 0
    and cats.get("EXPERIMENT", 0) == 0
    and cats.get("FORMAL_DEFS", 0) > 0,
    "comparative": lambda cats: cats.get("SURVEY", 0) > cats.get("MODEL", 0)
    and cats.get("EXPERIMENT", 0) == 0
    and cats.get("DISCUSSION", 0) > 0,
    "field_study": lambda cats: cats.get("EXPERIMENT", 0) > 0
    and cats.get("MODEL", 0) == 0
    and cats.get("METHOD", 0) > 0,
}

# Russian purpose descriptions per DIS category
SECTION_PURPOSES = {
    "INTRO": ("Введение", "Обоснование актуальности, формулирование цели и задач исследования"),
    "SURVEY": ("Обзор литературы", "Систематизация существующих подходов и выявление пробелов"),
    "MODEL": ("Моделирование", "Описание разработанной модели или теоретической основы"),
    "METHOD": ("Методы исследования", "Описание методики, инструментов и процедур исследования"),
    "EXPERIMENT": ("Эксперимент", "Постановка и проведение экспериментальной проверки"),
    "RESULT": ("Результаты", "Представление и анализ полученных результатов"),
    "DISCUSSION": ("Обсуждение", "Интерпретация результатов и сравнение с существующими данными"),
    "CONCLUSION": ("Заключение", "Формулирование выводов и перспектив дальнейших исследований"),
    "TRANSITION": ("Переходы", "Логические мосты между разделами работы"),
    "FORMAL_DEFS": ("Формальные определения", "Введение терминологии, обозначений и формализация задачи"),
    "ENGINEERING": ("Инженерные решения", "Описание архитектуры, реализации и технических решений"),
}


def normalize_category(cat: str) -> str:
    """Map AREF categories to DIS categories; pass through DIS categories."""
    if cat in AREF_TO_DIS:
        return AREF_TO_DIS[cat]
    if cat in DIS_CATEGORIES:
        return cat
    return "INTRO"  # fallback


def get_cluster(discipline_name: str, _layer: str = "") -> str:
    """Determine cluster from discipline name or _layer field."""
    if _layer and _layer in ("TECH_LIFE", "HUM_SOC", "ART_SPORT", "MATH_PHYS", "GLOBAL"):
        return _layer
    # Try matching discipline name
    name_lower = discipline_name.lower().strip()
    for key, cluster in CLUSTER_MAP.items():
        if key in name_lower:
            return cluster
    return "GLOBAL"


def classify_approach(cat_counts: Counter) -> str:
    """Classify approach type based on category distribution."""
    for approach, rule in APPROACH_RULES.items():
        if rule(cat_counts):
            return approach
    # Default: if has any MODEL, theoretical; otherwise hybrid
    if cat_counts.get("MODEL", 0) > 0:
        return "theoretical"
    if cat_counts.get("INTRO", 0) > 0 and cat_counts.get("CONCLUSION", 0) > 0:
        return "hybrid"
    return "theoretical"


def build_common_chapter_structure(typical_sections: list) -> list:
    """Build common_chapter_structure from typical_sections."""
    structure = []
    for section in typical_sections:
        if section in SECTION_PURPOSES:
            name, purpose = SECTION_PURPOSES[section]
            structure.append({"section_name": name, "purpose_ru": purpose})
    return structure


def load_discipline_templates(discipline_file: Path) -> list:
    """Load all templates from a discipline JSONL file."""
    templates = []
    with open(discipline_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                templates.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return templates


def extract_methodology_for_discipline(
    discipline_name: str,
    templates: list,
    cluster: str,
    record_idx: int,
) -> dict:
    """Extract a methodology record for a single discipline."""
    # Count categories
    cat_counts: Counter = Counter()
    category_occurrences: dict[str, int] = defaultdict(int)
    pdf_categories: dict[str, set] = defaultdict(set)  # pdf_id -> categories

    for t in templates:
        raw_cat = t.get("category", "INTRO")
        dis_cat = normalize_category(raw_cat)
        cat_counts[dis_cat] += 1
        category_occurrences[dis_cat] += 1
        pdf_id = t.get("pdf_id", "unknown")
        pdf_categories[pdf_id].add(dis_cat)

    # Determine typical_sections: categories that appear in >20% of papers
    total_papers = max(len(pdf_categories), 1)
    category_paper_ratio = {}
    for cat in DIS_CATEGORIES:
        papers_with_cat = sum(1 for cats in pdf_categories.values() if cat in cats)
        category_paper_ratio[cat] = papers_with_cat / total_papers

    # Include categories that appear in >15% of papers
    present_cats = [
        cat for cat in DIS_CATEGORIES
        if category_paper_ratio.get(cat, 0) > 0.15 and cat_counts.get(cat, 0) > 0
    ]

    # Ensure INTRO and CONCLUSION are always present
    if "INTRO" not in present_cats:
        present_cats.insert(0, "INTRO")
    if "CONCLUSION" not in present_cats:
        present_cats.append("CONCLUSION")

    # Sort by canonical order
    typical_sections = [cat for cat in DIS_CATEGORIES if cat in set(present_cats)]

    # If too few sections, add minimum viable sequence
    if len(typical_sections) < 4:
        for fallback in ["INTRO", "SURVEY", "METHOD", "CONCLUSION"]:
            if fallback not in typical_sections:
                typical_sections.append(fallback)
        typical_sections = [cat for cat in DIS_CATEGORIES if cat in set(typical_sections)]

    # Classify approach type
    approach_type = classify_approach(cat_counts)

    # Determine requirements
    section_set = set(typical_sections)
    requires_model = "MODEL" in section_set or "FORMAL_DEFS" in section_set
    requires_experiment = "EXPERIMENT" in section_set
    requires_dataset = (
        "EXPERIMENT" in section_set
        or cat_counts.get("METHOD", 0) > cat_counts.get("MODEL", 0)
    )

    # Build chapter structure
    common_chapter_structure = build_common_chapter_structure(typical_sections)

    # Evidence count
    evidence_count = {
        "count": len(templates),
        "source": f"discipline/{discipline_name}",
        "confidence": (
            "high" if len(templates) >= 30
            else "medium" if len(templates) >= 10
            else "low"
        ),
    }

    # Build name_ru
    name_ru_map = {
        "theoretical": "Теоретико-аналитический подход",
        "experimental": "Экспериментальное исследование",
        "simulation": "Имитационное моделирование",
        "hybrid": "Комбинированный подход",
        "field_study": "Полевое исследование",
        "comparative": "Сравнительное исследование",
    }
    name_ru = f"{name_ru_map.get(approach_type, 'Методологический маршрут')} ({discipline_name})"

    record = {
        "methodology_id": f"methodology_{record_idx:04d}",
        "name_ru": name_ru,
        "discipline": discipline_name,
        "cluster": cluster,
        "approach_type": approach_type,
        "requires_model": requires_model,
        "requires_experiment": requires_experiment,
        "requires_dataset": requires_dataset,
        "typical_sections": typical_sections,
        "common_chapter_structure": common_chapter_structure,
        "evidence_count": evidence_count,
        "source": f"assets/discipline/{discipline_name}",
    }
    return record


def main():
    parser = argparse.ArgumentParser(
        description="Extract methodology records from discipline JSONL files."
    )
    parser.add_argument("--discipline", type=str, default=None,
                        help="Filter to a single discipline name (Russian)")
    parser.add_argument("--cluster", type=str, default=None,
                        help="Filter to a cluster (TECH_LIFE / HUM_SOC / ART_SPORT / MATH_PHYS / GLOBAL)")
    args = parser.parse_args()

    if not DISCIPLINE_DIR.is_dir():
        print(f"ERROR: {DISCIPLINE_DIR} not found")
        sys.exit(1)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Collect discipline files
    discipline_files = sorted(DISCIPLINE_DIR.glob("*.jsonl"))
    if not discipline_files:
        print("ERROR: No .jsonl files found in assets/discipline/")
        sys.exit(1)

    print(f"Found {len(discipline_files)} discipline files")

    records = []
    idx = 0

    for df in discipline_files:
        discipline_name = df.stem  # filename without extension

        # Apply --discipline filter
        if args.discipline and args.discipline.lower() not in discipline_name.lower():
            continue

        templates = load_discipline_templates(df)
        if not templates:
            continue

        # Determine cluster from first template's _layer field, or from name
        _layer = templates[0].get("_layer", "")
        cluster = get_cluster(discipline_name, _layer)

        # Apply --cluster filter
        if args.cluster and args.cluster.upper() != cluster:
            continue

        idx += 1
        record = extract_methodology_for_discipline(
            discipline_name, templates, cluster, idx
        )
        records.append(record)

        sects = ", ".join(record["typical_sections"])
        print(f"  [{record['methodology_id']}] {discipline_name}: "
              f"approach={record['approach_type']}, "
              f"sections={len(record['typical_sections'])}, "
              f"templates={len(templates)}")

    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nWritten: {OUTPUT_PATH}")
    print(f"Total methodology records: {len(records)}")


if __name__ == "__main__":
    main()
