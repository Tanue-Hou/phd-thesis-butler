# PhD Thesis Butler v5.1.3

Russian dissertation writing skill for AI assistants.

[中文](#中文) · [Русский](#русский) · [English](#english)

---

## 中文

### 这是什么

PhD Thesis Butler 是一个面向俄罗斯 кандидат наук / 博士论文写作的 Codex/Hermes skill。它不是论文自动生成器，而是让智能体在写作辅助时能够调用：

- 俄语学术句式模板；
- 论文结构规划规则；
- 学科方法论路线；
- 问题-目标-方法-实验-结论的逻辑闭环规则；
- 学科常见错误和润色规则。

v5.1.3 的核心目标是：**不要求用户重新读取原始论文，也不要求重新训练模型，就能让智能体获得可检索、可验证、可路由的俄罗斯论文写作范式资产。**

### 数据与资产

公开 skill 包含的是蒸馏后的写作资产，不包含原始 PDF、全文、作者可追溯信息或私有构建缓存。

| 项目 | 数量 / 状态 |
|---|---:|
| 句式模板 | 16,722 |
| 分类论文来源 | 2,118 篇公开俄罗斯学位论文 |
| 深度分析样本 | 679 篇 |
| 学科大类资产 | 5 个 |
| 规划层聚类 | 6 个 |
| 模板质量分布 | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 |

五大学科大类资产位于 `assets/references/disciplines/`：

- `AUTOMATION_CONTROL`：自动化、控制、车辆控制方向，深度增强；
- `SCI_TECH`：理工类；
- `AGRI_MED`：农医类；
- `ARTS_SPORTS`：艺术体育类；
- `HUM_POL_ECON`：人文、政治、经济类。

规划层位于 `planning_layer/`，用于论文结构、章节任务、实验方案和逻辑链设计。

### 能做什么

适合的任务：

- 规划俄语博士论文整体结构；
- 设计章节顺序和每章写作功能；
- 为方法、模型、实验、结果、结论等章节检索俄语句式；
- 检查论文是否形成问题-目标-方法-验证-结论闭环；
- 根据学科大类调用对应写作范式；
- 给出常见错误和修复建议；
- 支持用户未来用自己的论文做私有扩展包。

不适合的任务：

- 一键生成整篇论文；
- 绕过作者本人的学术判断；
- 把模板原样复制进论文；
- 替代导师、同行评审或学术规范审查。

### 运行逻辑

当用户提出“规划、结构、方法论、实验设计、逻辑闭环”等需求时，智能体优先使用 `planning_layer/` 和 `assets/references/disciplines/`。

当用户提出“给我俄语句式、写某段、润色某节”等需求时，智能体使用 `scripts/retrieve_templates.py` 检索模板。普通检索默认只返回俄语安全条目；标记为 `v5_lang=mixed` 的条目保留用于审计，但不会默认展示给用户。

### 快速使用

```bash
# 检索自动化/控制方向的引言句式
python3 scripts/retrieve_templates.py \
  --category INTRO \
  --cluster AUTOMATION_CONTROL \
  --query "цель исследования актуальность" \
  --limit 5
```

常见请求示例：

```text
帮我规划一篇车辆控制方向俄语博士论文的章节结构。
控制类论文的实验验证部分一般怎么写？
给我 METHOD 部分的俄语表达模板。
检查我的问题-目标-方法-实验-结论链条是否闭环。
```

### 验证

公开仓库可直接运行以下检查：

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
bash scripts/smoke_test.sh
```

这些检查覆盖：

- 版本一致性；
- 资产目录完整性；
- discipline JSON schema；
- planning layer 结构；
- CJK 字符和中文标点污染；
- 检索脚本基本可用性；
- 本地绝对路径泄漏。

### 公开包与私有管线边界

公开 skill 包只保留用户运行所需的资产和脚本。以下内容属于本地/私有构建管线，不要求用户安装，也不应在公开包中假定存在：

- 原始论文 PDF；
- `.phd_build/`；
- Layer 0-6 全量处理脚本；
- 私有 LLM 调用记录；
- 作者、学校、具体论文级追溯信息；
- 私有测试或抽样审计目录。

如果要继续训练或蒸馏新的论文，应在本地私有管线中完成，再把脱敏后的聚合资产发布到 `assets/references/`。

### 仓库结构

```text
phd-thesis-butler/
├── SKILL.md
├── BUILD_INFO.json
├── README.md
├── CHANGELOG.md
├── assets/
│   ├── cluster/
│   ├── global/
│   └── references/
│       ├── disciplines/
│       ├── schemas/
│       ├── corpus_summary_v5.json
│       ├── cross_cluster_insights_v5.json
│       └── polishing_rules_v5.json
├── planning_layer/
├── scripts/
│   ├── retrieve_templates.py
│   ├── validate_skill_assets.py
│   ├── validate_planning_assets.py
│   └── smoke_test.sh
└── extension_layer/
```

### 学术诚信

本 skill 只能作为写作辅助工具。任何输出都必须由作者本人进行实质性修改、事实核验、逻辑整合和学术责任承担。禁止将本工具用于自动生成完整学位论文或规避学术审查。

---

## Русский

### Что это такое

PhD Thesis Butler — это skill для Codex/Hermes, предназначенный для помощи в написании российских диссертаций уровня кандидат наук / PhD. Это не генератор готовых диссертаций. Skill предоставляет AI-ассистенту проверяемые активы для:

- поиска русскоязычных академических шаблонов;
- планирования структуры диссертации;
- выбора типичных методологических маршрутов;
- проверки логической цепочки проблема-цель-метод-эксперимент-вывод;
- выявления типичных ошибок по дисциплинам;
- дисциплинарного редактирования и полировки текста.

Цель v5.1.3: **дать ассистенту доступ к дистиллированным знаниям о письме без повторного чтения исходных PDF и без дообучения модели.**

### Данные и активы

Публичный skill содержит только дистиллированные активы. Он не содержит исходные PDF, полные тексты, имена авторов, трассируемые метаданные или приватные build-кэши.

| Компонент | Значение |
|---|---:|
| Шаблонов | 16 722 |
| Источник классификации | 2 118 публичных российских диссертаций |
| Глубоко проанализировано | 679 работ |
| Дисциплинарных профилей | 5 |
| Планировочных кластеров | 6 |
| Качество шаблонов | Q2: 4 236 / Q1: 10 486 / Q0: 2 000 |

Пять дисциплинарных профилей находятся в `assets/references/disciplines/`:

- `AUTOMATION_CONTROL`: автоматизация, управление, транспортные системы; усиленный профиль;
- `SCI_TECH`: инженерные и естественно-научные направления;
- `AGRI_MED`: аграрные и медицинские направления;
- `ARTS_SPORTS`: искусство, культура, спорт;
- `HUM_POL_ECON`: гуманитарные, политические и экономические направления.

Планировочные материалы находятся в `planning_layer/`.

### Что skill умеет

Подходит для задач:

- спланировать структуру диссертации;
- определить функции глав и последовательность разделов;
- подобрать русские шаблоны для введения, метода, модели, эксперимента, результатов и заключения;
- проверить логическую замкнутость диссертации;
- выбрать типичный методологический маршрут для дисциплины;
- показать частые ошибки и способы исправления;
- подготовить основу для приватного расширения на собственном корпусе пользователя.

Не подходит для:

- автоматического написания полной диссертации;
- замены автора, научного руководителя или рецензента;
- копирования шаблонов без переработки;
- обхода академической этики.

### Логика работы

Запросы о планировании, структуре, методологии, эксперименте и логической цепочке маршрутизируются к `planning_layer/` и `assets/references/disciplines/`.

Запросы о фразах, абзацах, формулировках и полировке используют `scripts/retrieve_templates.py`. В обычном режиме поиск показывает только русскоязычно безопасные записи. Записи с `v5_lang=mixed` сохраняются для аудита, но не выдаются пользователю по умолчанию.

### Быстрый старт

```bash
python3 scripts/retrieve_templates.py \
  --category INTRO \
  --cluster AUTOMATION_CONTROL \
  --query "цель исследования актуальность" \
  --limit 5
```

Примеры запросов:

```text
Помоги спланировать структуру диссертации по управлению транспортным средством.
Как обычно пишется экспериментальная часть в диссертациях по управлению?
Дай русские шаблоны для раздела METHOD.
Проверь, замкнута ли логика проблема-цель-метод-эксперимент-вывод.
```

### Проверка

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
bash scripts/smoke_test.sh
```

Проверки охватывают версии, структуру активов, discipline schema, planning layer, CJK-загрязнение, работу retrieval-скрипта и утечки локальных абсолютных путей.

### Граница публичного пакета

Публичный пакет не включает:

- исходные PDF;
- `.phd_build/`;
- приватные Layer 0-6 pipeline-скрипты;
- журналы LLM-вызовов;
- авторские или университетские идентификаторы;
- приватные тесты и аудиторские выборки.

Новые корпуса следует обрабатывать локально, затем публиковать только обезличенные агрегированные активы.

### Академическая этика

Skill является инструментом помощи. Все результаты должны быть существенно переработаны, проверены и интегрированы автором. Использование для автоматической генерации полной диссертации запрещено.

---

## English

### What This Is

PhD Thesis Butler is a Codex/Hermes skill for assisting with Russian кандидат наук / PhD dissertation writing. It is not a dissertation generator. It gives an AI assistant structured, auditable assets for:

- retrieving Russian academic sentence patterns;
- planning dissertation structure;
- selecting discipline-specific methodology routes;
- checking problem-goal-method-experiment-conclusion logic closure;
- identifying common dissertation writing failures;
- applying discipline-aware polishing guidance.

The goal of v5.1.3 is: **provide distilled dissertation-writing knowledge without requiring users to reread source PDFs or retrain a model.**

### Data and Assets

The public skill contains distilled writing assets only. It does not include raw PDFs, full source texts, author-traceable metadata, or private build caches.

| Component | Value |
|---|---:|
| Sentence templates | 16,722 |
| Classified source papers | 2,118 public Russian dissertations |
| Deep-analyzed papers | 679 |
| Discipline profiles | 5 |
| Planning clusters | 6 |
| Template quality | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 |

The five discipline profiles live in `assets/references/disciplines/`:

- `AUTOMATION_CONTROL`: automation, control, vehicle control; enhanced profile;
- `SCI_TECH`: science and engineering;
- `AGRI_MED`: agriculture and medicine;
- `ARTS_SPORTS`: arts, culture, and sports;
- `HUM_POL_ECON`: humanities, politics, and economics.

Planning assets live in `planning_layer/`.

### What It Can Do

Good use cases:

- plan a Russian dissertation structure;
- define chapter sequence and chapter functions;
- retrieve Russian templates for introduction, method, model, experiment, results, and conclusion sections;
- check whether the dissertation logic closes from problem to conclusion;
- choose discipline-appropriate methodology routes;
- surface common failures and repair actions;
- support private user-extension packs built from the user's own papers.

Out of scope:

- one-click full dissertation generation;
- replacing author judgment, supervision, or review;
- copying templates unchanged into a thesis;
- bypassing academic integrity requirements.

### Runtime Logic

Planning, structure, methodology, experiment design, and logic-chain requests route to `planning_layer/` and `assets/references/disciplines/`.

Sentence, paragraph, and polishing requests use `scripts/retrieve_templates.py`. Normal retrieval returns Russian-safe entries only. Entries tagged `v5_lang=mixed` are retained for audit/debug use but hidden from normal user-facing retrieval.

### Quick Start

```bash
python3 scripts/retrieve_templates.py \
  --category INTRO \
  --cluster AUTOMATION_CONTROL \
  --query "цель исследования актуальность" \
  --limit 5
```

Example prompts:

```text
Plan a Russian dissertation structure for a vehicle control topic.
How should the experiment chapter be written in control dissertations?
Give me Russian templates for the METHOD section.
Check whether my problem-goal-method-experiment-conclusion chain is closed.
```

### Validation

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
bash scripts/smoke_test.sh
```

These checks cover release metadata, asset structure, discipline schema, planning layer integrity, CJK contamination, retrieval smoke tests, and local absolute-path leakage.

### Public Package Boundary

The public package does not include:

- raw PDFs;
- `.phd_build/`;
- private Layer 0-6 pipeline scripts;
- LLM call logs;
- author or university identifiers;
- private tests or audit samples.

New corpora should be processed locally. Only anonymized aggregate assets should be published into `assets/references/`.

### Repository Structure

```text
phd-thesis-butler/
├── SKILL.md
├── BUILD_INFO.json
├── README.md
├── CHANGELOG.md
├── assets/
│   ├── cluster/
│   ├── global/
│   └── references/
│       ├── disciplines/
│       ├── schemas/
│       ├── corpus_summary_v5.json
│       ├── cross_cluster_insights_v5.json
│       └── polishing_rules_v5.json
├── planning_layer/
├── scripts/
│   ├── retrieve_templates.py
│   ├── validate_skill_assets.py
│   ├── validate_planning_assets.py
│   └── smoke_test.sh
└── extension_layer/
```

### Academic Integrity

This skill is an assistive tool. All outputs must be substantially revised, fact-checked, logically integrated, and academically owned by the author. It must not be used to auto-generate a complete dissertation or evade academic review.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
