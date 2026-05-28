---
name: phd-thesis-butler/dis_formal_defs
description: "FORMAL_DEFS 句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# DIS FORMAL_DEFS — 形式定义句式库

## 用途

写作正式定义与符号部分：定义引入、引理表述、约束引入、符号说明。

## 分类

### FORMAL_DEFS
- definition / lemma_style
- constraint_introductions / symbol_introductions

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

• definition 必须准确无歧义
• symbol_introductions 每个符号用完要说明
• lemma_style 要保持格式一致性

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
