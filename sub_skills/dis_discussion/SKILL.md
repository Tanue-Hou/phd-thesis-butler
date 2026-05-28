---
name: phd-thesis-butler/dis_discussion
description: "DISCUSSION 句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# DIS DISCUSSION — 讨论部分句式库

## 用途

写作讨论部分：机制解释、敏感性分析、权衡分析、泛化性、有效性威胁。

## 分类

### DISCUSSION
- mechanism_explanation / sensitivity / tradeoff
- generalization / threat_to_validity / interpretation_hedged

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

• threat_to_validity 要诚实，不要回避
• interpretation_hedged 必须使用保守措辞
• generalization 要基于证据，不要过度外推

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
