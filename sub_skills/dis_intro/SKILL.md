---
name: phd-thesis-butler/dis_intro
description: "INTRO 句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# DIS INTRO — 引言句式库

## 用途

写作论文引言（Введение）部分：交代动机、提出目标、预告贡献、概述结构。

## 分类

### INTRO
- motivation / relevance / problem_statement
- objective / tasks / object_subject
- contributions_preview / thesis_structure

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

• 动机段不要空泛（必须限定具体领域）
• contributions_preview 不要过度承诺成果
• thesis_structure 保持简洁，不要逐章展开

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
