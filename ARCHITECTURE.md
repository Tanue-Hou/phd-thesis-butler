# PhD Thesis Butler v5.1 — 架构

## 整体结构

```
┌─────────────────────────────────────────────────────────┐
│                    PUBLIC (GitHub)                        │
│                                                          │
│  SKILL.md → 智能体行为定义                                │
│  assets/   → 16,722 个纯俄语模板                          │
│  planning_layer/ → 论文规划指南                            │
│  scripts/retrieve_templates.py → 三层检索                   │
└─────────────────────────────────────────────────────────┘
                          ↑ 部署
┌─────────────────────────────────────────────────────────┐
│                    PRIVATE (本地)                          │
│                                                          │
│  corpus_layer/     → Schema + 蒸馏管线                     │
│  scripts/build_*   → 语料库构建脚本                        │
│  scripts/extract_* → 结构/方法/逻辑/修辞 提取               │
│  tests/            → pytest 验证                          │
│  .phd_build/       → 构建输出（gitignore）                  │
└─────────────────────────────────────────────────────────┘
```

## 运行时架构（对用户可见）

### 三层检索

```
用户请求（自然语言）
       ↓
  Layer 1: DISCIPLINE（34个学科，~10K 模板）
       ↓ 不足3条则回退
  Layer 2: CLUSTER（TECH_LIFE / HUM_SOC / GLOBAL）
       ↓ 仍不足
  Layer 3: GLOBAL + data_fallback
       ↓
  返回 3-5 个最佳模板（Q2优先）
```

### 六大能力

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│句子模板检索│ │论文结构规划│ │写作指南  │ │修辞手法匹配│ │逻辑链分析  │ │自动润色  │
│retrieve  │ │planning │ │METHODO‑ │ │rhetorical│ │logic     │ │polish   │
│templates │ │layer    │ │LOGY GUIDE│ │moves     │ │chains    │ │         │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 数据资产

```
assets/
├── discipline/          ← 34 个 .jsonl（学科级）
├── cluster/             ← TECH_LIFE(5,942) + HUM_SOC(4,031)
│   ├── TECH_LIFE/
│   │   ├── master/     ← 全量语料
│   │   └── quality/    ← Q2 精选
│   └── HUM_SOC/
├── global/              ← GLOBAL(820) 跨学科
└── references/          ← 分类映射表

planning_layer/
├── clusters/            ← 6 个学科聚类
├── patterns/            ← 5 种结构模式（含 evidence_count）
├── templates/           ← 4 套写作模板
├── schemas/             ← 2 个 JSON Schema
└── *GUIDE.md            ← 4 本写作指南
```

## 语料蒸馏架构（私有）

```
Source (data/raw/ PDFs)
    ↓ Pass A: 确定性抽取（章节标题 + 页锚 + 图/表/公式）
    ↓ Pass B: 结构化理解（LLM 分行节分析）
    ↓ Pass C: 跨文档综合（去重 + 模式提取 + 质量评分）
    ↓
assets/ （公共蒸馏资产）
    ↓ extract_*.py
.phd_build/（构建验证输出）
```

### Schema 体系（5 个）

| Schema | 描述 |
|--------|------|
| `paper_record` | 单篇论文的学科、聚类、章节覆盖、质量分布 |
| `structure_record` | 论文的章节序列、模式类型（演绎/归纳/假说演绎） |
| `methodology_record` | 研究方法论路线、需要的模型/实验/数据集 |
| `logic_chain` | INTRO→CONCLUSION 完整逻辑链、各阶段模板数 |
| `rhetorical_move` | 每类修辞功能的模板数量、质量分布、常见错误 |

### 质量门控

```bash
# 验证命令（本地）
validate_skill_assets.py     # 资产完整性
validate_planning_assets.py  # 规划层完整性
validate_corpus_layer.py     # 蒸馏层完整性
pytest -q                    # 单元测试
```

## 技术栈

- **运行时**: Hermes Agent（Skill 系统）
- **数据格式**: JSONL（每行一个独立 JSON 对象）
- **检索**: 语义理解优先 + 关键词回退 + 三层逐级回退
- **Schema**: JSON Schema draft-07
- **构建**: Python 3.14+

## 版本演进

```
v2.0 ─→ v3.0 ─→ v3.3.5 ─→ v5.1
管线搭建    三层资产   数据清洗   语料蒸馏层
           planning  纯俄语     schema + 脚本
           mode                + evidence_count
```
