#!/usr/bin/env python3
"""
Router Agent v3.0 — 三段式推断（Cluster→Discipline→排除词）
输出契约锁死 JSON
"""

import json, os, sys, re
from pathlib import Path

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")

# ========== 三大 CLUSTER 关键词 ==========
CLUSTER_KEYWORDS = {
    "TECH_LIFE": ["пациент", "n=", "клинический", "диагноз", "систем", "управление",
                  "алгоритм", "устройств", "параметр", "реакци", "синтез", "молекул",
                  "химическ", "клетк", "ген", "ДНК", "белок"],
    "HUM_SOC": ["экономическ", "рынок", "регресси", "эндогенност", "правов",
                "законодатель", "юридическ", "язык", "лингвистическ", "текст",
                "историческ", "событие", "период", "педагогическ", "воспитание",
                "социальн", "общество"],
    "ART_SPORT": ["искусств", "живопис", "музык", "театр", "архитектур",
                  "спорт", "тренировк", "соревнован", "физическ культур"],
}

CLUSTER_NAMES = {
    "TECH_LIFE": "理工农医",
    "HUM_SOC": "人文社科",
    "ART_SPORT": "艺术体育",
    "MATH_PHYS": "数理科学",
}

# Within-cluster discipline mapping
DISCIPLINE_MAP = {
    "TECH_LIFE": {
        "MEDICINE": ["пациент", "критерии включения", "n=", "клинический", "диагноз"],
        "BIOLOGY": ["клетк", "ген", "ДНК", "белок", "микроорганизм"],
        "CHEMISTRY": ["химическ", "реакци", "молекул", "синтез"],
    },
    "HUM_SOC": {
        "ECONOMICS": ["экономическ", "рынок", "регресси", "эндогенност"],
        "LAW": ["правов", "законодатель", "юридическ"],
        "PHILOLOGY": ["язык", "лингвистическ", "текст"],
        "HISTORY": ["историческ", "событие", "период"],
        "PEDAGOGY": ["педагогическ", "воспитание", "образова"],
    },
    "ART_SPORT": {
        "ARTS": ["искусств", "живопис", "музык", "театр"],
        "SPORT": ["спорт", "тренировк", "соревнован"],
    },
}

# Exclusion rules: keyword pair → override
EXCLUSION_RULES = [
    (["лемма", "теорема", "доказательство"], ["алгоритм", "управление"], "ENGINEERING"),
    (["систем", "управление"], ["язык", "лингвистик"], "PHILOLOGY"),
    (["клинический", "пациент"], ["экономическ"], "MEDICINE"),
]

# ========== Scene Keywords ==========
SCENE_KEYWORDS = {
    "FORMAL_DEFS": {"priority": 3, "keywords": ["теорема", "лемма", "доказательство"]},
    "MODEL": {"priority": 2, "keywords": ["уравнение", "модель", "допущение", "предполагается"]},
    "EXPERIMENT": {"priority": 2, "keywords": ["эксперимент", "выборка", "метрики", "n="]},
    "RESULT": {"priority": 2, "keywords": ["результат", "рис", "таблица", "RMSE", "ошибка"]},
    "INTRO": {"priority": 1, "keywords": ["актуальность", "цель работы", "задачи", "в последние годы"]},
    "METHOD": {"priority": 1, "keywords": ["метод", "алгоритм", "подход", "процедура"]},
    "DISCUSSION": {"priority": 1, "keywords": ["обсуждение", "ограничения", "перспективы"]},
    "CONCLUSION": {"priority": 1, "keywords": ["вывод", "заключение", "таким образом"]},
    "SURVEY": {"priority": 1, "keywords": ["обзор литературы", "известные работы"]},
    "TRANSITION": {"priority": 1, "keywords": ["перейдём к", "рассмотрим теперь"]},
}


def infer(text, filepath="", config={}):
    """Three-stage inference → locked JSON output"""
    text_lower = text.lower()
    
    # Stage 1: Cluster inference
    cluster_scores = {}
    for cluster, kws in CLUSTER_KEYWORDS.items():
        cluster_scores[cluster] = sum(1 for kw in kws if kw in text_lower)
    
    # Exclusion rules (check across clusters)
    for rule_kws, override_kws, override_cluster in EXCLUSION_RULES:
        has_rule = any(kw in text_lower for kw in rule_kws)
        has_override = any(kw in text_lower for kw in override_kws)
        if has_rule and has_override:
            # Override takes effect
            for c in cluster_scores:
                if c != override_cluster and override_cluster in [k for k in DISCIPLINE_MAP]:
                    cluster_scores[override_cluster] = cluster_scores.get(override_cluster, 0) + 3
                    break
    
    best_cluster = max(cluster_scores, key=cluster_scores.get) if any(cluster_scores.values()) else "TECH_LIFE"
    cluster_conf = min(0.3 + cluster_scores.get(best_cluster, 0) * 0.1, 0.95)
    
    # Stage 2: Discipline inference (within cluster)
    disc_map = DISCIPLINE_MAP.get(best_cluster, {})
    disc_scores = {}
    for disc, kws in disc_map.items():
        disc_scores[disc] = sum(1 for kw in kws if kw in text_lower)
    
    best_disc = max(disc_scores, key=disc_scores.get) if any(disc_scores.values()) else (
        "ENGINEERING" if best_cluster == "TECH_LIFE" else "GENERAL"
    )
    disc_conf = min(0.3 + disc_scores.get(best_disc, 0) * 0.15, 0.95)
    
    # Stage 3: Scene inference (priority-based)
    scene_scores = {}
    for scene, cfg in SCENE_KEYWORDS.items():
        score = sum(1 for kw in cfg["keywords"] if kw in text_lower)
        if score > 0:
            scene_scores[scene] = (cfg["priority"], score)
    
    if not scene_scores:
        best_scene = "INTRO"
        scene_conf = 0.2
    else:
        # Sort by priority desc, then score desc
        best_scene = max(scene_scores, key=lambda s: (scene_scores[s][0], scene_scores[s][1]))
        scene_conf = min(0.3 + scene_scores[best_scene][1] * 0.1, 0.95)
    
    # Determine subtypes for scene
    scene_subtypes = {
        "INTRO": ["motivation", "relevance", "objective", "problem_statement", "tasks"],
        "MODEL": ["assumptions", "mathematical_formulation", "notation"],
        "EXPERIMENT": ["data_description", "scenario_design", "metrics", "setup"],
        "RESULT": ["numeric_reporting", "improvement_reporting", "comparison_table"],
        "DISCUSSION": ["interpretation", "limitation", "implication"],
        "CONCLUSION": ["summary", "future_work", "contributions_recap"],
        "METHOD": ["algorithm_design", "pipeline_overview", "parameter_setting"],
        "SURVEY": ["taxonomy", "comparison", "gap", "limitations_of_prior"],
        "FORMAL_DEFS": ["definition", "theorem", "lemma", "notation"],
        "TRANSITION": ["sequencing", "contrast", "addition"],
    }
    subtypes = scene_subtypes.get(best_scene, ["general"])
    
    # Build locked output
    output = {
        "version": "3.0",
        "inference": {
            "cluster": best_cluster,
            "cluster_name": CLUSTER_NAMES.get(best_cluster, best_cluster),
            "cluster_confidence": round(cluster_conf, 2),
            "discipline": best_disc,
            "discipline_confidence": round(disc_conf, 2),
            "category": best_scene,
            "subtype": subtypes[0],
            "scene_confidence": round(scene_conf, 2),
        },
        "retrieval": {
            "fallback_chain": [
                f"DISCIPLINE({best_disc}).QUALITY2",
                f"CLUSTER({best_cluster}).QUALITY2",
                "GLOBAL.QUALITY2",
                f"DISCIPLINE({best_disc}).QUALITY1",
                f"CLUSTER({best_cluster}).QUALITY1",
                "GLOBAL.QUALITY1",
            ],
            "query": {
                "category": best_scene,
                "subtype": subtypes[0],
                "min_hit": 3,
                "need_utils": ["CONSERVATIVE", "CONNECTIVE", "NUMERIC"],
            }
        },
        "polish": {
            "level": "L1",
            "hit_layer": None,
            "hit_quality": None,
            "hit_count": 0,
        },
    }
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Input text")
    parser.add_argument("--file", help="Input file path")
    parser.add_argument("--output", "-o", help="Output JSON path", default="/dev/stdout")
    args = parser.parse_args()

    text = args.text or ""
    if args.file:
        with open(args.file) as f:
            text = f.read()

    result = infer(text, args.file or "")

    output = args.output
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Summary line
    inf = result["inference"]
    print(f"Cluster: {inf['cluster']}({inf['cluster_name']}) | "
          f"Discipline: {inf['discipline']} | "
          f"Scene: {inf['category']}/{inf['subtype']}")
