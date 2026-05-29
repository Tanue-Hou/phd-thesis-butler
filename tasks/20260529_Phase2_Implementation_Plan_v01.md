# Phase 2 — 全量抽取与三层归层实施计划

## 目标

从 SPbSU + MSU 的 PDF 全量抽取 → 严格 QA → 去重归并 → 按 LAYER_ASSIGNMENT_RULES.md 自动归层 → 生成三层 master/quality/top50 → coverage/gap_list → 回派补齐

**产出要求：**
- HUM_SOC ≥ 2,000 条，Q2 ≥ 25%
- ART_SPORT ≥ 2,000 条，Q2 ≥ 25%
- 5 个样板 DISCIPLINE 各 ≥ 300 条
- zero overlap 始终为 0
- 全量 smoke_test 通过
- Tag: **v3.1.0**

---

## 流水线（5 Step，每步有 Gate）

### Step 1｜全量抽取（Extraction）

**输入：** `data/{MSU|SPbSU}/{subject}/{author}/диссертация.pdf`
**输出：** `data/raw/{SPbSU|MSU}/batch_{N}.jsonl`
**方法：** 每篇 PDF 通过 mimo-v2.5 抽取 → 输出 JSONL（template/category/subtype/when_to_use/common_mistakes/quality_score）

**Gate-1：** JSON 可解析率 100%，字段完整率 ≥98%，[...] 覆盖率 100%

### Step 2｜严格 QA

**输入：** `data/raw/{source}/batch_{N}.jsonl`
**输出：** `data/qa_pass/{source}_pass.jsonl` + `data/qa_fail/{source}_fail.jsonl`

**检查项：**
- `___` 必须为 0
- 无空 template
- 字段完整（template/category/subtype/quality_score）
- 无超长/专名串

**Gate-2：** Q2 ≥ 20%，Q0 ≤ 5%

### Step 3｜去重与归并

**输入：** `data/qa_pass/{source}_pass.jsonl`
**输出：** `data/dedup/{discipline}_dedup.jsonl`

先同 category/subtype 内精确去重，再近似归并（保留 1 主模板 + 2-3 变体）。

**Gate-3：** 每 category ≥ 3 条，归并日志落盘

### Step 4｜三层归层

按 `references/LAYER_ASSIGNMENT_RULES.md` 自动分配：
- DISCIPLINE：D_total=1 或 dominant_discipline_share≥0.7
- CLUSTER：C_total=1, D_total≥2, share≥0.8
- GLOBAL：C_total≥2 或强通用功能

**Gate-4：** `scripts/smoke_test.sh` 全通过（zero overlap 硬门槛）

### Step 5｜精炼输出

生成每层的 master/QUALITY2_* 文件 + TOP50 + coverage/gap_list。

**Gate-5：** HUM_SOC/ART_SPORT ≥ 2,000 且 Q2≥25%，样板 DISCIPLINE ≥ 300

---

## 多智能体分工（10 个子智能体，mimo-v2.5）

```
思远（总控）— 分配、审计、验收
  │
  ├── Agent 1-4（Extractors）: SPbSU PDF 并行抽取（每 agent 负责 ~175 篇）
  ├── Agent 5-8（Extractors）: MSU PDF 并行抽取（每 agent 负责 ~145 篇）
  ├── Agent 9（QA）: 全量 QA 检查 + 生成 pass/fail
  └── Agent 10（Merge + Assign）: 去重归并 + 三层归层 + 精炼输出
```

**每个子智能体已知的工作规范：**
1. 只允许占位符 `[...]`
2. 输出必须含：template/category/subtype/when_to_use/common_mistakes/quality_score
3. 不引入新事实、不改变原意
4. 学科从目录路径推断（data/{source}/{subject}/）
5. 场景从文本关键词判断

---

## 子智能体工作流

### Extractor Agent（1-8）

```
输入: PDF 路径列表
流程:
  1. 读取学科目录名（决定 discipline）
  2. 读取 PDF（文本提取）
  3. 调用 mimo-v2.5 抽取句式模板（按 category/subtype）
  4. 每条标注 quality_score, when_to_use, common_mistakes
  5. 输出 JSONL，仅 [...]
输出: JSONL 文件
```

### QA Agent（9）

```
输入: 所有 raw JSONL
流程:
  1. JSON 解析检查
  2. 字段完整性检查
  3. 占位符规范检查
  4. 质量分布统计
  5. 分流 pass/fail
输出: qa_pass / qa_fail
```

### Merge + Assign Agent（10）

```
输入: qa_pass JSONL
流程:
  1. 同 category/subtype 精确去重
  2. 近似归并（保留 1主+2-3变体）
  3. 按 LAYER_ASSIGNMENT_RULES 计算 D_total/C_total
  4. 自动归层 → 写入 assets/{global|cluster|discipline}/
  5. 生成 quality/TOP50/coverage/gap_list
输出: 三层资产 + gap_list
```

---

## 时间线

| 阶段 | 内容 | 预估 |
|------|------|------|
| Phase 1 | SPbSU 全量抽取（Agents 1-4） | 2-3 天 |
| Phase 2 | MSU 全量抽取（Agents 5-8） | 3-4 天 |
| Phase 3 | QA + 去重归并 | 1 天 |
| Phase 4 | 三层归层 + 精炼 | 1 天 |
| Phase 5 | 验证 + tag v3.1.0 | 0.5 天 |
| **总计** | | **7-10 天** |

---

## 日报指标

每日只汇报这 4 项：

| 指标 | 目标 |
|------|------|
| HUM_SOC / ART_SPORT 模板数 + Q2% | ≥ 2,000 / ≥ 25% |
| 5 个样板 DISCIPLINE 模板数 + K=3 可用性 | ≥ 300 / 可用 |
| zero overlap | 0 ❗ |
| gap_list P0 趋势 | 逐步下降 |
