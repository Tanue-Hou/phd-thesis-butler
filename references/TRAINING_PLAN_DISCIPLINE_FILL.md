# DISCIPLINE 层填充训练计划

## 目标

从 СПбГУ + МГУ 已下载 PDF 中抽取学科专有模板，填充 DISCIPLINE 层。

## 优先级

### Phase 1: 先填 5 个样板学科

| 学科 | 源数据 | 优先场景 |
|------|--------|---------|
| MEDICINE | SPbSU(93篇) | EXPERIMENT.data_description, RESULT.numeric, DISCUSSION.limitation |
| ECONOMICS | SPbSU(28篇)+MSU(38篇) | METHOD.identification, RESULT.numeric, DISCUSSION |
| BIOLOGY | MSU(49篇) | EXPERIMENT.data, RESULT, DISCUSSION |
| CHEMISTRY | MSU(59篇) | EXPERIMENT.setup, RESULT, MODEL |
| PHILOLOGY | MSU(67篇)+SPbSU(65篇) | SURVEY, DISCUSSION, INTRO |

### Phase 2: 扩展全量

按学科论文数降序覆盖剩余学科。

## 填充流程

```
① 从 PDF 抽取 → ② QA 校验 → ③ 去重归并 → ④ 归层(L0/L1/L2) → ⑤ coverage/gap → ⑥ 回派补齐
```

### 输入/输出

| 步骤 | 输入 | 输出 |
|------|------|------|
| ① 抽取 | `data/{MSU|SPbSU}/{subject}/{author}/диссертация.pdf` | `data/raw/{source}_batch.jsonl` |
| ② QA | raw JSONL | `data/qa/{source}_qa_pass.jsonl` |
| ③ 归并 | QA pass | `data/dedup/{source}_dedup.jsonl` |
| ④ 归层 | Dedup | → `assets/discipline/{NAME}/master/` |
| ⑤ Coverage | Discipline master | `data/gaps/{discipline}_gaps.json` |
| ⑥ 补齐 | Gaps | 回 Phase 1 补抽 |

## 学科强差异场景

每个学科至少覆盖：

| 场景 | 学科差异点 |
|------|-----------|
| EXPERIMENT.data | 医学：纳排/伦理；经济：样本选择/数据源；理工：工况/参数 |
| RESULT.numeric | 医学：显著性/置信区间；经济：稳健性/内生性；理工：误差/RMSE |
| DISCUSSION.limitation | 医学：偏倚/混杂；经济：识别/内生性；人文：解释路径 |

## 质量门控

- DISCIPLINE 层的模板 quality≥1 即可进入（因专有性天然高）
- 通过使用反馈逐步提升到 quality=2
