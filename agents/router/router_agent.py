#!/usr/bin/env python3
"""
Router Agent — 学科推断 + 场景推断 + 执行计划输出
使用 mimo-v2.5 进行轻量文本分析
"""

import json, os, re, sys, subprocess
from pathlib import Path

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")

# ========== Cluster Mapping ==========
VAK_TO_CLUSTER = {
    '01': 'MATH_PHYS', '1.1': 'MATH_PHYS', '1.2': 'MATH_PHYS',
    '02': 'TECH_LIFE', '03': 'TECH_LIFE', '04': 'TECH_LIFE',
    '05': 'TECH_LIFE', '2.1': 'TECH_LIFE', '2.2': 'TECH_LIFE',
    '2.3': 'TECH_LIFE', '2.4': 'TECH_LIFE', '2.5': 'TECH_LIFE',
    '2.6': 'TECH_LIFE', '2.7': 'TECH_LIFE',
    '14': 'TECH_LIFE', '3.1': 'TECH_LIFE',
    '08': 'HUM_SOC', '5.2': 'HUM_SOC',
    '12': 'HUM_SOC', '5.1': 'HUM_SOC',
    '07': 'HUM_SOC', '5.6': 'HUM_SOC',
    '09': 'HUM_SOC', '5.9': 'HUM_SOC',
    '5.7': 'HUM_SOC', '5.3': 'HUM_SOC', '5.4': 'HUM_SOC',
}

CLUSTER_NAMES = {
    "TECH_LIFE": "理工农医",
    "HUM_SOC": "人文社科",
    "MATH_PHYS": "数理科学",
}

# ========== Scene Keywords ==========
SCENE_KEYWORDS = {
    "INTRO": {
        "keywords": ["актуальность", "цель работы", "задачи", "объект исследования",
                     "предмет", "в последние годы", "всё большее внимание", "мотивация"],
        "subtypes": ["motivation", "relevance", "problem_statement", "objective", "tasks"]
    },
    "SURVEY": {
        "keywords": ["обзор литературы", "известные работы", "посвящена", "рассматривались",
                     "анализ существующих", "классификация подходов"],
        "subtypes": ["taxonomy", "comparison", "gap", "limitations_of_prior"]
    },
    "MODEL": {
        "keywords": ["модель", "уравнение", "допущение", "предполагается",
                     "рассмотрим систему", "пусть", "обозначим", "теорема"],
        "subtypes": ["assumptions", "mathematical_formulation", "notation", "theorem"]
    },
    "METHOD": {
        "keywords": ["метод", "алгоритм", "подход", "процедура", "заключается в",
                     "предложен", "разработан"],
        "subtypes": ["algorithm_design", "pipeline_overview", "parameter_setting"]
    },
    "EXPERIMENT": {
        "keywords": ["эксперимент", "моделирование", "параметры", "выборка",
                     "критерии включения", "n=", "метрики", "benchmark"],
        "subtypes": ["data_description", "scenario_design", "metrics", "parameter_setting"]
    },
    "RESULT": {
        "keywords": ["результат", "рис", "таблица", "наблюдается",
                     "RMSE", "ошибка", "сравнение", "повышение"],
        "subtypes": ["numeric_reporting", "improvement_reporting", "comparison_table"]
    },
    "DISCUSSION": {
        "keywords": ["обсуждение", "объясняется", "связано с", "можно предположить",
                     "ограничения", "перспективы"],
        "subtypes": ["interpretation", "limitation", "implication", "mechanism_explanation"]
    },
    "CONCLUSION": {
        "keywords": ["вывод", "заключение", "таким образом", "перспектива",
                     "дальнейшие исследования"],
        "subtypes": ["summary", "future_work", "contributions_recap"]
    },
    "TRANSITION": {
        "keywords": ["перейдём к", "рассмотрим теперь", "далее", "с одной стороны"],
        "subtypes": ["sequencing", "contrast", "addition"]
    },
    "FORMAL_DEFS": {
        "keywords": ["определим", "пусть", "обозначим", "теорема", "лемма"],
        "subtypes": ["definition", "theorem", "lemma", "notation"]
    },
}


def infer_discipline(text, filepath="", config={}):
    """Infer discipline from config → filepath → text keywords"""
    # 1. Config — strongest signal
    if config.get("discipline") and config["discipline"] != "auto":
        disc = config["discipline"]
        cluster = config.get("cluster", "auto")
        return {"discipline": disc, "cluster": cluster, "source": "config", "confidence": 1.0}

    # 2. Filepath — check for university/subject in path
    path_lower = filepath.lower()
    for subj in ["медицин", "биологи", "хими"]:
        if subj in path_lower:
            return {"discipline": "MEDICINE", "cluster": "TECH_LIFE", "source": "path", "confidence": 0.85}

    # 3. Text keywords — weak signal
    text_lower = text.lower()
    discipline_signals = {
        "MEDICINE": ["пациент", "критерии включения", "n=", "клинический", "диагноз"],
        "BIOLOGY": ["клетк", "ген", "ДНК", "белок", "микроорганизм"],
        "CHEMISTRY": ["химическ", "реакци", "молекул", "синтез"],
        "ECONOMICS": ["экономическ", "рынок", "регресси", "эндогенность"],
        "MATHEMATICS": ["лемма", "теорема", "доказательство", "множество"],
        "PHYSICS": ["физическ", "электромагнит", "квантов", "термодинамик"],
        "ENGINEERING": ["систем", "управление", "алгоритм", "устройств"],
        "LAW": ["правов", "законодатель", "юридическ"],
        "PHILOLOGY": ["язык", "лингвистическ", "текст"],
        "HISTORY": ["историческ", "событие", "период"],
    }

    scores = {}
    for disc, signals in discipline_signals.items():
        scores[disc] = sum(1 for s in signals if s in text_lower)

    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return {"discipline": best, "cluster": _disc_to_cluster(best), "source": "text", "confidence": 0.7}

    # 4. Default
    return {"discipline": "ENGINEERING", "cluster": "TECH_LIFE", "source": "default", "confidence": 0.3}


def _disc_to_cluster(discipline):
    tech_life = ["MEDICINE", "BIOLOGY", "CHEMISTRY", "ENGINEERING"]
    hum_soc = ["ECONOMICS", "LAW", "HISTORY", "PHILOLOGY", "PHILOSOPHY"]
    if discipline in tech_life: return "TECH_LIFE"
    if discipline in hum_soc: return "HUM_SOC"
    return "MATH_PHYS"


def infer_scene(text):
    """Infer writing section from text keywords"""
    text_lower = text.lower()
    scores = {}

    for scene, config in SCENE_KEYWORDS.items():
        score = sum(1 for kw in config["keywords"] if kw.lower() in text_lower)
        if score > 0:
            scores[scene] = score

    if not scores:
        return {"category": "INTRO", "subtype": "general", "confidence": 0.2,
                "note": "no clear scene detected, defaulting to INTRO"}

    best = max(scores, key=scores.get)
    subtypes = SCENE_KEYWORDS[best]["subtypes"]
    return {"category": best, "subtype": subtypes[0], "confidence": min(0.5 + scores[best] * 0.1, 0.95)}


def build_plan(text, filepath="", config_path=None):
    """Main entry point: infer → build execution plan"""
    # Load config
    config = {}
    if config_path and os.path.exists(config_path):
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    # Infer
    disc_info = infer_discipline(text, filepath, config)
    scene_info = infer_scene(text)

    # Build fallback chain
    cluster = disc_info["cluster"]
    discipline = disc_info["discipline"]

    fallback_chain = [
        f"DISCIPLINE({discipline}).QUALITY2",
        f"CLUSTER({cluster}).QUALITY2",
        "GLOBAL.QUALITY2",
        f"DISCIPLINE({discipline}).QUALITY1",
        f"CLUSTER({cluster}).QUALITY1",
        "GLOBAL.QUALITY1",
    ]

    # Determine polish level
    level = "L1"
    if disc_info["confidence"] < 0.5:
        level = "L1"  # conservative when unsure
    elif "перепиш" in text.lower() or "rewrite" in text.lower():
        level = "L2"

    plan = {
        "discipline_inference": {
            "cluster": cluster,
            "cluster_name": CLUSTER_NAMES.get(cluster, cluster),
            "discipline": discipline,
            "confidence": disc_info["confidence"],
            "source": disc_info["source"],
        },
        "scene_inference": {
            "category": scene_info["category"],
            "subtype": scene_info["subtype"],
            "confidence": scene_info["confidence"],
        },
        "polish_level": level,
        "plan": [
            {
                "step": "retrieve_templates",
                "fallback_chain": fallback_chain,
                "query": {
                    "category": scene_info["category"],
                    "subtype": scene_info["subtype"],
                    "need_utils": ["CONSERVATIVE", "CONNECTIVE", "NUMERIC"]
                }
            },
            {"step": "polish_text", "level": level},
            {"step": "consistency_check"},
            {"step": "safety_check"}
        ]
    }
    return plan


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Input text to analyze")
    parser.add_argument("--file", help="Input file path")
    parser.add_argument("--config", help="Path to project_config.yaml")
    parser.add_argument("--output", "-o", help="Output JSON path", default="/dev/stdout")
    args = parser.parse_args()

    text = args.text or ""
    if args.file:
        with open(args.file) as f:
            text = f.read()

    plan = build_plan(text, args.file or "", args.config)

    output = args.output
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print(json.dumps(plan, ensure_ascii=False, indent=2))
