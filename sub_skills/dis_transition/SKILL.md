---
name: phd-thesis-butler/dis_transition
description: "过渡 — TRANSITION sentence templates"
version: "3.3.5"
---

# TRANSITION — 过渡（Переходы）

## Purpose

过渡句式模板，用于博士论文Переходы章节的写作辅助。

## Category

**TRANSITION** — 过渡

Relevant subtypes: связки между разделами, переходные фразы

## Retrieval files (in priority order)

1. `assets/discipline/технические_науки.jsonl` — discipline-specific templates (default)
2. `assets/cluster/TECH_LIFE/quality/QUALITY2_TRANSITION.jsonl` — cluster-level quality templates
3. `assets/global/quality/QUALITY2_TRANSITION.jsonl` — cross-cluster templates
4. `data/curated/quality/QUALITY2_SELECTION_DIS.jsonl` — flat fallback (for DIS)
5. `data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl` — deep fallback (full corpus)

## Quality Rules

- quality_score=2: auto-serve (field-independent, most portable)
- quality_score=1: use only if quality=2 yields <3 results
- quality_score=0: never auto-serve

## Common pitfalls

- Do not use templates without adapting `[...]` slots to the user's domain
- Always adjust number, case, and tense to match the user's context
- Never translate Russian templates to English or Chinese
