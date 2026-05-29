# Changelog

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
