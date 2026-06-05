# PhD Thesis Butler v5.4.1

Russian dissertation planning, evidence-aware revision, and academic polishing skill for AI assistants such as Codex, Hermes, Claude Code, and Antigravity.

[中文](#中文) · [Русский](#русский) · [English](#english)

---

## 中文

**PhD Thesis Butler 是一个开源俄语论文写作 Skill，可供 Codex、Hermes、Claude Code、Antigravity 等智能体调用，用于论文结构规划、文献证据检查和俄语学术润色。**

它面向正在写俄语 кандидат наук / PhD / 博士论文、俄语期刊论文、开题报告、章节草稿和文献综述的人。它的目标是帮助用户把研究想法变成结构清晰、证据更稳、表达更像俄罗斯学术写作的论文文本。

> 它不是代写工具。它不替代作者贡献、导师判断、事实核验或学术伦理责任。

### 最核心能做什么

核心能力概览：

| 工作流 | 什么时候用 | 涉及哪些层 |
|:-------|:-----------|:------------|
| **① 俄语润色与表达优化** | 已有俄语段落/全文，需要润色、改写、降机器感、查句式 | assets + retrieve_templates.py |
| **② 论文规划与结构设计** | 只有研究方向/想法，需要完整的论文结构、章节顺序、方法路线、实验方案 | planning_layer + discipline assets |
| **③ 文献调研与论文对比** | 需要查文献、找同方向俄罗斯论文、对比结构/方法/验证、用 Zotero 私有库 | research_layer + landscape/ + dissercat/elibrary |
| **④ 证据检查与引用修复** | 已有章节草稿，需要检查哪些论断缺引用、文献该放哪一章 | evidence_layer + binding/gap scripts |

### 典型使用场景

#### 1. 从想法到论文框架

```text
我想写车辆状态估计和横向控制方向的俄语博士论文，请帮我规划整体结构。
```

可以得到：

- 学科大类判断；
- 论文整体章节顺序；
- 每章应该完成的写作功能；
- 问题、目标、任务、方法、实验、结论之间的闭环；
- 哪些章节需要模型、实验、对比、消融或案例论证。

#### 2. 工作流 ③：文献调研与论文对比 🆕

```text
我研究车辆状态估计，帮我找同方向俄罗斯博士论文，看看别人怎么写结构。
——或者——
从我的 Zotero 里找 vehicle state estimation 相关论文，分析它们怎么支撑我的博士论文结构。
```

可以得到：

- 同方向论文的章节结构模式对比；
- 方法论路线类型分析（卡尔曼滤波、自适应估计、多传感器融合等）；
- 验证方式对比（仿真、实验台架、实车测试等）；
- 用户选题在同方向论文中的定位：重合点、差异点、可创新点；
- 建议的论文结构（可直接进入 planning_layer 进行细化）；
- 每章所需的证据绑定需求（进入 evidence_layer）。

#### 3. 从研究思路到方法论路线

```text
我的思路是用多传感器融合提高车辆控制稳定性，请拆成研究问题、目标、任务和实验路线。
```

可以得到：

- 研究问题类型；
- 方法论路线；
- 变量、模型、数据、指标和验证设计；
- 可能的 benchmark、对比方法和风险点。

#### 4. 从文献到章节证据

```text
请帮我判断这些文献应该分别支撑引言、综述、方法章还是实验章。
```

可以得到：

- 文献证据角色：background、research gap、method basis、benchmark、empirical support 等；
- 章节证据地图；
- 哪些章节证据足够，哪些只是 partial，哪些还需要补 eLIBRARY / DisserCat / CyberLeninka 文献。

#### 5. 检查引用缺口

```text
这是我的第二章，请检查哪些论断缺少引用支撑，并告诉我应该补什么类型的文献。
```

可以得到：

- 每个论断的 `covered / partial / missing / not_needed` 状态；
- 证据覆盖率、需引用论断比例；
- 高风险缺口；
- 可读 Markdown 报告；
- 下一步检索建议。

#### 6. 润色已经写好的俄语论文

```text
这是我写好的俄语引言。请保留我的原始思路，优化学术表达和段落逻辑，不要新增未经我提供的事实。
```

可以得到：

- 更自然的俄语学术表达；
- 更清楚的段落衔接；
- 减少机器化、直译化、口语化表达；
- 对目标、任务、结论不一致之处提出修改意见。

### 这不是做什么

请不要把本 skill 用于：

- 一键生成完整学位论文；
- 编造实验、数据、文献或引用；
- 绕过导师、学校、期刊或学术伦理审查；
- 直接复制模板作为最终论文文本；
- 代替作者完成研究贡献。

推荐用法是：**作者提供真实研究内容，智能体帮助规划、检查、组织、润色和提示风险。**

### 核心资产

公开仓库只包含脱敏和蒸馏后的知识资产，不包含原始 PDF、全文语料、作者可追溯信息、私有 LLM 调用记录或 `.phd_build/` 构建缓存。

| 资产层 | 数量 / 状态 | 作用 |
|---|---:|---|
| 俄语表达与润色模板 | 16,722 条 | 用于句式替换、段落润色、章节表达增强。这只是语言润色层，不代表系统全部能力。 |
| 公开俄罗斯学位论文蒸馏来源 | 2,118 篇 | 用于形成论文结构、方法论路线、逻辑链和学科写作范式。 |
| 深度分析样本 | 679 篇 | 用于提取章节功能、方法路线、验证模式和逻辑闭环规则。 |
| 学科大类资产 | 5 个 | 自动化控制、理工、农医、艺术体育、人文政经。 |
| 规划层聚类 | 6 个 | 用于把研究想法转成章节蓝图、方法路线、实验设计和汇报结构。 |
| 模板质量分级 | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 | 用于优先调用更可靠的俄语学术表达。 |

### 五大学科大类

| 学科资产 | 覆盖范围 |
|---|---|
| `AUTOMATION_CONTROL` | 自动化、控制、车辆控制、状态估计，重点增强。 |
| `SCI_TECH` | 理工类、工程类、自然科学类。 |
| `AGRI_MED` | 农业、医学、生物、健康相关方向。 |
| `ARTS_SPORTS` | 艺术、文化、体育相关方向。 |
| `HUM_POL_ECON` | 人文、政治、经济、管理、社会科学方向。 |

每个学科资产围绕七类知识组织：

```text
typical_structures
chapter_sequence
research_question_types
methodology_routes
logic_chains
validation_patterns
chapter_writing_rules
```

### 能力层级

```
User request — 4个工作流
  ├─ ① 俄语润色与表达优化
  │    └─ retrieve_templates.py + assets/cluster + assets/global
  ├─ ② 论文规划与结构设计
  │    └─ planning_layer/ + discipline assets（内部范式知识）
  ├─ ③ 文献调研与论文对比
  │    ├─ research_layer/（检索策略、元数据标准化）
  │    └─ landscape/（同方向论文对比分析——高级子工作流）
  └─ ④ 证据检查与引用修复
       └─ evidence_layer/ + bind/detect/render scripts
```

### 如何实际使用

普通用户不需要手动运行脚本。这个仓库的脚本和资产主要交给 **Codex / Hermes / Claude Code / Antigravity** 等智能体在后台调用。

你只需要对智能体说清楚任务，例如：

```text
请用 phd-thesis-butler 帮我规划一篇俄语博士论文结构。
请检查这章哪些论断缺少引用。
请根据这些参考文献判断它们应该放在引言、综述、方法章还是实验章。
请保留我的原意，润色这段俄语论文文本。
```

开发者如果需要调试具体脚本，可以查看 `scripts/`、`research_layer/` 和 `evidence_layer/` 中的示例文件。

### 仓库结构

```text
phd-thesis-butler/
├── SKILL.md
├── README.md
├── BUILD_INFO.json
├── CHANGELOG.md
├── assets/
│   ├── cluster/                 # 句式模板聚类资产
│   ├── global/                  # 全局模板资产
│   └── references/
│       ├── disciplines/         # 五大学科大类资产
│       └── schemas/             # 公开 schema
├── planning_layer/              # 论文规划、方法论、实验设计、逻辑闭环
├── research_layer/              # 文献调研来源、检索策略、示例
│   └── landscape/               # 同方向论文对比分析——文献调研的高级子工作流 (v5.4)
├── evidence_layer/              # 证据角色、章节绑定、引用缺口检测
├── extension_layer/             # 用户私有扩展入口
└── scripts/                     # 检索、调研、证据、验证脚本
```

### 验证

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
python3 scripts/validate_research_layer.py
python3 scripts/validate_evidence_layer.py
python3 scripts/validate_dissertation_landscape.py
bash scripts/smoke_test.sh
```

`v5.3.4` 当前验证重点：

- 版本一致性；
- 资产 JSON / JSONL 可解析；
- planning layer 完整性；
- research layer 元数据标准化；
- evidence layer schema 与安全不变量；
- `year: null` Zotero metadata 兼容；
- citation gap 报告中 `covered` 与 `not_needed` 分离；
- 普通模板检索隐藏 mixed/CJK 污染条目。

### 版本路线

| 版本 | 重点 |
|---|---|
| v3.3.5 | 稳定句式库、规划层和模板检索基线。 |
| v5.0 | 从句式库升级为论文范式资产。 |
| v5.1 | 五大学科资产、结构/方法论/逻辑链增强，不重新训练。 |
| v5.2 | Research Layer：俄语与国际文献调研路径、元数据标准化、综述 brief。 |
| v5.3 | Evidence-Aware Writing：章节证据绑定、引用缺口检测、可读报告。 |
| v5.4 | **文献调研与论文对比**：同方向俄罗斯博士论文搜索（DisserCat/eLIBRARY）、Zotero 私有文献库、结构化对比分析、自动推荐论文大纲。 |

完整记录见 [CHANGELOG.md](CHANGELOG.md)。

### 参与开发

欢迎提交：

- 新学科方向的写作规则；
- 更好的俄语学术表达模板；
- eLIBRARY / DisserCat / CyberLeninka 检索策略；
- Zotero、本地文献库、BibTeX 工作流集成；
- 证据匹配与引用缺口检测的测试用例；
- 不同学科的论文结构范式反馈。

优先贡献方向：

1. 跨语言语义证据匹配；
2. 更严格的学科过滤与模板路由；
3. `evals/` 自动评测集；
4. 用户私有扩展层；
5. 插件 / MCP 版本的实时检索能力。

### 学术诚信

PhD Thesis Butler 是科研写作辅助工具。它可以帮助规划、检索、检查、润色和提出修改意见，但所有事实、引用、实验、结论和学术责任都必须由作者本人确认。

---

## Русский

### Кратко

**PhD Thesis Butler — это open-source skill для AI-ассистентов, таких как Codex, Hermes, Claude Code и Antigravity. Он помогает планировать структуру русской диссертации, проверять доказательную базу и редактировать академический русский текст.**

Это не генератор диссертаций. Skill помогает автору планировать, проверять, связывать утверждения с источниками и улучшать уже написанный русский академический текст.

### Главные возможности

| Возможность | Когда использовать |
|---|---|
| **Русская академическая полировка** | Черновик уже написан, нужно улучшить стиль, связность и научную формулировку; это может помочь снизить машинный оттенок текста, но пока не проверено на полномасштабной оценке. |
| **Планирование диссертации** | Тема, идея, метод или требования руководителя уже есть, но нужна структура глав и логика исследования. |
| **Литературный поиск** | Нужно спланировать поиск по eLIBRARY, DisserCat, CyberLeninka, OpenAlex и нормализовать метаданные. |
| **Evidence-aware writing** | Нужно понять, какие утверждения требуют ссылок и какие источники подходят к главам. |
| **Частное расширение** | Пользователь хочет позже подключить собственный корпус или Zotero-библиотеку. |

### Типовые задачи

```text
Помоги спланировать структуру диссертации по управлению транспортным средством.
Разложи мою идею на проблему, цель, задачи, метод и экспериментальную проверку.
Проверь, какие утверждения во второй главе требуют ссылок.
Отполируй введение на русском, сохранив мой исходный смысл.
```

### Основные слои

```text
planning_layer/                         структура, главы, методология, эксперименты
assets/references/disciplines/          дисциплинарные writing profiles
research_layer/                         стратегии поиска и нормализация литературы
evidence_layer/                         роли источников, привязка к главам, citation gaps
assets/cluster/ + assets/global/        русские шаблоны и полировка
extension_layer/                        будущие пользовательские расширения
```

### Активы

| Слой | Объём | Назначение |
|---|---:|---|
| Русские шаблоны и полировка | 16 722 | Академические формулировки и редактирование текста. |
| Источник диссертационной дистилляции | 2 118 работ | Структура, методология, логика и дисциплинарные паттерны. |
| Глубокий анализ | 679 работ | Функции глав, методы, валидация, логические цепочки. |
| Дисциплинарные профили | 5 | Automation/control, science/engineering, agriculture/medicine, arts/sports, humanities/economics/politics. |
| Planning clusters | 6 | Преобразование идеи в план глав и проверочную логику. |

### Как использовать

Обычному пользователю не нужно запускать скрипты вручную. Активы и утилиты этого репозитория предназначены для вызова AI-ассистентом, например Codex, Hermes, Claude Code или Antigravity.

Пользователь формулирует задачу естественным языком:

```text
Помоги спланировать структуру русской диссертации.
Проверь, какие утверждения в этой главе требуют ссылок.
Свяжи мои источники с введением, обзором, методической и экспериментальной главами.
Отполируй этот русский академический текст, сохранив мой смысл.
```

### Проверка

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
python3 scripts/validate_research_layer.py
python3 scripts/validate_evidence_layer.py
python3 scripts/validate_dissertation_landscape.py
bash scripts/smoke_test.sh
```

### Ограничения

Skill не заменяет автора, научного руководителя, фактчекинг, рецензирование и академическую ответственность. Нельзя использовать его для автоматического создания полной диссертации или выдумывания источников.

---

## English

### In One Sentence

**PhD Thesis Butler is an open-source skill for AI assistants such as Codex, Hermes, Claude Code, and Antigravity. It helps with Russian dissertation planning, evidence-aware revision, and academic polishing.**

It is not a one-click dissertation generator. It helps authors structure real research, identify citation gaps, bind sources to chapters, and improve Russian academic writing while preserving the author's intent.

### Core Capabilities

| Workflow | Use it when | Layers involved |
|:---------|:------------|:----------------|
| **① Russian polishing** | You have a Russian draft and want better academic style, less machine-like phrasing | assets + retrieve_templates.py |
| **② Thesis planning** | You have a topic/idea and need full structure, chapters, methodology, experiments | planning_layer + discipline assets |
| **③ Literature & dissertation landscape** | You need to search the literature, find comparative Russian dissertations, compare structures/methods, use your Zotero library | research_layer + landscape/ |
| **④ Evidence & citation audit** | You have a chapter draft and need to check which claims lack citations, which sources support which chapter | evidence_layer + binding/gap scripts |

### Typical Prompts

```text
Plan a Russian dissertation structure for vehicle state estimation and control.
Break my research idea into problem, goal, tasks, method, experiment, and conclusion.
Check which claims in this chapter need citations.
Polish this Russian introduction while preserving my meaning and not adding new facts.
```

### Architecture

```text
 ─ Workflow ①: Polish & Templates
    assets/cluster/ + assets/global/     Russian sentence templates and polishing assets
 ─ Workflow ②: Thesis Planning
    planning_layer/                      dissertation structure, methodology, experiments
    assets/references/disciplines/       discipline-specific writing profiles (internal)
 ─ Workflow ③: Literature & Landscape
    research_layer/                      source profiles, search strategy, metadata normalization
    └── landscape/                       comparative dissertation analysis + Zotero (v5.4)
 ─ Workflow ④: Evidence & Citation
    evidence_layer/                      evidence roles, chapter binding, citation gap detection
 ─ Future
    extension_layer/                     future private corpus extension point
```

### Assets

| Layer | Scale | Role |
|---|---:|---|
| Russian expression and polishing layer | 16,722 entries | Sentence replacement, paragraph polishing, academic phrasing. |
| Dissertation paradigm source | 2,118 public Russian dissertations | Structure, methodology, logic chains, discipline patterns. |
| Deep analysis sample | 679 works | Chapter functions, validation patterns, logic closure. |
| Discipline assets | 5 profiles | Automation/control, science/engineering, agriculture/medicine, arts/sports, humanities/economics/politics. |
| Planning clusters | 6 clusters | Turns ideas into chapter blueprints and validation routes. |

### How To Use

End users do not need to run these scripts manually. The repository is designed for AI assistants such as Codex, Hermes, Claude Code, and Antigravity to call the right assets and utilities in the background.

Users can simply ask:

```text
Help me plan a Russian dissertation structure.
Check which claims in this chapter need citations.
Map these references to introduction, review, method, and experiment chapters.
Polish this Russian academic paragraph while preserving my meaning.
```

### Validation

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
python3 scripts/validate_research_layer.py
python3 scripts/validate_evidence_layer.py
python3 scripts/validate_dissertation_landscape.py
bash scripts/smoke_test.sh
```

### Roadmap

| Version | Focus |
|---|---|
| v5.1 | Discipline assets, methodology routes, logic chains, chapter rules. |
| v5.2 | Research layer for Russian and international literature workflows. |
| v5.3 | Evidence-aware writing: chapter evidence binding and citation gap reports. |
| v5.4 | **Dissertation Landscape**: agentic landscape comparison, DisserCat/eLIBRARY public search, Zotero private corpus, structure/methodology/validation pattern comparison, recommended outline → planning_layer. |

### Academic Integrity

The skill assists planning, checking, literature organization, polishing, and revision. It does not create the user's research contribution. All facts, citations, experiments, and conclusions must be verified and owned by the author.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
