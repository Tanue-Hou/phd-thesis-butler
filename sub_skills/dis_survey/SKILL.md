---
name: phd-thesis-butler/dis_survey
description: "SURVEY 句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# DIS SURVEY — 文献综述句式库

## 用途

写作文献综述部分：流派梳理、方法对比、识别空白、定位本文。

## 分类

### SURVEY
- taxonomy / comparison / limitations_of_prior
- gap / positioning / evaluation_axes / baseline_selection

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

• limitations_of_prior 要具体，不要笼统说"现有方法不足"
• gap 表述要直接且可验证
• positioning 要清晰说明本文的差异化贡献

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
