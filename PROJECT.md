# PhD Thesis Butler

## 项目范围

从俄罗斯多所高校和公开数据库收集学位论文（диссертации + авторефераты），扩展现有的俄语学术写作句式模板库（当前 19,747 条，1,403 篇论文+摘要）。

包括：
- 调研各大学公式论文公开来源
- 批量下载 авторефераты PDF
- 适配抽取管线（多源兼容）
- 分学科扩展分类体系
- 质量审计与合并

## 关键词

PhD Thesis Butler, disserCat, dissovet.msu.ru, disser.spbu.ru, ВАК, автореферат, диссертация, sentencebank, академическое письмо, русский язык

## 不属于本项目的内容

- ~/.hermes 下的 skill 本身（SKILL.md 等已有独立 git 仓库）
- 其他不相关的论文写作任务

## 当前状态

v3.1.1 — Asset Layer Fix: 归层修复 + 占位符迁移 + Zero Overlap

## 最近更新

2026-05-30: Phase 2 Complete — DIS+AREF Pipeline
- Phase 2 双通道全量抽取: DIS 1,042 ✅ / AREF 361 ✅
- Master/Worker 文件队列并行架构（20 Workers）
- G1 抽取 → G2 QA → G3 归并 → G4 归层 → G5 上线 全流程
- 10,045 条去重模板（HUM_SOC 5,150 + ART_SPORT 4,895）
- 23 categories, 34 学科, Zero Overlap = 0
