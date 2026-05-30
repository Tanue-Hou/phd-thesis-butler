---
name: phd-thesis-butler/utils_core
description: "UTILS — Connective, Conservative, Numeric functional language"
version: "3.3.4"
---

# UTILS — Вспомогательные конструкции（功能语言）

## Purpose

功能语言句式模板，用于论文中的过渡、保守措辞和数字比较。

## Kinds

- **CONNECTIVE** — transition and structural phrases (Однако, С одной стороны, Более того)
- **CONSERVATIVE** — hedging and cautious language (Предположительно, Вероятно, Можно предположить)
- **NUMERIC** — quantitative reporting patterns (увеличение на X%, ошибка составляет Y)

## Retrieval files

1. `assets/global/master/UTILS.jsonl` — GLOBAL-level UTILS (cross-discipline functional phrases)
2. `assets/cluster/TECH_LIFE/master/UTILS.jsonl` — TECH_LIFE-level UTILS
3. `data/curated/quality/QUALITY2_UTILS.jsonl` — quality-filtered UTILS
4. `data/curated/master/MASTER_UTILS.jsonl` — full UTILS corpus (fallback)

## Quality Rules

- quality_score=2: auto-serve
- quality_score=1: use only if Q2 < 3 results
- quality_score=0: never auto-serve
