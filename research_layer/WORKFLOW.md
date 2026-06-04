# Research Layer — Workflow Guide (v5.2)

## Overview

Research Layer v5.2 introduces three structured research workflows that standardize
the process of literature discovery, intake, and synthesis for PhD-level work.

---

## 1. Research Planning Mode

**Purpose:** Given a research direction, output a complete search strategy.

**Input:** A free-text description of the research topic/question.

**Output:** A structured search plan containing:
- Core keywords (Russian + English)
- Domain-specific terminology and abbreviations
- VAK specialty codes (candidate list)
- eLIBRARY search queries (ready to paste)
- DisserCat search queries
- Recommended high-impact journals
- Suggested filters (year range, language, document type)

**Workflow:**
1. User provides research direction (e.g. "оценка состояния трансмиссии автомобиля")
2. Agent selects the appropriate discipline template from `templates/`
3. Agent enriches keywords using domain knowledge + template suggestions
4. Agent generates ready-to-use search strings for eLIBRARY and DisserCat
5. Agent outputs the Search Plan as structured Markdown

**Template selection guide:**
| Domain | Template |
|--------|----------|
| Automation, control, vehicle engineering, state estimation | AUTOMATION_CONTROL.md |
| Engineering, physics, math, CS, chemistry | SCI_TECH.md |
| Agriculture, forestry, medicine | AGRI_MED.md |
| Arts, sports, music, design | ARTS_SPORTS.md |
| Humanities, political science, economics, law, education | HUM_POL_ECON.md |

---

## 2. Manual Literature Intake Mode

**Purpose:** Process a batch of manually collected literature into a standardized format.

**Input:** Literature records in one of:
- JSON array (e.g. from eLIBRARY export or manual entry)
- CSV / Markdown table
- Plain text with bibliographic info

**Output:** Standardized literature dataset:
1. Normalized records (unified schema)
2. Deduplication (by DOI, title similarity, or author+year+title)
3. Automatic categorization by theme / subtopic
4. Summary brief (statistics: count, year distribution, source distribution)

**Standard record schema:**
```json
{
  "id": "auto-generated",
  "title": "",
  "authors": [],
  "year": null,
  "journal": "",
  "doi": "",
  "source": "elibrary|dissercat|manual",
  "keywords": [],
  "abstract": "",
  "category": "",
  "notes": ""
}
```

**Workflow:**
1. User provides raw literature data
2. Agent parses and normalizes to standard schema
3. Agent deduplicates (fuzzy title match, DOI exact match)
4. Agent categorizes by thematic clusters
5. Agent outputs `intake_report.md` with stats + normalized dataset

---

## 3. Literature Review Brief Mode

**Purpose:** Generate a structured literature review from the standardized dataset.

**Input:** Standardized literature records (from Mode 2 or pre-existing dataset).

**Output:** A structured review brief containing:
- **Context paragraph** — why this topic matters, research gap
- **Thematic clusters** — groups of related works with synthesis
- **Methodology landscape** — what methods are used across the literature
- **Key findings summary** — consolidated results
- **Gaps and contradictions** — what's missing or debated
- **Recommended next steps** — suggested reading order, open questions
- **Bibliography** — formatted reference list

**Workflow:**
1. User triggers review generation from existing dataset
2. Agent clusters works by theme/methodology
3. Agent synthesizes per-cluster summaries
4. Agent identifies gaps and contradictions across clusters
5. Agent produces the review brief in Markdown

---

## Directory Structure

```
research_layer/
├── WORKFLOW.md              ← this file
├── templates/               ← discipline-specific search templates
│   ├── AUTOMATION_CONTROL.md
│   ├── SCI_TECH.md
│   ├── AGRI_MED.md
│   ├── ARTS_SPORTS.md
│   └── HUM_POL_ECON.md
├── examples/                ← sample data for validation
│   ├── elibrary_sample.json
│   ├── dissercat_sample.json
│   └── review_output.md
└── sources/                 ← actual literature data (populated by user)
```

---

## Usage with Hermes Agent

To invoke a workflow, use natural language:

- **Planning:** "Составь поисковый стратегию по теме: [topic]"
- **Intake:** "Обработай эту подборку литературы: [paste JSON/table]"
- **Review:** "Сгенерируй обзор литературы из имеющегося датасета"

The agent will automatically select the right template and follow the workflow.
