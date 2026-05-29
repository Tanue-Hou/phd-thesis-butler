# PhD Thesis Butler

## 项目范围

从俄罗斯多所高校和公开数据库收集学位论文（диссертации + авторефераты），扩展现有的俄语学术写作句式模板库（当前 9,602 条，327 篇）。

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

active - 5 智能体润色系统构建中

## 最近更新

2026-05-29: 5 Agent pipeline 构建完成并通过测试
- Router (学科/场景推断) ✅
- Retriever (3层回退链) ✅  
- Polisher (三级润色, 待API key验证) ✅
- Consistency (一致性检查) ✅
- Safety (安全审查) ✅
- 样本数据: 22 GLOBAL模板 + 5 UTILS + CLUSTER副本
- 管线测试: Router→Retriever→Consistency→Safety 全部通过
