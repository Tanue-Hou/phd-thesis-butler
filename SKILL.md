---
name: phd-thesis-butler
description: "博士论文管家 — 俄语学术写作句式库与抽取管线"
version: "2.1"
author: Tanue Hou
model: xiaomi mimo v2.5
tags: [russian, academic, writing, sentencebank, PhD, dissertation]
---

# PhD Thesis Butler — 博士论文管家

## 概述

从 300 篇俄语博士论文（DIS + AREF）中抽取全量句式与用法，生成可检索、可聚合的学术写作 Sentencebank。

## 目录结构

```
phd-thesis-butler/
├── SKILL.md                     ← 本文件：路由与使用说明
├── prompts/                     ← 可执行提示词（.prompt.txt）
│   ├── router.prompt.txt        ← 主路由器（输出执行计划 JSON）
│   ├── gm.prompt.txt            ← 总经理派工
│   ├── dis_full.prompt.txt      ← DIS 句式抽取
│   └── aref_full.prompt.txt     ← AREF 句式抽取
├── references/
│   ├── FULL_CLASSIFICATION.yaml ← 唯一枚举来源
│   ├── CROSS_CATEGORY_MAP.md    ← 写作场景→子 skill 映射
│   └── INDEX_GUIDE.md           ← 使用说明
├── schemas/
│   └── sentencebank_entry.schema.v2_1.json
├── scripts/
│   ├── aggregate.py             ← 聚合/去重/归并/过滤
│   ├── qa_check.py              ← QA 抽检
│   ├── coverage_check.py        ← 三档覆盖检测
│   ├── generate_top50.py        ← 精选 TOP50 生成
│   ├── smoke_test.sh            ← 全链路自检
│   ├── batch_runner.sh          ← batch 运行
│   └── retry_handler.sh         ← 重试/死信处理
├── sub_skills/                  ← 按需加载的子 skill
│   ├── dis_intro/               ← INTRO 句式库
│   ├── dis_survey/              ← SURVEY 句式库
│   ├── dis_model/               ← MODEL 句式库
│   ├── dis_method/              ← METHOD 句式库
│   ├── dis_experiment/          ← EXPERIMENT 句式库
│   ├── dis_result/              ← RESULT 句式库
│   ├── dis_discussion/          ← DISCUSSION 句式库
│   ├── dis_conclusion/          ← CONCLUSION 句式库
│   ├── dis_transition/          ← TRANSITION 句式库
│   ├── dis_formal_defs/         ← FORMAL_DEFS 句式库
│   ├── dis_engineering/         ← ENGINEERING 句式库
│   ├── aref_core/               ← AREF 全模块句式库
│   └── utils_core/              ← UTIL（连接词/保守/数字）
├── data/
│   ├── raw/                     ← 原始 batch 产出
│   └── curated/                 ← 最终产品
│       ├── master/              ← MASTER_*.jsonl
│       ├── quality/             ← QUALITY2_SELECTION + TOP50
│       └── gaps/                ← gap_list_*.json
└── qa_archive/                  ← QA 报告存档
```

## 路由规则

主路由器（prompts/router.prompt.txt）接收任务请求，输出执行计划 JSON。

### 输入格式
```json
{"goal":"extract|qa|aggregate|coverage|query|build_top50",
 "inputs":[{"path":"..."}],
 "context":{"paper_id":"001","mode":"lite|full","schema_version":"2.1"},
 "request":{"writing_scene":"写引言","subscene":"动机"}}
```

### 输出契约
```json
{"plan":[{"action":"run_skill|run_script|recommend",
          "skill":"sub_skills/xxx",
          "input":"/path/to/file",
          "output":"/path/to/output",
          "model":"xiaomi mimo v2.5"}]}
```

## Quickstart（最小可跑示例）

### 1. 查询句式（写作时）

```bash
# 加载主 skill → 路由
skill_view("phd-thesis-butler")

# 需要写引言 → 加载 INTRO 子 skill
skill_view("phd-thesis-butler/sub_skills/dis_intro")

# 检索 motivation 相关模板
grep '"subtype":"motivation"' data/curated/quality/QUALITY2_SELECTION_DIS.jsonl | head -5
```

### 2. 抽取新论文

```bash
# 准备命名规范的 PDF
# P001_DIS.pdf  +  P001_AREF.pdf

# 调用 Router 生成执行计划
cat prompts/router.prompt.txt | ... → {"plan":[...]}

# 按 plan 执行抽取
python3 scripts/qa_check.py --input raw/DIS_001.jsonl --output qa/DIS_001.json
```

### 3. 聚合已有产出

```bash
python3 scripts/aggregate.py dedup --input raw/Raw_DIS.jsonl --output dedup/DeDup_DIS.jsonl
python3 scripts/aggregate.py filter --input dedup/DeDup_DIS.jsonl --output filtered/Filtered_DIS.jsonl
python3 scripts/aggregate.py stats --dis filtered/Filtered_DIS.jsonl --output stats_report.json
python3 scripts/generate_top50.py --input filtered/Filtered_DIS.jsonl --output-dir TOP50/
```

### 4. 输出样例

**TEMPLATE 行（DIS）**:
```jsonl
{"paper_id":"001","source":"DIS","record_type":"TEMPLATE","category":"INTRO","subtype":"motivation","template":"В последние годы ___ привлекает все большее внимание в области ___.","slots":["объект/тема","область/контекст"],"when_to_use":"引言段首：交代研究方向关注度并限定领域","common_mistakes":["空泛不落地","未限定范围导致过度泛化"],"strength":"neutral","quality_score":2,"schema_version":"2.1"}
```

**UTIL 行**:
```jsonl
{"paper_id":"001","source":"DIS","record_type":"UTIL","kind":"CONSERVATIVE","subtype":"hedging","template":"В рамках допущений можно предположить, что {X}.","when_to_use":"讨论段：给出保守解释并显式限定条件","common_mistakes":["只加保守词但不给条件","用保守词回避可验证表述"],"function":"保守推断/限定结论","quality_score":2,"schema_version":"2.1"}
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.1 | 2026-05 | 最终版：9,602条，PII脱敏通过，JSON schema 严格化 |
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

## 约束
- 模型强制：xiaomi mimo v2.5
- 所有 category/subtype 必须来自 FULL_CLASSIFICATION.yaml
- 输出 schema 必须遵守 schemas/sentencebank_entry.schema.v2_1.json
- schema_version 必须为 "2.1"
