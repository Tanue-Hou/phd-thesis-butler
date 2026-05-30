---
name: phd-thesis-butler/aref_core
description: "Автореферат — AREF abstract modules"
version: "3.3.5"
---

# AREF — Автореферат（作者摘要）

## Purpose

Автореферат句式模板，用于博士论文摘要部分的写作辅助。

## Categories

**AREF modules:** АКТУАЛЬНОСТЬ, НОВИЗНА, ЦЕЛЬ_ЗАДАЧИ, ОБЪЕКТ_ПРЕДМЕТ, МЕТОДЫ, ПОЛОЖЕНИЯ, ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ, ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ, АПРОБАЦИЯ, ВЫВОДЫ, ПЕРСПЕКТИВЫ, ДОСТОВЕРНОСТЬ, СТЕПЕНЬ_РАЗРАБОТАННОСТИ, СТРУКТУРА

## Retrieval files (in priority order)

1. `assets/global/quality/QUALITY2_{MODULE}.jsonl` — GLOBAL-level AREF module quality files
2. `data/curated/quality/QUALITY2_SELECTION_AREF.jsonl` — flat quality selection (primary AREF source)
3. `data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl` — full AREF corpus (fallback)

## Quality Rules

- quality_score=2: auto-serve
- quality_score=1: use only if Q2 < 3 results
- quality_score=0: never auto-serve
