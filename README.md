# PhD Thesis Butler（博士论文管家）

<details open>
<summary><strong>🇬🇧 English</strong></summary>

<br>

A **sentence template bank** for **Russian academic writing**. Extracted from **1,042 dissertations + 361 abstracts** across 3 universities (BMSTU, MSU, SPbSU), organized into a **3-layer asset architecture** (GLOBAL → CLUSTER → DISCIPLINE), with **16,735 pure Russian templates** ready to use as a loadable skill for **LLM-based writing agents**. After v3.2 language purity cleanup, all Chinese and English templates have been removed.

> This project provides **portable rhetorical patterns** — template sentences with slot variables. It does **not** copy or redistribute original dissertation text.

---

## For AI Agents: How to Use This Skill

### Role

You are a **Russian academic writing assistant**. Your workflow:

1. **Detect the writing scene** — what section of the thesis is the user working on? (Introduction? Literature survey? Model description? Conclusion?)
2. **Map to the classification system** — find the matching category + subtype
3. **Query the sentence bank** — search the JSONL files for matching templates, prioritizing `quality_score = 2`
4. **Fill the slots** — insert the user's research content into `[...]` placeholders
5. **Adapt to the user's discipline** — if the template is from a different field, adjust terminology and framing
6. **Check common mistakes** — warn the user about anti-patterns listed in `common_mistakes`
7. **Explain your reasoning** — tell the user which template you used and why it fits

### Agent Workflow Diagram

```
User request → Detect writing scene → Map to category/subtype
    → Query JSONL bank → Filter by quality_score
    → Fill slots with user content → Adapt to domain
    → Check common_mistakes → Return result with citations
```

### Example Interaction

**User:** "Help me write the introduction for my dissertation on functional safety of braking systems."

**Agent reasoning:** This is INTRO → motivation + relevance. Query `MASTER_SENTENCEBANK_DIS.jsonl` for `category=INTRO, subtype=motivation`.

**Agent response:**
- Returns 2–3 best-matching templates with quality_score=2
- Fills `[X]` slots with the user's topic
- Explains why each template fits
- Warns about common mistakes (e.g., "Don't start the introduction with 'Во-первых'")

---

## Data Pipeline: How the Templates Were Built

### Phase 1: Corpus Collection (1,403 unique papers — 1,042 dissertations + 361 usable abstracts)

- Source: publicly defended Russian candidate & doctoral dissertations (2015–2025)
- Three universities: **BMSTU** (327 dissertations, no abstracts), **MSU** (589 dissertations + 587 abstracts → 361 usable after OCR filtering), **SPbSU** (727 dissertations, 2 abstracts — SPbSU does not publish abstracts)
- Only PDFs with extractable text were processed. Scanned PDFs (~20% of MSU+SPbSU corpus, 274 DIS + 226 AREF) were excluded from the extraction pipeline.
- Two document types per dissertation:
  - **DIS** (диссертация / full dissertation text)
  - **AREF** (автореферат / author's abstract, ~16–24 pages)

### Phase 2: Template Extraction (LLM-assisted)

Each PDF was processed by an LLM with structured prompts:

1. **Section detection** — identify which part of the thesis the text belongs to (INTRO, SURVEY, MODEL, etc.)
2. **Rhetorical function labeling** — classify each sentence fragment by its communicative purpose (motivation, gap-statement, comparison, etc.)
3. **Slot extraction** — replace domain-specific content with `[SlotName]` markers, keeping the connective structure intact
4. **Metadata annotation** — add `when_to_use`, `common_mistakes`, and `strength` (strong / conservative / neutral)

### Phase 3: Iterative Refinement (Closed Loop)

Each batch of ~15 dissertations went through this cycle:

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  Extract     │────→│  QA Check    │────→│  Aggregate  │
│  (LLM)       │     │  (script)    │     │  (dedup)    │
└─────────────┘     └──────────────┘     └────────────┘
       ↑                    │                    │
       │              ┌─────┴──────┐            │
       │              │  Pass?     │            │
       │              │  ≥95%?     │            │
       │              └─────┬──────┘            │
       │              No    │    Yes             │
       │  ┌──────────┐     │                    │
       └──│ Retry     │◄────┘                    │
          │ (≤3x)    │                           │
          └──────────┘                           ▼
                                        ┌──────────────┐
                                        │  Coverage    │
                                        │  Check       │
                                        └──────┬───────┘
                                               │
                                          ┌────┴────┐
                                          │  Gap?   │
                                          └────┬────┘
                                         Yes   │   No
                                           ┌───┘
                                           ▼
                                    ┌──────────────┐
                                    │  Re-extract   │
                                    │  (targeted)   │
                                    └──────────────┘
```

- **QA Check**: random 2 papers × 2 files per batch; automated script validates schema, slot counts, quality distribution
- **Retry**: failed papers retried up to 3 times, then moved to dead letter
- **Coverage Check**: compares extracted categories/subtypes against `FULL_CLASSIFICATION.yaml` specification
- **Gap Re-extraction**: P0/P1 gaps trigger targeted re-extraction on the same source PDFs

### Phase 4: 3-Layer Asset Architecture

After extraction, templates are classified into three layers (v3.2 counts):

| Layer | Name | Entries | Description |
|-------|------|---------|-------------|
| **L0** | **GLOBAL** | 185 | Cross-cluster universal templates (quality=2 only) |
| **L1** | **CLUSTER** | 9,734 | Discipline clusters: TECH_LIFE (5,699) + HUM_SOC (4,035) |
| **L2** | **DISCIPLINE** | ~10,045 | Per-discipline files across 34 subjects |

Each layer has a `master/` directory with full data and a `quality/` directory with Q2-filtered subsets per category. Layers have **zero template overlap** — every template appears in exactly one layer. Total unique templates across all layers: **16,735** (DIS 9,863 + AREF 6,568 + UTILS 304).

### Phase 5: Quality Filtering & Curation

- **Aggregation**: all batch outputs merged, deduplicated (by paper_id + category + subtype + template text)
- **Quality scoring**: each template rated 0–2 based on portability and slot design
- **Top 50 generation**: for each category, the 50 highest-quality templates selected
- **Final outputs**:
  - `MASTER_SENTENCEBANK_*.jsonl` — full deduplicated corpus
  - `QUALITY2_SELECTION_*.jsonl` — quality-filtered subset
  - `TOP50_BY_CATEGORY/*.md` — curated top templates per category

---

## Version History

| Version | Date | Milestone |
|---------|------|-----------|
| **v3.2** | 2026-05 | Language purity cleanup: removed 24 CN + 1,944 EN templates, 1,570 metadata translated; all templates pure Russian |
| **v3.1.1** | 2026-05 | Asset layer fix: overlap elimination, placeholder migration, PII check, GLOBAL/TECH_LIFE/HUM_SOC zero-overlap verified |
| **v3.1.0** | 2026-05 | Phase 2: MSU+SPbSU dual-channel pipeline (1,042 DIS + 361 AREF), 19,007 total, 3-layer architecture |
| **v2.1** | 2026-05 | Final schema (v2.1), PII sanitization complete, 9,602 entries, gap analysis, JSON schema strict mode |
| **v2.0** | 2026-05 | Full-scale extraction (5,695 → 9,602), quality scoring introduced, 13 sub-skills |
| **v1.0** | 2026-05 | Classification system design, pilot (236 entries from 9 papers), 13 sub-skills architecture |
| **Pilot** | 2026-05 | Pipeline proof-of-concept: 9 dissertations, 236 templates, category/subtype validation |

---

## Current Build (v3.2)

| Metric | DIS | AREF | UTILS | Total |
|--------|-----|------|-------|-------|
| Source dissertations | 1,042 | 361 | — | **1,403 unique** |
| Source universities | 3 (BMSTU + MSU + SPbSU) | — | — | **3** |
| Total templates | **9,863** | **6,568** | **304** | **16,735** |
| Language | Pure Russian ✅ | Pure Russian ✅ | Pure Russian ✅ | **100% pure** |
| Categories / kinds | 11 | 14 | 3 | **28** |
| Quality=2 (excellent) | **8,383** | **2,228** | ~100 | **~10,711** |
| Quality=1 (good) | ~1,200 | ~3,400 | ~180 | **~4,780** |
| Quality=0 (informative) | ~550 | ~700 | ~50 | **~1,300** |

### 3-Layer Architecture

| Layer | Name | Entries | Q2 entries |
|-------|------|---------|------------|
| L0 | GLOBAL (cross-cluster) | 185 | 185 (100%) |
| L1 | TECH_LIFE (technical) | 5,699 | 3,911 (68.6%) |
| L1 | HUM_SOC (humanities) | 4,035 | 2,484 (61.6%) |
| L2 | DISCIPLINE (34 subjects) | ~10,045 | 6,583 (65.5%) |
| | **Zero overlap** | **0** | — |

---

## Classification System (11 + 14 + 3)

### DIS Channel — Dissertation Sections

| Category | Subtypes | Description |
|----------|----------|-------------|
| **INTRO** | motivation, relevance, problem_statement, objective, tasks, object_subject, contributions_preview, thesis_structure | Introduction & background |
| **SURVEY** | taxonomy, comparison, limitations_of_prior, gap, positioning, evaluation_axes, baseline_selection | Literature review |
| **MODEL** | assumptions, boundary_conditions, uncertainties, errors, notation, units, coordinate_frames, parameter_identifiability, constraints, simplifications | Theoretical framework |
| **METHOD** | pipeline_overview, input_output, algorithm_steps, parameter_setting, complexity, stability_claims_conservative, implementation_details, ablation_plan | Methodology & algorithms |
| **EXPERIMENT** | data_description, scenario_design, metrics, baselines, train_test_split, hyperparams, reproducibility, statistical_reporting | Experimental setup |
| **RESULT** | numeric_reporting, improvement_reporting, distribution_reporting, case_studies, failure_cases, comparison_table | Results presentation |
| **DISCUSSION** | mechanism_explanation, sensitivity, tradeoff, generalization, threat_to_validity, interpretation_hedged | Analysis & discussion |
| **CONCLUSION** | summary, contributions_recap, applicability, limitations, future_work | Conclusion |
| **TRANSITION** | section_openers, section_closers, paragraph_linkers, signposting | Transitional phrases |
| **FORMAL_DEFS** | definition, lemma_style, constraint_introductions, symbol_introductions | Formal definitions |
| **ENGINEERING** | deployment, real_time, resource_usage, code_reproducibility, practical_complexity | Engineering implementation |

### AREF Channel — Abstract Modules

| Category | Description |
|----------|-------------|
| **АКТУАЛЬНОСТЬ** | Research relevance (practical demand, theoretical gap, regulatory context, trends) |
| **ОБЪЕКТ_ПРЕДМЕТ** | Object and subject of research |
| **ЦЕЛЬ_ЗАДАЧИ** | Goal and tasks |
| **МЕТОДЫ** | Research methods |
| **НОВИЗНА** | Scientific novelty |
| **НОВИЗНА_ФОРМУЛИРОВКИ** | Novelty phrasing variants |
| **ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ** | Theoretical significance |
| **ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ** | Practical significance |
| **ПОЛОЖЕНИЯ** | Defended propositions |
| **РЕЗУЛЬТАТЫ** | Results |
| **АПРОБАЦИЯ** | Validation & approval |
| **ПУБЛИКАЦИИ** | Publications |
| **СТРУКТУРА** | Structure & volume |
| **ВЫВОДЫ** | Conclusions |

### UTILS Channel — Functional Language

| Kind | Description | Examples |
|------|-------------|----------|
| **CONNECTIVE** | Transitional & structural phrases | "Однако...", "С одной стороны...", "Более того..." |
| **CONSERVATIVE** | Hedging & cautious language | "Предположительно...", "Вероятно...", "Можно предположить..." |
| **NUMERIC** | Quantitative reporting patterns | "увеличение на X%", "ошибка составляет Y" |

---

## Data Format (JSONL v2.1)

Each line in the `.jsonl` files is a JSON object:

```json
{
  "paper_id": "1090",
  "source": "DIS",
  "record_type": "TEMPLATE",
  "category": "INTRO",
  "subtype": "objective",
  "function": "Цель диссертации",
  "template": "Целью диссертационной работы является разработка и исследование [объект_разработки] для повышения эффективности [целевая_эффективность].",
  "slots": ["объект_разработки", "целевая_эффективность"],
  "when_to_use": "Во введении при формулировании цели.",
  "common_mistakes": ["Цель слишком общая", "Не указан ожидаемый результат"],
  "strength": "neutral",
  "quality_score": 2,
  "schema_version": "2.1"
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paper_id` | string | yes | Source dissertation ID (3–4 digits) |
| `source` | string | yes | "DIS" (dissertation) or "AREF" (abstract) |
| `record_type` | string | yes | "TEMPLATE" or "UTIL" |
| `category` | string | conditional | DIS/AREF category (required for TEMPLATE) |
| `subtype` | string | conditional | Rhetorical function subtype |
| `kind` | string | conditional | UTIL kind (CONNECTIVE/CONSERVATIVE/NUMERIC) |
| `function` | string | no | Human-readable function description |
| `template` | string | yes | Sentence pattern with `[slot_name]` or `___` placeholders |
| `slots` | array | no | Variable name array for placeholders |
| `when_to_use` | string | no | Usage guidance for the template |
| `common_mistakes` | array | no | Common writing errors to avoid |
| `strength` | string | no | "strong" / "conservative" / "neutral" |
| `quality_score` | integer | yes | 0 (domain-tied) / 1 (adaptable) / 2 (portable) |
| `schema_version` | string | yes | Always "2.1" |

---

## Usage Methods

### Method 1: Writing Assistance (for AI agents)

1. **Identify the writing scene** (e.g., "writing the introduction")
2. **Map to category/subtype** (INTRO → motivation, problem_statement, etc.)
3. **Query the sentence bank** (search by category + subtype in the JSONL files)
4. **Prioritize quality=2 templates** for maximum portability
5. **Fill slots** with the user's domain-specific content
6. **Adapt to the user's field** — a template from aerospace engineering can work for automotive safety with terminology substitution
7. **Check `common_mistakes`** — warn the user proactively
8. **Explain which template was used and why**

### Method 2: Quality Assessment & Polishing

1. Analyze the user's draft sentence → classify into category + subtype
2. Compare against the sentence bank — does it match an established rhetorical pattern?
3. Check against `common_mistakes` — any anti-patterns in the user's writing?
4. Suggest replacements with higher-quality_score alternatives
5. Adjust `strength` — is the claim too strong or too weak for the context?

### Method 3: Template Querying

- By category: `category=INTRO` → all introduction templates
- By subtype: `subtype=motivation` → all motivation-framing templates
- By quality: `quality_score=2` → only excellent, portable templates
- By strength: `strength=conservative` → only cautious/highly qualified language
- Mixed: `category=DISCUSSION & subtype=mechanism_explanation & quality_score=2`

---

## Quality Scoring

| Score | Label | Meaning | Selection Strategy |
|-------|-------|---------|-------------------|
| **2** | Excellent | Field-independent rhetorical pattern. Ready to use. Replace `[slots]` with any domain. | Always prefer these first |
| **1** | Good | Needs domain adaptation. The pattern works but has some domain-specific framing. | Use when no quality=2 match exists |
| **0** | Informative | Domain-tied example. Heavy manual review needed to adapt. | Only use as inspiration |

Quality distribution in the current build: **~2,000 quality=2 / ~6,250 quality=1 / ~1,300 quality=0**

---

## Files

### Master (full deduplicated corpus, pure Russian)
| File | Source | Records |
|------|--------|---------|
| `MASTER_SENTENCEBANK_DIS.jsonl` | Dissertation body | 10,124 |
| `MASTER_SENTENCEBANK_AREF.jsonl` | Author's abstract | 6,587 |
| `MASTER_UTILS.jsonl` | Functional language | 328 |

### Quality (filtered subsets)
| File | Description |
|------|-------------|
| `QUALITY2_SELECTION_DIS.jsonl` | DIS templates with quality_score ≥ 2 (8,383) |
| `QUALITY2_SELECTION_AREF.jsonl` | AREF templates with quality_score ≥ 2 (2,228) |
| `QUALITY2_UTILS.jsonl` | UTIL phrases with quality_score ≥ 2 |
| `TOP50_BY_CATEGORY/*.md` | Top 50 templates per category, in Markdown |

### Assets (3-layer structure)
| Layer | Directory | Description |
|-------|-----------|-------------|
| L0 | `assets/global/` | Cross-cluster universal templates (185) |
| L1 | `assets/cluster/TECH_LIFE/` | Technical/life sciences cluster (5,699) |
| L1 | `assets/cluster/HUM_SOC/` | Humanities/social sciences (4,035) |
| L2 | `assets/discipline/` | Per-discipline files (34 subjects) |

### Gaps (coverage reports)
| File | Description |
|------|-------------|
| `gap_list_DIS.json` | Coverage gaps across DIS categories |

---

## Installation

### Hermes (recommended)
```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
# Then load with:
/skill phd-thesis-butler
```

### Claude Code
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
# Then reference in CLAUDE.md
```

### Codex CLI
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

---

## Disclaimer

### Academic Integrity

**This repository provides sentence templates and writing patterns for drafting and polishing assistance only.** It is designed to help researchers express their ideas in well-structured academic Russian, not to generate or reproduce content.

Users are solely responsible for:
- **Factual verification** — all technical claims, data, and references must be verified by the author
- **Citation compliance** — proper attribution of sources is the author's responsibility
- **Plagiarism checking** — all generated text must be reviewed for originality
- **Academic integrity** — compliance with the author's institution and publisher guidelines
- **Domain adaptation** — templates must be adapted to the specific research domain; blind copying may produce inaccurate or misleading statements

### Data Origin

- All templates were extracted from **publicly defended dissertations** available in open-access repositories
- The project stores **rhetorical patterns only** (connective structures with slot variables), not original copyrighted text
- No full sentences, paragraphs, or original findings from any single dissertation are reproduced
- Users who require the original context should consult the source dissertations directly

### Limitation of Liability

The project maintainers and contributors provide this material **"as is"**, without warranty of any kind, express or implied. In no event shall the maintainers be liable for any claim, damages, or other liability arising from the use of this software or data.

---

## License

**CC BY 4.0** — Creative Commons Attribution 4.0 International

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — you must give appropriate credit, provide a link to the license, and indicate if changes were made

Full license: https://creativecommons.org/licenses/by/4.0/

---

## Citation

If you use this resource in your work, please cite:

```bibtex
@misc{phd-thesis-butler,
  author = {Tanue Hou},
  title = {PhD Thesis Butler: A Sentence Template Bank for Russian Academic Writing},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Tanue-Hou/phd-thesis-butler}
}
```

</details>

<br>

<details>
<summary><strong>🇷🇺 Русский</strong></summary>

<br>

**Банк шаблонов** для **академического письма на русском языке**. Извлечён из **1 042 диссертаций + 361 автореферата** из 3 университетов (МГТУ им. Баумана, МГУ, СПбГУ), организован в **3-уровневую архитектуру** (GLOBAL → CLUSTER → DISCIPLINE). Всего **16 735 шаблонов**, прошедших проверку на языковую чистоту (удалены все китайские и английские вкрапления).

> Проект предоставляет **переносимые риторические паттерны** — шаблонные предложения со слотами. Он **не копирует и не распространяет** исходный текст диссертаций.

---

## Текущая сборка (v3.2)

| Показатель | DIS | AREF | UTILS | Всего |
|-----------|-----|------|-------|-------|
| Источники | 1 042 дисс. | 361 авт. | — | **1 403** |
| Университеты | 3 (МГТУ+МГУ+СПбГУ) | — | — | **3** |
| Всего шаблонов | **9 863** | **6 568** | **304** | **16 735** |
| Язык | Чистый русский ✅ | Чистый русский ✅ | Чистый русский ✅ | **100%** |
| Категорий | 11 | 14 | 3 | **28** |
| Quality=2 | **8 383** | **2 228** | ~100 | **~10 711** |

### 3-уровневая архитектура

| Уровень | Название | Записей | Q2 |
|---------|----------|---------|-----|
| L0 | GLOBAL (междисциплинарные) | 185 | 185 (100%) |
| L1 | TECH_LIFE (технические науки) | 5 699 | 3 911 (68,6%) |
| L1 | HUM_SOC (гуманитарные науки) | 4 035 | 2 484 (61,6%) |
| L2 | DISCIPLINE (34 дисциплины) | ~10 045 | 6 583 (65,5%) |
| | **Нулевое пересечение** | **0** | — |

---

## Цель

Помочь исследователям, пишущим диссертации на русском языке, находить и использовать устоявшиеся риторические конструкции для каждого раздела работы — от введения до заключения.

Шаблоны извлечены из реальных кандидатских и докторских диссертаций (2015–2025), защищённых в открытых диссертационных советах.

---

## Установка

### Hermes (рекомендуется)
```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
# Загрузка:
/skill phd-thesis-butler
```

### Claude Code
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```

### Codex CLI
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

---

## Отказ от ответственности

Данный репозиторий предоставляет **только шаблонные фразы** для помощи в академическом письме. Все шаблоны извлечены из **общедоступных диссертаций**. Пользователь несёт полную ответственность за:
- проверку фактической точности
- соблюдение правил цитирования
- проверку на плагиат
- адаптацию шаблонов к своей предметной области

---

## Лицензия

**CC BY 4.0** — Creative Commons Attribution 4.0 International

</details>

<br>

<details
<summary><strong>🇨🇳 中文</strong></summary>

<br>

一个面向**俄语学术写作**的句式模板库（Sentence Bank）。从 **3 所高校（BMSTU + MSU + SPbSU）、1,042 篇论文 + 361 篇摘要**中抽取，按 **三级资产架构**（GLOBAL → CLUSTER → DISCIPLINE）组织，共 **19,007 条去重模板**，可作为 **LLM 写作智能体**的可加载技能库。

> 本项目提供**可迁移的修辞模式**（带槽位的模板句式），**不复制或再分发**原论文受著作权保护的文本内容。

---

## 给 AI 智能体的使用说明

### 你的角色

你是一名 **俄语学术写作助手**。工作流程：

1. **检测写作场景** — 用户在写论文的哪一部分？（引言？文献综述？模型描述？结论？）
2. **映射到分类体系** — 找到匹配的 category + subtype
3. **检索句式库** — 在 JSONL 文件中按 category + subtype 搜索，优先 `quality_score = 2`
4. **填入槽位** — 将用户的研究内容填入 `[X]` 占位符
5. **领域适配** — 如果模板来自不同领域，调整术语和表述框架
6. **检查常见错误** — 主动提示 `common_mistakes` 中的反模式
7. **解释推理过程** — 告诉用户你用了哪个模板以及为什么适合

### 智能体工作流程

```
用户请求 → 检测写作场景 → 映射到 category/subtype
    → 检索 JSONL 库 → 按 quality_score 筛选
    → 填入用户内容 → 领域适配
    → 检查 common_mistakes → 返回结果并说明依据
```

---

## 数据处理流程

### 阶段一：语料收集（1,403 篇独立论文 — 1,042 篇正文 + 361 篇可提取摘要）

- 来源：2015–2025 年在公开数据库中可获取的俄罗斯学位论文
- 三所高校：**BMSTU**（327 篇正文，无摘要）、**MSU**（589 篇正文 + 587 篇摘要 → OCR 过滤后 361 篇可用）、**SPbSU**（727 篇正文，2 篇摘要 — SPbSU 不公开摘要）
- 仅处理可提取文本的 PDF。扫描版 PDF（MSU+SPbSU 约 20%，274 篇正文 + 226 篇摘要）已从抽取管线中排除
- 每篇论文有两种文档：
  - **DIS**（диссертация / 论文全文）
  - **AREF**（автореферат / 作者摘要）

### 阶段二：模板抽取（LLM 辅助）

每篇 PDF 由 LLM 按结构化提示处理：

1. **章节检测** — 判断文本属于论文的哪一部分（INTRO, SURVEY, MODEL 等）
2. **修辞功能标注** — 将句子片段按交际目的分类（动机、空白陈述、比较等）
3. **槽位提取** — 用 `[槽位名]` 替换领域特定内容，保留连接结构
4. **元数据标注** — 添加 `when_to_use`, `common_mistakes`, `strength`

### 阶段三：迭代式精炼（闭环）

每批 ~15 篇论文经过以下循环：

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│ 抽取     │──→│ QA 检查  │──→│ 聚合去重  │
│ (LLM)    │   │ (脚本)   │   │          │
└──────────┘   └──────────┘   └──────────┘
     ↑              │              │
     │         ┌────┴─────┐       │
     │         │ 通过?    │       │
     │         │ ≥95%?   │       │
     │         └────┬─────┘       │
     │        否   │   是         │
     │  ┌──────┐   │              │
     └──│ 重试  │◄──┘              │
        │ (≤3次)│                  │
        └──────┘                  ▼
                           ┌─────────┐
                           │ 覆盖检查 │
                           └────┬────┘
                                │
                           ┌───┴───┐
                           │ 缺口？│
                           └───┬───┘
                          是  │   否
                         ┌────┘
                         ▼
                    ┌───────────┐
                    │ 定向补抽   │
                    └───────────┘
```

- **QA 检查**：每批随机抽 2 篇 × 2 文件；自动校验 schema、slot 数量、质量分布
- **重试**：不合格论文最多重试 3 次，超则进入死信队列
- **覆盖检查**：对照 `FULL_CLASSIFICATION.yaml` 规范检查覆盖缺口
- **缺口补抽**：P0/P1 缺口触发针对同一源 PDF 的定向重新抽取

### 阶段四：质量过滤与精选

- **聚合**：合并所有批次产出，去重（按 paper_id + category + subtype + template）
- **质量评分**：每条模板评分 0–2，基于可迁移性和槽位设计
- **Top 50 生成**：每个类别选出 50 条最高质量的模板
- **最终产出**：`MASTER_*.jsonl`（全量）+ `QUALITY2_SELECTION_*.jsonl`（精选）+ `TOP50_BY_CATEGORY/*.md`

---

## 版本历史

| 版本 | 日期 | 里程碑 |
|------|------|--------|
| **v3.2** | 2026-05 | 语言纯净度清洗：删除 24 条中文 + 1,944 条英文模板，修复 1,570 处中文元数据；所有模板为纯正俄语 |
| **v3.1.1** | 2026-05 | 资产修复：消除层级重叠、占位符迁移、PII 脱敏，GLOBAL/TECH_LIFE/HUM_SOC 零重叠验证 |
| **v3.1.0** | 2026-05 | Phase 2：MSU+SPbSU 双通道抽取上线，19,007 条，三级资产架构 |
| **v2.1** | 2026-05 | 最终 schema (v2.1)，PII 脱敏完成，9,602 条，缺口分析，JSON schema 严格模式 |
| **v2.0** | 2026-05 | 全量抽取（5,695 → 9,602），引入质量评分，13 个子 skill |
| **v1.0** | 2026-05 | 分类体系设计，试点 9 篇 236 条，13 子 skill 架构 |
| **Pilot** | 2026-05 | 管线概念验证：9 篇论文，236 条模板，category/subtype 验证 |

---

## 当前数据统计（v3.2）

| 指标 | DIS | AREF | UTILS | 合计 |
|--------|-----|------|-------|------|
| 来源论文 | 1,042 | 361 | — | **1,403 篇** |
| 来源高校 | 3 (BMSTU + MSU + SPbSU) | — | — | **3** |
| 模板总数 | **9,863** | **6,568** | **304** | **16,735** |
| 语言纯度 | 纯俄语 ✅ | 纯俄语 ✅ | 纯俄语 ✅ | **100% 纯正** |
| 类别/种类 | 11 | 14 | 3 | **28** |
| Quality=2（优秀） | **8,383** | **2,228** | ~100 | **~10,711** |
| Quality=1（可用） | ~1,200 | ~3,400 | ~180 | **~4,780** |
| Quality=0（参考） | ~550 | ~700 | ~50 | **~1,300** |

### 三级资产架构

| 层级 | 名称 | 条数 | Q2 |
|------|------|------|----|
| L0 | GLOBAL（跨学科通用） | 185 | 185 (100%) |
| L1 | TECH_LIFE（技术/生命科学） | 5,699 | 3,911 (68.6%) |
| L1 | HUM_SOC（人文/社会科学） | 4,035 | 2,484 (61.6%) |
| L2 | DISCIPLINE（34 个学科） | ~10,045 | 6,583 (65.5%) |
| | 跨层零重叠 | **0** | — |

---

## 分类体系

### DIS 通道（11 类）

| 类别 | 子类数量 | 说明 |
|----------|----------|-------------|
| **INTRO** | 8 | 引言与背景 |
| **SURVEY** | 7 | 文献综述 |
| **MODEL** | 10 | 理论模型构建 |
| **METHOD** | 8 | 方法与算法 |
| **EXPERIMENT** | 8 | 实验与验证 |
| **RESULT** | 6 | 结果汇报 |
| **DISCUSSION** | 6 | 讨论与分析 |
| **CONCLUSION** | 5 | 结论 |
| **TRANSITION** | 4 | 过渡承接 |
| **FORMAL_DEFS** | 4 | 形式化定义 |
| **ENGINEERING** | 5 | 工程实现 |

### AREF 通道（14 类）

| 类别 | 说明 |
|----------|-------------|
| **АКТУАЛЬНОСТЬ** | 选题相关性（实践需求、理论空白、法规背景、趋势动机） |
| **ОБЪЕКТ_ПРЕДМЕТ** | 研究对象与主题 |
| **ЦЕЛЬ_ЗАДАЧИ** | 目标与任务 |
| **МЕТОДЫ** | 研究方法 |
| **НОВИЗНА** | 科学新颖性 |
| **НОВИЗНА_ФОРМУЛИРОВКИ** | 新颖性表述变体 |
| **ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ** | 理论意义 |
| **ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ** | 实践意义 |
| **ПОЛОЖЕНИЯ** | 答辩论点 |
| **РЕЗУЛЬТАТЫ** | 结果 |
| **АПРОБАЦИЯ** | 验证与审批 |
| **ПУБЛИКАЦИИ** | 出版物 |
| **СТРУКТУРА** | 结构与篇幅 |
| **ВЫВОДЫ** | 结论 |

### UTILS 通道（3 类）

| 种类 | 说明 | 示例 |
|------|-------------|----------|
| **CONNECTIVE** | 过渡与结构短语 | "Однако...", "С одной стороны..." |
| **CONSERVATIVE** | 保守与不确定性措辞 | "Предположительно...", "Вероятно..." |
| **NUMERIC** | 数字汇报模式 | "увеличение на X%", "ошибка составляет Y" |

---

## 数据格式

每条 JSONL 记录的结构：

```json
{
  "paper_id": "1090",
  "source": "DIS",
  "record_type": "TEMPLATE",
  "category": "INTRO",
  "subtype": "objective",
  "function": "Цель диссертации",
  "template": "Целью диссертационной работы является разработка и исследование [объект_разработки] для повышения эффективности [целевая_эффективность].",
  "slots": ["объект_разработки", "целевая_эффективность"],
  "when_to_use": "Во введении при формулировании цели.",
  "common_mistakes": ["Цель слишком общая", "Не указан ожидаемый результат"],
  "strength": "neutral",
  "quality_score": 2,
  "schema_version": "2.1"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|-------|------|------|-------------|
| `paper_id` | string | 是 | 来源论文 ID（3–4 位数字） |
| `source` | string | 是 | "DIS"（论文）或 "AREF"（摘要） |
| `record_type` | string | 是 | "TEMPLATE"（模板）或 "UTIL"（功能短语） |
| `category` | string | 条件 | DIS/AREF 分类（TEMPLATE 必填） |
| `subtype` | string | 条件 | 修辞功能子类 |
| `kind` | string | 条件 | UTIL 种类（CONNECTIVE/CONSERVATIVE/NUMERIC） |
| `function` | string | 否 | 功能描述 |
| `template` | string | 是 | 带 `[槽位名]` 或 `___` 的句式模式 |
| `slots` | array | 否 | 占位符的变量名数组 |
| `when_to_use` | string | 否 | 使用时机说明 |
| `common_mistakes` | array | 否 | 常见写作错误 |
| `strength` | string | 否 | "strong" / "conservative" / "neutral" |
| `quality_score` | integer | 是 | 0（领域绑定）/ 1（可适配）/ 2（高可迁移） |
| `schema_version` | string | 是 | 固定为 "2.1" |

---

## 使用方式

### 方式一：写作辅助（AI 智能体）

1. **识别写作场景**（如"正在写引言"）
2. **映射 category/subtype**（INTRO → motivation, problem_statement 等）
3. **检索句式库**（在 JSONL 文件中按 category + subtype 搜索）
4. **优先 quality=2 的模板**以获得最佳可迁移性
5. **填入槽位** — 将用户的研究内容填入占位符
6. **领域适配** — 来自航空工程的模板，替换术语后可用于汽车安全
7. **检查 common_mistakes** — 主动向用户提示风险
8. **解释所使用的模板及选择理由**

### 方式二：质量评估与润色

1. 分析用户草稿句子 → 分类到 category + subtype
2. 与句式库对比 — 是否符合成熟的修辞模式？
3. 对照 common_mistakes 检查 — 是否存在反模式？
4. 推荐更高质量的替代方案
5. 调整语气强度 — 主张太强或太弱？

### 方式三：句式查询

- 按类别：`category=INTRO` → 所有引言模板
- 按子类：`subtype=motivation` → 所有动机框架模板
- 按质量：`quality_score=2` → 仅优秀模板
- 按语气：`strength=conservative` → 仅谨慎表述
- 组合：`category=DISCUSSION & subtype=mechanism_explanation & quality_score=2`

---

## 安装

### Hermes（推荐）
```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
# 然后加载：
/skill phd-thesis-butler
```

### Claude Code
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
# 在 CLAUDE.md 中引用
```

### Codex CLI
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

---

## 免责声明

### 学术诚信

**本仓库提供的句式模板仅用于润色与写作辅助。** 项目旨在帮助研究者以规范的俄语学术表达阐述其研究内容，而非用于生成或复制内容。

使用者需自行承担以下责任：
- **事实核查** — 所有技术声明、数据和参考文献必须由作者验证
- **引用合规** — 正确标注来源是作者的责任
- **查重检测** — 所有生成的文本必须进行原创性检查
- **学术诚信** — 遵守所在机构和出版方的指导方针
- **领域适配** — 模板必须适配到具体研究领域，盲目复制可能产生不准确或误导性陈述

### 数据来源

- 所有模板从**公开答辩的学位论文**中提取
- 项目仅存储**修辞模式**（带槽位的连接结构），不包含原论文著作权保护的文本
- 不复制任何单篇论文的完整句子、段落或研究发现
- 需要原始上下文的用户应直接查阅源论文

### 责任限制

项目维护者和贡献者按**"现状"**提供本材料，不作任何明示或暗示的保证。在任何情况下，维护者均不对因使用本软件或数据而产生的任何索赔、损害或其他法律责任负责。

---

## 许可证

**CC BY 4.0** — 知识共享署名 4.0 国际许可

您可以自由地：
- **共享** — 在任何媒介以任何格式复制和再分发本材料
- **改编** — 基于本材料进行修改、转换或创作

须遵守以下条件：
- **署名** — 必须给出适当的署名，提供指向本许可的链接，并标明是否做了修改

完整许可：https://creativecommons.org/licenses/by/4.0/

---

## 引用

如果您在研究中使用本资源，请引用：

```bibtex
@misc{phd-thesis-butler,
  author = {Tanue Hou},
  title = {PhD Thesis Butler: A Sentence Template Bank for Russian Academic Writing},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Tanue-Hou/phd-thesis-butler}
}
```

</details>
