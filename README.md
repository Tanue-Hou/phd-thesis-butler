# PhD Thesis Butler — 博士论文管家

俄语学术写作句式库与抽取管线。从 **300+ 篇俄语博士论文**（диссертация + автореферат）中抽取全量句式与用法，生成可检索、可聚合的学术写作 Sentencebank。

⚠️ **重要声明：本工具仅用于学术写作润色与句式参考，严禁用于自动生成学术论文。**
⚠️ **使用者需自行承担所有 AI 辅助写作带来的学术伦理与著作权风险。**

---

## 数据规模

| 数据集 | 条目数 | 说明 |
|--------|--------|------|
| MASTER_SENTENCEBANK_DIS.jsonl | 5,621 | 论文本体句式（11 category） |
| MASTER_SENTENCEBANK_AREF.jsonl | 3,573 | Автореферат 句式（14 模块） |
| MASTER_UTILS.jsonl | 408 | 连接词/保守措辞/数字汇报 |
| **合计** | **9,602** | |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **v2.1** | 2026-05 | 最终版：9,602条，PII脱敏通过，JSON schema严格化，qa_check参数修复 |
| v2.0 | 2026-05 | 引入 record_type(TEMPLATE/UTIL)，Router输出JSON契约，三档覆盖指标 |
| v1.0 | 2026-05 | 初始方案：13个子skill，按category拆分的Lite架构 |
| Pilot | 2026-05 | 9篇试点验证pipeline，确定分类体系与质量阈值 |

### v2.1 关键变更

- 字段命名清洗：消除 subrype/subtitle/common_mstake 等拼写错误
- quality_score 统一：int 0/1/2，清除 float/str 混用
- PII 脱敏：替换真实姓名、地址、机构名为占位符
- 移除中文模板：删除 607 条 Chinese-language 条目
- qa_check.py：--max-words 参数真正生效，overall_pass 包含所有检查
- JSON Schema：UTIL 必填字段补齐（kind/subtype/when_to_use/common_mistakes）
- FULL_CLASSIFICATION.yaml：新增 allowed_source / allowed_record_types 校验字段
- Router 输出契约：添加完整 plan JSON 示例

---

## 目录结构

```
phd-thesis-butler/
├── SKILL.md                         ← 主 skill：路由说明 + Quickstart
├── README.md                        ← 本文件
├── prompts/                         ← 可执行提示词（.prompt.txt）
│   ├── router.prompt.txt            ← 主路由器（输出执行计划 JSON）
│   ├── gm.prompt.txt                ← 总经理派工
│   ├── dis_full.prompt.txt          ← DIS 句式抽取（11 category）
│   └── aref_full.prompt.txt         ← AREF 句式抽取（14 category）
├── references/
│   ├── FULL_CLASSIFICATION.yaml     ← 唯一枚举来源，含校验约束
│   ├── CROSS_CATEGORY_MAP.md        ← 写作场景→子 skill 映射
│   └── INDEX_GUIDE.md               ← 使用说明
├── schemas/
│   └── sentencebank_entry.schema.v2_1.json  ← JSONL schema
├── scripts/                          ← 可执行工具
│   ├── aggregate.py                  ← 聚合/去重/归并/过滤/分库
│   ├── qa_check.py                   ← QA 抽检（槽位/有效性/长度/专名等）
│   ├── coverage_check.py             ← 三档覆盖检测 + gap_list
│   ├── generate_top50.py             ← 精选 TOP50 生成
│   ├── smoke_test.sh                 ← 全链路自检
│   ├── batch_runner.sh               ← batch 运行
│   └── retry_handler.sh              ← 重试/死信处理
├── sub_skills/                       ← 13 个子 skill（按需加载）
│   ├── dis_intro / dis_survey / dis_model / dis_method /
│   ├── dis_experiment / dis_result / dis_discussion /
│   ├── dis_conclusion / dis_transition / dis_formal_defs /
│   ├── dis_engineering / aref_core / utils_core
└── data/curated/
    ├── master/                       ← 主句式库（JSONL）
    ├── quality/                      ← 精选 + TOP50
    └── gaps/                         ← 覆盖缺口
```

---

## 在 Claude / Codex / Hermes 中使用

### 通用加载方式（三平台均支持）

```bash
# 1. 加载主 skill（路由说明 + 索引）
skill_view("phd-thesis-butler")

# 2. 按写作场景加载对应子 skill
#    写引言 → 加载 INTRO
skill_view("phd-thesis-butler/sub_skills/dis_intro")

#    写建模 → 加载 MODEL
skill_view("phd-thesis-butler/sub_skills/dis_model")

#    写结论 → 加载 CONCLUSION
skill_view("phd-thesis-butler/sub_skills/dis_conclusion")

# 3. 检索高质量模板
grep '"quality_score":2' data/curated/quality/QUALITY2_SELECTION_DIS.jsonl | grep '"subtype":"motivation"' | head -5
```

### Claude Code

```bash
# 安装 skill
claude skills install phd-thesis-butler

# 加载子 skill
/skill phd-thesis-butler/sub_skills/dis_intro

# 检索模板
grep "motivation" ~/.claude/skills/phd-thesis-butler/data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl | head -10
```

### Codex CLI

```bash
# 加载 skill
@skill phd-thesis-butler/sub_skills/dis_intro

# 查询用法
@search "numeric reporting templates" in phd-thesis-butler
```

### Hermes Agent

```bash
# 安装 skill
hermes skills install phd-thesis-butler

# 加载子 skill
/skill phd-thesis-butler/sub_skills/dis_intro

# 按需检索（不占上下文）
grep '"subtype":"gap"' ~/.hermes/skills/phd-thesis-butler/data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl | head -5
```

### 快速查询示例

```python
# 在任意平台用 Python 按需检索
import json, os

SKILL = os.path.expanduser("~/.hermes/skills/phd-thesis-butler")
with open(f"{SKILL}/data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl") as f:
    for line in f:
        e = json.loads(line)
        if e.get("category") == "INTRO" and e.get("quality_score") == 2:
            print(e["template"])
```

---

## 约束

- **模型强制**：xiaomi mimo v2.5（抽取管线）
- **所有 category/subtype 必须来自** `FULL_CLASSIFICATION.yaml`
- **输出 schema 必须遵守** `sentencebank_entry.schema.v2_1.json`
- **schema_version 必须为 "2.1"**

---

## 输出样例

### TEMPLATE 行（DIS-INTRO）

```jsonl
{"paper_id":"001","source":"DIS","record_type":"TEMPLATE","category":"INTRO","subtype":"motivation","template":"В последние годы ___ привлекает все большее внимание в области ___.","slots":["объект/тема","область/контекст"],"when_to_use":"引言段首：交代研究方向关注度并限定领域","common_mistakes":["空泛不落地","未限定范围导致过度泛化"],"strength":"neutral","quality_score":2,"schema_version":"2.1"}
```

### UTIL 行

```jsonl
{"paper_id":"001","source":"DIS","record_type":"UTIL","kind":"CONSERVATIVE","subtype":"hedging","template":"В рамках допущений можно предположить, что {X}.","when_to_use":"讨论段：给出保守解释并显式限定条件","common_mistakes":["只加保守词但不给条件","用保守词回避可验证表述"],"function":"保守推断/限定结论","quality_score":2,"schema_version":"2.1"}
```

---

## 快速启动

### 1. 查询句式（写作时）

```bash
# 加载子 skill
skill_view("phd-thesis-butler/sub_skills/dis_intro")

# 检索 motivation 模板
grep '"subtype":"motivation"' data/curated/quality/QUALITY2_SELECTION_DIS.jsonl | head -5
```

### 2. 抽取新论文

```bash
# 准备 PDF → 调用 Router → 执行 plan
cat prompts/router.prompt.txt | ... → {"plan":[...]}
python3 scripts/qa_check.py --input raw/DIS_001.jsonl --output qa/DIS_001.json
```

### 3. 聚合已有产出

```bash
python3 scripts/aggregate.py dedup --input raw/Raw_DIS.jsonl --output dedup/DeDup_DIS.jsonl
python3 scripts/aggregate.py filter --input dedup/DeDup_DIS.jsonl --output filtered/Filtered_DIS.jsonl
python3 scripts/generate_top50.py --input filtered/Filtered_DIS.jsonl --output-dir TOP50/
```

---

## 免责声明

⚠️ **本工具提供的所有句式模板、用法建议和写作辅助材料：**

1. **仅用于润色参考** — 不应用于自动生成学术论文全文或核心章节
2. **不构成原创学术贡献** — 使用者必须独立完成研究内容与核心写作
3. **学术伦理风险自担** — 使用 AI 辅助学术写作可能违反所在机构或期刊的伦理政策
4. **著作权责任** — 使用者需确保最终作品不侵犯原始论文的著作权
5. **数据来源** — 本句式库从公开论文中提取模板骨架，不包含原文复制内容

**使用本工具即表示您理解并接受上述风险。**
