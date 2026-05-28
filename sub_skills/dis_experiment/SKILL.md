---
name: phd-thesis-butler/dis_experiment
description: "EXPERIMENT 句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# DIS EXPERIMENT — 实验验证句式库

## 用途

写作实验部分：数据描述、场景设计、评价指标、基线设置。

## 分类

### EXPERIMENT
- data_description / scenario_design / metrics
- baselines / train_test_split / hyperparams
- reproducibility / statistical_reporting

## 检索方法

1. 识别你的写作子场景（参考 CROSS_CATEGORY_MAP.md）
2. 定位到对应的 subtype
3. 加载本 skill 后，检索 references/ 目录文件：
   - `QUALITY2_SELECTION.jsonl` — 高质量模板（quality=2）, 可直接 grep
   - `TOP50.md` — 该 category 最常用的 50 种句式模式
   - `FULL_INDEX.jsonl` — 完整库（含 quality=1）

## 质量门槛

- 仅使用 quality_score=2 的条目（看 QUALITY2_SELECTION）
- quality=1 的条目需要人工判断场景匹配度
- quality=0 的条目不进本 skill

## 常见误用

• metrics 要说明为什么选这个指标
• baselines 要解释为什么选这些对比方法
• reproducibility 要给出尽量多的复现信息

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
