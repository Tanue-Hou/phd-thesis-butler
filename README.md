# PhD Thesis Butler v4.0

[中](#zh) · [Рус](#ru) · [EN](#en)

---

<a id="zh"></a>

## 中文

### 简介

PhD Thesis Butler 是一个 Hermes Agent 技能，专为俄罗斯副博士（кандидат наук）学位论文写作设计。它从 1,403 篇真实学位论文和摘要中提取高质量写作模板，并在此基础上构建了语料库蒸馏层，提供结构模式、方法论路线、逻辑链和修辞手法分析。

### 核心能力

- **16,722 个纯俄语写作模板**，覆盖 34 个学科，11 个论文章节类别
- **语料库蒸馏层** — 从千篇论文中提取结构模式、方法论路线、逻辑链条
- **论文规划层** — 6 个学科聚类，5 种结构模式，4 套写作指南
- **三层检索** — 学科→聚类→全局 逐级回退，优先返回高质量模板

### 数据来源

| 指标 | 数值 |
|------|------|
| 模板总量 | 16,722 |
| 来源论文 | 1,403（1,042 篇学位论文 + 361 篇摘要）|
| 学科覆盖 | 34 |
| 质量分布 | Q2: 8,986 / Q1: 7,694 / Q0: 42 |

### 版本迭代

| 版本 | 新增能力 |
|------|----------|
| v4.0 | **语料库蒸馏层** — corpus_layer/ 管线 + 5 个结构化 schema + 6 个提取脚本 + .phd_build/ 输出 |
| v3.3.5 | 纯俄语数据清理完成，所有资产通过验证 |
| v3.0 | 三层资产架构稳定，Planning Mode 上线 |
| v2.0 | DIS + AREF 双通道管线完成 |

### 安装

```bash
# Hermes Agent 技能
cp -r phd-thesis-butler ~/.hermes/skills/
```

### 使用

加载技能后，直接输入自然语言请求：
- "帮我写俄语博士论文的актуальность"
- "规划论文结构，车辆动力学方向"
- "找三个 ограничения исследования 模板"

---

<a id="ru"></a>

## Русский

### Обзор

PhD Thesis Butler — навык Hermes Agent для написания диссертаций на соискание учёной степени кандидата наук. Система извлекает и стандартизирует шаблоны из 1 403 реальных диссертаций и авторефератов, добавляя слой дистилляции корпуса для анализа структур, методологий, логических цепочек и риторических приёмов.

### Возможности

- **16 722 чистых русскоязычных шаблона**, 34 предметных области, 11 категорий разделов
- **Слой дистилляции корпуса** — извлечение структурных паттернов, методологических маршрутов, логических цепочек
- **Слой планирования** — 6 кластеров дисциплин, 5 структурных паттернов, 4 руководства по написанию
- **Трёхуровневый поиск** — ДИСЦИПЛИНА → КЛАСТЕР → ГЛОБАЛЬНЫЙ

### Статистика

| Показатель | Значение |
|------------|----------|
| Всего шаблонов | 16 722 |
| Источников | 1 403 (1 042 диссертации + 361 автореферат) |
| Предметных областей | 34 |
| Распределение по качеству | Q2: 8 986 / Q1: 7 694 / Q0: 42 |

### Версии

| Версия | Новые возможности |
|--------|-------------------|
| v4.0 | **Слой дистилляции корпуса** — corpus_layer/, 5 схем, 6 скриптов, .phd_build/ |
| v3.3.5 | Очистка корпуса, строгая языковая проверка |
| v3.0 | Трёхуровневая архитектура, режим планирования |
| v2.0 | Конвейер DIS + AREF |

---

<a id="en"></a>

## English

### Overview

PhD Thesis Butler is a Hermes Agent skill for Russian candidate-of-sciences (кандидат наук) dissertation writing. It extracts high-quality writing templates from 1,403 real dissertations and abstracts, with an additional corpus distillation layer for structural patterns, methodology routes, logic chains, and rhetorical move analysis.

### Capabilities

- **16,722 pure Russian writing templates**, 34 disciplines, 11 section categories
- **Corpus distillation layer** — structural patterns, methodology routes, logic chains extracted from 1,000+ papers
- **Planning layer** — 6 discipline clusters, 5 structure patterns, 4 writing guides
- **3-tier retrieval** — DISCIPLINE → CLUSTER → GLOBAL with quality-based priority

### Data

| Metric | Value |
|--------|-------|
| Total templates | 16,722 |
| Source documents | 1,403 (1,042 dissertations + 361 abstracts) |
| Disciplines | 34 |
| Quality distribution | Q2: 8,986 / Q1: 7,694 / Q0: 42 |

### Version History

| Version | Highlights |
|---------|------------|
| v4.0 | **Corpus distillation layer** — corpus_layer/ pipeline, 5 schemas, 6 extraction scripts, .phd_build/ output |
| v3.3.5 | Strict Russian-only corpus cleanup, all validators green |
| v3.0 | Stable 3-tier asset architecture, Planning Mode |
| v2.0 | DIS + AREF dual-channel pipeline |

### Installation

```bash
# Deploy as Hermes Agent skill
cp -r phd-thesis-butler ~/.hermes/skills/
```

### Usage

After loading the skill, use natural language:
- "Give me INTRO templates for vehicle dynamics"
- "Plan a dissertation structure in control engineering"
- "Find three CONCLUSION templates with future work"
