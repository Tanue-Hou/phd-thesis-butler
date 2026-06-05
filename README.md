# PhD Thesis Butler v5.3.4 — Dissertation Writing Intelligence Platform

Russian dissertation writing and polishing skill for AI assistants.

[中文](#中文) · [Русский](#русский) · [English](#english)

---

## 🚀 能做什么 / What It Can Do / Возможности

| 📝 **论文结构规划** | 🔬 **俄罗斯文献调研** | 🌐 **英文文献检索** | 🔗 **文献证据绑定** |
|:---|:---|:---|:---|
| 给定研究方向，自动规划章节结构、方法论路线和实验方案 | 生成 eLIBRARY/DisserCat/РГБ/ CyberLeninka 检索策略（ВАК代码+关键词） | 支持 arXiv / Semantic Scholar / OpenAlex / Crossref 检索 | 将文献按证据角色绑定到 INTRO/SURVEY/METHOD/EXPERIMENT 等章节 |

| 🔍 **引用缺口检测** | 📊 **可读报告生成** | 🎯 **俄语学术润色** | ✅ **论文逻辑审校** |
|:---|:---|:---|:---|
| 检测段落中哪些论断缺引用，标记 missing/partial/covered | JSON→俄语Markdown报告（6大区块：风险→补引用→已覆盖→检索建议） | 基于16,722个俄语学术句模进行句式替换和语法修正 | 检查文章是否形成"问题→目标→方法→验证→结论"闭环 |

---

## 中文

### 这是什么

PhD Thesis Butler 是一个面向俄罗斯 кандидат наук / 博士论文写作的 Codex/Hermes skill。它不是"一键代写论文"的工具，而是一个可安装、可检索、可验证的论文写作辅助包。

#### 核心能力一览

| 能力 | 说明 |
|:-----|:-----|
| 📝 **论文结构规划** | 给定研究方向，自动规划章节结构、研究问题、方法论路线和实验验证方案 |
| 🔬 **俄罗斯文献调研** | 生成 eLIBRARY/РИНЦ、DisserCat、РГБ、CyberLeninka 的检索策略，含ВАК代码和学科关键词 |
| 🌐 **英文文献检索** | 支持 arXiv、Semantic Scholar、OpenAlex、Crossref 检索策略生成 |
| 🔗 **文献证据绑定** | 将查到的文献按证据角色绑定到具体章节（INTRO/SURVEY/METHOD/EXPERIMENT等） |
| 🔍 **引用缺口检测** | 检测用户段落中哪些论断需要引用，识别 missing/partial/covered 状态，给出补查建议 |
| 📊 **可读报告生成** | 将引用分析JSON转为俄语Markdown报告（必须补引用的句子、建议补充、已覆盖等6大区块） |
| 🎯 **俄语学术润色** | 基于16,722个俄语学术句模进行句式替换、语法修正和学术表达提升 |
| ✅ **论文逻辑审校** | 检查完整文章是否形成"问题→目标→任务→方法→验证→结论"闭环 |

v5.2 的核心目标是：**从"会写俄语论文"升级为"会调研俄罗斯文献、会规划论文结构、会引用证据、会润色成稿"的俄罗斯博士论文智能体。**


### 文献检索与调研能力

v5.2 受开源项目 [academic-search](https://github.com/ustc-ai4science/academic-search) 启发，在其多平台检索架构基础上，针对俄罗斯学术生态做了深度适配和功能扩展。

**俄语检索（特色强化）**

| 数据源 | 特色能力 |
|:-------|:---------|
| **eLIBRARY / РИНЦ** | 俄罗斯最大科学引文数据库。可检索期刊论文、会议论文、专著；获取РИНЦ引用数、ВАК专业代码、作者机构信息。适合支撑文献综述、актуальность论证、研究空白定位和引用依据。 |
| **DisserCat** | 俄罗斯学位论文目录。可检索相近 кандидат/доктор 论文；查看学科代码、章节结构预览、参考文献池。适合支撑论文结构范式参照、章节安排参考、相近选题对比、专业代码匹配。 |
| **РГБ / НЭБ** | 俄罗斯国家图书馆电子馆藏，作为 DisserCat 的官方补充验证源。 |
| **CyberLeninka** | 开放获取俄语论文平台，CC协议，全文可读。适合补充开放获取文献。 |

**英文/国际检索（academic-search 融合）**

| 数据源 | 特色能力 |
|:-------|:---------|
| **arXiv** | 预印本，适合最新方法追踪，OAI-PMH API |
| **Semantic Scholar** | 语义搜索+引用图，适合高引论文定位和引用分析 |
| **OpenAlex** | 开放学术图谱，250M+作品，免费API，适合文献计量 |
| **Crossref** | DOI元数据+引用关系，适合补全引用格式 |

**融合方式**

不是将 academic-search 的代码直接复制，而是借鉴其**平台路由 + 统一元数据 schema + 两遍检索 + 去重合并**的架构思路，重新针对俄罗斯论文写作场景设计：

- 新增 `research_layer/` 完整调研工作流（检索策略生成 → 文献接收 → 元数据标准化 → 综述生成）
- 8 个数据源各配独立 profile（搜索方法、字段映射、限制说明）
- 5 个学科各有专用检索模板（关键词、ВАК代码、典型检索式）
- 输出统一为 `russian_literature_record` / `russian_dissertation_record` 两种 schema
- 参考文献列表支持 ГОСТ Р 7.0.5-2008 和 Harvard 两种引用格式


### 作用边界

这个 skill 能帮助智能体更像一位“论文写作助手”和“结构审稿助手”：

- 理解用户的研究想法，并转化为论文结构；
- 判断论文适合哪类学科写作范式；
- 给出章节级写作动作，例如引言如何提出问题、方法章如何建立模型、实验章如何验证；
- 检索俄语学术表达模板，帮助用户改写或润色；
- 检查完整文章或章节是否形成问题-目标-任务-方法-验证-结论闭环；
- 对已经写完的文章进行基于原始思路的润色，而不是脱离作者意图重写；
- 提醒常见错误，例如目标过宽、任务和结论不对应、实验指标不足、章节功能混乱。

它不能替代：

- 作者本人的研究贡献；
- 导师意见；
- 事实核验；
- 学术伦理判断；
- 学校或期刊的正式审查。

禁止将本 skill 用于自动生成完整学位论文、规避学术审查或把模板原样复制为最终论文。

### 数据与资产

公开包只包含蒸馏后的写作资产，不包含原始 PDF、全文、作者可追溯信息、LLM 调用记录或私有构建缓存。

| 资产层 | 数量 / 状态 | 作用 |
|---|---:|---|
| 俄语表达与润色模板层 | 16,722 条 | 用于句式替换、段落润色、章节表达增强；这是润色层，不代表整个系统规模。 |
| 论文范式蒸馏来源 | 2,118 篇公开俄罗斯学位论文 | 用于形成结构、方法论、逻辑链和学科写作范式。 |
| 深度语义分析样本 | 679 篇 | 用于提取章节功能、方法路线、实验验证模式和逻辑闭环规则。 |
| 学科大类知识资产 | 5 个 | 覆盖自动化控制、理工、农医、艺术体育、人文政经。 |
| 论文规划推理聚类 | 6 个 | 用于从研究想法生成章节蓝图、实验设计和导师汇报结构。 |
| 表达质量分级 | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 | 用于优先调用高质量俄语表达模板。 |

换句话说，`16,722` 是**语言表达和润色引擎**的规模；整个 skill 的核心价值在于把这些表达模板与论文结构范式、方法论路线、实验验证模式和逻辑闭环规则组合成一个可调用的 dissertation-writing intelligence system。

五大学科大类资产位于 `assets/references/disciplines/`：

- `AUTOMATION_CONTROL`：自动化、控制、车辆控制方向，深度增强；
- `SCI_TECH`：理工类；
- `AGRI_MED`：农医类；
- `ARTS_SPORTS`：艺术体育类；
- `HUM_POL_ECON`：人文、政治、经济类。

规划层位于 `planning_layer/`，用于论文结构、章节任务、方法论路线、实验方案和逻辑链设计。

### 版本迭代

| 版本 | 重点 | 说明 |
|---|---|---|
| v1.0 | 初始句式库 | 手工整理基础俄语学术表达。 |
| v2.0 | 模板扩展 | 从公开俄罗斯论文中扩展到较大规模句式模板。 |
| v3.0 | 质量体系 | 引入 Q0/Q1/Q2 质量分级、学科聚类和三层检索。 |
| v3.3.5 | 稳定基线 | 完成资产校验、规划层和较稳定的运行时模板检索。 |
| v4.0 | 语料蒸馏设计 | 从单纯句式库升级为论文结构、方法论、逻辑链蒸馏系统。 |
| v5.0 | 全量范式资产 | 汇总 2,118 篇分类论文和 679 篇深度分析，形成五大学科资产。 |
| v5.1.0 | 不重训练升级 | 保留原句式库，增强结构、方法论、逻辑链、章节写作规则。 |
| v5.1.1 | 学科资产标准化 | 五大学科 JSON 统一为七类资产格式，并加入 evidence 字段。 |
| v5.1.2 | 语义级清理 | 修复中文污染、混合语言条目和检索暴露问题。 |
| v5.1.3 | 运行时可靠性 | 强化验证器、隐藏 mixed 条目、重写 README、明确公开包边界。 |
| v5.2.0 | Russian Research Layer | 新增调研层：8个数据源profile、2个元数据schema、文献标准化与综述生成脚本。 |
| v5.2.1 | 一致性修复 | 版本统一、CJK深层清理、normalize字段兼容、build_literature_review_brief.py入库。 |
| v5.2.2 | 最终收尾 | 版本统一到5.2.2、检索能力说明、学科映射增强、brief去重、目录树补全。 |
| v5.3.0 | Evidence-Aware Writing | 新增证据层：12种证据角色、3个绑定schema、引用缺口检测规则、16/16验证门禁。 |
| v5.3.1 | Chapter Binding + Gap Detection | 章节证据绑定脚本 + 引用缺口检测脚本 + 24/24验证门禁。 |
| v5.3.2 | 质量优化 | coverage指标语义修正、SKILL.md精简至519行。 |
| v5.3.3 | 证据层稳定化 | 6种新claim类型、reason解释字段、render报告脚本、evals测试集。 |
| v5.3.4 | Zotero兼容 + 报告修复 | year=null修复、版本统一、报告语义修正、27/27验证门禁。 |

### 能做什么

#### 1. 基于想法规划论文

当用户只有研究思路时，智能体可以帮助：

- 判断研究方向对应的学科大类；
- 生成博士论文整体结构；
- 设计章节顺序和每章功能；
- 把“研究想法”拆成问题、目标、任务、方法、实验、结论；
- 给出导师汇报或开题报告框架；
- 建议哪些章节需要模型、实验、对比、消融、案例或规范论证。

示例：

```text
我想写车辆横向控制和状态估计方向的俄语博士论文，请帮我规划整体结构。
我只有一个想法：用多传感器融合提高控制稳定性，请帮我拆成研究问题、目标、任务和实验路线。
帮我设计一个控制类博士论文的章节顺序，并说明每章应该完成什么写作功能。
```

#### 2. 润色已经完成的文章

当用户已经写完一章、一个小节或整篇文章时，智能体可以帮助：

- 保留作者原始思路，不改变核心论点；
- 把口语化或机器化表达改成更自然的俄语学术表达；
- 检查术语、句式、段落衔接和章节功能是否一致；
- 按俄罗斯论文常见结构重排段落；
- 检查结论是否回应目标和任务；
- 给出“应该改哪里、为什么改、如何改”的建议。

示例：

```text
这是我写完的俄语引言，请基于我的原始思路进行学术润色，不要改变研究含义。
请检查这篇文章是否有 AI 味太重、逻辑跳跃或俄语学术表达不自然的问题。
请按俄罗斯博士论文风格润色这一章，并指出哪些段落需要重排。
请只优化表达和逻辑衔接，不新增未经我提供的事实。
```

#### 3. 检索俄语句式模板

当用户需要某一章节的表达时，智能体可以调用句式库：

```bash
python3 scripts/retrieve_templates.py \
  --category INTRO \
  --cluster AUTOMATION_CONTROL \
  --query "цель исследования актуальность" \
  --limit 5
```

常用 `category`：

- `INTRO`：引言、 актуальность、目标、任务；
- `SURVEY`：文献综述、已有方法、研究空白；
- `MODEL`：模型、假设、变量、约束；
- `METHOD`：方法、算法、流程；
- `EXPERIMENT`：实验设计、指标、对比；
- `RESULT`：结果描述；
- `DISCUSSION`：讨论、限制、解释；
- `CONCLUSION`：结论、贡献、未来工作；
- `TRANSITION`：章节过渡。

普通检索默认隐藏 `v5_lang=mixed` 条目，只返回俄语安全内容。

#### 4. 检查逻辑闭环

适合检查完整文章或章节链条：

```text
请检查我的论文是否形成：问题 → 目标 → 任务 → 方法 → 实验 → 结果 → 结论 的闭环。
请找出这篇文章中目标和结论不对应的地方。
请检查实验指标是否足以支撑我的研究贡献。
```

#### 5. 支持私有扩展

用户可以未来用自己的论文或领域文献构建私有扩展包。公开 skill 不直接包含用户私有语料；建议在本地完成抽取、脱敏、聚合，再接入 `extension_layer/`。

### 运行逻辑

智能体应按任务类型选择资产：

| 用户意图 | 优先资产 |
|---|---|
| 论文规划、开题、章节结构 | `planning_layer/` |
| 学科范式、方法论路线、逻辑链 | `assets/references/disciplines/` |
| 俄语句式、段落表达、润色替换 | `scripts/retrieve_templates.py` + `assets/cluster/` + `assets/global/` |
| 已完成文章润色 | 先理解作者思路，再结合句式库和学科规则局部改写 |
| 用户私有论文学习 | `extension_layer/` 作为未来私有扩展入口 |

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
├── research_layer/
│   ├── sources/ (8 data sources)
│   ├── templates/ (5 discipline strategies)
│   └── examples/
├── evidence_layer/
│   ├── EVIDENCE_ROLE_TAXONOMY.md
│   ├── CHAPTER_EVIDENCE_BINDING.md
│   ├── CITATION_GAP_DETECTION.md
│   ├── templates/
│   └── examples/
├── planning_layer/
│   ├── clusters/
│   ├── patterns/
│   ├── schemas/
│   ├── templates/
│   ├── THESIS_PLANNER.md
│   ├── METHODOLOGY_GUIDE.md
│   ├── LOGIC_FLOW_GUIDE.md
│   └── EXPERIMENT_DESIGN_GUIDE.md
├── scripts/
│   ├── retrieve_templates.py
│   ├── normalize_russian_metadata.py
│   ├── build_literature_review_brief.py
│   ├── validate_skill_assets.py
│   ├── validate_planning_assets.py
│   ├── validate_research_layer.py
│   ├── validate_evidence_layer.py
│   └── smoke_test.sh
├── research_layer/
├── evidence_layer/
└── extension_layer/
```

### 验证

公开仓库可直接运行：

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
bash scripts/smoke_test.sh
```

这些检查覆盖版本一致性、资产目录、discipline JSON schema、planning layer、CJK 污染、检索脚本和本地路径泄漏。

### 公开包与私有管线边界

公开包只保留用户运行所需的资产和脚本。以下内容不属于公开包：

- 原始论文 PDF；
- `.phd_build/`；
- Layer 0-6 全量处理脚本；
- 私有 LLM 调用记录；
- 作者、学校、具体论文级追溯信息；
- 私有测试或抽样审计目录。

如果继续训练或蒸馏新的论文，应在本地私有管线完成，再把脱敏后的聚合资产发布到 `assets/references/`。

### 学术诚信

本 skill 是学术写作辅助工具。它可以帮助规划、润色、检查和检索表达，但不能替代作者的研究工作。任何输出都必须由作者本人进行实质性修改、事实核验、逻辑整合和学术责任承担。

---

## Русский

### Что это такое

PhD Thesis Butler — это skill для Codex/Hermes, предназначенный для помощи в написании российских диссертаций уровня кандидат наук / PhD. Это не инструмент для автоматического написания диссертации. Это пакет проверяемых письменных активов, который помогает AI-ассистенту работать как помощник по структуре, методологии, логике и русскоязычной академической формулировке.

Skill полезен в двух основных ситуациях:

- **От идеи к плану**: у пользователя есть тема, гипотеза, метод или требования научного руководителя; skill помогает построить структуру, задачи, методологию и план проверки.
- **От готового текста к улучшению**: у пользователя уже есть статья, глава, раздел или черновик; skill помогает отполировать стиль, улучшить логику, сохранить исходный смысл и приблизить текст к русской академической манере.

Цель v5.2: **дать ассистенту возможность не только писать диссертацию, но и исследовать российскую научную литературу, планировать структуру, подбирать источники и оформлять обзор.**

### Роль и границы

Skill помогает:

- превратить исследовательскую идею в структуру диссертации;
- определить дисциплинарный профиль;
- спланировать главы и функции разделов;
- выбрать методологический маршрут;
- подобрать русскоязычные академические шаблоны;
- проверить цепочку проблема-цель-задачи-метод-проверка-вывод;
- редактировать уже написанный текст, сохраняя мысль автора;
- выявлять типичные ошибки структуры, логики и выражения.

Skill не заменяет автора, научного руководителя, фактчекинг, рецензирование или академическую ответственность. Его нельзя использовать для автоматической генерации полной диссертации или обхода академической этики.

### Данные и активы

Публичный пакет содержит только дистиллированные активы. Он не содержит исходные PDF, полные тексты, имена авторов, трассируемые метаданные, журналы LLM-вызовов или приватные build-кэши.

| Уровень активов | Значение | Назначение |
|---|---:|---|
| Уровень русской формулировки и полировки | 16 722 записи | Используется для переформулирования, стилистической полировки и усиления академического выражения; это языковой слой, а не весь масштаб системы. |
| Источник дистилляции диссертационных парадигм | 2 118 публичных российских диссертаций | Основа для структур, методологии, логических цепочек и дисциплинарных моделей письма. |
| Глубокий семантический анализ | 679 работ | Извлечение функций глав, методологических маршрутов, экспериментальных схем и правил логической замкнутости. |
| Дисциплинарные knowledge assets | 5 профилей | Автоматизация/управление, science/engineering, agriculture/medicine, arts/sports, humanities/politics/economics. |
| Планировочные кластеры | 6 кластеров | Преобразование исследовательской идеи в структуру глав, экспериментальный дизайн и план доклада руководителю. |
| Качество выражений | Q2: 4 236 / Q1: 10 486 / Q0: 2 000 | Приоритетное использование более сильных русскоязычных формулировок. |

Иными словами, `16 722` — это масштаб **языкового и полировочного слоя**. Главная ценность skill — объединение этого слоя со структурами диссертаций, методологическими маршрутами, экспериментальными паттернами и правилами логической замкнутости.

Пять профилей находятся в `assets/references/disciplines/`:

- `AUTOMATION_CONTROL`: автоматизация, управление, транспортные системы; усиленный профиль;
- `SCI_TECH`: инженерные и естественно-научные направления;
- `AGRI_MED`: аграрные и медицинские направления;
- `ARTS_SPORTS`: искусство, культура, спорт;
- `HUM_POL_ECON`: гуманитарные, политические и экономические направления.

Планировочные материалы находятся в `planning_layer/`.

### История версий

| Версия | Фокус | Описание |
|---|---|---|
| v1.0 | Базовые фразы | Ручная коллекция академических русских формулировок. |
| v2.0 | Расширение шаблонов | Увеличение корпуса шаблонов на основе публичных диссертаций. |
| v3.0 | Качество и поиск | Q0/Q1/Q2, кластеризация, трехуровневый retrieval. |
| v3.3.5 | Стабильная база | Валидация активов, planning layer, стабильный runtime retrieval. |
| v4.0 | Дистилляция корпуса | Переход от банка фраз к структуре, методологии и логике диссертации. |
| v5.0 | Полные профильные активы | 2 118 классифицированных работ и 679 глубоких анализов. |
| v5.1.0 | Обновление без дообучения | Усиление структуры, методологии, логических цепочек и правил глав. |
| v5.1.1 | Стандартизация профилей | Пять discipline JSON приведены к единому формату. |
| v5.1.2 | Семантическая чистка | Исправлены mixed/CJK записи и runtime-фильтрация. |
| v5.1.3 | Надежность runtime | Усилен validator, hidden mixed entries, уточнены README и границы пакета. |
| v5.2.0 | Russian Research Layer | Добавлен исследовательский слой: 8 профилей, 2 схемы метаданных, скрипты нормализации и обзора. |
| v5.2.1 | Исправление согласованности | Унификация версий, очистка CJK, совместимость полей normalize, интеграция Research Layer в SKILL.md. |
| v5.2.2 | Финальное закрытие | Унификация версии до 5.2.2, описание поисковых возможностей, усиление маппинга дисциплин. |
| v5.3.0 | Evidence-Aware Writing | Добавлен слой Evidence Layer: 12 ролей свидетельств, 3 схемы привязки, правила обнаружения пробелов в цитировании. |
| v5.3.1 | Chapter Binding + Gap Detection | Скрипты привязки глав и обнаружения пробелов в цитировании, 24/24 проверки. |
| v5.3.2 | Оптимизация качества | Исправление семантики coverage, сокращение SKILL.md до 519 строк. |
| v5.3.3 | Стабилизация Evidence Layer | 6 новых типов claim, поле reason, скрипт отчёта, evals-тесты. |
| v5.3.4 | Совместимость с Zotero | Исправление year=null, унификация версий, исправление семантики отчёта. |

### Что можно делать
### Возможности поиска литературы

v5.2 вдохновлён открытым проектом [academic-search](https://github.com/ustc-ai4science/academic-search). На его многоплатформенной архитектуре поиска выполнена глубокая адаптация под российскую академическую экосистему.

**Поиск на русском языке**

| Источник | Возможности |
|:---------|:------------|
| **eLIBRARY / РИНЦ** | Крупнейшая база научных статей России. Поиск журнальных статей, конференций, монографий; получение числа цитирований РИНЦ, кодов ВАК, информации об авторах и организациях. |
| **DisserCat** | Каталог диссертаций. Поиск кандидатских и докторских диссертаций по специальности; просмотр структуры глав, списка литературы. |
| **РГБ / НЭБ** | Официальное дополнение к DisserCat, электронный фонд РГБ. |
| **CyberLeninka** | Открытые статьи на русском языке, лицензия CC, полный текст доступен. |

**Поиск на английском языке**

| Источник | Возможности |
|:---------|:------------|
| **arXiv** | Препринты, OAI-PMH API, категорийный поиск |
| **Semantic Scholar** | Семантический поиск, граф цитирований |
| **OpenAlex** | Открытая академическая карта, 250M+ работ |
| **Crossref** | DOI-метаданные, связи цитирований |




#### Планирование по идее

```text
Помоги спланировать структуру диссертации по управлению транспортным средством.
У меня есть идея о мультисенсорном слиянии для устойчивости управления. Разложи ее на проблему, цель, задачи и эксперименты.
Составь план глав для диссертации по автоматическому управлению и объясни функцию каждой главы.
```

#### Полировка готового текста

```text
Вот готовое введение на русском. Отполируй его академически, сохранив мой смысл.
Проверь, нет ли в этом разделе машинного стиля, логических скачков или слабой русской академической формулировки.
Перестрой абзацы этой главы под стиль российской диссертации, но не добавляй новых фактов.
```

#### Поиск шаблонов

```bash
python3 scripts/retrieve_templates.py \
  --category METHOD \
  --cluster AUTOMATION_CONTROL \
  --query "модель эксперимент верификация" \
  --limit 5
```

Категории: `INTRO`, `SURVEY`, `MODEL`, `METHOD`, `EXPERIMENT`, `RESULT`, `DISCUSSION`, `CONCLUSION`, `TRANSITION`.

Обычный поиск скрывает записи с `v5_lang=mixed`.

#### Проверка логики

```text
Проверь, замкнута ли логика проблема → цель → задачи → метод → эксперимент → вывод.
Найди места, где выводы не отвечают заявленным задачам.
Проверь, достаточно ли экспериментальных метрик для заявленного вклада.
```

### Runtime-логика

| Запрос пользователя | Основной актив |
|---|---|
| План, структура, главы | `planning_layer/` |
| Методология, логика, дисциплинарная модель | `assets/references/disciplines/` |
| Фразы, абзацы, редактирование | `scripts/retrieve_templates.py` и JSONL-активы |
| Полировка готовой статьи | Сначала смысл автора, затем локальная правка по шаблонам и правилам |
| Частный корпус пользователя | `extension_layer/` как будущий вход |

### Структура репозитория

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
│   ├── normalize_russian_metadata.py
│   ├── build_literature_review_brief.py
│   ├── validate_skill_assets.py
│   ├── validate_planning_assets.py
│   ├── validate_research_layer.py
│   ├── validate_evidence_layer.py
│   └── smoke_test.sh
├── research_layer/
├── evidence_layer/
└── extension_layer/
```

### Проверка

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
bash scripts/smoke_test.sh
```

### Академическая этика

Все результаты должны быть переработаны, проверены и интегрированы автором. Skill помогает писать, планировать и редактировать, но не создает научный вклад вместо пользователя.

---

## English

### What This Is

PhD Thesis Butler is a Codex/Hermes skill for assisting with Russian кандидат наук / PhD dissertation writing. It is not a one-click dissertation generator. It is a structured, auditable writing-support package that helps an AI assistant use distilled Russian dissertation-writing patterns.

It supports two major workflows:

- **From idea to plan**: when the user has a topic, hypothesis, method idea, or supervisor requirement, the skill helps build dissertation structure, research questions, methodology, experiments, and logic flow.
- **From finished draft to polished text**: when the user already has an article, chapter, section, or Russian draft, the skill helps polish academic expression, improve paragraph logic, preserve the author's meaning, and align the text with Russian dissertation style.

The goal of v5.2 is: **give assistants the ability to not only write dissertations, but also research Russian academic literature, plan structure, find sources, and generate bibliographies.**

### Role and Boundaries

The skill helps an assistant:

- turn research ideas into dissertation plans;
- classify the user's field into a writing profile;
- design chapter sequence and chapter functions;
- choose methodology routes;
- retrieve Russian academic sentence patterns;
- check problem-goal-task-method-validation-conclusion closure;
- polish already written work while preserving the author's intent;
- detect common failures in structure, logic, and expression.

It does not replace the author, supervisor, peer review, fact checking, or academic responsibility. It must not be used to auto-generate a full dissertation or bypass academic integrity requirements.

### Data and Assets

The public package contains distilled writing assets only. It does not include raw PDFs, full source texts, author-traceable metadata, LLM call logs, or private build caches.

| Asset layer | Value | Role |
|---|---:|---|
| Russian expression and polishing layer | 16,722 entries | Used for sentence replacement, paragraph polishing, and academic expression enhancement; this is the language layer, not the whole system. |
| Dissertation paradigm distillation source | 2,118 public Russian dissertations | Basis for structure, methodology, logic chains, and discipline-specific writing patterns. |
| Deep semantic analysis sample | 679 papers | Extracts chapter functions, methodology routes, validation patterns, and logic-closure rules. |
| Discipline knowledge assets | 5 profiles | Automation/control, science/engineering, agriculture/medicine, arts/sports, humanities/politics/economics. |
| Planning-reasoning clusters | 6 clusters | Turns research ideas into chapter blueprints, experiment designs, and supervisor-report structures. |
| Expression quality tiers | Q2: 4,236 / Q1: 10,486 / Q0: 2,000 | Prioritizes stronger Russian academic formulations at retrieval time. |

In short, `16,722` is the scale of the **language and polishing engine**. The real value of the skill is the combination of that expression layer with dissertation structure paradigms, methodology routes, validation patterns, and logic-closure rules.

The five discipline profiles live in `assets/references/disciplines/`:

- `AUTOMATION_CONTROL`: automation, control, vehicle control; enhanced profile;
- `SCI_TECH`: science and engineering;
- `AGRI_MED`: agriculture and medicine;
- `ARTS_SPORTS`: arts, culture, and sports;
- `HUM_POL_ECON`: humanities, politics, and economics.

Planning assets live in `planning_layer/`.

### Version History

| Version | Focus | Notes |
|---|---|---|
| v1.0 | Initial phrases | Manually curated Russian academic expressions. |
| v2.0 | Template expansion | Larger template bank from public Russian dissertations. |
| v3.0 | Quality and retrieval | Q0/Q1/Q2 quality scoring, clustering, three-level retrieval. |
| v3.3.5 | Stable baseline | Validation, planning layer, stable runtime retrieval. |
| v4.0 | Corpus distillation | Shift from sentence bank to structure, methodology, and logic assets. |
| v5.0 | Full paradigm assets | 2,118 classified papers and 679 deep analyses. |
| v5.1.0 | No-retrain upgrade | Added structure, methodology, logic-chain, and chapter-writing rules. |
| v5.1.1 | Profile standardization | Five discipline JSON files standardized. |
| v5.1.2 | Semantic cleanup | Mixed/CJK entries and retrieval exposure fixed. |
| v5.1.3 | Runtime reliability | Stronger validation, hidden mixed entries, clearer README and boundaries. |
| v5.2.0 | Russian Research Layer | New research layer: 8 source profiles, 2 metadata schemas, literature normalization and review scripts. |
| v5.2.1 | Consistency fixes | Version unification, CJK cleanup, normalize compat, build script tracked. |
| v5.2.2 | Final closure | Version unified to 5.2.2, search capability docs, discipline mapping enhancement, brief dedup. |
| v5.3.0 | Evidence-Aware Writing | New evidence layer: 12 evidence roles, 3 binding schemas, citation gap rules, 16/16 validation gate. |
| v5.3.1 | Chapter Binding + Gap Detection | Chapter evidence binding + citation gap detection scripts, 24/24 validation. |
| v5.3.2 | Quality optimization | Coverage ratio semantic fix, SKILL.md condensed to 519 lines. |
| v5.3.3 | Evidence layer stabilization | 6 new claim types, reason field, render report script, evals test suite. |
| v5.3.4 | Zotero compatibility + report fix | year=null fix, version unification, report semantics, 27/27 validation. |
### Literature Search Capabilities

v5.2 is inspired by the open-source [academic-search](https://github.com/ustc-ai4science/academic-search) project. Built on its multi-platform search architecture, we deeply adapt it for the Russian academic ecosystem.

**Russian-language search**

| Source | Capabilities |
|:-------|:-------------|
| **eLIBRARY / RINC** | Russia's largest scientific citation database. Search journal articles, conference papers, monographs; retrieve RINC citation counts, VAK specialty codes, author/institution info. |
| **DisserCat** | Russian dissertation catalog. Search candidate/doctoral theses by specialty code; preview chapter structure and bibliography. |
| **RSL / NEB** | Russian State Library electronic collection, official supplement to DisserCat. |
| **CyberLeninka** | Open-access Russian papers, CC license, full text available. |

**English-language search**

| Source | Capabilities |
|:-------|:-------------|
| **arXiv** | Preprints, OAI-PMH API, category-based search |
| **Semantic Scholar** | Semantic search, citation graph, influential citations |
| **OpenAlex** | Open scholarly graph, 250M+ works, free API |
| **Crossref** | DOI metadata, citation relationships |




### What It Can Do

#### Plan From an Idea

```text
Plan a Russian dissertation structure for a vehicle-control topic.
I have an idea about multisensor fusion for control stability. Break it into problem, goal, tasks, and experiments.
Design the chapter sequence for an automation-control dissertation and explain each chapter's function.
```

#### Polish a Finished Draft

```text
Here is my completed Russian introduction. Polish it academically while preserving my meaning.
Check whether this section sounds too machine-generated, has logic jumps, or uses unnatural Russian academic phrasing.
Reorganize this chapter in Russian dissertation style, but do not add facts I did not provide.
```

#### Retrieve Russian Templates

```bash
python3 scripts/retrieve_templates.py \
  --category METHOD \
  --cluster AUTOMATION_CONTROL \
  --query "модель эксперимент верификация" \
  --limit 5
```

Common categories: `INTRO`, `SURVEY`, `MODEL`, `METHOD`, `EXPERIMENT`, `RESULT`, `DISCUSSION`, `CONCLUSION`, `TRANSITION`.

Normal retrieval hides entries tagged `v5_lang=mixed`.

#### Check Logic Closure

```text
Check whether my dissertation closes the chain: problem → goal → tasks → method → experiment → conclusion.
Find conclusions that do not answer the stated tasks.
Check whether my experimental metrics are enough to support the claimed contribution.
```

### Runtime Routing

| User intent | Main asset |
|---|---|
| Planning, structure, chapters | `planning_layer/` |
| Methodology, logic, discipline profile | `assets/references/disciplines/` |
| Phrases, paragraphs, polishing | `scripts/retrieve_templates.py` and JSONL assets |
| Finished article polishing | Preserve author's idea first, then apply local style and logic edits |
| User private corpus | `extension_layer/` as a future extension entry |

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
│   ├── normalize_russian_metadata.py
│   ├── build_literature_review_brief.py
│   ├── validate_skill_assets.py
│   ├── validate_planning_assets.py
│   ├── validate_research_layer.py
│   ├── validate_evidence_layer.py
│   └── smoke_test.sh
├── research_layer/
├── evidence_layer/
└── extension_layer/
```

### Validation

```bash
python3 scripts/validate_skill_assets.py --deep
python3 scripts/validate_planning_assets.py
bash scripts/smoke_test.sh
```

### Academic Integrity

All outputs must be revised, checked, and academically owned by the author. The skill helps with writing, planning, polishing, and review; it does not create the user's research contribution.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
