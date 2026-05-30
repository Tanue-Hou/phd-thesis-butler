# PhD Thesis Butler（博士论文管家 / Научный дворецкий）

> **俄语学术写作句式模板库** | Sentence bank for Russian academic writing | Банк шаблонов для академического письма на русском языке
>
> **v3.3.3** — 16,735 条纯正科研俄语模板，语义理解 + 三层回退检索 | 16,735 templates, semantic retrieval + 3-layer fallback | 16 735 шаблонов, семантический поиск

---

<div align="center">

[🇨🇳 中文](#中文) · [🇷🇺 Русский](#русский) · [🇬🇧 English](#english)

</div>

---

<a name="中文"></a>

# 🇨🇳 中文

## 一、项目定位

**PhD Thesis Butler**（博士论文管家）是一个面向 **俄语学术写作** 的句式模板资产库。加载本仓库的 `SKILL.md` 后，用户的 AI 智能体（Claude Code / Codex / Hermes 等）可以自动：

1. **推断学科大类** → 具体学科（TECH_LIFE / HUM_SOC / ART_SPORT + 具体方向）
2. **推断写作场景**（INTRO / SURVEY / MODEL / METHOD / EXPERIMENT / RESULT / DISCUSSION / CONCLUSION / FORMAL_DEFS / TRANSITION / ENGINEERING / AREF 模块）
3. **三层回退链检索**：DISCIPLINE → CLUSTER → GLOBAL，逐层回退直到命中 ≥K 条
4. **智能润色**：在严格约束下润色用户文本（不引入新事实、不夸大、不改变结论）
5. **输出结构化结果**：润色文本 + 变更摘要（≤3 行）+ 命中层级 + 命中质量

> 本项目提供**可迁移的修辞模式**——带 `[...]` 槽位的句式模板。**不复制或再分发**原论文受著作权保护的文本内容。

---

## 二、当前规模（v3.3.3）

| 指标 | 数值 |
|------|------|
| 纯俄语模板（去重后） | **16,735** |
| 来源文献 | **1,403 份独立文档** |
| ├ 论文正文（DIS） | 1,042 篇 |
| ├ 作者摘要（AREF） | 361 篇 |
| 来源高校 | 多所俄罗斯高校 |
| 质量分=2（优秀、即用型） | **~10,711** |
| 质量分=1（需领域适配） | **~4,780** |
| 质量分=0（仅参考） | **~1,300** |
| 语言纯度 | **100% 纯正科研俄语**（经 v3.2 语言清洗，删除 24 条中文 + 1,944 条英文模板） |

### 三级资产架构（Zero Overlap）

| 层级 | 名称 | 条数 | Q2 占比 | 说明 |
|------|------|------|---------|------|
| L0 | **GLOBAL** | 1,284 | 85.6% | 跨学科通用 Q2 模板（INTRO + TRANSITION + UTILS） |
| L1 | **TECH_LIFE** | 5,699 | 68.6% | 技术/生命/精密科学 |
| L1 | **HUM_SOC** | 4,035 | 61.6% | 人文/社会科学 |
| L1 | **ART_SPORT** | — | — | 艺术/体育（结构就绪，持续填充） |
| L2 | **DISCIPLINE** | ~10,045 | 65.5% | 34 个学科专用文件 |

**核心规则：一条模板只属于一个层级，跨层零重叠。**

---

## 三、v3.3 更新亮点

### Subtype 标准化
| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| 非标准 subtype 数量 | 6,866 个 | **1,662 个** | −75.8% |
| 非俄语 subtype（英/中混用） | 431 个 | **0 个** | 全部清除 |
| 标准分类体系 | — | 25 category, 1,448 个标准名 | 新增 |
| 语义映射表 | — | 14,384 行映射关系 | 新增 |

### 语义理解：从"关键词匹配"到"意图理解"

**旧策略（v3.2）：关键词精确匹配**
```
用户写 "Целью данной работы является..." 
→ 查找关键词 "цель работы" 
→ 匹配 INTRO / objective
→ 搜索 subtype="objective"
```

**新策略（v3.3.3）：语义理解优先**
```
用户写 "Целью данной работы является..." 
→ 理解意图：作者在阐述研究目标
→ 推断章节：INTRO / формулировка цели
→ 搜索：不要求精确 subtype 名，读取模板后理解匹配
```

### 实际对比示例

| 用户输入 | v3.2 策略（关键词） | v3.3 策略（语义理解） |
|---------|-------------------|-------------------|
| "Целью данной работы является разработка метода..." | ❌ 需要 "цель работы" 精确匹配 | ✅ 理解"формулировка цели" → INTRO |
| "Задача исследования заключается в..." | ❌ "задача исследования" 不完全匹配 | ✅ 同样理解为"формулировка цели" → INTRO |
| "Модель базируется на допущении, что..." | ❌ "допущение" 需要 ≥2 hits | ✅ 理解为"допущение модели" → MODEL |
| "Позволим себе заметить, что результаты..." | ❌ 无匹配关键词 | ✅ 理解为 "вежливое обсуждение" → DISCUSSION |
| "На основе вышеизложенного перейдём к..." | ❌ 需要 "перейдём к" 精确 | ✅ 理解为 переход → TRANSITION |

**关键改进：** 用户不需要说出精确的关键词。智能体通过理解段落的功能和意图来判断章节，然后到 assets/ 中找到最匹配的模板。

---

## 四、Skill 制作过程

Skill 制作分为四个阶段，通过多级门控确保质量。

### Phase 1：语料收集（Corpus Collection）

| 类别 | 论文（DIS） | 摘要（AREF） |
|------|-----------|-------------|
| 有效论文正文 | 1,042 |
| 有效摘要 | 361 |
| **独立文档合计** | **1,403** |

- 来源：2015–2025 年公开答辩的俄罗斯学位论文
- 扫描版 PDF（约 20%）已被排除出抽取管线

### Phase 2：模板抽取（LLM-Assisted Extraction）

每篇 PDF 经由结构化提示词处理：

1. **章节检测** — 判断文本所属论文部分
2. **修辞功能标注** — 按交际目的分类（动机、空白陈述、比较等）
3. **槽位提取** — 领域特定内容替换为 `[...]`，保留连接结构
4. **元数据标注** — `when_to_use`、`common_mistakes`、`strength`、`quality_score`

### Phase 3：闭环精炼（Closed-Loop Refinement）

```
抽取 → G1QA门控 → 聚合去重 → G2覆盖检查 → 缺口回填
         ↑      失败(≤3次)   ↓
         └────── 重试 ──────┘
```

| 门控 | 检查项 | 通过标准 |
|------|--------|---------|
| G1 抽取 | JSON 合法性、字段完整性 | 100% 可解析，≥98% 字段完整 |
| G2 QA | `___`=0, Q2≥20%, Q0≤5% | 全部满足 |
| G3 归并 | 每 category ≥3 条 | 23 个 DIS/AREF 类别全部满足 |
| G4 归层 | Zero Overlap | 跨层模板零重复 |
| G5 上线 | 规模 + Q2% 达标 | HUM_SOC+ART_SPORT ≥2,000 且 Q2≥25% |

**关键设计**：Gate 失败只返工当前批次，不影响已通过部分。

### Phase 4：归层分配（Layer Assignment）

按 `references/LAYER_ASSIGNMENT_RULES.md` 中的分布规则：

| 条件 | 归层 |
|------|------|
| 模板出现在 ≥2 个学科大类 | → **GLOBAL**（L0） |
| 仅出现在 1 个大类，但 ≥2 个学科 | → **CLUSTER**（L1） |
| 集中在 1 个学科 | → **DISCIPLINE**（L2） |
| quality=0 的模板不参与自动归层 | → 仅做 review |

---

## 五、使用方式（无需外部 API）

### Claude Code

```bash
mkdir -p ~/.claude/skills/
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```

在 `CLAUDE.md` 中引用：
```markdown
Load ~/.claude/skills/phd-thesis-butler/SKILL.md.
When user provides Russian text, infer section + discipline, retrieve templates from assets/, then polish and output.
```

### Codex CLI

```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

配置智能体加载 `SKILL.md` 并允许读取 `assets/` 目录。

### Hermes

```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
# 加载：
/skill phd-thesis-butler
```

### 检索策略（三层回退链）

```
1. 先在 DISCIPLINE（L2）搜索：category + subtype 匹配，优先 Q2
2. 若命中 < K 条（K=3），回退到 CLUSTER（L1）对应大类
3. 若仍不足，回退到 GLOBAL（L0）
4. 输出时标注 hit_layer、hit_quality、hit_count
```

润色输出格式：

```
【润色后文本】
{template 填入用户内容后的完整句子}

---
摘要：修改了 X 处措辞，统一了术语表述
命中层级：CLUSTER (TECH_LIFE)
命中质量：Q2
```

---

## 六、快速验证

克隆仓库后，执行以下命令确认数据完整性：

```bash
# 1. 验证模板总数
echo "DIS: $(wc -l < data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl)"
echo "AREF: $(wc -l < data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl)"
echo "UTILS: $(wc -l < data/curated/master/MASTER_UTILS.jsonl)"

# 2. 验证三层资产结构
ls assets/global/master/MASTER.jsonl           # L0 GLOBAL
ls assets/cluster/TECH_LIFE/master/MASTER.jsonl # L1 TECH_LIFE
ls assets/cluster/HUM_SOC/master/MASTER.jsonl   # L1 HUM_SOC

# 3. 验证 subtype 标准化映射表
wc -l assets/references/subtype_mapping_v3.3.json

# 4. 查看构建信息
cat BUILD_INFO.json
```

预期输出（v3.3.3）：
```
DIS: 9863
AREF: 6568
UTILS: 304
```

---

## 七、文件结构速查

```
📂 仓库根目录
├── SKILL.md                          ← 智能体加载入口（角色定义、搜索规则、输出规范）
├── README.md                         ← 本文档
├── CHANGELOG.md                      ← 版本迭代记录
│
├── data/curated/
│   ├── master/
│   │   ├── MASTER_SENTENCEBANK_DIS.jsonl    (9,863 条)  ← 论文模板主库
│   │   ├── MASTER_SENTENCEBANK_AREF.jsonl   (6,568 条)  ← 摘要模板主库
│   │   └── MASTER_UTILS.jsonl               (304 条)    ← 功能短语库
│   └── quality/
│       ├── QUALITY2_SELECTION_DIS.jsonl     (8,383 条)  ← DIS Q2 精选
│       ├── QUALITY2_SELECTION_AREF.jsonl    (2,228 条)  ← AREF Q2 精选
│       └── QUALITY2_UTILS.jsonl                         ← UTILS Q2 精选
│
├── assets/
│   ├── global/master/MASTER.jsonl           (185 条)    ← L0 GLOBAL
│   ├── cluster/TECH_LIFE/master/MASTER.jsonl (5,699 条) ← L1 TECH_LIFE
│   ├── cluster/HUM_SOC/master/MASTER.jsonl  (4,035 条)  ← L1 HUM_SOC
│   └── discipline/                         (34 个文件)  ← L2 各学科
│
├── references/
│   ├── LAYER_ASSIGNMENT_RULES.md           ← 归层分配规则
│   ├── FULL_CLASSIFICATION.yaml            ← 完整分类体系
│   ├── INDEX_GUIDE.md                      ← 使用索引指南
│   └── pipeline-extraction.md              ← Phase 2 管线说明
│
├── scripts/
│   ├── retrieve_templates.py              ← 确定性三层检索脚本
│   └── validate_skill_assets.py           ← 全量验证脚本
├── evals/
│   └── evals.json                         ← 最小测试集（10 cases）
├── schemas/
│   └── sentencebank_entry.schema.v2_1.json ← JSON Schema
│
├── sub_skills/                            ← 13 个子 skill（按需加载）
    ├── dis_intro/SKILL.md
    ├── dis_survey/SKILL.md
    ├── dis_method/SKILL.md
    └── ...
```

---

## 八、分类体系

### DIS 通道（11 类）

| 类别 | 子类数 | 说明 |
|------|--------|------|
| INTRO | 8 | 引言与背景 |
| SURVEY | 7 | 文献综述 |
| MODEL | 10 | 理论模型构建 |
| METHOD | 8 | 方法与算法 |
| EXPERIMENT | 8 | 实验与验证 |
| RESULT | 6 | 结果汇报 |
| DISCUSSION | 6 | 讨论与分析 |
| CONCLUSION | 5 | 结论 |
| TRANSITION | 4 | 过渡承接 |
| FORMAL_DEFS | 4 | 形式化定义 |
| ENGINEERING | 5 | 工程实现 |

### AREF 通道（14 类）

АКТУАЛЬНОСТЬ / НОВИЗНА / ЦЕЛЬ_ЗАДАЧИ / ОБЪЕКТ_ПРЕДМЕТ / МЕТОДЫ / ПОЛОЖЕНИЯ / ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ / ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ / АПРОБАЦИЯ / ВЫВОДЫ / ПЕРСПЕКТИВЫ / ДОСТОВЕРНОСТЬ / СТЕПЕНЬ_РАЗРАБОТАННОСТИ / СТРУКТУРА

### UTILS 通道（3 类）

| 种类 | 说明 | 示例 |
|------|------|------|
| CONNECTIVE | 过渡与结构短语 | "Однако...", "С одной стороны..." |
| CONSERVATIVE | 保守与不确定性措辞 | "Предположительно...", "Вероятно..." |
| NUMERIC | 数字汇报模式 | "увеличение на X%", "ошибка составляет Y" |

---

## 九、数据格式（JSONL v2.1）

```json
{
  "paper_id": "1090",
  "source": "DIS",
  "record_type": "TEMPLATE",
  "category": "INTRO",
  "subtype": "objective",
  "template": "Целью диссертационной работы является разработка и исследование [объект] для повышения [эффективность].",
  "slots": ["объект", "эффективность"],
  "when_to_use": "Во введении при формулировании цели.",
  "common_mistakes": ["Цель слишком общая", "Не указан ожидаемый результат"],
  "strength": "neutral",
  "quality_score": 2,
  "schema_version": "2.1"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `paper_id` | string | 是 | 来源论文 ID |
| `source` | string | 是 | "DIS"(论文) / "AREF"(摘要) |
| `record_type` | string | 是 | "TEMPLATE"(模板) / "UTIL"(功能短语) |
| `category` | string | 条件 | DIS/AREF 类别（TEMPLATE 必填） |
| `subtype` | string | 条件 | 修辞功能子类 |
| `kind` | string | 条件 | UTIL 种类（CONNECTIVE/CONSERVATIVE/NUMERIC） |
| `template` | string | 是 | 带 `[...]` 槽位的句式模式 |
| `slots` | array | 否 | 槽位说明 |
| `when_to_use` | string | 否 | 使用时机（俄语） |
| `common_mistakes` | array | 否 | 常见错误（俄语） |
| `strength` | string | 否 | "strong" / "conservative" / "neutral" |
| `quality_score` | int | 是 | 0(领域绑定) / 1(可适配) / 2(高可迁移) |
| `schema_version` | string | 是 | 固定为 "2.1" |

---

## 十、质量评分标准

| 分数 | 标签 | 含义 | 选用策略 |
|------|------|------|---------|
| **2** | 优秀 | 领域无关修辞模式，替换 `[...]` 即可使用 | **优先选用** |
| **1** | 可用 | 需领域适配，有一定领域框架痕迹 | Q2 不足时回退使用 |
| **0** | 参考 | 领域绑定示例，需大量人工调整 | 仅作灵感参考 |

---

## 十一、免责声明

**本仓库提供句式模板与润色规则参考，不构成学术完成的保证。**

使用者需自行承担以下责任：

1. **事实核查** — 所有技术声明、数据和参考文献必须由作者验证
2. **引用合规** — 正确标注来源是作者的责任
3. **查重检测** — 所有生成的文本必须进行原创性检查
4. **学术诚信** — 遵守所在机构和出版方的指导方针
5. **领域适配** — 模板必须适配到具体研究领域，盲目复制可能产生不准确或误导性陈述

**数据来源**：所有模板从公开答辩的学位论文中提取，项目仅存储修辞模式（带槽位的连接结构），不包含原论文受著作权保护的文本。不复制任何单篇论文的完整句子、段落或研究发现。

**责任限制**：项目维护者和贡献者按"现状"提供本材料，不作任何明示或暗示的保证。在任何情况下，维护者均不对因使用本软件或数据而产生的任何索赔、损害或其他法律责任负责。

---

## 十二、开源声明

本仓库以 **CC BY 4.0**（知识共享署名 4.0 国际许可）发布。

您可以自由地：
- **共享** — 在任何媒介以任何格式复制和再分发本材料
- **改编** — 基于本材料进行修改、转换或创作

须遵守以下条件：
- **署名** — 必须给出适当的署名，提供指向本许可的链接，并标明是否做了修改

**推荐引用格式**：
```bibtex
@misc{phd-thesis-butler,
  author = {Tanue Hou},
  title = {PhD Thesis Butler: A Sentence Template Bank for Russian Academic Writing},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Tanue-Hou/phd-thesis-butler}
}
```

---

<a name="русский"></a>

# 🇷🇺 Русский

## 1. Назначение

**PhD Thesis Butler** — загружаемый банк шаблонов для **академического письма на русском языке**. После загрузки `SKILL.md` агент пользователя (Claude Code / Codex / Hermes и т.п.) автоматически:

1. **Определяет кластер → дисциплину** (TECH_LIFE / HUM_SOC / ART_SPORT + конкретная дисциплина)
2. **Определяет раздел текста** (INTRO / SURVEY / MODEL / METHOD / EXPERIMENT / RESULT / DISCUSSION / CONCLUSION / FORMAL_DEFS / TRANSITION / ENGINEERING / модули AREF)
3. **Извлекает шаблоны по трёхуровневой цепочке отката** (DISCIPLINE → CLUSTER → GLOBAL)
4. **Выполняет правку** без добавления новых фактов и без завышения выводов
5. **Возвращает**: отредактированный текст + краткое резюме (≤3 строки) + уровень попадания

> Проект предоставляет **переносимые риторические паттерны** — шаблонные предложения со слотами `[...]`. Он **не копирует и не распространяет** исходный текст диссертаций.

---

## 2. Масштаб (v3.3.3)

| Показатель | Значение |
|-----------|----------|
| Чисто русские шаблоны (после дедупликации) | **16 735** |
| Корпус | **1 403 независимых документа** |
| ├ Диссертации (DIS) | 1 042 |
| └ Авторефераты (AREF) | 361 |
| Университеты | Несколько российских вузов |
| Качество=2 (отличные) | **~10 711** |
| Качество=1 (требуют адаптации) | **~4 780** |
| Качество=0 (справочные) | **~1 300** |

### Трёхуровневая архитектура (Zero Overlap)

| Уровень | Название | Записей | Q2 |
|---------|----------|---------|-----|
| L0 | **GLOBAL** | 1 284 | 85,6% |
| L1 | **TECH_LIFE** | 5 699 | 68,6% |
| L1 | **HUM_SOC** | 4 035 | 61,6% |
| L1 | **ART_SPORT** | — | пополняется |
| L2 | **DISCIPLINE** (34 дисциплины) | ~10 045 | 65,5% |

**Жёсткое правило:** один шаблон принадлежит ровно одному слою (zero overlap).

---

### Что нового в v3.3

**Стандартизация subtype:** 6 866 → **1 662** (−75,8%), 431 не-русских subtype удалено
**Семантическое понимание:** вместо поиска по ключевым словам — понимание намерения пользователя

Пример:
```
Пользователь: "Целью данной работы является разработка метода..."
v3.2: ищет "цель работы" (ключевое слово) → может не найти
v3.3: понимает "формулировка цели" → INTRO → находит шаблон
```

**Файлы:**
- `assets/references/standard_taxonomy_v3.3.json` — 25 category, 1 448 стандартных subtype
- `assets/references/subtype_mapping_v3.3.json` — 14 384 строки отображения старых→новых имён

---

## 3. Процесс создания

Создание навыка проходит четыре фазы с многоуровневыми gate-проверками.

### Фаза 1: Сбор корпуса
- 1 042 диссертации + 361 автореферат из нескольких российских университетов
- Отсканированные PDF (~20%) исключены из пайплайна

### Фаза 2: Извлечение шаблонов
Каждый PDF обрабатывается через структурированные промпты:
1. **Детекция раздела** — INTRO / SURVEY / MODEL / METHOD / EXPERIMENT / RESULT / DISCUSSION / CONCLUSION / FORMAL_DEFS / TRANSITION / ENGINEERING / AREF
2. **Определение риторической функции** — category + subtype
3. **Замена содержимого на слоты** — `[...]`
4. **Аннотация метаданных** — `when_to_use`, `common_mistakes`, `strength`, `quality_score`

### Фаза 3: Итеративное улучшение (G1–G5)
```
Извлечение → G1 QA → Агрегация/дедупликация → G2 Покрытие → G3 Слияние → G4 Распределение → G5 Запуск
```

| Gate | Проверка | Критерий |
|------|----------|----------|
| G1 | JSON + поля | 100% парсинг, ≥98% заполнение |
| G2 | Качество | Q2≥20%, Q0≤5%, `___`=0 |
| G3 | Слияние | ≥3 записи на категорию |
| G4 | Zero Overlap | Нет повторов между слоями |
| G5 | Запуск | ≥2000 записей, Q2≥25% |

### Фаза 4: Распределение по слоям

| Условие | Слой |
|---------|------|
| Шаблон встречается в ≥2 кластеров | → **GLOBAL** (L0) |
| В 1 кластере, но ≥2 дисциплин | → **CLUSTER** (L1) |
| Сконцентрирован в 1 дисциплине | → **DISCIPLINE** (L2) |

---

## 4. Использование (без внешних API)

### Claude Code
```bash
mkdir -p ~/.claude/skills/
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```

### Codex CLI
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

### Hermes
```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
/skill phd-thesis-butler
```

### Стратегия поиска (цепочка отката)
1. **DISCIPLINE (L2)** — поиск по category + subtype, приоритет Q2
2. **CLUSTER (L1)** — если < K записей (K=3), откат к соответствующему кластеру
3. **GLOBAL (L0)** — если всё ещё недостаточно

**Формат вывода:**
```
【Отредактированный текст】
{шаблон с заполненными слотами}

---
Резюме: исправлено X формулировок, унифицирована терминология
Уровень: CLUSTER (TECH_LIFE)
Качество: Q2
```

---

## 5. Формат данных (JSONL v2.1)

```json
{
  "paper_id": "1090",
  "source": "DIS",
  "record_type": "TEMPLATE",
  "category": "INTRO",
  "subtype": "objective",
  "template": "Целью диссертационной работы является разработка и исследование [объект] для повышения [эффективность].",
  "slots": ["объект", "эффективность"],
  "when_to_use": "Во введении при формулировании цели.",
  "common_mistakes": ["Цель слишком общая", "Не указан ожидаемый результат"],
  "strength": "neutral",
  "quality_score": 2,
  "schema_version": "2.1"
}
```

---

---

## 6. Быстрая проверка

После клонирования репозитория выполните:

```bash
# 1. Количество шаблонов
echo "DIS: $(wc -l < data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl)"
echo "AREF: $(wc -l < data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl)"
echo "UTILS: $(wc -l < data/curated/master/MASTER_UTILS.jsonl)"

# 2. Структура активов
ls assets/global/master/MASTER.jsonl
ls assets/cluster/TECH_LIFE/master/MASTER.jsonl
ls assets/cluster/HUM_SOC/master/MASTER.jsonl

# 3. Карта subtype
wc -l assets/references/subtype_mapping_v3.3.json

# 4. Информация о сборке
cat BUILD_INFO.json
```

Ожидаемый результат (v3.3.3):
```
DIS: 9863
AREF: 6568
UTILS: 304
```

---

## 6. Дисклеймер

Репозиторий предоставляет **только шаблонные фразы и рекомендации по стилю**.

**Пользователь несёт полную ответственность за:**
- проверку фактической точности всех технических утверждений
- соблюдение правил цитирования и требований вуза/журнала
- проверку на плагиат и обеспечение оригинальности текста
- адаптацию шаблонов к своей предметной области
- соблюдение норм академической этики

**Происхождение данных:** все шаблоны извлечены из общедоступных диссертаций. Проект хранит только риторические паттерны, не защищённый авторским правом исходный текст.

**Ограничение ответственности:** материалы предоставляются «как есть». В любой юрисдикции ответственность за последствия использования лежит на пользователе.

---

## 8. Лицензия

**CC BY 4.0** — Creative Commons Attribution 4.0 International

Разрешается:
- **Делиться** — копировать и распространять материал
- **Адаптировать** — изменять, преобразовывать и дополнять

При условии:
- **Атрибуция** — указание автора и ссылки на лицензию

**Рекомендуемая ссылка:**
```bibtex
@misc{phd-thesis-butler,
  author = {Tanue Hou},
  title = {PhD Thesis Butler: A Sentence Template Bank for Russian Academic Writing},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Tanue-Hou/phd-thesis-butler}
}
```

---

<a name="english"></a>

# 🇬🇧 English

## 1. What This Skill Does

**PhD Thesis Butler** is a loadable **sentence template bank** for **Russian academic writing**. After loading `SKILL.md`, your agent (Claude Code / Codex / Hermes) automatically:

1. **Infers cluster → discipline** (TECH_LIFE / HUM_SOC / ART_SPORT + specific subject)
2. **Infers writing scene** (INTRO / SURVEY / MODEL / METHOD / EXPERIMENT / RESULT / DISCUSSION / CONCLUSION / FORMAL_DEFS / TRANSITION / ENGINEERING / AREF modules)
3. **Retrieves templates via 3-layer fallback**: DISCIPLINE → CLUSTER → GLOBAL, until ≥K hits
4. **Polishes user text** under strict constraints (no new facts, no overclaiming, no changed conclusions)
5. **Outputs structured result**: polished text + change summary (≤3 lines) + hit layer + hit quality

> This repository provides **portable rhetorical patterns** — sentence templates with `[...]` slot variables. It does **not** copy or redistribute original dissertation text.

---

## 2. Current Scale (v3.3.3)

| Metric | Value |
|--------|-------|
| Pure Russian templates (deduplicated) | **16,735** |
| Source documents | **1,403 unique** |
| ├ DIS (dissertations) | 1,042 |
| └ AREF (abstracts) | 361 |
| Source universities | Multiple Russian universities |
| Quality=2 (excellent, ready-to-use) | **~10,711** |
| Quality=1 (needs domain adaptation) | **~4,780** |
| Quality=0 (informational only) | **~1,300** |
| Language purity | **100% pure Russian** (after v3.2 cleanup: −24 CN, −1,944 EN) |

### 3-Layer Asset Architecture (Zero Overlap)

| Layer | Name | Entries | Q2 Ratio |
|-------|------|---------|----------|
| L0 | **GLOBAL** | 1,284 | 85.6% |
| L1 | **TECH_LIFE** | 5,699 | 68.6% |
| L1 | **HUM_SOC** | 4,035 | 61.6% |
| L1 | **ART_SPORT** | — | being populated |
| L2 | **DISCIPLINE** (34 subjects) | ~10,045 | 65.5% |

**Cardinal rule:** One template belongs to exactly one layer. Zero cross-layer overlap.

---

### v3.3 Highlights

| Optimization | Before | After |
|-------------|--------|-------|
| Subtype standardization | 6,866 non-standard | **1,662 standardized** (−75.8%) |
| Non-Russian subtypes | 431 EN/CN mix | **0** |
| Standard taxonomy | — | 25 categories, 1,448 standard names |
| Semantic mapping table | — | 14,384 mapping entries |

**From keyword matching to intent understanding:**

```
Old (v3.2): "Целью работы является..." → search keyword "цель работы" → exact match
New (v3.3.3): "Целью работы является..." → understand intent "формулировка цели" → INTRO
```

**New files:** `assets/references/standard_taxonomy_v3.3.json`, `assets/references/subtype_mapping_v3.3.json`

---

## 3. Asset-Building Pipeline

The skill is built through a four-phase gated pipeline.

### Phase 1: Corpus Collection

| Category | DIS (dissertations) | AREF (abstracts) |
|----------|---------------------|------------------|
| Valid dissertations | 1,042 |
| Valid abstracts | 361 |
| **Total unique documents** | **1,403** |

- Source: publicly defended Russian dissertations (2015–2025)
- Scanned PDFs (~20%) excluded from the extraction pipeline

### Phase 2: Template Extraction

Each PDF is processed with structured prompts:
1. **Section detection** — identify thesis part (INTRO / SURVEY / MODEL / etc.)
2. **Rhetorical function labeling** — categorize by communicative purpose
3. **Slot extraction** — replace domain content with `[...]`
4. **Metadata annotation** — `when_to_use`, `common_mistakes`, `strength`, `quality_score`

### Phase 3: Closed-Loop Refinement (G1–G5 Gates)

```
Extract → G1 QA Gate → Aggregate/Dedup → G2 Coverage → G3 Merge → G4 Layer Assign → G5 Launch
             ↑            Fail (≤3x)       ↓
             └────────── Retry ───────────┘
```

| Gate | Check | Pass Criteria |
|------|-------|---------------|
| G1 | JSON validity + field completeness | 100% parseable, ≥98% field complete |
| G2 | Quality distribution | Q2≥20%, Q0≤5%, `___`=0 |
| G3 | Category merge | ≥3 entries per category |
| G4 | Zero overlap | No cross-layer duplication |
| G5 | Release readiness | ≥2,000 entries per cluster, Q2≥25% |

**Key design:** Gate failure only returns the current batch, not already-passed data.

### Phase 4: Layer Assignment

Per `references/LAYER_ASSIGNMENT_RULES.md`:

| Condition | Assignment |
|-----------|------------|
| Template appears in ≥2 clusters | → **GLOBAL** (L0) |
| In 1 cluster but ≥2 disciplines | → **CLUSTER** (L1) |
| Concentrated in 1 discipline | → **DISCIPLINE** (L2) |
| quality=0 templates | → Review only, not auto-assigned |

---

## 4. How to Use (No External API Required)

### Options

**Claude Code**:
```bash
mkdir -p ~/.claude/skills/
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```
Then reference in `CLAUDE.md`.

**Codex CLI**:
```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```
Point agent to `SKILL.md` and allow reading `assets/`.

**Hermes**:
```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
/skill phd-thesis-butler
```

### Retrieval Policy (3-Layer Fallback)

```
1. DISCIPLINE (L2): search by category + subtype, prioritize Q2
2. If <K hits (K=3), fall back to CLUSTER (L1) for the matched cluster
3. If still insufficient, fall back to GLOBAL (L0)
```

**Output format**:
```
【Polished Text】
{template filled with user content}

---
Summary: revised X phrasings, unified terminology
Hit layer: CLUSTER (TECH_LIFE)
Hit quality: Q2
```

---

## 5. Classification System

### DIS Channel (11 categories)

INTRO / SURVEY / MODEL / METHOD / EXPERIMENT / RESULT / DISCUSSION / CONCLUSION / TRANSITION / FORMAL_DEFS / ENGINEERING

### AREF Channel (14 categories)

АКТУАЛЬНОСТЬ / НОВИЗНА / ЦЕЛЬ_ЗАДАЧИ / ОБЪЕКТ_ПРЕДМЕТ / МЕТОДЫ / ПОЛОЖЕНИЯ / ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ / ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ / АПРОБАЦИЯ / ВЫВОДЫ / ПЕРСПЕКТИВЫ / ДОСТОВЕРНОСТЬ / СТЕПЕНЬ_РАЗРАБОТАННОСТИ / СТРУКТУРА

### UTILS Channel (3 kinds)

CONNECTIVE / CONSERVATIVE / NUMERIC

---

## 6. Data Format (JSONL v2.1)

```json
{
  "paper_id": "1090",
  "source": "DIS",
  "record_type": "TEMPLATE",
  "category": "INTRO",
  "subtype": "objective",
  "template": "Целью диссертационной работы является разработка и исследование [объект] для повышения [эффективность].",
  "slots": ["объект", "эффективность"],
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
| `paper_id` | string | yes | Source dissertation ID |
| `source` | string | yes | "DIS" or "AREF" |
| `record_type` | string | yes | "TEMPLATE" or "UTIL" |
| `category` | string | conditional | DIS/AREF category (required for TEMPLATE) |
| `subtype` | string | conditional | Rhetorical function subtype |
| `kind` | string | conditional | UTIL kind (CONNECTIVE/CONSERVATIVE/NUMERIC) |
| `template` | string | yes | Sentence pattern with `[...]` slots |
| `slots` | array | no | Slot name descriptions |
| `when_to_use` | string | no | Usage guidance (Russian) |
| `common_mistakes` | array | no | Common writing errors (Russian) |
| `strength` | string | no | "strong" / "conservative" / "neutral" |
| `quality_score` | int | yes | 0(domain-tied) / 1(adaptable) / 2(portable) |
| `schema_version` | string | yes | Always "2.1" |

---

## 8. Quality Scoring

| Score | Label | Meaning | Selection Strategy |
|-------|-------|---------|-------------------|
| **2** | Excellent | Field-independent, replace `[...]` and use | **Always prefer first** |
| **1** | Good | Needs domain adaptation | Use when no Q2 match |
| **0** | Informative | Domain-tied example, heavy manual review | Inspiration only |

---

---

## 7. Quick Verify

After cloning the repository, run:

```bash
# 1. Template counts
echo "DIS: $(wc -l < data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl)"
echo "AREF: $(wc -l < data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl)"
echo "UTILS: $(wc -l < data/curated/master/MASTER_UTILS.jsonl)"

# 2. Asset structure
ls assets/global/master/MASTER.jsonl
ls assets/cluster/TECH_LIFE/master/MASTER.jsonl
ls assets/cluster/HUM_SOC/master/MASTER.jsonl

# 3. Subtype mapping
wc -l assets/references/subtype_mapping_v3.3.json

# 4. Build info
cat BUILD_INFO.json
```

Expected output (v3.3.3):
```
DIS: 9863
AREF: 6568
UTILS: 304
```

---

## 8. Disclaimer

**This repository provides sentence templates and polishing guidance only.**

Users bear sole responsibility for:
- **Factual verification** — all technical claims, data, and references must be verified
- **Citation compliance** — proper attribution of sources
- **Plagiarism checking** — all generated text must be reviewed for originality
- **Academic integrity** — compliance with institution and publisher guidelines
- **Domain adaptation** — templates must be adapted; blind copying may produce inaccurate statements

**Data origin:** All templates were extracted from publicly defended dissertations in open-access repositories. The project stores only rhetorical patterns (connective structures with slot variables), not copyrighted original text. No full sentences, paragraphs, or original findings from any single dissertation are reproduced.

**Limitation of liability:** The material is provided "as is" without warranty of any kind. In no event shall the maintainers be liable for any claim, damages, or other liability arising from use.

---

## 10. License & Citation

**CC BY 4.0** — Creative Commons Attribution 4.0 International

You are free to **Share** (copy and redistribute) and **Adapt** (remix, transform, build upon) for any purpose, even commercially, **provided you give appropriate credit**.

**Recommended citation:**
```bibtex
@misc{phd-thesis-butler,
  author = {Tanue Hou},
  title = {PhD Thesis Butler: A Sentence Template Bank for Russian Academic Writing},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Tanue-Hou/phd-thesis-butler}
}
```

---

<div align="center">

[🇨🇳 中文](#中文) · [🇷🇺 Русский](#русский) · [🇬🇧 English](#english)

</div>
