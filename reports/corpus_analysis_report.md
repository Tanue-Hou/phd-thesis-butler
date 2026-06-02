# Corpus Analysis Report — PhD Thesis Butler v3.3.5
**Date:** 2026-06-02 | **Analyst:** Hermes Agent

---

## 1. Data Overview

**Total templates:** 16,722 (DIS: 9,855 | AREF: 6,564 | UTILS: 303)
**Sources:** 1,042 dissertations + 361 abstracts = 1,403 documents, 34 disciplines

### Templates per Discipline (top 15)
| Discipline | Templates | Cluster |
|---|---|---|
| физико-математические науки | 1,275 | TECH_LIFE |
| другие науки | 1,252 | mixed |
| филологические науки | 1,114 | HUM_SOC |
| химические науки | 958 | TECH_LIFE |
| биологические науки | 705 | TECH_LIFE |
| медицинских наук | 517 | TECH_LIFE |
| юридические науки | 493 | HUM_SOC |
| экономические науки | 408 | HUM_SOC |
| исторические науки | 329 | HUM_SOC |
| филологических наук | 313 | HUM_SOC |
| юридических наук | 150 | HUM_SOC |
| политические/политических наук | 342 | HUM_SOC |
| психологические/психологических наук | 262 | HUM_SOC |
| химических наук | 190 | TECH_LIFE |
| географические/географических наук | 277 | TECH_LIFE |

### Cluster Totals (quality-binned files)
| Cluster | Quality files (total) |
|---|---|
| TECH_LIFE | 8,251 |
| HUM_SOC | 4,968 |
| MATH_PHYS | exists but sparse |
| GLOBAL | exists, separate |

**BUG:** `_layer` field in discipline files shows only `ART_SPORT` (4,895) and `HUM_SOC` (5,150) — the `TECH_LIFE` and `GLOBAL` layer assignments are NOT reflected in the per-entry `_layer` field. The cluster/quality directories are correctly populated, but the metadata is inconsistent.

---

## 2. Structure Patterns (from STRUCTURE_PATTERNS.json)

5 canonical patterns defined:
1. **engineering_model_method_experiment** (deductive) — MODEL→METHOD→EXPERIMENT→RESULT
2. **ai_method_dataset_ablation** (hypothetico-deductive) — METHOD→DATASET→ABLATION
3. **empirical_social_science** (hypothetico-deductive) — THEORY→DATA→ANALYSIS
4. **life_science_imrad** (inductive) — INTRO→METHODS→RESULTS→DISCUSSION
5. **humanities_argumentative_analysis** (inductive) — THEORY→ANALYTICAL CHAPTERS

All 5 patterns have `evidence_count: "pending"` — **no actual counting has been done yet**. This is a critical gap for v4.0.

---

## 3. DIS Category Distribution

| Category | Count | Coverage |
|---|---|---|
| INTRO | 3,440 | **STRONG** |
| SURVEY | 1,070 | Strong |
| АКТУАЛЬНОСТЬ | 1,024 | Strong (AREF) |
| METHOD | 582 | Good |
| ЦЕЛЬ_ЗАДАЧИ | 412 | Good (AREF) |
| НОВИЗНА | 408 | Good (AREF) |
| DISCUSSION | 328 | Moderate |
| TRANSITION | 325 | Moderate |
| CONCLUSION | 309 | Moderate |
| МЕТОДЫ | 307 | Moderate (AREF) |
| ОБЪЕКТ_ПРЕДМЕТ | 286 | Moderate (AREF) |
| RESULT | 276 | **WEAK** |
| FORMAL_DEFS | 276 | Moderate |
| ПОЛОЖЕНИЯ | 245 | Moderate (AREF) |
| ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ | 207 | Moderate (AREF) |
| АПРОБАЦИЯ | 139 | Weak (AREF) |
| ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ | 117 | Weak (AREF) |
| ВЫВОДЫ | 116 | Weak (AREF) |
| MODEL | 84 | **CRITICAL** |
| EXPERIMENT | 50 | **CRITICAL** |
| ПЕРСПЕКТИВЫ | 30 | **CRITICAL** |
| СТЕПЕНЬ_РАЗРАБОТАННОСТИ | 11 | **CRITICAL** |
| ДОСТОВЕРНОСТЬ | 3 | **EMPTY** |

---

## 4. Logic Chain Coverage

Canonical chain: INTRO → SURVEY → MODEL → METHOD → EXPERIMENT → RESULT → DISCUSSION → CONCLUSION

| Stage | Templates | Status |
|---|---|---|
| INTRO | 3,440 | ✅ Over-represented |
| SURVEY | 1,070 | ✅ Good |
| MODEL | 84 | ⚠️ Severely under-supplied |
| METHOD | 582 | ✅ Adequate |
| EXPERIMENT | 50 | ❌ Critical gap |
| RESULT | 276 | ⚠️ Weak |
| DISCUSSION | 328 | ⚠️ Moderate |
| CONCLUSION | 309 | ⚠️ Moderate |

**Verdict:** The middle of the chain (MODEL→EXPERIMENT) is severely undersampled. The corpus is INTRO/SURVEY-heavy because those sections are template-rich in Russian dissertations. The scientific core (how you actually prove things) is thin.

---

## 5. Rhetorical Moves per Section (sampled from Q2 files)

**INTRO** (1,480 TECH_LIFE, 1,004 HUM_SOC Q2 templates):
- Relevance/justification, goal formulation, task decomposition, gap identification, significance statement, historical context, object/subject definition
- **Well covered** — 20+ rhetorical subtypes observed

**SURVEY** (376 TECH_LIFE, 315 HUM_SOC):
- Literature overview, gap identification, historical review, theoretical framework, domestic research gap, partial coverage gap
- **Good coverage**

**MODEL** (31 TECH_LIFE, 21 HUM_SOC):
- Problem formulation, model applicability, principle of operation, architecture description, property explanation
- **Thin** — only 20 templates in entire Q2 for TECH_LIFE MODEL

**EXPERIMENT** (15 TECH_LIFE, 2 HUM_SOC):
- Comparative analysis, validation, bioefficacy assay, structural characterization
- **Almost empty for HUM_SOC** (2 templates!)

**CONCLUSION** (142 TECH_LIFE, 37 HUM_SOC):
- Novelty statement, practical significance, summary conclusions, prospective application
- **HUM_SOC critically thin** (37 templates for all social sciences)

---

## 6. Quality Distribution

| Quality | Count | % |
|---|---|---|
| Q2 (high) | 8,986 | 53.7% |
| Q1 (medium) | 7,694 | 46.0% |
| Q0 (low) | 42 | 0.3% |

Q0 is effectively purged. Per-discipline quality shows most templates are Q2-Q1 mix. No discipline is Q0-dominated.

---

## 7. Coverage Gaps (Critical for v4.0)

1. **EXPERIMENT** — 50 templates total. HUM_SOC has 2. Needs 200+ for viable retrieval.
2. **MODEL** — 84 templates. Heavy on physics/chemistry, thin on engineering/AI.
3. **RESULT** — 276 templates. Needs quantitative result patterns (tables, figures, statistical reporting).
4. **DISCUSSION** — 328 but heavily humanities-slanted. Technical discussion (limitation analysis, ablation, comparison with baselines) is thin.
5. **ПЕРСПЕКТИВЫ** (future directions) — 30 templates. Critical for conclusion generation.
6. **ДОСТОВЕРНОСТЬ** (validity/reliability) — 3 templates. Essentially empty.
7. **СТЕПЕНЬ_РАЗРАБОТАННОСТИ** — 11 templates. Empty.
8. **Subtype inconsistency** — 6,866→1,662 subtypes standardized, but top subtypes still show near-duplicates: "формулировка цели" (108), "формулировка_цели" (54), "Формулировка цели" (27), "формулировка цели исследования" (45). Need final normalization pass.
9. **`_layer` metadata bug** — All discipline file entries show `_layer: ART_SPORT` regardless of actual cluster. This will break retrieval routing in v4.0.

---

## 8. Recommendations for corpus_layer Design

### Schema Priorities
1. **Fix `_layer` bug immediately** — every entry must have correct cluster assignment. Re-derive from discipline→cluster mapping.
2. **Define 11 canonical categories** as first-class schema fields: INTRO, SURVEY, MODEL, METHOD, EXPERIMENT, RESULT, DISCUSSION, CONCLUSION, TRANSITION, FORMAL_DEFS, + AREF group.
3. **Normalize subtypes** — apply case-insensitive, underscore/space-insensitive dedup. Target: ~400 canonical subtypes from current 1,662.

### Script Priorities for v4.0
1. **Augment EXPERIMENT+MODEL+RESULT** — mine 200+ templates from remaining untapped dissertations. Focus on technical clusters.
2. **Generate DISCUSSION templates** for STEM — ablation studies, limitation analysis, comparison-with-baselines patterns.
3. **Populate empty AREF categories** — ДОСТОВЕРНОСТЬ, СТЕПЕНЬ_РАЗРАБОТАННОСТЬ, ПЕРСПЕКТИВЫ need dedicated extraction runs.
4. **Evidence-count filling** — STRUCTURE_PATTERNS.json has 5 patterns, all with `evidence_count: "pending"`. Run counting script against discipline files.
5. **Logic chain validation script** — verify each dissertation's templates actually cover a coherent INTRO→CONCLUSION path; flag incomplete chains.

### Retrieval Layer
- Fallback chain `DISCIPLINE → CLUSTER → GLOBAL` works, but thin categories (EXPERIMENT, MODEL) will always fall through to GLOBAL. Consider synthetic template generation for these gaps rather than relying on fallback.

---

*Report generated from v3.3.5 corpus. 16,722 templates, 1,403 sources, 34 disciplines.*
