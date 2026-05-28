# PhD Thesis Butler (博士论文管家)

**Language:** English | [中文](README.zh-CN.md)

A skill-pack for **Russian academic writing**: a curated **sentence template bank** extracted from candidate & doctoral dissertations, organized into dual channels (DIS + AREF) and served through a loadable "skill" interface for Hermes / Claude Code / Codex-style agents.

> This project focuses on **portable expression patterns** (templates with slots), not on copying original text.

---

## Overview

**Corpus & output (current build):**

- Source dissertations: **327**
- Total templates: **9,602**
  - DIS channel: **5,621** (by dissertation section)
  - AREF channel: **3,573** (by автореферат module)
  - UTILS channel: **408** (connectives / hedging / numeric reporting)
- Quality 2 (excellent, portable): **~2,000+**
- Active categories/modules: **23**

Each template includes:
- Russian pattern with slot markers `[...]`
- `when_to_use` guidance
- `common_mistakes` warnings
- `quality_score` (0–2)

---

## Classification System

### DIS channel — by dissertation section (11 categories)

- INTRO — opening, motivation, problem statement, objectives
- SURVEY — prior work review, gap identification, positioning
- FORMAL_DEFS — notation, theorems, definitions, formulation
- MODEL — modeling, assumptions, theoretical framework
- METHOD — algorithms, procedures, criteria
- ENGINEERING — implementation, prototypes, systems
- EXPERIMENT — setup, parameters, scenarios, benchmarks
- RESULT — findings, figures/tables, comparisons
- DISCUSSION — interpretation, limitations, implications
- TRANSITION — cross-section connective phrasing
- CONCLUSION — summary, contributions, future work

### AREF channel — by автореферат module (14 modules)

Includes: актуальность, новизна, цель/задачи, объект/предмет, методы, положения, достоверность, теоретическая/практическая значимость, апробация, внедрение, структура, выводы, etc.

### UTILS channel — utility patterns (3 kinds)

- CONNECTIVE — contrast/addition/cause-effect/concession/illustration/sequencing
- CONSERVATIVE — hedging, limitation qualifiers, uncertainty expressions
- NUMERIC — improvement/error/distribution/comparison reporting patterns

---

## Quality Scoring

Templates are scored 0–2:

- **2 (excellent)**: field-independent, self-contained, ready to use
- **1 (good)**: valid but needs domain adaptation
- **0 (informative)**: domain-tied; manual review required

---

## Data Format (JSONL v2.1)

Example entry:

```json
{
  "id": "DIS_INTRO_0427",
  "text": "В последние годы [Область] привлекает всё большее внимание исследователей в связи с [Фактор/Причина].",
  "source": "DIS",
  "category": "INTRO",
  "quality_score": 2,
  "when_to_use": "Для открытия введения, когда нужно обосновать актуальность через возрастающий интерес",
  "common_mistakes": "Не злоупотребляйте — эта конструкция эффективна 1–2 раза на всё введение"
}
```

Master files:

- `data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl`
- `data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl`
- `data/curated/master/MASTER_UTILS.jsonl`

Quality selections:

- `data/curated/quality/QUALITY2_SELECTION_DIS.jsonl`
- `data/curated/quality/QUALITY2_SELECTION_AREF.jsonl`
- `data/curated/quality/QUALITY2_UTILS.jsonl`

---

## Installation

### Hermes (skill install)

```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
```

Load in a session:

```
/skill phd-thesis-butler
```

### Claude Code

```bash
mkdir -p ~/.claude/skills/
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```

Then add in CLAUDE.md (example):

```
Always load ~/.claude/skills/phd-thesis-butler/SKILL.md for Russian academic writing.
```

### Codex CLI

```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

---

## Usage

The skill is designed to be **proactive**: once loaded, the agent can detect your writing context (e.g., INTRO vs MODEL) and serve a small set of relevant templates.

You can also query directly:

```bash
# Search by category/subtype in quality templates
grep '"category":"INTRO"' data/curated/quality/QUALITY2_SELECTION_DIS.jsonl | head -5
```

Or load a section sub-skill:

```
/skill phd-thesis-butler/sub_skills/dis_intro
```

---

## Sub-Skills (by writing section)

- `sub_skills/dis_intro`
- `sub_skills/dis_survey`
- `sub_skills/dis_model`
- `sub_skills/dis_method`
- `sub_skills/dis_experiment`
- `sub_skills/dis_result`
- `sub_skills/dis_discussion`
- `sub_skills/dis_conclusion`
- `sub_skills/dis_transition`
- `sub_skills/dis_formal_defs`
- `sub_skills/dis_engineering`
- `sub_skills/aref_core`
- `sub_skills/utils_core`

---

## Disclaimer (Important)

This repository provides **sentence templates and writing patterns** for polishing and drafting assistance. It does not guarantee that any output is suitable for direct submission as a dissertation, paper, or academic work.

You are responsible for:

- factual verification, citations, and compliance with your institution/journal rules
- plagiarism/similarity checks and proper quotation/paraphrasing
- ensuring academic integrity and originality

If you directly submit AI-generated text or unreviewed template-filled content, any resulting academic or legal risk is solely your responsibility.

---

## License

**CC BY 4.0** — Free to use, adapt, and redistribute with attribution.

All personal identifiers in the templates have been replaced with placeholders.

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
