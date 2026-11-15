# PhD Thesis Butler v5.4.1

Russian dissertation planning, evidence-aware revision, and academic polishing skill for AI assistants such as Codex, Hermes, Claude Code, and Antigravity.

[中文](#中文) · [Русский](#русский) · [English](#english)

---

## 中文

**PhD Thesis Butler 是一个开源俄语论文写作 Skill，可供 Codex、Hermes、Claude Code、Antigravity 等智能体调用，用于论文结构规划、文献证据检查和俄语学术润色。**

它面向正在写俄语 кандидат наук / PhD / 博士论文、俄语期刊论文、开题报告、章节草稿和文献综述的人。它的目标是帮助用户把研究想法变成结构清晰、证据更稳、表达更像俄罗斯学术写作的论文文本。

> 它不是代写工具。它不替代作者贡献、导师判断、事实核验或学术伦理责任。

### 2026-11-15：已合入的可靠性修复与下一步

当前版本标识仍为 **v5.4.1**。以下三批代码已进入 `main`，不代表 v5.4.2 全部完成，也不代表历史语料已完成清洗、来源验真或授权核验。

| 已合入提交 | 本次提交了什么 | 边界 |
|---|---|---|
| [`31a2273`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/31a227378339bbf86c5f7a60f7c199cbdfc88b2c) | 修复失效检索路径；按记录内 `v5_cluster` 跨目录筛选；非空查询没有词汇重合时不再返回无关结果；补充命中层、别名与未验证标签说明和检索回归。 | 按标签过滤不等于标签正确；旧别名映射可能损失语义。 |
| [`4ad61ab`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/4ad61abc9ac1788a086213e06db97df21d6b823d) | 停止启发式来源错配；L1 改为显式经审阅映射及独立输出；转换重跑保护、备份与稳定 ID；元数据无损去重和错误退出；引用候选不再自动判为充分证据；修复 Zotero 导入失败/空结果、章节解析和 deep 检查退出行为。 | 修复防止继续产生错误，不会自动恢复历史作品身份；词汇/角色匹配仍需查原文。 |
| [`93da703`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/93da703db9a2207c57a8725916d46901d55b2017) | 新增 `preview_asset_repairs.py`、14 项测试和隔离预览说明；拒绝重复 JSON 键、非有限数、键/ID 冲突及已有输出目录，生成逐文件哈希和精确变更清单。 | **仅合入工具、测试与说明，真实 `assets/` 未迁移。** 1,405 行损坏键及 13 组、41 条重复 ID 的修复仅在隔离副本验证，3 处歧义键仍保留。 |

**已记录的云端离线验证：**首批 16 项、第二批 41 项、第三批 14 项回归通过；smoke 11/11、planning 22/22、research 17/17、evidence 27/27、临时样例 deep 229/229 通过。skill 检查仍提示缺少可选 `evals/`。Zotero 使用 mock/本地样例，不是实际服务验收；这些结果不是 GitHub CI 或生产端到端认证。

**剩余 bug 修复纳入下一阶段，与扩库准备一并推进：**

1. **来源与分类：**先恢复旧构建的最小来源索引，逐条核对作品身份、`v5_cluster` 和依据；不能由旧标签倒造作者、机构或来源。
2. **可确定数据修复：**审阅隔离预览清单，核对仓库外的旧 ID 引用、保留快照后再采用；不整目录覆盖新工作。合法 `[...]` 槽位及中文说明不作一刀切删除。
3. **统计与引用：**用实际资产重建 `BUILD_INFO` 统计口径；章节统计回查真实目录，不按任意章数阈值冒充验真；补充引用语义反例和原文支持核验。
4. **可靠性与权利链：**完善 L1 部分输出、L2 原子写入和验证器临时文件并发隔离；核对来源许可、私有内容边界和撤销链。脱敏不等于获得使用或公开发布授权。
5. **30,000 篇扩库准备：**在可追溯来源、分类和质量基线之上，按文章类别蒸馏知识与场景化学术表达，建立独立评测和小批校准；当前未执行扩库或外部模型蒸馏。

细节见 [第二批修复记录](REMAINING_REPAIRS.md) 与 [资产修复隔离预览](ASSET_REPAIR_PREVIEW.md)。两份记录中的“候选/未推送”为当时打包状态；上述提交现已合入，但资产迁移和未解决项仍未完成。

### 最核心能做什么

核心能力概览：

| 工作流 | 什么时候用 | 涉及哪些层 |
|:-------|:-----------|:------------|
| **① 俄语润色与表达优化** | 已有俄语段落/全文，需要润色、改写、降机器感、查句式 | assets + retrieve_templates.py |
| **② 论文规划与结构设计** | 只有研究方向/想法，需要完整的论文结构、章节顺序、方法路线、实验方案 | planning_layer + discipline assets |
| **③ 文献调研与论文对比** | 需要查文献、找同方向俄罗斯论文、对比结构/方法/验证、用 Zotero 私有库 | research_layer + landscape/ + dissercat/elibrary |
| **④ 证据检查与引用修复** | 已有章节草稿，需要检查哪些论断缺引用、文献该放哪一章 | evidence_layer + binding/gap scripts |

### 核心亮点

| 亮点 | 说明 |
|:-----|:------|
| 🔍 **俄罗斯学位论文搜索** | 直接检索 **DisserCat**（俄罗斯学位论文库）、**eLIBRARY / RINC**（俄罗斯核心期刊）、**CyberLeninka**（开放获取）等俄罗斯本土文献源，不仅仅是国际数据库 |
| 📚 **Zotero 私有库直连** | 支持读取本地 Zotero 文献库的元数据、标签、集合、已索引全文，按条件搜索筛选后直接进入论文对比分析——**不需要手动导出** |
| 🏗 **同方向论文结构对比** | 从公开来源或 Zotero 获取 10-30 篇同方向论文，自动聚类主题、对比章节结构模式、方法论路线和验证方式，生成 12 节结构化报告 + 推荐大纲 |
| 📝 **16,722 条俄语学术句式** | 从 2,118 篇俄罗斯学位论文中蒸馏出的俄语原生句式模板，历史构建覆盖引言至结论；当前句式从实际 JSONL 检索，学科画像独立读取 |
| 🧩 **论文全流程规划** | 从研究方向自动生成完整论文结构：整体章节设计（6大学科×5种结构模式）、方法论路线选择、实验方案设计、各章节写作功能定义和输入输出——不是只给大纲框架，而是每章该写什么、怎么展开、和前后章节如何闭环 |
| ✅ **引用缺口检测** | 逐句检测章节草稿中的论断是否缺引用，12 种证据角色，输出候选与缺口状态；词汇匹配只标为 `partial/weak`、`candidate_unverified`，不自动证明引用支持 |

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

公开仓库的设计范围是脱敏、蒸馏后的知识资产，不应包含原始 PDF、全文语料、私有 LLM 调用记录或 `.phd_build/` 构建缓存；历史来源、许可和隐私边界仍待逐项核验，不能据此宣称全库已合规。

下表 16,722 / 2,118 / 679 等为历史构建口径，尚未重新核实。当前快照有 30,952 条 JSONL 物理记录、16,958 条不同完整记录、14,851 个不同模板文本，均不是已验真论文篇数；跨文件重复也不直接等于错误。

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

`v5.4.1` 当前验证覆盖：

- 版本一致性；
- 资产 JSON / JSONL 可解析；
- planning layer 完整性；
- research layer 元数据标准化；
- evidence layer schema 与安全不变量；
- dissertation landscape 样例管线（原始样例→JSON→Markdown）；
- Zotero API 能力门控和降级。
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
| v5.4.1 | **工作流路由收敛**：6 个平级入口→4 个用户工作流，SKILL.md 路由优先规则，多意图处理，三语文档同步。 |

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

### Обновление надёжности — 15.11.2026

В `main` включены три пакета: [`31a2273`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/31a227378339bbf86c5f7a60f7c199cbdfc88b2c) — пути поиска, фильтрация по `v5_cluster` записи и регрессии; [`4ad61ab`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/4ad61abc9ac1788a086213e06db97df21d6b823d) — защита идентичности источников, преобразования, метаданных и проверки цитат; [`93da703`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/93da703db9a2207c57a8725916d46901d55b2017) — строгий предварительный просмотр исправлений активов, тесты и манифест изменений.

Версия остаётся **v5.4.1**; завершение v5.4.2 не заявляется. Реальные `assets/` не изменены: исправления 1 405 строк и 41 записи с повторяющимися ID проверены только в изолированной копии. Три неоднозначных ключа оставлены без изменений. Зафиксированы 16 + 41 + 14 успешных офлайн-регрессий и проверки существующих слоёв; это не GitHub CI и не проверка рабочего Zotero.

Следующий этап объединяет оставшиеся ошибки с подготовкой расширения до 30 000 работ: восстановление происхождения, проверка классификации и прав, проверяемая миграция, пересчёт статистики, семантические проверки цитат и защита записи. Расширение ещё не выполнено. Числа 16 722 / 2 118 / 679 ниже — исторические показатели сборки, а не вновь подтверждённые объёмы; 30 952 физических строки JSONL также не означают 30 952 работы. Совпадение слов даёт `candidate_unverified`, а не доказанную поддержку утверждения. См. [подробности исправлений](REMAINING_REPAIRS.md) и [границы предварительного просмотра](ASSET_REPAIR_PREVIEW.md).

### Кратко

**PhD Thesis Butler — это open-source skill для AI-ассистентов, таких как Codex, Hermes, Claude Code и Antigravity. Он помогает планировать структуру русской диссертации, проверять доказательную базу и редактировать академический русский текст.**

Это не генератор диссертаций. Skill помогает автору планировать, проверять, связывать утверждения с источниками и улучшать уже написанный русский академический текст.

### Главные возможности — 4 рабочих потока

| Поток | Когда использовать | Задействованные слои |
|:------|:-------------------|:----------------------|
| **① Русская академическая полировка** | Уже есть черновик на русском, нужно улучшить стиль, убрать машинный оттенок | 16 722 шаблона + retrieve_templates.py |
| **② Планирование структуры диссертации** | Есть тема/направление, нужна полная структура глав, методология, эксперименты | planning_layer + discipline assets |
| **③ Поиск литературы и анализ диссертаций** | Нужно найти диссертации по теме — **DisserCat**, **eLIBRARY**, **CyberLeninka**, **OpenAlex**; сравнить структуры, методы; подключить **личную Zotero-библиотеку** | research_layer + landscape/ |
| **④ Проверка цитирования** | Есть черновик главы, нужно проверить, какие утверждения требуют ссылок | evidence_layer + bind/detect/render scripts |

| Ключевая возможность | Описание |
|:---------------------|:----------|
| 🔍 **Поиск по российским базам** | **DisserCat**, **eLIBRARY / RINC**, **CyberLeninka**, **OpenAlex** — российские диссертации и журналы |
| 📚 **Интеграция с Zotero** | Чтение метаданных, тегов, коллекций, индексированного полного текста — **без ручного экспорта** |
| 🏗 **Сравнение структур диссертаций** | Автоматическая кластеризация 10–30 диссертаций по теме, сравнение структуры глав, методологий и типов валидации — отчёт из 12 разделов + рекомендуемый план |
| 📝 **16 722 русских академических шаблона** | Дистиллированы из 2 118 диссертаций (МГТУ/МГУ/СПбГУ), покрытие всех глав от ВВЕДЕНИЯ до ЗАКЛЮЧЕНИЯ |
| 🧩 **Полное планирование диссертации** | От направления исследования → полная структура: проектирование глав (6 кластеров × 5 паттернов), выбор методологии, дизайн экспериментов, функции каждой главы и её ввод/вывод — не просто план, а что писать в каждой главе, как её развивать и как главы связаны |
| ✅ **Проверка цитирования** | Пословный анализ утверждений, 12 ролей источников, маркировка кандидатов и пробелов; совпадения слов остаются partial/weak и candidate_unverified |

Это не генератор диссертаций. Skill помогает автору планировать, искать, проверять и улучшать уже написанный текст.

### Типовые задачи

```text
Помоги спланировать структуру диссертации по управлению транспортным средством.
Разложи мою идею на проблему, цель, задачи, метод и экспериментальную проверку.
Проверь, какие утверждения во второй главе требуют ссылок.
Отполируй введение на русском, сохранив мой исходный смысл.
```

### Основные слои — 4 рабочих потока

```text
 ─ Поток ①: Полировка и шаблоны
    assets/cluster/ + assets/global/     16 722 русских академических шаблона
 ─ Поток ②: Планирование диссертации
    planning_layer/                      структура глав, методология, эксперименты
    assets/references/disciplines/       дисциплинарные профили (внутренние)
 ─ Поток ③: Поиск литературы и анализ
    research_layer/                      стратегии поиска, нормализация метаданных
    └── landscape/                       сравнительный анализ диссертаций + Zotero (v5.4)
 ─ Поток ④: Проверка цитирования
    evidence_layer/                      привязка источников к главам, citation gaps
 ─ Будущее
    extension_layer/                     пользовательские расширения
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

### Reliability update — 2026-11-15

Three batches are merged into `main`: [`31a2273`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/31a227378339bbf86c5f7a60f7c199cbdfc88b2c) fixes retrieval paths, record-level cluster filtering and regression coverage; [`4ad61ab`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/4ad61abc9ac1788a086213e06db97df21d6b823d) adds source-mapping, conversion, metadata and citation safety; [`93da703`](https://github.com/Tanue-Hou/phd-thesis-butler/commit/93da703db9a2207c57a8725916d46901d55b2017) adds strict asset-repair preview tooling, tests and a change manifest.

The version remains **v5.4.1**; v5.4.2 is not declared complete. Actual `assets/` have **not** been migrated: repairs affecting 1,405 rows and 41 duplicate-ID records were verified only in an isolated copy; three ambiguous keys remain untouched. Recorded offline validation includes 16 + 41 + 14 regression tests and existing layer checks, not GitHub CI or live Zotero acceptance.

Remaining bugs are part of the next phase alongside preparation for 30,000 works: recover source provenance, verify classification and rights, review migration and external ID references, rebuild statistics, test semantic citation support, and harden output writes. Expansion has not run. The 16,722 / 2,118 / 679 figures below are historical build claims, not newly verified corpus sizes; 30,952 physical JSONL rows are not 30,952 papers either. Lexical matches remain `candidate_unverified`, not proven support. See [repair details](REMAINING_REPAIRS.md) and [preview boundaries](ASSET_REPAIR_PREVIEW.md).

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

### Key Highlights

| Feature | Description |
|:--------|:------------|
| 🔍 **Russian dissertation search** | Direct search across **DisserCat**, **eLIBRARY / RINC**, **CyberLeninka**, **OpenAlex** — Russian-language sources, not just international databases |
| 📚 **Zotero direct integration** | Read local Zotero metadata, tags, collections, indexed full text — search and feed directly into comparative analysis. **No manual export needed.** |
| 🏗 **Comparative landscape analysis** | Collect 10-30 similar-topic dissertations from public sources or Zotero, auto-cluster themes, compare chapter structures, methodology routes, and validation patterns — generates a 12-section structured report + recommended outline |
| 📝 **16,722 Russian sentence templates** | Distilled from 2,118 Russian dissertations (BMSTU/MSU/SPbSU), covers INTRO through CONCLUSION, JSONL retrieval with separate discipline profiles |
| 🧩 **Full thesis planning** | From research direction → complete thesis structure: whole-chapter design (6 clusters × 5 patterns), methodology route selection, experiment design, per-chapter writing function and input/output — not just an outline, but what each chapter should cover, how to develop it, and how chapters connect |
| ✅ **Citation gap detection** | Sentence-level claim analysis, 12 evidence roles, candidate and gap annotation; lexical matches remain partial/weak and candidate_unverified |

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
| v5.4.1 | **Workflow Router**: 6 flat entry points → 4 user workflows, routing priority in SKILL.md, multi-intent handling, trilingual README sync. |

### Academic Integrity

The skill assists planning, checking, literature organization, polishing, and revision. It does not create the user's research contribution. All facts, citations, experiments, and conclusions must be verified and owned by the author.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
