# Evidence Layer Workflow

> Version: 1.0 | Defines the complete research-to-writing pipeline

---

## Overview

The PhD Thesis Butler Evidence Layer operates through four distinct modes. Each mode has clear entry conditions, operations, and exit criteria. The system transitions between modes based on the state of evidence bindings and citation gaps.

```
[Research Mode] → [Evidence Binding Mode] → [Citation Gap Mode] → [Polishing Mode]
      ↑                    |                        |                      |
      └────────────────────┴────────────────────────┘                      |
                         (loop until gaps = 0)                             |
                                                                           |
                              [Final Delivery] ←───────────────────────────┘
```

---

## Mode 1: Research Mode

**Purpose**: Discover, collect, and evaluate sources relevant to the thesis.

### Entry Conditions
- New topic area identified
- Citation gap report shows `missing` entries
- User explicitly requests research

### Operations
1. Parse `recommended_query` fields from gap reports or user input
2. Execute search across academic databases (Semantic Scholar, arXiv, eLIBRARY/DisserCat)
3. For each candidate source:
   - Extract metadata (title, authors, year, venue, DOI)
   - Assess relevance to the target claim
   - Assign preliminary `evidence_strength` (strong/medium/weak/none)
4. Store results in `sources/` directory with metadata files
5. Generate source evaluation summary

### Exit Conditions
- All targeted gaps have ≥1 candidate source
- User approves collected sources
- Source quality meets threshold (≥ medium strength)

### Output
- Source metadata files in `assets/references/`
- Research summary report

---

## Mode 2: Evidence Binding Mode

**Purpose**: Link collected sources to specific claims in the thesis text, assigning evidence roles.

### Entry Conditions
- Sources collected in Research Mode
- Thesis draft text available for analysis

### Operations
1. Parse thesis text sentence by sentence
2. For each claim sentence:
   - Classify `claim_type` (see CITATION_GAP_DETECTION.md)
   - Determine `required_evidence_roles` based on claim type and chapter context
3. Match available sources to claims:
   - Compare source content against claim text
   - Assign binding records with `binding_id`, `chapter`, `claim_text`, `matched_source_ids`
   - Calculate `evidence_strength` for each binding
4. Persist bindings to `evidence_binding_record` schema
5. Generate chapter-level evidence maps

### Exit Conditions
- All identified claims have binding attempts
- Binding records saved to schema-compliant JSON

### Output
- `evidence_binding_record` JSON files per chapter
- `chapter_evidence_map` JSON files

---

## Mode 3: Citation Gap Mode

**Purpose**: Identify claims that lack sufficient evidence coverage and generate actionable gap reports.

### Entry Conditions
- Evidence bindings completed for current chapter(s)
- Need to assess coverage before polishing

### Operations
1. Load all binding records for target chapter(s)
2. For each binding:
   - Check if `matched_source_ids` is non-empty
   - Evaluate `evidence_strength` against minimum threshold
   - Determine `gap_status`:
     - `covered` — strong binding exists, no action needed
     - `partial` — binding exists but strength is weak or role mismatch
     - `missing` — no binding exists for a required evidence role
     - `not_needed` — claim does not require citation (common knowledge, structural text)
3. Aggregate gaps into `citation_gap_report`
4. For each gap, generate `recommended_action` and `recommended_query`

### Decision Rules for gap_status
| Condition | gap_status |
|-----------|-----------|
| Source matched + strength ≥ medium + role matches | `covered` |
| Source matched + strength = weak OR role mismatch | `partial` |
| No source matched + claim requires citation | `missing` |
| Claim is common knowledge or structural | `not_needed` |

### Exit Conditions
- Gap report generated with zero `missing` entries (or all acknowledged)
- User reviews and approves gap resolution plan

### Output
- `citation_gap_report` JSON per chapter
- Summary: total gaps by status and risk level

---

## Mode 4: Polishing Mode

**Purpose**: Finalize citations, format references, and ensure consistency across the thesis.

### Entry Conditions
- All citation gaps resolved (status: covered or not_needed)
- User requests final polishing

### Operations
1. Verify all `binding_id` references resolve to valid sources
2. Check citation format consistency (GOST, APA, or target style)
3. Cross-validate in-text citations against bibliography
4. Ensure no duplicate citations with conflicting metadata
5. Generate final bibliography in target format
6. Produce final evidence coverage report

### Exit Conditions
- Zero citation errors
- Bibliography complete and formatted
- Coverage report shows 100% for all non-structural claims

### Output
- Formatted bibliography file
- Final evidence coverage report
- Polished thesis text with inline citations

---

## Mode Transition Rules

| From | To | Trigger |
|------|-----|---------|
| Research → Binding | Sources collected and approved |
| Binding → Gap | All claims have binding attempts |
| Gap → Research | `missing` gaps found → re-enter research for those gaps |
| Gap → Polishing | All gaps resolved |
| Polishing → Gap | Errors found during polish → re-enter gap analysis |
| Any → Research | User explicitly requests new research |

---

## State Tracking

Each mode transition is logged with:
- Timestamp
- Source mode → target mode
- Trigger reason
- Affected chapter(s)
- Gap count at transition
