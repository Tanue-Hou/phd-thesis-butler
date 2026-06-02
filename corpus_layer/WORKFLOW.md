# Corpus Distillation Pipeline — PhD Thesis Butler v4.0

## Overview

The corpus_layer reads raw JSONL assets, extracts structural patterns,
and distills them into statistically grounded records for the planning_layer.

```
assets/*.jsonl  ──►  EXTRACT  ──►  DISTILL  ──►  planning_layer/assets/  +  .phd_build/
```

---

## Stage 1 — SOURCE (Read)

### Input
- **Path**: `assets/cluster/{CLUSTER}/master/MASTER.jsonl`
- **Path**: `assets/cluster/{CLUSTER}/quality/QUALITY2_*.jsonl`
- **Path**: `assets/global/master/MASTER.jsonl`

### Scale
- 16,722 templates from 1,403 unique sources (pdf_id)
- Clusters: HUM_SOC, TECH_LIFE, GLOBAL, ART_SPORT, MATH_PHYS
- Categories (ENUM): INTRO, SURVEY, MODEL, METHOD, EXPERIMENT, RESULT,
  DISCUSSION, CONCLUSION, TRANSITION, FORMAL_DEFS, ENGINEERING, AREF, UTILS

### Known Bug
All `_layer` fields currently show `ART_SPORT` regardless of actual cluster.
Pipeline MUST derive cluster from directory path, NOT from `_layer` field.

### Data Fields per Entry
```
template, category, subtype, when_to_use, common_mistakes,
quality_score (Q2=2, Q1=1, Q0=0), source, subject, pdf_id,
slots[], _layer (UNRELIABLE), _discipline
```

---

## Stage 2 — EXTRACT (Parse & Structure)

### 2a. Paper Records
Group entries by `pdf_id` → one `paper_record` per source document:
- Derive `discipline` from `_discipline` field
- Derive `cluster` from directory path (NOT `_layer`)
- Count templates per category
- Sum quality_distribution (Q2/Q1/Q0 counts)
- Classify `document_type`: dissertation (page_count > 60) / abstract (≤ 60)

### 2b. Structure Records
Group entries by `pdf_id`, sort by category order → one `structure_record`:
- Extract `section_sequence` (ordered array of DIS categories present)
- Derive `pattern_type`:
  - **deductive**: INTRO → MODEL → METHOD → RESULT → CONCLUSION
  - **inductive**: INTRO → SURVEY → METHOD → RESULT → DISCUSSION
  - **hypothetico-deductive**: INTRO → SURVEY → MODEL → EXPERIMENT → RESULT → DISCUSSION
- Compute boolean flags: has_intro, has_survey, has_model, has_method,
  has_experiment, has_result, has_discussion, has_conclusion, has_formal_defs,
  has_engineering, has_transition

### 2c. Subtype Normalization
- Raw: ~1,662 distinct subtypes
- After dedup/canonical: ~400 normalized subtypes
- Group by semantic equivalence (e.g., "relevance_statement" ≈ "актуальность")

### 2c. AREF Extraction
Russian-specific categories (from AREF_RUSSIAN_CATEGORIES):
```
АКТУАЛЬНОСТЬ, НОВИЗНА, ЦЕЛЬ_ЗАДАЧИ, МЕТОДЫ, ОБЪЕКТ_ПРЕДМЕТ,
ПОЛОЖЕНИЯ, ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ, ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ,
АПРОБАЦИЯ, ВЫВОДЫ, ПЕРСПЕКТИВЫ, СТЕПЕНЬ_РАЗРАБОТАННОСТИ, ДОСТОВЕРНОСТЬ
```

---

## Stage 3 — DISTILL (Aggregate)

Aggregate extracted records into statistical patterns:

### 3a. Structure Pattern Distribution
For each (cluster, pattern_type) combination:
- Count how many papers follow each pattern
- Compute evidence_count = number of supporting papers
- Confidence: high (≥30), medium (10-29), low (<10), pending (0)

### 3b. Category Frequency Matrix
For each (cluster, category):
- Total template count
- Average quality score
- Top subtypes by frequency
- Gap analysis: categories with <100 templates = "thin"

### 3c. Methodology Route Extraction
Trace common sequences:
- Which categories typically precede/follow each other
- Identify mandatory vs. optional sections per discipline
- Compute transition probabilities between categories

### 3d. Evidence Count Computation
Every distilled record carries:
```json
{
  "count": <integer>,
  "source": "<paper_ids or aggregate source>",
  "confidence": "high" | "medium" | "low" | "pending"
}
```

---

## Stage 4 — PUBLISH (Write Output)

### Target Locations
1. **planning_layer/assets/** — Statistical summaries, pattern distributions
2. **.phd_build/** — Build-ready JSON for thesis generation

### Output Files
| File | Location | Description |
|------|----------|-------------|
| `paper_records.jsonl` | corpus_layer/schemas/ | Per-paper metadata records |
| `structure_records.jsonl` | corpus_layer/schemas/ | Per-paper structure records |
| `patterns_v4.json` | planning_layer/patterns/ | Distilled structure patterns |
| `category_stats_v4.json` | planning_layer/assets/ | Category frequency + quality |
| `methodology_routes_v4.json` | planning_layer/assets/ | Common chapter sequences |

---

## Gap Awareness (Current Corpus)

| Category | Count | Status |
|----------|-------|--------|
| INTRO | 3,440 | OVER-REPRESENTED |
| RESULT | 276 | THIN |
| MODEL | 84 | SEVERELY THIN |
| EXPERIMENT | 50 | SEVERELY THIN |
| Other | ~12,872 | OK |

Pipeline must flag thin categories and avoid over-generalizing from
insufficient evidence.

---

## Schema Files

- `corpus_layer/schemas/SCHEMA_CONVENTION.md` — Shared conventions
- `corpus_layer/schemas/paper_record.schema.json` — Paper metadata schema
- `corpus_layer/schemas/structure_record.schema.json` — Structure pattern schema
