# Phase 2 Extraction Pipeline — DIS + AREF Dual Channel

## Overview

When running a Phase 2 full-scale extraction from university dissertation repositories, you must explicitly handle **two parallel channels**:

| Channel | Document | Source | Volume |
|---------|----------|--------|--------|
| 📄 DIS | диссертация.pdf (full thesis) | All universities | 589 (MSU) + 727 (SPbSU) |
| 📝 AREF | автореферат.pdf (abstract/summary) | MSU only (SPbSU rarely includes) | 587 (MSU) |

**Critical pitfall**: AREF PDFs co-exist in the same `data/{University}/{Subject}/{Author}/` directory as dissertation PDFs but are **NOT automatically included** in the job queue. Job generation must explicitly enumerate both `диссертация.pdf` and `автореферат.pdf` files.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────┐
│ Master (queue orchestrator)                      │
│ Creates all jobs → manages todo/doing/done/dead  │
├───────────────────────┬─────────────────────────┤
│ DIS Workers (20 procs) │ AREF Workers (20 procs) │
│ G1+G2 gate per batch   │ G1+G2 gate per batch    │
├───────────┬───────────┴───────────┬─────────────┤
│           ▼                       ▼              │
│           G3 Merge (DIS + AREF by category)      │
│           G4 Classify (to layer/cluster/displine)│
│           G5 Smoke test + quality gates          │
└─────────────────────────────────────────────────┘
```

## Queue Directory (Atomics)

```
queue/
├── todo/          ← job JSON files waiting
├── doing/         ← claimed by workers (rename = atomic lock)
├── done/          ← completed successfully
└── dead_letter/   ← failed after 3 retries
```

**Atomic operations:**
- **Claim**: `os.rename(todo/job.json, doing/job.json)` — atomic lock, no race
- **Complete**: `copy + unlink(doing)` → atomic write to `data/raw/{source}/{id}.jsonl`
- **Fail**: increment `retry` counter, return to `todo/` if < 3, else `dead_letter/`

## Job File Schema

```json
{
  "id": "MSU_0037",
  "pdf_path": "data/MSU/исторические_науки/Автор/диссертация.pdf",
  "source": "MSU",
  "subject": "исторические науки",
  "doc_type": "диссертация",
  "retry": 0
}
```

AREF jobs differ: `doc_type: "автореферат"` and a different `pdf_path` pointing to the `автореферат.pdf`.

## Worker Implementation

Each worker is a standalone process that:

1. **Picks a job** from `queue/todo/` (atomic rename to `doing/`)
2. **Extracts text** from PDF via PyMuPDF (first 15,000 chars to fit token limit)
3. **Calls MIMO API** with appropriate system prompt:
   - DIS prompt: extract structural templates (INTRO→SURVEY→MODEL→…)
   - AREF prompt: extract summative templates (АКТУАЛЬНОСТЬ→НОВИЗНА→…)
4. **Runs G1 gate** on returned entries:
   - 100% JSON parsable
   - Field completeness ≥ 98% (template, category, subtype, quality_score)
   - No `___` placeholders (only `[...]` allowed)
5. **Writes atomically** to `data/raw/{source}/{id}.jsonl`
6. **Tags each entry** with `source`, `subject`, `pdf_id`, `doc_type`

### DIS vs AREF System Prompts

| Aspect | DIS | AREF |
|--------|-----|------|
| Categories | INTRO, SURVEY, MODEL, METHOD, EXPERIMENT, RESULT, DISCUSSION, CONCLUSION, TRANSITION, FORMAL_DEFS, ENGINEERING | АКТУАЛЬНОСТЬ, НОВИЗНА, ЦЕЛЬ, ЗАДАЧИ, ОБЪЕКТ, ПРЕДМЕТ, МЕТОДЫ, ПОЛОЖЕНИЯ, ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ, ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ, ДОСТОВЕРНОСТЬ, АПРОБАЦИЯ, СТРУКТУРА, ВНЕДРЕНИЕ |
| Template type | Structural patterns from body text | Summative patterns from formalized sections |
| Quality distinction | quality=2 → interdisciplinary | quality=2 → cross-disciplinary formulation |

## Gate System (G1–G5)

| Gate | Name | Check | Action on Fail |
|------|------|-------|----------------|
| G1 | Parsing | JSON valid 100%, fields ≥98%, no `___` | Retry (up to 3×), then dead_letter |
| G2 | Quality | `___`=0, Q2≥20%, Q0≤5% | Retry or exclude |
| G3 | Merge | Each category ≥3 entries from combined DIS+AREF | Log gap, continue |
| G4 | Classification | LAYER_ASSIGNMENT_RULES.md → zero overlap, Router contract | Fail batch, manual review |
| G5 | Production | HUM_SOC/ART_SPORT ≥2,000 per cluster, Q2≥25% | Block release |

## Worker Count Strategy

| Phase | Workers | Notes |
|-------|---------|-------|
| Start | 8 DIS + 8 AREF = 16 | Conservative, gauge API rate limits |
| Ramp | 20 DIS + 20 AREF = 40 | If failure rate < 5% and API stable |
| Sustain | 20 total | Rate ~25/min average after throttling |

REALITY: API rate limiting is the bottleneck. MIMO API with 20 workers yielded ~135/min initially, then settled to ~25/min sustained. Do not over-provision workers beyond what the API can sustain.

## Job Generation Script Pattern

```python
# Pseudo-code for generating both DIS and AREF jobs
def generate_jobs(data_root, output_queue):
    for university_dir in data_root.iterdir():
        for subject_dir in university_dir.iterdir():
            for author_dir in subject_dir.iterdir():
                # Generate DIS job
                dis_pdf = author_dir / "диссертация.pdf"
                if dis_pdf.exists():
                    create_job(f"{uni}_{author}", dis_pdf, "диссертация")
                
                # Generate AREF job (MUST be explicit!)
                aref_pdf = author_dir / "автореферат.pdf"
                if aref_pdf.exists():
                    create_job(f"{uni}_{author}", aref_pdf, "автореферат")
```

## Cache Management

Each worker uses an isolated cache directory to prevent file conflicts:

```python
CACHE_DIR = Path(f"/tmp/.cache/phd-thesis-butler/worker_{os.getpid()}")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

## Monitoring

Track progress with:
```bash
# Quick status
echo "todo: $(ls queue/todo/ | wc -l)  doing: $(ls queue/doing/ | wc -l)  done: $(ls queue/done/ | wc -l)  dead: $(ls queue/dead_letter/ | wc -l)"

# Rate
done_count / ((now - start_time) / 60) = items/min

# Log tail
tail -5 logs/full_fast.log
```

## 故障恢复流程

### Dead Letter 重试

当 API 限流（429）导致大量 job 进入 dead_letter 时，**不要直接丢弃**——先验证：

```bash
# 1) 抽样重放一个 dead job，确认是否真是扫描版
python3 agents/worker.py --job queue/dead_letter/SPbSU_0006.json --output /tmp/test

# 2) 如果是 API 限流导致 → 重置 retry=0 移回 todo
# 使用 execute_code 批量操作
for f in queue/dead_letter/*.json:
    job = json.load(open(f))
    job["retry"] = 0
    json.dump(job, open(f"queue/todo/{job['id']}.json", "w"), ensure_ascii=False)
    os.unlink(f)

# 3) 降低并行度后重启（前车之鉴：20 Workers → 10 Workers 即可避免 429）
```

典型结果：637 篇 dead 中 100% 可恢复（均为 API 限流，非 PDF 本身问题）。

### 429 指数退避（代码级）

API 返回 `{"error":{"code":"429","message":"Too many requests"}}` 时，**必须实现在 Worker 内部**，不能推到 Runner 层：

```python
max_retries = 5
for attempt in range(max_retries):
    result = subprocess.run([curl_cmd], ...)
    resp = json.loads(result.stdout)
    if "error" in resp and resp["error"].get("code") == "429":
        wait = min(2 ** attempt * 5, 60)  # 5s, 10s, 20s, 40s, 60s
        time.sleep(wait)
        continue
    # ... normal processing
```

注意：重试逻辑必须包含 `time.sleep()` 并在循环中 `continue`，不要 return 错误。5 次重试基本覆盖所有瞬态限流。

### Worker 无声挂掉（Runner 僵死）

场景：Runner 仍在运行但最后一个 Worker 进程已无声退出，doing 目录留有一个 job 文件，循环无限等待 `doing` 清空。

```bash
# 检查
ls queue/aref_doing/        # 还有文件
ps aux | grep aref_worker  # 无进程

# 恢复
python3 agents/aref_worker.py --job queue/aref_doing/LAST_JOB.json --output data/raw/AREF
cp queue/aref_doing/LAST_JOB.json queue/aref_done/
rm queue/aref_doing/LAST_JOB.json
pkill -f "run_aref.py"  # 杀掉僵死的 Runner
```

预防：Runner 主循环应定期检查 worker 进程数，发现 doing 有文件但 worker 进程为 0 时强制退出。

### Worker 脚本常见问题

| 问题 | 现象 | 修复 |
|------|------|------|
| 缺少 `subprocess` import | Worker 报 `name 'subprocess' is not defined` | 确保 `import json, os, sys, re, time, subprocess, shutil` 在文件顶部 |
| API 返回无 choices | 429 限流时返回 `{"error":{...}}` 而非 `{"choices":[...]}` | 加错误检测 + 指数退避重试 |
| curl 引用 `api_key` 变量被写为字面量 | `***` 而非 `{api_key}` 在 f-string 中 | 检查 Authorization 行是否使用 `f"...{api_key}"` |

## G3 归并：Category 归一化（关键步骤）

合并 DIS + AREF 数据前必须先做 category 清洗，否则 G3 gate 会因大量孤类 < 3 条而失败。

### 必须合并的 Category 变体

```python
CATEGORY_MERGE = {
    # 拼写错误
    "DISCUYSIS": "DISCUSSION",
    "DISCUYSSION": "DISCUSSION",
    "METHODOLOGY": "METHOD",    # 与 METHOD 同义
    "METHODS": "METHOD",        # 单复数
    "RESULTS": "RESULT",
    "STRUCTURE": "INTRO",       # 极少条目，合入 INTRO
    # AREF 复合类别（pipe 分隔）
    "НОВИЗНА|ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ": "НОВИЗНА",
    "ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ|ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ": "ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ",
    "ТЕОРЕТИЧЕСКАЯ_ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ": "ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ",
    # 孤类 → 父类
    "ВВОДНАЯ_ФОРМУЛИРОВКА": "INTRO",
    "ВОПРОСЫ": "DISCUSSION",
    "ГИПОТЕЗЫ": "DISCUSSION",
    "ЗНАЧИМОСТЬ": "ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ",
    "КОНСТРУКТИВНАЯ_КРИТИКА": "DISCUSSION",
    "СОДЕРЖАНИЕ": "INTRO",
    "СТРУКТУРА": "INTRO",
}
```

> 经验：G3 合并后应有约 **23 个核心 category**。如果 > 30，说明有未合并的拼写错误或孤类。

## Subject 归一化（G4 归层）

SPbSU 和 MSU 的 subject 字段在**格**和**分隔符**上不一致，必须在 G4 归层前归一化：

```python
# 归一化
subject = subject.strip().lower().replace("_", " ")

# 主格（MSU）和属格（SPbSU）的学科名必须同时在 rule set 中
HUM_SOC_SUBJECTS = {
    "исторические науки", "исторических наук",
    "филологические науки", "филологических наук",
    ...
}
```

详见 `agents/g3_merge.py`、`agents/g4_classify.py`、`agents/g5_smoke_test.py`（Phase 2 项目目录）。

## G3–G5 Pipeline (Post-Extraction)

After G1+G2 pass for both DIS and AREF channels, run the 3-stage post-processing pipeline:

### G3 Merge (`g3_merge.py`)

1. Load all raw JSONL from `data/raw/{MSU,SPbSU,AREF/MSU}/*.jsonl`
2. Deduplicate by `template` text (exact match)
3. **Critical: Category normalization** — merge typos/rare variants (DISCUYSIS→DISCUSSION, METHODOLOGY→METHOD, etc.) See full mapping below
4. Write per-category files to `data/merged/by_category/`
5. G3 Gate: each category ≥ 3 entries

**Known categories after normalization**: INTRO, SURVEY, MODEL, METHOD, EXPERIMENT, RESULT, DISCUSSION, CONCLUSION, TRANSITION, FORMAL_DEFS, АКТУАЛЬНОСТЬ, НОВИЗНА, ЦЕЛЬ_ЗАДАЧИ, ОБЪЕКТ_ПРЕДМЕТ, МЕТОДЫ, ПОЛОЖЕНИЯ, ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ, ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ, АПРОБАЦИЯ, ВЫВОДЫ, ПЕРСПЕКТИВЫ, ДОСТОВЕРНОСТЬ, СТЕПЕНЬ_РАЗРАБОТАННОСТИ (~23 core categories)

### G4 Classify (`g4_classify.py`)

1. Assign each entry to a discipline (from `subject` field)
2. Assign to layer (HUM_SOC / ART_SPORT per LAYER_ASSIGNMENT_RULES.md)
3. **Subject normalization is critical**: replace underscores→spaces, handle nominative+genitive cases
4. Write per-layer files to `assets/cluster/{HUM_SOC,ART_SPORT,TECH_LIFE}/`
5. Write per-discipline files to `assets/discipline/`
6. G4 Gate: zero overlap between layers

### G5 Smoke Test (`g5_smoke_test.py`)

1. Report HUM_SOC / ART_SPORT template count + Q2%
2. Check 5 sample disciplines for K=3 availability
3. Verify zero overlap
4. Report P0 gap list
5. G5 Gate: each layer ≥ 2,000 entries AND Q2 ≥ 25%

## Post-Processing: Asset Layer Rebuild (v3.1.1+)

After G4 but before production, a second-pass layer reassignment is needed to ensure:

1. **GLOBAL (L0)** — templates appearing in ≥2 clusters (quality must be ≥2)
2. **TECH_LIFE (L1)** — technical/life sciences cluster
3. **HUM_SOC (L1)** — humanities/social sciences cluster
4. **Zero overlap verification** — no template appears in >1 layer

The algorithm (implemented in `fix_v311_assets.py`):

```python
# Track per-template cluster distribution
template_clusters = defaultdict(set)
for e in all_entries:
    template_clusters[e["template"]].add(discipline_to_cluster(e["subject"]))

# Assign each entry to layer
for e in all_entries:
    n_clusters = len(template_clusters[e["template"]])
    if n_clusters >= 2 and e["quality_score"] == 2:
        assign_to("GLOBAL")
    else:
        assign_to(cluster_from_subject(e["subject"]))
```

### Quality File Generation per Layer

Each layer's `quality/` directory should contain per-category Q2=2 files:
- `QUALITY2_{CATEGORY}.jsonl` — Q2 entries for that category
- `QUALITY2_ALL.jsonl` — all Q2 entries combined
- `UTILS.jsonl` — utility patterns

Generate with:
```python
q2 = [e for e in layer_entries if e.get("quality_score") == 2]
by_cat = defaultdict(list)
for e in q2: by_cat[e["category"]].append(e)
for cat, entries in by_cat.items():
    write_jsonl(f"quality/QUALITY2_{cat}.jsonl", entries)
write_jsonl("quality/QUALITY2_ALL.jsonl", q2)
```

## v3.1.1 Asset Fix Recipe

When GLOBAL and TECH_LIFE quality files show 100% overlap (identical templates in EXPERIMENT/METHOD/MODEL/RESULT/SURVEY), run:

```bash
python3 agents/fix_v311_assets.py
```

This single script performs:
1. Load classified master (10,045 entries)
2. Reassign layers per LAYER_ASSIGNMENT_RULES (template-cluster distribution)
3. Populate master/MASTER.jsonl for each layer
4. Generate non-overlapping quality files per category per layer
5. Migrate `___` → `[...]` placeholders in all UTILS files
6. PII scan (known names, emails, phones, URLs)
7. Verify zero overlap across all layers
8. Write v3.1.1_FIX_REPORT.json

| 问题 | 解决方法 |
|-------|-----------|
| Worker gets killed mid-job | `doing/` → move to `todo/` on restart |
| API timeout | Subprocess timeout=180s, curl --max-time=120 |
| AREF PDF smaller (50-100KB) vs DIS (2-15MB) | Shorter text, fewer templates per job |
| FileNotFoundError during `os.rename` | Skip gracefully (another worker already claimed) |
| Worker 无声挂掉 | Runner 循环等待 doing 队列清空但 worker 进程已死 → 手动处理最后一个 job + kill runner |
| 旧 AREF 进程被 kill 后新进程正常 | 通知 stale（proc_a26 被手动 kill 重启为 proc_fc25）— 确认 ps 后忽略通知即可 |
