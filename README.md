# PhD Thesis Butler

## Sentence Bank for Russian Academic Writing

**9,602 sentence templates** extracted from **327 candidate and doctoral dissertations** across 23+ scientific fields, organized into a dual-channel classification system.

Built for researchers writing dissertations in Russian — especially engineering, mathematics, and natural sciences. Designed as a skill that any AI agent can load to automatically detect the user's writing context and serve relevant templates.

---

## Overview

| Metric | Value |
|---|---|
| Source dissertations | 327 (BMSTU) |
| Total templates | 9,602 |
| DIS channel (structural) | 5,621 — organized by dissertation section |
| AREF channel (auto-reference) | 3,573 — organized by contribution framing |
| UTILS channel (utility patterns) | 408 — connectives, hedging, numeric reporting |
| Quality 2 (excellent, portable) | ~2,000+ |
| Categories covered | 23 active |

Each template includes: the Russian sentence pattern, slot markers `[...]` for user input, `when_to_use` guidance, and `common_mistakes` warnings.

---

## Classification System

### DIS Channel — By Dissertation Section (11 categories)

| Category | Templates | Usage |
|---|---|---|
| Introduction (INTRO) | ~800 | Opening, motivation, problem statement, objectives |
| Literature Survey (SURVEY) | ~700 | Prior work review, gap identification, positioning |
| Formal Definitions (FORMAL_DEFS) | ~300 | Notation, theorems, definitions, problem formulation |
| Model Construction (MODEL) | ~600 | Mathematical modeling, assumptions, theoretical framework |
| Methodology (METHOD) | ~600 | Algorithm design, procedures, criteria |
| Engineering (ENGINEERING) | ~400 | System design, implementation, prototypes |
| Experiments (EXPERIMENT) | ~500 | Setup, parameters, benchmarks, scenarios |
| Results (RESULT) | ~600 | Findings, tables, figures, comparative analysis |
| Discussion (DISCUSSION) | ~500 | Interpretation, limitations, implications |
| Transition (TRANSITION) | ~300 | Connective phrases between sections |
| Conclusion (CONCLUSION) | ~500 | Summary, contributions, future work |

### AREF Channel — By Автореферат Module (14 modules)

| Module | Purpose |
|---|---|
| Актуальность | Relevance / timeliness |
| Новизна | Novelty claims |
| Цель / Задачи | Goals and task decomposition |
| Объект / Предмет | Object and subject of study |
| Гипотеза | Hypothesis formulation |
| Методы | Methods description |
| Положения | Defended provisions |
| Достоверность | Validity claims |
| Теоретическая значимость | Theoretical significance |
| Практическая значимость | Practical significance |
| Апробация | Approbation / validation |
| Внедрение | Implementation claims |
| Структура | Structural overview |

### UTILS Channel — Utility Patterns (3 kinds)

| Kind | Examples |
|---|---|
| CONNECTIVE | contrast, addition, cause_effect, concession, illustration, sequencing |
| CONSERVATIVE | hedging, limitation_qualifier, suggestion_soft, uncertainty_expression |
| NUMERIC | improvement_report, error_report, distribution_report, comparison_report |

---

## Quality Scoring

Every template is scored 0–2:

| Score | Meaning | Auto-serve? |
|---|---|---|
| **2 (excellent)** | Field-independent, self-contained, ready to use | ✅ Default |
| **1 (good)** | Valid but needs domain adaptation | ⚠️ Fallback only |
| **0 (informative)** | Domain-tied construction | ❌ Manual only |

---

## Data Format (JSONL v2.1)

```json
{
  "id": "DIS_INTRO_0427",
  "text": "В последние годы [Область] привлекает всё большее внимание исследователей в связи с [Фактор/Причина].",
  "kind": "problem_statement",
  "subtype": "relevance_opening",
  "source": "DIS",
  "category": "INTRO",
  "quality_score": 2,
  "semantic_tags": ["relevance", "opening", "trend"],
  "when_to_use": "Для открытия введения, когда нужно обосновать актуальность через возрастающий интерес",
  "common_mistakes": "Не злоупотребляйте — эта конструкция эффективна 1–2 раза на всё введение"
}
```

Master files:
- `data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl` (5,621 lines)
- `data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl` (3,573 lines)
- `data/curated/master/MASTER_UTILS.jsonl` (408 lines)

Quality selections:
- `data/curated/quality/QUALITY2_SELECTION_DIS.jsonl`
- `data/curated/quality/QUALITY2_SELECTION_AREF.jsonl`
- `data/curated/quality/QUALITY2_UTILS.jsonl`

---

## Installation

### Hermes Agent

```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
```

Then load in any session:

```
/skill phd-thesis-butler
```

The agent will automatically detect your writing context and serve templates.

### Claude Code

```bash
mkdir -p ~/.claude/skills/
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```

Add to your CLAUDE.md:

```
Always load ~/.claude/skills/phd-thesis-butler/SKILL.md for Russian academic writing.
```

### Codex CLI

```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

Then reference the template files during writing sessions.

---

## Usage

The skill is designed to be **proactive**: once loaded, the agent scans your writing, detects which dissertation section you're working on, and serves 3–5 relevant templates automatically.

You can also query directly:

```
# Search for specific subtype in quality templates
grep '"subtype":"motivation"' data/curated/quality/QUALITY2_SELECTION_DIS.jsonl | head -5

# Or load a sub-skill for section-specific guidance
/skill phd-thesis-butler/sub_skills/dis_intro
```

---

## Sub-Skills

| Writing section | Load this sub-skill |
|---|---|
| Introduction | `sub_skills/dis_intro` |
| Literature Survey | `sub_skills/dis_survey` |
| Model Construction | `sub_skills/dis_model` |
| Methodology | `sub_skills/dis_method` |
| Experiments | `sub_skills/dis_experiment` |
| Results | `sub_skills/dis_result` |
| Discussion | `sub_skills/dis_discussion` |
| Conclusion | `sub_skills/dis_conclusion` |
| Transitions | `sub_skills/dis_transition` |
| Formal Definitions | `sub_skills/dis_formal_defs` |
| Engineering | `sub_skills/dis_engineering` |
| Avtoreferat | `sub_skills/aref_core` |
| Utils | `sub_skills/utils_core` |

---

## License

**CC BY 4.0** — Free to use, adapt, and redistribute with attribution.

Templates extracted from publicly available BMSTU dissertation materials. All personal identifiers replaced with placeholders.

---

## Citation

```bibtex
@misc{phd-thesis-butler-2025,
  author = {Hou, Tianyu},
  title = {PhD Thesis Butler: Russian Academic Writing Sentence Templates},
  year = {2025},
  howpublished = {\url{https://github.com/Tanue-Hou/phd-thesis-butler}}
}
```

---

## Disclaimer

This tool provides sentence templates for **writing reference only**. It is not intended for automatic generation of academic papers. Users are responsible for compliance with their institution's academic ethics policies.
