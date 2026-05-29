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

# 3) 降低并行度后重启
```

典型结果：637 篇 dead 中约 637/637 可恢复（100%，均为 API 限流，非 PDF 本身问题）。

### Worker 脚本常见问题

| 问题 | 现象 | 修复 |
|------|------|------|
| 缺少 `subprocess` import | Worker 报 `name 'subprocess' is not defined` | 确保 `import json, os, sys, re, time, subprocess, shutil` 在文件顶部 |
| API 返回无 choices | 429 限流时返回 `{"error":{...}}` 而非 `{"choices":[...]}` | 加错误检测 + 指数退避重试 |
| curl 引用 `api_key` 变量被写为字面量 | `***` 而非 `{api_key}` 在 f-string 中 | 检查 Authorization 行是否使用 `f"...{api_key}"` |

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

详见 `batch-extraction-pipeline` skill 的 `references/g3-g5-pipeline-implementation.md`。

## 已知问题

| 问题 | 解决方法 |
|-------|-----------|
| Worker gets killed mid-job | `doing/` → move to `todo/` on restart |
| API timeout | Subprocess timeout=180s, curl --max-time=120 |
| AREF PDF smaller (50-100KB) vs DIS (2-15MB) | Shorter text, fewer templates per job |
| FileNotFoundError during `os.rename` | Skip gracefully (another worker already claimed) |
| Worker 无声挂掉 | Runner 循环等待 doing 队列清空但 worker 进程已死 → 手动处理最后一个 job + kill runner |
