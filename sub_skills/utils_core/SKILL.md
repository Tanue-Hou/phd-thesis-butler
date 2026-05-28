---
name: phd-thesis-butler/utils_core
description: "UTIL 句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# UTILS — 连接词/保守措辞/数字汇报

## 用途

写作中的连接词、保守措辞和数字汇报表达。所有子 skill 产出的 UTIL 最终汇聚于此。

## 分类

### CONNECTIVE
- contrast / addition / cause_effect
- concession / illustration / sequencing
### CONSERVATIVE
- hedging / limitation_qualifier
- suggestion_soft / uncertainty_expression
### NUMERIC
- improvement_report / error_report
- distribution_report / comparison_report

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

• CONNECTIVE 不要过度使用
• CONSERVATIVE.hedging 不能破坏结论强度
• NUMERIC 要配合数据上下文使用

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
