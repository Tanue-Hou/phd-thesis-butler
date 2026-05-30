---
name: phd-thesis-butler/dis_intro
description: "引言 — INTRO sentence templates"
version: "3.3"
---

# INTRO — 引言（Введение）

## Purpose

引言句式模板，用于博士论文Введение章节的写作辅助。

## Category

**INTRO** — 引言

Relevant subtypes: актуальность, постановка проблемы, формулировка цели и задач, объект и предмет

## Retrieval files (in priority order)

1. `assets/discipline/технические_науки.jsonl` — discipline-specific templates (default)
2. `assets/cluster/TECH_LIFE/quality/QUALITY2_INTRO.jsonl` — cluster-level quality templates
3. `assets/global/quality/QUALITY2_INTRO.jsonl` — cross-cluster templates
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
