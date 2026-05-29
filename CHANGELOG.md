# Changelog

## v3.1.0 (2026-05-30)

### Phase 2 Integration — MSU + SPbSU 双通道数据合并

**新增**
- 合并 MSU + SPbSU Phase 2 抽取数据（10,045 条 → 合并后 19,007 条）
- 新增 6,621 条 DIS 模板（总计 11,980）
- 新增 3,291 条 AREF 模板（总计 6,619）
- Quality=2 selections：DIS 8,383 / AREF 2,228
- 新增参考文献：pipeline-extraction.md / dissertation-sources.md / batch-download-tips.md

**架构**
- DIS + AREF 双通道独立抽取 → 去重归并 → 归层分配 → 门控上线
- 从 BMSTU 扩展到 MSU + SPbSU（3 所高校）
- 数据源覆盖 34 学科、23 categories

**Skill 版本**
- 内置模板：9,602 → 19,007 条（+98%）
- 学科覆盖：1 校 → 3 校
- SKILL.md 更新数据引用和版本号

## v2.1.0 (2026-05-29)

### BMSTU 基线 + 13 子 Skill 架构

- 第一批 327 篇 BMSTU 论文全量抽取（9,602 条）
- 13 个子 skill 按需加载架构
- 5-Agent 润色管线：Router → Retriever → Polisher → Consistency → Safety
- 公开 README + 私有配置分层隔离
