# Changelog

## v4.0 (2026-06-02)

### Corpus Distillation Layer — 语料库蒸馏层

**New: corpus_layer/**
- `WORKFLOW.md` — 4-stage pipeline: SOURCE → EXTRACT → DISTILL → PUBLISH
- 5 JSON Schema: `paper_record`, `structure_record`, `methodology_record`, `logic_chain`, `rhetorical_move`
- `SCHEMA_CONVENTION.md` — shared ID naming, category/cluster enums, evidence_count format

**New: extraction scripts**
- `build_corpus_inventory.py` — full corpus scan, per-discipline stats
- `extract_structure_records.py` — structure patterns → `.phd_build/structure_records.jsonl`
- `extract_methodology_records.py` — methodology routes → `.phd_build/methodology_records.jsonl`
- `extract_logic_chains.py` — logic chain analysis → `.phd_build/logic_chains.jsonl`
- `extract_rhetorical_moves.py` — rhetorical move extraction → `.phd_build/rhetorical_moves.jsonl`
- `validate_corpus_layer.py` — corpus layer integrity validation

**New: planning_layer/**
- 22 files: 6 clusters, 6 patterns, 4 templates, 2 schemas, 4 guides
- All patterns include `evidence_count` with corpus-derived numbers

**Infrastructure**
- `validate_skill_assets.py`: fixed timeout, no hardcoded paths, `--deep` mode
- `validate_planning_assets.py`: new validator (22/22 checks)
- `tests/`: 23 pytest tests, all passing in <1s
- `.phd_build/`: gitignored build output directory
- `reports/drafts/`: 4 draft reference assets (rhetorical moves, methodology routes, logic chains, common failures)
- `corpus_analysis_report.md`: full corpus analysis with coverage gaps

## v3.3.5 (2026-05-30)

### Asset Layer Fix — 归层修复 + 占位符迁移 + PII 脱敏

**修复**
- HUM_SOC/ART_SPORT master 空文件填充
- GLOBAL/TECH_LIFE quality 文件 100% 重叠消除
- UTILS 占位符 ___ → [...] 全局迁移（1,234 处）
- HUM_SOC quality 子目录生成
- PII 脱敏检查通过（无泄漏）

**资产结构**
- GLOBAL (L0): 188 条 / TECH_LIFE (L1): 5,802 条 / HUM_SOC (L1): 4,055 条
- Zero overlap across all layers

## v3.1.0 (2026-05-30)

### Phase 2 Complete — DIS + AREF Dual-Channel Pipeline

**新增**
- Phase 2 双通道全量抽取管线：DIS（论文 1,316 篇）+ AREF（摘要 587 篇）
- `agents/aref_worker.py` — автореферат 专用抽取 Worker（含 429 指数退避）
- `agents/run_aref.py` — AREF 并行执行器
- `agents/run_dis_retry.py` — DIS 死信恢复执行器
- `agents/g3_merge.py` — 归并门控（去重 + category 分组 + G3 门控）
- `agents/g4_classify.py` — 归层分配（HUM_SOC / ART_SPORT + zero overlap 检查）
- `agents/g5_smoke_test.py` — 上线烟雾测试（模板数 + Q2% + K=3 + gap 趋势）
- `assets/` — 分层产出目录结构

**Pipeline 架构**
- Master/Worker 文件队列并行（独立 todo/doing/done/dead_letter 目录）
- 原子写：tmp → rename 确保不破坏输出
- 5 级门控：G1 抽取完整性 → G2 QA → G3 归并 → G4 归层 → G5 上线
- 10,045 条去重模板，23 categories，34 学科

**结果**
- DIS 论文：1,042 ✅ / 274 ❌（扫描PDF）
- AREF 摘要：361 ✅ / 226 ❌（扫描PDF）
- 分层：HUM_SOC 5,150 / ART_SPORT 4,895，Zero Overlap = 0
- G1–G5 全部通过

## v3.0.0 (2026-05-29)

### 5-Agent 润色管线 + BMSTU 基线冻结

- 5 Agent 润色管线：Router → Retriever → Polisher → Consistency → Safety
- 基线数据：9,602 条（DIS 5,621 + AREF 3,573 + UTILS 408）
- 13 个子 skill 按需加载架构
- 分层隔离：公开 README + 私有 _private_notes.md
- 第一批 327 篇 BMSTU 论文全量抽取
