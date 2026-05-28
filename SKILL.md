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

## 使用方式

### 查询句式（写作时）
1. 识别写作场景（如"写引言"）
2. 查看 CROSS_CATEGORY_MAP.md → 定位 category/subtype
3. 加载对应子 skill：`skill_view("phd-thesis-butler/sub_skills/dis_intro")`
4. 从子 skill 的 references/ 中检索模板

### 抽取新论文（扩展用）
1. 准备 PDF（命名规范：P###_DIS.pdf / P###_AREF.pdf）
2. 调用 router: `cat prompts/gm.prompt.txt | ...`
3. 按输出 plan 执行

### 聚合已有产出
```bash
scripts/aggregate.py dedup --input raw/Raw_DIS.jsonl --output dedup/DeDup_DIS.jsonl
scripts/aggregate.py coverage --input filtered/Filtered_DIS.jsonl --spec references/FULL_CLASSIFICATION.yaml --gap-output gaps/gap_DIS.json
scripts/generate_top50.py --input curated/quality/QUALITY2_SELECTION_DIS.jsonl --output-dir curated/quality/TOP50_BY_CATEGORY/
```

## 约束
- 模型强制：xiaomi mimo v2.5
- 所有 category/subtype 必须来自 FULL_CLASSIFICATION.yaml
- 输出 schema 必须遵守 schemas/sentencebank_entry.schema.v2_1.json
- schema_version 必须为 "2.1"
