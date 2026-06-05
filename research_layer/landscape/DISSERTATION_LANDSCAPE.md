# Dissertation Landscape Mode

> phd-thesis-butler v5.4.0 | research_layer/landscape

## Purpose

Dissertation Landscape Mode produces a structured comparative analysis of existing dissertations in the user's research domain. It answers the question: *"What have others done, how did they structure it, and where is my opening?"*

The landscape report is a **pre-writing intelligence product** — not a literature review. It maps the dissertation field so the user can make informed structural, methodological, and positioning decisions before committing to an outline.

---

## When to Run

Run Dissertation Landscape **after** the user has a working topic statement but **before** detailed outline planning. It feeds directly into planning_layer.

---

## End-to-End Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   USER INPUT                            │
│  • Topic / research question                            │
│  • Preferred sources (DisserCat, eLIBRARY, CyberLeninka,│
│    OpenAlex, Semantic Scholar, Zotero private corpus)   │
│  • Language preference (ru/en/both)                     │
│  • Degree level filter (candidate/doctoral/both)        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              1. AGENTIC SEARCH                          │
│                                                         │
│  For each selected source:                              │
│  • Generate language-appropriate search queries          │
│  • Execute search (API / public page scrape)            │
│  • Parse: title, author, year, specialty code, abstract,│
│    keywords, TOC, institution, degree type              │
│  • Assign source_access level                           │
│  • Assign read_depth level                              │
│  • Assign structure_confidence score                    │
│                                                         │
│  → Output: raw_records[]                                │
│  See: AGENTIC_SEARCH.md                                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              2. ZOTERO PRIVATE CORPUS                    │
│                                                         │
│  If Zotero enabled:                                     │
│  • Query Zotero Local API                               │
│  • Filter by collection / tags / topic relevance        │
│  • Skip notes & attachments (handle gracefully)         │
│  • Extract metadata + indexed fulltext where available  │
│  • Respect privacy boundaries                           │
│                                                         │
│  → Output: zotero_records[]                             │
│  See: ZOTERO_PRIVATE_CORPUS.md                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              3. MERGE & DEDUPLICATE                      │
│                                                         │
│  • Combine raw_records + zotero_records                 │
│  • Deduplicate by (author, year, title similarity)      │
│  • Tag provenance per record                            │
│  • Resolve conflicts (prefer deeper read_depth)         │
│                                                         │
│  → Output: merged_records[]                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              4. RUBRIC ANALYSIS                          │
│                                                         │
│  For each record and across the corpus:                 │
│  • Chapter structure comparison                         │
│  • Methodology landscape identification                 │
│  • Validation / argumentation pattern extraction        │
│  • Theme clustering                                     │
│  • Gap identification                                   │
│  • Borrowable writing move detection                    │
│  • Risk warning generation                              │
│                                                         │
│  → Output: analysis blocks                              │
│  See: COMPARISON_RUBRIC.md                              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              5. SYNTHESIS & OUTPUT                       │
│                                                         │
│  • Generate landscape report (12-section markdown)      │
│  • Generate landscape result JSON                       │
│  • Map recommended_outline → planning_layer chapters    │
│  • Route evidence needs → evidence_layer                │
│                                                         │
│  → Output: landscape_report.md + landscape_result.json  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              6. PLANNING_LAYER HANDOFF                   │
│                                                         │
│  • recommended_outline provides chapter skeleton        │
│  • positioning_gaps inform novelty statement            │
│  • methodology_patterns inform method chapter approach  │
│  • borrowable_moves inform writing strategy             │
│                                                         │
│  → planning_layer receives structured input             │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Points

### → planning_layer

| Landscape Output | Planning Layer Use |
|---|---|
| `recommended_outline` | Chapter skeleton with suggested types |
| `positioning_gaps` | Novelty / contribution statement drafting |
| `methodology_patterns` | Method chapter structure guidance |
| `structure_patterns` | Overall dissertation architecture |
| `borrowable_moves` | Writing strategy for each chapter |

### → evidence_layer

| Landscape Output | Evidence Layer Use |
|---|---|
| `evidence_layer_routes` | Which chapters need empirical evidence binding |
| `validation_patterns` | What evidence types are expected by the field |
| `source_summary` | Available data sources for evidence collection |

---

## Output Schema

The landscape produces two outputs:

1. **landscape_report.md** — A 12-section human-readable report (see example)
2. **landscape_result.json** — A machine-readable analysis object (see example)

The JSON schema is defined in `examples/dissertation_landscape_result_sample.json`.

---

## Read Depth & Confidence

Every record carries two quality indicators:

- **read_depth** — How much content was actually read (see AGENTIC_SEARCH.md taxonomy)
- **structure_confidence** — 0.0–1.0 score indicating how reliably the chapter structure was extracted

Low-confidence records are still included but flagged. The rubric analysis weights high-confidence records more heavily.

---

## Privacy & Ethics

- Zotero attachment paths are **never** exposed in outputs
- Private corpus data is **never** sent to external APIs
- All search queries are logged for reproducibility
- Landscape reports are local-only artifacts

---

## File Index

| File | Purpose |
|---|---|
| `DISSERTATION_LANDSCAPE.md` | This document — workflow overview |
| `AGENTIC_SEARCH.md` | Agentic search workflow & taxonomy |
| `ZOTERO_PRIVATE_CORPUS.md` | Zotero integration workflow |
| `COMPARISON_RUBRIC.md` | Analysis rubric specification |
| `examples/dissercat_landscape_input_sample.json` | Sample DisserCat input |
| `examples/zotero_landscape_input_sample.json` | Sample Zotero input |
| `examples/dissertation_landscape_result_sample.json` | Sample result JSON |
| `examples/dissertation_landscape_report_sample.md` | Sample report markdown |
