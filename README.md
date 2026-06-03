# PhD Thesis Butler v5.1 — Dissertation Writing Intelligence Platform

[中](#zh) · [Рус](#ru) · [EN](#en)

---

## ⚠️ 重要免责声明 / IMPORTANT DISCLAIMER / ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ

**使用本工具即表示您同意以下条款：**

1. **禁止自动生成本科/硕士/博士学位论文全文**。本工具仅作为学术写作辅助，提供句子模板、结构参考和修辞建议。**任何使用本工具生成的句子、段落或结构必须经过作者本人的实质性修改、批判性审核和学术性整合**。

2. **学术诚信第一**。本工具提供的所有模板和案例来源于已公开的俄罗斯学位论文数据库。使用者不得将模板内容直接复制到自己的论文中而不进行实质性改写和引用标注。任何抄袭行为由使用者自行承担全部责任。

3. **不构成完整的论文写作方案**。本工具输出的内容只是写作辅助参考，不构成、不替代、也不应被视为完整的论文写作解决方案。最终的论文内容、学术质量、逻辑完整性、数据准确性和法律合规性由使用者全权负责。

4. **学科局限性**。本技能的训练语料以俄罗斯技术科学（технические науки）和人文社会科学为主。在医学、农业、艺术等领域的覆盖不完整，使用者需自行评估适用性。

5. **无保证**。本技能按"原样"提供，不提供任何明示或暗示的保证，包括但不限于适销性、特定用途适用性和不侵权保证。

**By using this tool, you agree to:**
1. NOT auto-generate full dissertations/theses. This is an **assistive writing aid**, not a paper generator.
2. All output must be **substantially modified, critically reviewed, and academically integrated** by the author.
3. Plagiarism is strictly prohibited. Users bear full responsibility for academic misconduct.
4. The tool does NOT constitute a complete dissertation-writing solution.
5. Provided "as is" without warranty of any kind.

**Используя данный инструмент, Вы соглашаетесь:**
1. НЕ использовать для автоматической генерации полного текста диссертации. Это **вспомогательный инструмент** для академического письма.
2. Все выходные данные должны быть **существенно изменены, критически проверены** автором.
3. Плагиат строго запрещен. Пользователь несет полную ответственность за нарушение академической этики.
4. Инструмент НЕ является полным решением для написания диссертации.
5. Предоставляется «как есть» без каких-либо гарантий.

---

## v5.1 更新说明 / What's New in v5.1 / Что нового в v5.1

**核心策略：不重训练，只做结构增强、资产标准化和验证闭环。**

- **架构标准化**：7类标准资产格式（typical_structures / chapter_sequence / research_question_types / methodology_routes / logic_chains / validation_patterns / chapter_writing_rules），统一JSON Schema校验

- **学科资产重排**：5个discipline JSON全部转换为v5.1标准格式，统计聚合数据保留，噪声结构（chapter_count>30）降权排除

- **写作规则增强**：每条规则增加 when_to_use、recommended_actions、common_failures、template_family_links，方法论路线增加 description 和 typical_steps，逻辑链增加 chain_description 和 writing_sequence

- **模板标注**：40,997个句式模板全部标注 v5_cluster（AUTOMATION_CONTROL / SCI_TECH / AGRI_MED / ARTS_SPORTS / HUM_POL_ECON / GLOBAL），91.3%标记为纯俄语

- **润色规则**：从679篇深度分析数据中提炼学科专用润色规则（DO / DON'T / 常见错误），存入 polishing_rules_v5.json

- **验证闭环**：smoke_test 7项测试全通过（含版本一致性、schema校验、目录完整性）；validate_skill_assets / validate_planning_assets 双验证器通过；无本地绝对路径硬编码

- **数据清理**：CJK字符污染清理完毕（40,997条metadata字段清洗），非俄语模板标记为 mixed

- **文档修复**：README口径与公开仓库一致，不再宣称不存在的目录；版本统一为 5.1.0


---

<a id="zh"></a>

## 中文

### 1. 项目简介

**PhD Thesis Butler v5.1** 是一个面向俄罗斯副博士（кандидат наук）学位论文写作的智能辅助平台。它的核心使命是：**让AI助手在不需要重读千篇论文的前提下，获得编写俄罗斯学位论文的专业能力**。

**核心理念：** 源语料 → 蒸馏写作知识 → 验证模板/结构/评估标准 → 运行时检索与规划 → 可选私有扩展

#### v5.0 核心数据

| 指标 | 数值 |
|------|------|
| 分类论文 | 2,118 篇（来自3所俄罗斯高校，覆盖34个学科） |
| 深度分析 | 679 篇（mimo-v2.5-pro 全章节分析） |
| 写作模板 | 16,722 个纯俄语句式模板 |
| 学科聚类 | 5 大类（自动控制/理工/农林医/文体艺术/人文社科） |
| 质量分布 | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 |
| 管线覆盖 | Layer 0-6 全管线自动化（入库→全文→结构→分类→深读→蒸馏→发布） |

### 2. 技能架构

```
PhD Thesis Butler v5.1
│
├── 📦 核心组件
│   ├── SKILL.md          — 智能体运行时指令（agent-facing）
│   ├── BUILD_INFO.json   — 版本和构建元数据
│   ├── planning_layer/   — 论文规划指南（6个学科聚类）
│   └── scripts/          — 检索、验证、用户扩展脚本
│
├── 📝 句式模板库 (assets/ — 独立资产，管线重新训练不影响)
│   ├── global/            — 跨学科通用模板 (~7,030个)
│   ├── cluster/           — 按旧聚类归类 (~23,922个)
│   │   ├── HUM_SOC/       — 人文社科类 (~9,003个)
│   │   └── TECH_LIFE/     — 理工技术类 (~14,358个)
│   └── discipline/        — 34个学科专用文件
│
├── 📚 语料库蒸馏资产 (assets/references/ — 管线输出，可重建)
│   ├── disciplines/      — 5大学科写作范式
│   │   ├── AUTOMATION_CONTROL.json  — 自动控制/车辆工程 (148篇)
│   │   ├── SCI_TECH.json           — 理工科 (771篇)
│   │   ├── AGRI_MED.json           — 农林医 (268篇)
│   │   ├── ARTS_SPORTS.json        — 文体艺术 (96篇)
│   │   └── HUM_POL_ECON.json       — 人文社科 (792篇)
│   ├── corpus_summary_v5.json      — 语料库摘要
│   └── cross_cluster_insights_v5.json — 跨聚类对比分析
│
├── 🔬 数据管线 (scripts/pipeline/ — 构建使用，公开仓库不含)
│   ├── layer0_ingest.py    — PDF入库
│   ├── layer1_fulltext.py  — 全文抽取
│   ├── layer2_structure.py — 章节结构解析
│   ├── layer3_lite.py      — 轻量语义分类 (mimo-v2.5 / deepseek)
│   ├── layer4_deep.py      — 深度语义分析 (mimo-v2.5-pro)
│   ├── layer5_distill.py   — 范式蒸馏（统计聚合）
│   └── layer6_publish.py   — 公开资产构建
│
├── 🧪 验证体系 (构建使用，公开仓库不含)
│   ├── validate_skill_assets.py   — 资产完整性检查
│   └── validate_planning_assets.py— 规划层验证
│
├── 🔌 扩展层（v5.0预留）
│   ├── extension_layer/    — 用户私有论文扩展包
│   └── reading_layer/      — 个人文献阅读缓存
│
└── 📖 文档
    ├── README.md           — 三语文档（本文件）
    ├── corpus_layer/WORKFLOW.md   — 语料蒸馏说明
    └── CHANGELOG.md        — 版本历史
```

### 3. 数据管线（Layer 0–6）

每一层都设计为独立运行、断点续跑、可验证：

```
Layer 0 [入库]      → 2,267 篇 PDF 元数据入库
Layer 1 [全文]      → 2,267 篇全文抽取（含OCR备选）
Layer 2 [结构]      → 2,266 篇章节结构解析（TOC优先，回退正文检测）
Layer 3 [分类]      → 2,118 篇轻量语义分类（5个聚类，93.5%覆盖率）
Layer 4 [深度分析]  → 679 篇深度结构/方法/实验/逻辑分析（mimo-v2.5-pro）
Layer 5 [蒸馏]      → 5大学科写作范式 + 跨聚类洞见（统计聚合）
Layer 6 [发布]      → 公开资产构建、版本标记、文档同步
```

**数据脱敏声明：** 所有公开资产中的原始论文标识（作者名、高校名、具体学科名）均已被抽象化处理。公共仓库不包含任何原始PDF全文或可追溯到具体作者的元数据。学科聚类仅保留大类标签（如"AUTOMATION_CONTROL"），不暴露具体研究机构名称。

### 4. 迭代历史

| 版本 | 主题 | 关键进展 |
|:----:|:----:|:---------|
| v1.0 | 初始版本 | 手动整理的 ~500 个俄语学术句式 |
| v2.0 | 模板扩展 | 从1,042篇论文中提取16,722个模板，按DIS/AREF双通道分拣 |
| v3.0 | 质量体系 | 引入Q0/Q1/Q2三级质量评分、学科聚类、三层检索 |
| v3.3.5 | 稳定基线 | 34个学科全覆盖，validate/planning层就绪 |
| v4.0 | 语料蒸馏 | 50篇测试管线验证通过，corpus_layer设计完成 |
| **v5.0** | **全量管线** | **2,118篇全量分类+679篇深度分析，5大学科范式蒸馏，自动化Pipeline** |

### 5. 使用场景

| 场景 | 说明 | 示例 |
|:----:|:----|:-----|
| 🎓 论文规划 | 加载技能后，AI帮你规划章节结构和逻辑流 | "帮我规划一篇车辆工程博士论文的章节" |
| ✍️ 段落写作 | 根据当前学科和章节获取俄语句式模板 | "帮我写论文的MODEL部分" |
| 🔍 方法选择 | 获取所属学科的典型方法论路线 | "控制类论文用什么实验方法比较常见？" |
| ✅ 逻辑检查 | 评估论文的逻辑闭环完整性 | "检查我的论文逻辑链是否完整" |
| 📚 文献扩展 | 通过私有扩展包集成自己的论文语料 | "把我之前发表的3篇论文加入知识库" |
| ⚠️ 常见错误 | 获取本学科常见写作问题和修复策略 | "工程学科论文有哪些常见错误？" |
| 🏗️ 工程深化 | 面向车辆控制/状态估计等领域的专门写作指南 | "我需要写状态估计方法的实验部分" |

### 6. 真实使用案例

**案例：自动化控制方向的论文引言写作**

用户需求：我是车辆工程专业博士生，需要写俄语论文的引言（Введение）部分，展示研究问题的重要性。

**AI助手响应流程：**

1. **场景检测** → 检测到用户在写车辆控制类论文，自动定位到 AUTOMATION_CONTROL 聚类
2. **结构提取** → 从该聚类资产中提取典型引言结构：
   - 研究背景（актуальность）
   - 现有方法局限性（обзор литературы）
   - 研究空白（пробел）
   - 研究目标（цель）
   - 论文结构预览（структура работы）
3. **模板检索** → 返回该学科最常用的引言句式：
   ```
   [высокая актуальность]
   "В последние годы проблема [тема] привлекает всё большее внимание исследователей в связи с [причина]."
   
   [обоснование пробела]
   "Однако существующие методы [метод] не позволяют в полной мере учесть [ограничение], что приводит к [недостаток]."
   
   [формулировка цели]
   "Целью настоящей работы является разработка и верификация [предлагаемый метод] для [применение]."
   ```
4. **常见错误提醒** → 提示避免：目标设定过宽、背景与目标脱节、研究空白论证不充分
5. **逻辑链检查** → 确保问题→空白→目标→方法→实验→结果→结论的闭环完整

### 7. 快速开始

```bash
# 加载技能（Hermes Agent 环境）
hermes skill load phd-thesis-butler

# 或手动加载 SKILL.md
hermes skill install /path/to/phd-thesis-butler/SKILL.md

# 检索模板
python3 scripts/retrieve_templates.py \
  --category INTRO \
  --cluster AUTOMATION_CONTROL \
  --query "цель исследования" \
  --limit 5

# 运行验证
python3 scripts/validate_skill_assets.py
python3 -m pytest tests/ -q
```

---

<a id="ru"></a>

## Русский

### 1. Обзор

**PhD Thesis Butler v5.1** — это интеллектуальная платформа-помощник для написания кандидатских диссертаций на русском языке. Основная миссия: дать AI-ассистенту возможность профессионально помогать с диссертацией без необходимости перечитывать тысячи исходных работ.

**Основной принцип:** Исходный корпус → дистиллированное знание о письме → проверенные шаблоны/структуры/критерии → поиск и планирование во время работы → опциональные частные расширения.

#### Ключевые показатели v5.0

| Показатель | Значение |
|------------|----------|
| Классифицировано работ | 2 118 (из 3 российских вузов, 34 дисциплины) |
| Глубокий анализ | 679 работ (mimo-v2.5-pro, полный анализ глав) |
| Шаблонов | 16 722 чистых русскоязычных шаблона |
| Кластеров | 5 (AUTOMATION_CONTROL / SCI_TECH / AGRI_MED / ARTS_SPORTS / HUM_POL_ECON) |
| Распределение качества | Q2: 4 236 / Q1: 10 486 / Q0: 2 000 |
| Pipeline | Layer 0–6: полная автоматизация |

### 2. Архитектура навыка

Структура проекта аналогична китайской секции выше. Основные компоненты:

- `SKILL.md` — инструкции для AI-агента
- `assets/references/disciplines/` — профили по 5 кластерам
- `scripts/pipeline/` — полный конвейер обработки (Layer 0–6, не входит в публичный репозиторий)
- `tests/` — 23 теста pytest (не входит в публичный репозиторий)

### 3. Конвейер данных (Layer 0–6)

| Слой | Действие | Результат |
|:----:|:---------|:----------|
| Layer 0 | Загрузка PDF | 2 267 записей |
| Layer 1 | Извлечение текста | 2 267 полных текстов |
| Layer 2 | Парсинг структуры | 2 266 структур глав |
| Layer 3 | Легкая классификация | 2 118 работ, 5 кластеров (93.5%) |
| Layer 4 | Глубокий анализ | 679 работ (структура, методология, эксперименты) |
| Layer 5 | Дистилляция | 5 профилей кластеров + межкластерный анализ |
| Layer 6 | Публикация | Сборка открытых активов, тегирование |

**Анонимизация данных:** Все идентификаторы исходных работ (имена авторов, названия вузов, конкретные дисциплины) удалены из публичных активов. Публичный репозиторий не содержит ни одного полного PDF-текста или метаданных, позволяющих идентифицировать конкретного автора.

### 4. История версий

| Версия | Тема | Ключевые изменения |
|:------:|:----:|:-------------------|
| v1.0 | Начальная | ~500 вручную собранных фраз |
| v2.0 | Расширение | 16 722 шаблона из 1 042 работ |
| v3.0 | Качество | Q0/Q1/Q2, кластеризация, трехуровневый поиск |
| v3.3.5 | Базовый уровень | 34 дисциплины, валидация |
| v4.0 | Дистилляция | Пилотный pipeline 50 работ |
| **v5.0** | **Полный конвейер** | **2 118 классификаций + 679 глубоких анализов** |

### 5. Сценарии использования

- Планирование структуры диссертации по дисциплине
- Получение русскоязычных шаблонов для нужного раздела
- Выбор методологии на основе анализа корпуса
- Проверка логической целостности работы
- Расширение корпуса своими публикациями
- Выявление типичных ошибок по дисциплине

### 6. Пример использования

**Сценарий:** Аспирант пишет введение к диссертации по управлению транспортными средствами.

AI-ассистент автоматически определяет кластер AUTOMATION_CONTROL, извлекает типичную структуру введения (актуальность → обзор → пробел → цель → задачи), предлагает наиболее частотные шаблоны для каждого элемента и предупреждает о типичных ошибках (слишком широкая цель, отрыв актуальности от конкретной задачи).

### 7. Быстрый старт

```bash
hermes skill load phd-thesis-butler
python3 scripts/retrieve_templates.py --category INTRO --cluster AUTOMATION_CONTROL --query "цель" --limit 5
python3 -m pytest tests/ -q
```

---

<a id="en"></a>

## English

### 1. Overview

**PhD Thesis Butler v5.1** is a dissertation writing intelligence platform for Russian PhD (кандидат наук) theses. Its core mission: **give an AI assistant professional dissertation-writing capability without re-reading thousands of source papers**.

**Core principle:** Source corpus → distilled writing knowledge → validated templates/structures/rubrics → runtime retrieval & planning → optional private extension packs.

#### v5.0 Key Metrics

| Metric | Value |
|:-------|:------|
| Papers classified | 2,118 (3 Russian universities, 34 disciplines) |
| Deep-analyzed | 679 (mimo-v2.5-pro full chapter analysis) |
| Writing templates | 16,722 pure Russian sentence patterns |
| Discipline clusters | 5 (AUTOMATION_CONTROL / SCI_TECH / AGRI_MED / ARTS_SPORTS / HUM_POL_ECON) |
| Quality | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 |
| Pipeline | Layer 0–6 fully automated (ingest → publish) |

### 2. Skill Architecture

Same structure as the Chinese section. Key components:

- `SKILL.md` — agent-facing runtime instructions
- `assets/references/disciplines/` — 5 discipline writing profiles
- `scripts/pipeline/` — full processing pipeline (Layer 0–6, not in public repo)
- `tests/` — 23 pytest test suite (not in public repo)

### 3. Data Pipeline (Layer 0–6)

| Layer | Action | Result |
|:-----:|:-------|:-------|
| Layer 0 | PDF ingest | 2,267 paper records |
| Layer 1 | Full text extraction | 2,267 full texts |
| Layer 2 | Structure parsing | 2,266 chapter structures |
| Layer 3 | Lightweight classification | 2,118 papers, 5 clusters (93.5%) |
| Layer 4 | Deep analysis | 679 papers (structure/methodology/experiment/logic) |
| Layer 5 | Paradigm distillation | 5 cluster profiles + cross-cluster insights |
| Layer 6 | Release assembly | Public asset build, tagging, doc sync |

**Data Anonymization:** All public assets have author names, university names, and specific discipline identifiers removed. The public repository contains NO raw PDF text or author-traceable metadata. Discipline clusters use only broad category labels.

### 4. Version History

| Version | Theme | Key Changes |
|:-------:|:-----:|:-----------|
| v1.0 | Initial | ~500 manually curated Russian phrases |
| v2.0 | Template expansion | 16,722 templates from 1,042 papers |
| v3.0 | Quality system | Q0/Q1/Q2 scoring, clustering, 3-level retrieval |
| v3.3.5 | Stable baseline | 34 disciplines, validate/planning layers |
| v4.0 | Corpus distillation | 50-paper pilot pipeline |
| **v5.0** | **Full pipeline** | **2,118 classified + 679 deep-analyzed** |

### 5. Use Cases

- Plan dissertation chapter structure by discipline
- Retrieve Russian sentence templates for any section
- Identify typical methodology routes for your field
- Check logic chain completeness
- Extend corpus with your own publications (via extension packs)
- Get discipline-specific writing mistake warnings

### 6. Real Usage Example

**Scenario:** A vehicle engineering PhD student needs to write the Introduction (Введение) section of their Russian dissertation.

The AI assistant automatically detects the AUTOMATION_CONTROL cluster, extracts the typical introduction structure (background → literature gap → research gap → goal → tasks), retrieves the most frequent Russian sentence patterns for each element, and warns about common mistakes (overly broad goal, disconnected motivation).

### 7. Quick Start

```bash
hermes skill load phd-thesis-butler
python3 scripts/retrieve_templates.py --category INTRO --cluster AUTOMATION_CONTROL --query "goal" --limit 5
python3 -m pytest tests/ -q
```

---

## License

This project is provided for **academic research and writing assistance purposes only**. See Disclaimer at the top of this file for usage restrictions.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## Repository Structure

```
phd-thesis-butler/
├── SKILL.md                    # Agent runtime instructions (v5.0)
├── BUILD_INFO.json             # Build metadata & pipeline stats
├── README.md                   # This file (ZH/RU/EN)
├── CHANGELOG.md                # Version history
├── assets/
│   └── references/
│       ├── disciplines/        # 5 cluster writing profiles
│       ├── corpus_summary_v5.json
│       └── cross_cluster_insights_v5.json
├── planning_layer/             # Dissertation planning guides
├── scripts/
│   ├── pipeline/               # Layer 0–6 pipeline scripts
│   ├── retrieve_templates.py   # Template retrieval CLI
│   └── validate_*.py           # Validation scripts
├── corpus_layer/               # Corpus distillation design (not in public repo)
│   └── schemas/                # JSON schemas (not in public repo)
├── extension_layer/            # User extension pack design
├── reading_layer/              # Document reading cache
├── tests/                      # 23 pytest tests (not in public repo)
├── data/                       # Source PDFs (private, gitignored)
```
