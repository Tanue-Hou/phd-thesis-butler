# PhD Thesis Butler（博士论文管家）

<details open>
<summary><strong>🇬🇧 English</strong></summary>

<br>

A skill-pack for **Russian academic writing**: a curated **sentence template bank** extracted from candidate & doctoral dissertations, organized into dual channels (DIS + AREF) and served through a loadable "skill" interface for Hermes / Claude Code / Codex-style agents.

> This project focuses on **portable expression patterns** (templates with slots), not on copying original text.

---

### Overview

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

### Classification System

**DIS channel** — INTRO · SURVEY · FORMAL_DEFS · MODEL · METHOD · ENGINEERING · EXPERIMENT · RESULT · DISCUSSION · TRANSITION · CONCLUSION

**AREF channel** — актуальность · новизна · цель/задачи · объект/предмет · методы · положения · достоверность · теоретическая/практическая значимость · апробация · внедрение · структура · выводы

**UTILS channel** — CONNECTIVE · CONSERVATIVE · NUMERIC

---

### Quality Scoring

- **2 (excellent)**: field-independent, ready to use
- **1 (good)**: needs domain adaptation
- **0 (informative)**: domain-tied, manual review

---

### Data Format (JSONL v2.1)

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

Master: `MASTER_SENTENCEBANK_DIS.jsonl` · `MASTER_SENTENCEBANK_AREF.jsonl` · `MASTER_UTILS.jsonl`

Quality: `QUALITY2_SELECTION_DIS.jsonl` · `QUALITY2_SELECTION_AREF.jsonl` · `QUALITY2_UTILS.jsonl`

---

### Installation

**Hermes:** `hermes skill install github:Tanue-Hou/phd-thesis-butler` → load with `/skill phd-thesis-butler`

**Claude Code:** clone to `~/.claude/skills/`, reference in CLAUDE.md

**Codex CLI:** `git clone https://github.com/Tanue-Hou/phd-thesis-butler.git`

---

### Sub-Skills

`dis_intro` · `dis_survey` · `dis_model` · `dis_method` · `dis_experiment` · `dis_result` · `dis_discussion` · `dis_conclusion` · `dis_transition` · `dis_formal_defs` · `dis_engineering` · `aref_core` · `utils_core`

---

### Disclaimer

This repository provides sentence templates and writing patterns for polishing and drafting assistance. Users are responsible for factual verification, citations, plagiarism checks, and academic integrity.

---

### License

**CC BY 4.0** — Free to use, adapt, and redistribute with attribution.

</details>

<br>

<details>
<summary><strong>🇨🇳 中文</strong></summary>

<br>

一个面向**俄语学术写作**的 skill-pack：从大量 кандидат/доктор 学位论文中抽取可迁移的**句式模板库**，按 DIS 与 AREF 双通道分类组织，可作为 Hermes / Claude Code / Codex 等代理的可加载技能库。

> 项目只提供可迁移表达模式（模板），不复制原文。

---

### 概览

- 来源论文：**327**
- 模板总量：**9,602**（DIS 5,621 + AREF 3,573 + UTILS 408）
- Quality=2（高可迁移精选）：**~2,000+**
- 覆盖分类/模块：**23**

每条模板包含：俄语句式（含槽位 `[...]`）、使用场景、常见误用、质量评分。

---

### 分类体系

**DIS 通道** — INTRO · SURVEY · FORMAL_DEFS · MODEL · METHOD · ENGINEERING · EXPERIMENT · RESULT · DISCUSSION · TRANSITION · CONCLUSION

**AREF 通道** — актуальность · новизна · цель/задачи · объект/предмет · методы · положения · достоверность · 理论/实践意义 · апробация · внедрение · структура · выводы

**UTILS 通道** — CONNECTIVE · CONSERVATIVE · NUMERIC

---

### 质量分级

- **2（优秀）**：跨学科通用，可直接填槽
- **1（可用）**：需要领域适配
- **0（信息性）**：领域绑定，需人工挑选

---

### 数据格式

```json
{
  "id": "DIS_INTRO_0427",
  "text": "В последние годы [Область] привлекает всё большее внимание исследователей в связи с [Фактор/Причина].",
  "source": "DIS",
  "category": "INTRO",
  "quality_score": 2,
  "when_to_use": "用于引言开头：用'关注度上升'来引出 актуальность",
  "common_mistakes": "不要反复使用；一篇引言建议 1–2 次即可"
}
```

主库：`MASTER_SENTENCEBANK_DIS.jsonl` · `MASTER_SENTENCEBANK_AREF.jsonl` · `MASTER_UTILS.jsonl`

精选：`QUALITY2_SELECTION_DIS.jsonl` · `QUALITY2_SELECTION_AREF.jsonl` · `QUALITY2_UTILS.jsonl`

---

### 安装

**Hermes：** `hermes skill install github:Tanue-Hou/phd-thesis-butler` → 加载 `/skill phd-thesis-butler`

**Claude Code：** 克隆到 `~/.claude/skills/`，在 CLAUDE.md 中引用

**Codex CLI：** `git clone https://github.com/Tanue-Hou/phd-thesis-butler.git`

---

### 子技能

`dis_intro` · `dis_survey` · `dis_model` · `dis_method` · `dis_experiment` · `dis_result` · `dis_discussion` · `dis_conclusion` · `dis_transition` · `dis_formal_defs` · `dis_engineering` · `aref_core` · `utils_core`

---

### 免责声明

本仓库提供的句式模板仅用于润色与写作参考。使用者的学术诚信、引用合规、原创性保障等责任自行承担。

---

### 许可证

**CC BY 4.0** — 可自由使用、改编、再分发，需保留署名。

</details>
