---
name: phd-thesis-butler/aref_core
description: "AREF 全模块句式模板与用法"
version: "2.1"
model: xiaomi mimo v2.5
---

# AREF — Автореферат 全模块句式库

## 用途

写作 автореферат：选题意义、创新点、理论实践意义、保护条款、结果结论。

## 分类

### AREF 模块
- АКТУАЛЬНОСТЬ / ОБЪЕКТ_ПРЕДМЕТ / ЦЕЛЬ_ЗАДАЧИ
- МЕТОДЫ / НОВИЗНА / НОВИЗНА_ФОРМУЛИРОВКИ
- ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ / ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ
- ПОЛОЖЕНИЯ / РЕЗУЛЬТАТЫ / АПРОБАЦИЯ
- ПУБЛИКАЦИИ / СТРУКТУРА / ВЫВОДЫ

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

• НОВИЗНА 表述必须具体可验证
• ПОЛОЖЕНИЯ 是核心条款，每个要独立成句
• ВЫВОДЫ 要与 ЦЕЛЬ_ЗАДАЧИ 对应

## 文件说明

| 文件 | 位置 | 更新方式 |
|------|------|---------|
| QUALITY2_SELECTION.jsonl | references/ | 自动生成（aggregate 产出） |
| TOP50.md | references/ | 自动生成（generate_top50.py） |
| FULL_INDEX.jsonl | references/ | 自动生成（aggregate 产出） |
